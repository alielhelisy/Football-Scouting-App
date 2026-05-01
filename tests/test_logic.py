import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from models import (
    validate_player_name,
    validate_team,
    validate_position,
    validate_stars,
    validate_non_negative_int,
    validate_cards,
    compute_average_stars,
    filter_players_by_position,
    stars_display,
)


# ── validate_player_name ──────────────────────────────────────────────────────

def test_valid_player_name():
    assert validate_player_name("  Ronaldo  ") == "Ronaldo"

def test_player_name_empty_raises():
    with pytest.raises(ValueError):
        validate_player_name("")

def test_player_name_whitespace_only_raises():
    with pytest.raises(ValueError):
        validate_player_name("   ")

def test_player_name_too_long_raises():
    with pytest.raises(ValueError):
        validate_player_name("A" * 101)


# ── validate_team ─────────────────────────────────────────────────────────────

def test_team_strips_whitespace():
    assert validate_team("  Al Ahly  ") == "Al Ahly"

def test_team_empty_returns_empty():
    assert validate_team("") == ""

def test_team_none_returns_empty():
    assert validate_team(None) == ""


# ── validate_position ─────────────────────────────────────────────────────────

def test_valid_positions():
    for pos in ["CB", "FB", "6ER", "8ER", "WIDE", "CF"]:
        assert validate_position(pos) == pos

def test_position_lowercase_accepted():
    assert validate_position("cb") == "CB"
    assert validate_position("cf") == "CF"

def test_invalid_position_raises():
    with pytest.raises(ValueError):
        validate_position("STRIKER")

def test_empty_position_allowed():
    assert validate_position("") == ""


# ── validate_stars ────────────────────────────────────────────────────────────

def test_valid_stars():
    for s in [1, 2, 3, 4, 5]:
        assert validate_stars(s) == s

def test_stars_zero_raises():
    with pytest.raises(ValueError):
        validate_stars(0)

def test_stars_six_raises():
    with pytest.raises(ValueError):
        validate_stars(6)

def test_stars_string_number():
    assert validate_stars("4") == 4

def test_stars_non_numeric_raises():
    with pytest.raises(ValueError):
        validate_stars("great")


# ── validate_non_negative_int ─────────────────────────────────────────────────

def test_minutes_valid():
    assert validate_non_negative_int(90, "Minutes Played") == 90

def test_minutes_zero_valid():
    assert validate_non_negative_int(0, "Minutes Played") == 0

def test_minutes_negative_raises():
    with pytest.raises(ValueError):
        validate_non_negative_int(-1, "Minutes Played")

def test_minutes_string_number():
    assert validate_non_negative_int("45", "Minutes Played") == 45

def test_minutes_non_numeric_raises():
    with pytest.raises(ValueError):
        validate_non_negative_int("lots", "Minutes Played")


# ── validate_cards ────────────────────────────────────────────────────────────

def test_cards_none_valid():
    assert validate_cards("None") == "None"

def test_cards_yellow_valid():
    assert validate_cards("Yellow") == "Yellow"

def test_cards_red_valid():
    assert validate_cards("Red") == "Red"

def test_cards_invalid_raises():
    with pytest.raises(ValueError):
        validate_cards("Blue")


# ── compute_average_stars ─────────────────────────────────────────────────────

def test_average_single_report():
    assert compute_average_stars([{"rating": 4}]) == 4.0

def test_average_multiple_reports():
    reports = [{"rating": 3}, {"rating": 5}, {"rating": 4}]
    assert compute_average_stars(reports) == 4.0

def test_average_empty_reports():
    assert compute_average_stars([]) == 0.0

def test_average_rounds_to_one_decimal():
    assert compute_average_stars([{"rating": 1}, {"rating": 2}]) == 1.5


# ── filter_players_by_position ────────────────────────────────────────────────

def _make_players():
    return [
        {"id": 1, "name": "Ali",   "position": "CB"},
        {"id": 2, "name": "Omar",  "position": "FB"},
        {"id": 3, "name": "Karim", "position": "6ER"},
        {"id": 4, "name": "Samir", "position": "CF"},
        {"id": 5, "name": "Tarek", "position": "CB"},
    ]

def test_filter_by_position_returns_correct():
    result = filter_players_by_position(_make_players(), "CB")
    assert len(result) == 2
    assert all(p["position"] == "CB" for p in result)

def test_filter_empty_position_returns_all():
    assert len(filter_players_by_position(_make_players(), "")) == 5

def test_filter_no_match_returns_empty():
    assert len(filter_players_by_position(_make_players(), "WIDE")) == 0

def test_filter_case_insensitive():
    assert len(filter_players_by_position(_make_players(), "cf")) == 1


# ── stars_display ─────────────────────────────────────────────────────────────

def test_stars_display_full():
    assert stars_display(5.0) == "★★★★★"

def test_stars_display_empty():
    assert stars_display(0.0) == "☆☆☆☆☆"

def test_stars_display_partial():
    assert stars_display(3.0) == "★★★☆☆"

def test_stars_display_rounds():
    assert stars_display(3.6) == "★★★★☆"
