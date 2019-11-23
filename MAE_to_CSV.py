import os
import click
import XML_parser.XML_parser as XML_parser
import pandas as pd


def sentence_generator(anot_df):
    is_sep = anot_df['category'] == 'SEPARATOR'
    sep_rows = [i for i, x in enumerate(is_sep) if x]
    sep_pairs = [(sep_rows[i] + 1, sep_rows[i + 1]) for i in range(len(sep_rows) - 1)]
    # Sentence are between separators in the same source file
    borders_list = [pair for pair in sep_pairs if anot_df.iloc[pair[0]]['xml_num'] == anot_df.iloc[pair[1]]['xml_num']]
    for borders in borders_list:
        yield anot_df.iloc[borders[0]:borders[1]]
    print('end')


def print_stats(anot_df):
    for i, sentence in enumerate(sentence_generator(anot_df)):
        active_actor_num = sum(sentence["category"] == 'Attribute')
        deontic_num = sum(sentence["category"] == 'Deontic')
        aim_num = sum(sentence["category"] == 'aIm')
        object_num = sum(sentence["category"] == 'oBject')
        passive_actor_num = sum(sentence["category"] == 'aCtor')
        ac_num = sum(sentence["category"] == 'ActivCondition')
        method_num = sum(sentence["category"] == 'Method')
        print(f'In sentence {i + 1}: active actors num = {active_actor_num}, deontic num = {deontic_num}, '
              f'object num = {object_num}, passive actor num = {passive_actor_num}, '
              f'active condition num = {ac_num}, method num = {method_num}')

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

    print_stats(anot_df)


if __name__ == '__main__':
    main()

# print(anot_df)