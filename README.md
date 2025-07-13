# Budgetizer

Categorizes items on receipts into specific budget categories.

### Configuration

Before you deploy through serverless, you must 
1. Install the serverless framework cli tool.
    a. To do this, you first need to install node.
    b. If you decide to install nvm, then you will need to remember what node version you install serverless in.
    c. I've run into an issue with having to use sudo to deploy my serverless resources due to an issue with the node installation location (TODO)
2. install the `serverless-python-requirements`
    a. `npm install --save serverless-python-requirements`
3. Make sure Docker is installed. This will ensure native dependencies are compatible with Amazon Linux containers Lambdas run in.
4. If using a non ARM arch machine, change `dockerizePip: non-linux` to `dockerizePip: true`
5. Create a venv and install dependencies
6. Install dependencies to `.requirements`:
    `mkdir -p .requirements`
    `pip install -r requirements.txt -t .requirements`
7. Create an AWS profile named `serverless-personal`. This value profile is used in the serverless 
config.
8. Add a file `google-creds.json` with your Google service account credentials so you can access Google.sheets from the Lambda. To setup, you can follow this article: https://genezio.com/deployment-platform/blog/google-sheets-as-apis/#prerequisites.
  a. Enable the Google Drive API in your Google Cloud console.
9. Create a OpenAI API key for a service user and add as file `openai-key.txt`.
10. Build the Docker image in the root dir: `docker buildx build --platform linux/arm64 -t lambda-builder-py313 -f Dockerfile .`

### OpenAI

This application uses OpenaI Vision to parse receipts, and extract the text
docs: https://platform.openai.com/docs/guides/images-vision?api-mode=responses

### OpenAI Vision vs Tesseract

I chose to use OpenAI Vision instead of adding a Lambda layer with the Tesseract binaries installed for simplicity. 

### Deploying
To deploy:
`AWS_PROFILE=serverless-personal serverless deploy`

To destroy:
`AWS_PROFILE=serverless-personal serverless remove`

Deploying with debug:
`AWS_PROFILE=serverless-personal serverless deploy --debug`

### Testing locally
`AWS_PROFILE=serverless-personal GOOGLE_SHEET_NAME=budget python3 src/handler.py`

### TODO
- Create a bootstrap script to perform most of the configuration steps.
- Implement some expense analysis and feedback for savings.

### What is the LLM doing
Reading the receipt image
Determining which category an expense falls into based on the expense description and provided categories
Determining the total expense for each item (msrp plus tax)