import re
import os.path

sourceDirectory = 'pa3-data/Training';

# aflam dictionarul termenilor
def getMapOfQueryTerms():
    mapOfQueryTerms = {};
    if os.path.exists('terms.txt'):
        print("Read query terms from file");
        file = open("terms.txt", 'r');
        arrayOfTerms = re.split(r'[ \n]+', file.read());
        for word in arrayOfTerms:
            if word != '':
                mapOfQueryTerms[word] = {};
        return mapOfQueryTerms;
    else:
        print("Find query terms");
        for line in open(sourceDirectory + '/queries', encoding="utf-8"):
            arrayOfWords = re.split(r'[ \n]+', line);
            if len(arrayOfWords) > 0 and arrayOfWords[0] == 'query:':
                for word in arrayOfWords[1:-1]:
                    mapOfQueryTerms[word] = {};
        f = open("terms.txt", "w");
        print("Write query terms in file");
        for word in mapOfQueryTerms.keys():
            f.write(word + " ");
        return mapOfQueryTerms;

def getMapOfQueryVector(mapOfQueryTerms):
    mapOfQueryVectors = {};
    if os.path.exists('queryVector.txt'):
        print("Read query vector from file");
        for line in open('queryVector.txt', 'r'):
            arrayOfWords = re.split(r'[ \t\n]+', line);
            mapOfQueryVectors[arrayOfWords[0]] = float(arrayOfWords[1]);
    else:
        print("Create query vector");
        for term in mapOfQueryTerms:
            mapOfQueryVectors[term] = 0;
        N = 0;
        for directoryname in os.listdir('real_data/'):
            for filename in os.listdir('real_data/' + directoryname):
                N += 1;
                file = open('real_data/' + directoryname + '/' + filename, 'r');
                text = file.read();
                arrayOfWords = re.split(r'[&$_;,:?. !\n\t]+', text);
                mapOfAppearance = {};
                for term in mapOfQueryTerms.keys():
                    if term in arrayOfWords:
                        mapOfAppearance[term] = 1;
                for term in mapOfAppearance.keys():
                    mapOfQueryVectors[term] += 1;
        for term in mapOfQueryVectors.keys():
            if mapOfQueryVectors[term] != 0:
                # calculam idf
                mapOfQueryVectors[term] = numpy.log10(N/mapOfQueryVectors[term]);
        f = open("queryVector.txt", "w");
        print("Write query vector in file");
        for term in mapOfQueryTerms.keys():
            f.write(term + " " + str(mapOfQueryVectors[term]) + "\n");
    return mapOfQueryVectors;

def getRelevanceOfOrderedScores(scores):
    max = scores[0];
    relevances = [];
    for score in scores:
        # calculate relevances from scores
        if max == 0:
            relevances.append(0);
        else:
            relevances.append((4/max) * score - 1);
    return relevances;