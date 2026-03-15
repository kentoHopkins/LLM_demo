# pip install chromadb pdfplumber openai python-dotenvimport os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import os

from loader import load_documents, chunk_documents
from retriever import build_vector_store, retrieve

# .env is one level above RAG_demo/
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(f"OPENAI_API_KEY not found. Looked for .env at: {dotenv_path}")

openai_client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using only the provided context.
If the answer is not in the context, say you don't know — do not make things up.
Always be concise and cite which document your answer comes from."""


def build_context(chunks: list[str]) -> str:
    """Format retrieved chunks into a context block for the prompt."""
    return "\n\n---\n\n".join(chunks)


def chat(user_input: str, history: list[dict], collection) -> str:
    """
    Run one turn of RAG:
    1. Retrieve relevant chunks for the user's question.
    2. Inject them as context into the message.
    3. Send full conversation history to OpenAI.
    """
    chunks = retrieve(user_input, collection, openai_client)
    context = build_context(chunks)

    # Inject context into the user message
    augmented_message = f"""Context from documents:
{context}

User question: {user_input}"""

    history.append({"role": "user", "content": augmented_message})

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
    )

    answer = response.choices[0].message.content

    # Store the original (non-augmented) user message in history for readability
    history[-1] = {"role": "user", "content": user_input}
    history.append({"role": "assistant", "content": answer})

    return answer


def main():
    # --- Load and index documents ---
    docs = load_documents("documents")
    chunks = chunk_documents(docs)
    collection = build_vector_store(chunks, openai_client)

    # --- Multi-turn chat loop ---
    history = []
    print("\nRAG demo ready. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        answer = chat(user_input, history, collection)
        print(f"\nAssistant: {answer}\n")


if __name__ == "__main__":
    main()

    # Who is the CEO of NovaMind AI?
    # What is the price of the Growth plan?
    # Does FlowMind support Claude models?
    # What discount do nonprofits get?