import string
import nltk
from nltk import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import pymorphy2  # морфологический анализатор https://pymorphy2.readthedocs.io/en/latest/user/index.html

morph = pymorphy2.MorphAnalyzer()

def lemmatize(word_tokens):
    res = list()
    for token in word_tokens:
        p = morph.parse(token)[0]
        res.append(p.normal_form)
    return res


def remove_punctuation(text):
    punctuation = string.punctuation + '\n\t\xa0«»-—…'
    return "".join([char for char in text if char not in punctuation])


if __name__ == '__main__':
    nltk.download('punkt')
    nltk.download('stopwords')

    file = open('recources/text.txt', "r", encoding="utf-8")
    text = file.read()
    file.close()
    print(f'Text characters count = {len(text)}')

    # препроцессинг
    text = text.lower()
    text = remove_punctuation(text)

    word_tokens = word_tokenize(text, 'russian')

    # очистка текста
    rus_stopwords = stopwords.words('russian')
    rus_stopwords += []  # при необходимости добавить доп слова не несущие смысловой нагрузки
    word_tokens = [token for token in word_tokens if token not in rus_stopwords]

    # лемматизация
    word_tokens = lemmatize(word_tokens)

    # результат
    nltk_text = nltk.Text(word_tokens)
    freq_dist = FreqDist(nltk_text)  # распределение частот
    print('Most common words:')
    for word in freq_dist.most_common(15):
        print(word)
