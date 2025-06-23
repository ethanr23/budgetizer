import openai
import os
import boto3

# --- Configuration ---
if __name__ == "__main__":
    # export AWS_PROFILE=severlelss-personal
    os.environ["AWS_PROFILE"] = "serverless-personal"
    os.environ["AWS_REGION"] = "us-east-1"

# openai key
secrets_client = boto3.client("secretsmanager")
secret_response = secrets_client.get_secret_value(SecretId="budgetizer-openai-key")
openai.api_key = secret_response["SecretString"]

models = openai.models.list()
for model in models.data:
    print(model.id)