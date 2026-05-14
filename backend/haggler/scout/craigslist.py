"""Craigslist scout via Apify actor `ivanvs~craigslist-scraper-pay-per-result`."""

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

_ACTOR = "ivanvs~craigslist-scraper-pay-per-result"
_APIFY_RUN_URL = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
_CL_SUBDOMAIN = "sfbay"


def _build_search_url(criteria: SearchCriteria) -> str:
    params = {
        "query": criteria.query,
        "max_price": int(criteria.max_price),
        "search_distance": criteria.radius_miles,
        "postal": criteria.location,
    }
    return f"https://{_CL_SUBDOMAIN}.craigslist.org/search/sss?{urlencode(params)}"

_CONDITION_MAP: dict[str, Condition] = {
    "new": Condition.NEW,
    "like new": Condition.LIKE_NEW,
    "excellent": Condition.LIKE_NEW,
    "good": Condition.GOOD,
    "fair": Condition.FAIR,
    "salvage": Condition.POOR,
}


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


def _parse_item(item: dict[str, Any]) -> Listing | None:
    listing_url = item.get("url") or item.get("link")
    if not listing_url:
        return None

    price = _parse_price(item.get("price"))
    if price is None:
        return None

    external_id = str(item.get("id") or item.get("pid") or listing_url)
    photos: list[str] = item.get("images") or []

    posted_at: datetime | None = None
    if raw_date := item.get("postedAt") or item.get("date"):
        with contextlib.suppress(ValueError, TypeError):
            posted_at = datetime.fromisoformat(raw_date)

    return Listing(
        platform=Platform.CRAIGSLIST,
        external_id=external_id,
        title=item.get("title", ""),
        price=price,
        location=item.get("location") or item.get("area"),
        condition=_map_condition(item.get("condition")),
        description=item.get("postingBody") or item.get("description") or "",
        photo_urls=photos,
        listing_url=listing_url,
        contact_url=item.get("replyUrl"),
        seller_name=item.get("sellerName"),
        posted_at=posted_at,
        raw_data=item,
    )


class CraigslistScout(Scout):
    """Searches Craigslist via the Apify craigslist-scraper actor."""

    platform = Platform.CRAIGSLIST

    async def search(self, criteria: SearchCriteria) -> list[Listing]:
        settings = get_settings()
        if not settings.apify_api_key:
            log.warning("craigslist_scout.skipped", reason="no APIFY_API_KEY configured")
            return []

        actor_input = {
            "urls": [{"url": _build_search_url(criteria)}],
            "maxAge": 15,
            "maxConcurrency": 4,
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
            raise ScoutError(f"Apify Craigslist request failed: {exc}") from exc

        log.info("craigslist_scout.results", raw_count=len(items))
        return [listing for item in items if (listing := _parse_item(item)) is not None]
