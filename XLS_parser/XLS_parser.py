import pandas as pd
import sys
import bs4
from bs4 import BeautifulSoup as bs


CATEGORY_KEY = 'category'
TEXT_KEY = 'text'


class XLS_parser:
    def __init__(self, file):
        self.exel_df = pd.read_excel(file, encoding=sys.getfilesystemencoding(), sheet_name='mae_xml')

    def inst_gram_sentence_generator(self):
        for _, sentence in self.exel_df.iterrows():
            anots_list = []
            soup = bs(sentence[0], 'html.parser')
            for tag in soup:
                if isinstance(tag, bs4.element.Tag):
                    text = tag.text.replace('\n', ' ').replace('  ', ' ')
                    anots_list.append((tag.name, text))
            yield pd.DataFrame(anots_list, columns=[CATEGORY_KEY, TEXT_KEY])
