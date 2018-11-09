import re
from nltk.stem import *

def tokenize(text):
    arrayOfTokensBefore = re.split(r'[0123456789&$_;,:?. !\n\t]+', text)
    arrayOfTokens = []
    stemmer = PorterStemmer()
    for token in arrayOfTokensBefore:
        # validam daca e diferit de null si daca nu e numar
        if token != '' and not token.isdigit():
            # lowercase si eliminare - din cuvinte
            goodToken = ''.join(re.split(r'[-]+', token.lower()))
            # eliminam " 's "
            goodToken = goodToken.replace('\'s', '')
            # Stem cu libraria nltk: http://www.nltk.org
            goodToken = stemmer.stem(goodToken)
            arrayOfTokens.append(goodToken)
    return arrayOfTokens