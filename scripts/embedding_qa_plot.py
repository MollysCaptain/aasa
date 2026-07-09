"""
Card 2.2, Optional — visually sanity-check the embedding space.
Not part of the shipped app; a dev-time-only QA check.

Run after scripts/embed_cases.py has populated ./chroma_store.
Run directly:  python3 scripts/embedding_qa_plot.py
Produces:      data/embedding_qa_plot.png
"""
import chromadb
import matplotlib.pyplot as plt
from chromadb.utils import embedding_functions
from sklearn.decomposition import PCA

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_collection("aasa_cases", embedding_function=embedding_fn)

# Pull back the stored embeddings + metadata (Chroma keeps both).
data = collection.get(include=["embeddings", "metadatas"], limit=500)  # sample 500 for a fast, readable plot
embeddings = data["embeddings"]
industries = [m["industry"] for m in data["metadatas"]]  # now one of 3 chunk_types per case — fine for a rough visual check

coords_2d = PCA(n_components=2).fit_transform(embeddings)

# Color by industry so real clusters (if any) become visible.
unique_industries = sorted(set(industries))
color_map = {industry: i for i, industry in enumerate(unique_industries)}
colors = [color_map[industry] for industry in industries]

plt.figure(figsize=(10, 7))
scatter = plt.scatter(coords_2d[:, 0], coords_2d[:, 1], c=colors, cmap="tab20", alpha=0.6, s=15)
plt.title("Case embeddings, projected to 2D (colored by industry)")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.savefig("data/embedding_qa_plot.png", dpi=150)
print("Saved data/embedding_qa_plot.png — open it and look for industry clusters.")
