import xml.etree.ElementTree as ET
import subprocess
import json
import os
import sys


class Entry:
    def __init__(self, text, definition, pos):
        self.text = text
        self.definition = definition
        self.pos = pos

    def __repr__(self):
        return self.definition


def definitions(sense, text, pos):
    current = []
    def_text = ''
    for tags in sense:
        if tags.tag == "DEF" and tags.text.strip(' ') != '':
            if sense.find("FULLFORM") is not None:
                children = [c for c in sense]
                if children.index(sense.find("FULLFORM")) < children.index(tags):
                    def_text = sense.find("FULLFORM").text.strip(' ') + ' ' + tags.text.strip(' ')
                else:
                    def_text = tags.text.strip(' ') + ' ' + sense.find("FULLFORM").text.strip(' ')
            else:
                def_text = tags.text.strip(' ')
            current.append(Entry(text, def_text.strip(' '), pos))
            def_text = ''
        elif tags.tag == "DEF" and tags.find("TEXT") is not None:
            for texts in tags:
                if texts.tag == "TEXT" or texts.tag == "FULLFORM":
                    def_text = ' '.join([def_text, texts.text.strip(' ')])
                elif texts.tag == "NonDV" and texts.find("REFHWD") is not None:
                    for refhwd in texts.findall("REFHWD"):
                        def_text = ' '.join([def_text, refhwd.text.strip(' ')])
            current.append(Entry(text, def_text.strip(' '), pos))
            def_text = ''
    return current


def get_entries(dict_xml):
    tree = ET.parse(dict_xml)
    entries = []
    for entry in tree.findall("Entry"):
        text = entry.find("Head").find("HWD").text.strip(' ')
        if entry.find("Head").find("POS") is not None:
            pos = entry.find("Head").find("POS").text.strip(' ')
        else:
            pos = '-'
        for sense in entry.findall("Sense"):
            entries += definitions(sense, text, pos)
            for subsense in sense.findall("Subsense"):
                entries += definitions(subsense, text, pos)
    return entries


def parser(dict_xml, definition_file):
    tree = ET.parse(dict_xml)
    entries = []
    with open(definition_file, 'w') as definition_file:
        for entry in tree.findall("Entry"):
            current = []
            text = entry.find("Head").find("HWD").text.strip(' ')
            if entry.find("Head").find("POS") is not None:
                pos = entry.find("Head").find("POS").text.strip(' ')
            else:
                pos = '-'
            for sense in entry.findall("Sense"):
                current += definitions(sense, text, pos)
                for subsense in sense.findall("Subsense"):
                    current += definitions(subsense, text, pos)
            entries += current
            for c in current:
                print(str(c), file=definition_file)
                print(c.text, c.definition, c.pos)
    return entries


def command_call(definition_file, definition_graph, parse_to_isi, stanford_parser, converter):
    command = "python {0}/parse_to_isi.py {1} {2} {3} {4}".format(parse_to_isi, stanford_parser, converter,
                                                                  definition_file, definition_graph).split(' ')
    subprocess.call(command)


def save_dictionary(definition_graph, dictionary, entries):
    with open(dictionary, 'w') as dictionary_file:
        definition_graph_file = open(definition_graph, 'r')
        definition_graphs = definition_graph_file.read().split('\n')
        for graph, entry in zip(definition_graphs[2:], entries):
            dictionary_file.write(json.dumps({"text": entry.text, "pos": entry.pos, "def": entry.definition, "graph": graph}))
            dictionary_file.write('\n')
        definition_graph_file.close()


if __name__ == '__main__':
    if len(sys.argv) != 8:
        print("Proper usage:\npython3 graph_generator.py <dictionary_xml> <definitions_output> <output_graphs>"
              "<dictionary_output_json> <parse_to_isi_path> <stanford_parser_path> <converter_path>", file=sys.stderr)
        raise Exception()
    xml_dict = sys.argv[1]
    definition_file_ = sys.argv[2]
    definition_graph_ = sys.argv[3]
    dictionary_ = sys.argv[4]
    parse_to_isi_ = sys.argv[5]
    stanford_parser_ = sys.argv[6]
    converter_ = sys.argv[7]
    if not os.path.isfile(definition_file_):
        entries_ = parser(xml_dict, definition_file_)
    else:
        entries_ = get_entries(xml_dict)
    if not os.path.isfile(definition_graph_):
        command_call(definition_file_, definition_graph_, parse_to_isi_, stanford_parser_, converter_)
    save_dictionary(definition_graph_, dictionary_, entries_)
