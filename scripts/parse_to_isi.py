import sys
import subprocess


def main(stanford_parser, converter, input_filename, output_filename):
    if not stanford_parser.endswith("stanford-parser"):
        '/'.join([stanford_parser, "stanford-parser"])

    conll_file = open("conll_out.txt", 'w')
    command = "java -cp {0} edu.stanford.nlp.trees.EnglishGrammaticalStructure -parserFile englishPCFG.ser.gz " \
              "-sentFile {1} -basic -keepPunct -conllx".format(stanford_parser, input_filename).split(' ')
    subprocess.call(command, stdout=conll_file)
    conll_file.close()

    convert_file = open("convert_file.txt", 'w')
    command3 = "python3 {0}/convert.py conll_out.txt".format(converter).split(' ')
    subprocess.call(command3, stdout=convert_file)
    convert_file.close()

    output_file = open(output_filename, 'w')
    command2 = "python dep_to_isi.py convert_file.txt".split(' ')
    subprocess.call(command2, stdout=output_file)
    output_file.close()


if __name__ == '__main__':
    try:
        stanford_ = sys.argv[1]
        converter_ = sys.argv[2]
        input_ = sys.argv[3]
        output_ = sys.argv[4]
        main(stanford_, converter_, input_, output_)
    except IndexError:
        print("Proper usage:\npython parse_to_isi.py <path_to_stanford_parser> <converter_path> "
              "<input_text_file> <output_graph_file>")
