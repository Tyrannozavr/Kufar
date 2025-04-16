from aiogram import Bot
from aiogram.enums import ParseMode
from schema import ListingItem
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

    async def send_error(self, err: str):
        try:
            error_message = f"❗️ <b>Произошла ошибка</b>\n\n<pre>{err}</pre>"
            await self._bot.send_message(
                chat_id=self._chat_id,
                text=error_message,
                parse_mode=ParseMode.HTML
            )
            print(f"Error notification sent: {err}")
        except Exception as e:
            print(f"Failed to send error notification: {str(e)}")

    async def close(self):
        await self._bot.close()

class EmailNotification:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str, recipient_email: str):
        self._smtp_server = smtp_server
        self._smtp_port = smtp_port
        self._sender_email = sender_email
        self._sender_password = sender_password
        self._recipient_email = recipient_email

    def _render_message(self, item: ListingItem) -> str:
        message = f"""
        <h2>Новое объявление</h2>
        <p><strong>Параметры:</strong> {item.parameters}</p>
        <p><strong>Адрес:</strong> {item.address}</p>
        <p>ЕТ/Д</p>
        <h3>Цена:</h3>
        """

        if item.prices.byn:
            message += f"<p>BYN: {item.prices.byn}</p>"
        if item.prices.usd:
            message += f"<p>USD: {item.prices.usd}</p>"
        if item.prices.per_meter:
            message += f"<p>За м²: {item.prices.per_meter}</p>"

        message += f"<p><a href='https://re.kufar.by/vi/brest/snyat/kommercheskaya/magaziny/{item.id}?searchId=5591851b475bb654ab25f35c6b40a1a72922'>Подробнее</a></p>"

        if item.photo_url:
            message += f"<img src='{item.photo_url}' alt='Фото объявления'>"

        return message

    async def send_notification(self, item: ListingItem):
        subject = item.address
        html_content = self._render_message(item)

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self._sender_email
            message["To"] = self._recipient_email

            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            with smtplib.SMTP(self._smtp_server, self._smtp_port) as server:
                server.starttls()
                server.login(self._sender_email, self._sender_password)
                server.sendmail(self._sender_email, self._recipient_email, message.as_string())

            print(f"Email notification sent for listing {item.id}")
        except Exception as e:
            print(f"Failed to send email notification for listing {item.id}: {str(e)}")

    async def send_error(self, err: str):
        subject = "Ошибка в приложении Kufar"
        html_content = f"""
        <h2>Произошла ошибка</h2>
        <pre>{err}</pre>
        """

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self._sender_email
            message["To"] = self._recipient_email

            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            with smtplib.SMTP(self._smtp_server, self._smtp_port) as server:
                server.starttls()
                server.login(self._sender_email, self._sender_password)
                server.sendmail(self._sender_email, self._recipient_email, message.as_string())

            print(f"Error email notification sent: {err}")
        except Exception as e:
            print(f"Failed to send error email notification: {str(e)}")

    async def close(self):
        # No need to close anything for email, but keeping the method for consistency
        pass