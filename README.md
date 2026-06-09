# 🚦 DriveLegal AI

DriveLegal AI is an AI-powered traffic law assistant designed to help citizens understand traffic regulations, challan fines, legal provisions, and road safety requirements. The system provides accurate, source-backed answers using official traffic law documents, government notifications, and state-specific regulations.

## 🎯 Problem Statement

Traffic laws are often difficult to understand and vary across states. Citizens struggle to find accurate information regarding:
- Traffic violations and penalties
- State-specific challan amounts
- Legal provisions and sections
- Required driving documents

DriveLegal AI solves this problem by providing instant, easy-to-understand, and source-backed answers through an intelligent conversational interface.

---

## ✨ Features

### 🤖 AI Traffic Law Assistant
- Natural language question answering
- Context-aware legal explanations
- Simple and user-friendly responses
- **Multi-language Support** (English, Hindi, Bengali, Tamil, Telugu)
- **Voice Input & Auto TTS Readback**

### ⚖️ Traffic Law Information
- Motor Vehicles Act, 1988
- Motor Vehicles (Amendment) Act, 2019
- State-specific traffic regulations (West Bengal, Delhi, Maharashtra, Karnataka)

### 💰 Interactive Challan Calculator
- Calculate exact fines based on violation, vehicle type, and state.
- Handles repeat offenses and multiple violations.

### 🔎 AI E-Challan OCR
- Upload a photo of a physical challan or e-challan.
- AI extracts Violation, Section, Fine Amount, Vehicle details, and provides payment verification steps.

### 📍 Location-Aware Responses
- GPS-based auto-detection of your state for localized traffic law filtering.
- Nearby Help integration via Google Maps.

---

## 🏗️ System Architecture

```text
User Query / Image / Voice
         ↓
  Frontend (React)
         ↓
  FastAPI Backend  <---> SQLite (Direct Fine Lookup)
         ↓
  FAISS Vector Index (Legal Knowledge Base)
         ↓
  Gemini API (RAG Generation)
         ↓
  Response Generation (SSE Streamed)
```

---

## 🛠️ Tech Stack

### Frontend
- React.js (Vite)
- Vanilla CSS (Glassmorphism UI)
- Web Speech API (Voice/TTS)

### Backend
- FastAPI (Python)
- SQLite (Structured rules & fines)
- Server-Sent Events (SSE) for streaming

### AI & RAG
- Gemini Pro / Gemini Flash
- FAISS (Facebook AI Similarity Search)
- LangChain / HuggingFace Embeddings

---

## 📂 Project Structure

```text
DriveLegal/
│
├── frontend/             # React application
│   ├── src/App.tsx       # Main UI & streaming logic
│   └── src/index.css     # UI Styling
│
├── backend/              # FastAPI application
│   ├── app/main.py       # API Endpoints
│   ├── app/services/     # Chat, OCR, and Calculator services
│   ├── ingestion/        # Document parsing & FAISS indexing
│   ├── rag/              # Retrieval & Embedding logic
│   └── scraper/          # Web scrapers for state fines
│
├── data/                 # Golden datasets & generated JSONs
│
├── embeddings/           # Generated FAISS binary indexes
│
├── scripts/              # Evaluation & testing scripts
│
└── README.md
```

---

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/Subhankarnandi777/DriveLegal.git
cd DriveLegal
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r backend/requirements.txt

# Start FastAPI server
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
```

---

## 📜 License
This project is intended for educational and research purposes. Users should verify legal information with official government sources before making legal decisions.

---
⭐ If you found this project useful, consider giving it a star!
