import re
import json
from pathlib import Path


def load_text(file_path):
    """Load cleaned text from a file."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path.read_text(encoding="utf-8")


def create_chunks(text, standard_name="Unknown"):
    """
    Split accounting standard text into chunks.

    For the first version, chunks are created based on
    paragraph numbers where possible.
    """

    # Find paragraph numbers such as:
    # 1, 2, 7, 10, 25, 100 etc.
    pattern = r"(?m)^\s*(\d{1,3})\s+"

    matches = list(re.finditer(pattern, text))

    chunks = []

    for index, match in enumerate(matches):

        paragraph_number = match.group(1)

        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        chunk_text = text[start:end].strip()

        if len(chunk_text) < 30:
            continue

        chunks.append({
            "standard": standard_name,
            "paragraph": paragraph_number,
            "text": chunk_text
        })

    return chunks


def save_chunks(chunks, output_file):
    """Save chunks as JSON."""

    output_file = Path(output_file)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )


if __name__ == "__main__":

    input_file = "data/processed/cleaned_text.txt"
    output_file = "data/processed/chunks.json"

    # Change this when using another standard
    standard_name = "IAS 16"

    text = load_text(input_file)

    chunks = create_chunks(
        text,
        standard_name
    )

    save_chunks(
        chunks,
        output_file
    )

    print("Chunking completed.")
    print(f"Number of chunks: {len(chunks)}")
    print(f"Saved to: {output_file}")