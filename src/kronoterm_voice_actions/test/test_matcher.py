# src/kronoterm_voice_actions/test/test_matcher.py

# Import relative to the package structure
from kronoterm_voice_actions.wyoming import matcher

import pytest


def test_parse_slovene_number_basic():
    assert matcher.parse_slovene_number("ena") == 1
    assert matcher.parse_slovene_number("dvajset in tri") == 23
    # Add more unit tests for parse_slovene_number
