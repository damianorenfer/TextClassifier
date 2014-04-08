#!/usr/bin/env python3
#-*- coding : utf-8 -*-

__author__ = 'Damiano Renfer & Mirco Nasuti'

import json
import datetime
import os
from DataExtraction import countWords

def compute_probabilities(words_list):
    """
    words_list is a list of dict : [{word1 : count1}, {word2 : count2}]
    returns a dict : {word: probabilities}
    """
    words_probabilities = {}
    words_occurrences = 0

    for w in words_list:
        for k, v in w.items():
            words_occurrences += v
            if k not in words_probabilities:
                words_probabilities[k] = v
            else:
                words_probabilities[k] += v

    words_count = len(words_probabilities)

    for k, v in words_probabilities.items():
        words_probabilities[k] = (v+1)/(words_count+words_occurrences)

    return words_probabilities

def is_text_positive(text, probabilities_positive_word, probabilities_negative_word, positive_apriori_probability):
    positive_probability = positive_apriori_probability
    negative_probability = 1.0-positive_apriori_probability

    #Positive probability
    for k, v in text:
        positive_probability += probabilities_positive_word[k]**v

    #Negative probability
    for k, v in text:
        negative_probability += probabilities_negative_word[k]**v

    return positive_probability > negative_probability

def save_probabilities(probabilities_positive_word, probabilities_negative_word, positive_apriori_probability):
    json_file_content = dict()
    json_file_content['probabilities_positive_word'] = probabilities_positive_word
    json_file_content['probabilities_negative_word'] = probabilities_negative_word
    json_file_content['positive_apriori_probability'] = positive_apriori_probability

    txt = json.dumps(json_file_content, sort_keys=True, indent=4, separators=(',', ':'))
    filename = "knowledge_base/knowledge_base-%s.json" % datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(txt)

def load_probabilities(filename):
    probabilities_positive_word = dict()
    probabilities_negative_word = dict()
    positive_apriori_probability = 0.0

    with open(filename, mode='r', encoding='utf-8') as f:
        txt = f.read()
        json_dict = json.loads(txt, encoding='utf-8')

        try:
            probabilities_positive_word = json_dict['probabilities_positive_word']
            probabilities_negative_word = json_dict['probabilities_negative_word']
            positive_apriori_probability = json_dict['positive_apriori_probability']
        except Exception as e:
            print(e)

    return probabilities_positive_word, probabilities_negative_word, positive_apriori_probability

if __name__ == "__main__":

    #Lists of dict : {word : count}
    pathPosFiles = './data/pos/'
    pathNegFiles = './data/neg/'
    pathPosTaggedFiles = './data/tagged/pos/'
    pathNegTaggedFiles = './data/tagged/neg/'
    uselessWordsFileName = './data/frenchST.txt'

    positive_texts = countWords(pathPosFiles, uselessWordsFileName, False)
    negative_texts = countWords(pathNegFiles, uselessWordsFileName, False)
    #positive_texts = countWords(pathPosTaggedFiles, uselessWordsFileName, True)
    #negative_texts = countWords(pathNegTaggedFiles, uselessWordsFileName, True)
    test_texts = []

    print("data loaded")

    #Lists of dict : {word : probability}
    probabilities_positive_word = compute_probabilities(positive_texts)
    probabilities_negative_word = compute_probabilities(negative_texts)

    positive_texts_count = len(positive_texts)
    negative_texts_count = len(negative_texts)
    positive_apriori_probability = positive_texts_count / (positive_texts_count+negative_texts_count)

    #load probabilities from file
    #probabilities_positive_word, probabilities_negative_word, positive_apriori_probability = load_probabilities("knowledge_base-01-04-2014_10-59-53.json")

    print(probabilities_positive_word)
    print(probabilities_negative_word)
    print(positive_apriori_probability)

    #save_probabilities(probabilities_positive_word, probabilities_negative_word, 0.5)


