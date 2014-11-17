# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    #response.flash = T("This is only a demo...")
    message=T('please upload chatlog file:')
    db.chatlog.category_id.readable =False
    db.category.id.readable =False
    db.chatlog.is_confirmed.represent=lambda is_confirmed,row: is_confirmed >= ACC_PER_CONFIRM and '===>' or '=>'
    db.chatlog.is_confirmed.writable =False

    db.chatlog.category_id.requires = IS_SET_OR_PREDICTED(db, 'category.id','%(name)s',zero=T('choose one'), 
                                                       error_message=T('invalid category'),predictedBy=request.vars.said)
    grid = SQLFORM.grid(db.chatlog,
                        fields=[db.chatlog.id,db.chatlog.msg_time,db.chatlog.who,db.chatlog.said,db.chatlog.is_confirmed,db.category.name],
                        deletable=False,
                        user_signature=False,
                        orderby='is_confirmed',
                        left=db.chatlog.on(db.chatlog.category_id == db.category.id),
                        selectable=[(T('confirm'),lambda ids : redirect(URL('default', 'confirm_predict', vars=dict(id=ids)))),],
                        )
    return locals()

def confirm_predict():
    #set confirmation to certain level
    for rowId in request.vars.id:
        row = db(db.chatlog.id == rowId).select().first()
        #Task:should check if the row's category is changed
        if True:
            row.is_confirmed = ACC_PER_CONFIRM
            row.update_record()
    redirect(URL('index'))

#import classify
class IS_SET_OR_PREDICTED(IS_IN_DB):
    def __init__(self, *params,**kv ):
        #initialize
        self.predictedBy = kv.pop('predictedBy')
        super(IS_SET_OR_PREDICTED,self).__init__(*params,**kv)
       
    def __call__(self, value):
        try:
           _value,error_message =super(IS_SET_OR_PREDICTED,self).__call__(value)
           if error_message:
               value = 6      #暂用“其他”代表         
#               value = classify.get_cls_model('cn_').predict(self.predictedBy)
               return (value, error_message + T(',predicted as:') + self.formatter(value))
           else:
#               return (_value, self.formatter(_value))
               return (_value, None)
        except:
           return (value, T('unknown error'))
    def formatter(self, value):
#        Task: map id to category name
        return super(IS_SET_OR_PREDICTED,self).formatter(value)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
