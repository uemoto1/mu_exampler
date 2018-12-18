import os
import csv
import gzip
import _pickle
import collections
from . import kwsearch
from . import porterstemmer


class Corpus:

    ps = None
    text = []
    stem_text = []

    def __init__(self, file_cache=''):
        self.ps = porterstemmer.PorterStemmer()
        if file_cache:
            with open(file_cache, 'rb') as fh:
                state = _pickle.load(fh)
            self.text = state['text']
            self.stem_text = state['stem_text']
        return

    def dump_cache(self, file_cache):
        state = {
            'text': self.text,
            'stem_text': self.stem_text,
        }
        with open(file_cache, 'wb') as fh:
            _pickle.dump(state, fh)
            
    def migrate(self, file_inp):
        # Open file_inp (with decompress gzip)
        if os.path.splitext(file_inp)[-1] == '.gz':
            fh = gzip.open(file_inp, 'rt')
        else:
            fh = open(file_inp, 'rt')
        # Read CSV File
        for row in csv.reader(fh):
            self.text += row
            self.stem_text += [
                self.ps.stem(word, 0, len(word) - 1).lower()
                for word in row
            ]
        fh.close()

    def find(self, keyword, use_stemming=True, margin=10):
        # Prepare kw-list
        kw = [
            self.ps.stem(word, 0, len(word) - 1).lower()
            for word in keyword.split()
        ]
        # Find from corpus
        if use_stemming:
            match_list = kwsearch.findall(kw, self.stem_text)
        else:
            match_list = kwsearch.findall(kw, self.text)
        # Create groups
        mdict = collections.defaultdict(list)
        for i, j in match_list:
            mdict[tuple(self.stem_text[i:j])] += [(i, j)]
        ranking = [(len(v), k) for k, v in mdict.items()]
        ranking.sort(reverse=True)
        # Create results
        result = []
        for _, k in ranking:
            tmp = []
            for i, j in mdict[k]:
                body = self.text[i:j]
                head = self.text[i-margin:i]
                tail = self.text[j:j+margin]
                tmp += [(body, head, tail)]
            result += [tmp]
        return result
