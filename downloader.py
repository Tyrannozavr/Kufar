import asyncio
import random
from pathlib import Path
from typing import List

import httpx

from data import USER_AGENTS, URL
from extractor import extract_pagination_links



PAGES_DIR = Path("pages")

async def download_and_save_page(session: httpx.AsyncClient, url: str, output_file: str) -> str:
    """
    Download the page content and save it as HTML using an open session with protection measures.

    :param session: An open httpx.AsyncClient session
    :param url: The URL to download
    :param output_file: The name of the file to save the HTML content
    :return: The path of the saved file
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",
    }

    try:
        response = await session.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()

        # Create the pages directory if it doesn't exist
        PAGES_DIR.mkdir(exist_ok=True)

        # Save the content to a file in the pages directory
        output_path = PAGES_DIR / output_file
        output_path.write_text(response.text, encoding="utf-8")
        print(f"Page content saved to {output_path.absolute()}")
        return str(output_path.absolute())

    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")

    return ""

async def download_all_pages(session: httpx.AsyncClient) -> List[str]:
    saved_files = []

    # Download the first page
    first_page_file = await download_and_save_page(session, URL, "kufar_page1.html")
    saved_files.append(first_page_file)

    # Extract pagination links
    with open(first_page_file, 'r', encoding='utf-8') as f:
        pagination_links = await extract_pagination_links(f.read())

    # Download other pages
    for i, link in enumerate(pagination_links, start=2):
        # Add a random delay before the request
        await asyncio.sleep(random.uniform(3, 7))

        file_name = f"kufar_page{i}.html"
        saved_file = await download_and_save_page(session, link, file_name)
        if saved_file:
            saved_files.append(saved_file)

    return saved_files