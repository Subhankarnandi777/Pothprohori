# DriveLegal AI — RAG Chatbot

This project contains a RAG (Retrieval-Augmented Generation) chatbot for Indian traffic laws and violation fines, built with FastAPI for the backend API and ChromaDB + Gemini for the AI services.

## Repository Layout
- `backend/` - FastAPI web backend.
- `ai-services/` - RAG pipeline, retriever, embedding models, and LLM wrappers.
- `scripts/` - Ingestion and backend runner scripts.

---

## Quick Start (Windows PowerShell)

### 1. Set Up Python Virtual Environment
We recommend using a virtual environment to manage dependencies locally.
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 2. Install Backend & AI Services Dependencies
```powershell
pip install -r backend/requirements.txt
pip install -r ai-services/requirements.txt
```

### 3. Set Your API Keys
Edit `backend/.env` and replace `your_gemini_key_here` with your Google Gemini API Key.
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Ingest Laws into ChromaDB
```powershell
python scripts/ingest_laws.py
```
> **Note:** Without a running ChromaDB Docker container, the indexer automatically falls back to an in-memory client database (data will reset when Python process exits).

### 5. Start the FastAPI API Server
You can start the backend using the provided runner script:
```powershell
.\scripts\run_backend.ps1
```
Or directly run:
```powershell
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Test the Chatbot Endpoint
You can query the chatbot via a curl request:
```bash
curl -X POST http://localhost:8000/chat/ `
  -H "Content-Type: application/json" `
  -d '{"message":"What is the helmet fine in West Bengal?","location":{"state":"West Bengal"}}'
```

### API Interactive Documentation
Visit [http://localhost:8000/docs](http://localhost:8000/docs) once the server starts.

---

## Optional: Run ChromaDB in Docker
To keep your ChromaDB database persistent, run it in Docker:
```bash
docker run -d -p 8001:8000 chromadb/chroma
```
And make sure `CHROMA_HOST=localhost` and `CHROMA_PORT=8001` are specified in `backend/.env`.
