"""Base class for marketplace scouts.

Every platform-specific scout (Craigslist, eBay, Facebook) must subclass
`Scout` and implement `search`. This is the only contract the orchestrator
relies on.
"""

from abc import ABC, abstractmethod

from haggler.models.schemas import Listing, Platform, SearchCriteria


class Scout(ABC):
    """Abstract base class for marketplace search modules."""

    platform: Platform

    @abstractmethod
    async def search(self, criteria: SearchCriteria) -> list[Listing]:
        """Search the marketplace and return normalized listings.

        Args:
            criteria: User's search parameters.

        Returns:
            A list of `Listing` objects matching the criteria.
            May be empty if no listings found.

        Raises:
            ScoutError: When the platform is unreachable or blocks us.
        """
        ...


class ScoutError(Exception):
    """Raised when a scout fails to retrieve listings."""
