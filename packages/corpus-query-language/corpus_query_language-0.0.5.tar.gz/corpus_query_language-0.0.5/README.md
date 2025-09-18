# Corpus Query Language Engine

## Presentation
This repo hosts the code for a simple 
CQL processor. CQL is a language used for 
linguistics queries over large corporas.

## Pip install

```shell
pip3 install corpus-query-language
```

## Uses

Two main functions are implemented:
- match, for checking if some pattern exists in a corpus (stops at first match). Returns a boolean
- findall, for finding the position of all matching tokens. Returns a list of tuples, with start and end position.

```python
import sys
import corpus_query_language as CQL

query = "Some CQL query"
corpus = CQL.utils.import_corpus("path/to/json/corpus.json")
MyEngine = CQL.core.CQLEngine()
MyEngine.findall(corpus, query)
MyEngine.match(corpus, query)
```

## Implemented CQL functions

- parsing of any kind of annotation classes: `word`, `lemma`, `pos`, `morph`
- combination of annotations: `[lemma='rey' & pos='NCMP000']`
- one or zero annotations `[lemma='rey']?` (partially implemented, may produce errors).
- distance `[lemma='rey'][]{,5}[lemma='santo']`
- any regex in the annotation value `[lemma='reye?s?']`
- alternatives: `([lemma='rey']|[lemma='príncipe'])[]{,5}[lemma='santo']` (may produce errors)