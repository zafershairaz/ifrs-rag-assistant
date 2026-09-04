import ollama

from vectorstore.search import search


MODEL_NAME = "qwen3:8b"


def build_context(results):
    """
    Convert retrieved search results into
    structured context for the LLM.
    """

    context_parts = []

    for number, result in enumerate(
        results,
        start=1
    ):

        source = (
            f"{result['standard']} "
            f"paragraph {result['paragraph']}"
        )

        context_parts.append(
            f"""
SOURCE {number}
-----------
Standard: {result['standard']}
Paragraph: {result['paragraph']}
Similarity score: {result['score']:.4f}

Text:
{result['text']}
"""
        )

    return "\n".join(context_parts)


def build_prompt(question, context):
    """
    Build a strict grounded RAG prompt.
    """

    return f"""
You are an IFRS and IAS accounting
research assistant.

Your job is to answer the user's question
using ONLY the retrieved source material
provided below.

USER QUESTION
=============

{question}


RETRIEVED SOURCE MATERIAL
=========================

{context}


INSTRUCTIONS
============

1. Use only the retrieved source material.

2. Do not use your own knowledge to introduce
   accounting requirements that are not contained
   in the retrieved material.

3. Do not invent IFRS or IAS paragraph numbers.

4. Cite the relevant standard and paragraph
   number when the information is available.

5. Clearly distinguish between:
   - what the source states
   - your explanation of the source

6. If the retrieved material does not provide
   enough information to answer the question,
   say:

   "The retrieved IFRS/IAS material does not
   contain enough information to answer this
   question reliably."

7. Do not pretend that an unsupported answer
   is authoritative.

8. Keep the answer professional and suitable
   for an accounting student or professional.

9. Do not present the response as a substitute
   for professional accounting judgment.

10. Do not cite a source that was not included
    in the retrieved source material.


ANSWER
======

Provide:

- A direct answer
- A short explanation
- Relevant IFRS/IAS paragraph references
- A brief source list
"""


def ask_question(question, top_k=5):
    """
    Complete RAG pipeline:

    Question
       ↓
    FAISS retrieval
       ↓
    Context construction
       ↓
    Qwen3
       ↓
    Grounded answer
    """

    if not question or not question.strip():

        return {
            "answer": "Please enter an accounting question.",
            "sources": []
        }

    print(
        "\nSearching IFRS/IAS documents..."
    )

    results = search(
        question,
        top_k=top_k
    )

    if not results:

        return {
            "answer": (
                "No relevant IFRS/IAS material "
                "was retrieved."
            ),
            "sources": []
        }

    print(
        f"Retrieved {len(results)} "
        f"relevant paragraphs."
    )

    context = build_context(
        results
    )

    prompt = build_prompt(
        question,
        context
    )

    print(
        "Sending retrieved context to Qwen..."
    )

    response = ollama.chat(

        model=MODEL_NAME,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = (
        response["message"]["content"]
    )

    sources = []

    for result in results:

        sources.append({

            "standard": result["standard"],

            "paragraph": result["paragraph"],

            "score": result["score"]

        })

    return {

        "answer": answer,

        "sources": sources

    }


if __name__ == "__main__":

    question = input(
        "\nEnter your accounting question: "
    )

    result = ask_question(
        question,
        top_k=5
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "ANSWER"
    )

    print(
        "=" * 70
    )

    print(
        result["answer"]
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "RETRIEVED SOURCES"
    )

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