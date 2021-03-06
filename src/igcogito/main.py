import itertools
import click
import pandas as pd
from tqdm import tqdm
from pathlib import Path

from igcogito.aim_category.aim_linker import AimLinker
import igcogito.XLS_parser.XLS_parser as XLS_parser
from igcogito.XLS_parser.XLS_parser import CATEGORY_KEY, TEXT_KEY, SENTENCE_KEY
from igcogito.XML_parser.xls import MAEToXLSParser

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


def cogito(xls_file, output_file):
    xls_parser = XLS_parser.XLS_parser(xls_file)
    aim_linker = create_aim_linker(xls_parser.anots_df)
    relational_sentences_list = []
    for inst_gram_sentence_df in tqdm(xls_parser.inst_gram_sentence_generator(), total=xls_parser.get_sentence_num()):
        relational_sentences_list.extend(process_sentence(inst_gram_sentence_df, aim_linker))
    df = pd.DataFrame(relational_sentences_list, columns=['sentence_num', 'active_actor', 'aim', 'aim_category',
                                                          'deontic', 'active_condition', 'method', 'passive_actor',
                                                          'object'])
    target_path = Path(output_file).expanduser().absolute()
    target_path.parents[0].mkdir(parents=True, exist_ok=True)
    df.to_csv(str(target_path), index=False)


def xml_to_xls(mae_file, output_file):
    mae_schema = str(Path(__file__).parents[0] / 'XML_parser' / 'mae_schema.xsd')
    mae_parser = MAEToXLSParser(mae_schema, str(mae_file))
    mae_parser.parse_xml(str(output_file))

@click.command()
@click.argument('xls_file', type=click.File('rb'))
@click.argument('output_file', type=str)
def console_entry(xls_file, output_file):
    cogito(xls_file, output_file)


@click.command()
@click.argument('mae_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
def xml_to_xls_console_entry(mae_file, output_file):
    xml_to_xls(mae_file, output_file)


if __name__ == '__main__':
    console_entry()
