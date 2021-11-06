import string
import nltk
import os
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
        # Пропускаем только необходимые части речи -
        # if p.tag.POS != 'VERB' and p.tag.POS != 'INFN' and p.tag.POS != 'ADVB' and p.tag.POS != 'CONJ':
        #     res.append(p.normal_form)
        # print(f'Word: {p.word}, pos: {pos}\n')
        # TODO надо ли убрирать местоименные прилагательные/существительные? (который, свой и т.д.)
        #      > почему-то пропускает мг (единицы измерения)
        if pos == 'NOUN' or pos == 'ADJF' or pos == 'ADJS':
            res.append(p.normal_form)
    return res


def remove_punctuation(text):
    punctuation = string.punctuation + '\n\t\xa0«»-—…'
    return "".join([char for char in text if char not in punctuation])

# слова
def words_processing(text):
    # препроцессинг
    text = text.lower()
    text = remove_punctuation(text)

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
        print(word)



# Определения
def definition_processing(text):
    print('def processing not implemented')



# Словосочетания
def collocation_processing(text):
    print('coll processing not implemented')

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
