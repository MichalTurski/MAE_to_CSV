import pytest
from unittest import mock

from Cogito.aim_category import lex_api
from Cogito.aim_category.lex_api import NONE_CATEGORY_KEY
from tests.mocked_api import get_mocked_response

TOOLS = [lex_api.MORFEUSZ]#, lex_api.PLWORDNET]
@pytest.mark.parametrize("tool", TOOLS)
def test_create_api_post_request(tool):
    resp = lex_api.create_api_post_request(lex_api.BASE_URL,
                                           payload={"task": lex_api.ALL, "tool": tool, "lexeme": "jestem"})
    assert resp


AIM_TO_STANDARDIZE = [
    ("nie podoba się", "podobać się"),
    ("robi się", "robić się"),
    ("nie pracuje", "pracować"),
    ("dmucha", "dmuchać"),
    ("regulamin organizacyjny", None),
    ("ma", "mieć"),
    ("uda", "udać"),
    ("nie uda się", "udać się")
]
@pytest.mark.parametrize("aim_input, aim_output", AIM_TO_STANDARDIZE)
def test_get_verb_infinitive_form(aim_input, aim_output):
    standardized_aim = lex_api.get_verb_infinitive_form(aim_input)
    assert standardized_aim == aim_output


@mock.patch('Cogito.aim_category.lex_api.create_api_post_request', return_value=get_mocked_response("wybierać się"))
def test_get_aim_infinitive_id(mocked_request):
    synset_id = lex_api.get_aim_infinitive_id("wybierać się")
    assert synset_id == 67547


@mock.patch('Cogito.aim_category.lex_api.create_api_post_request', return_value=get_mocked_response("uważać się"))
def test_get_aim_infinitive_id2(mocked_request):
    expected = NONE_CATEGORY_KEY
    synset_id = lex_api.get_aim_infinitive_id("uważać się")
    assert expected == synset_id


@mock.patch('Cogito.aim_category.lex_api.create_api_post_request', return_value=get_mocked_response(""))
def test_get_ancestors(mocked_request):
    pass


HYPONIMS =[
    ([[56063, "{udawać_się.1(36:ruch), [+ 1 unit(s)]}"]], (56063, "udawać_się"))
]
@pytest.mark.parametrize("hyponim, output", HYPONIMS)
def test_get_best_hiponim(hyponim, output):
    ret_output = lex_api.get_best_hiponim(hyponim)
    assert ret_output == output


def test_get_domain_synset():
    relevant_sysnet = get_mocked_response("wybierać się")[lex_api.RESULTS][lex_api.SYNSETS][1]
    domain_synset = lex_api.get_domain_synset(get_mocked_response("wybierać się"))
    assert relevant_sysnet == domain_synset


# infinitive not in wordnet
def test_get_domain_synset2():
    expected = {}
    response = lex_api.get_domain_synset(get_mocked_response("uważać się"))
    assert expected == response


def test_get_related_synsets():
    expected = None
    response = lex_api.get_related_synsets(get_mocked_response("uważać się"))
    assert expected == response
