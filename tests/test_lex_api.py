from unittest import TestCase

import pytest
from .context import lex_api

AIM_TO_STANDARDIZE = [
    ("nie podoba się", "nie podobać się"),
    ("robi się", "robić się"),
    ("nie pracuje", "nie pracować"),
    ("dmucha", "dmuchać"),
    ("regulamin organizacyjny", None),
    ("ma", "mieć"),
    ("uda", "udać"),
    ("nie uda się", "nie udać się")
]


@pytest.mark.parametrize("aim_input, aim_output", AIM_TO_STANDARDIZE)
def test_get_verb_standard_form(aim_input, aim_output):
    standardized_aim = lex_api.get_verb_standard_form(aim_input)
    assert standardized_aim == aim_output


def test_get_aim_id():
    pass


def test_get_best_hiponim():
    pass

