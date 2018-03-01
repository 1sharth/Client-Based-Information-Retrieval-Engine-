import string

def newTrie():
    trie={}
    for letters in string.ascii_lowercase:
        trie[letters]=[{},0]
    return trie

def trieAddString(trie,string):
    temp=trie
    count=1
    for letter in string:
        if count==len(string):
            temp[letter][1]+=1
        if len(temp[letter][0])==0:
            temp[letter][0]=newTrie()
        temp = temp[letter][0]
        count+=1
    return trie

def trieStringPresent(trie,string):
    count=1
    for letter in string:
        #print(letter)
        if len(trie[letter][0])!=0:
            if count == len(string):
                return trie[letter][1]
            trie=trie[letter][0]
        else:
            return 0
        count+=1
    print("reached unexpected piece of code")

'''t=newTrie()
t=trieAddString(t,"shit")
t=trieAddString(t,"shii")
t=trieAddString(t,"shitt")
t=trieAddString(t,"shit")
#print(t)
print(trieStringPresent(t,"shitt"))'''

