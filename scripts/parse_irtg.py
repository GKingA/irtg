import sys
import json


def get_words(irtg):
    words = []
    with open(irtg, 'r') as irtg_file:
        line = irtg_file.readline()
        while line is not None and line != "":
            if '->' in line and not line.startswith('X') and not line.startswith('S') and not line.startswith('//'):
                words.append(line.strip('\n').split(' -> ')[1])
            line = irtg_file.readline()
    return words


def get_graphs_for_words(words, graph_path, output_path):
    with open(graph_path, 'r') as graphs:
        output_file = open(output_path, 'w')
        words_file = open("words.txt", 'w')
        output_file.write("# IRTG unannotated corpus file, v1.0\n"
                          "# interpretation graph: de.up.ling.irtg.algebra.graph.GraphAlgebra\n")
        line = graphs.readline()
        while line is not None and line != "":
            line_data = json.loads(line.strip())
            if line_data["text"] in words:
                acceptable = True
                for definition in line_data["def"].split(' '):
                    if definition not in words:
                        acceptable = False
                if acceptable:
                    output_file.write(line_data["graph"])
                    output_file.write('\n')
                    words_file.write(line_data["text"] + ': ' + line_data["def"])
                    words_file.write('\n')
            line = graphs.readline()
        output_file.close()
        words_file.close()


def get_relevant_graphs(words, file_name, output_path):
    with open(file_name, 'r') as graphs:
        output_file = open(output_path, 'w')
        line = graphs.readline()
        while line is not None and line != "":
            split_line = line.strip().split(' ')
            allowed = True
            for i, s in enumerate(split_line):
                if i > 1 and split_line[i - 1] == '/' and s != "ROOT" and s.strip(')') not in words:
                    allowed = False
            if allowed:
                output_file.write(line)
            line = graphs.readline()
        output_file.close()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Proper usage:\npython3 parse_irtg.py <irtg_path> <graph_path> <output_path>", file=sys.stderr)
        raise Exception()
    irtg_path = sys.argv[1]
    graph_path = sys.argv[2]
    output_path = sys.argv[3]
    words = get_words(irtg_path)
    if graph_path.endswith('json'):
        get_graphs_for_words(words, graph_path, output_path)
    else:
        get_relevant_graphs(words, graph_path,  output_path)
