#-*- coding: utf-8 -*-

import re
import locale
import os

def parseFile(fileName):
    with open(fileName, 'r', encoding='utf-8') as f:
        text = f.read()
        f.close()
    return re.findall('[\w]+', text, re.UNICODE)

def countWords(pathToFiles, uselessWordsFileName):
    filesList = os.listdir(pathToFiles)

    listDico = []
    uselessWords = parseFile(uselessWordsFileName)
    
    for fileName in filesList:
        wordCounter = {}
        words = parseFile(pathToFiles + fileName)
        for word in words:
            if word not in uselessWords:
                if word in wordCounter:
                    wordCounter[word] += 1
                else:
                    wordCounter[word] = 1
        listDico.append(wordCounter)
    return listDico

if __name__ == "__main__":
    pathPosFiles = '../../pos/'
    pathNegFiles = '../../neg/'
    uselessWordsFileName = '../../frenchST.txt'

    posListDict = countWords(pathPosFiles, uselessWordsFileName)
    negListDict = countWords(pathNegFiles, uselessWordsFileName)

    print(negListDict[4])
    
    
