import CQLEngine.functions as functions


def parse_corpus(ast, corpus, mode, debug):
	match = False
	text_end = False
	tree_index = 0
	text_index = 0


	ast_length = len(ast)
	if debug:
		for item in ast:
			print(item)
		print(f"{ast_length} items to match.")

	all_spans = []
	matches = False
	first_matching_index = None
	current_initial_state = 0

	analysis_list = ['lemma', 'pos', 'morph', 'word']

	# Text-directed engine.
	while text_end == False:

		# On teste si on est en bout de texte.
		if len(corpus) == text_index and tree_index != ast_length:
			if debug:
				print("End of text a. Exiting.")
			text_end = True
			if mode == "match":
				return False
			break


		# Si on matche la longueur de notre arbre
		if tree_index == ast_length:
			match = True
			all_spans.append((first_matching_index, text_index))
			if debug:
				print(f"Appending {(first_matching_index, text_index)} to spans.")
				print(tree_index)
				print(ast_length)
			first_matching_index = None
			if match is True and mode == "match":
				return True
			text_index += 1
			tree_index = 0
			matches = True
			# La boucle s'arrête là

		if debug:
			print("-")
			print(corpus[text_index])
			print(f"Text index: {text_index}")
			print(f"Tree index: {tree_index}")
			print(f"Ast length: {ast_length}")
		current_query = ast[tree_index]
		operator = current_query[0]
		if debug:
			print(f"Current query: {current_query}")
		if operator in analysis_list:
			if debug:
				print(f"{operator} in list of analysis")
				print(len(corpus))
				print(text_index)
			if functions.simple_match(current_query, corpus[text_index]):
				if debug:
					print("Found you a. Going forward on tree and text.")
					print(f"First match is {text_index}")
				if not first_matching_index:
					first_matching_index = text_index
				tree_index += 1
				text_index += 1
			else:
				tree_index = 0
				current_initial_state = current_initial_state + 1
				text_index = current_initial_state
				first_matching_index = None
				if debug:
					print(f"Nothing. Going forward on text a, at state {text_index}")
		else:
			if debug:
				print(f"{operator} operator")
			if operator == "or":
				if functions.alternative_match(current_query[1:], corpus[text_index]):
					if debug:
						print("Found your alternative. Going forward on tree and text.")
						print(f"First match is {text_index}")
					if not first_matching_index:
						first_matching_index = text_index
					tree_index += 1
					text_index += 1
				else:
					if debug:
						print("Nothing. Going forward on text b.")
					tree_index = 0
					current_initial_state = current_initial_state + 1
					text_index = current_initial_state
			elif operator == "distance":
				if debug:
					print(f"Found distance operator: {current_query}")
				submatch = False
				for i in range(current_query[1][0], current_query[1][1]):
					if debug:
						print(f"\t{text_index}: Looking for {ast[tree_index + 1]} in position {text_index}")
					if len(corpus) == text_index:
						break
					if functions.simple_match(ast[tree_index + 1], corpus[text_index]):
						submatch = True
						tree_index += 2
						if debug:
							print("\tFound you b")
						text_index += 1
						break
					else:
						if debug:
							print("\tNo luck")
					text_index += 1
				if submatch is False:
					tree_index = 0
					current_initial_state = current_initial_state + 1
					text_index = current_initial_state
					first_matching_index = None
			elif operator == "and":
				all_matches = []
				for item in current_query[1:]:
					if functions.simple_match(item, corpus[text_index]):
						all_matches.append(True)
					else:
						all_matches.append(False)
				if all([item is True for item in all_matches]):
					if not first_matching_index:
						first_matching_index = text_index
					tree_index += 1
					text_index += 1
				else:
					tree_index = 0
					current_initial_state = current_initial_state + 1
					text_index = current_initial_state
			elif operator == "?":
				# Pour l'opérateur "0 ou 1", on vérifie que le token matche.
				# S'il ne matche pas, on passe à la requête suivante sans
				# incrémenter le texte
				if functions.alternative_match(current_query[1:], corpus[text_index]):
					if debug:
						print("Found your alternative. Going forward on tree and text.")
						print(f"First match is {text_index}")
					if not first_matching_index:
						first_matching_index = text_index
					tree_index += 1
					text_index += 1
				else:
					tree_index += 1


	return all_spans