import json
import os
from typing import List, Optional, Dict
from sheets_manager import SheetsManager
from vector_store import VectorStoreManager

CONFIG_FILE = "business_config.json"

class BusinessManager:
    def __init__(self):
        self.businesses = self._load_businesses()
        self.vector_store = VectorStoreManager()
        
        # Ensure all loaded businesses are indexed (Self-Healing)
        # In production, check if exists first to avoid re-indexing every restart
        for biz in self.businesses:
            self.index_business(biz)

    def index_business(self, biz_data):
        try:
             print(f"Checking ingestion for {biz_data.get('name', 'Unknown')}...")
             # For this demo, we re-index on startup to ensure freshness. 
             # Optimization: Check if vector_store has items for this business_id before indexing.
             sheets = SheetsManager(inventory_sheet_id=biz_data['sheet_id'])
             if not sheets.inventory_data:
                 sheets.refresh_inventory()
             
             if sheets.inventory_data:
                 self.vector_store.index_inventory(biz_data['id'], sheets.inventory_data)
             else:
                 print(f"Warning: No inventory to index for {biz_data['id']}")
        except Exception as e:
            print(f"Error indexing {biz_data.get('name')}: {e}")

    def _load_businesses(self) -> List[Dict]:
        if not os.path.exists(CONFIG_FILE):
            return []
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading business config: {e}")
            return []

    def save_businesses(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.businesses, f, indent=2)
        except Exception as e:
            print(f"Error saving business config: {e}")

    def get_business(self, business_id: str) -> Optional[Dict]:
        for biz in self.businesses:
            if biz["id"] == business_id:
                return biz
        return None

    def list_businesses(self) -> List[Dict]:
        return self.businesses

    def create_business(self, business_data: Dict) -> Dict:
        # Simple ID generation if not provided
        if "id" not in business_data:
            business_data["id"] = f"biz_{len(self.businesses) + 1}"
        
        self.businesses.append(business_data)
        self.save_businesses()
        
        # Trigger Initial Indexing
        try:
            print(f"Triggering ingestion for {business_data.get('name', 'Unknown')} ({business_data['id']})...")
            sheets = SheetsManager(inventory_sheet_id=business_data['sheet_id'])
            # Ensure we have data
            if not sheets.inventory_data:
                sheets.refresh_inventory()
            
            if sheets.inventory_data:
                 self.vector_store.index_inventory(business_data['id'], sheets.inventory_data)
                 print("Ingestion successful.")
            else:
                print("Warning: No inventory data found to index.")

        except Exception as e:
            print(f"Error during ingestion: {e}")
            # Don't fail the create_business call, just log error

        return business_data
