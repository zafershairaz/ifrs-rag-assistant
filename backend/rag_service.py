import time

import ollama

from vectorstore.search import (
    search,
    detect_standard
)


MODEL_NAME = "qwen3:8b"

DEFAULT_TOP_K = 5


# =========================================================
# Build context
# =========================================================

def build_context(results):

    context_parts = []

    for number, result in enumerate(
        results,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {number}

Standard: {result['standard']}
Paragraph: {result['paragraph']}
Section: {result.get('section', 'General')}

{result['text']}
"""
        )

    return "\n".join(
        context_parts
    )


# =========================================================
# Build Qwen prompt
# =========================================================

def build_prompt(question, context):

    return f"""
You are an IFRS and IAS accounting research assistant.

Your task is to answer the user's accounting question using ONLY
the IFRS/IAS source material provided below.

USER QUESTION:
{question}

SOURCE MATERIAL:
{context}

IMPORTANT RULES:

1. Use ONLY the supplied IFRS/IAS source material.

2. Do not rely on your general accounting knowledge.

3. Do not invent, assume, or reconstruct requirements that are not
supported by the supplied source material.

4. Do not invent paragraph numbers.

5. Do not cite a paragraph unless that paragraph is present in the
supplied source material.

6. If several supplied paragraphs are relevant, synthesize them
into one coherent answer.

7. Distinguish clearly between requirements stated in the source
material and explanatory comments.

8. Cite the relevant IFRS/IAS standard and paragraph number(s).

9. When the question asks for a comparison, explain the distinction
using the supplied source material.

10. When the question asks for a process, model, criteria, or
multiple steps, present the answer in a structured numbered list
if the supplied source material supports that structure.

11. If the retrieved material does not contain enough information
to answer the question reliably, state exactly:

"The retrieved IFRS/IAS material does not contain enough information
to answer this question reliably."

12. Keep the answer concise, technically accurate, and professional.

13. Do not mention the retrieval process, embeddings, FAISS,
TF-IDF, vector search, reranking, or the RAG system.

ANSWER FORMAT:

Answer:
[Direct answer to the user's question]

Explanation:
[Brief explanation based only on the supplied source material]

References:
[Relevant standard and paragraph number(s)]
"""


# =========================================================
# Ask Qwen
# =========================================================

def ask_qwen(prompt):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        think=False,
        options={
            "temperature": 0,
            "num_predict": 800
        }
    )
    return response["message"]["content"]


# =========================================================
# Ask question
# =========================================================

def ask_question(
    question,
    top_k=DEFAULT_TOP_K
):

    if not question or not question.strip():

        return {
            "question": question,
            "answer": "Please enter an accounting question.",
            "sources": []
        }

    question = question.strip()

    total_start = time.perf_counter()

    # -----------------------------------------------------
    # Detect standard
    # -----------------------------------------------------

    requested_standard = detect_standard(
        question
    )

    if requested_standard:

        print(
            f"Detected standard: "
            f"{requested_standard}"
        )

    else:

        print(
            "No specific IAS/IFRS standard detected. "
            "Searching across all standards."
        )

    # -----------------------------------------------------
    # Retrieval
    # -----------------------------------------------------

    search_start = time.perf_counter()

    results = search(
        question,
        top_k=top_k,
        standard=requested_standard
    )

    search_time = (
        time.perf_counter()
        - search_start
    )

    print(
        f"Hybrid retrieval time: "
        f"{search_time:.2f} seconds"
    )

    # -----------------------------------------------------
    # No results
    # -----------------------------------------------------

    if not results:

        total_time = (
            time.perf_counter()
            - total_start
        )

        print(
            f"Total RAG time: "
            f"{total_time:.2f} seconds"
        )

        return {
            "question": question,
            "answer": (
                "No sufficiently relevant "
                "IFRS/IAS material was retrieved "
                "for this question."
            ),
            "sources": []
        }

    # -----------------------------------------------------
    # Print sources
    # -----------------------------------------------------

    print(
        f"Using {len(results)} retrieved "
        f"sources for Qwen."
    )

    print(
        "\nRetrieved sources:"
    )

    for number, result in enumerate(
        results,
        start=1
    ):

        print(
            f"{number}. "
            f"{result['standard']} "
            f"paragraph "
            f"{result['paragraph']} "
            f"(score: "
            f"{result['score']:.4f})"
        )

        print(
            f"   Section: "
            f"{result.get('section', 'General')}"
        )

    # -----------------------------------------------------
    # Build context
    # -----------------------------------------------------

    context = build_context(
        results
    )

    prompt = build_prompt(
        question,
        context
    )

    # -----------------------------------------------------
    # Qwen
    # -----------------------------------------------------

    print(
        "\nSending retrieved context to Qwen..."
    )

    llm_start = time.perf_counter()

    answer = ask_qwen(
        prompt
    )

    llm_time = (
        time.perf_counter()
        - llm_start
    )

    print(
        f"Qwen response time: "
        f"{llm_time:.2f} seconds"
    )

    # -----------------------------------------------------
    # API sources
    #
    # IMPORTANT:
    # section/text remain internal.
    # The API only exposes standard, paragraph and score.
    # -----------------------------------------------------

    sources = []

    for result in results:

        sources.append(
            {
                "standard": result[
                    "standard"
                ],
                "paragraph": result[
                    "paragraph"
                ],
                "score": result[
                    "score"
                ]
            }
        )

    # -----------------------------------------------------
    # Total time
    # -----------------------------------------------------

    total_time = (
        time.perf_counter()
        - total_start
    )

    print(
        f"Total RAG time: "
        f"{total_time:.2f} seconds"
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }


# =========================================================
# CLI
# =========================================================

if __name__ == "__main__":

    question = input(
        "\nEnter your accounting question: "
    ).strip()

    result = ask_question(
        question,
        top_k=DEFAULT_TOP_K
    )

    print(
        "\n"
        + "=" * 70
    )

    print("ANSWER")

    print(
        "=" * 70
    )

    print(
        result["answer"]
    )

    print(
        "\n"
        + "=" * 70
    )

    print("RETRIEVED SOURCES")

    print(
        "=" * 70
    )

    for number, source in enumerate(
        result["sources"],
        start=1
    ):

        print(
            f"{number}. "
            f"{source['standard']} "
            f"paragraph "
            f"{source['paragraph']} "
            f"(similarity: "
            f"{source['score']:.4f})"
        )