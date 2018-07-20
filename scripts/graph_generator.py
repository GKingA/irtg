import xml.etree.ElementTree as ET
import json
import os
import sys
import requests
import time
from parser import arguments


class Entry:
    def __init__(self, text, definition, pos):
        self.text = text
        self.definition = definition
        self.pos = pos

    def __repr__(self):
        return self.definition


special_characters = {
    '¢': 'cent',
    '£': 'pound ',
    '¥': 'yen',
    '¨': 'umlaut',
    '°': 'degrees',
    '²': '^2',
    'º': ' degrees',
    '¼': ' 1/4',
    '½': ' 1/2 ',
    '¾': ' 3/4 ',
    'à': 'a',
    'â': 'a',
    'ç': 'c',
    'è': 'e',
    'é': 'e',
    'ê': 'e',
    'ñ': 'nj',
    'ô': 'o',
    'ŋ': 'nh',
    'ə': 'e',
    'ˈ': '\'',
    'ˌ': ',',
    'β': 'beta',
    'π': 'pi',
    '–': '-',
    '♭': 'b',
    '〃': 'repeat',
    '₂': '2',
    '™': 'TM'
}


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


def find_special_chars(sentences):
    special = []
    with open(sentences, 'r') as sentence_file:
        sents = sentence_file.read().split('\n')
        for s in sents:
            special += [c for c in s if ord(c) > 128]
    special = list(set(special))
    special.sort()
    return special, len(special)


def replace_special_chars(sentence):
    for key, value in special_characters.items():
        sentence = sentence.replace(key, value)
    return sentence


def command_call(definition_file, definition_graph):
    with open(definition_file, 'r') as defs:
        definitions_read = defs.read().split('\n')
        start_at = 0
        graph_file = open(definition_graph, 'a')
        if os.path.isfile(definition_graph) and os.stat(definition_graph).st_size != 0:
            start_at = len(open(definition_graph, 'r').read().split('\n')) - 2 - 1  # -2 for the headers
                                                                                    # -1 for the newline at the end
        else:
            graph_file.write("# IRTG unannotated corpus file, v1.0\n"
                             "# interpretation graph: de.up.ling.irtg.algebra.graph.GraphAlgebra\n")
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        for line in definitions_read[start_at:]:
            graph_line = requests.post("http://hlt.bme.hu/4lang/udgraph",
                                       data=json.dumps({'sentence': replace_special_chars(line.strip())}),
                                       headers=headers, timeout=60)
            try:
                graph_to_print = graph_line.json()['graph'].split('\n')[-1]
                print(graph_to_print, file=graph_file)
            except Exception:
                time.sleep(60)
                graph_line = requests.post("http://hlt.bme.hu/4lang/udgraph",
                                           data=json.dumps({'sentence': replace_special_chars(line.strip())}),
                                           headers=headers, timeout=60)
                graph_to_print = graph_line.json()['graph'].split('\n')[-1]
                print(graph_to_print, file=graph_file)
        graph_file.close()


def save_dictionary(definition_graph, dictionary, entries):
    with open(dictionary, 'w') as dictionary_file:
        definition_graph_file = open(definition_graph, 'r')
        definition_graphs = definition_graph_file.read().split('\n')
        for graph, entry in zip(definition_graphs[2:], entries):
            dictionary_file.write(json.dumps({"text": entry.text, "pos": entry.pos, "def": entry.definition, "graph": graph}))
            dictionary_file.write('\n')
        definition_graph_file.close()


if __name__ == '__main__':
    if arguments.longman is None:
        print("Proper usage:\n"
              "python3 graph_generator.py --longman <dictionary_xml> [--definitions <definitions_output>] "
              "[--ud_graphs <ud_graphs>] [--definitions_json <dictionary_output_json>]", file=sys.stderr)
        raise Exception()
    xml_dict = arguments.longman
    definition_file_ = arguments.definitions
    definition_graph_ = arguments.ud_graphs
    dictionary_ = arguments.definitions_json
    if not os.path.isfile(definition_file_):
        entries_ = parser(xml_dict, definition_file_)
    else:
        entries_ = get_entries(xml_dict)
    # print(find_special_chars(definition_file_))
    command_call(definition_file_, definition_graph_)
    save_dictionary(definition_graph_, dictionary_, entries_)
