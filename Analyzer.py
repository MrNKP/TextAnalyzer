import string
import nltk
import os
import re
from nltk import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import pymorphy2  # морфологический анализатор https://pymorphy2.readthedocs.io/en/latest/user/index.html

morph = pymorphy2.MorphAnalyzer()

BOLD = '\033[1m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
END = '\033[0m'

def lemmatize_and_clean(word_tokens):
    res = list()
    for token in word_tokens:
        p = morph.parse(token)[0]
        pos = p.tag.POS
        # Пропускаем только необходимые части речи - существительные, прилагательные
        if (pos == 'NOUN' or pos == 'ADJF' or pos == 'ADJS') and len(p.word) > 1:
            res.append(p.normal_form)
    return res


def remove_unnecessary_symbols(text):
    punctuation = """!"#$%&'()*+,./:;<=>?@[\]^_`{|}~""" + '\n\t\xa0'
    return "".join([char for char in text if char not in punctuation])


def remove_units(text):
    file = open('resources/dicts/units.txt', "r", encoding="utf-8")
    dict_tokens = word_tokenize(file.read(), 'russian')
    file.close()
    for token in dict_tokens:
        text = re.sub(r'\s+' + token + r'(\s+|\.|,|\(|\))', ' ', text)
    return text

def read_exclude_dict(filename):
    file = open('resources/dicts/' + filename, "r", encoding="utf-8")
    dict_tokens = word_tokenize(file.read(), 'russian')
    file.close()
    return dict_tokens


# очистка текста от ненужных слов
def remove_stopwords(word_tokens):
    rus_stopwords = stopwords.words('russian')
    rus_stopwords += read_exclude_dict('exclude_from_collocations.txt')
    return [token for token in word_tokens if token not in rus_stopwords]


# слова
def words_processing(text):
    # препроцессинг
    text = text.lower()
    text = remove_unnecessary_symbols(text)
    text = remove_units(text)

    word_tokens = word_tokenize(text, 'russian')

    # лемматизация
    word_tokens = lemmatize_and_clean(word_tokens)

    # очистка текста
    word_tokens = remove_stopwords(word_tokens)

    # результат
    nltk_text = nltk.Text(word_tokens)
    freq_dist = FreqDist(nltk_text)  # распределение частот
    print(GREEN + BOLD + 'Most common words:' + END)
    for word in freq_dist.most_common(15):
        if (word[1] > 1):
            print('\t', word)


# Определения
def definition_processing(text):
    punctuation = """!"#$%&'()*+,./:;<=>?@[\]^_`{|}~«»"""
    # punctuation = """!"#$%&'*+,./:;<=>?@[\]^_`{|}~«»"""
    text = text.lower()
    # text = remove_units(text)
    text = text.replace('—', '—' + ' ', text.count('—'))
    text = text.replace('–', '–' + ' ', text.count('–'))
    for char in punctuation:
        text = text.replace(char, char + ' ', text.count(char))
    word_tokens = word_tokenize(text, 'russian')
    definitions = list()
    position = 0
    sentencesPositions = []
    sentencesPositions.append(-1)
    for token in word_tokens:
        if token == '.':
            sentencesPositions.append(position)
        position += 1
    sentencesCount = len(sentencesPositions)
    # print(f'sentencesCount = {sentencesCount}')
    for i in range(0, sentencesCount-1):
        # print(f'{i}/{sentencesCount}')
        for pos in range(sentencesPositions[i]+1, sentencesPositions[i+1]):
            localToken = word_tokens[pos]
            type1Condition = ((localToken == '—' or localToken == '–') and (word_tokens[pos-1] not in punctuation)) if pos != sentencesPositions[i]+1 else False
            type2Condition = (localToken == 'это' and (word_tokens[pos-1] == '—' or word_tokens[pos-1] == '–')) if pos != sentencesPositions[i]+1 else False
            type3Condition = (localToken == 'понимается' and (word_tokens[pos-2] == 'под' or word_tokens[pos-3] == 'под')) if pos != sentencesPositions[i]+3 else False
            if type1Condition or type2Condition or type3Condition:
                localDefinition = ''
                for index in range(sentencesPositions[i]+1, sentencesPositions[i+1]):
                    localDefinition += word_tokens[index]
                    if index != sentencesPositions[i+1] - 1:
                        localDefinition += ' '
                definitions.append(localDefinition)
                break
    print(GREEN + BOLD + 'Definitions: ' + END)
    for definition in definitions:
        print('\t>>> ', definition)


