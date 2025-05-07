import os
import json
from pip._vendor import requests


def send_request_msg(message: str, chat_id: int) -> str:
    """request to Agent API
    Args:
        message (str): Message to be send.
        chat_id (int): User chat ID.

    Return:
        JSON response to the Agent API. Format:
        {
            "response": str,
            "chat_id": str,
            "timestamp": int
        }
    """
    # request to Agent API
    # Define the URL endpoint
    url = f"{os.environ['ELB_ENDPOINT']}/telegram/"
    # Prepare the headers
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    # Prepare the JSON payload
    payload = {"message": message, "chat_id": chat_id}
    # Send the POST request
    return requests.post(url, json=payload, headers=headers)


def lambda_handler(event, context):
    """Use Telegram Bot Webhook to recive and send messages"""

    body = json.loads(event.get("body", "{}"))
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if text:
        # TODO: uncomment below and set up ECS url to API
        response = send_request_msg(text, chat_id)
        response = response.json()
        # response = {"response": f"test lambda - {text}", "chat_id": 123}
        reply = response.get("response", "")
        # reply = f"You said: {text} - {chat_id}"
        # reply to user
        token = os.environ["TELEGRAM_TOKEN"]
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": reply},
        )

    return {"sttusCode": 200, "body": json.dumps("OK")}
