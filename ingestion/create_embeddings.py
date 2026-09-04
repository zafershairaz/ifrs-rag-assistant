import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

INPUT_FILE = "data/processed/chunks.json"
OUTPUT_FILE = "data/processed/embeddings.npy"


def load_chunks(file_path):
    """Load chunks from JSON."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def prepare_text_for_embedding(chunk):
    """
    Create contextual text for embedding.

    Metadata is included so the embedding model
    understands the source context.
    """

    return (
        f"Standard: {chunk['standard']}\n"
        f"Paragraph: {chunk['paragraph']}\n"
        f"Text: {chunk['text']}"
    )


def create_embeddings(chunks):
    """
    Create embeddings for all document chunks.
    """

    model = SentenceTransformer(
        MODEL_NAME
    )

    texts = [
        prepare_text_for_embedding(chunk)
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    )

    return embeddings


if __name__ == "__main__":

    print("Loading chunks...")

    chunks = load_chunks(
        INPUT_FILE
    )

    print(
        f"Chunks loaded: {len(chunks)}"
    )

    print(
        "Preparing text for embeddings..."
    )

    print(
        "Creating embeddings..."
    )

    embeddings = create_embeddings(
        chunks
    )

    np.save(
        OUTPUT_FILE,
        embeddings
    )

    print(
        "Embedding creation completed."
    )

    print(
        f"Embedding shape: {embeddings.shape}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )