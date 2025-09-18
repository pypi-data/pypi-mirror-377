import ast
import sys
sys.path.append('src/')
import CQLEngine.functions as functions
import unittest

def import_test_queries(path):
	with open(path, "r") as f:
		list_of_queries = f.read().splitlines()
	return [line.split("\t") for line in list_of_queries]

def import_match_queries(path):
	with open(path, "r") as f:
		list_of_queries = f.read().splitlines()
	as_splits = [line.split("\t") for line in list_of_queries]
	return [(ast.literal_eval(nodes), query, GT) for nodes, query, GT in as_splits]


class TestFunctions(unittest.TestCase):
	def test_simple_match(self):
		query = ("lemma", "=", "asno")
		test_token = {"lemma": "asno",
					  "pos": "NCMS000",
					  "morph": None,
					  "word": "asnos"}
		self.assertEqual(functions.simple_match(query, test_token), True, "Something is wrong"
																		  "with function `test_simple_match`")

class TestQueries(unittest.TestCase):
	def test_findall_queries(self):
		self.corpus = functions.import_corpus("tests/test_data/test_corpus.json")
		self.queries = import_test_queries("tests/queries_findall.txt")
		self.MyEngine = functions.CQLEngine()
		for query, GT in self.queries:
			GT = ast.literal_eval(GT)
			with self.subTest(query=query, GT=GT):
				self.assertEqual(self.MyEngine.findall(self.corpus, query, debug=False), GT, "Error with findall function")


	def test_match_queries(self):
		self.queries = import_match_queries("tests/queries_match.txt")
		self.MyEngine = functions.CQLEngine()
		for idx, (nodes, query, GT) in enumerate(self.queries):
			with self.subTest(query=query, GT=GT):
				GT = True if GT == "True" else False
				match = self.MyEngine.match(nodes, query, debug=True)
				self.assertEqual(match, GT,
								 msg=f"\nTest {idx + 1} failed.\n"
									 f"Query: {query}\n"
									 f"Nodes: {nodes}\n"
									 f"Match should be {GT}, is {match}")


if __name__ == '__main__':
	unittest.main()