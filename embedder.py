from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from loader import load_quran

DB_PATH = Path(__file__).parent / "vector_db"
COLLECTION_NAME = "quran"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def main():
    verses = load_quran()
    print(f"Loading multilingual embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=str(DB_PATH))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    batch_size = 64
    for start in range(0, len(verses), batch_size):
        batch = verses[start:start + batch_size]
        # One multilingual embedding can match questions in Arabic or English.
        texts = [
            f"{row['english_translation']}\n{row['arabic_text']}"
            for row in batch
        ]
        embeddings = model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        ).tolist()
        ids = [f"{int(row['surah'])}:{int(row['ayah'])}" for row in batch]
        metadatas = [
            {"surah": int(row["surah"]), "ayah": int(row["ayah"])}
            for row in batch
        ]
        documents = [
            f"English translation: {row['english_translation']}\n"
            f"Arabic: {row['arabic_text']}"
            for row in batch
        ]
        collection.add(
            ids=ids, embeddings=embeddings,
            documents=documents, metadatas=metadatas
        )
        print(f"Indexed {min(start + batch_size, len(verses))}/{len(verses)} ayahs")

    print(f"Done. Indexed all {len(verses)} ayahs into ChromaDB.")


if __name__ == "__main__":
    main()
