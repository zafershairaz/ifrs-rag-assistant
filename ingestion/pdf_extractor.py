import pymupdf
from pathlib import Path

RAW_FOLDER = Path("data/raw")
OUTPUT_FOLDER = Path("data/processed")


def extract_pdf_blocks(pdf_path):
    """
    Extract text blocks together with their coordinates from a PDF.
    This preserves layout information needed for paragraph detection.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        blocks = page.get_text("blocks")

        page_blocks = []

        for block in blocks:

            x0, y0, x1, y1, text, *_ = block

            text = text.strip()

            if not text:
                continue

            page_blocks.append({
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "text": text
            })

        pages.append({
            "page": page_number,
            "blocks": page_blocks
        })

    document.close()

    return pages


def extract_all_pdfs():

    RAW_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(RAW_FOLDER.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF files found in data/raw/"
        )

    print(f"Found {len(pdf_files)} PDF file(s).")

    for pdf_file in pdf_files:

        print(f"\nProcessing: {pdf_file.name}")

        pages = extract_pdf_blocks(pdf_file)

        output_file = (
            OUTPUT_FOLDER /
            f"{pdf_file.stem}_blocks.json"
        )

        import json

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                pages,
                file,
                ensure_ascii=False,
                indent=2
            )

        print(f"Saved: {output_file}")
        print(f"Pages: {len(pages)}")


if __name__ == "__main__":

    extract_all_pdfs()

    print("\nPDF block extraction completed successfully.")