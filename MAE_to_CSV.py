import itertools
import os

import click
import pandas as pd
from tqdm import tqdm

import XML_parser.XML_parser as XML_parser
from aim_category.aim_linker import AimLinker

METHOD_KEY = 'Method'
ACTIVE_CONDITION_KEY = 'ActivCondition'
ACTOR_KEY = 'aCtor'
OBJECT_KEY = 'oBject'
AIM_KEY = 'aIm'
DEONTIC_KEY = 'Deontic'
ATTRIBUTE_KEY = 'Attribute'

CATEGORY_KEY = 'category'
XML_NUM = 'xml_num'


def inst_gram_sentence_generator(anot_df):
    is_sep = anot_df[CATEGORY_KEY] == 'SEPARATOR'
    sep_rows = [i for i, x in enumerate(is_sep) if x]
    sep_pairs = [(sep_rows[i] + 1, sep_rows[i + 1]) for i in range(len(sep_rows) - 1)]
    # Sentence are between separators in the same source file
    borders_list = [pair for pair in sep_pairs if anot_df.iloc[pair[0]][XML_NUM] == anot_df.iloc[pair[1]][XML_NUM]]
    for borders in borders_list:
        yield anot_df.iloc[borders[0]:borders[1]]


def print_stats(anot_df):
    for i, sentence in enumerate(inst_gram_sentence_generator(anot_df)):
        active_actor_num = sum(sentence[CATEGORY_KEY] == ATTRIBUTE_KEY)
        deontic_num = sum(sentence[CATEGORY_KEY] == DEONTIC_KEY)
        aim_num = sum(sentence[CATEGORY_KEY] == AIM_KEY)
        object_num = sum(sentence[CATEGORY_KEY] == OBJECT_KEY)
        passive_actor_num = sum(sentence[CATEGORY_KEY] == ACTOR_KEY)
        ac_num = sum(sentence[CATEGORY_KEY] == ACTIVE_CONDITION_KEY)
        method_num = sum(sentence[CATEGORY_KEY] == METHOD_KEY)
        print(f'In sentence {i + 1}: active actors num = {active_actor_num}, deontic num = {deontic_num}, '
              f'aim num = {aim_num}, object num = {object_num}, passive actor num = {passive_actor_num}, '
              f'active condition num = {ac_num}, method num = {method_num}')


def anot_text_generator(senetence_anots, anot_type):
    emptyable = {DEONTIC_KEY, ACTIVE_CONDITION_KEY, METHOD_KEY, OBJECT_KEY}
    df = senetence_anots.loc[senetence_anots[CATEGORY_KEY] == anot_type]
    if anot_type in emptyable:
        if df.empty:
            df = df.append(pd.Series(), ignore_index=True)
    for _, row in df.iterrows():
        yield row['text']


def relational_sentence_generator(inst_gram_sentence_df, sentence_idx, aim_linker):
    # It returns each possible combination of entities (does a cartesian product). Therefore we call it Cogito XD.
    for active_actor, aim, deontic, ac, method, passive_actor, obj in itertools.product(
            *get_sentence_anots(inst_gram_sentence_df)):
        yield (sentence_idx + 1, active_actor, aim, aim_linker.get_aim_category(aim), deontic, ac, method,
               passive_actor, obj)


def get_sentence_anots(senetence_anots):
    return (anot_text_generator(senetence_anots, ATTRIBUTE_KEY),
            anot_text_generator(senetence_anots, AIM_KEY),
            anot_text_generator(senetence_anots, DEONTIC_KEY),
            anot_text_generator(senetence_anots, ACTIVE_CONDITION_KEY),
            anot_text_generator(senetence_anots, METHOD_KEY),
            anot_text_generator(senetence_anots, ACTOR_KEY),
            anot_text_generator(senetence_anots, OBJECT_KEY))


def process_sentence(inst_gram_sentence_df, sentence_idx, aim_linker):
    relational_sentence_list = []
    for rel_sentence in relational_sentence_generator(inst_gram_sentence_df, sentence_idx, aim_linker):
        relational_sentence_list.append(rel_sentence)
    return relational_sentence_list


def read_xmls(xml_directory):
    parser = XML_parser.MAE_parser()
    xml_files = [os.path.join(xml_directory, file) for file in os.listdir(xml_directory) if file.endswith(".xml")]
    anot_dfs = []

    for i, xml_file in enumerate(xml_files):
        anot_df = parser.parse_file(xml_file)
        anot_df[XML_NUM] = i + 1
        anot_dfs.append(anot_df)
    anot_df = pd.concat(anot_dfs, sort=False).reset_index(drop=True)
    return anot_df


def create_aim_linker(df):
    aim_df = df.loc[df[CATEGORY_KEY] == AIM_KEY]
    return AimLinker(aim_df[['text']])


@click.command()
@click.argument('xml_directory', type=click.Path(exists=True))
@click.argument('output_file', type=click.File('w'))
def main(xml_directory, output_file):
    anot_df = read_xmls(xml_directory)
    # print_stats(anot_df)
    aim_linker = create_aim_linker(anot_df)
    relational_sentences_list = []
    for i, inst_gram_sentence_df in enumerate(tqdm(inst_gram_sentence_generator(anot_df))):
        relational_sentences_list.extend(process_sentence(inst_gram_sentence_df, i, aim_linker))
    df = pd.DataFrame(relational_sentences_list, columns=['sentence_num', 'active_actor', 'aim', 'aim_category',
                                                          'deontic', 'active_condition', 'method', 'passive_actor',
                                                          'object'])
    df.to_csv(output_file, index=False)


if __name__ == '__main__':
    main()

# print(anot_df)
