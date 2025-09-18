# Python package project: CQL (Corpus Query Language) parser:
# - parsing of any kind of annotation: word, lemma, pos, morph
# - combination of annotations: [lemma='rey' & pos='NCMP000']
# - one or zero annotations [lemma='rey']?.
# - distance [lemma='rey'][]{,5}[lemma='santo']
# - any regex in the annotation value [lemma='reye?s?']
# - alternatives: [lemma='rey']|[lemma='príncipe'][]{,5}[lemma='santo']
import sys
import CQLEngine.functions as functions

# Takes a list of dicts with the annotations as input. Returns:
# - a list of spans (search_all function)
# - a boolean (match function)



def main():
	query = sys.argv[1]
	corpus = functions.import_corpus("tests/test_data/test_corpus.json")
	MyEngine = functions.CQLEngine()
	MyEngine.findall(corpus, query)
	MyEngine.match(corpus, query)


if __name__ == '__main__':
	main()