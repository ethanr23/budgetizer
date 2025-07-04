import json
import os
import base64
import boto3
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO

# --- Configuration ---
if __name__ == "__main__":
    # export AWS_PROFILE=severlelss-personal
    os.environ["AWS_PROFILE"] = "serverless-personal"
    os.environ["AWS_REGION"] = "us-east-1"

# openai key
secrets_client = boto3.client("secretsmanager")
secret_response = secrets_client.get_secret_value(SecretId="budgetizer-openai-key")
openai.api_key = secret_response["SecretString"]

# Get Google credentials from secrets manager
GOOGLE_CREDENTIALS = json.loads(secrets_client.get_secret_value(SecretId="budgetizer-google-creds")["SecretString"])
#GOOGLE_SHEET_NAME = os.environ["GOOGLE_SHEET_NAME"] # TODO add google sheet name to serverless.yml

# Budget categories
BUDGET_CATEGORIES = ["Groceries", "Medical", "Utilities", "Dining", "Subscriptions", "Travel", "Home", "Other"]

def analyze_receipt_with_openai(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = f"""
    This is a receipt. Extract all itemized purchases and return them in the following JSON format:

    {{
      "items": [
        {{
          "name": "Milk",
          "amount": 3.49,
          "category": "Groceries",
          "date": "2025-06-17",
          "tax": 0.25,
          "vendor": "Walmart"
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

def append_items_to_google_sheet(items):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1

    for item in items:
        sheet.append_row([
            item.get("date"),
            item.get("name"),
            item.get("category"),
            item.get("amount"),
            item.get("vendor"),
            item.get("tax")
        ])

def lambda_handler(event, context):
    print("📥 Event received:", json.dumps(event))

    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    s3 = boto3.client("s3")
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        image_bytes = obj["Body"].read()
    except Exception as e:
        print(f"❌ Failed to fetch S3 object: {e}")
        return {"status": "error", "message": str(e)}

    print("🧠 Sending to OpenAI for analysis...")
    items = analyze_receipt_with_openai(image_bytes)

    if items:
        print(f"📤 Appending {len(items)} items to Google Sheet...")
        append_items_to_google_sheet(items)
        return {"status": "success", "items_added": len(items)}
    else:
        print("⚠️ No items parsed.")
        return {"status": "no_items_parsed"}

if __name__ == "__main__":
    # Test the function with a local image
    with open(os.path.join(os.getcwd(), "tests/test_receipt.jpg"), "rb") as f:
        image_bytes = f.read()
    f.close()
    openai_response = analyze_receipt_with_openai(image_bytes)
    print(openai_response)