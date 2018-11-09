import os
import tokenizer as tok
import sys
import gc
import uuid
import re
import psutil

sourceDirectory = 'real_data/'

def retriveInfo():
    infoDictionary = {}
    indexDictionary = {}
    index = 0
    fileName = ''
    infoDictionary, indexDictionary, dictionaryAsAString, index, fileName = recurviseCrossing('', infoDictionary,
                                                                indexDictionary, '', index, fileName)
    fileName = writeOnDisk(infoDictionary, fileName)
    # stergem postinglist-urile
    del infoDictionary
    # fortam Garbage collecter-ul sa elibereze acea zona de memorie orfana
    gc.collect()
    return indexDictionary, fileName, dictionaryAsAString

# cautare recursiva prin directoare
def recurviseCrossing(filePath, infoDictionary, indexDictionary, dictionaryAsAString, index, fileName):
    for filename in os.listdir(sourceDirectory + filePath):
        if os.path.isfile(sourceDirectory + filePath + '/' + filename):
            index += 1
            indexDictionary[index] = (filePath + '/' + filename)[1:]
            file = open(sourceDirectory + filePath + '/' + filename, 'r')
            arrayOfTokens = tok.tokenize(file.read())
            for idx, token in enumerate(arrayOfTokens, start=1):
                # compresie dictionar
                # cautam daca cuvantul apare deja in lista de cuvinte din dictionar si retinem pozitia
                tokenPoz = getPositionFromString(token, dictionaryAsAString)
                if tokenPoz in infoDictionary:
                    if index == infoDictionary[tokenPoz][-1]['fileNr']:
                        # compresie a postinglist-urilor
                        # in loc sa retinem fiecare pozitie in care apare acel cuvant, vom retine doar diferenta dintre
                        # doua pozitii consecutive
                        # Ex: in loc sa retinem [1, 6, 10], vom retine [1, 5, 4]
                        infoDictionary[tokenPoz][-1]['pozArray'].append(idx - sum(infoDictionary[tokenPoz][-1]['pozArray']))
                        #infoDictionary[token][-1]['pozArray'].append(idx)
                    else:
                        pair = {}
                        pair['fileNr'] = index
                        pair['pozArray'] = [idx]
                        infoDictionary[tokenPoz].append(pair)
                else:
                    pair = {}
                    pair['fileNr'] = index
                    pair['pozArray'] = [idx]
                    if tokenPoz == -1:
                        # retinem pozitia cuvantului ca si cheie a dictionarului
                        infoDictionary[len(dictionaryAsAString)] = [pair]
                        dictionaryAsAString += token + ','
                    else:
                        infoDictionary[tokenPoz] = [pair]
            file.close()
            # daca dimensiunea postinglist-urilor este mai mare de 512MB, scriem in fisier si le golim
            print(index)
            #if sys.getsizeof(infoDictionary) > 6291500:
            if sys.getsizeof(infoDictionary) > 70000:
            #if psutil.Process(os.getpid()).memory_info().rss > 536870912:
                fileName = writeOnDisk(infoDictionary, fileName)
                # stergem postinglist-urile
                del infoDictionary
                # fortam Garbage collecter-ul sa elibereze acea zona de memorie orfana
                gc.collect()
                infoDictionary = {}
        else:
            infoDictionary, indexDictionary, dictionaryAsAString, index, fileName = recurviseCrossing(filePath + '/' + filename,
                                                infoDictionary, indexDictionary, dictionaryAsAString, index, fileName)
    return infoDictionary, indexDictionary, dictionaryAsAString, index, fileName

# functia de scriere a postinglist-urilor pe disk
# primeste dictionarul care contine postinglist-urile si numele fisierul vechi
# returneaza numele fisierului nou creat dupa merge
def writeOnDisk(infoDictionary, fileName):
    print('*')
    if infoDictionary == {}:
        return fileName
    if fileName == '':
        # generam un nume random de fisier
        newFileName = str(uuid.uuid4()) + '.txt'
        f = open(newFileName, "w")
        # dictionarul este sortat dupa chei
        # scriem postinglist-urile in fisier
        for key in sorted(infoDictionary):
            f.write(str(key) + '[')
            for item in infoDictionary[key]:
                f.write(str(item['fileNr']) + ':' + ','.join(map(str, item['pozArray'])) + ';')
            f.write(']\n')
        return newFileName
    else:
        # sortam noile postinglist-uri dupa chei
        keysArray = sorted(list(infoDictionary.keys()))
        index = 0
        keysArrayLen = len(keysArray)
        # generam un nume random de fisier
        newFileName = str(uuid.uuid4()) + '.txt'
        f = open(newFileName, "w")

        # algoritmul de merge: Fisierul vechi este sortat dupa chei, precum si noile postinglist-uri
        # cat timp putem citi din fisier
        for line in open(fileName):
            line = line.rstrip('\n')
            parts = re.split(r'[\[\]\n\t]+', line)
            # daca nu am terminat de parcurs postinglist-urile
            if index < keysArrayLen:
                # daca prima cheie din fisier este mai mica decat prima din dictionar, o scriem in fisierul nou
                if int(parts[0]) < keysArray[index]:
                    f.write(line + '\n')
                else:
                    # daca cheia apara atat in fisier, cat si in dictionar, scriem intai ce apare in fisier, iar apoi
                    # adaugam ce am gasit in noul dictionar. Astfel este pastrata ordinea crescatoare a fisierelor
                    # in care apare acea cheie
                    if int(parts[0]) == keysArray[index]:
                        f.write(parts[0] + '[')
                        f.write(parts[1])
                        for item in infoDictionary[keysArray[index]]:
                            f.write(str(item['fileNr']) + ':' + ','.join(map(str, item['pozArray'])) + ';')
                        f.write(']\n')
                        index += 1
                    # in final, cat timp cuvantul din dictionar este mai mic decat cel din fisier, le scriem in fisierul nou
                    else:
                        while index < keysArrayLen and int(parts[0]) > keysArray[index]:
                            f.write(str(keysArray[index]) + '[')
                            for item in infoDictionary[keysArray[index]]:
                                f.write(str(item['fileNr']) + ':' + ','.join(map(str, item['pozArray'])) + ';')
                            f.write(']\n')
                            index += 1
                        if index < keysArrayLen:
                            if int(parts[0]) < keysArray[index]:
                                f.write(line + '\n')
                            else:
                                if int(parts[0]) == keysArray[index]:
                                    f.write(parts[0] + '[')
                                    f.write(parts[1])
                                    for item in infoDictionary[keysArray[index]]:
                                        f.write(str(item['fileNr']) + ':' + ','.join(map(str, item['pozArray'])) + ';')
                                    f.write(']\n')
                                    index += 1
                        else:
                            f.write(line + '\n')
            # dc am terminat, scriem tot ce a mai ramas din vechiul fisier in cel nou
            else:
                f.write(line + '\n')
        # dupa ce am terminat de transcris fisierul vechi, scriem in cel nou tot ce a mai ramas din postingliste
        while index < keysArrayLen:
            f.write(str(keysArray[index]) + '[')
            for item in infoDictionary[keysArray[index]]:
                f.write(str(item['fileNr']) + ':' + ','.join(map(str, item['pozArray'])) + ';')
            f.write(']\n')
            index += 1
        # stergem vechiul fisier
        os.remove(fileName)
        return newFileName

def getPositionFromString(str, strToSearch):
    strArray = re.split(r'[,\n\t]+', strToSearch)
    suma = 0
    for word in strArray:
        if word == str:
            return suma
        else:
            suma += len(word) + 1
    return -1