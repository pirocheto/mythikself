from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class MessageResponse(BaseModel):
    """Schema for a generic message response."""

    message: str


class Urls(BaseModel):
    receipt: HttpUrl


class FirstOrderItem(BaseModel):
    id: int
    price: int
    order_id: int
    price_id: int
    quantity: int
    test_mode: bool
    created_at: datetime
    product_id: int
    updated_at: datetime
    variant_id: int
    product_name: str
    variant_name: str


class Attributes(BaseModel):
    tax: int
    urls: Urls
    total: int
    status: str
    tax_usd: int
    currency: str
    refunded: bool
    store_id: int
    subtotal: int
    tax_name: str
    tax_rate: float
    setup_fee: int
    test_mode: bool
    total_usd: int
    user_name: str
    created_at: datetime
    identifier: str
    updated_at: datetime
    user_email: str
    customer_id: int
    refunded_at: datetime | None = None
    order_number: int
    subtotal_usd: int
    currency_rate: str
    setup_fee_usd: int
    tax_formatted: str
    tax_inclusive: bool
    discount_total: int
    refunded_amount: int
    total_formatted: str
    first_order_item: FirstOrderItem
    status_formatted: str
    discount_total_usd: int
    subtotal_formatted: str
    refunded_amount_usd: int
    setup_fee_formatted: str
    discount_total_formatted: str
    refunded_amount_formatted: str


class RelationshipLinks(BaseModel):
    self: HttpUrl
    related: HttpUrl


class RelationshipItem(BaseModel):
    links: RelationshipLinks


class Relationships(BaseModel):
    store: RelationshipItem
    customer: RelationshipItem
    order_items: RelationshipItem = Field(..., alias="order-items")
    license_keys: RelationshipItem = Field(..., alias="license-keys")
    subscriptions: RelationshipItem
    discount_redemptions: RelationshipItem = Field(..., alias="discount-redemptions")


class Links(BaseModel):
    self: HttpUrl


class OrderData(BaseModel):
    id: str
    type: str
    links: Links
    attributes: Attributes
    relationships: Relationships


class Meta(BaseModel):
    test_mode: bool
    event_name: str
    webhook_id: str


class OrderResponse(BaseModel):
    data: OrderData
    meta: Meta
