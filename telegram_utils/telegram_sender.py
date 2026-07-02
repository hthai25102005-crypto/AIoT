import requests

class TelegramSender:

    def __init__(self):

        self.token="TOKEN"

        self.chat_id="CHATID"

    def send(self,image,caption):

        url=(
        f"https://api.telegram.org/"
        f"bot{self.token}/sendPhoto"
        )

        with open(image,"rb") as photo:

            requests.post(
                url,
                data={
                    "chat_id":self.chat_id,
                    "caption":caption
                },
                files={
                    "photo":photo
                }
            )