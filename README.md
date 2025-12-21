# ElectroShop Voice Bot

A real-time Voice AI Agent for taking electronics orders.

## Features
- **Voice Interface**: Speak naturally to the agent.
- **Inventory Search**: Real-time lookup from Google Sheets (or Mock Data).
- **Cart Management**: Add multiple items, quantities.
- **Order Placement**: Saves confirmed orders to Google Sheets.

## Setup

### 1. Prerequisites
- **OpenAI API Key**: You need a key from [platform.openai.com](https://platform.openai.com).
- **Google Sheets Credentials** (Optional for Demo):
    - Create a Project in Google Cloud Console.
    - Enable **Google Sheets API** and **Google Drive API**.
    - Create a **Service Account** and download the JSON key.
    - Rename it to `credentials.json` and place it in the `backend/` folder.
    - Share your Inventory and Orders sheets with the Service Account email.

### 2. Configuration
1. Open `backend/.env` and paste your OpenAI API Key:
   ```bash
   OPENAI_API_KEY=sk-proj-...
   ```
2. (Optional) If using real sheets, update `backend/sheets_manager.py` with your Sheet names if they are not "Inventory" and "Orders".

### 3. Run the Application

**Terminal 1: Backend**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
```

Open the URL shown in Terminal 2 (usually `http://localhost:5173`) to interact with the bot.
