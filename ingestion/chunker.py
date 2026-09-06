import re
import json
from pathlib import Path

PROCESSED_FOLDER = Path("data/processed")
OUTPUT_FILE = PROCESSED_FOLDER / "chunks.json"


def load_text(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    return file_path.read_text(
        encoding="utf-8"
    )


def extract_standard_from_filename(file_path):
    """
    Extract the IFRS/IAS standard from the filename.

    Examples:

    ifrs-15-revenue-from-contracts-with-customers
        -> IFRS 15

    ifrs-9-financial-instruments
        -> IFRS 9

    ias-16-property-plant-and-equipment
        -> IAS 16
    """

    filename = Path(file_path).stem.lower()

    match = re.match(
        r"^(ifrs|ias)[_\-\s]*(\d{1,3})(?:[_\-\s].*)?$",
        filename
    )

    if not match:
        return "Unknown"

    standard_type = match.group(1).upper()
    standard_number = match.group(2)

    return f"{standard_type} {standard_number}"


def create_chunks(text, standard_name):
    """
    Create chunks based on IFRS/IAS paragraph numbers.

    Handles formats such as:

        12
        An entity shall...

    and:

        12 An entity shall...

    The paragraph number becomes the chunk identifier.
    """

    # ---------------------------------------------------------
    # Find paragraph numbers
    # ---------------------------------------------------------
    #
    # We look for a number at the beginning of a line.
    #
    # Example:
    #
    # 12
    # An entity shall...
    #
    # or
    #
    # 12 An entity shall...
    #

    pattern = r"(?m)^[ \t]*(\d{1,3})(?=[ \t]*\n|[ \t]+)"

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

        chunk_text = text[start:end].strip()

        # -----------------------------------------------------
        # Clean excessive whitespace
        # -----------------------------------------------------

        chunk_text = re.sub(
            r"\n{3,}",
            "\n\n",
            chunk_text
        )

        chunk_text = re.sub(
            r"[ \t]+",
            " ",
            chunk_text
        )

        chunk_text = chunk_text.strip()

        # -----------------------------------------------------
        # Ignore very small chunks
        # -----------------------------------------------------

        if len(chunk_text) < 50:
            continue

        chunks.append(
            {
                "standard": standard_name,
                "paragraph": paragraph_number,
                "text": chunk_text
            }
        )

    return chunks


def process_all_documents():

    cleaned_files = sorted(
        PROCESSED_FOLDER.glob("*_cleaned.txt")
    )

    if not cleaned_files:
        raise FileNotFoundError(
            "No cleaned documents found."
        )

    print(
        f"Found {len(cleaned_files)} "
        f"cleaned document(s)."
    )

    all_chunks = []

    for cleaned_file in cleaned_files:

        print(
            f"\nProcessing: {cleaned_file.name}"
        )

        text = load_text(cleaned_file)

        standard_name = (
            extract_standard_from_filename(
                cleaned_file
            )
        )

        print(
            f"Detected standard: {standard_name}"
        )

        if standard_name == "Unknown":

            print(
                "WARNING: Standard could not "
                f"be detected from {cleaned_file.name}"
            )

        chunks = create_chunks(
            text,
            standard_name
        )

        print(
            f"Chunks created: {len(chunks)}"
        )

        all_chunks.extend(chunks)

    return all_chunks


def save_chunks(chunks):

    PROCESSED_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
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

    chunks = process_all_documents()

    save_chunks(chunks)

    print("\nChunking completed.")

    print(
        f"Total chunks: {len(chunks)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )