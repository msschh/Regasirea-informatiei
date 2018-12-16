import re
import os.path
import numpy
from util import getMapOfQueryTerms, getMapOfQueryVector, getRelevanceOfOrderedScores

sourceDirectory = 'pa3-data/Training';

def getPostingLists(mapOfQueryTerms):
    if os.path.exists('postingLists.txt'):
        print("Read posting lists from file");
        for line in open('postingLists.txt', 'r'):
            arrayOfWords = re.split(r'[ \t\n]+', line);
            n = len(arrayOfWords);
            idx = 0
            mapOfQueryTerms[arrayOfWords[0]] = {};
            while idx + 7 < n:
                mapOfQueryTerms[arrayOfWords[0]][arrayOfWords[idx + 1]] = {};
                mapOfQueryTerms[arrayOfWords[0]][arrayOfWords[idx + 1]]['rawScore'] = [float(arrayOfWords[idx + 2]),
                                                        float(arrayOfWords[idx + 3]), float(arrayOfWords[idx + 4])];
                mapOfQueryTerms[arrayOfWords[0]][arrayOfWords[idx + 1]]['normScore'] = [float(arrayOfWords[idx + 5]),
                                                        float(arrayOfWords[idx + 6]), float(arrayOfWords[idx + 7])];
                idx += 7;
        return mapOfQueryTerms;
    else:
        print("Create posting lists.");
        terms = [];
        L = 0;
        url = '';
        for line in open(sourceDirectory + '/queries', encoding="utf-8"):
            arrayOfWords = re.split(r'[ \t\n]+', line);
            if arrayOfWords[0] == 'query:':
                if L != 0:
                    for term in terms:
                        [t,h,b] = mapOfQueryTerms[term][url]['rawScore'];
                        if t == 0:
                            normt = 0;
                        else:
                            normt = (1 + numpy.log10(t))/L;
                        if h == 0:
                            normh = 0;
                        else:
                            normh = (1 + numpy.log10(h))/L;
                        if b == 0:
                            normb = 0;
                        else:
                            normb = (1 + numpy.log10(b))/L;
                        mapOfQueryTerms[term][url]['normScore'] = [normt, normh, normb];
                terms = arrayOfWords[1:-1];
                L = 0;
            else:
                if arrayOfWords[1] == 'url:':
                    if L != 0:
                        for term in terms:
                            [t,h,b] = mapOfQueryTerms[term][url]['rawScore'];
                            if t == 0:
                                normt = 0;
                            else:
                                normt = (1 + numpy.log10(t))/L;
                            if h == 0:
                                normh = 0;
                            else:
                                normh = (1 + numpy.log10(h))/L;
                            if b == 0:
                                normb = 0;
                            else:
                                normb = (1 + numpy.log10(b))/L;
                            mapOfQueryTerms[term][url]['normScore'] = [normt, normh, normb];
                    L = 0;
                    url = arrayOfWords[2];
                    for term in terms:
                        mapOfQueryTerms[term][arrayOfWords[2]] = {};
                        mapOfQueryTerms[term][arrayOfWords[2]]['rawScore'] = [0,0,0];
                        mapOfQueryTerms[term][arrayOfWords[2]]['normScore'] = [0,0,0];
                if arrayOfWords[1] == 'title:':
                    L += len(arrayOfWords[2:-1]);
                    for word in arrayOfWords[2:-1]:
                        for term in terms:
                            if word == term:
                                mapOfQueryTerms[term][url]['rawScore'][0] += 1;
                if arrayOfWords[1] == 'header:':
                    L += len(arrayOfWords[2:-1]);
                    for word in arrayOfWords[2:-1]:
                        for term in terms:
                            if word == term:
                                mapOfQueryTerms[term][url]['rawScore'][1] += 1;
                if arrayOfWords[1] == 'body_hits:':
                    mapOfQueryTerms[arrayOfWords[2]][url]['rawScore'][2] += len(arrayOfWords[3:-1]);
                if arrayOfWords[1] == 'body_length:':
                    L += int(arrayOfWords[2]);
        if L != 0:
            for term in terms:
                [t, h, b] = mapOfQueryTerms[term][url]['rawScore'];
                if t == 0:
                    normt = 0;
                else:
                    normt = (1 + numpy.log10(t))/L;
                if h == 0:
                    normh = 0;
                else:
                    normh = (1 + numpy.log10(h))/L;
                if b == 0:
                    normb = 0;
                else:
                    normb = (1 + numpy.log10(b))/L;
                mapOfQueryTerms[term][url]['normScore'] = [normt, normh, normb];
        f = open("postingLists.txt", "w");
        print("Write posting lists in file");
        for key in mapOfQueryTerms.keys():
            f.write(key + " ");
            for url in mapOfQueryTerms[key].keys():
                f.write(url + " ");
                f.write(str(mapOfQueryTerms[key][url]['rawScore'][0]) + " " + str(mapOfQueryTerms[key][url]['rawScore'][1]) + " ");
                f.write(str(mapOfQueryTerms[key][url]['rawScore'][2]) + " " + str(mapOfQueryTerms[key][url]['normScore'][0]) + " ");
                f.write(str(mapOfQueryTerms[key][url]['normScore'][1]) + " " + str(mapOfQueryTerms[key][url]['normScore'][2]) + " ");
            f.write("\n");
        return mapOfQueryTerms;

def calculateDocumentScoresOfQuery(queryArray, postinglists, mapOfQueryVectors, weigths = [0.1, 0.1, 0.8], k = 10):
    documentScores = {};
    for term in queryArray:
        for doc in postinglists[term]:
            if doc in documentScores:
                documentScores[doc] += mapOfQueryVectors[term] * (weigths[0] * postinglists[term][doc]['normScore'][0]
                    + weigths[1] * postinglists[term][doc]['normScore'][1]
                    + weigths[2] * postinglists[term][doc]['normScore'][2]);
            else:
                documentScores[doc] = mapOfQueryVectors[term] * (weigths[0] * postinglists[term][doc]['normScore'][0]
                    + weigths[1] * postinglists[term][doc]['normScore'][1]
                    + weigths[2] * postinglists[term][doc]['normScore'][2]);
    return sorted(documentScores.values(), reverse=True)[:k];

def calculateNDCG(postinglists, mapOfQueryVectors, weigths):
    sumDoc = 0;
    sumQuery = 0;
    nrQuery = 0;
    sum = 0;
    idx = 1;
    relevances = [];
    for line in open(sourceDirectory + '/relevance', encoding="utf-8"):
        arrayOfWords = re.split(r'[ \n]+', line);
        if arrayOfWords[0] == 'query:':
            if sum != 0:
                sumDoc = 0;
                for item in relevances:
                    sumDoc += (2 ** item - 1) / numpy.log2(1 + idx);
                sumQuery += sumDoc / sum;
            scores = calculateDocumentScoresOfQuery(arrayOfWords[1:-1], postinglists, mapOfQueryVectors, weigths);
            relevances = getRelevanceOfOrderedScores(scores);
            sum = 0;
            idx = 1;
            nrQuery += 1;
        else:
            if arrayOfWords[1] == 'url:':
                sum += (2 ** float(arrayOfWords[3]) - 1) / numpy.log2(1 + idx);
                idx += 1;
    if sum != 0:
        sumDoc = 0;
        for item in relevances:
            sumDoc += (2 ** item - 1) / numpy.log2(1 + idx);
        sumQuery += sumDoc / sum;
    return sumQuery / nrQuery;

def calculateCosineSim():
    mapOfQueryTerms = getMapOfQueryTerms();
    postinglists = getPostingLists(mapOfQueryTerms);
    mapOfQueryVectors = getMapOfQueryVector(mapOfQueryTerms);
    ndcgScore = calculateNDCG(postinglists, mapOfQueryVectors, [0, 0.97, 0.03]);
    print(ndcgScore);

    """ 
        0 0.29 0.71 
            test - 65.42
            training - 79.48

        0 0.97 0.03
            training - 85.65

    bestw1 = 0;
    bestw2 = 0;
    bestw3 = 0;
    bestScore = 0;
    w1 = 0;
    w2 = 0;
    w3 = 0;
    while w1 <= 1:
        while w2 <= (1 - w1):
            w3 = 1 - w1 - w2;
            ndcgScore = calculateNDCG(postinglists, mapOfQueryVectors, [w1, w2, w3]);
            if ndcgScore > bestScore:
                bestw1 = w1;
                bestw2 = w2;
                bestw3 = w3;
                bestScore = ndcgScore;
            w2 += 0.01
        w1 += 0.01;
    print(str(bestw1) + " " + str(bestw2) + " " + str(bestw3) + " " + str(bestScore));
    """