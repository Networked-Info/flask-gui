#! /usr/bin/python
# -*- coding: utf-8 -*-

import json
import nltk
import shelve
import time
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from math import log10, sqrt
from pydoc import doc

stemmer = SnowballStemmer("english")
stop = set(stopwords.words('english'))

# Calculate the term frequency of each term in each document
def insertIndex(text,i):
    i = str(i)
    if not s.has_key(text):
        s[text] = {}
        tmp = {}
        tmp.update({i:1})
        s[text] = tmp
    else:
        if i not in s[text]:
            tmp = s[text]
            tmp.update({i:1})
            s[text] = tmp
        else :
            tmp = s[text]
            tmp[i] = tmp[i] + 1
            s[text] = tmp
     
# processs the text to clear the noisy data
def processText(text, i):
    tokenizer = RegexpTokenizer(r'\w+')
    words = tokenizer.tokenize(text)
    for word in words: 
        # case folding each word
        word = word.lower()
        # remove stop words
        if word in stop:
            continue
        # stemming each word
        word = stemmer.stem(word).encode('utf-8')
        insertIndex(word, i)
        #insertFrequency(word, i)

# With document term frequency to calculate the weight of document term and the length of document
def updateD_tfidf():
    dtTerm = {}
    for term in s:
        termDoc = s[term]
        df = len(termDoc)
        for doc in termDoc:
            tmp = (1 + log10(termDoc[doc]))*(log10(documentN)-log10(df))
            dtTerm[doc] = tmp
            if l.has_key(doc):
                tmpl = l[doc]
                tmpl = sqrt(pow(tmpl,2) + pow(tmp,2))
                l[doc] = tmpl
            else:
                l[doc] = tmp
        dt[term] = dtTerm
        dtTerm = {} 

# normalize the weight of document term with length of document
def cosine_norm():
    for term in dt:
        termDoc = dt[term]
        tempTermDoc = {}
        for docId in termDoc:
            lenghth = l[docId]
            result = termDoc[docId] / lenghth
            tempTermDoc[docId] = result
        n[term] = tempTermDoc
        tempTermDoc = {}

# copy the frequency posting list into shelve file
def copyIndexFrequency():
    shelv_index = {}
    for token in s:
        shelv_index[token] = s[token]

# update the weight of document term of term in each document into dictionary in document unit
def update_dtw():
    for token in dt:
        tokenDocList = dt[token]
        for doc in tokenDocList:
            if not dtw.has_key(doc):
                dtw[doc] = {str(token) : tokenDocList[doc]}
            else :
                if not dtw[doc].has_key(token):
                    tokenlist = dtw[doc]
                    tokenlist[token] = tokenDocList[doc]
                    dtw[doc] = tokenlist

#update the normalized weight of document term of term in each document into dictionary in document unit                    
def update_dtwn():
    for doc in dtw:
        new_tokenWeightList = {}
        length = l[doc]
        tokenWeightList = dtw[doc]
        for token in tokenWeightList:
            normWeight = tokenWeightList[token] / length
            new_tokenWeightList[token] = normWeight
        dtw_n[doc] = new_tokenWeightList

'''
Start from here
'''
# take the start time
start_time = time.time()

# the shelve file to store posting list
s = {}
# the shelve file to store docId and weight for each term
dt = {}
# the shelve file to store the term weight in each document
dtw= {}
# the shelve file store the length of each document
l = {}
# the shelve file stores the normalized weight of each term in each doc
dtw_n = {}
# the shelve file stores the normalized weight of each term
n = shelve.open('shelv_normalizedWeight', writeback = False)
# import json file as dictionary
with open('films_corpus.json') as data_file:
    dictionary = json.load(data_file)
    json.dump(dictionary,open('doc_data.json','w'))

# the total number of document in this collection
documentN = len(dictionary)
     
for i in dictionary:
    fdict = dictionary[i]
    i = i.encode('utf-8')
    i = int(i)
    
    ''' TEXT '''
    text = fdict['text']
    # normalize the contents in text and put it into inverted index
    sens = nltk.sent_tokenize(text)
    # remove punctuation and add each word into index list
    for sent in sens:
        processText(sent, i)
        
    ''' TITLE '''
    titleString = fdict['title']
    # normalize title and add it into corpus
    processText(titleString, i)
  
# update the tf-idf weight of term in documents
updateD_tfidf()
# calculate the normalized weight of document term
cosine_norm()
# update the weight of document term into weight of document term for each document
update_dtw()
# update the normalized weight of document term into weight of document term for each document
update_dtwn()

# store weight posting list info into shelv_index
shelv_index = shelve.open('shelv_index', writeback = False)
for token in s:
    shelv_index[token] = s[token]
shelv_index.close()

# store weight of document term for each document info into shelv_dtw
shelv_dtw = shelve.open('shelv_dtw', writeback = False)
for doc in dtw:
    shelv_dtw[doc] = dtw[doc]
shelv_dtw.close()

# store normalized weight of document term for each document info into shelv_dtw_n
shelv_dtwn = shelve.open('shelv_dtwn', writeback = False)
for doc in dtw_n:
    shelv_dtwn[doc] = dtw_n[doc]
shelv_dtwn.close()

# close n
n.close()

print("--- Running time is %s seconds ---" % (time.time() - start_time))
                    
            

    

    
