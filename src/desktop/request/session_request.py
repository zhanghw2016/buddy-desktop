'''
Created on 2012-7-9

@author: yunify
'''
from request.base_request import BaseRequest
from request.consolidator.request_checker import RequestChecker
from utils.time_stamp import get_ts, cmp_ts, get_expired_ts, parse_ts
from utils.auth import SignatureAuthHandler
from utils.misc import format_params
from constants import DEFAULT_LANG, CHANNEL_SESSION, REQ_EXPIRED_INTERVAL, DESKTOP_ACCESS_KEY_ID, DESKTOP_SECRET_ACCESS_KEY, USER_ROLE_NORMAL
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from resource_control.user.session import check_session
from log.logger import logger

class SessionRequest(BaseRequest):

    def __init__(self, headers, params):
        """Represents an request from console with session.
        @param headers - A dict for request dispatch_context like HTTP method and request path.
        @param params - A dictionary object containing all given console request parameters.
        """
        # A string representing the HTTP method used in the request. e.g. "GET" or "POST".
        self.method = headers["method"]
        # A string representing the path to the requested page, not including the domain.
        self.path = headers["path"]
        # weather the request is sent through a secure path
        self.is_secure = headers["is_secure"]
        # request parameters
        self.params = self._get_params(params)
        # request sender infomation
        self.sender = {}

    def __str__(self):
        return (('method:(%s) path(%s) params(%s)') % (self.method,
                                                       self.path,
                                                       self.params))

    def _check_params(self):
        ''' check required params
            @return: True if succeeded and False if failed.
        '''
        required_params = ["signature", "access_key_id",
                           "signature_method", "signature_version",
                           "action", "sk"]
        for param in required_params:
            if param not in self.params:
                
                if param == "sk":
                    logger.error("[%s] not found in this request [%s]" % (param, format_params(self.params)))
                    err = Error(ErrorCodes.INVALID_REQUEST_FORMAT_SK,
                                ErrorMsg.ERR_MSG_MISSING_PARAMETER, param)
                    self.set_error(err)
                else:
                    logger.error("[%s] not found in this request [%s]" % (param, format_params(self.params)))
                    err = Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                ErrorMsg.ERR_MSG_MISSING_PARAMETER, param)
                    self.set_error(err)
                return False
        # either "expires" or "time_stamp" should be contained in params
        if "expires" not in self.params and "time_stamp" not in self.params:
            logger.error("[expires] and [time_stamp] both not found in request [%s]" % (format_params(self.params)))
            err = Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                        ErrorMsg.ERR_MSG_MISSING_PARAMETER, "expires or time_stamp")
            self.set_error(err)
            return False

        # check time stamp format
        for param in ["expires", "time_stamp"]:
            if param not in self.params:
                continue
            if 0 == parse_ts(self.params[param]):
                logger.error("[%s]'s format is incorrect in request [%s]" % (param, format_params(self.params)))
                err = Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                            ErrorMsg.ERR_MSG_ILLEGAL_TIMESTAMP, param)
                self.set_error(err)
                return False

        return True

    def _check_signature(self):
        ''' check signature of request
            @return: user id if succeeded and None if failed.
        ''' 
        # get secret_access_key
        access_key = DESKTOP_ACCESS_KEY_ID
        access_secret = DESKTOP_SECRET_ACCESS_KEY

        # check authorize information for request
        auth_handler = SignatureAuthHandler("", access_key, access_secret)
        if not auth_handler.check_auth(self):
            logger.error("check auth for [%s] failed" % format_params(self.params))
            err = Error(ErrorCodes.AUTH_FAILURE, 
                        ErrorMsg.ERR_MSG_SIGNATURE_NOT_MACTCHED)
            self.set_error(err)
            return None
        
        return True

    def _check_expires(self):
        ''' check expires of request '''
        current_time = get_ts()
        expires = self.params.get("expires", None)
        if not expires:
            expires = get_expired_ts(self.params['time_stamp'], REQ_EXPIRED_INTERVAL)
        # request is expires if current_time greater than expires
        if 1 == cmp_ts(current_time, expires):
            logger.error("request [%s] is expired, current_time [%s], expires [%s]" %
                         (format_params(self.params), current_time, expires))
            err = Error(ErrorCodes.REQUEST_HAS_EXPIRED)
            self.set_error(err)
            return False
        return True

    def _check_session(self):
        ''' check session of request
            @return: user id if succeeded and None if failed.
        '''
        # get session key
        session_key = self.params["sk"]
        user_id = check_session(session_key)
        if user_id is None:
            logger.error("unregistered session key [%s]" % (session_key))
            err = Error(ErrorCodes.SESSION_EXPIRED,
                        ErrorMsg.ERR_MSG_PLZ_LOGIN_AGAIN)
            self.set_error(err)
            return None
        return user_id

    def validate(self):
        ''' validate request '''
        # check request format
        if not self._check_params():
            return False
        # check if request expired
        if not self._check_expires():
            return False
        # check signature
        if not self._check_signature():
            return False
        # check session
        user_id = self._check_session()
        if user_id is None:
            return False
        # check if user can access
        zone = self.params.get('zone')
        user = self._check_access(user_id, zone)
        if user is None:
            return False

        if not zone:
            zone = user.get("zone", "")

        # init sender
        self.sender = self._get_sender(user)
        self.sender.update({'channel': CHANNEL_SESSION})
        self.sender.update({'console_id': self.params.get('console_id',USER_ROLE_NORMAL)})
        self.sender.update({'zone': zone})
        self.sender.update({'lang': self.params.get('lang', DEFAULT_LANG)})
        self.sender.update({'sk': self.params["sk"]})
        if "domain" in user:
            self.sender.update({'domain': user["domain"]})

        return True

    def build_internal_request(self):
        ''' build request in internal format '''
        self._build_list_params(self.params)

        builder = RequestChecker(self.sender)
        internal_request = builder.build_request(self.params["action"], self.params)
        if internal_request is None:
            logger.error("build internal request failed [%s]" % format_params(self.params))
            self.set_error(builder.get_error())
            return None

        return internal_request
