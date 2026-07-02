from telegram import Bot
import asyncio

class TelegramNotifier:

    def __init__(self, token, chat_id):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_message_async(self, text):
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=text
        )

    async def send_photo_async(
        self,
        image_path,
        caption=""
    ):
        with open(image_path, "rb") as img:

            await self.bot.send_photo(
                chat_id=self.chat_id,
                photo=img,
                caption=caption
            )

    def send_message(self, text):
        asyncio.run(
            self.send_message_async(text)
        )

    def send_photo(
        self,
        image_path,
        caption=""
    ):
        asyncio.run(
            self.send_photo_async(
                image_path,
                caption
            )
        )