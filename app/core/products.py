from typing import Literal, TypedDict


class Product(TypedDict):
    name: str
    units: int
    url: str


Units = Literal[100]

products = [
    Product(
        name="100 credits",
        units=100,
        url="https://pix-fusion.lemonsqueezy.com/buy/56882feb-98ba-4986-b574-b590b84c5d0a",
    ),
    Product(
        name="500 credits",
        units=500,
        url="https://pix-fusion.lemonsqueezy.com/buy/2f0b1c3e-4d5a-4b6c-8f7e-9a1b2c3d4e5f",
    ),
    Product(
        name="1000 credits",
        units=1000,
        url="https://pix-fusion.lemonsqueezy.com/buy/3a4b5c6d-7e8f-9a1b-2c3d-4e5f6a7b8c9d",
    ),
]


def get_product_by_units(units: int) -> Product:
    """Retrieve a product by its units."""
    return next(product for product in products if product["units"] == units)


def get_product_by_name(name: str) -> Product:
    """Retrieve a product by its name."""
    return next(product for product in products if product["name"] == name)
