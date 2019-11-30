def get_simple_verb_form(verb):
    return verb.split('.')[0][1:]


def add_if_not_present(key, value, dict):
    if key not in dict:
        dict[key] = value
    return dict


def get_unique_values_number(dict):
    s = set(val for val in dict.values())
    return len(s)
