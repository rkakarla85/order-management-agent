TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_inventory",
            "description": "Search for items in the inventory/menu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for the item"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Add items to the current order cart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "quantity": {"type": "integer"},
                                "notes": {"type": "string", "description": "Optional notes for customization (e.g. 'Spicy', 'No onions')"}
                            }
                        }
                    }
                },
                "required": ["items"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "confirm_and_place_order",
            "description": "Finalize and place the order after user confirmation.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
