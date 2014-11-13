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
    db.chatlog.is_confirmed.readable =False
    db.chatlog.is_confirmed.writable =False
    #db.chatlog.who.writable=False
    #db.chatlog.said.writable=False
    db.chatlog.category.widget = SQLFORM.widgets.autocomplete(
     request, db.category.name, limitby=(2,5), min_length=2)

    refDB_param = dict(params=(db,'category.name'),error_message=T('invalid category'))
    db.chatlog.category.requires = IS_SET_OR_PREDICTED(refDB=refDB_param,
                                                       predictedBy=request.vars.said)
    grid = SQLFORM.grid(db.chatlog,deletable=False,
                        user_signature=False,
                        orderby='is_confirmed',
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
    def __init__(self, refDB,predictedBy, errMsg=T(',predicted as:')):
        #initialize
        super(IS_SET_OR_PREDICTED,self).__init__(*refDB['params'],error_message = refDB['error_message'])
        self.predictedBy = predictedBy
#        super(IS_SET_OR_PREDICTED,self).error_message = error_message
        self.errMsg = errMsg
        
    def __call__(self, value):
        try:
           _value,error_message =super(IS_SET_OR_PREDICTED,self).__call__(value)
           if error_message:
               value = "其他"
#               value = classify.get_cls_model('cn_').predict(self.predictedBy)
               return (value, error_message + self.errMsg + value)
           else:
               return (_value, None)
        except:
           return (value, 'unknown error happened...')
        
    def formatter(self, value):
        return value

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
