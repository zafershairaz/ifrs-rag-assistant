from vectorstore.search import search
from backend.rag_service import build_context


question = input(
    "\nEnter an accounting question: "
)


results = search(
    question,
    top_k=5
)


print(
    "\n" + "=" * 80
)

print(
    "RETRIEVED DOCUMENTS"
)

print(
    "=" * 80
)


for number, result in enumerate(
    results,
    start=1
):

    print(
        f"\nRESULT {number}"
    )

    print(
        "-" * 80
    )

    print(
        f"Standard: {result['standard']}"
    )

    print(
        f"Paragraph: {result['paragraph']}"
    )

    print(
        f"Similarity: {result['score']:.4f}"
    )

    print(
        "\nText:"
    )

    print(
        result["text"]
    )


print(
    "\n" + "=" * 80
)

print(
    "CONTEXT SENT TO QWEN"
)

print(
    "=" * 80
)

context = build_context(
    results
)

print(
    context
)