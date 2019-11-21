import os
import XML_parser.XML_parser as XML_parser


def sentence_generator(anot_df):
    is_sep = anot_df['category'] == 'SEPARATOR'
    sep_rows = [i for i, x in enumerate(is_sep) if x]
    borders_list = [(sep_rows[i] + 1, sep_rows[i + 1]) for i in range(len(sep_rows)-1)]
    for borders in borders_list:
        yield anot_df.iloc[borders[0]:borders[1]]
    print('end')

xml_directory = "test_xml"
xml_files = [os.path.join(xml_directory, file) for file in os.listdir(xml_directory) if file.endswith(".xml")]
xml_file = xml_files[2]
print(f"I'm parsing {xml_file}")

parser = XML_parser.MAE_parser()
anot_df = parser.parse_file(xml_file)
for i, sentence in enumerate(sentence_generator(anot_df)):
    active_actor_num = sum(sentence["category"] == 'Attribute')
    deontic_num = sum(sentence["category"] == 'Deontic')
    aim_num = sum(sentence["category"] == 'aIm')
    object_num = sum(sentence["category"] == 'oBject')
    passive_actor_num = sum(sentence["category"] == 'aCtor')
    ac_num = sum(sentence["category"] == 'ActivCondition')
    method_num = sum(sentence["category"] == 'Method')
    print(f'In sentence {i+1}: active actors num = {active_actor_num}, deontic num = {deontic_num}, '
          f'object num = {object_num}, passive actor num = {passive_actor_num}, '
          f'active condition num = {ac_num}, method num = {method_num}')

# print(anot_df)