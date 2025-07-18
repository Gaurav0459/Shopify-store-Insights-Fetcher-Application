from typing import List, Dict, Optional, Any
from pydantic import BaseModel, HttpUrl, Field


class Product(BaseModel):
    id: str
    title: str
    handle: str
    description: Optional[str] = None
    price: Optional[str] = None
    compare_at_price: Optional[str] = None
    available: Optional[bool] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    variants: Optional[List[Dict[str, Any]]] = None
    url: Optional[str] = None


class SocialHandle(BaseModel):
    platform: str
    url: str


class ContactInfo(BaseModel):
    emails: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    address: Optional[str] = None


class ImportantLink(BaseModel):
    name: str
    url: str


class FAQ(BaseModel):
    question: str
    answer: str


class ShopifyInsights(BaseModel):
    store_url: str
    store_name: str
    products: List[Product] = Field(default_factory=list)
    hero_products: List[Product] = Field(default_factory=list)
    privacy_policy: Optional[str] = None
    return_refund_policy: Optional[str] = None
    faqs: List[FAQ] = Field(default_factory=list)
    social_handles: List[SocialHandle] = Field(default_factory=list)
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    about_brand: Optional[str] = None
    important_links: List[ImportantLink] = Field(default_factory=list)


class InsightRequest(BaseModel):
    website_url: HttpUrl


class ErrorResponse(BaseModel):
    detail: str