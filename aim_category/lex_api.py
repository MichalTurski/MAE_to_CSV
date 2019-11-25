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


class ApiError(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f"ApiError: status={self.status}"


# TODO: think about 'się', ':v1'
# TODO: domain id = 39
# TODO: more synsets than one. (sorting by domains)

# TODO: get only ID of synset (possibly from higher api than only wordnet itself)
# TODO: allow user add predefined aim_categories by file

def create_api_post_request(BASE_URL, json):
    resp = requests.post(BASE_URL, json=json)
    if resp.status_code != 200:
        raise ApiError(resp.status_code)
    return resp


def get_verb_standard_form(aim):
    # to omit 'się' TODO: merge with '_'
    aim = aim.split()[0]
    resp = create_api_post_request(BASE_URL, json={"task": ALL, "tool": MORFEUSZ, "lexeme": aim})
    return resp.json()[RESULTS][ANALYSE][0][1]


# TODO: dziewczyno 'ma'!
def get_aim_id(aim):
    # to omit versioning 'kierować:v1'
    aim = aim.split(':')[0]
    resp = create_api_post_request(BASE_URL, json={"task": ALL, "tool": PLWORDNET, "lexeme": aim})
    return resp.json()[RESULTS][SYNSETS][0]['id']


# TODO: refactor
def get_all_hiponimia(aim):
    ancestors = hiponimia = []
    while hiponimia or not ancestors:
        resp = create_api_post_request(BASE_URL, json={"task": ALL, "tool": PLWORDNET, "lexeme": aim})
        try:
            related = resp.json()[RESULTS][SYNSETS][0][RELATED]
        except IndexError:
            break
        hiponimia = [] if HIPONIMIA not in related else related[HIPONIMIA]
        if hiponimia:
            hiponim_id, hiponim_name = hiponimia[0][VERB_ID_INDEX], get_simple_verb_form(hiponimia[0][VERB_NAME_INDEX])
            if (hiponim_id, hiponim_name) not in ancestors:
                aim = hiponim_name
                ancestors.append((hiponim_id, aim))
            else:
                break
    return ancestors


def add_ancestor():
    pass
