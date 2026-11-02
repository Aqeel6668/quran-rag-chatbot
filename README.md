# Quran RAG Chatbot (Local)

A beginner-friendly local Retrieval-Augmented Generation (RAG) project using the complete Quran in Arabic and an English translation.

## Dataset

The downloader fetches two complete editions from the AlQuran Cloud API and joins them by Surah/Ayah number:

- Arabic: `quran-uthmani` (Uthmani script).
- English: `en.sahih` (Saheeh International translation).
- The CSV has one row per ayah, with Arabic and English in separate columns.
- The script checks that both editions contain the same 6,236 unique ayahs across all 114 surahs before writing `data/quran.csv`.

Sources: https://alquran.cloud/api and https://api.alquran.cloud/v1/quran/quran-uthmani . The English text is a translation of the meanings, not the Arabic Quran itself. Preserve source attribution and check the source's current reuse terms before redistributing the dataset.

## Setup (Windows PowerShell)

### 1. Install packages

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Download the complete Quran dataset

Run once from the project folder:

```powershell
python download_quran.py
```

This needs an internet connection. It creates `data/quran.csv` and checks for exactly 6,236 unique ayahs. You do not need to edit the CSV manually.

### 3. Start the local LLM

Install Ollama and run:

```powershell
ollama pull qwen2.5:3b
```

Make sure Ollama is running.

### 4. Build the vector database

```powershell
python embedder.py
```

This downloads the multilingual embedding model the first time and indexes the Arabic and English text in ChromaDB. Run it again whenever the source CSV changes.

### 5. Start the chatbot

```powershell
python app.py
```

Type `exit` to quit.

## How RAG works

1. The multilingual Sentence Transformer converts the question and each verse into embeddings.
2. ChromaDB finds the most similar verse embeddings.
3. ChromaDB returns the original Arabic and English verse text with Surah/Ayah references.
4. `chatbot.py` puts those verses into a prompt.
5. Qwen 2.5:3B, running locally through Ollama, generates an answer from the supplied context.

The LLM receives verse text, not embedding vectors.

## Files

- `download_quran.py`: downloads and validates the complete dataset.
- `data/quran.csv`: generated source dataset (created by the download script).
- `loader.py`: loads and checks the 6,236 ayahs.
- `embedder.py`: creates multilingual embeddings and stores them in ChromaDB.
- `chatbot.py`: retrieves verses and asks Qwen to answer using those verses only.
- `app.py`: terminal interface.
- `vector_db/`: generated ChromaDB database.
- `requirements.txt`: Python dependencies.

## Important limitations

This is an educational RAG prototype, not an authoritative source of religious rulings or Quran interpretation. Search similarity does not prove that a verse answers a question, and the LLM can still make mistakes. Verify the Arabic text, translation, and references against a trusted Quran edition. A translation is not a substitute for the Arabic text.

## Source and reuse terms

AlQuran Cloud API: https://alquran.cloud/api . Editions: `quran-uthmani` and `en.sahih`. Preserve source attribution and check current reuse terms before redistribution.
