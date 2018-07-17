import argparse


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
arguments = parser.parse_args()
