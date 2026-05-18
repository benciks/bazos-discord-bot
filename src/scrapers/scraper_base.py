from abc import ABC, abstractmethod

from ..part_offer import PartOffer


class ScraperBase(ABC):
    name: str = "Base"
    color: int = 0x001E50  # VW Blue

    @abstractmethod
    def get_latest_offers(self) -> list[PartOffer]:
        pass
