from dataclasses import dataclass


@dataclass
class PartOffer:
    link: str
    title: str
    description: str
    price: str
    location: str
    image_url: str
    date_posted: str
    search_query: str

    def __hash__(self):
        return hash(self.link)

    def __eq__(self, other):
        if isinstance(other, PartOffer):
            return self.link == other.link
        return False
