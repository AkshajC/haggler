"""Core data models shared across all layers.

These Pydantic models are the contract between scout, negotiator, messaging,
and orchestrator. Never pass raw dicts between layers — always go through
one of these types.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Platform(str, Enum):
    """Marketplace platforms we support."""

    CRAIGSLIST = "craigslist"
    EBAY = "ebay"
    FACEBOOK = "facebook"


class Condition(str, Enum):
    """Item condition, normalized across platforms."""

    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"


class NegotiationState(str, Enum):
    """State machine values for a single conversation."""

    PENDING = "pending"           # not yet contacted
    OPENING = "opening"           # initial message sent, waiting on reply
    PROBING = "probing"           # asking clarifying questions
    OFFERING = "offering"         # made an offer, waiting on response
    COUNTERING = "countering"     # received counter, deciding
    CLOSED_WON = "closed_won"     # deal accepted
    CLOSED_LOST = "closed_lost"   # seller rejected / ghosted
    WALKED_AWAY = "walked_away"   # we decided to stop


class NegotiationAction(str, Enum):
    """Decisions the negotiator can make at each turn."""

    SEND_OPENING = "send_opening"
    ASK_QUESTION = "ask_question"
    MAKE_OFFER = "make_offer"
    COUNTER = "counter"
    ACCEPT = "accept"
    WALK_AWAY = "walk_away"
    WAIT = "wait"


class SearchCriteria(BaseModel):
    """What the user is looking for."""

    query: str = Field(..., description="Natural language item description")
    max_price: float = Field(..., gt=0)
    location: str = Field(..., description="City or zip code")
    radius_miles: int = Field(default=25, gt=0, le=500)
    min_condition: Condition = Condition.FAIR
    target_price: float | None = Field(
        default=None,
        description="Price we'd be thrilled with; defaults to 70% of max_price",
    )

    def effective_target(self) -> float:
        return self.target_price if self.target_price else self.max_price * 0.7


class Listing(BaseModel):
    """A single marketplace listing, normalized across platforms."""

    model_config = ConfigDict(use_enum_values=False)

    platform: Platform
    external_id: str = Field(..., description="Platform's listing ID")
    title: str
    price: float = Field(..., ge=0)
    currency: str = "USD"
    location: str | None = None
    distance_miles: float | None = None
    condition: Condition = Condition.UNKNOWN
    description: str = ""
    photo_urls: list[HttpUrl] = Field(default_factory=list)
    listing_url: HttpUrl
    contact_url: HttpUrl | None = None
    seller_name: str | None = None
    seller_rating: float | None = None
    posted_at: datetime | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)


class RankedListing(BaseModel):
    """A listing with its computed score, ready for negotiation."""

    listing: Listing
    score: float = Field(..., ge=0, le=1)
    rank: int


class Message(BaseModel):
    """A single message in a conversation."""

    sender: str = Field(..., description="'agent' or 'seller'")
    body: str
    sent_at: datetime


class Conversation(BaseModel):
    """The full negotiation thread with one seller."""

    listing: Listing
    state: NegotiationState
    current_offer: float | None = None
    seller_last_price: float | None = None
    messages: list[Message] = Field(default_factory=list)
    started_at: datetime
    updated_at: datetime
    final_price: float | None = None


class NegotiatorDecision(BaseModel):
    """Structured output from the LLM negotiator for one turn."""

    action: NegotiationAction
    message: str | None = Field(
        default=None,
        description="Message to send to seller (required for SEND_*, ASK_*, COUNTER)",
    )
    offer_amount: float | None = Field(
        default=None,
        description="Dollar amount being offered (required for MAKE_OFFER, COUNTER, ACCEPT)",
    )
    reasoning: str = Field(..., description="Why we chose this action — for debugging")


class SearchJob(BaseModel):
    """A user's complete search job."""

    id: str
    criteria: SearchCriteria
    listings: list[RankedListing] = Field(default_factory=list)
    conversations: list[Conversation] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    status: str = "running"
