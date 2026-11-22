"""Persistent player data (best score, key bindings), stored as JSON in the user's data folder."""

import json
import logging
from pathlib import Path

from spaceshooter.controls import Bindings

log = logging.getLogger(__name__)


def default_path() -> Path:
    try:
        from platformdirs import user_data_path
    except ImportError:  # e.g. in the browser build, where the folder does not matter
        return Path.home() / ".spaceshooter" / "save.json"
    # e.g. %APPDATA%\spaceshooter\save.json on Windows
    return user_data_path("spaceshooter", appauthor=False, roaming=True) / "save.json"


class SaveData:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_path()
        self.best_score = 0
        self.bindings = Bindings()
        self.load()

    def load(self) -> None:
        """Read the save file. A missing or corrupt file just means a fresh start."""
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.best_score = max(int(data.get("best_score", 0)), 0)
            self.bindings = Bindings.from_json(data.get("bindings"))
        except FileNotFoundError:
            pass
        except (OSError, ValueError, TypeError, AttributeError) as error:
            log.warning("Ignoring unreadable save file %s: %s", self.path, error)

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            data = {"best_score": self.best_score, "bindings": self.bindings.to_json()}
            self.path.write_text(json.dumps(data), encoding="utf-8")
        except OSError as error:
            log.warning("Could not write save file %s: %s", self.path, error)

    def submit_score(self, score: int) -> bool:
        """Record a finished game's score. Returns whether it is a new best."""
        if score <= self.best_score:
            return False
        self.best_score = score
        self.save()
        return True
