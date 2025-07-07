import asyncio
import json
import os
import random
from typing import List, Dict

import httpx
from pathlib import Path

from dotenv import load_dotenv

from downloader import download_all_pages
from extractor import extract_all_listings_data
from logger_config import logger
from notifications import TelegramNotification, EmailNotification
from schema import ListingItem

from services import update_offers

# Constants for timing
MIN_DELAY = 55  # minimum delay in seconds
MAX_DELAY = 65  # maximum delay in seconds
MAX_CONSECUTIVE_ERRORS = 3
ERROR_COOLDOWN = 300  # 5 minutes cooldown after consecutive errors
load_dotenv()


async def start_parsing(storage_file: str = "listings_data.json") -> List[Dict[str, str]]:
    storage_path = Path(storage_file)

    if storage_path.exists():
        # If storage file exists, load data from it
        with open(storage_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # If storage file doesn't exist, download pages and extract data
    async with httpx.AsyncClient(timeout=30.0, verify=True, http2=True) as session:
        saved_files = await download_all_pages(session)

    all_listings_data = []
    for file in saved_files:
        with open(file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            listings_data = extract_all_listings_data(html_content)
            all_listings_data.extend(listings_data)

    # Save extracted data to storage file
    with open(storage_path, 'w', encoding='utf-8') as f:\
        json.dump(all_listings_data, f, ensure_ascii=False, indent=2)

    logger.info(f"updated {storage_path} with {len(all_listings_data)}")
    return all_listings_data


async def main():
    # Initial parsing
    await start_parsing()

    error_count = 0
    telegram_notification = TelegramNotification(
        bot_token=os.getenv("BOT_TOKEN"),
        chat_id=os.getenv("CHAT_ID")
    )
    email_notification = EmailNotification(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email=os.environ.get("SENDER_EMAIL"),
        sender_password=os.environ.get("SENDER_PASSWORD"),
        recipient_email=os.environ.get("RECIPIENT_EMAIL")
    )

    # Then use it in your main script

    async with httpx.AsyncClient(timeout=30.0, verify=True, http2=True) as session:
        while True:
            try:
                logger.info("Updating offers...")
                new_offers = await update_offers(session)
                for offer in new_offers:
                    offer = ListingItem.from_dict(offer)
                    await asyncio.gather(
                        telegram_notification.send_notification(offer),
                        # email_notification.send_notification(offer)
                    )
                    # await telegram_notification.send_notification(offer)
                    # await email_notification.send_notification(offer)

                logger.info(f"Found {len(new_offers)} new offers.")
                
                # Reset error count on successful update
                error_count = 0

                # Random delay before next update
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                logger.info(f"Waiting for {delay:.2f} seconds before next update.")
                await asyncio.sleep(delay)

            except Exception as e:
                error_count += 1
                logger.error(f"Error occurred: {e}")
                
                if error_count >= MAX_CONSECUTIVE_ERRORS:
                    error_message = f"Too many consecutive errors ({error_count}). Last error: {str(e)}"
                    logger.warning(error_message)
                    await telegram_notification.send_error(error_message)
                    logger.warning(f"Cooling down for {ERROR_COOLDOWN} seconds.")
                    await asyncio.sleep(ERROR_COOLDOWN)
                    error_count = 0
                else:
                    # Shorter delay on error, but still random
                    delay = random.uniform(MIN_DELAY / 2, MAX_DELAY / 2)
                    logger.info(f"Retrying in {delay:.2f} seconds.")
                    await asyncio.sleep(delay)

if __name__ == "__main__":
    asyncio.run(main())