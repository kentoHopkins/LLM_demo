import os
import chromadb
from openai import OpenAI

# --- Configuration ---
COLLECTION_NAME = "rag_demo"
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K = 3  # Number of chunks to retrieve per query


def get_embedding(texts: list[str], client: OpenAI) -> list[list[float]]:
    """Get OpenAI embeddings for a list of texts."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def build_vector_store(chunks: list[dict], openai_client: OpenAI) -> chromadb.Collection:
    """
    Embed all chunks and store them in a local ChromaDB collection.
    If the collection already exists, it will be replaced.
    """
    chroma_client = chromadb.PersistentClient(path=".chromadb")

    # Clear existing collection so re-runs start fresh
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(COLLECTION_NAME)

    texts = [chunk["text"] for chunk in chunks]
    ids = [chunk["chunk_id"] for chunk in chunks]
    metadatas = [{"source": chunk["source"]} for chunk in chunks]

    # Embed in batches of 100 (OpenAI limit)
    batch_size = 100
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        all_embeddings.extend(get_embedding(batch, openai_client))

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=all_embeddings,
        metadatas=metadatas,
    )

    print(f"Vector store built with {len(chunks)} chunks.")
    return collection


def retrieve(query: str, collection: chromadb.Collection, openai_client: OpenAI) -> list[str]:
    """
    Retrieve the top-K most relevant chunks for a given query.
    Returns a list of text strings.
    """
    query_embedding = get_embedding([query], openai_client)[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=["documents", "metadatas"],
    )

    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]

    print(f"\n  [retrieved {len(chunks)} chunk(s): {', '.join(set(sources))}]")
    return chunks