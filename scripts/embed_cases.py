"""
Card 2.2, Step 2 — Embed the metadata-enriched chunks into a local, persistent
Chroma vector store, using an explicitly-named local HuggingFace embedding model
(same model Chroma would use by default — named here so it's a provable, not
coincidental, match with the colleague's branch decision in PLANNING.md).

Run directly:  python3 scripts/embed_cases.py
Reads:         data/use_cases_chunks.jsonl (from Step 1)
Produces:      a ./chroma_store/ folder on disk (the vector database files)
"""
import json
import chromadb
from chromadb.utils import embedding_functions

CHUNKS_PATH = "data/use_cases_chunks.jsonl"
CHROMA_PATH = "./chroma_store"
COLLECTION_NAME = "atsa_cases"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def load_chunks(path: str):
    with open(path) as f:
        return [json.loads(line) for line in f]


def main():
    chunks = load_chunks(CHUNKS_PATH)

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # get_or_create_collection: safe to re-run this script without erroring on a duplicate.
    # embedding_function must be passed consistently every time this collection is opened.
    collection = client.get_or_create_collection(COLLECTION_NAME, embedding_function=embedding_fn)

    documents, metadatas, ids = [], [], []
    for i, chunk in enumerate(chunks):
        documents.append(chunk["text"])
        meta = chunk["metadata"]
        metadatas.append({
            "case_id": str(meta["case_id"]),
            "organization": str(meta["organization"]),
            "title": str(meta["title"]),
            "industry": str(meta["industry"]),
            "domain": str(meta["domain"]),
            "canonical_tools": ",".join(meta["tools"]),  # Chroma metadata must be simple types
            "source_url": str(meta["source_url"]),
            "chunk_type": meta["chunk_type"],
        })
        ids.append(f"chunk-{i}")

    # Chroma enforces a hard max batch size per add() call (client.get_max_batch_size(),
    # e.g. 5461) — with 9,069 chunks (3,023 cases x 3), a single add() call exceeds that,
    # so this splits into batches under the limit. add() will error on duplicate ids if
    # you re-run — for a clean re-run, delete the ./chroma_store folder first, or switch
    # to collection.upsert(...) instead.
    max_batch_size = client.get_max_batch_size()
    total = len(documents)
    for start in range(0, total, max_batch_size):
        end = min(start + max_batch_size, total)
        collection.add(
            documents=documents[start:end],
            metadatas=metadatas[start:end],
            ids=ids[start:end],
        )
        print(f"  added batch {start}-{end} of {total}")

    print(f"Embedded {collection.count()} chunks into Chroma at {CHROMA_PATH}")

    # --- Sanity-check retrieval quality with a test query ---
    test_query = "customer service chatbot for an e-commerce company"
    results = collection.query(query_texts=[test_query], n_results=5)
    print(f"\nTop 5 matches for: '{test_query}'")
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print(f"- [{meta['chunk_type']}][{meta['industry']}] tools={meta['canonical_tools']} :: {doc[:120]}...")


if __name__ == "__main__":
    main()
