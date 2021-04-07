from utils import *
from typing import List,Tuple,Callable,Any


class NTerminal:
    def __init__(self, func:Callable[[List], Tuple[Any,List]]):
        self.func = func

    def parse(self, tokens):
        return self.func(tokens)
       
    def pack(self, f):
        def func(tokens):
            (acc, rem) = self.parse(tokens)
            return (f(acc), rem)
        return NTerminal(func=func)

    def caten(self, other:'NTerminal'):
        def func(tokens):
            (acc1, rem) = self.parse(tokens)
            (acc2, rem) = other.parse(rem)
            return ((acc1, acc2), rem)
        return NTerminal(func=func)
    
    def caten_list(self, others:List['NTerminal']):
        epsilon = NTerminal(func=nt_epsilon)
        nts = [self] + others
        f = lambda nt1,nt2: nt1.caten(nt2).pack(concat)
        return foldr(f, epsilon, nts)
    
    def disj(self, other:'NTerminal'):
        def func(tokens):
            try:
                (acc, rem) = self.parse(tokens)
            except NoMatchError:
                (acc, rem) = other.parse(tokens)
            return (acc, rem)
        return NTerminal(func=func)
    
    def disj_list(self, others:List['NTerminal']):
        none = NTerminal(func=nt_none)
        nts = [self] + others
        f = lambda nt1,nt2: nt1.disj(nt2)
        return foldr(f, none, nts)

    def delayed(self, thunk):
        def func(tokens):
            return thunk()(tokens)
        return NTerminal(func=func)
    
    def star(self):
        def func(tokens):
            try:
                (acc1, rem) = self.parse(tokens)
                (acc2, rem) = self.star().parse(rem)
                return (concat((acc1,acc2)), rem)
            except NoMatchError:
                return ([], tokens)
        return NTerminal(func=func)
    
    def plus(self):
        return self.caten(self.star()).pack(concat)

    def guard(self, pred):
        def func(tokens):
            (e, rem) = self.parse(tokens)
            if pred(e):
                return (e, rem)
            else:
                raise NoMatchError()
        return NTerminal(func=func)
    
    def diff(self, other:'NTerminal'):
        def func(tokens):
            result = self.parse(tokens)
            try:
                _ = other.parse(tokens)
            except NoMatchError:
                return result
            raise NoMatchError()
        return NTerminal(func=func)

    def not_followed_by(self, other:'NTerminal'):
        def func(tokens):
            (acc, rem) = self.parse(tokens)
            try:
                _ = other.parse(rem)
            except NoMatchError:
                return (acc, rem)
            raise NoMatchError()
        return NTerminal(func=func)    

    def maybe(self):
        def func(tokens):
            try:
                return self.parse(tokens)
            except NoMatchError:
                return (None, tokens)
        return NTerminal(func=func)
    
    def __or__(self, other:'NTerminal'):
        return self.disj(other)

    def __add__(self, other:'NTerminal'):
        return self.caten(other)
    
    def __invert__(self):
        return self.maybe()

    def __ne__(self, other:'NTerminal'):
        return self.diff(other)

    def __xor__(self, other:'NTerminal'):
        return self.not_followed_by(other)

    def __lshift__(self, other):
        if type(other) != str and type(other) != list:
            raise Exception('When using << operator, LHS is a NT and RHS is the input!')
        return self.parse(other)
    
    def __matmul__(self, f):
        return self.pack(f)

# useful general parsers for working with text

def make_char(eq):
    def func(ch1):
        def pred(ch2):
            return eq(ch1,ch2)
        return NTerminal(nt_const(pred))
    return func

char = make_char(lambda ch1,ch2: ch1 == ch2)

char_ci = make_char(lambda ch1,ch2: ch1.lower() == ch2.lower())

def make_word(char):
    def func(string):
        f = lambda nt1,nt2: nt1.caten(nt2).pack(concat)
        l = [char(c) for c in string]
        epsilon = NTerminal(nt_epsilon)
        return foldr(f, epsilon, l)
    return func

word = make_word(char)

word_ci = make_word(char_ci)

def make_one_of(char):
    def func(string):
        f = lambda nt1,nt2: nt1.disj(nt2)
        l = [char(c) for c in string]
        none = NTerminal(nt_none)
        return foldr(f, none, l)
    return func

one_of = make_one_of(char)

one_of_ci = make_one_of(char_ci)

whitespace = NTerminal(nt_const(lambda c: ord(c) <= 32))

def make_range(leq):
    def func(c1, c2):
        return NTerminal(nt_const(lambda c: leq(c1,c) and leq(c,c2)))
    return func

nt_range = make_range(lambda c1,c2: ord(c1) <= ord(c2))

nt_range_ci = make_range(lambda c1,c2: ord(c1.lower()) <= ord(c2.lower()))

nt_any = NTerminal(nt_const(lambda _: True))

alpha_char_lower = nt_range('a','z')

alpha_char_upper = nt_range('A','Z')

alpha_char_ci = alpha_char_lower | alpha_char_upper

alpha_word_lower = alpha_char_lower.plus() @ list_to_string

alpha_word_upper = alpha_char_upper.plus() @ list_to_string

alpha_word_ci = alpha_char_ci.plus() @ list_to_string

digit = nt_range('0','9')

pos_digit = digit != char('0')

hex_digit = digit | nt_range_ci('a','f')

pos_hex_digit = hex_digit != char('0')