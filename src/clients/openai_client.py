import openai
import base64
from config.settings import BUDGET_CATEGORIES, OPENAI_API_KEY
import json

class OpenAIClient:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.api_key = OPENAI_API_KEY
        self.model = model
        openai.api_key = self.api_key

    def analyze_receipt(self, image_bytes):
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        prompt = f"""
        This is a receipt. Extract all itemized purchases and return them in the following JSON format:

        {{
        "items": [
            {{
            "Item Description": "Milk",
            "Amount": 3.49,
            "Category": "Groceries",
            "Date": "2025-06-17",
            "Tax": 0.25,
            "Merchant": "Walmart",
            "Receipt ID": "12341234"
            }},
            ...
        ]
        }}

        Only use these categories: {", ".join(BUDGET_CATEGORIES)}.
        """

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            temperature=0.2,
            max_tokens=1000,
        )

        output = response.choices[0].message.content
        try:
            data = json.loads(output)
            return data.get("items", [])
        except Exception as e:
            print("❌ Error parsing OpenAI output:", e)
            print("Raw output:\n", output)
            return []
