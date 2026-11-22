"""Persistent player data (top 10, key bindings), stored as JSON.

On the desktop the file lives in the user's data folder; in the browser the same JSON
goes to localStorage, so scores survive a page reload.
"""

import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

from spaceshooter.controls import Bindings

log = logging.getLogger(__name__)

TOP_SIZE = 10
NAME_LENGTH = 3
DEFAULT_NAME = "AAA"
LEGACY_NAME = "---"  # owner of a best score saved before names existed
STORAGE_KEY = "spaceshooter.save"


@dataclass
class Entry:
    name: str
    score: int


def default_path() -> Path:
    try:
        from platformdirs import user_data_path
    except ImportError:  # e.g. in the browser build, where the folder does not matter
        return Path.home() / ".spaceshooter" / "save.json"
    # e.g. %APPDATA%\spaceshooter\save.json on Windows
    return user_data_path("spaceshooter", appauthor=False, roaming=True) / "save.json"


def web_storage():
    """The browser's localStorage when running under pygbag, else None."""
    if sys.platform != "emscripten":
        return None
    try:
        import platform  # pygbag's platform module exposes the JS window

        return platform.window.localStorage
    except Exception as error:
        log.warning("No localStorage: %s", error)
        return None


def clean_name(name: object) -> str:
    text = "".join(c for c in str(name).upper() if "A" <= c <= "Z")[:NAME_LENGTH]
    return text.ljust(NAME_LENGTH, "A") if text else DEFAULT_NAME


class SaveData:
    def __init__(self, path: Path | None = None) -> None:
        self.storage = web_storage() if path is None else None
        self.path = path or default_path()
        self.scores: list[Entry] = []
        self.last_name = DEFAULT_NAME  # offered first when entering a new score
        self.bindings = Bindings()
        self.load()

    @property
    def best_score(self) -> int:
        return self.scores[0].score if self.scores else 0

    # --- storage -------------------------------------------------------------

    def read_text(self) -> str | None:
        if self.storage is not None:
            return self.storage.getItem(STORAGE_KEY)
        try:
            return self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

    def write_text(self, text: str) -> None:
        if self.storage is not None:
            self.storage.setItem(STORAGE_KEY, text)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(text, encoding="utf-8")

    def load(self) -> None:
        """Read the save. A missing or corrupt save just means a fresh start."""
        try:
            text = self.read_text()
            if text is None:
                return
            data = json.loads(text)
            self.scores = self.parse_scores(data)
            self.last_name = clean_name(data.get("last_name", DEFAULT_NAME))
            self.bindings = Bindings.from_json(data.get("bindings"))
        except (OSError, ValueError, TypeError, AttributeError, KeyError) as error:
            log.warning("Ignoring unreadable save %s: %s", self.path, error)

    @staticmethod
    def parse_scores(data: dict) -> list[Entry]:
        raw = data.get("scores")
        if raw is None:  # save from before the top 10: keep the best score
            best = max(int(data.get("best_score", 0)), 0)
            return [Entry(LEGACY_NAME, best)] if best else []
        entries = [Entry(clean_name(e["name"]), int(e["score"])) for e in raw]
        entries = [e for e in entries if e.score > 0]
        entries.sort(key=lambda e: e.score, reverse=True)
        return entries[:TOP_SIZE]

    def save(self) -> None:
        data = {
            "scores": [{"name": e.name, "score": e.score} for e in self.scores],
            "last_name": self.last_name,
            "bindings": self.bindings.to_json(),
        }
        try:
            self.write_text(json.dumps(data))
        except Exception as error:
            log.warning("Could not write save %s: %s", self.path, error)

    # --- scores --------------------------------------------------------------

    def rank_for(self, score: int) -> int | None:
        """1-based place `score` would take in the top 10, or None if it does not make it.

        Ties go after the existing scores: whoever got there first keeps the place.
        """
        if score <= 0:
            return None
        rank = 1 + sum(1 for e in self.scores if e.score >= score)
        return rank if rank <= TOP_SIZE else None

    def submit_score(self, score: int, name: str | None = None) -> int | None:
        """Record a finished game. Returns its 1-based rank, or None if not in the top 10."""
        rank = self.rank_for(score)
        if rank is None:
            return None
        self.scores.insert(rank - 1, Entry(clean_name(name or self.last_name), score))
        del self.scores[TOP_SIZE:]
        self.save()
        return rank

    def rename(self, rank: int, name: str) -> None:
        """Give the entry at `rank` its player's name (typed after the game)."""
        self.last_name = clean_name(name)
        self.scores[rank - 1].name = self.last_name
        self.save()
