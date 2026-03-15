import os
from pathlib import Path

def load_documents(folder: str = "documents") -> list[dict]:
    """
    Load all .txt and .pdf files from the given folder.
    Returns a list of {"text": ..., "source": ...} dicts.
    """
    docs = []
    folder_path = Path(folder)

    if not folder_path.exists():
        raise FileNotFoundError(f"Documents folder '{folder}' not found.")

    for file_path in folder_path.iterdir():
        if file_path.suffix == ".txt":
            text = file_path.read_text(encoding="utf-8")
            docs.append({"text": text, "source": file_path.name})

        elif file_path.suffix == ".pdf":
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text = "\n".join(
                        page.extract_text() or "" for page in pdf.pages
                    )
                docs.append({"text": text, "source": file_path.name})
            except ImportError:
                print("pdfplumber not installed. Run: pip install pdfplumber")

    print(f"Loaded {len(docs)} document(s) from '{folder}'.")
    return docs


def chunk_documents(docs: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Split documents into smaller overlapping chunks for better retrieval.
    Returns a list of {"text": ..., "source": ..., "chunk_id": ...} dicts.
    """
    chunks = []
    for doc in docs:
        text = doc["text"]
        start = 0
        chunk_id = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "source": doc["source"],
                    "chunk_id": f"{doc['source']}_chunk{chunk_id}",
                })
            start += chunk_size - overlap
            chunk_id += 1

    print(f"Created {len(chunks)} chunk(s) from {len(docs)} document(s).")
    return chunks