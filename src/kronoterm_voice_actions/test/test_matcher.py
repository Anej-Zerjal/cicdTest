# src/kronoterm_voice_actions/test/test_matcher.py

# Import relative to the package structure
from kronoterm_voice_actions.wyoming import matcher

import pytest


def test_parse_slovene_number_basic():
    assert matcher.slovenian_word_to_number_strict("ena") == 1
    # Add more unit tests for parse_slovene_number
