from typing import List, Tuple

import xmlschema
import pandas as pd

SEPARATOR_TAG = 'SEPARATOR'

SPANS_KEY = '@spans'
ID_KEY = '@id'
TEXT_KEY = '@text'

BASE_KEYS = [ID_KEY, SPANS_KEY, TEXT_KEY]


class MAEToXLSParser:

    def __init__(self, xsd_path: str, xml_path: str):
        """Produces XML-like XLS file from MAE format XML's

        Args:
            xsd_path: path to the MAE XSD schema file
            xml_path: path to annotated XML in MAE format
        """
        self._schema = xmlschema.XMLSchema(xsd_path)
        self._schema.validate(xml_path)

        xml_dict = self._schema.to_dict(xml_path)
        self._text = xml_dict['TEXT']
        self._tags = xml_dict['TAGS']

    def _get_sorted_tags_spans(self) -> List[Tuple[int, int, str, list]]:
        """Creates sorted list of tags and indices.
        Additional properties like 'Time' from ActivCondition are also attached

        Returns:
            list of tuples: (start_index, end_index, tag, additional_properties)

        """
        all_spans = []
        for tag in self._tags.keys():
            for row in self._tags[tag]:
                for span_set in row[SPANS_KEY].split(','):
                    spans = [int(span) for span in span_set.split('~')]

                    properties = [row[key] for key in row.keys() if key not in BASE_KEYS]
                    all_spans.append((spans[0], spans[1], tag, properties))

        all_spans.sort(key=lambda x: x[0])

        return all_spans

    def parse_xml(self, output_path: str):
        """Parses MAE's XML into XLS file.
         Produces XLS file with one column ('statement') and one sheet('mae_xml').
         Rows are separated by the SEPARATOR tags, thus each new row usually starts with the <SEPARATOR> tag.

         Single row example:
             <SEPARATOR>2.</SEPARATOR><Attribute>Uniwersytet</Attribute><aIm>
             jest</aIm><aCtor>osobą prawną z siedzibą w Warszawie</aCtor>

         Note:
             additional properties like 'Time' indicator in ActivCondition tags are attached in a similar way as the
             HTML attributes, eg:
                <ActivCondition Time>na wniosek ...</ActivCondition>

        Args:
            output_path: path to the output file

        """

        sorted_spans = self._get_sorted_tags_spans()

        output = ""
        separators_idx = []

        for i in range(0, len(sorted_spans)):
            tag = sorted_spans[i][2]
            properties = " ".join(sorted_spans[i][3])
            start = sorted_spans[i][0]
            end = sorted_spans[i][1]

            if i > 0:
                end_prev = sorted_spans[i - 1][1]
            else:
                end_prev = 0

            if properties:
                opening_tag = f"<{tag} {properties}>"
            else:
                opening_tag = f"<{tag}>"
            closing_tag = f"</{tag}>"

            output += self._text[end_prev:start]

            if tag == SEPARATOR_TAG: # store where are the separators
                separators_idx.append(len(output))

            output += opening_tag + self._text[start:end] + closing_tag

        output += self._text[end:]
        output_rows = []
        start_split = 0
        # split the text by separators
        for separator_start in separators_idx:
            output_rows.append(output[start_split: separator_start])
            start_split = separator_start

        df = pd.DataFrame(output_rows, columns=['statement'])
        df.to_excel(output_path, sheet_name='mae_xml', index=False)
