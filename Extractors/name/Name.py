text = 'Александр Сергеевич Пушкин был убит Дантесом'

import dawg, re, pickle
from itertools import chain
from .UdPipeModel import Model
from pyrsistent import plist, pvector
from .utils import _group, _match, replace_text

gen = re.compile('gender=(\w+)\|')
f_gen = re.compile(r'(\w+(?:ова|ева|ая|цка|ска|ина|ана|ава|ена|ица|еца)\b)')
cap = lambda s: s[0].upper() + s[1:]

class NameExtractor:
    def __init__(self, modelpath="./Extractors/src/models/russian-syntagrus-ud-2.5-191206.udpipe"):
        self.M_keys = pickle.load(open("./Extractors/src/musc_dawg.pickle","rb")).keys
        self.F_keys = pickle.load(open("./Extractors/src/fem_dawg.pickle","rb")).keys
        self.F_names_keys = pickle.load(open("./Extractors/src/fem_name_dawg.pickle","rb")).keys
        self.M_names_keys = pickle.load(open("./Extractors/src/musc_name_dawg.pickle","rb")).keys
        self.aft_dct, self.bfr_dct = pickle.load(open('./Extractors/src/repl_dct.pickle','rb'))
        self.model = Model(modelpath)
        self.tag_dct = {}
        self.bfr_dct = {'Алл':'Алла','Ксение':'Ксения','Оксан':'Оксана','Игнатие':'Игнатий','Александер':'Александра','Антонин':'Антонина'}
        self.line = ''
        
    def _check_gen(self, word):
        if word == 'Найди': pass
        word_repl = word[1]
        if word_repl in self.bfr_dct.keys():
            word_repl = self.bfr_dct[word[1]]
        
        if 'Animacy=Anim' in word[2] and word_repl in self.F_names_keys(word_repl): self.tag_dct[word_repl] = 'fem'
            
        if 'Animacy=Anim' in word[2] and word_repl in self.M_names_keys(word_repl): self.tag_dct[word_repl] = 'masc'
            
        if 'Animacy=Anim' in word[2] and word_repl in self.tag_dct.keys():
            return word_repl
        elif 'Animacy=Anim' in word[2] and word_repl not in self.tag_dct.keys():
            self.tag_dct[word_repl] = gen.findall(word[2].lower())[0]
            return word_repl
        else:
            pass
    
    def _repl(self, array):
        return pvector(map(lambda x: self.aft_dct[x] if x in self.aft_dct.keys() else x, array))
    
    def _filter_normalize(self, sent): 
        val = list(filter(None,list(map(lambda x: self._check_gen(x) ,self.model.extract('текст а ' + sent)))))
        return plist(val)
    
    def _strmatch(self, element, text):
        del_ch = lambda x: 2 if len(x) > 3 else 1
        spn = re.search(str(element[:-del_ch(element)])+'\w{0,4}', self.line)
        len_txt = len(text) - len(self.line)
        self.line = self.line[spn.end():]
        return tuple(map(lambda x: x+len_txt, spn.span()))
    
    def _repl_dct(self, array, text):
        if 'fem' in list(map(lambda x: self.tag_dct[x] if x in self.tag_dct.keys() else None, array)):
            f_v = pvector(filter(None, list(map(lambda x: self.F_keys(x)[0] if self.F_keys(x) else None, array))))
            ind_v = pvector([self._strmatch(x,text) for x in array if self.F_keys(x)])
            if f_v: return (' '.join(f_v),(ind_v[0][0],ind_v[-1][1]))
            else: return None
        
        if 'masc' in list(map(lambda x: self.tag_dct[x] if x in self.tag_dct.keys() else None, array)):
            array = list(map(lambda x: x[:-1] if f_gen.findall(x) else x ,array))
            m_v = pvector(filter(None, list(map(lambda x: self.M_keys(x)[0] if self.M_keys(x) else None, array))))
            ind_v = pvector([self._strmatch(x,text) for x in array if self.M_keys(x)])
            if m_v: return (' '.join(m_v),(ind_v[0][0],ind_v[-1][1]))
            else: return None
        
    def extract(self, text):
        text = cap(text)
        text = replace_text(text)
        self.line = text
        matches = _match(text, self._filter_normalize(text))
        tet = pvector(map(self._repl ,_group(matches)))
        all_vectors = pvector(filter(None, list(map(lambda x: self._repl_dct(x,text),tet))))
        self.tag_dct = {}
        self.line = ''
        return all_vectors
