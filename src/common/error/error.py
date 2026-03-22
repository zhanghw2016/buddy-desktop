'''
Created on 2012-9-14

@author: yunify
'''
import error_code as ErrorCodes
import error_msg as ErrorMsg
from constants import DEFAULT_LANG, SUPPORTED_LANGS

'''
    Here are the definition of default error messages.
'''
DEFAULT_ERROR_MSG = {
    ErrorCodes.DATABASE_OPERATION_EXCEPTION: ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION,
    # Client Error Codes
    ErrorCodes.INVALID_REQUEST_FORMAT: ErrorMsg.ERR_CODE_MSG_INVALID_REQUEST_FORMAT,
    ErrorCodes.INVALID_REQUEST_METHOD: ErrorMsg.ERR_CODE_MSG_INVALID_REQUEST_METHOD,
    ErrorCodes.REQUEST_HAS_EXPIRED: ErrorMsg.ERR_CODE_MSG_REQUEST_HAS_EXPIRED,
    ErrorCodes.PERMISSION_DENIED: ErrorMsg.ERR_CODE_MSG_PERMISSION_DENIED,
    ErrorCodes.RESOURCE_ALREADY_EXISTED: ErrorMsg.ERR_MSG_RESOURCE_ALREADY_EXISTED,
    ErrorCodes.SESSION_EXPIRED: ErrorMsg.ERR_CODE_MSG_SESSION_EXPIRED,
    ErrorCodes.RESOURCE_NOT_FOUND: ErrorMsg.ERR_CODE_MSG_RESOURCE_NOT_FOUND,
    ErrorCodes.INVALID_API_MODULES: ErrorMsg.ERR_CODE_MSG_INVALID_API_MODULES,
    ErrorCodes.RESOURCES_DEPENDENCE: ErrorMsg.ERR_CODE_MSG_STILL_HAS_DEPENDENCY,
    # Server Error Codes
    ErrorCodes.INTERNAL_ERROR: ErrorMsg.ERR_CODE_MSG_INTERNAL_ERROR,
    ErrorCodes.SERVER_BUSY: ErrorMsg.ERR_CODE_MSG_SERVER_BUSY,
    ErrorCodes.INSUFFICIENT_RESOURCES: ErrorMsg.ERR_CODE_MSG_INSUFFICIENT_RESOURCES,
    ErrorCodes.SERVERS_UPDATING: ErrorMsg.ERR_CODE_MSG_SERVER_UPDATING,
}

'''
    Here is the class to manager error codes and error messages.
'''


class Error(object):
    ''' error class '''

    def __init__(self, code, message=None, args=None, kwargs=None):
        '''
        @param code - the error code, it is an integer.
        @param message - the error message to describe the error information in detail.
                         it is a dict with multi-language defined
        '''
        self.code = code
        self.message = message
        self.args = args
        self.kwargs = kwargs
        pass

    def get_code(self):
        ''' return a valid error code that defined in error codes'''
        return self.code

    def get_message(self, lang=DEFAULT_LANG):
        ''' return message
        @return:  "defaultmsg, message"
        '''
        lang = DEFAULT_LANG if lang not in SUPPORTED_LANGS else lang
        default_msg = DEFAULT_ERROR_MSG.get(self.code, {}).get(lang, "")
        if not self.message:
            return default_msg
        if self.args is not None:
            msg = self.message.get(lang) % self.args
        else:
            msg = self.message.get(lang)

        if self.kwargs:
            try:
                msg = msg.format(**self.kwargs)
            except:
                pass

        return default_msg + " " + msg
