import fitz


PDF_FILE = "data/raw/ifrs-15-revenue-from-contracts-with-customers.pdf"


doc = fitz.open(PDF_FILE)


for page_number in [5, 6, 7, 8]:

    page = doc[page_number - 1]

    print("\n" + "=" * 100)
    print(f"PAGE {page_number}")
    print("=" * 100)

    blocks = page.get_text("blocks")

    for number, block in enumerate(blocks, start=1):

        x0, y0, x1, y1, text, *_ = block

        text = text.strip().replace("\n", " | ")

        print(
            f"\nBLOCK {number}"
        )

        print(
            f"Coordinates: "
            f"x0={x0:.1f}, "
            f"y0={y0:.1f}, "
            f"x1={x1:.1f}, "
            f"y1={y1:.1f}"
        )

        print(
            f"Text: {text[:500]}"
        )


doc.close()