import json
import os
from typing import List, Optional, Dict

CONFIG_FILE = "business_config.json"

class BusinessManager:
    def __init__(self):
        self.businesses = self._load_businesses()

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
        return business_data
