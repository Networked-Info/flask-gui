# -*- coding: utf-8 -*-
from flask import *
from heapq import heappush, heappop
import heapq
import querysearch

app = Flask(__name__)

temp_query = ""

@app.route("/")
def search():
    return render_template('page_query.html')

@app.route("/results", defaults={'page': 1}, methods=['GET','POST'])
@app.route("/results/<page>", methods=['GET','POST'])
def results(page):
    global temp_query
    if type(page) is not int:
        page = int(page.encode('utf-8'))
    try:        
        if temp_query == "":
            query = ""
            query = request.form['query'].encode('utf-8')
            query = query + " " + request.form['director'].encode('utf-8')
            query = query + " " + request.form['starring'].encode('utf-8')
            query = query + " " + request.form['location'].encode('utf-8')
            temp_query = query
        elif request.method == 'POST':
            query = ""
            query = request.form['query'].encode('utf-8')
            query = query + " " + request.form['director'].encode('utf-8')
            query = query + " " + request.form['starring'].encode('utf-8')
            query = query + " " + request.form['location'].encode('utf-8')
            temp_query = query
        else:
            query = temp_query
           
        search_results = querysearch.query_search(query)
            
        # get the number of results
        result_num = search_results[1]
         
        # if we find the results, extract title and text information from doc_data, else do nothing
        if result_num > 0:
            dicList = search_results[0]
            heap = []
            # extract the top 30 records with highest similarity scores
            for dic in dicList:
                if len(heap) < 30:
                    heapq.heappush(heap, (dicList[dic], dic))
                else :
                    minScore = heap[0]
                    if dicList[dic] < minScore[0]:
                        heapq.heapreplace(heap, (dicList[dic], dic))
            # pop the records from heap into list
            rList = []
            while heap:
                rList.append(heapq.heappop(heap))
                
            # the final record number    
            finalResult_num = len(rList)
            
            # generate output contents
            resList = querysearch.completeWeight(rList)
            
            # generate output contents for current page
            start = 0 + (page-1)*10
            end = 10 + (page-1)*10
            resultsList = resList[start:end]
        else:
            resultsList = search_results[0]
         
        # get stop words list
        stop_list = search_results[2]
        
        return render_template('page_SERP.html', text=query, results=resultsList, res_num=finalResult_num, stop_len=len(stop_list), stops=stop_list, page_num=page)
    except KeyError:
        return "Problem"
     
@app.route("/documents/<res>", methods=['GET'])
def documents(res):
    query = res
    contents = querysearch.doc_search(str(query))
    contents = querysearch.pretty(contents)
    return render_template('page_targetArticle.html',film=contents)

@app.route("/morelikethis/<res>", methods=['GET','POST'])
def morelike(res):
    res = str(res.encode('utf-8'))
    res_list = querysearch.moreDocSearch(res)
    search_results = querysearch.completeWeight(res_list)
    return render_template('page_moreLike.html', results=search_results)
    
if __name__ == "__main__":
    app.run()
