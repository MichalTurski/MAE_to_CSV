import pandas as pd
import sys
import bs4
from bs4 import BeautifulSoup as bs


CATEGORY_KEY = 'category'
TEXT_KEY = 'text'
SENTENCE_KEY = 'sentence_id'


class XLS_parser:
    def __init__(self, file):
        exel_df = pd.read_excel(file, encoding=sys.getfilesystemencoding(), sheet_name='mae_xml')
        anots_list = []
        for idx, sentence in exel_df.iterrows():
            anots_list.extend(self.__process_sentence__(sentence, idx + 1))
        self.anots_df = pd.DataFrame(anots_list, columns=[SENTENCE_KEY, CATEGORY_KEY, TEXT_KEY])

    @staticmethod
    def __process_sentence__(sentence, sentence_id):
        anots_list = []
        soup = bs(sentence[0], 'html.parser')
        for tag in soup:
            if isinstance(tag, bs4.element.Tag):
                text = tag.text.replace('\n', ' ').replace('  ', ' ')
                anots_list.append((sentence_id, tag.name, text))
        return anots_list

    def inst_gram_sentence_generator(self):
        sentences_num = self.anots_df[SENTENCE_KEY].max()
        for sent_id in range(1, sentences_num + 1):
            to_ret = self.anots_df.loc[self.anots_df[SENTENCE_KEY] == sent_id]
            yield to_ret

    def get_sentence_num(self):
        return self.anots_df[SENTENCE_KEY].max()
