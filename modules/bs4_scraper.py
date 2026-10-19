"""
BeautifulSoup-based web scraper for static HTML parsing
Extracts product data: title, prices, images, code, reviews, specifications
Flow: download HTML via requests → parse with BeautifulSoup → extract fields → save to DB
"""

import re
from pprint import pprint

import requests
from bs4 import BeautifulSoup, Tag

from load_django import *  # type: ignore
from modules.base_parser import Parser
from parser_app.models import Product

URL = (
    "https://brain.com.ua/ukr/"
    "Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_"
    "Black_Titanium-p1145443.html"
)


class ProductScraper:
    @staticmethod
    def scrape_product(url: str):
        downloader = RequestsDataDownloader()
        html = downloader.download_page(url)
        parser = BeautifulSoupDataParser(html, URL)
        pprint(parser.product_data, sort_dicts=False, indent=4)
        ProductDataSaver.save_product(parser.product_data)


class RequestsDataDownloader:
    def __init__(self):
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) "
                "Gecko/20100101 Firefox/126.0"
            ),
            "Accept-Language": "uk-UA,uk;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self._base_url = "https://brain.com.ua/ukr/"
        self._session = requests.Session()
        self._session.headers.update(self._headers)

    def download_page(self, url) -> str:
        response = self._session.get(url, timeout=30)
        response.raise_for_status()
        return response.text


class BeautifulSoupDataParser(Parser):
    def __init__(self, html_text: str, source_url: str):
        self._source_url = source_url
        self._soup = BeautifulSoup(html_text, "lxml")
        self._product_data: dict | None = None

    @property
    def product_data(self) -> dict:
        if self._product_data is None:
            self._product_data = self._scrape_product()
        return self._product_data

    def _scrape_product(self) -> dict:
        self._check_html()

        specifications = self._get_specifications()
        images = self._get_images()

        product = {
            "source_url": self._source_url,
            "title": self._safe_get_text(self._soup.find("h1", class_="main-title")),
            "price": self._get_price(),
            "discount_price": self._get_discount_price(),
            "images": images,
            "product_code": self._safe_get_text(
                self._soup.select_one("#product_code .br-pr-code-val")
            ),
            "reviews_count": self._get_reviews_count(),

            "color": specifications.get("Колір", None),
            "storage_capacity": specifications.get("Вбудована пам'ять", None),
            "manufacturer": specifications.get("Виробник", None),
            "screen_diagonal_inches": self._get_diagonal_inches(
                specifications.get("Діагональ екрану", None)
            ),
            "screen_resolution": specifications.get("Роздільна здатність екрану", None),
            "specifications": specifications,
        }
        return product

    def _check_html(self):
        if self._soup.find("h1", class_="main-title") is None:
            raise ValueError(
                "Product name not found. Check the HTML response."
            )

    def _safe_get_text(self, element: Tag | None) -> str | None:
        if element is None:
            return None

        value = element.get_text(" ", strip=True)
        value = re.sub(r"\s+", " ", value).strip()
        return value or None

    def _get_specifications(self):
        specifications = dict()
        container = self._soup.find("div", id="br-characteristics")

        if container is None:
            return specifications

        for element in container.find_all("div"):
            spans = element.find_all("span", recursive=False)

            if len(spans) != 2:
                continue

            key = self._safe_get_text(spans[0])
            value = self._safe_get_text(spans[1])

            if key and value:
                specifications[key.rstrip(":")] = value

        return specifications

    def _get_images(self) -> list[str]:
        images = [
            str(image.get("src"))
            for image
            in self._soup.find_all("img", class_="br-main-img")
        ]
        return list(filter(None, images))

    def _get_price(self):
        return self._safe_to_float(
            self._safe_get_text(
                self._soup.select_one(
                    ".price-wrapper > span:not(.red-price)"
                )
            ))

    def _get_discount_price(self):
        return self._safe_to_float(
            self._safe_get_text(
                self._soup.select_one(".price-wrapper > span.red-price")
            ))

    def _get_reviews_count(self):
        return self._safe_to_int(self._safe_get_text(
            self._soup.select_one("#reviews a[href=\"#reviews-list\"] > span")
        ))


class ProductDataSaver:
    @staticmethod
    def save_product(product_data: dict):
        if product_data:
            product, created = Product.objects.get_or_create(**product_data)
            print(f"Product {product.title} saved")


if __name__ == "__main__":
    ProductScraper.scrape_product(URL)
