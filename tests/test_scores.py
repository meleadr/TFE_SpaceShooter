import json

import pygame
import pytest

from spaceshooter.save import LEGACY_NAME, TOP_SIZE, SaveData
from spaceshooter.scenes import SceneManager
from spaceshooter.scenes.gameover import GameOverScene, NameEntry
from spaceshooter.scenes.scores import ScoresScene
from spaceshooter.scenes.title import TitleScene


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


@pytest.fixture
def save(tmp_path):
    return SaveData(tmp_path / "save.json")


# --- top 10 ------------------------------------------------------------------


def test_scores_are_kept_sorted_and_capped(save):
    for score in (5, 50, 20, 1, 30, 40, 10, 60, 70, 80, 90, 15):
        save.submit_score(score, "ABC")
    scores = [e.score for e in save.scores]
    assert len(scores) == TOP_SIZE
    assert scores == sorted(scores, reverse=True)
    assert 1 not in scores and 5 not in scores


def test_rank_for(save):
    for score in range(10, 110, 10):  # a full table: 10..100
        save.submit_score(score)
    assert save.rank_for(1000) == 1
    assert save.rank_for(55) == 6
    assert save.rank_for(10) is None  # tie with the last one: does not make it
    assert save.rank_for(0) is None


def test_zero_is_never_recorded(save):
    assert save.submit_score(0) is None
    assert save.scores == []


def test_names_and_last_name_round_trip(save):
    rank = save.submit_score(42)
    save.rename(rank, "zoe")
    again = SaveData(save.path)
    assert (again.scores[0].name, again.scores[0].score) == ("ZOE", 42)
    assert again.last_name == "ZOE"


def test_old_best_score_is_migrated(tmp_path):
    path = tmp_path / "save.json"
    path.write_text(json.dumps({"best_score": 77}), encoding="utf-8")
    save = SaveData(path)
    assert save.best_score == 77
    assert save.scores[0].name == LEGACY_NAME


def test_odd_entries_are_ignored(tmp_path):
    path = tmp_path / "save.json"
    path.write_text(json.dumps({"scores": [{"name": "A"}]}), encoding="utf-8")
    assert SaveData(path).scores == []


# --- name entry --------------------------------------------------------------


def test_typing_a_name(display):
    entry = NameEntry("AAA")
    for k in (pygame.K_z, pygame.K_o, pygame.K_e):  # Z is also "up": typing wins
        entry.handle_event(key(k))
    entry.handle_event(key(pygame.K_RETURN))
    assert entry.done and entry.name == "ZOE"


def test_arcade_style_name(display):
    entry = NameEntry("AAA")
    entry.handle_event(key(pygame.K_UP))  # A -> B
    entry.handle_event(key(pygame.K_RETURN))  # next letter
    entry.handle_event(key(pygame.K_DOWN))  # A -> Z (wraps)
    entry.handle_event(key(pygame.K_RIGHT))
    assert not entry.done
    entry.handle_event(key(pygame.K_RETURN))  # last letter: done
    assert entry.done and entry.name == "BZA"


def test_escape_keeps_the_offered_name(display):
    entry = NameEntry("MAX")
    entry.handle_event(key(pygame.K_ESCAPE))
    assert entry.done and entry.name == "MAX"


def test_game_over_asks_for_a_name_then_shows_the_menu(display, save):
    manager = SceneManager()
    rank = save.submit_score(25)
    over = GameOverScene(manager, save, 25, rank)
    manager.push(over)
    over.update(GameOverScene.INPUT_DELAY)
    assert over.entering_name
    for k in (pygame.K_b, pygame.K_o, pygame.K_b, pygame.K_RETURN):
        over.handle_event(key(k))
    assert not over.entering_name
    assert SaveData(save.path).scores[0].name == "BOB"

    over.handle_event(key(pygame.K_DOWN))  # "Meilleurs scores"
    over.handle_event(key(pygame.K_RETURN))
    assert isinstance(manager.top, ScoresScene)
    assert manager.top.highlight == 1
    manager.top.handle_event(key(pygame.K_ESCAPE))
    assert manager.top is over


def test_no_name_entry_outside_the_top_10(display, save):
    over = GameOverScene(SceneManager(), save, 0, None)
    assert not over.entering_name


def test_title_opens_the_scores(display, save):
    manager = SceneManager()
    save.submit_score(12, "ANA")
    manager.push(TitleScene(manager, save))
    manager.handle_event(key(pygame.K_DOWN))
    manager.handle_event(key(pygame.K_RETURN))
    assert isinstance(manager.top, ScoresScene)
    manager.draw(pygame.display.get_surface())
