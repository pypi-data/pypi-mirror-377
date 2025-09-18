import re
import json
import CQLEngine.parser as parser
import CQLEngine.lexer as lexer
import CQLEngine.engine as engine


class CQLEngine():
	def findall(self, corpus:list[dict], query:str, verbose:bool=True,  debug:bool=False) -> list[tuple[int, int]]:
		"""
			This function checks if a query matches some text, and returns the start and end span.
			:param query: a CQL query
			:param corpus: the annotated text as a list of dictionnaries containing the annotations (lemma, pos, morph, word)
			:return: a list of tuples with the start and end position.
			"""
		query_ast = build_grammar(debug=debug, query=query)
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
		query_ast = build_grammar(debug=debug, query=query)
		result = engine.parse_corpus(query_ast, corpus, mode="match", debug=debug)
		if verbose:
			print(f"\n---\nResults for query {query}:")
			print(result)
		return result


def build_grammar(debug, query):
	MyLexer = lexer.Lexer()
	MyLexer.tokenize(query, debug=debug)
	MyParser = parser.Parser(MyLexer, debug=debug)
	if debug:
		print(MyParser.ast)
	return MyParser.ast


def simple_match(query:tuple, text_token:dict) -> bool:
	"""
	This function checks if a simple query matches a token.
	:param query: the tuple containing the annotation to match and its value as a regexp expression
	:param text_token: the text token as a dict of annotations
	:return:
	"""
	annotation, equality, regexp = query
	compiled_regexp = re.compile(fr"^{regexp}$")
	if re.match(compiled_regexp, text_token[annotation]):
		if equality == "=":
			return True
		else:
			return False
	else:
		if equality == "!=":
			return True
		else:
			return False

def alternative_match(queries:list[tuple], text_token:dict) -> bool:
	"""
	This function matches an alternative
	:param queries: the list of queries to match
	:param text: the text token as a dict of annotations
	:return: boolean
	"""
	for query in queries:
		if 'and' in query:
			all_matches = []
			for item in query[1:]:
				if simple_match(item, text_token):
					all_matches.append(True)
				else:
					all_matches.append(False)
			if all([item is True for item in all_matches]):
				return True
			else:
				print("False")
				return False
		else:
			annotation, equality, regexp = query
			compiled_regexp = re.compile(fr"^{regexp}$")
			if re.match(compiled_regexp, text_token[annotation]):
				if equality == "=":
					return True
				else:
					return False
			else:
				if equality == "!=":
					return True
				else:
					return False
	return False



def import_corpus(path):
	with open(path, "r") as f:
		corpus = json.load(f)
	return corpus