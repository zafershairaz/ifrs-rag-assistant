from pathlib import Path


def read_extracted_text(file_path):
    """
    Read extracted PDF text.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path.read_text(encoding="utf-8")


def save_clean_text(text, output_path):
    """
    Save processed text to a file.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_text(
        text,
        encoding="utf-8"
    )


if __name__ == "__main__":

    input_file = "data/processed/extracted_text.txt"
    output_file = "data/processed/cleaned_text.txt"

    text = read_extracted_text(input_file)

    # Basic whitespace cleaning
    cleaned_text = "\n".join(
        line.strip()
        for line in text.splitlines()
        if line.strip()
    )

    save_clean_text(
        cleaned_text,
        output_file
    )

    print("Text processing completed.")
    print(f"Characters: {len(cleaned_text):,}")
    print(f"Saved to: {output_file}")