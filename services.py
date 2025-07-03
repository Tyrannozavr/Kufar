import json
from pathlib import Path
from typing import List, Dict

import httpx

from data import URL
from extractor import extract_all_listings_data
from logger_config import logger


def transform_address_parameters(address: str, parameters: str) -> str:
    return "".join(address.split()).lower() + "".join(parameters.split()).lower()


def transform_item(item: Dict) -> str:
    return transform_address_parameters(address=item.get("address"), parameters=item.get("parameters"))


async def update_offers(session: httpx.AsyncClient, storage_file: str = "listings_data.json") -> List[Dict[str, str]]:
    storage_path = Path(storage_file)

    # Load existing data
    if storage_path.exists():
        with open(storage_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_parameters_addresses = set(
        transform_item(item=item)
        for item in existing_data
    )

    # Download the latest page using the provided session
    response = await session.get(URL)
    html_content = response.text

    # Extract listings from the new page
    new_listings = extract_all_listings_data(html_content)

    # Check for new offers
    new_offers = []
    for offer in new_listings:
        if transform_item(offer) not in existing_parameters_addresses:
            new_offers.append(offer)
            logger.info(f"New offer found: {offer}")
            existing_data.append(offer)

    # Update the storage file with new data
    with open(storage_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Updated storage file with {len(new_offers)} new offers.")
    return new_offers
