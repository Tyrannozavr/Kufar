import asyncio
import json
from typing import List, Dict

import httpx
from pathlib import Path
from downloader import download_all_pages
from extractor import extract_all_listings_data

async def process_pages(saved_files):
    all_listings = []
    for file in saved_files:
        with open(file, 'r', encoding='utf-8') as f:
            html_content = f.read()
            listings_data = extract_all_listings_data(html_content)
            all_listings.extend(listings_data)
    return all_listings



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
    await start_parsing()

if __name__ == "__main__":
    asyncio.run(main())

# площадь
# адрес
# фото
# цена
# id
# https://re.kufar.by/vi/gomel/snyat/kommercheskaya/magaziny/1003991422?rank=58&searchId=3a5060eed5996b107f2070f7f12830472565
# https://re.kufar.by/vi/minsk/snyat/kommercheskaya/magaziny/246430817?rank=57&searchId=3a5060eed5996b107f2070f7f12830472565
# https://re.kufar.by/vi/postavy/snyat/kommercheskaya/magaziny/239021229?rank=55&searchId=3a5060eed5996b107f2070f7f12830472565