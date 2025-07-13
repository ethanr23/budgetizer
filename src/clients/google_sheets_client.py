import gspread
from src.config.settings import GOOGLE_CREDENTIALS, GOOGLE_SHEET_NAME, EXPENSE_SHEET_HEADERS, CATEGORY_SHEET_HEADERS, BUDGET_CATEGORIES
from google.oauth2.service_account import Credentials


class GoogleSheetsClient:
    def __init__(self):
        #self.credentials = gspread.service_account(filename=GOOGLE_CREDENTIALS)
        self.credentials = Credentials.from_service_account_info(
            GOOGLE_CREDENTIALS, 
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        self.spreadsheet_name = GOOGLE_SHEET_NAME
        self.client = self._create_client()
        
    def _create_client(self):
        SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/sheets"]
        #creds = ServiceAccountCredentials.from_json_keyfile_name(
        #    GOOGLE_CREDENTIALS,
        #    scope
        #)
        authorized_client = gspread.authorize(self.credentials)
        authorized_client.set_timeout(60)  # Set a timeout for operations
        client = authorized_client.open(self.spreadsheet_name)
        return client
    
    def _create_expense_worksheet(self, month: str, year: str) -> None:
        self.expense_worksheet = f"{month}_{year}_Expenses"
        try:
            self.client.worksheet(self.expense_worksheet)
        except gspread.exceptions.WorksheetNotFound:
            self.client.add_worksheet(title=self.expense_worksheet, rows="200", cols="20")
            # add column headers
            self.client.worksheet(self.expense_worksheet).append_row(EXPENSE_SHEET_HEADERS)
            print(f"Worksheet '{self.expense_worksheet}' created successfully.")

    def _create_category_worksheet(self, month: str, year: str) -> None:
        self.category_worksheet = f"{month}_{year}_Categories"
        try:
            self.client.worksheet(self.category_worksheet)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.client.add_worksheet(title=self.category_worksheet, rows="100", cols="20")
            row_num = len(self.client.worksheet(self.category_worksheet).get_all_values()) + 1
            for category, details in BUDGET_CATEGORIES.items():
                #row_num = len(self.client.worksheet(self.category_worksheet).get_all_values()) + 1
                formula = f"=SUMIF('{self.expense_worksheet}'!D:D, A{row_num}, '{self.expense_worksheet}'!E:E)"
                self.client.worksheet(self.category_worksheet).update(
                    [[
                        category,
                        details.get("budgeted"),
                        details.get("savings", False),
                        formula
                    ]],
                    range_name=f"A{row_num}:D{row_num}",
                    value_input_option='USER_ENTERED'
                )
                row_num += 1
                
            # add column headers
            self.client.worksheet(self.category_worksheet).insert_row(
                CATEGORY_SHEET_HEADERS,
                1
            )
            print(f"Worksheet '{self.category_worksheet}' created successfully.")

    def budgetize_items(self, items):
        """
        Appends a list of items to the Google Sheet.
        Each item should be a dictionary with keys: date, name, category, amount, vendor, tax.
        """
        if not items:
            print("No items to append.")
            return
        
        # Get date from the first item to determine the month and year
        first_item = items[0]
        if "Date" not in first_item:
            print("No date found in items. Cannot determine month and year.")
            raise ValueError("Items must contain a 'Date' key.")

        date = first_item.get("Date")
        date_parts = date.split("-")
        if len(date_parts) < 2:
            print("Invalid date format. Expected 'YYYY-MM-DD'.")
            raise ValueError("Date must be in 'YYYY-MM-DD' format.")
        
        month = date_parts[1]
        year = date_parts[0]

        # Create the itemized expense and category worksheets if they don't exist
        self._create_expense_worksheet(month, year)
        self._create_category_worksheet(month, year)

        # Get a total value amount for receipt
        total_amount = sum(item.get("Amount", 0) for item in items if "Amount" in item)
        
        # Append each item to the sheet
        for item in items:
            item["Total Receipt Amount"] = total_amount
            # Ensure the row matches the order of EXPENSE_SHEET_HEADERS
            row = []
            for header in EXPENSE_SHEET_HEADERS:
                # Use .get(header) for direct mapping, fallback to .get(header.lower()) for case-insensitive match
                value = item.get(header)
                if value is None:
                    value = item.get(header.lower())
                row.append(value)
            self.client.worksheet(self.expense_worksheet).append_row(row)