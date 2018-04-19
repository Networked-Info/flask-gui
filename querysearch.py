#Illustrates a search method, just to check web interface

import shelve
import json
import heapq
from math import log10
from heapq import heappush, heappop
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

stemmer = SnowballStemmer("english")
stop = set(stopwords.words('english'))

# search the results with query
def query_search(query):
    res_list = []
    tmp_list = []
    stop_list = []
    searchedList = {}
    termWeight = {}
    res_doc_list = {}
    
    s = shelve.open('shelv_index')
    n = shelve.open('shelv_normalizedWeight')
    
    with open('doc_data.json') as data_file:
        dictionary = json.load(data_file)
    totalDoc = len(dictionary)
    
    count = 0
    for term in query.split():
        #remove punctuation
        tokenizer = RegexpTokenizer(r'\w+')
        term = tokenizer.tokenize(term)
        
        #case folding
        term = term[0].lower()
   
        # remove the stop words
        if term in stop:
            stop_list.append(term)
            continue
        
        # stemming each word
        term = stemmer.stem(term)
        
        # record the frequency of query term
        if term in searchedList:
            searchedList[term] = searchedList[term] + 1
            continue;
        else :
            searchedList[term] = 1

        # conjunctive search for final result 
        if s.has_key(term):
            if len(res_list) == 0 and count == 0:
                for dicId in s[term]:
                    res_list.append(dicId)
            else:
                for dicId in s[term]:
                    if dicId in res_list:
                        tmp_list.append(dicId)
                res_list = tmp_list
                tmp_list = []
        else :
            res_list = []
        count = count + 1
    
    if len(res_list) > 0:
        # calculate the weight of query term
        for term in searchedList:
            termWeight[term] = (1 + log10(searchedList[term]))*(log10(totalDoc) - log10(len(s[term])))
        
        # calculate the cosine similarity score
        for document in res_list:
            scores = 0
            for term in termWeight:
                termDoc = n[term]
                termDocWeight = termDoc[document]
                scores = scores + termWeight[term]*termDocWeight
            res_doc_list[document] = scores   
            
        return [res_doc_list,len(res_doc_list),stop_list]
    else:
        message = 'Unknown search term: '+query
        messageList = []
        messageList.append(message)
        return [messageList,0,stop_list]

# search the document contents from films_corpus    
def doc_search(query):
    json_data=open('doc_data.json').read()
    documents = json.loads(json_data)
    return documents[str(query)]

# add contents to final result with list of doc Ids
def complete(terms):
    json_data=open('doc_data.json').read()
    documents = json.loads(json_data)
    
    results = {}
    for term in terms:
        if not results.has_key(str(term)):
            results[term]=[]
            results[term].append(documents[str(term)]['title'])
            results[term].append(documents[str(term)]['text'])
    return results

# reverse the list extracted from heap to descending order
def completeWeight(terms):
    json_data = open('doc_data.json').read()
    documents = json.loads(json_data)
    
    results = []
    for i in range(len(terms)-1,-1,-1):
        result = (terms[i][0], documents[str(terms[i][1])]['title'], documents[str(terms[i][1])]['text'], str(terms[i][1]))
        results.append(result)
    return results

# pretty the contents
def pretty(contents):
    for term in contents:
        if type(contents[term]) is list:
            s = ""
            for item in contents[term]:
                s += item + ", "
            contents[term] = s
    return contents

# implement more like this search
def moreDocSearch(docId):
    documentWeights = shelve.open('shelv_dtwn')
    queryWeights = shelve.open('shelv_dtw')
    
    h = []
    resultsList = []
    documentN = len(documentWeights)
    
    queryWeight = queryWeights[docId]
    for doc in range(1,documentN + 1):
        document = documentWeights[str(doc)]
        score = 0
        for token in document:
            if queryWeight.has_key(token):
                score = score + document[token]*queryWeight[token]
        if len(h) < 10:
            heapq.heappush(h, (score, doc))
        else :
            if score < h[0]:
                heapq.heapreplace(h, (score, doc))
    while h:
        resultsList.append(heapq.heappop(h))
    
    documentWeights.close()
    queryWeights.close()
    
    return resultsList


