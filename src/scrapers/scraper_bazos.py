import logging
import re
import time
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from ..part_offer import PartOffer
from .scraper_base import ScraperBase

logger = logging.getLogger(__name__)


class ScraperBazos(ScraperBase):
    name = "Bazos.sk"
    color = 0xE53935  # Red (Bazos brand color)
    logo_url = "https://www.bazos.sk/obrazky/bazos.svg"

    BASE_URL = "https://www.bazos.sk/search.php"

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "sk,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    }

    def __init__(self, queries: list[str], delay_between_requests: float = 1.5):
        self._queries = queries
        self._delay = delay_between_requests

    def _build_url(self, query: str) -> str:
        return f"{self.BASE_URL}?hledat={quote_plus(query)}&rubriky=www&humkreis=25&kitx=ano"

    def _fetch_page(self, url: str) -> str | None:
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _parse_offers(self, html: str, query: str) -> list[PartOffer]:
        soup = BeautifulSoup(html, "html.parser")
        offers = []

        listings = soup.select("div.inzeraty.inzeratyflex")

        for listing in listings:
            try:
                title_elem = listing.select_one("h2.nadpis > a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                link = title_elem.get("href", "")
                if not link.startswith("http"):
                    link = f"https:{link}" if link.startswith("//") else f"https://www.bazos.sk{link}"

                price_elem = listing.select_one("div.inzeratycena b span")
                price = price_elem.get_text(strip=True) if price_elem else "Neuvedená"

                location_elem = listing.select_one("div.inzeratylok")
                if location_elem:
                    location_parts = [t.strip() for t in location_elem.stripped_strings]
                    location = ", ".join(location_parts) if location_parts else "Neznáma"
                else:
                    location = "Neznáma"

                img_elem = listing.select_one("img.obrazek")
                image_url = img_elem.get("src", "") if img_elem else ""
                if image_url and not image_url.startswith("http"):
                    image_url = f"https:{image_url}" if image_url.startswith("//") else f"https://www.bazos.sk{image_url}"

                desc_elem = listing.select_one("div.popis")
                description = desc_elem.get_text(strip=True)[:300] if desc_elem else ""

                date_match = re.search(r"\[(\d{1,2}\.\d{1,2}\.\s*\d{4})\]", listing.get_text())
                date_posted = date_match.group(1) if date_match else ""

                offers.append(
                    PartOffer(
                        link=link,
                        title=title,
                        description=description,
                        price=price,
                        location=location,
                        image_url=image_url,
                        date_posted=date_posted,
                        search_query=query,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to parse listing: {e}")
                continue

        return offers

    def get_latest_offers(self) -> list[PartOffer]:
        all_offers: dict[str, PartOffer] = {}

        for i, query in enumerate(self._queries):
            if i > 0:
                time.sleep(self._delay)

            url = self._build_url(query)
            logger.info(f"Fetching: {query}")

            html = self._fetch_page(url)
            if not html:
                continue

            offers = self._parse_offers(html, query)
            logger.info(f"Found {len(offers)} offers for '{query}'")

            for offer in offers:
                if offer.link not in all_offers:
                    all_offers[offer.link] = offer

        return list(all_offers.values())
