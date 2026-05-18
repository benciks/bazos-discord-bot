import hashlib
import re
from pathlib import Path

from .part_offer import PartOffer


class OffersStorage:
    def __init__(self, file_path: Path):
        self._file_path = file_path
        self._content_hashes_file = file_path.parent / "content_hashes.txt"
        self._links: set[str] = set()
        self._content_hashes: set[str] = set()
        self._load()

    def _load(self):
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        if self._file_path.exists():
            with open(self._file_path, "r", encoding="utf-8") as f:
                self._links = {line.strip() for line in f if line.strip()}
        else:
            self._file_path.touch()

        if self._content_hashes_file.exists():
            with open(self._content_hashes_file, "r", encoding="utf-8") as f:
                self._content_hashes = {line.strip() for line in f if line.strip()}
        else:
            self._content_hashes_file.touch()

    def _normalize_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s]", "", text)
        return text.strip()

    def _compute_content_hash(self, offer: PartOffer) -> str:
        normalized_title = self._normalize_text(offer.title)
        normalized_desc = self._normalize_text(offer.description)
        content = f"{normalized_title}|{normalized_desc}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def contains(self, offer: PartOffer) -> bool:
        if offer.link in self._links:
            return True
        content_hash = self._compute_content_hash(offer)
        return content_hash in self._content_hashes

    def save(self, offers: list[PartOffer]):
        if not offers:
            return

        new_links = []
        new_hashes = []

        for o in offers:
            if o.link not in self._links:
                new_links.append(o.link)
                self._links.add(o.link)

            content_hash = self._compute_content_hash(o)
            if content_hash not in self._content_hashes:
                new_hashes.append(content_hash)
                self._content_hashes.add(content_hash)

        if new_links:
            with open(self._file_path, "a", encoding="utf-8") as f:
                for link in new_links:
                    f.write(f"{link}\n")

        if new_hashes:
            with open(self._content_hashes_file, "a", encoding="utf-8") as f:
                for h in new_hashes:
                    f.write(f"{h}\n")

    def count(self) -> int:
        return len(self._links)
