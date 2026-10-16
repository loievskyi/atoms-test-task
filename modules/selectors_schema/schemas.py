from pydantic import BaseModel, RootModel


class Selector(RootModel):
    root: str


class ProductSelectorsSchema(BaseModel):
    title: Selector
    specifications_container: Selector
    specifications: Selector

    price: Selector
    discount_price: Selector
    promo_price: Selector
    images: Selector
    product_code: Selector
    reviews_count: Selector


class ProductSpecificationsSelectorsSchema(BaseModel):
    """
    A class for searching for specific specifications.
    The search must be performed on specifications, not on the complete HTML page!
    """
    color: Selector
    storage_capacity: Selector
    manufacturer: Selector
    screen_diagonal_inches: Selector
    screen_resolution: Selector


class SearchSelectorsSchema(BaseModel):
    search_input: Selector
    search_button: Selector
    first_product_url: Selector


class ListSelectorsSchema(BaseModel):
    products: Selector
