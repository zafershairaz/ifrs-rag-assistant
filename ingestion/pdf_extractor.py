import fitz
from pathlib import Path


def extract_text_from_pdf(pdf_path):
    """
    Extract text from every page of a PDF.

    Returns:
        str: Complete extracted text.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = fitz.open(pdf_path)

    all_text = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        if text.strip():
            all_text.append(
                f"\n--- PAGE {page_number} ---\n{text}"
            )

    document.close()

    return "\n".join(all_text)


if __name__ == "__main__":

    pdf_file = "data/raw/sample.pdf"

    try:
        extracted_text = extract_text_from_pdf(pdf_file)

        output_file = Path("data/processed/extracted_text.txt")

        output_file.write_text(
            extracted_text,
            encoding="utf-8"
        )

        print("PDF extraction completed successfully.")
        print(f"Output saved to: {output_file}")
        print(f"Characters extracted: {len(extracted_text):,}")

    except FileNotFoundError as error:
        print(error)