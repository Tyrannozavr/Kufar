import re
from typing import List, Dict, Optional

from bs4 import BeautifulSoup


async def extract_pagination_links(html_content: str) -> List[str]:
    soup = BeautifulSoup(html_content, 'html.parser')
    pagination_div = soup.find('div', class_='styles_links__wrapper__ig13W')
    if not pagination_div:
        return []

    links = pagination_div.find_all('a', class_='styles_link__8m3I9')
    base_url = "https://re.kufar.by"
    return [f"{base_url}{link['href']}" for link in links if 'href' in link.attrs]


def extract_area_from_parameters(parameters_text: str) -> Optional[float]:
    """
    Извлекает площадь из строки параметров.
    Поддерживает разные форматы:
    - "114 м², этаж 1" -> 114.0
    - "775.5 м², этаж 1 из 5" -> 775.5
    - "150 кв.м." -> 150.0
    - "150 кв м" -> 150.0
    """
    if not parameters_text:
        return None
    
    # Ищем разные форматы площади
    patterns = [
        r'(\d+\.?\d*)\s*м²',  # "114 м²"
        r'(\d+\.?\d*)\s*кв\.?\s*м',  # "150 кв.м." или "150 кв м"
        r'(\d+\.?\d*)\s*кв\.м',  # "150 кв.м"
        r'(\d+\.?\d*)\s*м\s*²',  # "114 м ²" (с пробелом)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, parameters_text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    return None


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
        # Пробуем несколько вариантов классов на случай изменения верстки
        parameters = listing_a.find('div', class_='styles_parameters__7zKlL')
        if not parameters:
            # Пробуем найти по другому классу или по тексту
            parameters = listing_a.find('div', class_=re.compile('parameter', re.I))
        if not parameters:
            # Ищем div содержащий "м²"
            for div in listing_a.find_all('div'):
                if 'м²' in div.text:
                    parameters = div
                    break
        
        parameters_text = parameters.text.strip() if parameters else ''
        
        # Extract area from parameters
        area = extract_area_from_parameters(parameters_text)

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
            'area': area,  # Добавляем площадь отдельно
            'prices': prices,
            'address': address,
            'photo_url': photo_url
        }

        all_listings_data.append(listing_data)

    return all_listings_data
