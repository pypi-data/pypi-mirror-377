import ply.yacc as yacc
import CQLEngine.lexer as lexer



# API functionnalities.

class Parser(lexer.Lexer):
    tokens = lexer.Lexer.tokens

    def p_or_queries(self, p):
        '''
        queries : LPAREN query OR query RPAREN
        | queries LPAREN query OR query RPAREN
        '''
        if len(p) == 6:
            p[0] = [('or', p[2], p[4])]
        else:
            p[0] = p[1] + [('or', p[3], p[5])]

    def p_queries(self, p):
        '''queries : query
                   | queries query
                   | queries DISTANCE query'''
        if len(p) == 2:
            p[0] = [p[1]]  # Single query
        elif len(p) == 3:
            p[0] = p[1] + [p[2]]  # Append the new query to the list
        else:
            p[0] = p[1] + [('distance', p[2])] + [p[3]]


    def p_query(self, p):
        '''query : bracketed_query'''
        p[0] = p[1]


    def p_bracketed_query(self, p):
        'bracketed_query : LSQBRACK query_content RSQBRACK'
        p[0] = p[2]

    def p_ling_equality(self, p):
        '''query_atom : LEMMA EQUAL VALUE
         | POS EQUAL VALUE
         | MORPH EQUAL VALUE
         | WORD EQUAL VALUE
         | LEMMA NOTEQUAL VALUE
         | POS NOTEQUAL VALUE
         | MORPH NOTEQUAL VALUE
         | WORD NOTEQUAL VALUE'''
        if p[2] == "=":
            if p[1] == "lemma":
                p[0] = ('lemma', '=', p[3])
            elif p[1] == "pos":
                p[0] = ('pos', '=', p[3])
            elif p[1] == "morph":
                p[0] = ('morph', '=', p[3])
            elif p[1] == "word":
                p[0] = ('word', '=', p[3])
        else:
            if p[1] == "lemma":
                p[0] = ('lemma', '!=', p[3])
            elif p[1] == "pos":
                p[0] = ('pos', '!=', p[3])
            elif p[1] == "morph":
                p[0] = ('morph', '!=', p[3])
            elif p[1] == "word":
                p[0] = ('word', '!=', p[3])



    def p_subquery_and_subquery(self, p):
        '''query_content : query_atom
        | query_atom AND query_atom
        | query_atom AND query_atom AND query_atom
        | query_atom AND query_atom AND query_atom AND query_atom'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = ('and', p[1], p[3])
        elif len(p) == 6:
            p[0] = ('and', p[1], p[3], p[5])
        elif len(p) == 8:
            p[0] = ('and', p[1], p[3], p[5], p[7])

    def p_one_or_zero(self, p):
        'queries : queries query INTERROGATIVE'
        p[0] = p[1] + [('?', p[2])]

    def p_error(self, p):
        if p:
            print(f"Erreur de syntaxe à '{p.value}'")
        else:
            print("Erreur de syntaxe : fin de fichier inattendue")



    def __init__(self, lexer, debug):
        self.lexer = lexer
        self.parser = yacc.yacc(module=self, start='queries', debug=debug)
        self.ast = self.parser.parse(lexer=self.lexer, tracking=True, debug=debug)




