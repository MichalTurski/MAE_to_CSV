import requests

BASE_URL = 'http://ws.clarin-pl.eu/lexrest/lex'

MORFEUSZ = 'morfeusz'
PLWORDNET = 'plwordnet'
ALL = 'all'

RESULTS = 'results'
SYNSETS = 'synsets'
HIPONIMIA = 'hiponimia'
RELATED = 'related'
ANALYSE = 'analyse'


# TODO: think about 'się', ':v1'
# TODO: domain id = 39


def get_verb_standard_form(aim):
    # to omit 'się'
    aim = aim.split()[0]

    resp = requests.post(BASE_URL, json={"task": ALL, "tool": MORFEUSZ, "lexeme": aim})
    if resp.status_code != 200:
        raise ApiError(resp.status_code)

    return resp.json()[RESULTS][ANALYSE][0][1]


def get_hiperonims(aim):
    # to omit versioning 'kierować:v1'
    aim = aim.split(':')[0]

    resp = requests.post(BASE_URL, json={"task": ALL, "tool": PLWORDNET, "lexeme": aim})
    if resp.status_code != 200:
        raise ApiError(resp.status_code)

    return resp.json()[RESULTS][SYNSETS][0][RELATED][HIPONIMIA]


class ApiError(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f"ApiError: status={self.status}"
