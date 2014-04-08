#-*- coding: utf-8 -*-

import re
import locale
import os

def parseFile(fileName):
    with open(fileName, 'r', encoding='utf-8') as f:
        text = f.read()
        f.close()
    return re.findall('\w+', text, re.UNICODE)

def parseTaggedFile(fileName):
    with open(fileName, 'r', encoding='utf-8') as f:
        text = f.read()
        f.close()
    return re.findall('(\w+)\n', text, re.UNICODE)

def countWords(pathToFiles, uselessWordsFileName, tagged):
    listDico = []
    
    filesList = os.listdir(pathToFiles)
    uselessWords = parseFile(uselessWordsFileName)
    
    for fileName in filesList:
        wordCounter = {}
        
        if tagged:
            words = parseTaggedFile(pathToFiles + fileName)
        else:
            words = parseFile(pathToFiles + fileName)
            
        for word in words:
            if word not in uselessWords:
                if word in wordCounter:
                    wordCounter[word] += 1
                else:
                    wordCounter[word] = 1
        listDico.append(wordCounter)
    return listDico
    
