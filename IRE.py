import os,string
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
import math
import numpy as np
import operator
from trie import*
#
def initStopwords():
    global stopwords
    f=open("stopwords.txt")
    for line in f:
            stopwords.add(PorterStemmer().stem(line[:-1]))
    f.close()

def validWord(word):
    if len(word)<2:return False
    for i in string.punctuation+string.digits+'—'+'ū':
        if i in word:
            return False
    return True

def removeStopwords(l):
    global stopwords
    for i in stopwords:
        while i in l:
            l.remove(i)
    return l

def stemLine(s):
    s=[i.lower() for i in word_tokenize(s)]
    s=[PorterStemmer().stem(i) for i in s]
    return s

def newDoc(docname):
    global vocabulary
    f=open('docs/'+docname,'r')
    doc={}
    doc['name']=docname
    doc['keywordlist']=[]
    doc['trie']=newTrie()
    doc['relevancy']=0
    for line in f:
            temp=[i.lower() for i in word_tokenize(line) if validWord(i.lower())]
            temp=removeStopwords(temp)
            doc['keywordlist'].extend([PorterStemmer().stem(i) for i in temp])
            #print(doc['keywordlist'])
    f.close()
    vocabulary.update(doc['keywordlist'])
    for s in doc['keywordlist']:
        doc['trie'] = trieAddString(doc['trie'], s)
    doc['keywordlist']=sorted(doc['keywordlist'])
    return doc

def docAndVocabInitializer(docnamelist):
    global doclist,vocabulary
    for doc in docnamelist:
        doclist.append(newDoc(doc))
    vocabulary=sorted(vocabulary)

def printDocumentsInfo():
    for doc in doclist:
        print("name: ",doc['name'])
        print("keywords: ",doc['keywordlist'])
        print()

def makeDocumentTermMatrix():
    global docTermMat,vocabulary,doclist
    for i in range(len(vocabulary)):
        docTermMat.append([])
        for j in range(len(doclist)):
            docTermMat[i].append(0)

    for keywordindex in range(len(vocabulary)):
        for docindex in range(len(doclist)):
            doc=doclist[docindex]
            keyword=vocabulary[keywordindex]
            docTermMat[keywordindex][docindex]=trieStringPresent(doc['trie'],keyword)

    #normalize
    for docindex in range(len(doclist)):
        max=0
        for keywordindex in range(len(vocabulary)):
            if max<docTermMat[keywordindex][docindex]:
                max=docTermMat[keywordindex][docindex]
        for keywordindex in range(len(vocabulary)):
            docTermMat[keywordindex][docindex]/=max

    #tf-idf
    idflist=[]
    for keywordindex in range(len(vocabulary)):
        count=0
        for docindex in range(len(doclist)):
            doc = doclist[docindex]
            keyword = vocabulary[keywordindex]
            if trieStringPresent(doc['trie'], keyword)>0:
                count+=1
        df=count
        idf=math.log(len(doclist)/count,2)
        idflist.append(idf)
    print(idflist)

    for keywordindex in range(len(vocabulary)):
        for docindex in range(len(doclist)):
            docTermMat[keywordindex][docindex]*=idflist[keywordindex]



def printDocTermMatrix(upto=20):
    global docTermMat, vocabulary, doclist
    print("\n\nDocTermMatrix")
    print(" "*20,end="")
    for doc in doclist:print(doc['name'],end=" ")
    print()
    for i in range(upto):
        print(vocabulary[i],end=" "*(20-len(vocabulary[i])))
        for docindex in range(len(doclist)):
            print("%.3f" % (docTermMat[i][docindex]),end=" "*len(doclist[docindex]['name']))
            '''else:
                print("%.3f" % (docTermMat[i][docindex]), end=" ")'''
        print()
    print()

def cosineSimilarity(vec1,vec2):
    vec1=np.array(vec1)
    vec2=np.array(vec2)
    sim=np.sum(vec1*vec2)/(np.sum(np.square(vec1))*np.sum(np.square(vec2))+1)
    return sim


def rankDocs(rawquery):
    global doclist,docdisplayorder,currentSemiRefinedQuery,currentRefinedQuery

    querywords = word_tokenize(rawquery)
    querywords = [i.lower() for i in querywords if validWord(i.lower())]
    querywords = removeStopwords(querywords)
    currentSemiRefinedQuery = querywords
    querywords = [PorterStemmer().stem(i) for i in querywords]
    currentRefinedQuery=querywords

    queryvector=[0.0 for i in range(len(vocabulary))]

    for i in range(len(vocabulary)):
        if vocabulary[i] in querywords:queryvector[i]=1.0
    simlistcdocs=[]
    for i in range(len(doclist)):
        docvect=[]
        for j in range(len(vocabulary)):
            docvect.append(docTermMat[j][i])
        simlistcdocs.append(cosineSimilarity(queryvector,docvect))

    docdisplayorderdict = {}
    for i in range(len(simlistcdocs)):
        doclist[i]['relevancy']=simlistcdocs[i]
        docdisplayorderdict[i]=simlistcdocs[i]
    docdisplayorderdict=sorted(docdisplayorderdict.items(),key=operator.itemgetter(1),reverse=True)
    docdisplayorder=[i[0] for i in docdisplayorderdict]

    print("Similarities: ")
    for i in docdisplayorderdict:print(i[1],end=" ")
    print("\n")


def showRankedDocSummary():
    global doclist,docdisplayorder,currentSemiRefinedQuery
    for i in docdisplayorder:
        print(doclist[i]['name'])
        f=open('docs/'+doclist[i]['name'])
        whole=f.read()
        whole=whole.split('\n')
        sentences=[]
        for i in whole:sentences.extend(i.split('.'))
        sentences=[i.lower() for i in sentences if len(i)>2]
        summary=[]
        for line in sentences:
            stemmedline=stemLine(line)
            for qword in currentRefinedQuery:
                if qword in stemmedline:
                    summary.append(line)
        if len(summary)==0:
            print("none")
        else:
            if len(summary)<5:
                n=len(summary)
            else: n=5
            for line in summary[:n]:
                print('...'+line+'...')
        print()
    print()

stopwords=set()
vocabulary=set()
doclist=[]
docTermMat=[]
docdisplayorder=[]
currentSemiRefinedQuery=[]
currentRefinedQuery=[]
LANGUAGE = "czech"
SENTENCES_COUNT = 10
initStopwords()
path=input("Directory for search: ")
docnamelist = os.listdir(path)
print(docnamelist)
docAndVocabInitializer(docnamelist)
printDocumentsInfo()
makeDocumentTermMatrix()
#printDocTermMatrix(50)

while True:
    query=input("Search: ")
    print()
    rankDocs(query)
    showRankedDocSummary()



