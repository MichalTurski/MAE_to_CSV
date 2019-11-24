import pandas as pd
from tqdm import tqdm

from aim_category.lex_api import get_verb_standard_form, get_homonimia_and_hiperonimia

AIM = "aim"


def get_simple_verb_form(verb):
    return verb.split('.')[0][1:]


class Aim_linker:
    def __init__(self, df):
        self.aim_df = df
        self.aim_dict = {}
        self.aim_id_2_aim_name = {}
        self.create_aim_dict()

    def create_aim_dict(self):
        self.aim_df.drop_duplicates(AIM, inplace=True)
        for aim in tqdm(self.aim_df[AIM]):
            aim = get_verb_standard_form(aim)
            aim_id, hiponimia, hiperonimia = get_homonimia_and_hiperonimia(aim)
            self.__update_aim_dict(aim, aim_id, hiponimia, hiperonimia)
        print(self.aim_dict)
        s = set(val for val in self.aim_dict.values())
        print(len(self.aim_dict), len(s))

    def __update_aim_dict(self, aim, aim_id, hiponimia, hiperonimia):
        self.__add_aim_id_2_aim_name_if_not_present(aim_id, aim)
        self.aim_dict[aim_id] = aim

        for verb in hiponimia:
            self.aim_dict[aim_id] = get_simple_verb_form(verb[1])
            if verb[0] in self.aim_dict:
                self.__add_aim_id_2_aim_name_if_not_present(verb[0], get_simple_verb_form(verb[1]))
                print(f"\nhimopnimia {self.aim_id_2_aim_name[aim_id]} --> {get_simple_verb_form(verb[1])}")
                continue

        for verb in hiperonimia:
            self.aim_dict[verb[0]] = self.aim_dict[aim_id]
            if verb[0] in self.aim_dict:
                self.__add_aim_id_2_aim_name_if_not_present(verb[0], get_simple_verb_form(verb[1]))
                print(f"\nhiperpnimia {get_simple_verb_form(verb[1])} --> {self.aim_id_2_aim_name[aim_id]}")

    def __add_aim_id_2_aim_name_if_not_present(self, aim_id, aim):
        if aim_id not in self.aim_id_2_aim_name:
            self.aim_id_2_aim_name[aim_id] = aim


linker = Aim_linker(pd.read_csv("out.csv"))
