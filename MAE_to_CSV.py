import os
import XML_parser.XML_parser as XML_parser


xml_directory = "test_xml"
xml_files = [os.path.join(xml_directory, file) for file in os.listdir(xml_directory) if file.endswith(".xml")]
xml_file = xml_files[0]

parser = XML_parser.MAE_parser()
anot_df = parser.parse_file(xml_file)
print(anot_df)