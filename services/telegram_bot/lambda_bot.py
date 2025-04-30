import json
import os
import pip._vendor import requests

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    message = body.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if text:
        # get answer from Agent: TODO
        reply = requests.post()
        # reply to user
        token = os.environ["TELEGRAM_TOKEN"]
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      json={"chat_id": chat_id, "text": reply})
        
    return {"sttusCode": 200, "body": json.dumps("OK")}