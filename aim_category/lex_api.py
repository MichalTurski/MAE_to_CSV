import requests

from aim_category.utils import get_simple_verb_form

BASE_URL = 'http://ws.clarin-pl.eu/lexrest/lex'

MORFEUSZ = 'morfeusz'
PLWORDNET = 'plwordnet'
ALL = 'all'

RESULTS = 'results'
SYNSETS = 'synsets'
HIPONIMIA = 'hiponimia'
HIPERONIMIA = 'hiperonimia'
RELATED = 'related'
ANALYSE = 'analyse'

VERB_ID_INDEX = 0
VERB_NAME_INDEX = 1

MORFEUSZ_VERB_FLAG = 'fin'


class ApiError(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f"ApiError: status={self.status}"


# TODO: think about 'się', ':v1'
# TODO: more synsets than one. (sorting by domains)
# TODO: get only ID of synset (possibly from higher api than only wordnet itself)


def create_api_post_request(BASE_URL, json):
    resp = requests.post(BASE_URL, json=json)
    if resp.status_code != 200:
        raise ApiError(resp.status_code)
    return resp


def get_verb_standard_form(aim):
    standardized_aim = None

    found_sie = 0
    found_nie = 0
    aim_splitted = aim.split()
    aim_to_process = aim_splitted[0]

    if aim_splitted[0] == "nie":
        found_nie = 1
        aim_to_process = aim_splitted[1]
    if aim.find("się") > -1:
        found_sie = 1

    resp = create_api_post_request(BASE_URL, json={"task": ALL, "tool": MORFEUSZ, "lexeme": aim_to_process})
    list_of_words = resp.json()[RESULTS][ANALYSE]
    for word_array in list_of_words:
        flags = word_array[2].split(":")
        if MORFEUSZ_VERB_FLAG in flags:
            standardized_aim = word_array[1].split(":")[0]

    if found_nie:
        standardized_aim = "nie " + standardized_aim
    if found_sie:
        standardized_aim = standardized_aim + " się"

    return standardized_aim


def get_aim_id(aim):
    # to omit versioning 'kierować:v1'
    aim = aim.split(':')[0]
    resp = create_api_post_request(BASE_URL, json={"task": ALL, "tool": PLWORDNET, "lexeme": aim})
    return resp.json()[RESULTS][SYNSETS][0]['id']


def best_ancestor_not_found(hiponimia, ancestors):
    return hiponimia or not ancestors


def get_ancestors(aim):
    ancestors = hiponimia = []
    while best_ancestor_not_found(hiponimia, ancestors):
        resp = create_api_post_request(BASE_URL, json={"task": ALL, "tool": PLWORDNET, "lexeme": aim})
        related = get_related_synsets(resp)
        if related:
            hiponimia = [] if HIPONIMIA not in related else related[HIPONIMIA]
            next_ancestor = add_ancestor(ancestors, hiponimia)
            if next_ancestor:
                ancestors.append(next_ancestor)
            else:
                break
        else:
            break
    return ancestors


def add_ancestor(ancestors, hiponimia):
    if hiponimia:
        hiponim = get_best_hiponim(hiponimia)
        if hiponim in ancestors:
            return None
        else:
            return hiponim


# TODO: best domain id = 39 - proper order
# TODO: also - allow user add predefined aim_categories by file
def get_best_hiponim(hiponimia):
    return hiponimia[0][VERB_ID_INDEX], get_simple_verb_form(hiponimia[0][VERB_NAME_INDEX])


def get_related_synsets(resp):
    try:
        return resp.json()[RESULTS][SYNSETS][0][RELATED]
    except IndexError:
        return None
