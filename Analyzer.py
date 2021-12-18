import string
import nltk
import os
import re
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
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
    punctuation = """!"#$%&'()*+,./:;<=>?@[\]«»^_`{|}~""" + '\n\t\xa0'
    table = str.maketrans(dict.fromkeys(punctuation))
    return text.translate(table)


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


def is_token_in_dict(token, dict):
    stopwords = read_exclude_dict(dict)
    for dict_word in stopwords:
        if token.lower() == dict_word:
            return True
    return False

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

def is_dash(token):
    return token == '—' or token == '–'

def is_comma(token):
    return token == ','


def is_word(token):
    return len(re.sub(r'[A-Za-zА-Яа-я\-]+\.?', r'', token)) == 0


def is_number(token):
    return len(re.sub(r'[0-9]+', r'', token)) == 0


# Определения
def definition_processing(text):
    definitions = []

    # разделяем текст на предложения предложения
    sentences = sent_tokenize(text, 'russian')
    # for s in sentences:
    #     print('sentence: ' + s)

    for original_sentence in sentences:
        sentence = re.sub(r'[\(\[].*?[\)\]]', r'', original_sentence)

        word_tokens = word_tokenize(sentence)
        tokens_count = len(word_tokens)

        word_tokens_without_punct = word_tokenize(remove_unnecessary_symbols(sentence))
        tokens_without_punct_count = len(word_tokens_without_punct)
        if (tokens_count >= 5):

            # конструкции определений
            #   1) [1-2 слова] [-] [N слов]
            #   2) [N слов] [-] [1-2 слова]
            #       возможно исключаем слова начинающиеся с большой буквы (но вообще это ошибка в тексте)
            #   3) [1-3 слова КАПСОМ] [,]|[-] [N слов]
            #   4) [под] [N слов] [понимается] [N слов]

            is_definition = False

            # case 1) [1-2 слова] [-] [N слов]
            for i in range(tokens_without_punct_count):
                current_token = word_tokens_without_punct[i]
                next_token = word_tokens_without_punct[i+1] if i < tokens_without_punct_count - 1 else ''
                if (is_dash(current_token) and
                    1 <= i <= 2 and
                    not is_token_in_dict(word_tokens_without_punct[i-1], 'exclude_from_definitions.txt') and
                    not is_number(next_token)):

                    if tokens_without_punct_count - i >= 4 and (
                            is_dash(word_tokens_without_punct[i+3]) or
                            is_dash(word_tokens_without_punct[i+4])):
                        continue
                    else:
                        is_definition = True
                        break


            # case 2) [N слов] [-] [1-2 слова]
            if not is_definition:
                reversed_tokens = word_tokens[::-1]  # reverse list
                for i in range(tokens_count):
                    current_token = reversed_tokens[i]
                    next_token = reversed_tokens[i+1] if i < tokens_count - 1 else ''
                    if (is_dash(current_token) and
                        1 <= i <= 2 and
                        not is_number(next_token)): # and not (len(next_token) > 0 and next_token[0].isupper())

                        is_definition = True
                        break


            # case 3) [1-3 слова КАПСОМ] [,]|[-] [N слов]
            if not is_definition:
                for i in range(tokens_count):
                    current_token = word_tokens[i]
                    next_token = word_tokens[i+1] if i < tokens_count - 1 else ''
                    if ((is_dash(current_token) or is_comma(current_token)) and
                        1 <= i <= 3 and
                        not is_number(next_token)):

                        is_upper = True
                        for k in range(i):
                            if not word_tokens[k].isupper():
                                is_upper = False

                        if is_upper:
                            is_definition = True
                            break


            # 4) [под] [N слов] [понимается] [N слов]
            if not is_definition and word_tokens[0].lower() == 'под':
                for i in range(1, tokens_count):
                    current_token = word_tokens[i]
                    if morph.parse(current_token.lower())[0].normal_form == 'пониматься' and i <= 5:
                        is_definition = True
                        break


            if is_definition:
                definitions.append(original_sentence)

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
    # виды словосочетаний, которые НЕ учитываем
    #  NOUN + NOUN
    #  NUMR + NOUN
    #  VERB\INFN + ADVB\GRND
    #  GRND + NOUN/ADVB
    #  PRTF/PRTS + зависимое слово
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

            # words_processing(text)
            definition_processing(text)
            # collocation_processing(text)

            print(YELLOW + BOLD + '============================================================\n\n' + END)
            # break
            continue
        else:
            continue
