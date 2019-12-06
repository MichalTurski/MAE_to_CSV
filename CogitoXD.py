import itertools
import click
import pandas as pd
from tqdm import tqdm

from aim_category.aim_linker import AimLinker
import XLS_parser.XLS_parser as XLS_parser
from XLS_parser.XLS_parser import CATEGORY_KEY, TEXT_KEY, SENTENCE_KEY

METHOD_KEY = 'method'
ACTIVE_CONDITION_KEY = 'activcondition'
ACTOR_KEY = 'actor'
OBJECT_KEY = 'object'
AIM_KEY = 'aim'
DEONTIC_KEY = 'deontic'
ATTRIBUTE_KEY = 'attribute'


def anot_text_generator(senetence_anots, anot_type):
    emptyable = {DEONTIC_KEY, ACTIVE_CONDITION_KEY, METHOD_KEY, OBJECT_KEY}
    df = senetence_anots.loc[senetence_anots[CATEGORY_KEY] == anot_type]
    if anot_type in emptyable:
        if df.empty:
            df = df.append(pd.Series(), ignore_index=True)
    for _, row in df.iterrows():
        yield row[TEXT_KEY]


def relational_sentence_generator(inst_gram_sentence_df, aim_linker):
    # It returns each possible combination of entities (does a cartesian product). Therefore we call it Cogito XD.
    if not inst_gram_sentence_df.empty:
        sentence_id = inst_gram_sentence_df[SENTENCE_KEY].iloc[0]  # Since all id comes from the same sentence, they
        # are the same
        for active_actor, aim, deontic, ac, method, passive_actor, obj in itertools.product(
                *get_sentence_anots(inst_gram_sentence_df)):
            yield (sentence_id, active_actor, aim, aim_linker.get_aim_category(aim), deontic, ac, method,
                   passive_actor, obj)


def get_sentence_anots(senetence_anots):
    return (anot_text_generator(senetence_anots, ATTRIBUTE_KEY),
            anot_text_generator(senetence_anots, AIM_KEY),
            anot_text_generator(senetence_anots, DEONTIC_KEY),
            anot_text_generator(senetence_anots, ACTIVE_CONDITION_KEY),
            anot_text_generator(senetence_anots, METHOD_KEY),
            anot_text_generator(senetence_anots, ACTOR_KEY),
            anot_text_generator(senetence_anots, OBJECT_KEY))


def process_sentence(inst_gram_sentence_df, aim_linker):
    relational_sentence_list = []
    for rel_sentence in relational_sentence_generator(inst_gram_sentence_df, aim_linker):
        relational_sentence_list.append(rel_sentence)
    return relational_sentence_list


def create_aim_linker(df):
    aim_df = df.loc[df[CATEGORY_KEY] == AIM_KEY]
    return AimLinker(aim_df[['text']])


@click.command()
@click.argument('xls_file', type=click.File('rb'))
@click.argument('output_file', type=click.File('w'))
def cogito(xls_file, output_file):
    xls_parser = XLS_parser.XLS_parser(xls_file)
    aim_linker = create_aim_linker(xls_parser.anots_df)
    relational_sentences_list = []
    for inst_gram_sentence_df in tqdm(xls_parser.inst_gram_sentence_generator(), total=xls_parser.get_sentence_num()):
        relational_sentences_list.extend(process_sentence(inst_gram_sentence_df, aim_linker))
    df = pd.DataFrame(relational_sentences_list, columns=['sentence_num', 'active_actor', 'aim', 'aim_category',
                                                          'deontic', 'active_condition', 'method', 'passive_actor',
                                                          'object'])
    df.to_csv(output_file, index=False)


if __name__ == '__main__':
    cogito()
