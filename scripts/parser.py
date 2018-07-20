import argparse


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser()
parser.add_argument('--longman', type=str, help='Path to the longman dictionary xml file.')
parser.add_argument('--definitions', type=str, default='definitions.txt',
                    help='Path to the longman definitions (just the definitions in a txt)')
parser.add_argument('--ud_graphs', type=str, default='definitions.graph',
                    help='Path to the UD v2 graphs generated from the definitions')
parser.add_argument('--definitions_json', type=str, default='dictionary.json',
                    help='Path to the json file containing one word, pos, definition, graph in each line')
parser.add_argument('--grammar', type=str, help='Path to the irtg file containing the grammar')
parser.add_argument('--alto', type=str, help='Path to the alto-2.3 jar')
parser.add_argument('--out', type=str, default='4lang.graphs', help='Path to save the 4lang graphs')
parser.add_argument('--add', type=str2bool, default=False, help='Add to the grammar, or replace')
parser.add_argument('--expand', type=str2bool, default=True, help='Expand or abstract graph')
arguments = parser.parse_args()
