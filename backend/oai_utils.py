import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

_FUNCTION_DESCRIPTION = [
    {
        "type": "function",
        "function": {
            "name": "extract_order_info",
            "description": "Extract the order information from the given text. The order text can be 1. creating a new order or 2. updating or deleting an existing order. Orders consist of only Burgers, Fries, and Drinks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "is_creating_order": {
                        "type": "boolean",
                        "description": "Whether or not the order is a new order or modifies an existing order. e.g. 'true' if the order is a new order, 'false' if the order modifies an existing order. Note that only one of 'is_creating_order', 'is_deleting_order', and 'is_editing_order' can be 'true'.",
                    },
                    "is_deleting_order": {
                        "type": "boolean",
                        "description": "Whether or not the order is being deleted. e.g. 'true' if the order is being deleted, 'false' if the order is not being deleted. Note that only one of 'is_creating_order', 'is_deleting_order', and 'is_editing_order' can be 'true'.",
                    },
                    "is_editing_order": {
                        "type": "boolean",
                        "description": "Whether or not the order is being edited. e.g. 'true' if the order is being edited, 'false' if the order is not being edited. Note that only one of 'is_creating_order', 'is_deleting_order', and 'is_editing_order' can be 'true'.",
                    },
                    "order_number": {
                        "type": "string",
                        "description": "The order number of the order being modified if the order is not a new order. If the order is a new order, this field is not required.",
                    },
                    "burger_delta": {
                        "type": "integer",
                        "description": "The number of burgers to add or remove from the order. This field is required for both new orders and orders that modify an existing order.",
                    },
                    "fries_delta": {
                        "type": "integer",
                        "description": "The number of fries to add or remove from the order. This field is required for both new orders and orders that modify an existing order.",
                    },
                    "drinks_delta": {
                        "type": "integer",
                        "description": "The number of drinks to add or remove from the order. This field is required for both new orders and orders that modify an existing order.",
                    },
                },
                "required": [
                    "is_creating_order",
                    "is_deleting_order",
                    "is_editing_order",
                    "burger_delta",
                    "fries_delta",
                    "drinks_delta",
                ],
            },
        },
    },
]


def extract_order_info(order_text):

    messages = [
        {
            "role": "system",
            "content": "Extract the order information from the customer's text.",
        },
        {
            "role": "user",
            "content": order_text,
        },
    ]

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=_FUNCTION_DESCRIPTION,
    )
    if response.choices[0].message.tool_calls is None:
        return None

    return json.loads(response.choices[0].message.tool_calls[0].function.arguments)
