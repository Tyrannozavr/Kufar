import asyncio
import random
from pathlib import Path
from typing import List

import httpx

from extractor import extract_pagination_links

USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
]
URL = "https://re.kufar.by/l/belarus/snyat/kommercheskaya/magaziny?cmpt=v.or%3A1%2C5%2C10%2C15%2C20%2C35&cur=BYR&fl=r%3A1%2C1&prn=1000&r_pageType=saved_search&size=30&sort=lst.d&st=r%3A70%2C1000"

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