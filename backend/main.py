from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv

# Import Routers
from routers import web_chat, whatsapp, twilio_voice, admin

load_dotenv()

app = FastAPI()

# Mount the React build directory (static files)
# In Docker, we'll copy frontend/dist to /app/static or similar
# Local dev fallback: ../frontend/dist
if os.path.exists("../frontend/dist"):
    app.mount("/assets", StaticFiles(directory="../frontend/dist/assets"), name="assets")

# Restarting connection to verify API status
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(web_chat.router)
app.include_router(whatsapp.router)
app.include_router(twilio_voice.router)
app.include_router(admin.router)

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
