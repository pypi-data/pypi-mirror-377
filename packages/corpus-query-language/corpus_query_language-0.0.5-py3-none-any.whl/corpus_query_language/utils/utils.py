import re
import json
import corpus_query_language.language.parser as parser
import corpus_query_language.language.lexer as lexer




def build_grammar(debug:bool, query:str) -> list:
	"""
	This function builds an Abstract Syntax Tree from a query
	:param debug: outputs parsing information
	:param query: the query to build the AST from
	:return: the ast
	"""
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



def import_corpus(path) -> list:
	"""
	Simple JSON file import to dict
	:param path: Path to the JSON file
	:return: the list of dicts
	"""
	with open(path, "r") as f:
		corpus = json.load(f)
	return corpus