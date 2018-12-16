import re
import os.path
import numpy
from util import getMapOfQueryTerms, getMapOfQueryVector, getRelevanceOfOrderedScores

sourceDirectory = 'pa3-data/Training';

def getPostingLists(mapOfQueryTerms):
    if os.path.exists('postingListsBM25F.txt'):
        print("Read posting lists from file");
        for line in open('postingListsBM25F.txt', 'r'):
            arrayOfWords = re.split(r'[ \t\n]+', line);
            n = len(arrayOfWords);
            idx = 0
            mapOfQueryTerms[arrayOfWords[0]] = {};
            while idx + 8 < n:
                mapOfQueryTerms[arrayOfWords[0]][arrayOfWords[idx + 1]] = {};
                mapOfQueryTerms[arrayOfWords[0]][arrayOfWords[idx + 1]]['rawScore'] = [float(arrayOfWords[idx + 2]),
                                                        float(arrayOfWords[idx + 3]), float(arrayOfWords[idx + 4])];
                mapOfQueryTerms[arrayOfWords[0]][arrayOfWords[idx + 1]]['length'] = [float(arrayOfWords[idx + 5]),
                                                        float(arrayOfWords[idx + 6]), float(arrayOfWords[idx + 7])];
                mapOfQueryTerms[arrayOfWords[0]][arrayOfWords[idx + 1]]['pagerank'] = int(arrayOfWords[idx + 8]);
                idx += 8;
        return mapOfQueryTerms;
    else:
        print("Create posting lists.");
        terms = [];
        Lt = 0;
        Lh = 0;
        Lb = 0;
        url = '';
        for line in open(sourceDirectory + '/queries', encoding="utf-8"):
            arrayOfWords = re.split(r'[ \t\n]+', line);
            if arrayOfWords[0] == 'query:':
                if Lt != 0 or Lh != 0 or Lb != 0:
                    for term in terms:
                        mapOfQueryTerms[term][url]['length'] = [Lt, Lh, Lb];
                terms = arrayOfWords[1:-1];
                Lt = 0;
                Lh = 0;
                Lb = 0;
            else:
                if arrayOfWords[1] == 'url:':
                    if Lt != 0 or Lh != 0 or Lb != 0:
                        for term in terms:
                            mapOfQueryTerms[term][url]['length'] = [Lt, Lh, Lb];
                    Lt = 0;
                    Lh = 0;
                    Lb = 0;
                    url = arrayOfWords[2];
                    for term in terms:
                        mapOfQueryTerms[term][arrayOfWords[2]] = {};
                        mapOfQueryTerms[term][arrayOfWords[2]]['rawScore'] = [0,0,0];
                        mapOfQueryTerms[term][arrayOfWords[2]]['length'] = [0,0,0];
                        mapOfQueryTerms[term][arrayOfWords[2]]['pagerank'] = 0;
                if arrayOfWords[1] == 'title:':
                    Lt += len(arrayOfWords[2:-1]);
                    for word in arrayOfWords[2:-1]:
                        for term in terms:
                            if word == term:
                                mapOfQueryTerms[term][url]['rawScore'][0] += 1;
                if arrayOfWords[1] == 'header:':
                    Lh += len(arrayOfWords[2:-1]);
                    for word in arrayOfWords[2:-1]:
                        for term in terms:
                            if word == term:
                                mapOfQueryTerms[term][url]['rawScore'][1] += 1;
                if arrayOfWords[1] == 'body_hits:':
                    mapOfQueryTerms[arrayOfWords[2]][url]['rawScore'][2] += len(arrayOfWords[3:-1]);
                if arrayOfWords[1] == 'body_length:':
                    Lb += int(arrayOfWords[2]);
                if arrayOfWords[1] == 'pagerank:':
                    for term in terms:
                        mapOfQueryTerms[term][url]['pagerank'] = arrayOfWords[2];

        if Lt != 0 or Lh != 0 or Lb != 0:
            for term in terms:
                mapOfQueryTerms[term][url]['length'] = [Lt, Lh, Lb];
        f = open("postingListsBM25F.txt", "w");
        print("Write posting lists in file");
        for key in mapOfQueryTerms.keys():
            f.write(key + " ");
            for url in mapOfQueryTerms[key].keys():
                f.write(url + " ");
                f.write(str(mapOfQueryTerms[key][url]['rawScore'][0]) + " " + str(mapOfQueryTerms[key][url]['rawScore'][1]) + " ");
                f.write(str(mapOfQueryTerms[key][url]['rawScore'][2]) + " " + str(mapOfQueryTerms[key][url]['length'][0]) + " ");
                f.write(str(mapOfQueryTerms[key][url]['length'][1]) + " " + str(mapOfQueryTerms[key][url]['length'][2]) + " ");
                f.write(str(mapOfQueryTerms[key][url]['pagerank']) + " ");
            f.write("\n");
        return mapOfQueryTerms;

