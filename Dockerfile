# Stage 1: Build the Frontend
FROM node:20-alpine as frontend-build

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2: Setup the Backend
FROM python:3.11-slim

WORKDIR /app/backend

# Install system dependencies if needed (e.g. for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy built frontend assets from Stage 1
# We copy them to a directory that matches the "../frontend/dist" path expected by main.py
# Or we can adjust main.py to look in a local folder by creating the structure:
# /app/backend (WORKDIR)
# /app/frontend/dist

COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Expose the port (Cloud Run typically uses 8080)
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
