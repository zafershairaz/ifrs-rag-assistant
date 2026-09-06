import json
from pathlib import Path

import faiss
import numpy as np


CHUNKS_FILE = "data/processed/chunks.json"
EMBEDDINGS_FILE = "data/processed/embeddings.npy"
INDEX_FILE = "vectorstore/ifrs.index"


def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_embeddings():
    return np.load(EMBEDDINGS_FILE)


def build_faiss_index(embeddings):
    """
    Build a FAISS similarity-search index.

    IndexFlatIP uses inner product similarity.
    Embeddings are normalized first, making this equivalent
    to cosine similarity.
    """

    embeddings = embeddings.astype("float32")

    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index


if __name__ == "__main__":

    print("Loading chunks...")
    chunks = load_chunks()

    print("Loading embeddings...")
    embeddings = load_embeddings()

    print(f"Embedding shape: {embeddings.shape}")

    print("Building FAISS index...")

    index = build_faiss_index(
        embeddings
    )

    Path("vectorstore").mkdir(
        exist_ok=True
    )

    faiss.write_index(
        index,
        INDEX_FILE
    )

    print("FAISS index created successfully.")
    print(f"Number of vectors: {index.ntotal}")
    print(f"Index saved to: {INDEX_FILE}")