def getAverageLengthOfField(postinglists):
    if os.path.exists('averageLength.txt'):
        print("Read average length of fields from file");
        file = open("averageLength.txt", 'r');
        arrayOfTerms = re.split(r'[ \n]+', file.read());
        return [float(arrayOfTerms[0]),float(arrayOfTerms[1]),float(arrayOfTerms[2])];
    else:
        print("Calculate average length of fields from file");
        mapOfDocuments = {};
        lenT = 0;
        lenH = 0;
        lenB = 0;
        size = 0;
        for term in postinglists.keys():
            for doc in postinglists[term].keys():
                if doc not in mapOfDocuments:
                    mapOfDocuments[doc] = 1;
                    size += 1;
                    lenT += postinglists[term][doc]['length'][0];
                    lenH += postinglists[term][doc]['length'][1];
                    lenB += postinglists[term][doc]['length'][2];
        avlenT = lenT / size;
        avlenH = lenH / size;
        avlenB = lenB / size;
        f = open("averageLength.txt", "w");
        print("Write query terms in file");
        f.write(str(avlenT) + " " + str(avlenH) + " " + str(avlenB));
        return [avlenT, avlenH, avlenB];

def calculateNormScoreFromRawScore(postinglistOfTermInDoc, avlen, Bf):
    ftfT = postinglistOfTermInDoc['rawScore'][0] / (1 + Bf[0] * (postinglistOfTermInDoc['length'][0]/avlen[0] - 1));
    ftfH = postinglistOfTermInDoc['rawScore'][1] / (1 + Bf[1] * (postinglistOfTermInDoc['length'][1]/avlen[1] - 1));
    ftfB = postinglistOfTermInDoc['rawScore'][2] / (1 + Bf[2] * (postinglistOfTermInDoc['length'][2]/avlen[2] - 1));
    return [ftfT, ftfH, ftfB];

def calculateWeigthOfTermInDocument(postinglistOfTermInDoc, avlen, Bf, Wf):
    [ftfT, ftfH, ftfB] = calculateNormScoreFromRawScore(postinglistOfTermInDoc, avlen, Bf);
    w = Wf[0] * ftfT + Wf[1] * ftfH + Wf[2] * ftfB;
    return w;

def calculateScoreOfQuery(queryArray, postinglists, mapOfQueryVectors, avlen, Bf, Wf, K1, lambda1, k = 10):
    documentScores = {};
    for term in queryArray:
        for doc in postinglists[term]:
            w = calculateWeigthOfTermInDocument(postinglists[term][doc], avlen, Bf=Bf, Wf=Wf);
            if doc in documentScores:
                documentScores[doc] += w / (w + K1) * mapOfQueryVectors[term];
            else:
                documentScores[doc] = w / (w + K1) * mapOfQueryVectors[term];
                if postinglists[term][doc]['pagerank'] != 0:
                    documentScores[doc] += lambda1 * numpy.log10(postinglists[term][doc]['pagerank']);
    return sorted(documentScores.values(), reverse=True)[:k];

def calculateNDCG(postinglists, mapOfQueryVectors, avlen, Bf = [0, 8, 8], Wf = [0, 0.97, 0.03], K1 = 1.5, lambda1 = 2):
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
            scores = calculateScoreOfQuery(arrayOfWords[1:-1], postinglists, mapOfQueryVectors, avlen, Bf=Bf, Wf=Wf, K1=K1, lambda1=lambda1);
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

def calculateBM25F():
    mapOfQueryTerms = getMapOfQueryTerms();
    postinglists = getPostingLists(mapOfQueryTerms);
    avlen = getAverageLengthOfField(postinglists);
    mapOfQueryVector = getMapOfQueryVector(mapOfQueryTerms);
    ndcgScore = calculateNDCG(postinglists, mapOfQueryVector, avlen);
    print(ndcgScore);