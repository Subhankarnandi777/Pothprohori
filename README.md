# 🚦 DriveLegal AI

DriveLegal AI is an AI-powered traffic law assistant designed to help citizens understand traffic regulations, challan fines, legal provisions, and road safety requirements. The system provides accurate, source-backed answers using official traffic law documents, government notifications, and state-specific regulations.

## 🎯 Problem Statement

Traffic laws are often difficult to understand and vary across states. Citizens struggle to find accurate information regarding:

- Traffic violations and penalties
- State-specific challan amounts
- Legal provisions and sections
- Required driving documents
- Road safety compliance
- Traffic-related legal guidance

DriveLegal AI solves this problem by providing instant, easy-to-understand, and source-backed answers through an intelligent conversational interface.

---

## ✨ Features

### 🤖 AI Traffic Law Assistant
- Natural language question answering
- Context-aware legal explanations
- Simple and user-friendly responses

### ⚖️ Traffic Law Information
- Motor Vehicles Act, 1988
- Motor Vehicles (Amendment) Act, 2019
- State-specific traffic regulations
- Government notifications and circulars

### 💰 Challan & Fine Information
- Violation-specific fines
- State-wise penalty lookup
- Challan calculation assistance
- Repeat offense handling

### 📍 Location-Aware Responses
- State-specific traffic laws
- Regional enforcement differences
- Local traffic rule awareness

### 🔎 Legal Document Retrieval (RAG)
- Retrieval-Augmented Generation (RAG)
- Source-backed answers
- Original legal document references
- Reduced hallucinations

### 📚 Source Citation
- Government sources
- Official legal documents
- Transport department notifications
- Traffic police advisories

---

## 🏗️ System Architecture

```text
User Query
     ↓
Frontend (React)
     ↓
FastAPI Backend
     ↓
ChromaDB (Legal Knowledge Base)
     ↓
Gemini/OpenAI
     ↓
Response Generation
```

### Data Flow

```text
Official Government Sources
        ↓
PDF Collection
        ↓
Text Extraction
        ↓
Chunking
        ↓
ChromaDB
        ↓
AI Retrieval
        ↓
User Response
```

---

## 🛠️ Tech Stack

### Frontend
- React.js
- Tailwind CSS
- Axios

### Backend
- FastAPI
- Python

### AI & RAG
- Gemini API / OpenAI API
- ChromaDB
- Sentence Transformers

### Database
- PostgreSQL
- ChromaDB

### Data Processing
- PyPDF
- BeautifulSoup
- Requests

---

## 📂 Project Structure

```text
DriveLegalAI/
│
├── frontend/
│
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── services/
│   └── database/
│
├── data/
│   ├── raw_documents/
│   ├── processed/
│   └── embeddings/
│
├── chroma_db/
│
├── scripts/
│   ├── pdf_extractor.py
│   ├── ingest_data.py
│   └── update_data.py
│
└── README.md
```

---

## 📄 Data Sources

The system uses information from official sources including:

- Ministry of Road Transport and Highways (MoRTH)
- Parivahan Sewa
- State Transport Departments
- Traffic Police Departments
- Government Gazette Notifications
- Motor Vehicles Act, 1988
- Motor Vehicles (Amendment) Act, 2019

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/drivelegal-ai.git

cd drivelegal-ai
```

### Create Virtual Environment

```bash
python -m venv venv

source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Backend

```bash
uvicorn app:app --reload
```

### Start Frontend

```bash
npm install

npm run dev
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_API_KEY

DATABASE_URL=postgresql://username:password@localhost:5432/drivelegal

CHROMA_DB_PATH=./chroma_db
```

---

## 💬 Example Queries

```text
What is the fine for riding without a helmet?

What documents should I carry while driving?

Explain Section 194D.

Calculate challan for no helmet and no driving licence.

What is the penalty for drunk driving?

Compare traffic fines in Delhi and West Bengal.
```

---

## 🎯 Future Enhancements

- Voice-based assistance
- Multi-language support
- Real-time traffic alerts
- Mobile application
- GPS-based traffic law lookup
- Automated legal document updates
- AI-powered challan calculator

---

## 📈 Benefits

- Accurate and reliable legal information
- Reduced misinformation
- Improved road safety awareness
- Easy access to traffic law guidance
- Source-backed legal explanations

---

## 👨‍💻 Team

Developed as part of an AI-powered Legal Traffic Assistant project to improve access to traffic law information and promote safer road usage.

---

## 📜 License

This project is intended for educational and research purposes. Users should verify legal information with official government sources before making legal decisions.

---
⭐ If you found this project useful, consider giving it a star.
