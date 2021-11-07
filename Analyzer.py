import string
import nltk
import os
import re
from nltk import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import pymorphy2  # морфологический анализатор https://pymorphy2.readthedocs.io/en/latest/user/index.html

morph = pymorphy2.MorphAnalyzer()


def lemmatize_and_clean(word_tokens):
    res = list()
    for token in word_tokens:
        p = morph.parse(token)[0]
        pos = p.tag.POS
        # Пропускаем только необходимые части речи - существительные, прилагательные
        # TODO надо ли убрирать местоименные прилагательные/существительные? (который, свой и т.д.)
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
    rus_stopwords = stopwords.words('russian')
    rus_stopwords += []  # при необходимости добавить доп слова не несущие смысловой нагрузки
    word_tokens = [token for token in word_tokens if token not in rus_stopwords]

    # результат
    nltk_text = nltk.Text(word_tokens)
    freq_dist = FreqDist(nltk_text)  # распределение частот
    print('Most common words:')
    for word in freq_dist.most_common(15):
        if (word[1] > 1):
            print('\t', word, morph.parse(word[0])[0].tag.POS)


# Определения
def definition_processing(text):
    print('def processing not implemented')


# Словосочетания
def collocation_processing(text):
    # препроцессинг
    text = text.lower()
    text = remove_units(text)

    word_tokens = word_tokenize(text, 'russian')

    # TODO словосочетания, вынести в метод
    #  ADJF + NOUN
    #  NOUN + NOUN
    #  NUMR + NOUN
    #  VERB\INFN + NOUN
    #  VERB\INFN + ADVB\GRND
    #  GRND + NOUN/ADVB
    #  PRTF/PRTS + зависимое слово?
    collocations_tokens = list()
    i = 0
    while i < (len(word_tokens) - 1):
        p1 = morph.parse(word_tokens[i])[0]
        pos1 = p1.tag.POS
        p2 = morph.parse(word_tokens[i+1])[0]
        pos2 = p2.tag.POS

        if (
                (pos1 == 'ADJF' and pos2 == 'NOUN') or
                (pos1 == 'NOUN' and pos2 == 'NOUN') or
                (pos1 == 'NUMR' and pos2 == 'NOUN') or
                (pos1 == 'VERB' and pos2 == 'NOUN') or
                (pos1 == 'INFN' and pos2 == 'NOUN') or
                (pos1 == 'VERB' and pos2 == 'ADVB') or
                (pos1 == 'INFN' and pos2 == 'ADVB') or
                (pos1 == 'VERB' and pos2 == 'GRND') or
                (pos1 == 'INFN' and pos2 == 'GRND') or
                (pos1 == 'GRND' and pos2 == 'NOUN') or
                (pos1 == 'GRND' and pos2 == 'ADVB')
        ) and len(p1.word) > 1 and len(p2.word) > 1:
            # TODO проблемы:
            #      может быть 3 слова
            #      привести к удобоваримому виду в плане падежа/числа (как минимум)
            #      возможно надо найти сначала главное и зависимое слово
            collocations_tokens.append(p1.word + ' ' + p2.word)
        i = i + 1

    # очистка текста
    rus_stopwords = stopwords.words('russian')
    rus_stopwords += []  # при необходимости добавить доп слова не несущие смысловой нагрузки
    collocations_tokens = [token for token in collocations_tokens if token not in rus_stopwords]

    # результат
    nltk_text = nltk.Text(collocations_tokens)
    freq_dist = FreqDist(nltk_text)  # распределение частот
    print('Most common collocations:')
    for word in freq_dist.most_common(15):
        if (word[1] > 1):
            print('\t', word, morph.parse(word[0])[0].tag.POS)



if __name__ == '__main__':
    nltk.download('punkt')
    nltk.download('stopwords')

    # копаемся во всех файлах в папке resources
    for filename in os.listdir("./resources"):
        if filename.endswith(".txt"):
            file = open('resources/' + filename, "r", encoding="utf-8")
            text = file.read()
            file.close()
            print(f'Filename = {filename}')
            print(f'First 80 symbols = {text[:80]}...')
            print(f'Characters count = {len(text)}')

            words_processing(text)
            definition_processing(text)
            collocation_processing(text)

            print('==============================\n\n')
            # break
            continue
        else:
            continue
