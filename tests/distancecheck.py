import chromadb
from chromadb.utils import embedding_functions

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_collection("aasa_cases", embedding_function=embedding_fn)

queries = [
    ("plausible", "Customer Service in the Technology industry"),
    ("plausible", "Data & Analytics in the Healthcare industry"),
    ("plausible", "Facilities & EHS in the Agriculture industry"),
    ("plausible", "HR in the Financial Services industry"),
    ("nonsense", "quantum toaster repair scheduling for underwater basket weavers"),
    ("nonsense", "medieval calligraphy pricing for pet grooming salons"),
    ("nonsense", "competitive yodeling championship logistics"),
    ("nonsense", "haunted lighthouse tour guide certification"),
]
for label, q in queries:
    r = collection.query(query_texts=[q], n_results=15)
    dists = r["distances"][0]
    print(f"{label:10s} {q!r}: min={min(dists):.3f} max={max(dists):.3f} top5={[round(d,3) for d in dists[:5]]}")