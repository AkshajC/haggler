"""Facebook Marketplace scout via Apify actor `apify/facebook-marketplace-scraper`."""

import contextlib
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

import httpx
import structlog

from haggler.config import get_settings
from haggler.models.schemas import Condition, Listing, Platform, SearchCriteria
from haggler.scout.base import Scout, ScoutError

log = structlog.get_logger()

_ACTOR = "apify~facebook-marketplace-scraper"
_APIFY_RUN_URL = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
_FB_SEARCH_BASE = "https://www.facebook.com/marketplace/search/"

_CONDITION_MAP: dict[str, Condition] = {
    "new": Condition.NEW,
    "new with tags": Condition.NEW,
    "new without tags": Condition.LIKE_NEW,
    "like new": Condition.LIKE_NEW,
    "good": Condition.GOOD,
    "fair": Condition.FAIR,
    "poor": Condition.POOR,
}


def _build_search_url(criteria: SearchCriteria) -> str:
    params: dict[str, str | int] = {
        "query": criteria.query,
        "maxPrice": int(criteria.max_price),
        "exact": "false",
    }
    return f"{_FB_SEARCH_BASE}?{urlencode(params)}"


def _parse_price(raw: Any) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    cleaned = re.sub(r"[^\d.]", "", str(raw))
    return float(cleaned) if cleaned else None


def _map_condition(raw: str | None) -> Condition:
    if not raw:
        return Condition.UNKNOWN
    return _CONDITION_MAP.get(raw.lower().strip(), Condition.UNKNOWN)


def _extract_photos(item: dict[str, Any]) -> list[str]:
    raw: list[Any] = item.get("images") or item.get("photos") or []
    photos = [p if isinstance(p, str) else p.get("url", "") for p in raw]
    return [p for p in photos if p]


def _extract_location(item: dict[str, Any]) -> str | None:
    raw = item.get("location") or item.get("locationText")
    if isinstance(raw, dict):
        return raw.get("city") or raw.get("text")
    return raw


def _parse_item(item: dict[str, Any]) -> Listing | None:
    listing_url = item.get("url") or item.get("link")
    if not listing_url:
        return None

    price = _parse_price(item.get("price") or item.get("priceAmount"))
    if price is None:
        return None

    external_id = str(item.get("id") or listing_url)

    seller: dict[str, Any] = item.get("seller") or {}
    seller_name = item.get("sellerName") or (seller.get("name") if seller else None)

    posted_at: datetime | None = None
    if raw_date := item.get("postedAt") or item.get("listingDate"):
        with contextlib.suppress(ValueError, TypeError):
            posted_at = datetime.fromisoformat(raw_date)

    return Listing(
        platform=Platform.FACEBOOK,
        external_id=external_id,
        title=item.get("title", ""),
        price=price,
        location=_extract_location(item),
        condition=_map_condition(item.get("condition")),
        description=item.get("description") or "",
        photo_urls=_extract_photos(item),
        listing_url=listing_url,
        contact_url=item.get("contactUrl"),
        seller_name=seller_name,
        seller_rating=item.get("sellerRating"),
        posted_at=posted_at,
        raw_data=item,
    )


class FacebookScout(Scout):
    """Searches Facebook Marketplace via the Apify facebook-marketplace-scraper actor."""

    platform = Platform.FACEBOOK

    async def search(self, criteria: SearchCriteria) -> list[Listing]:
        settings = get_settings()
        if not settings.apify_api_key:
            log.warning("facebook_scout.skipped", reason="no APIFY_API_KEY configured")
            return []

        actor_input = {
            "startUrls": [{"url": _build_search_url(criteria)}],
            "maxItems": 25,
            "location": criteria.location,
            "radius": criteria.radius_miles,
        }

        url = _APIFY_RUN_URL.format(actor=_ACTOR)
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    url,
                    params={"token": settings.apify_api_key},
                    json=actor_input,
                )
                resp.raise_for_status()
                items: list[dict[str, Any]] = resp.json()
        except httpx.HTTPError as exc:
            raise ScoutError(f"Apify Facebook request failed: {exc}") from exc

        log.info("facebook_scout.results", raw_count=len(items))
        return [listing for item in items if (listing := _parse_item(item)) is not None]
