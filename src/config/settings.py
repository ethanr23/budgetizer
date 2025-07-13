import boto3
import json


# OpenAI key
secrets_client = boto3.client(
    "secretsmanager", 
    region_name="us-east-1"
)
secret_response = secrets_client.get_secret_value(
    SecretId="budgetizer-openai-key-2"
)
OPENAI_API_KEY = secret_response["SecretString"]

# Google credentials
GOOGLE_CREDENTIALS = json.loads(
    secrets_client.get_secret_value(
        SecretId="budgetizer-google-creds"
    )["SecretString"]
)

# Google Sheet name
#GOOGLE_SHEET_NAME = os.environ["GOOGLE_SHEET_NAME"]
GOOGLE_SHEET_NAME = "Budget_2"

# Budget categories
BUDGET_CATEGORIES = {
    "Work Benefits": {
        "savings": False,
        "budgeted": 68
    },
    "Ethan Farmers AD&D": {
        "savings": False,
        "budgeted": 16
    },
    "Ethan Truist AD&D": {
        "savings": False,
        "budgeted": 16
    },
    "Auto Insurance": {
        "savings": False,
        "budgeted": 215
    },
    "Northwestern Mutual (Life and Disability)": {
        "savings": False,
        "budgeted": 83
    },
    "Mortgage": {
        "savings": False,
        "budgeted": 1780
    },
    "IRA": {
        "savings": False,
        "budgeted": 600
    },
    "Water": {
        "savings": False,
        "budgeted": 100
    },
    "Power": {
        "savings": False,
        "budgeted": 106
    },
    "Internet": {
        "savings": True,
        "budgeted": 60
    },
    "Groceries": {
        "savings": False,
        "budgeted": 500
    },
    "Vehicle Gas": {
        "savings": False,
        "budgeted": 120
    },
    "Tithe": {
        "savings": False,
        "budgeted": 150
    },
    "Diapers": {
        "savings": False,
        "budgeted": 70
    },
    "Family Clothing and personal Care": {
        "savings": False,
        "budgeted": 160
    },
    "Chuck Yard": {
        "savings": False,
        "budgeted": 48
    },
    "Amazon/Living Essentials": {
        "savings": False,
        "budgeted": 200
    },
    "Dog Food": {
        "savings": False,
        "budgeted": 50
    },
    "Ada 529": {
        "savings": True,
        "budgeted": 125
    },
    "Ellis 529": {
        "savings": True,
        "budgeted": 100
    },
    "Brokerage": {
        "savings": True,
        "budgeted": 150
    },
    "Gym": {
        "savings": False,
        "budgeted": 10
    },
    "HBO": {
        "savings": False,
        "budgeted": 17
    },
    "Apple Music": {
        "savings": False,
        "budgeted": 17
    },
    "iCloud": {
        "savings": False,
        "budgeted": 10
    },
    "Amazon Prime": {
        "savings": False,
        "budgeted": 16
    },
    "Netflix": {
        "savings": False,
        "budgeted": 18
    },
    "Dining Out": {
        "savings": False,
        "budgeted": 200
    },
    "Alcohol": {
        "savings": False,
        "budgeted": 100
    },
    "Travel": {
        "savings": False,
        "budgeted": 100
    },
    "Sam's Club": {
        "savings": False,
        "budgeted": 150
    },
    "Gifts": {
        "savings": False,
        "budgeted": 50,
    },
    "Miscellaneous Wants": {
        "savings": False,
        "budgeted": 300
    },
    "Trugreen": {
        "savings": False,
        "budgeted": 132
    },
    "Vivint": {
        "savings": False,
        "budgeted": 49
    },
    "Unplanned Expenses": {
        "savings": False,
        "budgeted": None
    }
}

EXPENSE_SHEET_HEADERS = (
    "Date",
    "Merchant",
    "Item Description",
    "Category",
    "Amount",
    "Receipt ID",
    "Total Receipt Amount"
)

CATEGORY_SHEET_HEADERS = (
    "Category",
    "Budgeted Amount",
    "Is Savings",
    "Total Expense"
)