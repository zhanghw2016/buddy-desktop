'''
Created on 2016-08-10

@author: cipher
'''

import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from common import (
    is_admin_user,
)
from constants import (
    LONG_STR_LEN,
    LONG_STR_PARAMS,
    EXTRA_LONG_STR_LEN,
    EXTRA_LONG_STR_PARAMS,
    NORMAL_STR_LEN,
    FILE_CONTENT_LEN,
    FILE_CONTENT_PARAMS,
    MAX_PORT,

    SUPPORTED_LANGS,
    SUPPORTED_GENDERS,
    ALL_ROLES,
    LIST_PARAMETER_MAX_LENGTH,
)
from error.error import Error
from log.logger import logger
from utils.misc import (
    is_integer,
    is_str,
    get_byte_len,
    strip_xss_chars,
    format_params,
)
from utils.email_tool import is_email_valid
from utils.passwd import (
    is_strong_user_passwd,
    is_passwd_too_simple,
    is_ascii_passwd,
)
from utils.json import json_load
from utils.time_stamp import (
    parse_utctime,
    is_valid_ts,
)

class BaseRequestChecker(object):
    ''' api request format checking '''

    # parameters that can be negative
    SPECIAL_INTEGER_PARAMS = []

    def __init__(self, sender, checker):
        '''
        @param sender - the id of the sender of the request
        '''
        self.checker = checker
        self.sender = sender                    # sender information
        self.builder = None                     # api request builder
        self.checker.error = Error(ErrorCodes.INVALID_REQUEST_FORMAT)

    def __getattr__(self, zone):
        return getattr(self.checker, zone , None)

    def get_error(self):
        ''' return the information describing the error occurred
            in Request Builder.
        '''
        return self.checker.error

    def set_error(self, msg=None, args=None, kwargs=None):
        self.checker.error = Error(
            ErrorCodes.INVALID_REQUEST_FORMAT,
            msg,
            args=args,
            kwargs=kwargs,
        )

    def _trim_directive(self, directive):
        param_to_trim = []
        for param in directive:
            if directive[param] is not None:
                continue
            param_to_trim.append(param)

        for param in param_to_trim:
            del directive[param]

    def _trim_list(self, list_items):
        ''' del None item and duplicate items '''
        new_items = list()
        for item in list_items:
            if item is None:
                continue
            if not is_str(item) and not is_integer(item):
                continue
            if item not in new_items:
                new_items.append(item)
        return new_items

    def _check_str_params(self, directive, params):
        '''
            @param directive: the directive to check
            @param params: the params that should be string type.
        '''
        for param in params:
            if param not in directive:
                continue
            if not is_str(directive[param]):
                logger.error("parameter [%s] should be string in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_STR, param)
                return False
            directive[param] = strip_xss_chars(directive[param])
            byte_len = get_byte_len(directive[param])
            if param in LONG_STR_PARAMS:
                if byte_len > LONG_STR_LEN:
                    logger.error("parameter [%s] value too long [%s bytes] in directive [%s]" % (param, byte_len, format_params(directive)))
                    self.set_error(ErrorMsg.ERR_MSG_PARAMETER_VALUE_TOO_LONG, (param, LONG_STR_LEN))
                    return False
            elif param in EXTRA_LONG_STR_PARAMS:
                if byte_len > EXTRA_LONG_STR_LEN:
                    logger.error("parameter [%s] value too long [%s bytes] in directive [%s]" % (param, byte_len, format_params(directive)))
                    self.set_error(ErrorMsg.ERR_MSG_PARAMETER_VALUE_TOO_LONG, (param, EXTRA_LONG_STR_LEN))
                    return False
            elif param in FILE_CONTENT_PARAMS:
                if byte_len > FILE_CONTENT_LEN:
                    logger.error("parameter [%s] value too long [%s bytes] in directive [%s]" % (param, byte_len, format_params(directive)))
                    self.set_error(ErrorMsg.ERR_MSG_PARAMETER_VALUE_TOO_LONG, (param, FILE_CONTENT_LEN))
                    return False
            else:
                if byte_len > NORMAL_STR_LEN:
                    logger.error("parameter [%s] value too long [%s bytes] in directive [%s]" % (param, byte_len, format_params(directive)))
                    self.set_error(ErrorMsg.ERR_MSG_PARAMETER_VALUE_TOO_LONG, (param, NORMAL_STR_LEN))
                    return False
        return True

    def _check_integer_params(self, directive, params):
        '''
            @param directive: the directive to check
            @param params: the params that should be integer type.
        '''
        for param in params:
            if param not in directive:
                continue
            val = directive[param]
            if is_integer(val):
                val = int(val)
                if val < 0 and param not in self.SPECIAL_INTEGER_PARAMS:
                    logger.error("parameter [%s] should not be negative in directive [%s]" % (param, format_params(directive)))
                    self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_NOT_BE_NEGATIVE, param)
                    return False
                directive[param] = val
            else:
                logger.error("parameter [%s] should be integer in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_INTEGER, param)
                return False
        return True

    def _check_list_params(self, directive, params):
        '''
            @param directive: the directive to check
            @param params: the params that should be list type.
        '''
        for param in params:
            if param not in directive:
                continue
            if not isinstance(directive[param], list):
                logger.error("parameter [%s] should be list in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_LIST, param)
                return False
            directive[param] = self._trim_list(directive[param])
            if not is_admin_user(self.sender):
                if len(directive[param]) > LIST_PARAMETER_MAX_LENGTH:
                    logger.error('parameter [%s] length greater than %d',
                                 param, LIST_PARAMETER_MAX_LENGTH)
                    self.set_error(ErrorMsg.ERR_MSG_LIST_PARAMETER_LENGTH_TOO_LONG,
                                   args=(param, LIST_PARAMETER_MAX_LENGTH))
                    return False
        return True

    def _check_dict_params(self, directive, params):
        '''
            @param directive: the directive to check
            @param params: the params that should be dict type.
        '''
        for param in params:
            if param not in directive:
                continue
            if not isinstance(directive[param], dict):
                logger.error("parameter [%s] should be dict in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_DICT, param)
                return False
            directive[param] = self._trim_list(directive[param])
        return True

    def _check_time_params(self, directive, params):
        ''' check time params and format it to local datetime '''
        for param in params:
            if param not in directive:
                continue
            # time param should be string
            if not is_str(directive[param]):
                logger.error("parameter [%s] should be string in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_STR, param)
                return False
            # parse UTC time string to local time stamp
            ts = parse_utctime(directive[param])
            if ts is None:
                logger.error("parameter [%s] should be UTC time in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_UTCTIME, param)
                return False
            directive[param] = ts
        return True

    def _check_ts_without_zone_params(self, directive, params):
        ''' check timestamp params, dont convert, keep the string '''
        for param in params:
            if param not in directive:
                continue

            # time param should be string
            if not is_str(directive[param]):
                logger.error("parameter [%s] should be string in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_STR, param)
                return False

            if not is_valid_ts(directive[param]):
                logger.error("parameter [%s] should be timestampin directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_UTCTIME, param)
                return False

        return True

    def _check_filter_params(self, directive, params):
        ''' string or list of strings '''
        for param in params:
            if param not in directive:
                continue
            if is_str(directive[param]):
                directive[param] = [directive[param]]
            if not isinstance(directive[param], list):
                logger.error("parameter [%s] should be list in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_LIST, param)
                return False
            directive[param] = self._trim_list(directive[param])
            if not is_admin_user(self.sender):
                if len(directive[param]) > LIST_PARAMETER_MAX_LENGTH:
                    logger.error('parameter [%s] length greater than %d',
                                 param, LIST_PARAMETER_MAX_LENGTH)
                    self.set_error(ErrorMsg.ERR_MSG_LIST_PARAMETER_LENGTH_TOO_LONG,
                                   args=(param, LIST_PARAMETER_MAX_LENGTH))
                    return False
        return True

    def _check_filter_integer_params(self, directive, params):
        ''' integer or list of integers '''
        for param in params:
            if param not in directive:
                continue
            if is_integer(directive[param]):
                directive[param] = [int(directive[param])]
            elif isinstance(directive[param], list):
                vals = []
                for val in directive[param]:
                    if not is_integer(val):
                        logger.error("parameter [%s] should be integer in directive [%s]" % (param, format_params(directive)))
                        self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_INTEGER, param)
                        return False
                    vals.append(int(val))
                directive[param] = vals
            else:
                logger.error("parameter [%s] should be list in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_LIST, param)
                return False
        return True

    def _check_list_dict_params(self, directive, params):
        ''' the items in list should be dict '''
        for param in params:
            if param not in directive:
                continue
            if not isinstance(directive[param], list):
                logger.error("parameter [%s] should be list in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_LIST, param)
                return False
            for item in directive[param]:
                if not isinstance(item, dict):
                    logger.error("item [%s] should be dict in directive [%s]" % (item, format_params(directive)))
                    self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_PARAMETER_FORMAT, param)
                    return False
        return True

    def _check_required_params(self, directive, params):
        '''
            @param directive: the directive to check
            @param params: the params that should be list type.
        '''
        for param in params:
            if param not in directive or directive[param] is None:
                logger.error("[%s] should be specified in directive [%s]" % (param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_MISSING_PARAMETER, param)
                return False
            if isinstance(directive[param], str) or isinstance(directive[param], unicode):
                if not directive[param]:
                    self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_NOT_BE_EMPTY, param)
                    return False
            elif isinstance(directive[param], list) or isinstance(directive[param], dict):
                if len(directive[param]) == 0:
                    self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_NOT_BE_EMPTY, param)
                    return False
        return True

    def _check_required_one_params(self, directive, params):
        '''
            @param directive: the directive to check
            @param params: the params that should be list type.
        '''
        if not params:
            return True

        params_str = ""
        for param in params:
            if param in directive:
                return True
            params_str+=(",%s" % param)
        logger.error("require one parameter [%s]" % params_str[1:])
        self.set_error(ErrorMsg.ERR_MSG_MISSING_PARAMETER, params_str)
        return False

    def _check_email(self, email):

        if not is_email_valid(email):
            logger.error("invalid email format [%s]" % (email))
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_EMAIL_ADDR)
            return False

        return True

    def _check_json_params(self, directive, params):
        ''' json string '''
        for param in params:
            if param not in directive or not directive[param] or isinstance(directive[param], dict):
                continue
            else:
                if not is_str(directive[param]):
                    logger.error("parameter [%s] should be str or unicode in directive [%s]" % (param, format_params(directive)))
                    self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_STR, param)
                    return False
                if not json_load(directive[param]):
                    logger.error("parameter [%s] should be json str in directive [%s]" % (param, format_params(directive)))
                    self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_PARAMETER_FORMAT, param)
                    return False
        return True

    def _check_params(self, directive, required_params=[], str_params=[],
                      integer_params=[], float_params=[], list_params=[], dict_params=[],
                      time_params=[], filter_params=[], list_dict_params=[],
                      filter_integer_params=[], json_params=[], required_one_params=[]):
        ''' check the param type for directive
        '''
        return self._check_required_params(directive, required_params) and \
            self._check_required_one_params(directive, required_one_params) and \
            self._check_str_params(directive, str_params) and \
            self._check_integer_params(directive, integer_params) and \
            self._check_time_params(directive, time_params) and \
            self._check_list_params(directive, list_params) and \
            self._check_dict_params(directive, dict_params) and \
            self._check_filter_params(directive, filter_params) and \
            self._check_list_dict_params(directive, list_dict_params) and \
            self._check_json_params(directive, json_params) and \
            self._check_filter_integer_params(directive, filter_integer_params)

    def _check_port(self, port):
        ''' check port '''
        if not is_integer(port):
            logger.error("port [%s] should be integer" % (port))
            self.set_error(ErrorMsg.ERR_MSG_PORT_SHOULD_BE_INT, port)
            return False
        if int(port) < 0 or int(port) > MAX_PORT:
            logger.error("illegal port range [%s]" % (port))
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_PORT_RANGE, port)
            return False
        return True

    def _check_users(self, users):
        ''' check user ID '''
        ctx = context.instance()
        if not users:
            return True
        if not isinstance(users, list):
            users = users.strip().split(';')
        users = list(set(users))
        _users = ctx.pgm.get_users(users=users, limit=len(users))
        if len(users) != len(_users):
            logger.error("invalid user_id(s) existed in [%s]." % users)
            self.set_error(ErrorMsg.ERR_MSG_USERS_NOT_FOUND, ",".join(users))
            return False
        return True

    def _check_user_password(self, passwd, user_name):
        ''' check user password '''
        passwd = passwd.strip()
        if not is_ascii_passwd(passwd):
            logger.error("user password [%s] should be ASCII" % (passwd))
            self.set_error(ErrorMsg.ERR_MSG_PASSWD_SHOULD_BE_ASCII)
            return False
        if not is_strong_user_passwd(passwd):
            logger.error("user password [%s] is not strong enough" % (passwd))
            self.set_error(ErrorMsg.ERR_MSG_NOT_STRONG_USER_PASSWD)
            return False
        # if is_passwd_too_simple(passwd):
        #     logger.error("password [%s] is too simple" % (passwd))
        #     self.set_error(ErrorMsg.ERR_MSG_PASSWD_TOO_SIMPLE)
        #     return False
        
        if user_name.lower() in passwd.lower():
            logger.error("password [%s] cant contain username %s" % (passwd, user_name))
            self.set_error(ErrorMsg.ERR_MSG_PASSWD_CANT_CONTAIN_USER_NAME)
            return False
        return True

    def _check_lang(self, lang):
        ''' check language '''
        if lang not in SUPPORTED_LANGS:
            logger.error("language [%s] not supported" % (lang))
            self.set_error(ErrorMsg.ERR_MSG_LANG_NOT_SUPPORTED, lang)
            return False
        return True

    def _check_gender(self, gender):
        ''' check gender '''
        if gender not in SUPPORTED_GENDERS:
            logger.error("illegal gender [%s]" % (gender))
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_GENDER, gender)
            return False
        return True

    def _check_role(self, role):
        ''' check role '''
        if role not in ALL_ROLES:
            logger.error("illegal role [%s]" % (role))
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_ROLE, role)
            return False
        return True
    
    def _check_str_length(self, check_str, max_length=63):

        if not check_str or len(check_str) > max_length: 
            logger.error("illegal string length [%s], %s" % (check_str, max_length))
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_STR_LENGTH, (check_str, max_length))
            return False
        return True
        


