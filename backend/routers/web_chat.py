from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import StreamingResponse
import io
import os
import base64
from openai import OpenAI
from tts_wrapper import get_google_tts
from ai_agent import get_agent_response

router = APIRouter()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    session_id: str
    image: Optional[str] = None # Base64 encoded image or URL
    business_id: str = "electronics_default"

class TTSRequest(BaseModel):
    text: str
    language: str = "en-US"

@router.post("/chat")
def chat(request: ChatRequest):
    image_url = None
    if request.image:
        if request.image.startswith("data:image"):
             image_url = request.image
        else:
             image_url = request.image

    ai_text = get_agent_response(request.session_id, request.message, image_url=image_url, business_id=request.business_id)
    return {"response": ai_text}

@router.post("/process-audio")
def process_audio(file: UploadFile = File(...), session_id: str = Form(...), business_id: str = Form("electronics_default")):
    try:
        import tempfile
        import shutil

        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        
        os.remove(tmp_path)
        
        user_text = transcript.text
        print(f"User: {user_text}")
    except Exception as e:
        print(f"STT Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    ai_text = get_agent_response(session_id, user_text, business_id=business_id)
    print(f"AI: {ai_text}")

    audio_content = None
    try:
        audio_content = get_google_tts(ai_text, "en-US") 
    except Exception as e:
        print(f"Google TTS Error: {e}. Falling back to OpenAI.")
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

    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
    
    return {
        "user_text": user_text,
        "ai_text": ai_text,
        "audio_base64": audio_base64
    }

@router.post("/tts")
def tts_endpoint(request: TTSRequest):
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
