import pandas as pd
from tqdm import tqdm

from aim_category.lex_api import get_verb_standard_form, get_all_hiponimia
from aim_category.utils import get_simple_verb_form, add_if_not_present

AIM_KEY = "text"
STANDARDIZED_AIM_KEY = 'standardized_aim'
AIM_CATEGORY_KEY = 'aim_category'



class Aim_linker:
    def __init__(self, df):
        self.aim_df = df
        self.aim_dict = {}
        self.aim_id_2_aim_name = {}
        self.aim_name_2_aim_id = {}
        self.create_aim_dict()

    def create_aim_dict(self):
        self.aim_df.drop_duplicates(AIM_KEY, inplace=True)
        self.aim_df[STANDARDIZED_AIM_KEY] = self.aim_df.apply(lambda df: get_verb_standard_form(df[AIM_KEY]), axis=1)
        self.aim_df.drop_duplicates(STANDARDIZED_AIM_KEY, inplace=True)

        for aim in tqdm(self.aim_df[STANDARDIZED_AIM_KEY]):
            ancestors = self.get_ancestors(aim)
            if ancestors:
                aim_id, aim_name = ancestors[-1]
                self.__add_aim_id_2_aim_name_if_not_present(aim_id, aim_name)
                self.__add_aim_name_2_aim_id_if_not_present(aim_name, aim_id)
                self.aim_dict[self.aim_name_2_aim_id[aim]] = aim_name
        self.aim_df[AIM_CATEGORY_KEY] = self.aim_df.apply(lambda df: self.get_aim_category(df[STANDARDIZED_AIM_KEY]),
                                                          axis=1)
        print(self.aim_df.describe(include='all'))
        print(self.aim_df.head())

    def get_aim_category(self, aim):
        standardized_aim = get_verb_standard_form(aim)
        aim_id = self.aim_name_2_aim_id[standardized_aim]
        return self.aim_dict[aim_id]

    def get_ancestors(self, standardized_aim):
        ancestors = get_all_hiponimia(standardized_aim)
        print(ancestors)
        return ancestors

    def __update_aim_dict(self, aim, aim_id, hiponimia, hiperonimia):
        self.__add_aim_id_2_aim_name_if_not_present(aim_id, aim)
        self.__add_aim_name_2_aim_id_if_not_present(aim, aim_id)
        self.aim_dict[aim_id] = aim

        for verb in hiponimia:
            self.__add_aim_id_2_aim_name_if_not_present(verb[0], get_simple_verb_form(verb[1]))
            self.__add_aim_name_2_aim_id_if_not_present(get_simple_verb_form(verb[1]), verb[0])
            # TODO: move it to move_up function
            if verb[0] in self.aim_dict:
                print(f"\nhiponimia {self.aim_id_2_aim_name[aim_id]} --> {get_simple_verb_form(verb[1])}")

            # TODO: chose 39 domain, or other in correct order
            self.aim_dict[verb[0]] = get_simple_verb_form(verb[1])
            continue

        for verb in hiperonimia:
            if verb[0] in self.aim_dict:
                self.aim_dict[verb[0]] = self.aim_dict[aim_id]
                self.__add_aim_id_2_aim_name_if_not_present(verb[0], get_simple_verb_form(verb[1]))
                self.__add_aim_name_2_aim_id_if_not_present(get_simple_verb_form(verb[1]), verb[0])
                print(f"\nhiperonimia {get_simple_verb_form(verb[1])} --> {self.aim_id_2_aim_name[aim_id]}")

    def __add_aim_id_2_aim_name_if_not_present(self, aim_id, aim_name):
        self.aim_id_2_aim_name = add_if_not_present(aim_id, aim_name, self.aim_id_2_aim_name)

    def __add_aim_name_2_aim_id_if_not_present(self, aim_name, aim_id):
        self.aim_name_2_aim_id = add_if_not_present(aim_name, aim_id, self.aim_name_2_aim_id)


linker = Aim_linker(pd.read_csv("out.csv"))
