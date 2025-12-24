from fastapi import APIRouter, Request, Response, Form
from typing import Optional
from twilio.twiml.voice_response import VoiceResponse, Gather
from ai_agent import get_agent_response

router = APIRouter()

@router.post("/voice")
def voice_webhook(SpeechResult: Optional[str] = Form(None), CallSid: str = Form(...)):
    """
    Handle incoming Voice calls from Twilio
    """
    user_speech = SpeechResult
    call_sid = CallSid
    
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
