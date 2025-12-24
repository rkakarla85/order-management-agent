from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
import io
import os
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
import base64
from tts_wrapper import get_google_tts
from business_manager import BusinessManager

load_dotenv()

from openai import OpenAI
from ai_agent import get_agent_response

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Mount the React build directory (static files)
# In Docker, we'll copy frontend/dist to /app/static or similar
# Local dev fallback: ../frontend/dist
if os.path.exists("../frontend/dist"):
    app.mount("/assets", StaticFiles(directory="../frontend/dist/assets"), name="assets")

business_manager = BusinessManager()

# Restarting connection to verify API status
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Handle incoming WhatsApp messages from Twilio
    """
    form_data = await request.form()
    incoming_msg = form_data.get('Body', '').strip()
    sender_id = form_data.get('From', '') # e.g., whatsapp:+14155238886

    print(f"WhatsApp Message from {sender_id}: {incoming_msg}")

    # Use the sender_id as the session_id so the conversation persists for this user
    # TODO: Determine business_id from sender_id or phone number mapping
    response_text = get_agent_response(sender_id, incoming_msg, business_id="electronics_default")

    # Create Twilio XML response
    twilio_resp = MessagingResponse()
    twilio_resp.message(response_text)
    
    return Response(content=str(twilio_resp), media_type="application/xml")

@app.post("/voice")
async def voice_webhook(request: Request):
    """
    Handle incoming Voice calls from Twilio
    """
    form_data = await request.form()
    user_speech = form_data.get('SpeechResult')
    call_sid = form_data.get('CallSid') # Use CallSid as unique session ID for the call
    
    resp = VoiceResponse()
    
    if not user_speech:
        # Initial Greeting (Start of Call)
        greeting = "Welcome to the Application. How can I help you place an order today?"
        gather = Gather(input='speech', action='/voice', timeout=3, language='en-US')
        gather.say(greeting)
        resp.append(gather)
    else:
        # User spoke something, get AI response
        print(f"Voice Input from {call_sid}: {user_speech}")
        
        # Get response from AI Agent
        ai_reply = get_agent_response(call_sid, user_speech, business_id="electronics_default")
        print(f"AI Voice Reply: {ai_reply}")
        
        # Respond and wait for next input
        gather = Gather(input='speech', action='/voice', timeout=3, language='en-US')
        gather.say(ai_reply)
        resp.append(gather)
        
    # If the user doesn't say anything or the gather times out, we can loop or end.
    # For now, let's redirect back to voice to keep the line open if they are silent (or you could hangup)
    resp.redirect('/voice')
    
    return Response(content=str(resp), media_type="application/xml")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

from pydantic import BaseModel

from typing import Optional

class ChatRequest(BaseModel):
    message: str
    session_id: str
    image: Optional[str] = None # Base64 encoded image or URL
    business_id: str = "electronics_default"

@app.post("/chat")
async def chat(request: ChatRequest):
    image_url = None
    if request.image:
        # If it's a raw base64 string without prefix, add it
        if request.image.startswith("data:image"):
             image_url = request.image
        else:
             # Assume it's a base64 string and prepend standard header or it's a URL
             # For simplicity, we'll assume the frontend sends a data URL if it's an upload
             image_url = request.image

    ai_text = get_agent_response(request.session_id, request.message, image_url=image_url, business_id=request.business_id)
    return {"response": ai_text}

import base64

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...), session_id: str = Form(...), business_id: str = Form("electronics_default")):
    # 1. Transcribe Audio (STT)
    try:
        # Save to a temporary file instead of mutating file.file.name
        import tempfile
        import shutil

        # Create a temp file with the same extension
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        # Open the temp file for reading
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        
        # Cleanup
        os.remove(tmp_path)
        
        user_text = transcript.text
        print(f"User: {user_text}")
    except Exception as e:
        print(f"STT Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Get AI Response
    ai_text = get_agent_response(session_id, user_text, business_id=business_id)
    print(f"AI: {ai_text}")

    # 3. Generate Audio (TTS)
    audio_content = None
    try:
        audio_content = get_google_tts(ai_text, "en-US") 
    except Exception as e:
        print(f"Google TTS Error: {e}. Falling back to OpenAI.")
        # Fallback to OpenAI
        try:
             response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=ai_text
            )
             audio_content = response.content
        except Exception as oe:
             print(f"OpenAI TTS Error: {oe}")
             raise HTTPException(status_code=500, detail=str(e))

    # Encode to base64
    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
    
    return {
        "user_text": user_text,
        "ai_text": ai_text,
        "audio_base64": audio_base64
    }

class TTSRequest(BaseModel):
    text: str
    language: str = "en-US"

@app.post("/tts")
async def tts_endpoint(request: TTSRequest):
    try:
        audio_content = get_google_tts(request.text, request.language)
        return StreamingResponse(io.BytesIO(audio_content), media_type="audio/mpeg")
    except Exception as e:
        print(f"Google TTS Error: {e}. Falling back to OpenAI.")
        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=request.text
            )
            return StreamingResponse(io.BytesIO(response.content), media_type="audio/mpeg")
        except Exception as oe:
            print(f"OpenAI TTS Error: {oe}")
            raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Admin Endpoints
@app.get("/admin/businesses")
async def list_businesses():
    return business_manager.list_businesses()

class BusinessCreate(BaseModel):
    name: str
    type: str # retail or restaurant
    sheet_id: str
    config: Optional[dict] = {}

@app.post("/admin/businesses")
async def create_business(biz: BusinessCreate):
    return business_manager.create_business(biz.dict())

@app.get("/orders")
async def get_orders(business_id: str = "electronics_default"):
    # This endpoint is tricky because ai_agent.sheets is gone.
    # We need to get the sheets instance for this business via a helper or direct instantiation
    # But for cleaner architecture, we should expose a method in ai_agent or business_manager to get the relevant sheet manager
    # HACK: We will import get_sheets_manager from ai_agent (circular import risk? ai_agent imports sheets_manager, main imports both)
    # Safer: Re-instantiate locally for now or move get_sheets_manager to a shared utility.
    # Given the project structure, I will attempt to import get_sheets_manager from ai_agent (it is inside a function there or I can make it public)
    from ai_agent import get_sheets_manager 
    sheets = get_sheets_manager(business_id)
    if not sheets:
        raise HTTPException(status_code=404, detail="Business not found")
    return sheets.get_orders()

@app.get("/health")
def health():
    return {"status": "ok"}

# Serve React App (Catch-all for SPA)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    # API routes are already handled above. 
    # If a file exists in dist, serve it (e.g. vite.svg), otherwise serve index.html
    possible_file = f"../frontend/dist/{full_path}"
    if os.path.isfile(possible_file):
        return FileResponse(possible_file)
    
    # Fallback to index.html for React Router
    if os.path.exists("../frontend/dist/index.html"):
        return FileResponse("../frontend/dist/index.html")
    
    return {"error": "Frontend not found. Did you run 'npm run build'?"}
