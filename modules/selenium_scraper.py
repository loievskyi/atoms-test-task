import pprint
import re
import time
from urllib.parse import urlencode

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from modules.load_django import *  # type: ignore
from modules.selectors_schema import (
    product_selectors,
    specifications_selectors,
    search_selectors,
    Selector,
)
from modules.selectors_schema.xpath_selectors import list_selectors
from parser_app.models import Product


class SeleniumParser:
    def __init__(self, driver: WebDriver):
        self._driver = driver
        self._parsed_data: dict | None = None
        self._base_url = "https://brain.com.ua/ukr/"
        self._base_search_url = "https://brain.com.ua/ukr/search/"
        self._products_urls: list[str] = list()

    def run(self, search_query: str) -> dict | None:
        search_url = self._generate_search_url(search_query)
        self.download(search_url)
        # self.download(self._base_url)
        # self._perform_search(search_query)
        self.parse_list()
        for url in self._products_urls:
            self._products_urls.remove(url)
            self.download(url)
            self.parse_details()
            self.save_data()
            pprint.pprint(self._parsed_data, indent=4)

    def download(self, url: str) -> str:
        self._driver.get(url)
        wait = WebDriverWait(self._driver, 25)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(1)

        html = self._driver.execute_script("return document.documentElement.outerHTML;")
        return html

    def parse_list(self):
        products = self._driver.find_elements(by=By.XPATH, value=list_selectors.products.root)
        products_urls = {a.get_attribute("href") for a in products}
        products_urls = list(filter(None, products_urls))
        self._products_urls.extend(products_urls)

    def parse_details(self) -> dict | None:
        specifications_container = self._driver.find_element(
            By.XPATH,
            product_selectors.specifications_container.root,
        )
        self._parsed_data = dict(
            source_url=self._driver.current_url,
            title=self._safe_find_element_text(self._driver, product_selectors.title),
            color=self._safe_find_element_text(specifications_container, specifications_selectors.color),
            storage_capacity=self._safe_find_element_text(specifications_container,
                                                          specifications_selectors.storage_capacity),
            manufacturer=self._safe_find_element_text(specifications_container, specifications_selectors.manufacturer),

            price=self._safe_to_float(self._safe_find_element_text(self._driver, product_selectors.price)),
            discount_price=self._safe_to_float(
                self._safe_find_element_text(self._driver, product_selectors.discount_price)),

            images=self._get_images(self._driver, product_selectors.images),
            product_code=self._safe_find_element_text(self._driver, product_selectors.product_code),
            reviews_count=self._safe_to_int(self._safe_find_element_text(self._driver, product_selectors.reviews_count)),
            screen_diagonal_inches=self._get_diagonal_inches(
                self._safe_find_element_text(specifications_container, specifications_selectors.screen_diagonal_inches)),
            screen_resolution=self._safe_find_element_text(specifications_container,
                                                           specifications_selectors.screen_resolution),
            specifications=self._get_specifications(self._driver, product_selectors.specifications),
        )
        return self._parsed_data

    def save_data(self):
        if self._parsed_data:
            product, created = Product.objects.get_or_create(**self._parsed_data)
            print(f"Product {product.title} saved")

    def _perform_search(self, search_query: str):
        try:
            search_input = self._driver.find_element(By.XPATH, search_selectors.search_input.root)
            search_input.send_keys(search_query)
            time.sleep(1)
            search_input.send_keys(Keys.ENTER)
        except (NoSuchElementException, AttributeError, EmptyData):
            return None

    # TODO: REFACTOR THIS
    def _get_text(self, element: WebElement):
        # The "product code" is not visible in the first case, but it is visible in the second.
        text_v1 = element.text
        text_v2 = element.get_attribute("textContent")
        if text_v1 and text_v1.strip():  # if not empty after strip
            final_text = text_v1
        elif text_v2 and text_v2.strip():  # if not empty after strip
            final_text = text_v2
        else:
            raise EmptyData
        return re.sub(r"\s+", " ", final_text).strip()

    def _safe_find_element_text(self, element: WebDriver | WebElement,
                                selector: Selector) -> str | None:
        try:
            element = element.find_element(By.XPATH, selector.root)
            return self._get_text(element)
        except (NoSuchElementException, AttributeError, EmptyData):
            return None

    def _get_diagonal_inches(self, text_value: str | None) -> float | None:
        if not text_value:
            return None
        normalized = (text_value.replace('"', "")
                      .replace("''", "")
                      .replace("″", "")
                      .replace("“", "")
                      .replace(",", ".")
                      .strip())
        try:
            return float(normalized)
        except ValueError:
            return None

    def _get_images(self, element: WebDriver, selector: Selector) -> list[str]:
        try:
            img_tags = element.find_elements(By.XPATH, selector.root)
            images = [a.get_attribute("src") for a in img_tags]
            return list(filter(None, images))
        except (NoSuchElementException, AttributeError):
            return []

    def _safe_to_int(self, value: str | None) -> int | None:
        if value is None:
            return None
        try:
            return int(value.replace(" ", ""))
        except ValueError:
            return None

    def _safe_to_float(self, value: str | None) -> float | None:
        if value is None:
            return None
        try:
            return float(value
                         .replace(" ", "")
                         .replace(",", "."))
        except ValueError:
            return None

    def _get_specifications(
            self,
            element: WebDriver | WebElement,
            selector: Selector,
    ) -> dict[str, str]:
        specification_web_elements = element.find_elements(By.XPATH, selector.root)
        specification = dict()
        for spec in specification_web_elements:
            try:
                key, value = self._get_one_specification(spec)
                specification[key] = value
            except EmptyData:
                continue
        return specification

    def _get_one_specification(self, element: WebElement) -> tuple:
        elements = element.find_elements(By.TAG_NAME, "span")
        if len(elements) == 2:  # key and value
            try:
                key = self._get_text(elements[0])
                value = self._get_text(elements[1])
                if key and value:
                    return key, value
            except (NoSuchElementException, AttributeError, EmptyData):
                pass
        # In any other case, we throw an exception.
        raise EmptyData

    def _generate_search_url(self, search_query: str) -> str:
        params = urlencode({"Search": search_query})
        return f"{self._base_search_url}?{params}"


class EmptyData(ValueError):
    pass


def main() -> None:
    driver = webdriver.Firefox()

    try:
        parser = SeleniumParser(driver)
        parser.run("Apple iPhone 15 128GB Black")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
