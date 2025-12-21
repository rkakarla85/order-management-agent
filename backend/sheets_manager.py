import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import datetime
import json

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

class SheetsManager:
    def __init__(self, inventory_sheet_id="1XdM-7X0wfzroeXil1c3NBbSxgv9hrtR7qFu4glMbi-M", orders_sheet_name="Orders", creds_file="credentials.json"):
        self.inventory_data = [] # Cache inventory
        self.creds_file = creds_file
        self.inventory_sheet_id = inventory_sheet_id
        self.orders_sheet_name = orders_sheet_name
        self.client = None
        
        if os.path.exists(creds_file):
            self.connect()
        else:
            print("Warning: credentials.json not found. Using Mock Data.")
            self.inventory_data = [
                {"item": "Switch", "category": "Electrical", "price": 50},
                {"item": "Fan", "category": "Electrical", "price": 1500},
                {"item": "Wire (1m)", "category": "Electrical", "price": 20},
                {"item": "Plug", "category": "Electrical", "price": 30},
                {"item": "Pipe", "category": "Hardware", "price": 100},
                {"item": "LED Bulb", "category": "Lighting", "price": 200},
            ]

    def connect(self):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_file, SCOPES)
            self.client = gspread.authorize(creds)
            print("Connected to Google Sheets")
            self.refresh_inventory()
        except Exception as e:
            print(f"Error connecting to sheets: {e}")

    def refresh_inventory(self):
        if not self.client: return
        try:
            # Open by Key (ID)
            spreadsheet = self.client.open_by_key(self.inventory_sheet_id)
            
            # Debug: List all worksheets
            worksheets = spreadsheet.worksheets()
            print(f"DEBUG: Available worksheets: {[ws.title for ws in worksheets]}")

            try:
                sheet = spreadsheet.worksheet("inventory")
                self.inventory_data = sheet.get_all_records()
                print(f"DEBUG: Inventory successfully loaded. {len(self.inventory_data)} items found.")
            except gspread.WorksheetNotFound:
                print("ERROR: Worksheet 'inventory' not found. Falling back to first sheet.")
                sheet = spreadsheet.sheet1
                self.inventory_data = sheet.get_all_records()
                print(f"DEBUG: Inventory refreshed from first worksheet: '{sheet.title}'. {len(self.inventory_data)} items found.")

            # Print first 3 items to verify structure
            if self.inventory_data:
                print(f"DEBUG: First 3 items sample: {self.inventory_data[:3]}")
            else:
                print("DEBUG: Inventory is EMPTY!")

        except Exception as e:
            print(f"CRITICAL ERROR reading inventory: {type(e).__name__}: {e}")
            # Do NOT suppress error, let user see it clearly
            import traceback
            traceback.print_exc()

    def search_inventory(self, query: str):
        print(f"DEBUG: Searching inventory for: '{query}'")
        # fuzzy search or simple checking
        query = query.lower()
        query_tokens = query.split() # ['usha', 'fan']
        
        results = []
        for item in self.inventory_data:
            # Check if ANY value in the item dict contains ALL tokens
            # e.g. if item is "Usha Wall Fan", it contains 'usha' AND 'fan'
            
            # Create a localized string of the entire item for searching
            # e.g. "Usha Wall Fan Electrical 1500"
            item_str = " ".join([str(v).lower() for v in item.values()])
            
            # Check if all tokens search query tokens are present in the item string
            if all(token in item_str for token in query_tokens):
                results.append(item)
        
        print(f"DEBUG: Found {len(results)} matches for '{query}'")
        return results

    def add_order(self, order_details):
        if not self.client:
            print(f"Mock Order Placed: {order_details}")
            return True
            
        try:
            # Open the same spreadsheet by ID, then find the specific 'Orders' tab
            sheet = self.client.open_by_key(self.inventory_sheet_id).worksheet("Orders")
            
            # Assuming order_details is a list of items. We want to format it nicely.
            # Columns: Timestamp, Order Content, Status
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            items_str = ", ".join([f"{item['quantity']}x {item['name']}" for item in order_details['items']])
            row = [timestamp, items_str, "Confirmed", str(order_details)]
            sheet.append_row(row)
            return True
        except Exception as e:
            print(f"Error adding order: {e}")
            return False

    def get_orders(self):
        if not self.client:
            return [{"timestamp": "N/A", "items": "Mock Order", "status": "Mock", "raw": "{}"}]
            
        try:
            sheet = self.client.open_by_key(self.inventory_sheet_id).worksheet("Orders")
            return sheet.get_all_records()
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return []
