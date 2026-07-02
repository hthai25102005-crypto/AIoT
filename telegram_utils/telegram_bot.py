import requests

TOKEN="8982026853:AAHPcKW9SZoHIRoPOEc0-d6GhNKmJMMwf_4"
CHAT_ID="8400023438"

def send_alert(msg, image_path=None):

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

    if image_path:
        with open(image_path,"rb") as photo:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID, "caption": msg},
                files={"photo": photo}
            )