from telegram import Bot
import asyncio

TOKEN = "8982026853:AAHPcKW9SZoHIRoPOEc0-d6GhNKmJMMwf_4"
CHAT_ID = "8400023438"

async def main():
    bot = Bot(token=TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID,
        text="🚨 TEST AIoT FALL DETECTION"
    )

asyncio.run(main())
