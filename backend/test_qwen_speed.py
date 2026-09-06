import time
import ollama

MODEL_NAME = "qwen3:8b"

question = """
Explain briefly what impairment of trade receivables means under IFRS 9.
"""

print(f"Testing model: {MODEL_NAME}")
print("Sending request to Qwen...\n")

start = time.perf_counter()

response = ollama.chat(
    model=MODEL_NAME,
    messages=[
        {
            "role": "user",
            "content": question
        }
    ],
    options={
        "temperature": 0,
        "num_predict": 300
    }
)

elapsed = time.perf_counter() - start

print("=" * 70)
print("QWEN RESPONSE")
print("=" * 70)
print(response["message"]["content"])

print("\n" + "=" * 70)
print(f"TIME: {elapsed:.2f} seconds")
print("=" * 70)