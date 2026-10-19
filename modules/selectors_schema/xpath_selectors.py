"""
Product page XPath selectors for parsing specific website structure
Extracts: product title, price variants (regular/discount/promo),
images, product code, specification container, and customer reviews count
"""

from .schemas import (
    ProductSelectorsSchema,
    ProductSpecificationsSelectorsSchema,
    SearchSelectorsSchema,
    Selector, ListSelectorsSchema,
)


product_selectors = ProductSelectorsSchema(
    title=Selector("//h1[@class=\"main-title\"]"),
    specifications_container=Selector("//div[@id=\"br-characteristics\"]"),
    specifications=Selector("//div[@id=\"br-characteristics\"]//div[count(span) = 2]"),

    price=Selector("//div[@class=\"price-wrapper\"]/span[not(@class) or @class != \"red-price\"]"),
    discount_price=Selector("//div[@class=\"price-wrapper\"]/span[@class = \"red-price\"]"),
    promo_price=Selector("//div[@data-order-class=\"buy-wrapper\"]//span[@class = \"promo-price\"]"),
    images=Selector("//img[@class=\"br-main-img\"]"),
    product_code=Selector('//div[@id="product_code"]/span[@class="br-pr-code-val"]'),
    reviews_count=Selector("//div[@id=\"reviews\"]//a[@href=\"#reviews-list\"]/span"),
)
specifications_selectors = ProductSpecificationsSelectorsSchema(
    color=Selector("//a[contains(@title, \"Колір\")]"),
    storage_capacity=Selector("//a[contains(@title, \"Вбудована пам\")]"),
    manufacturer=Selector("//a[contains(@title, \"Виробник\")]"),
    screen_diagonal_inches=Selector("//a[contains(@title, \"Діагональ екрану\")]"),
    screen_resolution=Selector("//a[contains(@title, \"Роздільна здатність екрану\")]"),
)
search_selectors = SearchSelectorsSchema(
    search_input = Selector("//input[@class=\"quick-search-input\"]"),
    search_button = Selector("//*[@type=\"submit\" and @class=\"qsr-submit\"]"),
    first_product_url = Selector("//div[@class=\"product-item\"]"),
)
list_selectors = ListSelectorsSchema(
    products = Selector("//div[contains(@class, \"product-wrapper\")]//a"),
)
# search-form
