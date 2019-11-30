from tqdm import tqdm
import pandas as pd

from aim_category.lex_api import get_verb_infinitive_form, get_ancestors, get_aim_infinitive_id
from aim_category.lex_api import NONE_CATEGORY_KEY
from aim_category.utils import add_if_not_present

AIM_KEY = "text"
AIM_INFINITIVE_KEY = 'aim_infinitive'
AIM_CAT_KEY = 'aim_category'
NONE_CATEGORY = None

class AimLinker:
    def __init__(self, df):
        self.aim_df = df
        self.aim_dict = {}
        self.aim_id_2_aim_name = {}
        self.aim_name_2_aim_id = {}
        self.aim_to_aim_infinitive = {NONE_CATEGORY_KEY: None}
        self.__create_aim_dict()

    def get_aim_category(self, aim):
        if not aim:
            return None
        if aim not in self.aim_to_aim_infinitive:
            self.aim_to_aim_infinitive[aim] = get_verb_infinitive_form(aim)
        aim_infinitive = self.aim_to_aim_infinitive[aim]
        aim_id = self.aim_name_2_aim_id[aim_infinitive]
        return self.aim_dict[aim_id]

    def get_ancestors(self, standardized_aim):
        return get_ancestors(standardized_aim)

    def __create_aim_dict(self):
        self.__initialize_aim_df()

        for aim_infinitive in tqdm(self.aim_df[AIM_INFINITIVE_KEY]):
            if aim_infinitive:
                self.__process_aim(aim_infinitive)

        self.aim_df[AIM_CAT_KEY] = self.__create_aim_category_column()
        # print(self.aim_df.describe(include='all'))
        # print(self.aim_df.head())

    def __initialize_aim_df(self):
        self.aim_df.drop_duplicates(AIM_KEY, inplace=True)
        self.aim_df[AIM_INFINITIVE_KEY] = self.__create_standardized_aim_column()
        self.aim_df.drop_duplicates(AIM_INFINITIVE_KEY, inplace=True)

    def __create_standardized_aim_column(self):
        return self.aim_df.apply(lambda df: get_verb_infinitive_form(df[AIM_KEY]), axis=1)

    def __create_aim_category_column(self):
        return self.aim_df.apply(lambda df: self.get_aim_category(df[AIM_INFINITIVE_KEY]), axis=1)

    def __process_aim(self, aim_infinitive):
        aim_id = get_aim_infinitive_id(aim_infinitive)
        self.__add_dual_mappings(aim_id, aim_infinitive)
        self.aim_dict[aim_id] = aim_infinitive
        self.__add_aim_ancestor(aim_infinitive, aim_id)

    def __add_aim_ancestor(self, aim_infinitive, aim_id):
        ancestors = self.get_ancestors(aim_infinitive)
        if ancestors:
            ancestor_aim_id, ancestor_aim_name = ancestors[-1]
            self.__add_dual_mappings(ancestor_aim_id, ancestor_aim_name)
            self.aim_dict[aim_id] = ancestor_aim_name
            self.aim_dict[ancestor_aim_id] = ancestor_aim_name

    def __add_dual_mappings(self, aim_id, aim):
        self.__add_aim_id_2_aim_name_if_not_present(aim_id, aim)
        self.__add_aim_name_2_aim_id_if_not_present(aim, aim_id)

    def __add_aim_id_2_aim_name_if_not_present(self, aim_id, aim_name):
        self.aim_id_2_aim_name = add_if_not_present(aim_id, aim_name, self.aim_id_2_aim_name)

    def __add_aim_name_2_aim_id_if_not_present(self, aim_name, aim_id):
        self.aim_name_2_aim_id = add_if_not_present(aim_name, aim_id, self.aim_name_2_aim_id)

# linker = AimLinker(pd.read_csv("out.csv"))
