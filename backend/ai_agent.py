from openai import OpenAI
import os
import json
from sheets_manager import SheetsManager
from business_manager import BusinessManager
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
business_manager = BusinessManager()

# Cache for SheetsManager instances to avoid reconnecting every time
# Key: business_id, Value: SheetsManager instance
sheet_instances = {}

# Simple session state management
# Key: session_id, Value: { history: [], cart: [], business_id: str }
sessions = {}

def get_sheets_manager(business_id):
    if business_id in sheet_instances:
        return sheet_instances[business_id]
    
    biz_config = business_manager.get_business(business_id)
    if not biz_config:
        print(f"Error: Business ID {business_id} not found.")
        return None
        
    instance = SheetsManager(inventory_sheet_id=biz_config["sheet_id"])
    sheet_instances[business_id] = instance
    return instance

from jinja2 import Environment, FileSystemLoader

# ... (retain existing imports)

# Setup Jinja2 Environment
prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
jinja_env = Environment(loader=FileSystemLoader(prompts_dir))

# ... (retain existing code up to get_system_prompt)

def get_system_prompt(business_type, current_time=None):
    try:
        if business_type == "restaurant":
            template = jinja_env.get_template('restaurant.j2')
            return template.render(current_time=current_time)
        else:
            # Default Retail/Electronics
            template = jinja_env.get_template('retail.j2')
            return template.render()
    except Exception as e:
        print(f"Error loading prompt template: {e}")
        # Fallback to a basic prompt if template loading fails
        return "You are a helpful assistant."

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

def get_agent_response(session_id, user_text, image_url=None, business_id="electronics_default"):
    # Initialize Session
    if session_id not in sessions:
        biz_config = business_manager.get_business(business_id)
        if not biz_config:
            # Fallback
            biz_config = {"type": "retail"}
        
        current_time_str = datetime.now().strftime("%H:%M")
        system_prompt = get_system_prompt(biz_config["type"], current_time_str)
        
        sessions[session_id] = {
            "history": [{"role": "system", "content": system_prompt}],
            "cart": [],
            "business_id": business_id
        }
    
    session = sessions[session_id]
    
    # Ensure we use the correct Sheets instance for this session's business
    current_biz_id = session.get("business_id", business_id)
    sheets = get_sheets_manager(current_biz_id)
    
    if image_url:
        content_payload = [
            {"type": "text", "text": user_text or "Please look at this image and identify the items."},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
        session["history"].append({"role": "user", "content": content_payload})
    else:
        session["history"].append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=session["history"],
        tools=TOOLS,
        tool_choice="auto"
    )

    msg = response.choices[0].message
    
    if msg.tool_calls:
        session["history"].append(msg)
        
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result_content = ""
            
            if fn_name == "search_inventory":
                if sheets:
                    results = sheets.search_inventory(args["query"])
                    if results:
                        result_content = f"Found: {json.dumps(results)}"
                    else:
                        result_content = "No items found."
                else:
                     result_content = "System Error: Inventory unavailable."
            
            elif fn_name == "add_to_cart":
                items = args["items"]
                session["cart"].extend(items)
                result_content = f"Added items. Current Cart: {json.dumps(session['cart'])}"
            
            elif fn_name == "confirm_and_place_order":
                if not session["cart"]:
                    result_content = "Cart is empty."
                elif sheets:
                    success = sheets.add_order({"items": session['cart']})
                    if success:
                        result_content = "Order placed successfully."
                        session["cart"] = []
                    else:
                        result_content = "Failed to place order."
                else:
                    result_content = "System Error: Order system unavailable."

            session["history"].append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_content
            })
        
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=session["history"]
        )
        final_msg = final_response.choices[0].message.content
        session["history"].append({"role": "assistant", "content": final_msg})
        return final_msg
    else:
        session["history"].append(msg)
        return msg.content
