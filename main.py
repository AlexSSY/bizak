import re


class Foo:
    def __init__(self, string: str = ''):
        self.string = string if isinstance(string, str) else ''
        self.spec_fymbols_pattern = r'[.,?!]'
        self.words = re.sub(self.spec_fymbols_pattern, '', self.string).split(' ')

    def longest(self) -> str:
        return sorted(self.words, key=len, reverse=True)[0]
    
    def most_rated(self) -> str:
        word_rating = {}
        for word in self.words:
            rating = word_rating.get(word, 1)
            word_rating[word] = rating + 1
        return sorted(word_rating.items(), key=lambda t: t[-1], reverse=True)[0][0]
    
    def spcified_symbols(self) -> str:
        return len([i for i in self.string if re.match(self.spec_fymbols_pattern, i)])
    
    def polyndroms(self) -> str:
        return len([i for i in self.words if i == ''.join(reversed(i))])


Foo('abc abcdef abcde, ab').longest() == 'abcdef'
Foo('abc abcdef abcde, ab abc').most_rated() == 'abc'
Foo('abc abcdef abcde, ab abc').spcified_symbols() == 1
Foo('abc abcdef poop, huh, ab abc').polyndroms() == 2

Foo('').longest() == ''
Foo('').most_rated() == ''
Foo('').spcified_symbols() == 0
Foo('').polyndroms() == 0

Foo(None).longest() == ''
Foo(None).most_rated() == ''
Foo(None).spcified_symbols() == 0
Foo(None).polyndroms() == 0

Foo(3).longest() == ''
