//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by Fernflower decompiler)
//

import com.beust.jcommander.DynamicParameter;
import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;
import de.saar.basic.StringTools;
import de.up.ling.irtg.Interpretation;
import de.up.ling.irtg.InterpretedTreeAutomaton;
import de.up.ling.irtg.TreeWithInterpretations;
import de.up.ling.irtg.algebra.Algebra;
import de.up.ling.irtg.automata.TreeAutomaton;
import de.up.ling.irtg.automata.coarse_to_fine.CoarseToFineParser;
import de.up.ling.irtg.automata.coarse_to_fine.FineToCoarseMapping;
import de.up.ling.irtg.automata.coarse_to_fine.GrammarCoarsifier;
import de.up.ling.irtg.automata.language_iteration.SortedLanguageIterator;
import de.up.ling.irtg.automata.pruning.NoPruningPolicy;
import de.up.ling.irtg.automata.pruning.PruningPolicy;
import de.up.ling.irtg.codec.AlgebraStringRepresentationOutputCodec;
import de.up.ling.irtg.codec.InputCodec;
import de.up.ling.irtg.codec.OutputCodec;
import de.up.ling.irtg.corpus.Corpus;
import de.up.ling.irtg.corpus.CorpusReadingException;
import de.up.ling.irtg.corpus.Instance;
import de.up.ling.irtg.util.Util;
import de.up.ling.tree.ParseException;
import de.up.ling.tree.Tree;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

public class AltoHomomorphism {
    private static JCommander jc;

    public AltoHomomorphism() {
    }

    public static void main(String[] args) throws IOException, CorpusReadingException, Exception {
        AltoHomomorphism.CmdLineParameters param = new AltoHomomorphism.CmdLineParameters();
        jc = new JCommander(param, args);
        if (param.help) {
            usage((String)null);
        }

        if (param.inputFiles.isEmpty()) {
            usage("No input files specified.");
        }

        if (param.grammarName == null) {
            usage("No grammar specified.");
        }

        if (param.inputInterpretations == null) {
            usage("No input interpretations specified.");
        }

        InputCodec<InterpretedTreeAutomaton> icGrammar = InputCodec.getInputCodecByNameOrExtension(param.grammarName, (String)null);
        InterpretedTreeAutomaton irtg = (InterpretedTreeAutomaton)icGrammar.read(new FileInputStream(param.grammarName));
        List<String> interpretations = Arrays.asList(param.inputInterpretations.split(","));
        List<String> outputInterpretations = new ArrayList(param.outputCodecs.keySet());
        String firstInterp = (String)interpretations.get(0);
        Algebra firstAlgebra = irtg.getInterpretation(firstInterp).getAlgebra();
        PrintWriter out = new PrintWriter(new FileWriter(param.outCorpusFilename));
        Map<String, OutputCodec> ocForInterpretation = new HashMap();
        Iterator var14 = outputInterpretations.iterator();

        String ctfInterpretation;
        while(var14.hasNext()) {
            ctfInterpretation = (String)var14.next();
            String ocName = (String)param.outputCodecs.get(ctfInterpretation);
            OutputCodec oc = null;
            if ("alg".equals(ocName)) {
                Interpretation i = irtg.getInterpretation(ctfInterpretation);
                oc = new AlgebraStringRepresentationOutputCodec(i.getAlgebra());
            } else {
                oc = OutputCodec.getOutputCodecByName(ocName);
            }

            if (oc == null) {
                System.err.println("Could not resolve output codec '" + ocName + "' for interpretation '" + ctfInterpretation + "'.");
                System.exit(1);
            } else {
                ocForInterpretation.put(ctfInterpretation, oc);
            }
        }

        CoarseToFineParser coarseToFineParser = null;
        ctfInterpretation = null;
        if (param.ctf != null) {
            if (interpretations.size() != 1) {
                System.err.println("Coarse-to-fine parsing only supports a single input interpretation.");
                System.exit(1);
            }

            System.err.printf("Reading fine-to-coarse symbol map from %s ...\n", param.ctf);
            ctfInterpretation = (String)interpretations.iterator().next();
            coarseToFineParser = makeCoarseToFineParserFromFile(irtg, ctfInterpretation, param.ctf, 1.0E-4D);
        }

        long overallStart = System.nanoTime();
        Iterator var39 = param.inputFiles.iterator();

        while(var39.hasNext()) {
            String filename = (String)var39.next();
            Corpus corpus = irtg.readCorpus(new FileReader(filename));
            System.err.println("Processing " + filename + " (" + corpus.getNumberOfInstances() + " instances) ...");
            int width = (int)Math.ceil(Math.log10((double)corpus.getNumberOfInstances()));
            String formatString = "%0" + width + "d [%-50.50s] ";
            int pos = 1;

            for(Iterator var24 = corpus.iterator(); var24.hasNext(); System.err.println()) {
                Instance inst = (Instance)var24.next();
                Tree<String> dt = null;
                ArrayList<Tree<String>> trees = null;
                System.err.printf(formatString, pos++, firstAlgebra.representAsString(inst.getInputObjects().get(firstInterp)));
                long start = System.nanoTime();
                if (param.ctf == null && param.viterbi != null) {
                    dt = parseViterbi(irtg, inst, interpretations);
                } else if (param.ctf != null) {
                    dt = parseCtf(coarseToFineParser, inst, ctfInterpretation);
                }
                else {
                    trees = parse(irtg, inst, interpretations);
                }

                System.err.print(Util.formatTimeSince(start));
                if (trees == null) {
                    out.println(dt);
                    getResults(irtg, dt, outputInterpretations, out, ocForInterpretation);
                    if (param.blankLinkes) {
                        out.println();
                    }
                }
                else {
                    for(Tree<String> tree: trees) {
                        out.println(tree);
                        getResults(irtg, tree, outputInterpretations, out, ocForInterpretation);
                    }
                    out.println();
                }

                out.flush();
            }
        }

        out.flush();
        out.close();
        System.err.println("Done, total time: " + Util.formatTimeSince(overallStart));

    }

