import pandas as pd
from tqdm import tqdm

from aim_category.lex_api import get_verb_standard_form, get_all_hiponimia, get_aim_id
from aim_category.utils import add_if_not_present

AIM_KEY = "text"
STANDARDIZED_AIM_KEY = 'standardized_aim'
AIM_CATEGORY_KEY = 'aim_category'


class Aim_linker:
    def __init__(self, df):
        self.aim_df = df
        self.aim_dict = {}
        self.aim_id_2_aim_name = {}
        self.aim_name_2_aim_id = {}
        self.__create_aim_dict()

    def __create_aim_dict(self):
        self.aim_df.drop_duplicates(AIM_KEY, inplace=True)
        self.aim_df[STANDARDIZED_AIM_KEY] = self.aim_df.apply(lambda df: get_verb_standard_form(df[AIM_KEY]), axis=1)
        self.aim_df.drop_duplicates(STANDARDIZED_AIM_KEY, inplace=True)

        for aim in tqdm(self.aim_df[STANDARDIZED_AIM_KEY]):
            aim_id = get_aim_id(aim)
            self.add_dual_mappings(aim_id, aim)
            self.aim_dict[aim_id] = aim

            ancestors = self.get_ancestors(aim)
            if ancestors:
                ancestor_aim_id, ancestor_aim_name = ancestors[-1]
                self.add_dual_mappings(ancestor_aim_id, ancestor_aim_name)
                self.aim_dict[aim_id] = ancestor_aim_name
                self.aim_dict[ancestor_aim_id] = ancestor_aim_name

        self.aim_df[AIM_CATEGORY_KEY] = self.aim_df.apply(lambda df: self.get_aim_category(df[STANDARDIZED_AIM_KEY]),
                                                          axis=1)
        print(self.aim_df.describe(include='all'))
        print(self.aim_df.head())

    def get_aim_category(self, aim):
        standardized_aim = get_verb_standard_form(aim)
        aim_id = self.aim_name_2_aim_id[standardized_aim]
        return self.aim_dict[aim_id]

    def get_ancestors(self, standardized_aim):
        return get_all_hiponimia(standardized_aim)

    def __add_aim_id_2_aim_name_if_not_present(self, aim_id, aim_name):
        self.aim_id_2_aim_name = add_if_not_present(aim_id, aim_name, self.aim_id_2_aim_name)

    def __add_aim_name_2_aim_id_if_not_present(self, aim_name, aim_id):
        self.aim_name_2_aim_id = add_if_not_present(aim_name, aim_id, self.aim_name_2_aim_id)

    def add_dual_mappings(self, aim_id, aim):
        self.__add_aim_id_2_aim_name_if_not_present(aim_id, aim)
        self.__add_aim_name_2_aim_id_if_not_present(aim, aim_id)


linker = Aim_linker(pd.read_csv("out.csv"))
