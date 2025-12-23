# WhatsApp Integration Setup Guide

Your agent is already configured to handle WhatsApp messages via Twilio! Follow these steps to connect it to the real world.

## Prerequisites

1.  **Twilio Account**: Sign up at [twilio.com](https://www.twilio.com/).
2.  **Ngrok**: A tool to expose your local server to the internet.
3.  **Python Environment**: Ensure you are in the `backend` directory and your virtual environment is active.

## Step 1: Install Dependencies

We've added `twilio` to your `requirements.txt`. Install it:

```bash
pip install -r requirements.txt
```

## Step 2: Run the Backend Server

Start your FastAPI server. Make sure you are in the `backend` folder:

```bash
uvicorn main:app --reload
```

Your server will be running at `http://127.0.0.1:8000`.

## Step 3: Expose Localhost with Ngrok

In a new terminal window, run ngrok to create a public URL for your local server:

```bash
ngrok http 8000
```

Copy the `Forwarding` URL (e.g., `https://a1b2-c3d4.ngrok-free.app`).

## Step 4: Configure Twilio Sandbox

1.  Go to the [Twilio Console](https://console.twilio.com/).
2.  Navigate to **Messaging** > **Try it out** > **Send a WhatsApp message**.
3.  Follow the instructions to join the sandbox (usually sending a code like `join <word>` to the sandbox number).
4.  Go to **Messaging** > **Settings** > **WhatsApp Sandbox Settings**.
5.  In the "When a message comes in" field, paste your ngrok URL and append `/whatsapp`.
    *   Example: `https://a1b2-c3d4.ngrok-free.app/whatsapp`
6.  Set the method to **POST**.
7.  Click **Save**.

## Step 5: Test It!

1.  Open WhatsApp on your phone.
2.  Send a message to the Twilio Sandbox number (the one you joined in Step 4).
3.  Try saying: "Hi, do you have any fans?"
4.  The agent should reply!

## Troubleshooting

*   **500 Error**: Check your terminal running `uvicorn` for python errors.
*   **Twilio Error**: Check the Twilio Debugger in the console for webhook failures.
*   **Inventory Issues**: If the agent can't find items, ensure `credentials.json` is present or rely on the mock data fallback.
