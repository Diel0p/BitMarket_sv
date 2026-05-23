"""
Product domain models and schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
import re
from pydantic import BaseModel, Field, field_validator


_UNSAFE_TEXT_RE = re.compile(r"[<>]")
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
_ALLOWED_CATEGORIES = {
    "Electronics",
    "Books",
    "Art & Collectibles",
    "Gaming",
    "Home & Garden",
    "Other",
}


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    REJECTED = "rejected"


# ── Request schemas ────────────────────────────────────────

class ProductCreateRequest(BaseModel):
    # Validation limits keep listings consistent and prevent oversized payloads.
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    price_sats: int = Field(..., gt=0, description="Price in satoshis")
    category: str = Field(..., min_length=2, max_length=60)
    stock: int = Field(..., ge=0)
    tags: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)

    @field_validator("title", "description", "category", mode="before")
    @classmethod
    def _sanitize_text_fields(cls, value: str):
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError("Field cannot be empty")
        if _CONTROL_CHARS_RE.search(cleaned):
            raise ValueError("Text contains invalid control characters")
        if _UNSAFE_TEXT_RE.search(cleaned):
            raise ValueError("Text contains unsupported characters")
        return cleaned

    @field_validator("category")
    @classmethod
    def _validate_category(cls, value: str):
        if value not in _ALLOWED_CATEGORIES:
            raise ValueError("Invalid category")
        return value

    @field_validator("tags", mode="before")
    @classmethod
    def _normalize_tags(cls, value):
        tags = value or []
        if not isinstance(tags, list):
            raise ValueError("Tags must be a list")

        normalized = []
        seen = set()
        for tag in tags:
            cleaned = str(tag).strip().lower()
            if not cleaned:
                continue
            if _CONTROL_CHARS_RE.search(cleaned) or _UNSAFE_TEXT_RE.search(cleaned):
                raise ValueError("Tag contains unsupported characters")
            if len(cleaned) > 30:
                raise ValueError("Tag is too long")
            if cleaned in seen:
                continue
            seen.add(cleaned)
            normalized.append(cleaned)

        if len(normalized) > 15:
            raise ValueError("Maximum 15 tags allowed")
        return normalized

    @field_validator("images", mode="before")
    @classmethod
    def _validate_images(cls, value):
        images = value or []
        if not isinstance(images, list):
            raise ValueError("Images must be a list")
        if len(images) > 5:
            raise ValueError("Maximum 5 images allowed")
        for image in images:
            image_url = str(image).strip()
            if not image_url:
                raise ValueError("Image URL cannot be empty")
            if len(image_url) > 255:
                raise ValueError("Image URL is too long")
            if not (image_url.startswith("/static/uploads/products/") or image_url.startswith("http://") or image_url.startswith("https://")):
                raise ValueError("Invalid image URL")
        return images


class ProductUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    price_sats: Optional[int] = Field(None, gt=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    tags: Optional[list[str]] = None
    images: Optional[list[str]] = None
    status: Optional[ProductStatus] = None

    @field_validator("title", "description", "category", mode="before")
    @classmethod
    def _sanitize_optional_text_fields(cls, value: str | None):
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned:
            return None
        if _CONTROL_CHARS_RE.search(cleaned):
            raise ValueError("Text contains invalid control characters")
        if _UNSAFE_TEXT_RE.search(cleaned):
            raise ValueError("Text contains unsupported characters")
        return cleaned

    @field_validator("category")
    @classmethod
    def _validate_optional_category(cls, value: str | None):
        if value is None:
            return None
        if value not in _ALLOWED_CATEGORIES:
            raise ValueError("Invalid category")
        return value

    @field_validator("tags", mode="before")
    @classmethod
    def _normalize_optional_tags(cls, value):
        if value is None:
            return None
        return ProductCreateRequest._normalize_tags(value)

    @field_validator("images", mode="before")
    @classmethod
    def _validate_optional_images(cls, value):
        if value is None:
            return None
        return ProductCreateRequest._validate_images(value)


# ── Response schemas ───────────────────────────────────────

class ProductResponse(BaseModel):
    id: str
    title: str
    description: str
    price_sats: int
    price_btc: float
    category: str
    stock: int
    tags: list[str]
    status: ProductStatus
    seller_id: str
    seller_name: Optional[str] = None
    images: list[str] = []
    created_at: datetime

    # Enables direct serialization from DB documents without manual mapping.
    model_config = {"from_attributes": True}


# ── Filters ────────────────────────────────────────────────

class ProductFilters(BaseModel):
    # Hard limits on pagination and sort prevent abusive or unsupported queries.
    q: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[int] = Field(None, ge=0)
    max_price: Optional[int] = Field(None, ge=0)
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort: str = Field("created_at", pattern="^(created_at|price_asc|price_desc)$")

    @field_validator("q", mode="before")
    @classmethod
    def _normalize_query(cls, value: str | None):
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned:
            return None
        if len(cleaned) > 120:
            raise ValueError("Search query is too long")
        if _CONTROL_CHARS_RE.search(cleaned):
            raise ValueError("Search query contains invalid characters")
        return cleaned
