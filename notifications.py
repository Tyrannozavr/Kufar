from aiogram import Bot
from aiogram.enums import ParseMode

from schema import ListingItem


class TelegramNotification:
    def __init__(self, bot_token: str, chat_id: str):
        self._bot = Bot(token=bot_token)
        self._chat_id = chat_id

    def _render_message(self, item: ListingItem) -> str:
        message = (
            f"🏠 <b>Новое объявление</b>\n\n"
            f"📏 {item.parameters}\n"
            f"📍 {item.address}\n\n"
            f"💰 Цена:\n"
        )

        if item.prices.byn:
            message += f"   BYN: {item.prices.byn}\n"
        if item.prices.usd:
            message += f"   USD: {item.prices.usd}\n"
        if item.prices.per_meter:
            message += f"   За м²: {item.prices.per_meter}\n"

        message += f"\n🔗 <a href='https://re.kufar.by/vi/brest/snyat/kommercheskaya/magaziny/{item.id}?searchId=5591851b475bb654ab25f35c6b40a1a72922'>Подробнее</a>"

        return message

    async def send_notification(self, item: ListingItem):
        message = self._render_message(item)

        try:
            if item.photo_url:
                await self._bot.send_photo(
                    chat_id=self._chat_id,
                    photo=item.photo_url,
                    caption=message,
                    parse_mode=ParseMode.HTML
                )
            else:
                await self._bot.send_message(
                    chat_id=self._chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
            print(f"Notification sent for listing {item.id}")
        except Exception as e:
            print(f"Failed to send notification for listing {item.id}: {str(e)}")

    async def close(self):
        await self._bot.close()
class EmailNotification:
    pass