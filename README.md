# irtg
## Python scripts
### graph_generator.py
The code expects the longman dictionary as its input and generates UD v2 graphs for every definition in the dictionary. The results are saved in 3 different files. A text file for the definitions, a graph file for the UD graphs and a json file which contains a word its pos tag, definition and UD graph in every line.

Usage:

python graph_generator.py --longman <dictionary_xml> [--definitions <definitions_output>] [--ud_graphs <ud_graphs>] [--definitions_json <dictionary_output_json>]

### parse_irtg.py
The code expects an irtg (grammar) file and a previously generated json as its input. It modifies the given irtg file so it contains every word from the dictionary and from their definitions.

Usage:

python parse_irtg.py --grammar <irtg_path> [--definitions_json <dictionary_json>]

### check_pos.py
The code expects an irtg (grammar) file and a previously generated json as its input. It generates a matched file containing one definition for each word in the grammar with a matching pos tag.

Usage:

python check_pos.py --grammar <irtg_path> [--definitions_json <dictionary_json>]

### generate_4lang.py
/ Under refactor /

The code generates a new grammar file with the 4lang graphs of the definitions.

Usage:

python generate_4lang.py <path_to_alto-2.3> <graphs_file_with_path> <irtg_file_with_path> <output_graphs> <output_json>
