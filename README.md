# Quran RAG Chatbot

A local Quran-based Retrieval-Augmented Generation (RAG) chatbot that answers questions using Arabic Quranic verses and Sahih International English translation.

## Tech Stack
- **Backend:** Python, FastAPI
- **Frontend:** React, TypeScript, Vite
- **Vector Database:** ChromaDB
- **Embeddings:** Sentence Transformers
- **LLM:** Qwen 2.5 3B via Ollama

## Features
- Complete Quran dataset (6,236 ayahs, 114 surahs).
- Multilingual semantic search.
- Relevant verse retrieval with references.
- Locally generated answers using retrieved context.
- React-based chat interface.

## Setup

**1. Clone the repository**
```powershell
git clone https://github.com/Aqeel6668/quran-rag-chatbot.git
cd quran-rag-chatbot
```

**2. Install Python dependencies**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**3. Download the Quran dataset**
```powershell
python download_quran.py
```

**4. Download the local LLM**
```powershell
ollama pull qwen2.5:3b
```

**5. Build the vector database**
```powershell
python embedder.py
```

**6. Start the backend**
```powershell
uvicorn server:app --reload
```

**7. Start the frontend** (in a second terminal)
```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

## How It Works
1. User submits a question.
2. Sentence Transformers creates an embedding.
3. ChromaDB retrieves relevant Quranic verses.
4. Retrieved verses are passed to Qwen.
5. The model generates a context-based answer.

## Dataset Source
[AlQuran Cloud API](https://alquran.cloud/api)

Editions: `quran-uthmani` and `en.sahih`.

## Disclaimer
This is an educational project, not an authoritative source of religious rulings or Quran interpretation. Always verify verses, translations, and references against a trusted Quran edition.