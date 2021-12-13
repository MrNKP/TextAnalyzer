import re
import string
import nltk
import os
from nltk import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import pymorphy2  # морфологический анализатор https://pymorphy2.readthedocs.io/en/latest/user/index.html

# morph = pymorphy2.MorphAnalyzer()

def checkDefType1(position, tokens):
    punctuation = """!"#$%&'()*+,./:;<=>?@[\]^_`{|}~«»"""
    localToken = tokens[position]
    mainCondition = localToken == '–' or localToken == '—'
    prevCond1 = tokens[position - 1] not in punctuation if position >= 1 else False
    nextCond1 = tokens[position + 1] not in punctuation if position <= len(tokens) - 2 else False
    nextCond2 = tokens[position + 2] not in punctuation if position <= len(tokens) - 3 else False
    # nextCond3 = tokens[position + 3] not in punctuation if position <= len(tokens) - 4 else False
    # nextCond4 = tokens[position + 4] not in punctuation if position <= len(tokens) - 5 else False
    return mainCondition and prevCond1 and not(nextCond1 or nextCond2)# and nextCond3 and nextCond4)

if __name__ == '__main__':
    # print(morph.parse('бери-бери')[0])
    # print(word_tokenize('«бери-бери»', 'russian'))
    punctuation = """!"#$%&'()*+,./:;<=>?@[\]^_`{|}~«»"""
    filename = 'resources/4.txt'
    file = open(filename, 'r', encoding="utf-8")
    text = file.read()
    file.close()
    print(text)
    # text = re.sub(r'([\(\[]).*?([\)\]])', r'\g<1>\g<2>', text)
    text = re.sub(r'[\(\[].*?[\)\]]', r'', text)
    print(text)
    indexes = re.findall(r'\.\s+[А-ЯA-Z0-9]', text)
    print(indexes)
    indexes1 = []
    indexes1.append(-2)
    for i in range(len(text)-3):
        substr = text[i:i+3]
        if re.match(r'\.\s+[А-ЯA-Z0-9]', substr):
            indexes1.append(i)
            # print('Found')
    print(f'len(indexes1) = {len(indexes1)}\nlen(indexes) = {len(indexes)}')
    sentences = []
    for i in range(len(indexes1)-1):
        # print(f'{i} i = {indexes1[i]}\ti+1 = {indexes1[i+1]}')
        start = indexes1[i] + 2
        finish = indexes1[i+1] + 1
        sbstr = text[start:finish]
        print(f'{i} : start = {start}\tfinish = {finish}\tindexes1[i] = {indexes1[i]}\tindexes1[i+1] = {indexes1[i+1]}')
        sentences.append(sbstr)
    print(f'len(sentences) = {len(sentences)}')
    for i in range(len(sentences)):
        print(f'{i} -> {sentences[i]}')

    print('Def list:')
    for i in range(len(sentences)):
        word_tokens = word_tokenize(sentences[i])
        for pos in range(len(word_tokens)):
            localToken = word_tokens[pos]
            type1Condition = (localToken == '—' or localToken == '–') and ((word_tokens[pos - 1] not in punctuation) if pos >= 1 else False) and (min(pos, len(word_tokens) - pos) <= 2)
            type2Condition = (localToken == 'это' and (word_tokens[pos - 1] == '—' or word_tokens[pos - 1] == '–')) if pos >= 1 else False
            type3Condition = (localToken == 'понимается' and (word_tokens[pos - 2] == 'под' or word_tokens[pos - 3] == 'под')) if pos >= 3 else False
            lengthCondition = (len(word_tokens) - pos >= 2 and pos >= 1)# and len(word_tokens) < 40)
            if (type1Condition or type2Condition or type3Condition):# and lengthCondition:
                print(f'{i} found def')
                break
