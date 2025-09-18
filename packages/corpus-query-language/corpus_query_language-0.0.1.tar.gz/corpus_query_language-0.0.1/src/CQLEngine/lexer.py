import ply.lex as lex
import copy

class Lexer(object):
    tokens = (
        'RANGE',
        'DISTANCE',
        'RPAREN',
        'LPAREN',
        'OR',
        'RSQBRACK',
        'LSQBRACK',
        'EQUAL',
        'AND',
        'QUOTE',
        'LEMMA',
        'POS',
        'MORPH',
        'NUMBER',
        'WORD',
        'NOTEQUAL',
        'INTERROGATIVE',
        'PLUS',
        'VALUE',
        'ASTERISK',
    )
    t_OR = r"\|"
    t_LSQBRACK = r"\["
    t_RSQBRACK = r"\]"
    t_EQUAL = r"\="
    t_NOTEQUAL = r"\!="
    t_AND = r"&"
    t_INTERROGATIVE = r"\?"
    t_PLUS = r"\+"
    t_ASTERISK = r"\*"
    t_ignore = ' \t'
    t_LPAREN = r"\("
    t_RPAREN = r"\)"

    def t_DISTANCE(self, t):
        r'\[\s*\]\{[0-9]*\s*,\s*[0-9]+\}'
        range = t.value.split("]")[-1][1:-1].split(',')
        try:
            t.value = (int(range[0].strip()), int(range[1].strip()))
        except ValueError:
            t.value = (0, int(range[1].strip()))
        return t

    def t_RANGE(self, t):
        r'\{[0-9]*\s*,\s*[0-9]+\}'
        numbers = t.value[1:-1].split(',')
        try:
            t.value = (int(numbers[0].strip()), int(numbers[1].strip()))
        except ValueError:
            t.value = (0, int(numbers[1].strip()))
        return t

    def t_LEMMA(self, t):
        r'lemma'
        return t

    def t_POS(self, t):
        r'pos'
        return t

    def t_MORPH(self, t):
        r'morph'
        return t

    def t_WORD(self, t):
        r'word'
        return t

    def t_VALUE(self, t):
        r"'[^']+'"
        t.value = t.value[1:-1]
        return t

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def tokenize(self, query, debug):
        self.lexer = lex.lex(module=self)
        self.lexer.input(query)

        if debug:
            debug_lexer = copy.deepcopy(self.lexer)
            while True:
                tok = debug_lexer.token()
                if not tok:
                    break  # No more input
                print(tok)

    def token(self):
        return self.lexer.token()

