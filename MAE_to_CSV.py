import os
import click
import XML_parser.XML_parser as XML_parser
import pandas as pd


def sentence_anots_generator(anot_df):
    is_sep = anot_df['category'] == 'SEPARATOR'
    sep_rows = [i for i, x in enumerate(is_sep) if x]
    sep_pairs = [(sep_rows[i] + 1, sep_rows[i + 1]) for i in range(len(sep_rows) - 1)]
    # Sentence are between separators in the same source file
    borders_list = [pair for pair in sep_pairs if anot_df.iloc[pair[0]]['xml_num'] == anot_df.iloc[pair[1]]['xml_num']]
    for borders in borders_list:
        yield anot_df.iloc[borders[0]:borders[1]]


def print_stats(anot_df):
    for i, sentence in enumerate(sentence_anots_generator(anot_df)):
        active_actor_num = sum(sentence['category'] == 'Attribute')
        deontic_num = sum(sentence['category'] == 'Deontic')
        aim_num = sum(sentence['category'] == 'aIm')
        object_num = sum(sentence['category'] == 'oBject')
        passive_actor_num = sum(sentence['category'] == 'aCtor')
        ac_num = sum(sentence['category'] == 'ActivCondition')
        method_num = sum(sentence['category'] == 'Method')
        print(f'In sentence {i + 1}: active actors num = {active_actor_num}, deontic num = {deontic_num}, '
              f'aim num = {aim_num}, object num = {object_num}, passive actor num = {passive_actor_num}, '
              f'active condition num = {ac_num}, method num = {method_num}')


def anot_text_generator(senetence_anots, anot_type):
    emptyable = {'Deontic', 'ActivCondition', 'Method', 'oBject'}
    df = senetence_anots.loc[senetence_anots['category'] == anot_type]
    if anot_type in emptyable:
        if df.empty:
            df = df.append(pd.Series(), ignore_index=True)
    for _, row in df.iterrows():
        yield row['text']


def relational_sentence_generator(anot_df):
    # It returns each possible combination of entities (does a cartesian product). Therefore we call it Cogito XD.
    for senetence_anots in sentence_anots_generator(anot_df):
        for active_actor in anot_text_generator(senetence_anots, 'Attribute'):
            for aim in anot_text_generator(senetence_anots, 'aIm'):
                for deontic in anot_text_generator(senetence_anots, 'Deontic'):
                    for ac in anot_text_generator(senetence_anots, 'ActivCondition'):
                        for method in anot_text_generator(senetence_anots, 'Method'):
                            for passive_actor in anot_text_generator(senetence_anots, 'aCtor'):
                                for obj in anot_text_generator(senetence_anots, 'oBject'):
                                    # TODO: replace None with aim_category
                                    yield (active_actor, aim, None, deontic, ac, method, passive_actor, obj)


def read_xmls(xml_directory):
    parser = XML_parser.MAE_parser()
    xml_files = [os.path.join(xml_directory, file) for file in os.listdir(xml_directory) if file.endswith(".xml")]
    anot_dfs = []

    for i, xml_file in enumerate(xml_files):
        anot_df = parser.parse_file(xml_file)
        anot_df['xml_num'] = i + 1
        anot_dfs.append(anot_df)
    anot_df = pd.concat(anot_dfs, sort=False).reset_index(drop=True)
    return anot_df


@click.command()
@click.argument('xml_directory', type=click.Path(exists=True))
@click.argument('output_file', type=click.File('w'))
def main(xml_directory, output_file):
    anot_df = read_xmls(xml_directory)
    # print_stats(anot_df)
    relational_sentences_list = []
    for i, sentence in enumerate(relational_sentence_generator(anot_df)):
        relational_sentences_list.append(sentence)
    df = pd.DataFrame(relational_sentences_list, columns=['active_actor', 'aim', 'aim_category', 'deontic',
                                                          'active_condition', 'method', 'passive_actor', 'object'])
    df.to_csv(output_file, index=False)


if __name__ == '__main__':
    main()

# print(anot_df)