def parse_and_inflect_collocations(word_tokens):
    collocations_tokens = list()
    i = 0
    while i < (len(word_tokens) - 1):
        p1 = morph.parse(word_tokens[i])[0]
        pos1 = p1.tag.POS

        p2 = morph.parse(word_tokens[i + 1])[0]
        pos2 = p2.tag.POS

        exclude_words = read_exclude_dict('exclude_from_collocations.txt')

        if (
                # сущ + прил
                (pos1 == 'ADJF' and pos2 == 'NOUN') or
                (pos1 == 'NOUN' and pos2 == 'ADJF') or

                # глаг + сущ
                (pos1 == 'VERB' and pos2 == 'NOUN') or
                (pos1 == 'INFN' and pos2 == 'NOUN') or
                (pos1 == 'NOUN' and pos2 == 'VERB') or
                (pos1 == 'NOUN' and pos2 == 'INFN')
        ) and p1.normal_form != p2.normal_form and len(p1.word) > 1 and len(p2.word) > 1 and (p1.normal_form not in exclude_words) and (p2.normal_form not in exclude_words):
            if pos1 == 'NOUN':  # определяем положение сущ
                p1_normal = morph.parse(p1.normal_form)[0]
                gender1 = p1_normal.tag.gender  # род
                number1 = p1_normal.tag.number  # число
                case1 = p1_normal.tag.case  # падеж
                if pos2 == 'ADJF':
                    (word2, error) = try_inflect_word(p2, gender1, number1, case1)
                    collocations_tokens.append(word2 + ' ' + (p1.word if error else p1_normal.word))
                # else:
                #     collocations_tokens.append(p1.word + ' ' + try_inflect_word(p2, gender1, number1, case1)[0])
            else:
                p2_normal = morph.parse(p2.normal_form)[0]
                gender2 = p2_normal.tag.gender
                number2 = p2_normal.tag.number
                case2 = 'nomn'
                if pos1 == 'ADJF':
                    (word1, error) = try_inflect_word(p1, gender2, number2, case2)
                    collocations_tokens.append(word1 + ' ' + (p2.word if error else p2_normal.word))
                else:
                    collocations_tokens.append(try_inflect_word(p1, gender2, number2, case2)[0] + ' ' + p2.word)
        i = i + 1
    return collocations_tokens


def try_inflect_word(parse, gender, number, case):
    if gender is None or number is None or case is None or parse.inflect({gender, number, case}) is None:
        return parse.word, True
    else:
        return parse.inflect({gender, number, case}).word, False


# Словосочетания
def collocation_processing(text):
    # препроцессинг
    text = text.lower()
    text = remove_units(text)

    word_tokens = word_tokenize(text, 'russian')

    # Словосочетания из 2-х слов - <сущ + прил> или <глаг + сущ>
    # виды словосочетаний, которые не учитываем
    #  NOUN + NOUN
    #  NUMR + NOUN
    #  VERB\INFN + ADVB\GRND
    #  GRND + NOUN/ADVB
    #  PRTF/PRTS + зависимое слово?
    collocations_tokens = parse_and_inflect_collocations(word_tokens)

    # результат
    nltk_text = nltk.Text(collocations_tokens)
    freq_dist = FreqDist(nltk_text)  # распределение частот
    print(GREEN + BOLD + 'Most common collocations:' + END)
    for collocation in freq_dist.most_common(15):
        if (collocation[1] > 1):
            print('\t', collocation)


if __name__ == '__main__':
    nltk.download('punkt')
    nltk.download('stopwords')

    # копаемся во всех файлах в папке resources
    for filename in os.listdir("./resources"):
        if filename.endswith(".txt"):
            file = open('resources/' + filename, "r", encoding="utf-8")
            text = file.read()
            file.close()
            print(f'{GREEN + BOLD}Filename{ END } = {filename}')
            print(f'{GREEN + BOLD}First 80 symbols{ END } = {text[:80]}...')
            print(f'{GREEN + BOLD}Characters count{ END } = {len(text)}')

            words_processing(text)
            definition_processing(text)
            collocation_processing(text)

            print(YELLOW + BOLD + '============================================================\n\n' + END)
            # break
            continue
        else:
            continue
