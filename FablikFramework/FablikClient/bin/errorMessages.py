from PyQt4.QtGui import QApplication as app

class MESSAGES:
    mesdict = {}

    @classmethod
    def init(cls):
        cls.mesdict[105] = app.translate('ErrorMessages','Languages config file parsing error!')
        cls.mesdict[402] = app.translate('ErrorMessages','User is not found!')
        cls.mesdict[403] = app.translate('ErrorMessages','Password is invalid!')

    @classmethod
    def get(cls, key, default=None):
        return cls.mesdict.get(key,default)

'''
FBE_NO_CURSOR               =   401
FBE_INVALID_USER            =   402
FBE_INVALID_PASSWORD        =   403
FBE_INVALID_SESSION         =   404
FBE_INVALID_AUDIT_TYPE      =   405
FBE_INVALID_AUDIT_OBJECT    =   406
FBE_INVALID_AUDIT_ID        =   407
FBE_INVALID_AUDIT_MESSAGE   =   408
FBE_INVALID_DEPARTAMENT     =   409
FBE_INVALID_INTERFACE       =   410
FBE_INVALID_SERVICE_URL     =   411
FBE_INVALID_DB_STRING       =   412
FBE_INVALID_DB_CONNECT      =   413
'''
