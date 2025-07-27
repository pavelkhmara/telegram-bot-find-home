import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

import logging
logger = logging.getLogger(__name__)

OLX_SEARCH_URL = "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/{city}/?search[filter_enum_rooms]={rooms}&search[filter_float_price%3Afrom]={price_from}&search[filter_float_price%3Ato]={price_to}"

def normalize_city(city):
    return city.lower().replace("ł", "l").replace("ó", "o").replace("ą", "a")\
        .replace("ś", "s").replace("ę", "e").replace("ż", "z").replace("ź", "z")\
        .replace("ń", "n").replace("ć", "c")

def build_url(filter_data: dict):
    city = normalize_city(filter_data.get("city", ""))
    rooms = re.sub(r"[^\d]", "", filter_data.get("rooms", ""))
    price_from = filter_data.get("price_from", "")
    price_to = filter_data.get("price_to", "")
    return OLX_SEARCH_URL.format(city=city, rooms=rooms, price_from=price_from, price_to=price_to)

async def fetch_olx_offers(filter_data: dict):
    url = build_url(filter_data)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            logger.info("Запрос к OLX: %s - статус %s", url, resp.status_code)
    except Exception as e:
        logger.exception("Ошибка при запросе к OLX: %s", e)
        return []

    soup = BeautifulSoup(resp.text, "lxml")

    offers = []
    for offer in soup.select("div[data-cy='l-card']")[:10]:  # Ограничим до 10
        title_el = offer.select_one("h6")
        link_el = offer.select_one("a")
        price_el = offer.select_one("p[data-testid='ad-price']")

        if not title_el or not link_el or not price_el:
            continue

        offers.append({
            "title": title_el.text.strip(),
            "url": "https://www.olx.pl" + link_el['href'].split('#')[0],
            "price": price_el.text.strip()
        })

    return offers
