# ElectroShop Omni-Channel Agent

A real-time AI Agent for taking electronics orders via Web (Text/Voice/Image), WhatsApp, and Phone Calls.

## Features
- **Active Listening (Voice Mode)**: Continuous, hands-free voice conversation loop (Web).
- **Visual Intelligence**: Upload images of items for the agent to identify and search in inventory.
- **Omni-Channel Support**:
    - **Web**: Rich UI with Voice & Image support.
    - **WhatsApp**: Text-based ordering via Twilio.
    - **Phone**: Full voice conversational agent via Twilio Voice.
- **Inventory & Orders**: Real-time read/write to Google Sheets.

## Setup

### 1. Prerequisites
- **OpenAI API Key**: Required for GPT-4o (Vision & Chat) and Whisper (STT).
- **Twilio Account** (Optional): For WhatsApp and Phone integration.
- **Google Sheets Credentials**:
    - Place `credentials.json` in the `backend/` folder.
    - Share your Sheets with the Service Account email.

### 2. Configuration
1. **Environment Variables**:
   Create `backend/.env`:
   ```bash
   OPENAI_API_KEY=sk-...
   ```
2. **Install Dependencies**:

   **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

   **Frontend**:
   ```bash
   cd frontend
   npm install
   ```

### 3. Run the Application

**Terminal 1: Backend**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
```

**Terminal 3: Tunnel (For WhatsApp/Voice)**
```bash
ngrok http 8000
```

### 4. Usage Drivers

- **Web App**: Open `http://localhost:5173`.
    - Click **Mic** for continuous voice chat.
    - Click **Image Icon** to upload and query products visually.
- **WhatsApp**: See [WHATSAPP_SETUP.md](./backend/WHATSAPP_SETUP.md).
- **Phone Call**: See [VOICE_SETUP.md](./backend/VOICE_SETUP.md).

## Project Structure
- `backend/`: FastAPI server, AI Logic, Google Sheets integration.
- `frontend/`: React app with Voice/Image UI components.
