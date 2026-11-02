from chatbot import ask

def main():
    print("Quran RAG Chatbot")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("Ask: ").strip()
            if question.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break
            if not question:
                continue

            answer, sources = ask(question)
            print("\nAnswer:")
            print(answer)

            if sources:
                print("\nRetrieved sources:")
                for source in sources:
                    print(
                        f"- Surah {source['surah']}, Ayah {source['ayah']} "
                        f"(distance: {source['cosine_distance']})"
                    )
            print()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as exc:
            print(f"\nError: {exc}")
            print("Check that Ollama is running and Qwen is installed.\n")

if __name__ == "__main__":
    main()
