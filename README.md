# Budgetizer

Categorizes items on receipts into specific budget categories.

### Configuration

Before you deploy through serverless, you must 
1. Install the serverless framework cli tool.
2. Create an AWS profile named `serverless-personal`. This value profile is used in the serverless 
config.
3. Add a file `google-creds.json` with your Google service account credentials so you can access Google.sheets from the Lambda. To setup, you can follow this article: https://genezio.com/deployment-platform/blog/google-sheets-as-apis/#prerequisites.
4. Create a OpenAI API key for a service user and add as file `openai-key.txt`.

### OpenAI

This application uses OpenaI Vision to parse receipts, and extract the text
docs: https://platform.openai.com/docs/guides/images-vision?api-mode=responses

### OpenAI Vision vs Tesseract

I chose to use OpenAI Vision instead of adding a Lambda layer with the Tesseract binaries installed for simplicity. 

###