    private static Map getResults(InterpretedTreeAutomaton irtg, Tree<String> dt, List<String> outputInterpretations,
                                  PrintWriter out, Map<String, OutputCodec> ocForInterpretation) {
        Map results = null;
        try {
            results = irtg.interpret(dt);
            Iterator var30 = outputInterpretations.iterator();

            while(var30.hasNext()) {
                String interp = (String)var30.next();
                if (dt == null) {
                    out.println("<null>");
                    out.println("<null>");
                } else {
                    OutputCodec oc = (OutputCodec)ocForInterpretation.get(interp);
                    out.println(oc.asString(results.get(interp)));
                    TreeWithInterpretations twi = irtg.interpretWithPointers(dt);
                    out.println(twi.getInterpretation(interp).getHomomorphicTerm().toString());
                }
            }
        } catch (Exception var36) {
            System.err.printf(" ** %s", var36.getMessage());
        }
        return results;
    }

    private static CoarseToFineParser makeCoarseToFineParserFromFile(InterpretedTreeAutomaton irtg, String interpretation, String ftcMapFilename, double theta) throws FileNotFoundException, IOException, ParseException {
        FineToCoarseMapping ftc = GrammarCoarsifier.readFtcMapping(StringTools.slurp(new FileReader(ftcMapFilename)));
        return new CoarseToFineParser(irtg, interpretation, ftc, theta);
    }

    private static Tree<String> parseViterbi(InterpretedTreeAutomaton irtg, Instance inst, List<String> interpretations) {
        TreeAutomaton chart = irtg.parseInputObjects(inst.getRestrictedInputObjects(interpretations));
        Tree<String> dt = chart.viterbi();
        return dt;
    }

    private static ArrayList<Tree<String>> parse(InterpretedTreeAutomaton irtg, Instance inst, List<String> interpretations) {
        TreeAutomaton chart = irtg.parseInputObjects(inst.getRestrictedInputObjects(interpretations));
        ArrayList<Tree<String>> trees = new ArrayList<>();
        SortedLanguageIterator sortedLanguageIterator = (SortedLanguageIterator)chart.sortedLanguageIterator();
        int maxIterations = 10;
        int i = 0;
        while (sortedLanguageIterator.hasNext() && i < maxIterations) {
            Tree<String> dt = irtg.getAutomaton().getSignature().resolve(sortedLanguageIterator.next().getTree());
            i++;
            trees.add(dt);
        }
        return trees;
    }

    public static Tree<String> parseCtf(CoarseToFineParser ctfp, Instance inst, String interpretation) {
        Object inp = inst.getInputObjects().get(interpretation);
        TreeAutomaton chart = ctfp.parseInputObject(inp);
        Tree<String> dt = chart.viterbi();
        return dt;
    }

    private static void usage(String errorMessage) {
        if (jc != null) {
            if (errorMessage != null) {
                System.out.println(errorMessage);
            }

            jc.setProgramName("java -cp <alto.jar> de.up.ling.irtg.script.ParsingEvaluator <inputfiles>");
            jc.usage();
            if (errorMessage != null) {
                System.exit(1);
            } else {
                System.exit(0);
            }
        }

    }

    private static class CmdLineParameters {
        @Parameter
        public List<String> inputFiles;
        @Parameter(
                names = {"--grammar", "-g"},
                description = "IRTG to be used in parsing."
        )
        public String grammarName;
        @Parameter(
                names = {"--input-interpretations", "-I"},
                description = "Comma-separated list of interpretations from which inputs are taken."
        )
        public String inputInterpretations;
        @Parameter(
                names = {"--out-corpus", "-o"},
                description = "Filename to which the parsed corpus will be written."
        )
        public String outCorpusFilename;
        @DynamicParameter(
                names = {"-O"},
                description = "Output interpretations with their output codecs (e.g. -Ostring=toString). As special case, use -Ostring=alg to use the algebra's default string representation."
        )
        public Map<String, String> outputCodecs;
        @Parameter(
                names = {"--blank-lines", "-b"},
                description = "Insert a blank line between any two output instances."
        )
        public boolean blankLinkes;
        @Parameter(
                names = {"--ctf"},
                description = "Perform coarse-to-fine parsing with the given CTF map file."
        )
        public String ctf;
        @Parameter(
                names = {"--viterbi"},
                description = "Perform viterbi parsing."
        )
        public String viterbi;
        @Parameter(
                names = {"--verbose"},
                description = "Print some debugging output."
        )
        public boolean verbose;
        @Parameter(
                names = {"--help"},
                help = true,
                description = "Prints usage information."
        )
        private boolean help;

        private CmdLineParameters() {
            this.inputFiles = new ArrayList();
            this.grammarName = null;
            this.inputInterpretations = null;
            this.outCorpusFilename = "out.txt";
            this.outputCodecs = new HashMap();
            this.blankLinkes = false;
            this.ctf = null;
            this.viterbi = null;
            this.verbose = false;
        }
    }
}
