import sys
import json
import subprocess
import os
import check_pos
import re


def generate_4lang(alto_path, graph_path, irtg_path, output):
    command = "java -Xmx2G -cp .:./{0} AltoHomomorphism" \
              " {1} -g {2} -I graph -O fourlang=amr-sgraph" \
              " -o {3} --verbose".format(alto_path, graph_path, irtg_path, output).split()
    subprocess.call(command)


def add_root(fourlang_graph, root):
    fourlang_graph = fourlang_graph.strip(')')
    open_brackets = []
    for i, c in enumerate(fourlang_graph):
        if c == '(':
            open_brackets.append(i)
        elif c == ')':
            open_brackets.remove(open_brackets[-1])
    if '-of' in fourlang_graph:
        open_brackets.reverse()
        before_of = 0
        for bracket_index in open_brackets:
            if fourlang_graph[bracket_index-4:bracket_index-1] == '-of':
                break
            before_of += 1
    else:
        before_of = len(open_brackets) - 1
    fourlang_graph += ')' * before_of
    fourlang_graph += ' :is_a-of (u_0 / '+root+')'
    fourlang_graph += ')' * (len(open_brackets) - before_of)
    return fourlang_graph


def add_root_to_term(fourlang_term, root):
    return "r_gov_root(f_dep(merge(merge(r_gov('({0}<root> / {0})'), '(g<gov> :is_a (d<dep>))'), " \
           "r_dep({1}))))".format(root, fourlang_term)


def make_json(fourlang, json_, output_json):
    with open(fourlang, 'r') as graphs:
        out = []
        jsonl = open(json_, 'r')
        line0 = graphs.readline()
        line1 = graphs.readline()
        line2 = graphs.readline()
        json_line = jsonl.readline()
        while line0 is not None and line1 is not None and line0 != '' and line1 != '' \
                and json_line is not None and json_line != '':
            json_line_parsed = json.loads(json_line)
            if line0.strip() != 'null':
                out.append({'text': json_line_parsed['text'], 'pos': json_line_parsed['pos'],
                            'fourlang': add_root(line1.strip(), json_line_parsed['text']),
                            'term': add_root_to_term(line2.strip(), json_line_parsed['text'])})
            line0 = graphs.readline()
            line1 = graphs.readline()
            line2 = graphs.readline()
            json_line = jsonl.readline()
        jsonl.close()
        check_pos.write_out(out, output_json)
    # check_pos.get_graphs(output_json, output_json.replace('.json', '.graphs'), 'fourlang')


def parse_fourlang_json(fourlang_json):
    fourlang_list = []
    with open(fourlang_json, 'r') as fourlang:
        json_line = fourlang.readline()
        while json_line is not None and json_line != '':
            fourlang_list.append(json.loads(json_line))
            json_line = fourlang.readline()
    return fourlang_list


def make_irtg(fourlang_json, irtg_path):
    with open(irtg_path.replace('.irtg', '_experiment.irtg'), 'w') as experiment_irtg:
        original_irtg = open(irtg_path, 'r')
        fourlang = parse_fourlang_json(fourlang_json)
        for i in range(3):
            experiment_irtg.write(original_irtg.readline())
        line0 = original_irtg.readline()
        line1 = original_irtg.readline()
        line2 = original_irtg.readline()
        new_line = original_irtg.readline()
        while line0 is not None and line0 != '':
            if '->' in line0 and not line0.startswith('X') and not line0.startswith('S') and not line0.startswith('//'):
                pos = line0.strip('\n').split(' -> ')[0]
                word = line0.strip('\n').split(' -> ')[1]
                for fourlang_line in fourlang:
                    if fourlang_line['pos'] == pos and fourlang_line['text'] == word:
                        line2 = "[fourlang] {0}\n".format(fourlang_line['term'])
                        break
                line0 = line0.replace('\n', '_'+pos+'\n')
            experiment_irtg.write(line0)
            experiment_irtg.write(line1)
            experiment_irtg.write(line2)
            experiment_irtg.write(new_line)
            line0 = original_irtg.readline()
            line1 = original_irtg.readline()
            line2 = original_irtg.readline()
            new_line = original_irtg.readline()


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("Proper usage:\n"
              "python generate_4lang.py <path_to_alto-2.3> <graphs_file_with_path> <irtg_file_with_path>"
              " <output_graphs> <output_json>", file=sys.stderr)
        raise Exception()
    alto = sys.argv[1]
    graph = sys.argv[2]
    irtg = sys.argv[3]
    out = sys.argv[4]
    json_l = sys.argv[5]
    if not os.path.isfile(out):
        generate_4lang(alto, graph, irtg, out)
    make_json(out, json_l, json_l.replace('.json', '_fourlang.json'))
    make_irtg(json_l.replace('.json', '_fourlang.json'), irtg)
