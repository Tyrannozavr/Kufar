import asyncio
import os

from dotenv import load_dotenv

from notifications import TelegramNotification
from schema import ListingItem

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

telegram_notification = TelegramNotification(
    bot_token=bot_token,
    chat_id=chat_id
)


async def main():
    item = {
        "id": "1014572788",
        "parameters": "71.3 м², этаж 1 из 3",
        "prices": {
            "byn": "1 711 р.",
            "usd": "555.03 $*",
            "per_meter": "24 p. / м²"
        },
        "address": "Янки Купалы ул, 3, Брест, Брестская обл.",
        "photo_url": "https://rms.kufar.by/v1/list_thumbs_2x/adim1/9b9bb479-c6d4-4266-a3ad-d176a58ae946.jpg"
    }
    item = ListingItem.from_dict(item)
    await telegram_notification.send_notification(item)
if __name__ == "__main__":
    asyncio.run(main())