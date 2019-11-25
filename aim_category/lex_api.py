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


# TODO: think about 'się', ':v1'
# TODO: domain id = 39
# TODO: more synsets than one. (sorting by domains)

# TODO: get only ID of synset (possibly from higher api than only wordnet itself)
# TODO: allow user add predefined aim_categories by file

def get_verb_standard_form(aim):
    # to omit 'się'
    aim = aim.split()[0]

    resp = requests.post(BASE_URL, json={"task": ALL, "tool": MORFEUSZ, "lexeme": aim})
    if resp.status_code != 200:
        raise ApiError(resp.status_code)

    return resp.json()[RESULTS][ANALYSE][0][1]


def get_aim_id(aim):
    # to omit versioning 'kierować:v1'
    aim = aim.split(':')[0]
    resp = requests.post(BASE_URL, json={"task": ALL, "tool": PLWORDNET, "lexeme": aim})
    if resp.status_code != 200:
        raise ApiError(resp.status_code)
    return resp.json()[RESULTS][SYNSETS][0]['id']


def get_homonimia_and_hiperonimia(aim):
    # to omit versioning 'kierować:v1'
    aim = aim.split(':')[0]

    resp = requests.post(BASE_URL, json={"task": ALL, "tool": PLWORDNET, "lexeme": aim})
    if resp.status_code != 200:
        raise ApiError(resp.status_code)
    # print(resp.json())
    related = resp.json()[RESULTS][SYNSETS][0][RELATED]
    hiponimia = [] if HIPONIMIA not in related else related[HIPONIMIA]
    hiperonimia = [] if HIPERONIMIA not in related else related[HIPERONIMIA]
    return resp.json()[RESULTS][SYNSETS][0]['id'], hiponimia, hiperonimia


def get_all_hiponimia(aim):
    res = []
    hiponimia = [1]
    while hiponimia:
        resp = requests.post(BASE_URL, json={"task": ALL, "tool": PLWORDNET, "lexeme": aim})
        if resp.status_code != 200:
            raise ApiError(resp.status_code)
        try:
            related = resp.json()[RESULTS][SYNSETS][0][RELATED]
        except:
            break
        hiponimia = [] if HIPONIMIA not in related else related[HIPONIMIA]
        if hiponimia:
            if (related[HIPONIMIA][0][0], get_simple_verb_form(related[HIPONIMIA][0][1])) not in res:
                aim = get_simple_verb_form(related[HIPONIMIA][0][1])
                res.append((related[HIPONIMIA][0][0], aim))
                print(related[HIPONIMIA][0][0], aim)
            else:
                break
    return res


class ApiError(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f"ApiError: status={self.status}"
