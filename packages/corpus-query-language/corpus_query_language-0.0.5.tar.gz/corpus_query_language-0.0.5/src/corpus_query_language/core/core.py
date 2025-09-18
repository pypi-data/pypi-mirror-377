import corpus_query_language.utils.utils as utils
import corpus_query_language.engine.engine as engine

class CQLEngine():
	"""
	The main class: tokenize a query, parse it, and parse a corpus with 2 main functions:
		- findall
		- match
	"""
	def findall(self, corpus:list[dict], query:str, verbose:bool=True,  debug:bool=False) -> list[tuple[int, int]]:
		"""
			This function checks if a query matches some text, and returns the start and end span.
			:param query: a CQL query
			:param corpus: the annotated text as a list of dictionnaries containing the annotations (lemma, pos, morph, word)
			:return: a list of tuples with the start and end position.
			"""
		query_ast = utils.build_grammar(debug=debug, query=query)
		result = engine.parse_corpus(query_ast, corpus, mode="find", debug=debug)
		if verbose:
			print(f"\n---\nResults for query {query}:")
			print(f"Ast: {query_ast}")
			print(f"Spans: {result}")
		return result


	def match(self, corpus:list[dict], query:str, verbose:bool=True, debug:bool=False) -> bool:
		"""
		This function checks whether a query matches some text, and returns True or False
		:param query: a CQL query
		:param corpus: the annotated text as a list of dictionnaries containing the annotations (lemma, pos, morph, word)
		:return: a boolean
		"""
		query_ast = utils.build_grammar(debug=debug, query=query)
		result = engine.parse_corpus(query_ast, corpus, mode="match", debug=debug)
		if verbose:
			print(f"\n---\nResults for query {query}:")
			print(result)
		return result
