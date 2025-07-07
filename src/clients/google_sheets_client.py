import gspread
from typing import List, Any, Optional
from config.settings import GOOGLE_CREDENTIALS, GOOGLE_SHEET_NAME, EXPENSE_SHEET_HEADERS, CATEGORY_SHEET_HEADERS, BUDGET_CATEGORIES
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetsClient:
    def __init__(self):
        self.credentials = gspread.service_account(filename=GOOGLE_CREDENTIALS)
        self.spreadsheet_name = GOOGLE_SHEET_NAME
        self.client = self._create_client()
        
    def _create_client(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            GOOGLE_CREDENTIALS,
            scope
        )
        autorized_client = gspread.authorize(creds)
        autorized_client.set_timeout(60)  # Set a timeout for operations
        client = autorized_client.open(self.spreadsheet_name)
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
            self.client.add_worksheet(title=self.category_worksheet, rows="100", cols="20")
            # add budget categories
            for category, details in BUDGET_CATEGORIES.items():
                self.client.worksheet(self.category_worksheet).append_row([
                    category,
                    details.get("budgeted"),
                    details.get("savings", False),
                    f"=SUMIF('{self.expense_worksheet}'!C:C, A{len(BUDGET_CATEGORIES) + 1}, '{self.expense_worksheet}'!D:D)" # use a formula instead of calculating at run time so I can make modifications in the sheet
                ])
            # add column headers
            self.client.worksheet(self.category_worksheet).append_row(CATEGORY_SHEET_HEADERS)
            print(f"Worksheet '{self.category_worksheet}' created successfully.")

    def open_sheet(self, spreadsheet_name: str, worksheet_name: Optional[str] = None):
        sh = self.client.open(spreadsheet_name)
        if worksheet_name:
            return sh.worksheet(worksheet_name)
        return sh.sheet1

    def read_range(self, spreadsheet_name: str, cell_range: str, worksheet_name: Optional[str] = None) -> List[List[Any]]:
        ws = self.open_sheet(spreadsheet_name, worksheet_name)
        return ws.get(cell_range)

    def write_range(self, spreadsheet_name: str, cell_range: str, values: List[List[Any]], worksheet_name: Optional[str] = None):
        ws = self.open_sheet(spreadsheet_name, worksheet_name)
        ws.update(cell_range, values)

    def append_row(self, spreadsheet_name: str, row_values: List[Any], worksheet_name: Optional[str] = None):
        ws = self.open_sheet(spreadsheet_name, worksheet_name)
        ws.append_row(row_values)

    def budgetize_items(self, items: List[dict]):
        """
        Appends a list of items to the Google Sheet.
        Each item should be a dictionary with keys: date, name, category, amount, vendor, tax.
        """
        if not items:
            print("No items to append.")
            return
        
        # Get date from the first item to determine the month and year
        first_item = items[0]
        if "date" not in first_item:
            print("No date found in items. Cannot determine month and year.")
            raise ValueError("Items must contain a 'date' key.")
        
        date = first_item.get("date")
        date_parts = date.split("-")
        if len(date_parts) < 2:
            print("Invalid date format. Expected 'YYYY-MM-DD'.")
            raise ValueError("Date must be in 'YYYY-MM-DD' format.")
        
        month = date_parts[1]
        year = date_parts[0]

        # Create the itemized expense and category worksheets if they don't exist
        self._create_expense_worksheet(month, year)
        self._create_category_worksheet(month, year)
        
        # Append each item to the sheet
        for item in items:
            # Ensure the row matches the order of EXPENSE_SHEET_HEADERS
            row = []
            for header in EXPENSE_SHEET_HEADERS:
                # Use .get(header) for direct mapping, fallback to .get(header.lower()) for case-insensitive match
                value = item.get(header)
                if value is None:
                    value = item.get(header.lower())
                row.append(value)
            self.append_row(self.spreadsheet_name, row)