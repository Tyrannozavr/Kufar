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


async def start_parsing(storage_file: str = None) -> List[Dict[str, str]]:
    # Get storage file path from environment or use default
    if storage_file is None:
        storage_file = os.getenv("STORAGE_FILE", "listings_data.json")
    
    storage_path = Path(storage_file)
    
    # Ensure directory exists
    storage_path.parent.mkdir(parents=True, exist_ok=True)

    existing_data = []
    if storage_path.exists():
        # If storage file exists, load data from it
        with open(storage_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        logger.info(f"Loaded {len(existing_data)} existing listings from {storage_path}")

    # Always download pages and extract data to check for new listings
    async with httpx.AsyncClient(timeout=30.0, verify=True, http2=True) as session:
        saved_files = await download_all_pages(session)

    all_listings_data = []
    for file in saved_files:
        with open(file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            listings_data = extract_all_listings_data(html_content)
            all_listings_data.extend(listings_data)

    # Create a set of existing listings for quick lookup
    existing_set = set()
    for item in existing_data:
        # Use a combination of address and parameters as unique identifier
        unique_id = f"{item.get('address', '')}_{item.get('parameters', '')}"
        existing_set.add(unique_id)

    # Add only new listings
    new_listings = []
    for listing in all_listings_data:
        unique_id = f"{listing.get('address', '')}_{listing.get('parameters', '')}"
        if unique_id not in existing_set:
            new_listings.append(listing)
            existing_data.append(listing)
            logger.info(f"Found new listing: {listing.get('address', 'N/A')}")

    # Save updated data to storage file
    with open(storage_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Updated {storage_path} with {len(new_listings)} new listings. Total: {len(existing_data)}")
    return existing_data


async def main():
    # Initial parsing
    await start_parsing()

    error_count = 0
    
    # Initialize notifications based on environment variables
    telegram_notification = None
    email_notification = None
    
    # Check if Telegram notifications are enabled
    if os.getenv("ENABLE_TELEGRAM", "true").lower() == "true":
        bot_token = os.getenv("BOT_TOKEN")
        chat_id = os.getenv("CHAT_ID")
        if bot_token and chat_id:
            telegram_notification = TelegramNotification(bot_token=bot_token, chat_id=chat_id)
            logger.info("Telegram notifications enabled")
        else:
            logger.warning("Telegram notifications disabled: missing BOT_TOKEN or CHAT_ID")
    else:
        logger.info("Telegram notifications disabled by ENABLE_TELEGRAM setting")
    
    # Check if Email notifications are enabled
    if os.getenv("ENABLE_EMAIL", "false").lower() == "true":
        sender_email = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDER_PASSWORD")
        recipient_email = os.environ.get("RECIPIENT_EMAIL")
        if sender_email and sender_password and recipient_email:
            email_notification = EmailNotification(
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                sender_email=sender_email,
                sender_password=sender_password,
                recipient_email=recipient_email
            )
            logger.info("Email notifications enabled")
        else:
            logger.warning("Email notifications disabled: missing email credentials")
    else:
        logger.info("Email notifications disabled by ENABLE_EMAIL setting")

    async with httpx.AsyncClient(timeout=30.0, verify=True, http2=True) as session:
        while True:
            try:
                logger.info("Updating offers...")
                new_offers = await update_offers(session)
                
                # Send notifications for new offers
                for offer in new_offers:
                    offer = ListingItem.from_dict(offer)
                    notification_tasks = []
                    
                    if telegram_notification:
                        notification_tasks.append(telegram_notification.send_notification(offer))
                    
                    if email_notification:
                        notification_tasks.append(email_notification.send_notification(offer))
                    
                    if notification_tasks:
                        await asyncio.gather(*notification_tasks)

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
                    
                    # Send error notifications
                    error_tasks = []
                    if telegram_notification:
                        error_tasks.append(telegram_notification.send_error(error_message))
                    # Временно закомментировано для тестирования
                    # if email_notification:
                    #     error_tasks.append(email_notification.send_error(error_message))
                    
                    if error_tasks:
                        await asyncio.gather(*error_tasks)
                    
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