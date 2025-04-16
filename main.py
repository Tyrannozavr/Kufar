import asyncio
import json
from typing import List, Dict

import httpx
from pathlib import Path
from downloader import download_all_pages
from extractor import extract_all_listings_data
from logger_config import logger

from services import update_offers


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
    with open(storage_path, 'w', encoding='utf-8') as f:
        json.dump(all_listings_data, f, ensure_ascii=False, indent=2)

    return all_listings_data


async def main():
    # Initial parsing
    await start_parsing()

    # Update offers
    async with httpx.AsyncClient(timeout=30.0, verify=True, http2=True) as session:
        print(f"Updating offers... session type is {type(session)}")
        new_offers = await update_offers(session)

    print(f"Found {len(new_offers)} new offers.")

if __name__ == "__main__":
    asyncio.run(main())
