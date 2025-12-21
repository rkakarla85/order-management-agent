from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
import io
import os
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()

from openai import OpenAI
from ai_agent import get_agent_response

app = FastAPI()

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
    response_text = get_agent_response(sender_id, incoming_msg)

    # Create Twilio XML response
    twilio_resp = MessagingResponse()
    twilio_resp.message(response_text)
    
    return Response(content=str(twilio_resp), media_type="application/xml")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.post("/chat")
async def chat(request: ChatRequest):
    ai_text = get_agent_response(request.session_id, request.message)
    return {"response": ai_text}

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...), session_id: str = Form(...)):
    # 1. Transcribe Audio (STT)
    try:
        # Save temp file because OpenAI client needs a file-like object with name or path
        # But we can pass the file.file directly if it has a name
        file.file.name = file.filename # Ensure it has a name for format detection
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=file.file
        )
        user_text = transcript.text
        print(f"User: {user_text}")
    except Exception as e:
        print(f"STT Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Get AI Response
    ai_text = get_agent_response(session_id, user_text)
    print(f"AI: {ai_text}")

    # 3. Generate Audio (TTS)
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=ai_text
        )
        
        # Stream the audio back
        return StreamingResponse(io.BytesIO(response.content), media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from ai_agent import sheets

@app.get("/orders")
async def get_orders():
    return sheets.get_orders()

@app.get("/health")
def health():
    return {"status": "ok"}
