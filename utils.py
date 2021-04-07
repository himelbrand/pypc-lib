import functools

def foldl(f, acc, l):
    return functools.reduce(f, l, acc)

def foldr(f, acc, l):
    return functools.reduce(lambda x,y: f(y,x), l[::-1], acc)

def ormap(f, s):
    if len(s) == 0:
        return False
    else:
        return f(s[0]) or ormap(f, s[1:])

def andmap(f, s):
    if len(s) == 0:
        return False
    else:
        return f(s[0]) and ormap(f, s[1:])

class NoMatchError(Exception):
    """ Exception raised for parsing errors.
        Specifically raised when input is not in the language defined by the CFG.

        Attributes:
            remaining -- the remaining tokens
            accepted -- the accepted tokens
            message -- explanation of the error
    """

    def __init__(self, remaining=None, accepted=None, message="No match for input! Parsing failed!"):
        self.remaining = remaining
        self.accepted = accepted
        self.message = message
        super().__init__(self.message)

def nt_none(_):
    raise NoMatchError()

def nt_epsilon(tokens):
    return ([],tokens)

def nt_EOF(tokens):
    if len(tokens):
        raise NoMatchError()
    else:
        return ([], [])

def concat(a):
    x,y = a
    if type(x) != 'list':
        x = [x]
    return x+y

def nt_const(pred):
    def f(tokens):
        if len(tokens) and pred(tokens[0]):
            return (tokens[0], tokens[1:])
        else:
            raise NoMatchError()
    return f

def list_to_string(l):
    return ''.join(l)