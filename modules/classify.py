# -*- coding: utf-8 -*-
import jieba.posseg as pseg

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
def get_cls_model(name):
    #getModel pipleline
    modelPipeline = _get_cls_models()[name]
    #Task: retrieve persisted model if any
    
    return modelPipeline

def _get_cls_models():
    clsModels = dict()
    cnPreprocessor = Pipeline([('vect', CountVectorizer(tokenizer=lambda doc:tokenize_CN(doc))),
                         ('tfidf', TfidfTransformer()),])
    cn_NB_clf = Pipeline([('preprocess',cnPreprocessor),
                         ('clf', MultinomialNB())])
    cn_SGD_clf = Pipeline([('preprocess',cnPreprocessor),
                         ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                               alpha=1e-3, n_iter=5))])                    
    clsModels['cn_NB'] = cn_NB_clf
    clsModels['cn_SGD'] = cn_SGD_clf
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

#import UnicodeReader
from sets import Set
def init_training(name):
    #read initial classified data 
    corpus,targets = _load_init_data('CallNature_CLS.csv')
    
    #train all model pipeline 
    model = get_cls_model(name)
    model.fit(corpus,targets['index'])
	
     #persist model accordingly
    _persist_cls_model('cn',model)

from csv_handler import UnicodeReader	
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
    
    model = get_cls_model('cn_SGD')
    
    #corpus needs to be transformed
    preprocessor = model.named_steps['preprocess']

    data = preprocessor.fit_transform(corpus)
    print "(row num , features num )=>"+data.shape.__str__()
	
	#cross-validate the sample
    data_train, data_test, tgt_train, tgt_test = cross_validation.train_test_split(data, targets['index'], 
                                      test_size=0.2, random_state=0) 
   
    clf = model.named_steps['clf']
    clf.fit(data_train, tgt_train)
    #test the effectiveness of model on test data   
    print clf.score(data_test, tgt_test)
    #test the effectiveness of model on over all 
    scores = cross_validation.cross_val_score(clf, data, targets['index'], cv=5)
    print scores
    print("Accuracy: %0.3f (+/- %0.3f)" % (scores.mean(), scores.std() * 2))

    
    
    
    
    
    