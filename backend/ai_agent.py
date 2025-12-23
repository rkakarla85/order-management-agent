from openai import OpenAI
import os
import json
from sheets_manager import SheetsManager
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
sheets = SheetsManager()

# Simple session state management (for demo purposes)
# In production, use a database or Redis
sessions = {}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_inventory",
            "description": "Search for items in the inventory. Use this when the user asks for products.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for the item (e.g., 'switch', 'fan')"
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
            "description": "Add items to the current order cart. Do NOT use this to confirm the order, just to build the list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "quantity": {"type": "integer"}
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

SYSTEM_PROMPT = """
You are a helpful Voice Assistant for an electronics shop. 
Your goal is to help customers place orders.
1. Greet the customer and ask what they need.
2. Search the inventory when they ask for items.
3. If found, ask for quantity and add to cart.
4. If not found, apologize.
5. ALWAYS extract precise item names and quantities.
6. Before placing the order, list the items in the cart and ask for confirmation.
7. Only call 'confirm_and_place_order' when the user explicitly says "Yes" or "Confirm".
8. Keep your responses concise and conversational (suitable for voice).
"""

def get_agent_response(session_id, user_text, image_url=None):
    if session_id not in sessions:
        sessions[session_id] = {
            "history": [{"role": "system", "content": SYSTEM_PROMPT}],
            "cart": []
        }
    
    session = sessions[session_id]
    
    if image_url:
        # Multimodal message structure
        content_payload = [
            {"type": "text", "text": user_text or "Please look at this image and identify the items."},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
        session["history"].append({"role": "user", "content": content_payload})
    else:
        # Standard text message
        session["history"].append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=session["history"],
        tools=TOOLS,
        tool_choice="auto"
    )

    msg = response.choices[0].message
    
    if msg.tool_calls:
        session["history"].append(msg) # Add the assistant's tool call message
        
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            result_content = ""
            
            if fn_name == "search_inventory":
                results = sheets.search_inventory(args["query"])
                if results:
                    result_content = f"Found: {json.dumps(results)}"
                else:
                    result_content = "No items found matching that query."
            
            elif fn_name == "add_to_cart":
                items = args["items"]
                session["cart"].extend(items)
                result_content = f"Added {len(items)} items to cart. Current Cart: {json.dumps(session['cart'])}"
            
            elif fn_name == "confirm_and_place_order":
                if not session["cart"]:
                    result_content = "Cart is empty. cannot place order."
                else:
                    success = sheets.add_order({"items": session['cart']})
                    if success:
                        result_content = "Order placed successfully in the system."
                        session["cart"] = [] # Clear cart
                    else:
                        result_content = "Failed to place order due to system error."

            session["history"].append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_content
            })
        
        # Get final response after tool execution
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
