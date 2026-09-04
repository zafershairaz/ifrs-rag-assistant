import ollama


response = ollama.chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": (
                "Explain the purpose of International Accounting Standards (IAS) and International Financial Reporting Standards (IFRS) "
                "in simple accounting language."
            )
        }
    ]
)


print("\n===== QWEN RESPONSE =====\n")

print(response["message"]["content"])