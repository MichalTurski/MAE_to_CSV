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


def get_objects(senetence_anots, obj_type):
    emptyable = {'Deontic', 'ActivCondition', 'Method', 'oBject'}
    df = senetence_anots.loc[senetence_anots['category'] == obj_type]
    if obj_type in emptyable:
        if df.empty:
            df = df.append(pd.Series(), ignore_index=True)
    return df

def relational_sentence_genetator(anot_df):
    # It returns each possible combination of entities (does a cartesian product). Therefore we call it Cogito XD.
    for senetence_anots in sentence_anots_generator(anot_df):
        active_actor_df = get_objects(senetence_anots, 'Attribute')
        aim_df = get_objects(senetence_anots, 'aIm')
        deontic_df = get_objects(senetence_anots, 'Deontic')
        ac_df = get_objects(senetence_anots, 'ActivCondition')
        method_df = get_objects(senetence_anots, 'Method')
        passive_actor_df = get_objects(senetence_anots, 'aCtor')
        object_df = get_objects(senetence_anots, 'oBject')
        for active_actor in active_actor_df.iterrows():
            for aim in aim_df.iterrows():
                for deontic in deontic_df.iterrows():
                    for ac in ac_df.iterrows():
                        for method in method_df.iterrows():
                            for passive_actor in passive_actor_df.iterrows():
                                for obj in object_df.iterrows():
                                    yield (active_actor, aim, deontic, ac, method, passive_actor, obj)


@click.command()
@click.argument('xml_directory', type=click.Path(exists=True))
def main(xml_directory):
    parser = XML_parser.MAE_parser()
    xml_files = [os.path.join(xml_directory, file) for file in os.listdir(xml_directory) if file.endswith(".xml")]
    anot_dfs =[]

    for i, xml_file in enumerate(xml_files):
        anot_df = parser.parse_file(xml_file)
        anot_df['xml_num'] = i+1
        anot_dfs.append(anot_df)
    anot_df = pd.concat(anot_dfs, sort=False).reset_index(drop=True)

    # print_stats(anot_df)
    for i, _ in enumerate(relational_sentence_genetator(anot_df)):
        pass
    print(i)


if __name__ == '__main__':
    main()

# print(anot_df)