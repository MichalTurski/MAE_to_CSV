from tqdm import tqdm

from aim_category.lex_api import get_verb_standard_form, get_homonimia_and_hiperonimia, get_all_hiponimia

AIM_CATEGORY = 'aim_category'

STANDARDIZED_AIM = 'standardized_aim'

AIM = "text"


def get_simple_verb_form(verb):
    return verb.split('.')[0][1:]


def add_if_not_present(key, value, dict):
    if key not in dict:
        dict[key] = value
    return dict


def get_unique_values_number(dict):
    s = set(val for val in dict.values())
    return len(s)


class Aim_linker:
    def __init__(self, df):
        self.aim_df = df
        self.aim_dict = {}
        self.aim_id_2_aim_name = {}
        self.aim_name_2_aim_id = {}
        self.__hiponimia__ = []
        self.create_aim_dict()

    def create_aim_dict(self):
        self.aim_df.drop_duplicates(AIM, inplace=True)

        self.aim_df[STANDARDIZED_AIM] = self.aim_df.apply(lambda df: get_verb_standard_form(df[AIM]), axis=1)
        self.aim_df.drop_duplicates(STANDARDIZED_AIM, inplace=True)
        for aim in tqdm(self.aim_df[STANDARDIZED_AIM]):
            aim_id, hiponimia, hiperonimia = get_homonimia_and_hiperonimia(aim)
            self.__update_aim_dict(aim, aim_id, hiponimia, hiperonimia)
        print(self.aim_dict)
        print(len(self.aim_dict), get_unique_values_number(self.aim_dict))
        # self.__merge_verb_meanings()
        print(self.aim_df.describe(include='all'))
        print(self.aim_df.head())
        for aim in tqdm(self.aim_df[STANDARDIZED_AIM]):
            ancestors = self.get_ancestors(aim)
            if ancestors:
                aim_id, aim_name = ancestors[-1]
                self.__add_aim_id_2_aim_name_if_not_present(aim_id, aim_name)
                self.__add_aim_name_2_aim_id_if_not_present(aim_name, aim_id)
                self.aim_dict[self.aim_name_2_aim_id[aim]] = aim_name
        self.aim_df[AIM_CATEGORY] = self.aim_df.apply(lambda df: self.__get_aim_category(df[STANDARDIZED_AIM]), axis=1)
        print(self.aim_df.describe(include='all'))
        print(self.aim_df.head())

    def get_aim_category(self, aim):
        aim = get_verb_standard_form(aim)
        return self.__get_aim_category(aim)

    def __get_aim_category(self, standardized_aim):
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
            self.__hiponimia__.append(verb[0])
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

    def __merge_verb_meanings(self):
        for verb_id in self.__hiponimia__:
            aim = self.aim_id_2_aim_name[verb_id]
            aim_id, hiponimia, hiperonimia = get_homonimia_and_hiperonimia(aim)
            for verb in hiponimia:
                self.__add_aim_id_2_aim_name_if_not_present(verb[0], get_simple_verb_form(verb[1]))
            for verb in hiperonimia:
                if verb[0] in self.aim_dict:
                    self.aim_dict[verb[0]] = self.aim_dict[aim_id]
                    self.__add_aim_id_2_aim_name_if_not_present(verb[0], get_simple_verb_form(verb[1]))
                    print(f"\nhiperonimia {get_simple_verb_form(verb[1])} --> {self.aim_id_2_aim_name[aim_id]}")

# linker = Aim_linker(pd.read_csv("out.csv"))
