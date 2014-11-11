# -*- coding: utf-8 -*-
import jieba.posseg as pseg

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

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

def get_cls_model(name):
    #getModel pipleline
    modelPipeline = _get_cls_models()[name]
    #Task: retrieve persisted model if any
    train_cls_model(modelPipeline) 
    return modelPipeline

def _get_cls_models():
    clsModels = dict()
    text_clf = Pipeline([('vect', CountVectorizer(tokenizer=lambda doc:tokenize_CN(doc))),
                         ('tfidf', TfidfTransformer()),
                         ('clf', MultinomialNB()),
    ])
    clsModels['simple'] = text_clf
    return clsModels

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
    
def persist_cls_model(model):
    pass