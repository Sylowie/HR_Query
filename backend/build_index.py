# build_index.py
import os, json, pdfplumber, requests

OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"

def get_embedding(text: str):
    # For debugging: show a bit of the text
    print("  ▶ Embedding chunk snippet:", repr(text[:80]))
    r = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    print("  ◀ Embedding status:", r.status_code)
    if not r.ok:
        print("  ❌ Embedding error body:", r.text[:300])
    r.raise_for_status()
    data = r.json()
    return data["embedding"]

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    assert chunk_size > overlap, "chunk_size must be larger than overlap"
    step = chunk_size - overlap

    n = len(text)
    for start in range(0, n, step):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            yield chunk


def pdf_to_text(path: str) -> str:
    print(f"📄 Extracting text from: {path}")
    with pdfplumber.open(path) as pdf:
        out = []
        for i, page in enumerate(pdf.pages):
            t = page.extract_text()
            print(f"  Page {i+1}: {'has text' if t else 'NO text'}")
            if t:
                out.append(t)
        return "\n".join(out)

if __name__ == "__main__":
    docs_dir = "docs_raw"
    all_chunks = []

    print(f"🔍 Scanning folder: {docs_dir}")
    if not os.path.isdir(docs_dir):
        print("❌ docs_raw directory not found!")
        raise SystemExit(1)

    for fname in os.listdir(docs_dir):
        if not fname.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(docs_dir, fname)
        doc_id = os.path.splitext(fname)[0]  # e.g. "29_common_hr_policies_aihr"
        print(f"\n=== Processing {pdf_path} as doc_id={doc_id} ===")

        text = pdf_to_text(pdf_path)
        if not text.strip():
            print("⚠ No text extracted from this PDF, skipping.")
            continue

        for idx, chunk in enumerate(chunk_text(text)):
            print(f"  📌 Chunk {idx}")
            emb = get_embedding(chunk)
            all_chunks.append({
                "id": f"{doc_id}-chunk-{idx}",
                "doc_id": doc_id,
                "text": chunk,
                "embedding": emb,
            })

    os.makedirs("data", exist_ok=True)
    out_path = "data/chunks.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f)

    print(f"\n✅ Indexed {len(all_chunks)} chunks into {out_path}")
