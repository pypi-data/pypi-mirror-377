import json



with open("test_corpus.tsv", "r") as f:
	as_file = [line.replace("\n", "") for line in f.readlines()][1:1000]

as_list_of_annotations = []

for line in as_file:
	try:
		word, lemma, pos, morph = line.split("\t")
	except ValueError:
		print(line.split("\t"))
	as_list_of_annotations.append(
		{"word": word,
	 "lemma": lemma,
	 "pos": pos,
	 "morph": morph}
	)

with open("test_corpus.json", "w") as f:
	json.dump(as_list_of_annotations, f)

exit(0)