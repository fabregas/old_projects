import sys, traceback

#FBE - Fablik error
FBE_OK              =   0
FBE_UNEXPECTED      =   666
FBE_CONFIG_ERROR    =   400

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
FBE_FORM_NOT_FOUND          =   414
FBE_FORM_NOT_AUTHORIZED     =   415
FBE_INVALID_LANG            =   416


def parse_exception(e_obj, debug):
    if len(e_obj.args) == 2:
        (err_code, err_message) = e_obj.args
    else:
        (err_code,err_message) = (FBE_UNEXPECTED, str(e_obj))

    if debug:
        err_message += '\n' + '-'*80 + '\n'
        err_message += ''.join(apply(traceback.format_exception, sys.exc_info()))
        err_message += '-'*80 + '\n'

    return (err_code, err_message)
