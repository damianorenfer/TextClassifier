#!/usr/bin/env python3
#-*- coding : utf-8 -*-

__author__ = 'Damiano Renfer & Mirco Nasuti'

import json
import datetime
import os
import random
import argparse
from DataExtraction import countWords

KNOWLEDGE_BASE_DIVISION = 0.8

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
    for k, v in text.items():
        if k in probabilities_positive_word:
            positive_probability += probabilities_positive_word[k]**v

    #Negative probability
    for k, v in text.items():
        if k in probabilities_negative_word:
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

def select_knownledge_texts(positive_texts, negative_texts, knowledge_base_division):
    positive_initial_size = len(positive_texts)
    negative_initial_size = len(negative_texts)
    knowledege_positive_list = []
    knowledege_negative_list = []

    #Positive texts
    i = 0
    while i < knowledge_base_division * positive_initial_size:
        r = random.randint(0, len(positive_texts)-1)
        text = positive_texts.pop(r)
        knowledege_positive_list.append(text)
        i += 1

    #Negative texts
    i = 0
    while i < knowledge_base_division * negative_initial_size:
        r = random.randint(0, len(negative_texts)-1)
        text = negative_texts.pop(r)
        knowledege_negative_list.append(text)
        i += 1

    return knowledege_positive_list, knowledege_negative_list, positive_texts, negative_texts

def naive_validate(knowledge_positive_texts, knowledge_negative_texts, test_positive_texts, test_negative_texts) :
    #Calculate probabilities
    #Lists of dict : {word : probability}
    probabilities_positive_word = compute_probabilities(knowledge_positive_texts)
    probabilities_negative_word = compute_probabilities(knowledge_negative_texts)

    positive_texts_count = len(knowledge_positive_texts)
    negative_texts_count = len(knowledge_negative_texts)
    positive_apriori_probability = positive_texts_count / (positive_texts_count+negative_texts_count)

    #Classificaiton
    positive_match_count = 0
    negative_match_count = 0

    #Positive texts
    positive_test_texts_count = len(test_positive_texts)
    for i in range(0, positive_test_texts_count):
        text = test_positive_texts[i]
        is_positive = is_text_positive(text, probabilities_positive_word, probabilities_negative_word, positive_apriori_probability)
        if is_positive:
            positive_match_count += 1

    #Negative texts
    negative_test_texts_count = len(test_negative_texts)
    for i in range(0, negative_test_texts_count):
        text = test_negative_texts[i]
        is_positive = is_text_positive(text, probabilities_positive_word, probabilities_negative_word, positive_apriori_probability)
        if not is_positive:
            negative_match_count += 1

    positive_precision = positive_match_count/positive_test_texts_count
    negative_precision = negative_match_count/negative_test_texts_count
    average_precision = (positive_precision + negative_precision)/2

    #Display results
    print("Positive texts : %s" % len(test_positive_texts))
    print("Positive texts matches : %s" % positive_match_count)
    print("Positive precision : %s" % positive_precision)
    print("Negative texts : %s" % len(test_negative_texts))
    print("Negative texts matches : %s" % negative_match_count)
    print("Negative precision : %s" % negative_precision)
    print("Average precision : %s" % average_precision)


def cross_validate(n, positive_texts, negative_texts):
    """
    N Folder - cross validation
    """

    folder_pos = []
    folder_neg = []

    offset_pos = int(len(positive_texts) / n)
    offset_neg = int(len(negative_texts) / n)

    for i in range(0, n):
        folder_pos.append(positive_texts[i*offset_pos:(i+1)*offset_pos])
        folder_neg.append(negative_texts[i*offset_neg:(i+1)*offset_neg])

    for i in range(0, n):
        knowledge_positive_texts = []
        knowledge_negative_texts = []
        for j in range(0, n):
            if(i!=j):
                knowledge_positive_texts += folder_pos[j]
                knowledge_negative_texts += folder_neg[j]

        #Calculate probabilities
        #Lists of dict : {word : probability}
        probabilities_positive_word = compute_probabilities(knowledge_positive_texts)
        probabilities_negative_word = compute_probabilities(knowledge_negative_texts)

        positive_texts_count = len(knowledge_positive_texts)
        negative_texts_count = len(knowledge_negative_texts)
        positive_apriori_probability = positive_texts_count / (positive_texts_count+negative_texts_count)

        #Classificaiton
        positive_match_count = 0
        negative_match_count = 0

        #Positive texts
        positive_test_texts_count = len(test_positive_texts)
        for j in range(0, positive_test_texts_count):
            text = test_positive_texts[j]
            is_positive = is_text_positive(text, probabilities_positive_word, probabilities_negative_word, positive_apriori_probability)
            if is_positive:
                positive_match_count += 1

        #Negative texts
        negative_test_texts_count = len(test_negative_texts)
        for j in range(0, negative_test_texts_count):
            text = test_negative_texts[j]
            is_positive = is_text_positive(text, probabilities_positive_word, probabilities_negative_word, positive_apriori_probability)
            if not is_positive:
                negative_match_count += 1

        positive_precision = positive_match_count/positive_test_texts_count
        negative_precision = negative_match_count/negative_test_texts_count
        average_precision = (positive_precision + negative_precision)/2

        #Display results
        print("Positive texts : %s" % len(test_positive_texts))
        print("Positive texts matches : %s" % positive_match_count)
        print("Positive precision : %s" % positive_precision)
        print("Negative texts : %s" % len(test_negative_texts))
        print("Negative texts matches : %s" % negative_match_count)
        print("Negative precision : %s" % negative_precision)
        print("Average precision : %s" % average_precision)


if __name__ == "__main__":

    #Args parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tagged", help="Use tagged texts", action="store_true")
    parser.add_argument("-d", "--division", help="Corpus division, percent of training texts", type=float)
    args = parser.parse_args()

    #Lists of dict : {word : count}
    pathPosFiles = './data/pos/'
    pathNegFiles = './data/neg/'
    pathPosTaggedFiles = './data/tagged/pos/'
    pathNegTaggedFiles = './data/tagged/neg/'
    uselessWordsFileName = './data/frenchST.txt'

    if not args.tagged:
        positive_texts = countWords(pathPosFiles, uselessWordsFileName, False)
        negative_texts = countWords(pathNegFiles, uselessWordsFileName, False)
    else:
        positive_texts = countWords(pathPosTaggedFiles, uselessWordsFileName, True)
        negative_texts = countWords(pathNegTaggedFiles, uselessWordsFileName, True)

    if args.division:
        knowledge_base_division = args.division
    else:
        knowledge_base_division = KNOWLEDGE_BASE_DIVISION

    knowledge_positive_texts, knowledge_negative_texts, test_positive_texts, test_negative_texts = select_knownledge_texts(list(positive_texts), list(negative_texts), knowledge_base_division)
    #naive_validate(knowledge_positive_texts, knowledge_negative_texts, test_positive_texts, test_negative_texts)
    cross_validate(5, positive_texts, negative_texts)

    #load probabilities from file
    #probabilities_positive_word, probabilities_negative_word, positive_apriori_probability = load_probabilities("knowledge_base-01-04-2014_10-59-53.json")
    #save_probabilities(probabilities_positive_word, probabilities_negative_word, positive_apriori_probability)


