#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: djokester
Samriddhi Sinha,
IIT Kharagpur
"""

from sklearn.neural_network import MLPClassifier
import lingatagger.sentence as sent
import lingatagger.gender as gndr
import lingatagger.genderlist as gndrlist
import lingatagger.tokenizer as tok
import gensim
import logging
import re
import sangita_data.hindi.sentences.loadsent as sents
import operator 

def genderdecode(genderTag):
    """
    one-hot decoding for the gender tag predicted by the classfier
    Dimension = 2. 
    """
    index, value = max(enumerate(genderTag), key=operator.itemgetter(1))
    if index == 0:
        return 'm'
    if index == 1:
        return 'f'
    if index == 2:
        return 'any'
    
def numericTagger(instr):
    """
    numericTagger is a regex based tagger that tags Numbers with the tag "num"
    :param instr: Can be a string, list of tokens or a list of tuples. 
    It can be the string to be tagged, tokenized string or even a pre-tagged string 
    :type inst: string, list of strings, list of tuples
    
    :return: Returns a List of tuples of the form [(token1, genderTag), (token2, genderTag)...]
    :rtype: List of Tuples.
    """
    lst = type([1, 2, 3])
    tup = type(("Hello", "Hi"))
    string = type("Hello")
    num_match = re.compile(r'([०१२३४५६७८९]+[\.\,]*)+[०१२३४५६७८९]+|([-+]*\d+[\.\,]*)+\d+|([०१२३४५६७८९]+|\d+)')
    if type(instr) == lst:
        for index, item in enumerate(instr):
            if type(item) == tup:
                if num_match.search(str(item[0])):
                    instr[index] = (instr[index][1], 'num')
            else:
                if num_match.search(str(item)):
                    instr[index] = (instr[index], 'num')
    else: 
        if type(instr) == string:
            instr = tok.tokenize(instr)
            numericTagger(instr)
        else:
            print("not supported")

    return instr

def defaultTagger(instr):
    """
    defaultTagger tags untagged tokens with "any"
    :param instr: Can be a string, list of tokens  
    It can be the string to be tagged, tokenized string 
    :type instr: string, list of strings, list of tuples
    
    :return: Returns a List of tuples of the form [(token1, genderTag), (token2, genderTag)...]
    :rtype: List of Tuples.
    """
    lst = type([1, 2, 3])
    tup = type(("Hello", "Hi"))
    string = type("Hello")
    if type(instr) == lst:
        for index, item in enumerate(instr):
            if type(item) != tup:
                instr[index] = (instr[index], 'any')
    else: 
        if type(instr) == string:
            instr = tok.tokenize(instr)
            defaultTagger(instr)
        else:
            print("not supported")
    return instr

def lookupTagger(instr):
    """
    lookupTagger looks up the Dictionary formatches and tags the token if a match is found
    :param instr: Can be a string, list of tokens or a list of tuples
    It can be the string to be tagged, tokenized string or a pre-tragged list of tokens.
    :type instr: string, list of strings, list of tuples
    
    :return: Returns a List of tuples of the form [(token1, genderTag), (token2, genderTag)...]
    :rtype: List of Tuples.
    """
    lst = type([1, 2, 3])
    tup = type(("Hello", "Hi"))
    string = type("Hello")
    gndrlst = gndrlist.drawlist()
    words = []
    genders = []
    for item in gndrlst:
        words.append(item.split("\t")[0])
        if(len(item.split("\t"))>2):
            genders.append("any")
        else:
            genders.append(item.split("\t")[1])
        
    tokens = set(words)
    
    if(type(instr) == lst):
        for index,item in enumerate(instr):
            if(type(item) == tup):
                if item[0] in tokens:
                    tag = genders[words.index(item[0])]
                    instr[index] = (instr[index][0],tag)
            else:
                if(type(item) != tup):
                    if item in tokens:
                        tag = genders[words.index(item)]
                        instr[index] = (instr[index], tag)
                
    else: 
        if(type(instr) == string):
            instr = tok.tokenize(instr)
            lookupTagger(instr)
            
        else:
            print("not supported")

    return(instr)

def genderclassify(sentence):
    """
    genderclassify tags with the help of multilayer perceptron classifier 
    trained over word vectors created with gensim's word2vec
    :param sentence: string to be tokenized and tagged
    :type sentence: string
    
    :return: Returns a List of tuples of the form [(token1, genderTag), (token2, genderTag)...]
    :rtype: List of Tuples.
    """
    sentences = sent.drawlist()
    sentences2 = sents.drawlist()
    sentences2.append(sentence)
    sentences = sentences + sentences2
    sentences = [tok.wordtokenize(i) for i in sentences]
    sentence = tok.wordtokenize(sentence)    

    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    model = gensim.models.Word2Vec(sentences, size =10,  min_count=1)

    pred = []
    
    for word in sentence:
        pred.append(model.wv[word].tolist())
        
    genders = gndr.drawlist()
    vector = [i[0] for i in genders]
    tags = [i[1] for i in genders]
    print(tags)    
    X = vector 
    y = tags
    clf = MLPClassifier(solver='sgd', alpha= 1e-5,
                            hidden_layer_sizes=(5, 2), random_state=1)
    clf.fit(X, y)
    predictions = clf.predict_proba(pred).tolist()

    predictions = [genderdecode(i) for i in predictions]
    print(predictions)
    
    for index,item in enumerate(sentence):
        sentence[index] = (sentence[index], predictions[index])
    
    return(sentence)
    
          
def Tagger(instr):
    """
    Combines the result of all four taggers for accuracte tagging
    :param sentence: string to be tokenized and tagged
    :type sentence: string
    
    :return: Returns a List of tuples of the form [(token1, genderTag), (token2, genderTag)...]
    :rtype: List of Tuples.
    """
    instr = genderclassify(instr)
    instr = lookupTagger(instr)
    instr = numericTagger(instr)
    instr = defaultTagger(instr)
    
    return(instr)

if __name__ == '__main__':
    input_str = 'नीरजः हाँ माता जी! स्कूल ख़त्म होते सीधा घर आऊँगा'

    print(Tagger(input_str))
    print(genderclassify(input_str))
    print(lookupTagger(input_str))
