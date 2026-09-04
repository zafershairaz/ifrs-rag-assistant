import re
import json
from pathlib import Path


def load_text(file_path):
    """Load cleaned text from a file."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    return file_path.read_text(
        encoding="utf-8"
    )


def extract_standard_name(text):
    """
    Extract the primary IAS/IFRS standard from the
    beginning/title section of the document.

    The function intentionally searches only the
    beginning of the document so references to other
    standards later in the document are ignored.
    """

    # Search only the beginning of the document.
    header_text = text[:15000]

    patterns = [

        # Example:
        # INTERNATIONAL FINANCIAL REPORTING STANDARD
        # 15 REVENUE FROM CONTRACTS WITH CUSTOMERS
        r"INTERNATIONAL\s+FINANCIAL\s+REPORTING\s+STANDARD"
        r"\s+(\d{1,3})",

        # Example:
        # International Financial Reporting Standard 15
        r"International\s+Financial\s+Reporting\s+Standard"
        r"\s+(\d{1,3})",

        # Example:
        # (IFRS 15)
        r"\(\s*(IFRS\s+\d{1,3})\s*\)",

        # Example:
        # IFRS 15 Revenue from Contracts with Customers
        r"\b(IFRS\s+\d{1,3})\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            header_text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1)

            # First two patterns capture only
            # the standard number.
            if value.isdigit():

                return f"IFRS {value}"

            return value.upper()

    return "Unknown"


def create_chunks(text, standard_name):
    """
    Split accounting standard text into
    paragraph-based chunks.
    """

    pattern = r"(?m)^\s*(\d{1,3})\s+"

    matches = list(
        re.finditer(pattern, text)
    )

    chunks = []

    for index, match in enumerate(matches):

        paragraph_number = match.group(1)

        start = match.start()

        if index + 1 < len(matches):

            end = matches[index + 1].start()

        else:

            end = len(text)

        chunk_text = text[
            start:end
        ].strip()

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

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )


if __name__ == "__main__":

    input_file = (
        "data/processed/cleaned_text.txt"
    )

    output_file = (
        "data/processed/chunks.json"
    )

    text = load_text(
        input_file
    )

    # Automatically identify the primary
    # standard from the document title/header.
    standard_name = extract_standard_name(
        text
    )

    print(
        f"Detected standard: {standard_name}"
    )

    chunks = create_chunks(
        text,
        standard_name
    )

    save_chunks(
        chunks,
        output_file
    )

    print(
        "Chunking completed."
    )

    print(
        f"Number of chunks: {len(chunks)}"
    )

    print(
        f"Saved to: {output_file}"
    )