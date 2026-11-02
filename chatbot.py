
import re
from pathlib import Path

import chromadb
import ollama
from sentence_transformers import SentenceTransformer

DB_PATH = Path(__file__).parent / "vector_db"
COLLECTION_NAME = "quran"

EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
LLM_MODEL = "qwen2.5:3b"

VECTOR_CANDIDATES = 40
KEYWORD_CANDIDATES = 40
FINAL_TOP_K = 12
RRF_K = 60

STOP_WORDS = {
    "what", "does", "the", "quran", "say", "about", "how",
    "can", "should", "why", "is", "are", "do", "we",
    "in", "of", "to", "and", "a", "an", "for", "on",
    "tell", "me", "according", "with", "from"
}

# Basic topic expansion to improve English keyword retrieval.
SYNONYMS = {
    "parent": {"parents", "mother", "father"},
    "parents": {"parent", "mother", "father"},
    "wife": {"wives", "spouse", "marriage"},
    "wives": {"wife", "spouse", "marriage"},
    "justice": {"just", "fair", "fairness", "equity"},
    "just": {"justice", "fair", "fairness"},
    "lie": {"lies", "lying", "falsehood", "deceit"},
    "lies": {"lie", "lying", "falsehood", "deceit"},
    "lying": {"lie", "lies", "falsehood"},
    "truth": {"truthful", "honesty", "honest"},
    "honesty": {"truth", "truthful"},
}

_embedding_model = SentenceTransformer(EMBEDDING_MODEL)
_client = chromadb.PersistentClient(path=str(DB_PATH))

try:
    _collection = _client.get_collection(COLLECTION_NAME)
except Exception as exc:
    raise RuntimeError(
        "Quran database not found. Run download_quran.py "
        "and embedder.py first."
    ) from exc


def tokenize(text):
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    return {
        word for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def expand_query(question):
    terms = tokenize(question)
    expanded = set(terms)

    for term in terms:
        expanded.update(SYNONYMS.get(term, set()))

    return expanded


def retrieve_verses(question):
    count = _collection.count()

    if count == 0:
        return []

    # 1. Semantic search
    query_vector = _embedding_model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    vector_results = _collection.query(
        query_embeddings=[query_vector],
        n_results=min(VECTOR_CANDIDATES, count),
        include=["documents", "metadatas", "distances"]
    )

    vector_ids = vector_results["ids"][0]
    vector_docs = vector_results["documents"][0]
    vector_metas = vector_results["metadatas"][0]
    vector_distances = vector_results["distances"][0]

    candidates = {}
    vector_ranks = {}

    for rank, (doc_id, doc, meta, distance) in enumerate(
        zip(vector_ids, vector_docs, vector_metas, vector_distances),
        start=1
    ):
        candidates[doc_id] = {
            "document": doc,
            "metadata": meta,
            "distance": float(distance)
        }
        vector_ranks[doc_id] = rank

    # 2. Keyword search across the complete Quran database
    all_verses = _collection.get(
        include=["documents", "metadatas"]
    )

    query_terms = expand_query(question)
    keyword_matches = []

    for doc_id, doc, meta in zip(
        all_verses["ids"],
        all_verses["documents"],
        all_verses["metadatas"]
    ):
        document_terms = tokenize(doc)
        score = len(query_terms.intersection(document_terms))

        if score > 0:
            keyword_matches.append(
                (score, doc_id, doc, meta)
            )

    keyword_matches.sort(
        key=lambda item: (
            -item[0],
            item[3]["surah"],
            item[3]["ayah"]
        )
    )

    keyword_ranks = {}

    for rank, (_, doc_id, doc, meta) in enumerate(
        keyword_matches[:KEYWORD_CANDIDATES],
        start=1
    ):
        keyword_ranks[doc_id] = rank

        if doc_id not in candidates:
            candidates[doc_id] = {
                "document": doc,
                "metadata": meta,
                "distance": None
            }

    # 3. Combine semantic and keyword rankings using RRF
    combined_scores = {}

    for doc_id in candidates:
        score = 0

        if doc_id in vector_ranks:
            score += 1 / (RRF_K + vector_ranks[doc_id])

        if doc_id in keyword_ranks:
            score += 1 / (RRF_K + keyword_ranks[doc_id])

        combined_scores[doc_id] = score

    ranked_ids = sorted(
        combined_scores,
        key=lambda doc_id: combined_scores[doc_id],
        reverse=True
    )

    return [
        (doc_id, candidates[doc_id])
        for doc_id in ranked_ids[:FINAL_TOP_K]
    ]


def ask(question: str):
    question = question.strip()

    if not question:
        return "Please enter a question.", []

    matches = retrieve_verses(question)

    if not matches:
        return "No relevant Quran verses were found.", []

    context_parts = []
    sources = []

    for doc_id, item in matches:
        meta = item["metadata"]
        doc = item["document"]

        surah = meta["surah"]
        ayah = meta["ayah"]

        context_parts.append(
            f"Surah {surah}, Ayah {ayah}:\n{doc}"
        )

        distance = item["distance"]

        sources.append({
            "surah": surah,
            "ayah": ayah,
            "cosine_distance": (
                round(distance, 4)
                if distance is not None else 1.0
            )
        })

    prompt = f"""
You are a knowledgeable and careful Quran question-answering assistant.

Your task is to explain what the Quran teaches about the user's question.

ANSWERING INSTRUCTIONS:

1. Answer in clear, natural English.

2. Do not merely list verses. Explain their meaning and the
   guidance they provide.

3. If the question contains multiple topics, create a separate
   heading for each topic and explain each one.

4. Explain the practical lessons a person can learn from
   the retrieved verses.

5. Use the English translations to explain the meaning.
   Include the Arabic text when useful.

6. Give the exact Surah and Ayah references for every
   Quranic point you discuss.

7. You may explain the meaning of the supplied verses in
   your own words, but do not invent Quranic teachings.

8. Do not invent quotations, references, or verse meanings.

9. Do not present your own interpretation as a direct
   quotation from the Quran.

10. If the retrieved verses do not adequately support
    a topic, clearly say that the available retrieved
    verses are insufficient to answer that part.

11. Do not claim that the retrieved verses represent
    every Quranic teaching on a topic.

12. Finish with a short practical summary.

Use this answer structure when appropriate:

## Introduction

Briefly introduce the Quranic guidance relevant to the question.

## Main teachings

Explain each relevant topic separately.
Include its Quranic references.

## Practical lessons

Explain what the reader can learn and apply.

## Quranic references

List the references used.

QURAN CONTEXT:

{chr(10).join(context_parts)}

USER QUESTION:

{question}

Now provide a clear, detailed, well-organized answer.
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        options={
            "temperature": 0.2,
            "num_predict": 800
        }
    )

    answer = response["message"]["content"].strip()

    return answer, sources
