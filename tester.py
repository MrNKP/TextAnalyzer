import string
import nltk
import os
from nltk import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import pymorphy2  # морфологический анализатор https://pymorphy2.readthedocs.io/en/latest/user/index.html

morph = pymorphy2.MorphAnalyzer()

if __name__ == '__main__':
    print(morph.parse('бери-бери')[0])
    print(word_tokenize('«бери-бери»', 'russian'))