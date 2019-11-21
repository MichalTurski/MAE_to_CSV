import os
import xmlschema
import pandas as pd

class MAE_parser:
    def __init__(self):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        self.mae_schema = xmlschema.XMLSchema(os.path.join(curr_path, 'MAE.xsd'))

    @staticmethod
    def __category_to_df__(tags_dict, category):
        annotations_list = tags_dict[category]
        df = pd.DataFrame(annotations_list)
        df = df.rename(columns={"@id": "id", "@spans": "spans", "@text": "text", "@RodzajAC": "RodzajAC"})
        df['begin'] = df['spans'].apply(lambda x: x.split('~')[0])
        df['end'] = df['spans'].apply(lambda x: x.split('~')[1])
        df = df.drop(['spans'], axis=1)
        df['category'] = category
        return df

    def parse_file(self, file_path):
        mae_dict = self.mae_schema.to_dict(file_path)
        tags_dict = mae_dict['TAGS']
        anot_dfs_list = [self.__category_to_df__(tags_dict, 'SEPARATOR'),
                         self.__category_to_df__(tags_dict, 'Attribute'), self.__category_to_df__(tags_dict, 'Deontic'),
                         self.__category_to_df__(tags_dict, 'aIm'), self.__category_to_df__(tags_dict, 'oBject'),
                         self.__category_to_df__(tags_dict, 'aCtor'),
                         self.__category_to_df__(tags_dict, 'ActivCondition'),
                         self.__category_to_df__(tags_dict, 'Method')]
        anot_df = pd.concat(anot_dfs_list, sort=False).reset_index(drop=True)
        anot_df.sort_values(by=['begin'], inplace=True)
        return anot_df




