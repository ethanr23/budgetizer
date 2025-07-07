import json
import os
import base64
import boto3
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from config.settings import GOOGLE_SHEET_NAME, BUDGET_CATEGORIES
from clients import OpenAIClient, GoogleSheetsClient, S3Client

# --- Configuration ---
if __name__ == "__main__":
    # export AWS_PROFILE=severlelss-personal
    os.environ["AWS_PROFILE"] = "serverless-personal"
    os.environ["AWS_REGION"] = "us-east-1"

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
    
    openai_client = OpenAIClient()
    google_sheets_client = GoogleSheetsClient()
    s3_client = S3Client(bucket_name=bucket)

    print("🧠 Sending to OpenAI for analysis...")
    items = openai_client.analyze_receipt(image_bytes)

    if items:
        print(f"📤 Appending {len(items)} items to Google Sheet...")
        google_sheets_client.budgetize_items(items)
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