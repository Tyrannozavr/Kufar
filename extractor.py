import re
from typing import List, Dict

from bs4 import BeautifulSoup


async def extract_pagination_links(html_content: str) -> List[str]:
    soup = BeautifulSoup(html_content, 'html.parser')
    pagination_div = soup.find('div', class_='styles_links__wrapper__ig13W')
    if not pagination_div:
        return []

    links = pagination_div.find_all('a', class_='styles_link__8m3I9')
    base_url = "https://re.kufar.by"
    return [f"{base_url}{link['href']}" for link in links if 'href' in link.attrs]


def extract_all_listings_data(html_content: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html_content, 'html.parser')
    listings = soup.find_all('section')

    all_listings_data = []

    for listing in listings:
        listing_a = listing.find('a', class_='styles_wrapper__Q06m9')
        if not listing_a:
            continue

        # Extract ID
        href = listing_a.get('href', '')
        id_match = re.search(r'/(\d+)\?', href)
        listing_id = id_match.group(1) if id_match else ''

        # Extract parameters (area and floor)
        parameters = listing_a.find('div', class_='styles_parameters__7zKlL')
        parameters_text = parameters.text if parameters else ''

        # Extract prices
        price_div = listing_a.find('div', class_='styles_price__gpHWH')
        prices = {}
        if price_div:
            for span in price_div.find_all('span'):
                class_name = span.get('class', [''])[0]
                if 'byr' in class_name:
                    prices['byn'] = span.text
                elif 'usd' in class_name:
                    prices['usd'] = span.text
                elif 'meter' in class_name:
                    prices['per_meter'] = span.text

        # Extract address
        address_span = listing_a.find('span', class_='styles_address__l6Qe_')
        address = address_span.text if address_span else ''

        # Extract photo URL
        photo_div = listing_a.find('div', class_='styles_image__7aRPM')
        photo_url = ''
        if photo_div:
            img = photo_div.find('img')
            if img:
                photo_url = img.get('src', '')

        listing_data = {
            'id': listing_id,
            'parameters': parameters_text,
            'prices': prices,
            'address': address,
            'photo_url': photo_url
        }

        all_listings_data.append(listing_data)

    return all_listings_data
