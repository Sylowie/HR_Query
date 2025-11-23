import os
import json
import pdfplumber
import requests

# Base URL for your local Ollama server
OLLAMA_URL = "http://localhost:11434"

# Name of the embedding model used to embed chunks
EMBED_MODEL = "nomic-embed-text"


def get_embedding(text: str):
    """
    Call Ollama's embedding endpoint to get an embedding for a text chunk.

    Args:
        text: The text content of one chunk.

    Returns:
        A Python list of floats representing the embedding vector.
    """
    # Log the first part of the chunk to see what we're embedding (for debugging)
    print("  ▶ Embedding chunk snippet:", repr(text[:80]))

    # Send the text to Ollama's /api/embeddings endpoint
    r = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )

    # Log HTTP status code for visibility
    print("  ◀ Embedding status:", r.status_code)

    # If there was an error response, print the body for debugging
    if not r.ok:
        print("  ❌ Embedding error body:", r.text[:300])

    # Raise an exception if the request failed (4xx/5xx)
    r.raise_for_status()

    # Parse the JSON and return just the "embedding" list
    data = r.json()
    return data["embedding"]


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    """
    Split a long string into overlapping chunks.

    Args:
        text: The full document text to chunk.
        chunk_size: Maximum number of characters per chunk.
        overlap: Number of characters to overlap between consecutive chunks.
                 This helps keep sentences that cross boundaries.

    Yields:
        Individual text chunks (strings).
    """
    # Ensure settings make sense: chunk_size must be larger than overlap
    assert chunk_size > overlap, "chunk_size must be larger than overlap"

    # How far we move the window forward each time
    step = chunk_size - overlap

    n = len(text)
    # Slide a window over the full text
    for start in range(0, n, step):
        end = start + chunk_size
        chunk = text[start:end]
        # Skip completely empty / whitespace-only chunks
        if chunk.strip():
            yield chunk


def pdf_to_text(path: str) -> str:
    """
    Extract text from a PDF file using pdfplumber.

    Args:
        path: Path to the PDF file on disk.

    Returns:
        A single string containing all page texts joined with newlines.
    """
    print(f"📄 Extracting text from: {path}")
    with pdfplumber.open(path) as pdf:
        out = []
        for i, page in enumerate(pdf.pages):
            # Extract text from each page (may be None if it's image-only)
            t = page.extract_text()
            print(f"  Page {i+1}: {'has text' if t else 'NO text'}")
            if t:
                out.append(t)
        # Join all pages into one big string
        return "\n".join(out)


if __name__ == "__main__":
    # Folder where your source PDFs live
    docs_dir = "docs_raw"

    # This will hold all chunks from all PDFs
    all_chunks = []

    print(f"🔍 Scanning folder: {docs_dir}")
    if not os.path.isdir(docs_dir):
        print("❌ docs_raw directory not found!")
        raise SystemExit(1)

    # Loop through every file in docs_raw
    for fname in os.listdir(docs_dir):
        # Only process PDFs
        if not fname.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(docs_dir, fname)
        # Use the filename (without extension) as the doc_id
        # e.g. "29_common_hr_policies_aihr"
        doc_id = os.path.splitext(fname)[0]
        print(f"\n=== Processing {pdf_path} as doc_id={doc_id} ===")

        # 1) Extract text from the PDF
        text = pdf_to_text(pdf_path)
        if not text.strip():
            print("⚠ No text extracted from this PDF, skipping.")
            continue

        # 2) Chunk the text and embed each chunk
        for idx, chunk in enumerate(chunk_text(text)):
            print(f"  📌 Chunk {idx}")
            emb = get_embedding(chunk)

            # Store everything needed for RAG later
            all_chunks.append({
                "id": f"{doc_id}-chunk-{idx}",  # unique chunk id
                "doc_id": doc_id,               # which PDF this chunk came from
                "text": chunk,                  # raw chunk text
                "embedding": emb,               # embedding vector
            })

    # 3) Save all chunks + embeddings into a single JSON index
    os.makedirs("data", exist_ok=True)
    out_path = "data/chunks.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f)

    print(f"\n✅ Indexed {len(all_chunks)} chunks into {out_path}")
