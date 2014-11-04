# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 17:40:42 2014

@author: david.dai
"""

import datetime
import sqlite3
import os
import codecs
import re
import jieba.posseg as pseg

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

def persist_chatlog(filename, conn):
    with conn:
        cur = conn.cursor()
        
        f = codecs.open(filename,'r+','gbk')
        messages = []
        for line in f.readlines():
            if line.startwith():                
                msg=generateMsg(line)
                print msg
                messages.append(msg.msgTime,msg.who,msg.said,False)
        cur.executemany('insert into messages(msg_time,who,said,is_confirmed) values (?,?,?,?)',messages)
        

def generateMsg(line):
    s = line.split()
    msgTime = datetime.datetime.strptime(s[0],"%Y年%m月%d日%X")        
    n = re.search('^(gelnic简妮:)?.+?:'.decode('utf-8','ignore'),s[1])
    who = n.group(0)
    said = s[1][len(who):]
    return Message(msgTime,who,said)    

def JB_tokenizer():
    words = pseg.cut(sentences)
    for w in words:
        #extract nouns &　verbs only
        if(w.flag in ['n','v']):
            w.word
    
#TODO: 1. traning 2. dateset 測試
def get_cls_model(sentences, categories):
    #extract features via jieba, only consider noun & verb
    
    #building pipeline
    text_clf = Pipeline([('vect', CountVectorizer(tokenizer=JB_tokenizer )),
                         ('tfidf', TfidfTransformer()),
                         ('clf', MultinomialNB()),
    ])
    #return trained models
    text_clf = text_clf.fit(JB_tokenizer,categories)
    return text_clf

#copy of https://docs.python.org/2/library/sqlite3.html
class Message(object):
    def __init__(self,msgTime,who,said):
        self.msgTime, self.who, self.said = msgTime, who, said
        
    def __repr__(self):
        return "on %s, %s said: %s" % (self.msgTime.strftime("%Y-%m-%d %X"), self.who, self.said)
    
#获取文件列表（该目录下放着100份文档）
def getFilelist(path):
    filelist = []
    files = os.listdir(path)
    for f in files:
        if(f[0] == '.'):
            pass
    else:
        filelist.append(f)
        return filelist,path

if __name__ == "__main__":
    conn = sqlite3.connect("CN_CLS")
    
    with conn:
        cur.execute("create table messages(id INTEGER PRIMARY KEY AUTOINCREMENT, msg_time datetime, who TEXT, said TEXT, category TEXT, is_confirmed BOOLEAN)")

    #從目錄下读取文档
    for filename in getFilelist("./chatlog"):
        persist_chatlog(filename,conn )
    
    #模拟写入category    
    
    
    #build models
    clsModel = get_cls_model(sentences, categories)
    
    #evaluate the model
    clsModel.predict()
    
    
    