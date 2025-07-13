import json
import os
import boto3
from src.clients import OpenAIClient, GoogleSheetsClient

# --- Configuration ---
if __name__ == "__main__":
    # export AWS_PROFILE=severlelss-personal
    os.environ["AWS_PROFILE"] = "serverless-personal"
    os.environ["AWS_REGION"] = "us-east-1"

def lambda_handler(event, context):
    print("📥 Event received:", json.dumps(event))

    #record = event["Records"][0]
    bucket = event["detail"]["bucket"]["name"]
    key = event["detail"]["object"]["key"]

    s3 = boto3.client("s3")
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        image_bytes = obj["Body"].read()
    except Exception as e:
        print(f"❌ Failed to fetch S3 object: {e}")
        return {"status": "error", "message": str(e)}
    
    openai_client = OpenAIClient()
    google_sheets_client = GoogleSheetsClient()

    print("🧠 Sending to OpenAI for analysis...")
    items = openai_client.analyze_receipt(image_bytes)

    if items:
        print(f"📤 Appending {len(items)} items to Google Sheet...")
        google_sheets_client.budgetize_items(items)
        print("✅ Receipt analysis completed successfully.")
        return {"status": "success", "items_added": len(items)}
    else:
        print("⚠️ No items parsed.")
        return {"status": "no_items_parsed"}

if __name__ == "__main__":
    # Test the function with a local image
    #with open(os.path.join(os.getcwd(), "tests/test_receipt.jpg"), "rb") as f:
    #    image_bytes = f.read()
    #f.close()

    # define test event
    test_event = {
        "detail": {
            "bucket": {
                "name": "budgetizer-receipts"
            },
            "object": {
                "key": "IMG_6359.jpg"
            }
        }
    }

    # print account ID for profile we're using
    sts_client = boto3.client("sts")
    account_id = sts_client.get_caller_identity()["Account"]
    print(f"Using AWS account ID: {account_id}")

    lambda_handler(test_event, None)

    #print(openai_response)