import json
import re
from pathlib import Path


PROCESSED_FOLDER = Path("data/processed")
OUTPUT_FILE = PROCESSED_FOLDER / "chunks.json"


# ---------------------------------------------------------
# Standard detection
# ---------------------------------------------------------

def extract_standard_from_filename(file_path):
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


# ---------------------------------------------------------
# Paragraph detection
# ---------------------------------------------------------

def is_paragraph_number(text):
    text = text.strip()

    return bool(
        re.fullmatch(r"\d{1,3}", text)
    )


# ---------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------

def clean_text(text):
    """
    Removes common PDF extraction artifacts while preserving
    accounting content.
    """

    text = text.strip()

    # Remove IFRS Foundation copyright footer
    text = re.sub(
        r"A\d+\s*\|?\s*©\s*IFRS\s*Foundation",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"©\s*IFRS\s*Foundation",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove standalone appendix/page identifiers such as A782
    # but DO NOT remove legitimate paragraph identifiers such as 62A.
    if re.fullmatch(r"A\d+", text, flags=re.IGNORECASE):
        return ""

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.;:])", r"\1", text)

    return text.strip()


# ---------------------------------------------------------
# Header / footer detection
# ---------------------------------------------------------

def is_noise_text(text, standard):
    """
    Identifies common headers, footers and PDF artifacts.
    """

    cleaned = clean_text(text)

    if not cleaned:
        return True

    # Standard name
    if cleaned.upper() == standard.upper():
        return True

    # Common IFRS title/header
    if cleaned.lower().startswith(
        "international financial reporting standard"
    ):
        return True

    # Copyright/footer
    if "© IFRS Foundation" in cleaned:
        return True

    # Appendix page marker
    if re.fullmatch(r"A\d+", cleaned, flags=re.IGNORECASE):
        return True

    return False


# ---------------------------------------------------------
# Heading detection
# ---------------------------------------------------------

def looks_like_heading(text):
    """
    Attempts to identify section headings from extracted PDF text.

    This is intentionally conservative. A heading is generally:
    - relatively short
    - not a sentence
    - not a paragraph number
    - not a footer
    """

    text = text.strip()

    if not text:
        return False

    if is_paragraph_number(text):
        return False

    if len(text) > 120:
        return False

    if len(text.split()) > 15:
        return False

    if text.endswith("."):
        return False

    # Do not classify obvious metadata as headings
    if "© IFRS Foundation" in text:
        return False

    if re.fullmatch(r"A\d+", text, flags=re.IGNORECASE):
        return False

    # Common IFRS/IAS structural terms
    heading_keywords = [
        "scope",
        "objective",
        "definitions",
        "recognition",
        "measurement",
        "presentation",
        "disclosure",
        "depreciation",
        "depreciable amount",
        "useful life",
        "residual value",
        "impairment",
        "identifying the contract",
        "performance obligations",
        "transaction price",
        "allocating the transaction price",
        "recognition of revenue",
        "lease term",
        "initial measurement",
        "subsequent measurement",
        "classification",
        "provisions",
        "contingent liabilities",
        "contingent assets",
        "employee benefits",
        "borrowing costs",
        "fair value",
        "financial instruments",
        "consolidation",
        "investment property",
        "inventories",
    ]

    lowered = text.lower()

    for keyword in heading_keywords:
        if keyword in lowered:
            return True

    return False


# ---------------------------------------------------------
# Paragraph processing
# ---------------------------------------------------------

def process_pdf_blocks(blocks_file):

    with open(blocks_file, "r", encoding="utf-8") as file:
        pages = json.load(file)

    standard = extract_standard_from_filename(blocks_file)

    print(f"Detected standard: {standard}")

    chunks = []

    current_paragraph = None
    current_text = []

    current_section = "General"

    for page in pages:

        page_blocks = page["blocks"]

        # Preserve the original reading order
        page_blocks = sorted(
            page_blocks,
            key=lambda block: (
                round(block["y0"], 1),
                block["x0"]
            )
        )

        paragraph_markers = []

        # -------------------------------------------------
        # Find paragraph number blocks
        # -------------------------------------------------

        for block in page_blocks:

            raw_text = block["text"].strip()

            if not is_paragraph_number(raw_text):
                continue

            x0 = block["x0"]
            y0 = block["y0"]

            # Paragraph numbers normally appear toward the left
            if x0 < 150:

                paragraph_markers.append(
                    {
                        "number": raw_text,
                        "y0": y0,
                        "x0": x0
                    }
                )

        # -------------------------------------------------
        # Process blocks
        # -------------------------------------------------

        for block in page_blocks:

            raw_text = block["text"].strip()

            if not raw_text:
                continue

            text = clean_text(raw_text)

            if not text:
                continue

            # Remove noise
            if is_noise_text(text, standard):
                continue

            # Paragraph number itself
            if (
                is_paragraph_number(text)
                and block["x0"] < 150
            ):
                continue

            # -------------------------------------------------
            # Section heading
            # -------------------------------------------------

            if looks_like_heading(text):

                # Only update the section if we are not
                # currently inside a paragraph.
                #
                # If a heading appears between paragraphs,
                # it becomes the section for subsequent chunks.
                if current_paragraph is None:
                    current_section = text

                continue

            # -------------------------------------------------
            # Match text block to paragraph number
            # -------------------------------------------------

            matched_marker = None

            for marker in paragraph_markers:

                if abs(marker["y0"] - block["y0"]) <= 4:

                    matched_marker = marker
                    break

            # -------------------------------------------------
            # New paragraph
            # -------------------------------------------------

            if matched_marker:

                paragraph_number = matched_marker["number"]

                # Save previous paragraph
                if current_paragraph is not None and current_text:

                    final_text = " ".join(current_text).strip()

                    if final_text:

                        chunks.append(
                            {
                                "standard": standard,
                                "paragraph": current_paragraph,
                                "section": current_section,
                                "text": final_text
                            }
                        )

                current_paragraph = paragraph_number

                current_text = [text]

            # -------------------------------------------------
            # Continuation of current paragraph
            # -------------------------------------------------

            else:

                if current_paragraph is not None:
                    current_text.append(text)

        # End page

    # ---------------------------------------------------------
    # Save final paragraph
    # ---------------------------------------------------------

    if current_paragraph is not None and current_text:

        final_text = " ".join(current_text).strip()

        if final_text:

            chunks.append(
                {
                    "standard": standard,
                    "paragraph": current_paragraph,
                    "section": current_section,
                    "text": final_text
                }
            )

    return chunks


# ---------------------------------------------------------
# Process all documents
# ---------------------------------------------------------

def process_all_documents():

    block_files = sorted(
        PROCESSED_FOLDER.glob("*_blocks.json")
    )

    if not block_files:
        raise FileNotFoundError(
            "No *_blocks.json files found."
        )

    print(
        f"Found {len(block_files)} block document(s)."
    )

    all_chunks = []

    for blocks_file in block_files:

        print(
            f"\nProcessing: {blocks_file.name}"
        )

        chunks = process_pdf_blocks(
            blocks_file
        )

        print(
            f"Chunks created: {len(chunks)}"
        )

        all_chunks.extend(chunks)

    return all_chunks


# ---------------------------------------------------------
# Save chunks
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

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