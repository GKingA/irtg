import sys
from check_pos import parse_tags
from parser import arguments
from common import sanitize_word, dict_pos_to_irtg_pos


def get_words(irtg):
    words = []
    with open(irtg, 'r') as irtg_file:
        line = irtg_file.readline()
        while line is not None and line != "":
            if '->' in line and not line.startswith('X') and not line.startswith('S') and not line.startswith('//'):
                words.append(line.strip('\n').split(' -> ')[1])
            line = irtg_file.readline()
    return words


def print_definition(grammar, pos, word):
    if word.startswith('interpretation'):
        word = word.capitalize()
    if ' ' not in word:
        grammar.write('{0} -> {1}\n[graph] "({1}<root> / {1})"\n[fourlang] "({1}<root> / {1})"\n\n'
                      .format(pos, sanitize_word(word)))


def find_unknown_words_in_definition(definition, graph_list, grammar, words):
    unknown = []
    for word in definition.split(' '):
        if word not in words:
            unknown.append(word)
    if len(unknown) != 0:
        for u in set(unknown):
            for graph in graph_list:
                if graph['text'] == u:
                    if type(dict_pos_to_irtg_pos[graph['pos']]) == list:
                        for pos in dict_pos_to_irtg_pos[graph['pos']]:
                            print_definition(grammar, pos, u)
                    else:
                        print_definition(grammar, dict_pos_to_irtg_pos[graph['pos']], u)
            words.append(u)


def get_graphs_for_words(words, graph_path, irtg):
    graph_list = parse_tags(graph_path)
    grammar = open(irtg, 'a')
    for line_data in graph_list:
        if line_data['text'] not in words:
            if type(dict_pos_to_irtg_pos[line_data['pos']]) == list:
                for pos in dict_pos_to_irtg_pos[line_data['pos']]:
                    print_definition(grammar, pos, line_data['text'])
            else:
                print_definition(grammar, dict_pos_to_irtg_pos[line_data['pos']], line_data['text'])
        find_unknown_words_in_definition(line_data['def'], graph_list, grammar, words)


def get_relevant_graphs(words, file_name, output_path):
    with open(file_name, 'r') as graphs:
        output_file = open(output_path, 'w')
        line = graphs.readline()
        while line is not None and line != "":
            split_line = line.strip().split(' ')
            unknown = []
            for i, s in enumerate(split_line):
                if i > 1 and split_line[i - 1] == '/' and s != "ROOT" and s.strip(')') not in words:
                    unknown.append(s.strip(')'))
            output_file.write(line)
            line = graphs.readline()
        output_file.close()


if __name__ == '__main__':
    if arguments.grammar is None:
        print("Proper usage:\n"
              "python parse_irtg.py --grammar <irtg_path> [--definitions_json <graph_path>]", file=sys.stderr)
        raise Exception()
    irtg_path = arguments.grammar
    graph_path = arguments.definitions_json
    words = get_words(irtg_path)
    # if graph_path.endswith('json'):
    get_graphs_for_words(words, graph_path, irtg_path)
    # else:
    #     get_relevant_graphs(words, graph_path)
