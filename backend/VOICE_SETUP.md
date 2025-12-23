# Voice Assistant Setup Guide

Your agent can now handle real phone calls using Twilio Voice!

## Logic Flow
1.  **Incoming Call** -> Hits `/voice` webhook.
2.  **Transcribe**: Twilio listens to the user (`<Gather input="speech">`) and converts speech to text.
3.  **Process**: The text is sent back to your `/voice` endpoint.
4.  **AI Reply**: Your agent generates a text response.
5.  **Speak**: Twilio converts the AI text to speech (`<Say>`) and plays it to the caller.

## Step 1: Ensure Server is Running and Exposed
You should already have this from the WhatsApp setup:
1.  **Backend Running**: `uvicorn main:app --reload` (port 8000)
2.  **Ngrok Running**: `ngrok http 8000` (port 8000)

## Step 2: Configure Twilio Voice

1.  Go to the [Twilio Console](https://console.twilio.com/).
2.  Navigate to **Phone Numbers** > **Manage** > **Active Numbers**.
    *   *If you don't have a phone number, buy one (trial accounts get one free).*
3.  Click on your phone number to edit its settings.
4.  Scroll down to the **Voice & Fax** section.
5.  **A Call Comes In**:
    *   Select **Webhook**.
    *   URL: Paste your ngrok URL and append `/voice`.
        *   Example: `https://a1b2-c3d4.ngrok-free.app/voice`
    *   HTTP Method: **POST**.
6.  Click **Save**.

## Step 3: Test It!

1.  Call your Twilio phone number from your real mobile phone.
2.  You should hear: "Welcome to the Application. How can I help you place an order today?"
3.  Say something like: "I need to buy 5 switches."
4.  Wait a moment (Twilio detects silence to know when you're done).
5.  The agent should reply!

## Troubleshooting

*   **"An application error has occurred"**:
    *   Check your ngrok terminal. Did it receive a POST /voice request?
    *   Check your uvicorn terminal. Did it error out?
    *   Ensure the URL in Twilio settings is exactly right (https, no typos).
*   **Silence / No Reply**:
    *   Twilio's `<Gather>` can sometimes be slow to detect "end of speech".
    *   Ensure you speak clearly.
    *   Check `ai_agent.py` logs to see if the AI generated a response.
