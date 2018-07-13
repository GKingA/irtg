import sys
import json
import spacy


def parse_tags(dictionary_file):
    original = []
    corrected = []
    pos = ['X']
    nlp = spacy.load('en')
    with open(dictionary_file, 'r') as words:
        line = words.readline()
        while line is not None and line != '':
            json_line = json.loads(line)
            original.append(json_line)
            if json_line['pos'] not in pos and json_line['pos'] != '-':
                pos.append(json_line['pos'])
            line = words.readline()
        pos.sort()
        print(pos)
    for json_line in original:
        new_json_line = json_line.copy()
        new_definitions = []
        if json_line['pos'] == '-':
            abb = ''
            if 'abbreviation of' in json_line['def']:
                abb = json_line['def'].split(' abbreviation of ')[1].split(' ')[0]
            elif 'short form' in json_line['def']:
                if ' short form of ' in json_line['def']:
                    abb = json_line['def'].split(' short form of ')[1].split(' ')[0]
                else:
                    abb = json_line['def'].split(' short form for ')[1].split(' ')[0]
            elif 'past' in json_line['def']:
                if 'past participle' in json_line['def']:
                    abb = json_line['def'].split(' past participle of ')[1].split(' ')[0]
                else:
                    abb = json_line['def'].split(' past tense of ')[1].split(' ')[0]
            elif ' present ' in json_line['def']:
                if 'present participle' in json_line['def']:
                    abb = json_line['def'].split(' present participle of ')[1].split(' ')[0]
                else:
                    abb = json_line['def'].split(' present tense of ')[1].split(' ')[0]
            elif 'spelling of' in json_line['def']:
                abb = json_line['def'].split(' spelling of ')[1].split(' ')[0]
            elif 'plural of' in json_line['def']:
                abb = json_line['def'].split(' plural of ')[1].split(' ')[0]
            elif json_line['text'] == 'cc':
                new_json_line['pos'] = 'NOUN'
            elif json_line['text'].startswith('Mr'):
                new_json_line['pos'] = 'PROPN'
            else:
                new_json_line['pos'] = [t.pos_ for t in nlp(json_line['text'])][0]
            if abb != '':
                for o in original:
                    if o['text'] == abb:
                        new_definitions.append({'text': json_line['text'], 'pos': o['pos'],
                                                'def': o['def'], 'graph': o['graph']})
            if new_json_line['pos'] == '-':
                new_json_line['pos'] = [t.pos_ for t in nlp(json_line['text'])][0]
        if new_definitions != []:
            corrected += new_definitions
        else:
            corrected.append(new_json_line)
    return corrected


def parse_irtg_tags(irtg_file):
    with open(irtg_file, 'r') as words:
        pairs = []
        pos = []
        line = words.readline()
        while line is not None and line != "":
            if '->' in line and not line.startswith('X') and not line.startswith('S') and not line.startswith('//'):
                word_pos = line.strip('\n').split(' -> ')[0]
                word = line.strip('\n').split(' -> ')[1]
                if word_pos not in pos:
                    pos.append(word_pos)
                pairs.append((word, word_pos))
            line = words.readline()
        pos.sort()
        print(pos)
        return pairs


def pair_up(corrected_dict, irtg_pairs):
    dict_pos_to_irtg_pos = {
        'adj': 'ADJ',
        'adv': 'ADV',
        'auxiliary verb': 'AUX',
        'conjunction': ['CCONJ', 'SCONJ'],
        'definite article': 'DET',
        'determiner': 'DET',
        'indefinite article': 'DET',
        'interjection': 'INTJ',
        'modal verb': 'AUX',
        'n': ['NOUN', 'PROPN'],
        'noun': ['NOUN', 'PROPN'],
        'number': 'NUM',
        'possessive pron': 'PRON',
        'prep': 'ADP',
        'pron': 'PRON',
        'suffix': 'ADP',
        'v': ['VERB', 'AUX']
    }
    result_dict = []
    good_words = []
    success = []
    exception = open("exceptions.txt", 'w')
    reject = open("rejects.txt", 'w')
    cntr = 0
    for word, pos in irtg_pairs:
        matches = []
        manipulated_word = word[:]
        manipulated_word.replace('PERIOD', '.').replace('HYPHEN', '-').replace('DIGIT', '0').replace('PER', '/').replace('SEMICOLON', ';').replace('COLON', ',')
        for dict_ in corrected_dict:
            if (manipulated_word == dict_['text'] or (manipulated_word.endswith('s') and
                                                     manipulated_word[:-1] == dict_['text']) \
                    or manipulated_word.lower() == dict_['text'] or manipulated_word.capitalize() == dict_['text']) \
                    and ':nn' not in dict_['graph']:
                matches.append(dict_)
                if (word, pos) not in good_words:
                    good_words.append((word, pos))
                if (dict_['pos'] in dict_pos_to_irtg_pos and (dict_pos_to_irtg_pos[dict_['pos']] == pos
                                                              or pos in dict_pos_to_irtg_pos[dict_['pos']])) \
                        or (dict_['pos'].upper() == pos):
                    result_dict.append({'text': word, 'pos': pos, 'def': dict_['def'], 'graph': dict_['graph']})
                    success.append((word, pos))
                    break
        if (word, pos) in good_words and (word, pos) not in success:
            print(word, pos, matches, file=exception)
            cntr += 1
        if (word, pos) not in good_words:
            print(word, pos, file=reject)
    print(len(result_dict), cntr, len(irtg_pairs))
    return result_dict


def write_out(dict_, filename):
    with open(filename, 'w') as writer:
        for element in dict_:
            print(json.dumps(element), file=writer)


def get_graphs(filename, new_filename, field):
    graphs = []
    with open(filename, 'r') as data:
        json_data = data.readline()
        while json_data is not None and json_data != '':
            graphs.append(json.loads(json_data)[field])
            json_data = data.readline()
    with open(new_filename, 'w') as writer:
        print("# IRTG unannotated corpus file, v1.0\n"
              "# interpretation graph: de.up.ling.irtg.algebra.graph.GraphAlgebra", file=writer)
        for graph in graphs:
            print(graph, file=writer)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Proper usage:\n"
              "python check_pos.py <dictionary_json> <irtg_file>", file=sys.stderr)
        raise Exception()
    dictionary = sys.argv[1]
    irtg = sys.argv[2]
    corrected_dict = parse_tags(dictionary)
    irtg_pairs = parse_irtg_tags(irtg)
    results = pair_up(corrected_dict, irtg_pairs)
    write_out(corrected_dict, dictionary.replace('.json', '_v2.json'))
    write_out(results, dictionary.replace('.json', '_matched.json'))
    get_graphs(dictionary.replace('.json', '_matched.json'), dictionary.replace('.json', '_matched.graph'), 'graph')
