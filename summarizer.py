from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
import copy
import string
import operator

stopwords=set()

def initStopwords():
  global stopwords
  f = open("stopwords.txt")
  for line in f:
    stopwords.add(PorterStemmer().stem(line[:-1]))
  f.close()


class Extractor:
  @classmethod
  def getParas(cls, docname):
    paras = []
    sentences = []
    st = ""
    doc = ""
    ch = '-1'
    prev = None
    f = open(docname, 'r')
    for line in f:
      for ch in line:
        if ch != '\n':
          st += ch
        if ch == '.':
          sentences.append(st)
          st = ""
        if ch == '\n' and prev == '\n':
          sentences.append(st)
          paras.append(sentences)
          st = ""
          sentences = []
        prev = ch
    else:
      paras.append(sentences)
    return paras
  @classmethod
  def getRefinedKeywords(cls,keywordslist):
    keywords = set([i.lower() for i in word_tokenize(keywordslist) if len(i) > 1])
    keywords -= stopwords
    keywords = {PorterStemmer().stem(i) for i in keywords}
    return keywords

  @classmethod
  def getRefinedKeywordsFromDoc(cls,docname):
    f=open(docname,'r')
    keywords=cls.getRefinedKeywords(f.read())
    return keywords


class TextMaintainer:
  def __init__(self):
    self.paras=[]
    self.summary=None

  def maintainParas(self,paras):
    countp=0
    counts=0
    for p in paras:
      para={}
      para['order']=countp
      para['sentences']=[]
      for s in p:
        sentence={}
        sentence['order']=counts
        sentence['content']=s
        sentence['score']=0
        para['sentences'].append(sentence)
        counts+=1
      counts=0
      if len(para['sentences'])>0 and len(para['sentences'][0]['content'])>0:
        self.paras.append(para)
      countp+=1

  def printParas(self):
    for p in self.paras:
      print(p)

  def extract(self,docname):
    return Extractor.getParas(docname)

  def analyse(self):
    summary=""
    for p in self.paras:
      orders=sorted(Analyser.refine(copy.deepcopy(p)))
      for i in orders:summary+=(p["sentences"][i]["content"])
    self.summary=summary




class Analyser:
  @classmethod
  def refine(cls,para):
    for s in para["sentences"]:
      s['content']=word_tokenize(s['content'])
      s['content']=[i.lower() for i in s['content']]
      s['content']=cls.removeStopwords(s['content'])
      s['content']=cls.stemLine(s['content'])
    para["sentences"]=cls.scoreSentences(para["sentences"])
    para["sentences"]=sorted(para["sentences"],key=lambda k: k['score'],reverse=True)
    no=len(para["sentences"])
    if no>0 and no<=2: n=no
    elif no>2 and no<=6: n=2
    elif no>6 and no<=10: n=3
    elif no>10:n=no/4
    
    return [para["sentences"][i]['order'] for i in range(n)]

  @classmethod
  def removeStopwords(cls,l):
    global stopwords
    return (set(l)-stopwords)-set(string.punctuation)

  @classmethod
  def stemLine(cls,s):
    s = [PorterStemmer().stem(i) for i in list(s)]
    return s

  @classmethod
  def scoreSentences(cls,sentences):
    for s1 in range(len(sentences)):
      for s2 in range(len(sentences)):
        if s1==s2:continue
        c1=set(sentences[s1]["content"])
        c2=set(sentences[s2]["content"])
        sentences[s1]['score']+=2*len(c1 & c2)/(len(c1)+len(c2))
    return sentences

class Tester:
  @classmethod
  def getRecallPrecision(cls,keywords,summary,refined=False):
    if not refined:
      summarywords=Extractor.getRefinedKeywords(summary)
    else: summarywords=summary
    totalRelevant=len(keywords)
    totalRetrieved=len(summarywords)
    retr_rel= len(summarywords & keywords)
    recall=retr_rel/totalRelevant
    precision=retr_rel/totalRetrieved
    return (recall,precision)

initStopwords()
tm=TextMaintainer()
paras=tm.extract("doc.txt")
tm.maintainParas(paras)
tm.analyse()
print(tm.summary)
print("\n\n")

keywords=Extractor.getRefinedKeywordsFromDoc('manualSummary.txt')
keywords2=Extractor.getRefinedKeywordsFromDoc('summaryFromOnlineS.txt')
recall,precision=Tester.getRecallPrecision(keywords,tm.summary)
print("recall ",recall,"\nprecision ",precision)
fscore=(2*recall*precision)/(recall+precision)
print("fscore ", fscore)

print("\n\nfor online summarizer:\n\n")

recall,precision=Tester.getRecallPrecision(keywords,keywords2,refined=True)
print("recall ",recall,"\nprecision ",precision)
fscore=(2*recall*precision)/(recall+precision)
print("fscore ", fscore)
