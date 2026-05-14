"""Smoke tests for the data model contract.

These tests exist mainly to catch breaking changes to the shared schemas
that would silently corrupt data between scout and negotiator.
"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from haggler.models.schemas import (
    Condition,
    Listing,
    NegotiationAction,
    NegotiatorDecision,
    Platform,
    SearchCriteria,
)


def test_search_criteria_target_defaults_to_70_percent() -> None:
    criteria = SearchCriteria(query="couch", max_price=400, location="94583")
    assert criteria.effective_target() == pytest.approx(280)


def test_search_criteria_respects_explicit_target() -> None:
    criteria = SearchCriteria(
        query="couch", max_price=400, location="94583", target_price=300
    )
    assert criteria.effective_target() == 300


def test_listing_requires_url() -> None:
    with pytest.raises(ValidationError):
        Listing(  # type: ignore[call-arg]
            platform=Platform.CRAIGSLIST,
            external_id="abc123",
            title="Couch",
            price=200,
        )


def test_listing_accepts_minimal_fields() -> None:
    listing = Listing(
        platform=Platform.CRAIGSLIST,
        external_id="abc123",
        title="Black couch",
        price=250,
        listing_url="https://sfbay.craigslist.org/foo",  # type: ignore[arg-type]
    )
    assert listing.condition == Condition.UNKNOWN
    assert listing.photo_urls == []


def test_negotiator_decision_requires_reasoning() -> None:
    with pytest.raises(ValidationError):
        NegotiatorDecision(action=NegotiationAction.WAIT)  # type: ignore[call-arg]


def test_negotiator_decision_minimal() -> None:
    decision = NegotiatorDecision(
        action=NegotiationAction.WAIT,
        reasoning="Seller hasn't replied yet, give them time",
    )
    assert decision.message is None
    assert decision.offer_amount is None
