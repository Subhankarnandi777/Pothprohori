<div align="center">
  <h1>🚦 Pothprohori</h1>
  <p><strong>Your Intelligent, AI-Powered Traffic Law Assistant</strong></p>
</div>

<p align="center">
  Pothprohori is a comprehensive AI-powered traffic law assistant designed to empower citizens by making traffic regulations, challan fines, legal provisions, and road safety requirements easy to understand. Using advanced RAG (Retrieval-Augmented Generation) and official legal documents, it provides accurate, source-backed, and state-specific answers.
</p>

---

## 🎯 Problem Statement

Traffic laws are notoriously complex, deeply bureaucratic, and vary significantly across different states. Citizens frequently struggle to access and understand accurate information regarding:
- Specific traffic violations and their corresponding penalties.
- State-specific challan amounts that differ from central rules.
- The exact legal provisions, acts, and sections associated with offenses.
- Required driving documents and compliance standards for different vehicle types.

## 💡 The Solution

Pothprohori bridges this gap by acting as a virtual legal assistant. It provides instant, easy-to-understand, and source-backed answers through a highly intelligent, conversational interface, eliminating the need to read through dense legal documents manually.

---

## ✨ Key Features

### 🤖 AI Traffic Law Assistant
- **Natural Language Question Answering:** Ask complex legal questions in plain language and get accurate answers.
- **Context-Aware Legal Explanations:** Understand the *why* behind a law, not just the rule itself.
- **Multi-language Support:** Fully localized for English, Hindi, Bengali, Tamil, and Telugu to serve a diverse population.
- **Accessibility First:** Integrated Voice Input and Auto Text-to-Speech (TTS) readback.

### ⚖️ Comprehensive Legal Knowledge Base
- Trained on the **Motor Vehicles Act, 1988** and **Motor Vehicles (Amendment) Act, 2019**.
- Deep integration of **State-specific traffic regulations** (including West Bengal, Delhi, Maharashtra, and Karnataka).

### 💰 Interactive Challan Calculator
- Accurately calculate fines based on the specific violation, vehicle category, and state jurisdiction.
- Intelligently handles compound scenarios like repeat offenses and simultaneous multiple violations.

### 🔎 AI E-Challan OCR
- **Image Upload:** Upload a photo of a physical challan or a screenshot of an e-challan.
- **Automated Extraction:** The AI instantly extracts the Violation, Section, Fine Amount, and Vehicle details.
- **Actionable Advice:** Provides step-by-step guidance on how to verify and pay the challan online.

### 📍 Location-Aware Responses
- GPS-based auto-detection of your current state to seamlessly filter local traffic laws.
- Nearby Help integration via Google Maps for immediate roadside or legal assistance.

---

## 🏗️ System Architecture

Pothprohori employs a modern Retrieval-Augmented Generation (RAG) architecture to ensure responses are grounded in actual law.

```text
User Query / Image / Voice
         ↓
  Frontend (React + Tailwind CSS)
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
- **React.js (Vite):** Fast, modern, and reactive UI framework.
- **Tailwind CSS:** Utility-first CSS framework for a sleek, responsive design.
- **Web Speech API:** For seamless Voice-to-Text and Text-to-Speech integration.

### Backend
- **FastAPI (Python):** High-performance backend framework for serving the API.
- **SQLite:** Lightweight relational database for structured rules and fine lookups.
- **Server-Sent Events (SSE):** For streaming AI responses back to the client in real-time.

### AI & Data Pipeline
- **Google Gemini API:** Core LLM for reasoning and response generation.
- **FAISS:** Facebook AI Similarity Search for hyper-fast vector retrieval.
- **LangChain / HuggingFace:** Embedding generation and RAG orchestration.

---

## 📂 Project Structure

```text
Pothprohori/
│
├── frontend/             # React application (Vite + Tailwind)
│   ├── src/App.tsx       # Main UI & streaming logic
│   └── src/index.css     # Global styles & Tailwind directives
│
├── backend/              # FastAPI application
│   ├── app/main.py       # API Endpoints & Routes
│   ├── app/services/     # Core logic (Chat, OCR, Calculator)
│   ├── ingestion/        # Document parsing & FAISS indexing scripts
│   ├── rag/              # Retrieval & Embedding orchestration
│   └── scraper/          # Web scrapers for up-to-date state fines
│
├── data/                 # Golden datasets & generated JSONs
├── embeddings/           # Generated FAISS binary indexes
├── scripts/              # Evaluation, testing, and deployment scripts
└── README.md             # Project documentation
```

---

## 🚀 Getting Started

Follow these instructions to get a local copy of Pothprohori up and running.

### 1. Clone the Repository
```bash
git clone https://github.com/Subhankarnandi777/Pothprohori.git
cd Pothprohori
```

### 2. Backend Setup
We recommend using a virtual environment to manage dependencies.

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install required Python packages
pip install -r backend/requirements.txt

# Start the FastAPI development server
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
*The API will be available at `http://localhost:8000`*

### 3. Frontend Setup
Open a new terminal window/tab to run the frontend client.

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the Vite development server
npm run dev
```
*The UI will be available at `http://localhost:5173`*

---

## 🔑 Environment Variables

To run the AI features, you will need a valid API key. Create a `.env` file in the root `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🤝 Contributing

We welcome contributions to make Pothprohori even better! 
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is intended for educational and research purposes. Users should verify legal information with official government sources before making legal decisions.

---
<div align="center">
  <i>⭐ If you found this project useful or insightful, please consider giving it a star!</i>
</div>
