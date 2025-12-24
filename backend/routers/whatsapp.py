from fastapi import APIRouter, Request, Response, Form
from twilio.twiml.messaging_response import MessagingResponse
from ai_agent import get_agent_response

router = APIRouter()

@router.post("/whatsapp")
def whatsapp_webhook(Body: str = Form(""), From: str = Form("")):
    """
    Handle incoming WhatsApp messages from Twilio
    """
    incoming_msg = Body.strip()
    sender_id = From

    print(f"WhatsApp Message from {sender_id}: {incoming_msg}")

    # Use the sender_id as the session_id so the conversation persists for this user
    response_text = get_agent_response(sender_id, incoming_msg, business_id="electronics_default")

    # Create Twilio XML response
    twilio_resp = MessagingResponse()
    twilio_resp.message(response_text)
    
    return Response(content=str(twilio_resp), media_type="application/xml")
