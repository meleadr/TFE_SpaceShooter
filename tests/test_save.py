from spaceshooter.save import SaveData


def test_missing_file_starts_at_zero(tmp_path):
    assert SaveData(tmp_path / "nope" / "save.json").best_score == 0


def test_best_score_round_trips_and_creates_folders(tmp_path):
    path = tmp_path / "deep" / "save.json"
    save = SaveData(path)
    assert save.submit_score(42)
    assert SaveData(path).best_score == 42


def test_lower_score_is_not_a_record(tmp_path):
    save = SaveData(tmp_path / "save.json")
    save.submit_score(10)
    assert not save.submit_score(10)
    assert not save.submit_score(3)
    assert save.best_score == 10


def test_corrupt_file_is_ignored(tmp_path):
    path = tmp_path / "save.json"
    for content in ("{not json", "[1, 2]", '{"best_score": "abc"}'):
        path.write_text(content, encoding="utf-8")
        assert SaveData(path).best_score == 0
