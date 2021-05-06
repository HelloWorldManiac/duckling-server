from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer
from pyrsistent import pmap,plist
from toolz.functoolz import thread_last
import re
import pickle

class CityExtractor:
    def __init__(self):
        regstr = open("./Extractors/src/city_regex2",encoding="utf8").read()
        tokenizer = RegexpTokenizer("[А-Яа-я\-]{3,}")
        stemmer = SnowballStemmer('russian')
        
        self.tok = lambda x: tokenizer.tokenize(x)
        self.stem = lambda x: map(stemmer.stem, x)
        self.ex = re.compile(regstr)
        self.dct = pickle.load(open("./Extractors/src/citi_dct.pkl","rb"))
        self._extract =  lambda text: list(thread_last(
                        self.ex.findall(text.lower()),
                        (map, self.tok),
                        (map, self.stem),
                        (map, lambda x: self.dct.get(plist(x)))
                        ))
        
    def extract(self, text):
        return self._extract(text)
