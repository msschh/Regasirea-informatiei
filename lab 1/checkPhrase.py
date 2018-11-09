import tokenizer as tok
import re
from retriveInfo import getPositionFromString

def checkPhrase(phrase, indexDictionary, fileName, dictionaryAsAString):
    phraseArray = tok.tokenize(phrase)
    mergedArray = getArrayFromFile(phraseArray[0], fileName, dictionaryAsAString)
    for word in phraseArray[1:]:
        mergedArray = mergeArrays(mergedArray, getArrayFromFile(word, fileName, dictionaryAsAString))
    f = open("answer.txt", "w")
    for pair in mergedArray:
        f.write(indexDictionary[int(pair['fileNr'])] + "\n")
        #f.write(pair['fileNr'] + "\n")

# vom folosi aceasta functie pentru a extrage postinglist-ul acestui cuvant
def getArrayFromFile(word, fileName, dictionaryAsAString):
    word = getPositionFromString(word, dictionaryAsAString)
    for line in open(fileName):
        line = line.rstrip('\n')
        parts = re.split(r'[\[\]\n\t]+', line)
        if parts[0] == str(word):
            arrays = re.split(r'[;\n\t]+', parts[1])
            arrayList = []
            for array in arrays:
                arrayParts = re.split(r'[:\n\t]+', array)
                if len(arrayParts) > 1:
                    pair = {}
                    pair['fileNr'] = arrayParts[0]
                    pair['pozArray'] = []
                    sum = 0
                    arrayNr = re.split(r'[,\n\t]+', arrayParts[1])
                    for nr in arrayNr:
                        sum += int(nr)
                        pair['pozArray'].append(sum)
                    arrayList.append(pair)
            return arrayList
    return []

def mergeArrays(array1, array2):
    mergedArray = []
    indexForArray1 = 0
    indexForArray2 = 0
    while indexForArray1 < len(array1) and indexForArray2 < len(array2):
        if array1[indexForArray1]['fileNr'] == array2[indexForArray2]['fileNr']:
            mergedArrayInner = []
            indexForArray3 = 0
            indexForArray4 = 0
            while indexForArray3 < len(array1[indexForArray1]['pozArray']) and indexForArray4 < len(array2[indexForArray2]['pozArray']):
                if array1[indexForArray1]['pozArray'][indexForArray3] == (array2[indexForArray2]['pozArray'][indexForArray4] - 1):
                    mergedArrayInner.append(array2[indexForArray2]['pozArray'][indexForArray4])
                    indexForArray3 += 1
                    indexForArray4 += 1
                else:
                    if array1[indexForArray1]['pozArray'][indexForArray3] < (array2[indexForArray2]['pozArray'][indexForArray4] - 1):
                        indexForArray3 += 1
                    else:
                        indexForArray4 += 1
            if len(mergedArrayInner) != 0:
                pair = {}
                pair['fileNr'] = array1[indexForArray1]['fileNr']
                pair['pozArray'] = mergedArrayInner
                mergedArray.append(pair)
            indexForArray1 += 1
            indexForArray2 += 1
        else:
            if array1[indexForArray1]['fileNr'] < array2[indexForArray2]['fileNr']:
                indexForArray1 += 1
            else:
                indexForArray2 += 1
    return mergedArray
