# -*- coding: utf-8 -*-
import jieba.posseg as pseg
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

def get_cls_model(name):
    #getModel pipleline
    modelPipeline = _get_cls_models()[name]
    #Task: retrieve persisted model if any
    
    return modelPipeline

def _get_cls_models():
    clsModels = dict()
    preProcessor_CN = Pipeline([('vect', CountVectorizer(tokenizer=lambda doc:tokenize_CN(doc))),
                         ('tfidf', TfidfTransformer()),])
    cn_NB_clf = Pipeline([('preProcess',preProcessor_CN),
                         ('clf', MultinomialNB()),
    ])
    clsModels['cn_NB'] = cn_NB_clf
    return clsModels

#Task: build customized 词库
def tokenize_CN(doc):
    words = pseg.cut(doc)
    featureWords = []
    for w in words:
        #extract nouns &　verbs only
        if(w.flag in ['n','v']):
            featureWords.append(w.word)
    #Task: log these feature words
    return featureWords

from cvs_handler import UnicodeReader
from sets import Set
def init_training(name):
    #read initial classified data 
    corpus,targets = _load_init_data('CallNature_CLS.csv')
    
    #train all model pipeline 
    model = get_cls_model(name)
    model.fit(corpus,targets['index'])
	
     #persist model accordingly
    _persist_cls_model('cn',model)
	
def _load_init_data(fileName):
    corpus = []
    targetIndex = []
    targetNames = Set()
    with open(fileName,'rb') as f:
        reader = UnicodeReader(f,encoding='gbk')
        headers = reader.next()
        #Task: enable data/target  from headers
        for row in reader:
            corpus.append(row[0])
            catPair = row[1].split('.')
            targetIndex.append(int(catPair[0]))
            targetNames.add(catPair[1])
    targets = dict()
    targets['index'] = targetIndex
    targets['name'] = targetNames
    return (corpus,targets)
'''
from gluon.shell import exec_environment    
def train_cls_model(model):
    app = exec_environment('applications/chatlogCLS/models/db.py')
    rows = app.db().select(app.db.chatlog.is_confirmed>=app.db.ACC_PER_CONFIRM)
    
    sentences = []
    categories = []
    for row in rows:
        sentences.append(row.said)
        categories.append(row.category)
    model.fit(sentences,categories)
    return model
'''    
import os
from sklearn.externals import joblib
def _persist_cls_model(name,model):
    #if current model exists, move
    sFilePathath = './' + name
    if not os.path.exists(sFilePath):
        os.mkdir(sFilePath)
        
    with open(sFilePath+"/"+filename+"/current.pkl","w+") as f:
        f.write(' '.join(result))
    #if 

def _retrieve_cls_model(name):
    filename = './' + name + '/current.pkl'
    model = joblib.load(filename)
    return model    

from sklearn import cross_validation
    
if __name__ == '__main__':
    #read initial csv to initial classifier
    corpus,targets = _load_init_data('CallNature_CLS.csv')
    
    model = get_cls_model('cn_NB')  
    #Task: corpus needs to be transformed
    data = model.fit_transform(corpus)
    
    data_train, data_test, tgt_train, tgt_test = cross_validation.train_test_split(data, 
                                                                                   targets['index'], test_size=0.3, random_state=0)    
    
    model.fit(data_train,tgt_train)
    #test the effectiveness of model    
    
    scores = cross_validation.cross_val_score(model, data, targets['index'], cv=5)
    
    #retrieve the issue and cross-validate the result
    #test the effectivenmess of model again
#    model = _retrieve_cls_model('cn_NB')
    
    
    
    
    
    
