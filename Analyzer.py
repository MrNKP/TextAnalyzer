import string

def remove_punctuation(text):
    punctuation = string.punctuation + '\n\t\xa0«»-…'
    return "".join([char for char in text if char not in punctuation])

if __name__ == '__main__':
    file = open('test.txt', "r", encoding="utf-8")
    text = file.read()
    file.close()
    print(f'len = {len(text)}')
    text = text.lower()
    text = remove_punctuation(text)
    set = {}
    for word in text.split():
        try:
            set[word] += 1
        except:
            set[word] = 1
    for i in sorted(set.keys()):
        print(f'{i} - {set[i]}')
    # print(text_tokens)
    # print(string.punctuation)
