'''
Created on 2012-7-9

@author: yunify
'''
from request.base_request import BaseRequest
from request.consolidator.request_checker import RequestChecker
from common import get_super_sender
from utils.misc import format_params
from constants import CHANNEL_INTERNAL, EN
import error.error_code as ErrorCodes 
from error.error import Error
import error.error_msg as ErrorMsg
from log.logger import logger
from constants import(
    GLOBAL_ADMIN_USER_ID,
)

class InternalRequest(BaseRequest):

    def __init__(self, params):
        """Represents an request from internal.
        @param params - A dictionary object containing all given internal request parameters.  
        """
        self.params = {}
        self.params = self._get_params(params)
        self.sender = {}

    def __str__(self):
        return (('params(%s)') % (self.params))
        
    def _check_params(self):
        ''' check required params '''
        required_params = ["action"]
        for param in required_params:
            if param not in self.params:
                logger.error("[%s] not found in this request [%s]" % (param, format_params(self.params)))
                err = Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                            ErrorMsg.ERR_MSG_MISSING_PARAMETER, param)
                self.set_error(err)
                return False    
        return True
    
    def validate(self):
        ''' validate request '''
        # check request format
        if not self._check_params():
            return False
        # check if user can access
        if "sender" in self.params:
            user_id = self.params["sender"]["user_id"]
            if user_id != GLOBAL_ADMIN_USER_ID:
                user = self._check_access(user_id)
                if user is None:
                    return False
                self.sender = self._get_sender(user)
                self.sender.update({'channel': CHANNEL_INTERNAL,
                                    'lang': EN})
            else:
                self.sender = get_super_sender()
                self.sender.update(self.params["sender"])
        else:
            self.sender = get_super_sender()
        self.sender.update({'zone': self.params['zone']})
        return True
    
    def build_internal_request(self):
        ''' build request in internal format '''
        builder = RequestChecker(self.sender)  
        internal_request = builder.build_request(self.params["action"], self.params)
        if internal_request is None:
            logger.error("build internal request failed [%s]" % format_params(self.params))
            self.set_error(builder.get_error())
            return None
        
        return internal_request
