import requests

from igcogito.aim_category.utils import get_simple_verb_form, get_synset_domain
from igcogito.aim_category.http_cache_client import HttpCacheClient

BASE_URL = 'http://ws.clarin-pl.eu/lexrest/lex'

MORFEUSZ = 'morfeusz'
PLWORDNET = 'plwordnet'
ALL = 'all'
SYNSET = 'synset'

RESULTS = 'results'
SYNSETS = 'synsets'
SYNSET_NAME = 'str'
ID = 'id'
HIPONIMIA = 'hiponimia'
HIPERONIMIA = 'hiperonimia'
RELATED = 'related'
ANALYSE = 'analyse'

GI_DOMAIN = 39

VERB_ID_INDEX = 0
VERB_NAME_INDEX = 1
NONE_CATEGORY_KEY = -1

MORFEUSZ_VERB_FLAG = 'fin'
MORFEUSZ_INF_FLAG = 'inf'

http_client = HttpCacheClient(BASE_URL)


class ApiError(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f"ApiError: status={self.status}"


def create_api_post_request(BASE_URL, payload):
    return http_client.post(payload=payload)


def get_verb_infinitive_form(aim):
    aim_infinitive = None

    found_sie = 0
    found_nie = 0
    aim_splitted = aim.split()
    aim_to_process = aim_splitted[0]

    if aim_splitted[0] == "nie":
        found_nie = 1
        aim_to_process = aim_splitted[1]
    if aim.find("się") > -1:
        found_sie = 1

    resp = create_api_post_request(BASE_URL, payload={"task": ALL, "tool": MORFEUSZ, "lexeme": aim_to_process})
    list_of_words = resp[RESULTS][ANALYSE]
    for word_array in list_of_words:
        flags = word_array[2].split(":")
        if MORFEUSZ_VERB_FLAG in flags or MORFEUSZ_INF_FLAG in flags:
            aim_infinitive = word_array[1].split(":")[0]
            if found_sie:
                aim_infinitive = aim_infinitive + " się"

    return aim_infinitive


def get_aim_infinitive_id(aim_infinitive):
    if aim_infinitive:
        # TODO: change to offline when possible, to API when possible
        resp = create_api_post_request(BASE_URL, payload={"task": ALL, "tool": PLWORDNET, "lexeme": aim_infinitive})
        synset = get_domain_synset(resp)
        if ID in synset.keys():
            return synset[ID]
    return NONE_CATEGORY_KEY


def best_ancestor_not_found(hiponimia, ancestors):
    return hiponimia or not ancestors


def get_ancestors(aim):
    ancestors = hiponimia = []
    while best_ancestor_not_found(hiponimia, ancestors):
        # TODO: change to offline when possible, to API when possible
        resp = create_api_post_request(BASE_URL, payload={"task": ALL, "tool": PLWORDNET, "lexeme": aim})
        related = get_related_synsets(resp)
        if related:
            hiponimia = [] if HIPONIMIA not in related else related[HIPONIMIA]
            next_ancestor = add_ancestor(ancestors, hiponimia)
            if next_ancestor:
                ancestors.append(next_ancestor)
                aim = next_ancestor[1]
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


def get_best_hiponim(hiponimia):
    return hiponimia[0][VERB_ID_INDEX], get_simple_verb_form(hiponimia[0][VERB_NAME_INDEX])


def get_related_synsets(resp):
    try:
        return get_domain_synset(resp)[RELATED]
    except (IndexError, KeyError):
        return None


def get_domain_synset(resp):
    for synset in resp[RESULTS][SYNSETS]:
        domain_id = get_synset_domain(synset[SYNSET_NAME])
        if domain_id == GI_DOMAIN:
            return synset
    try:
        return resp[RESULTS][SYNSETS][0]
    except IndexError:
        return {}
