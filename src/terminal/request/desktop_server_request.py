'''
Created on 2012-7-9

@author: yunify
'''
import error.error_code as ErrorCodes 
from error.error import Error
import error.error_msg as ErrorMsg
from log.logger import logger
from utils.json import json_load
from utils.misc import to_list
from utils.misc import is_integer, is_str, get_byte_len, strip_xss_chars, format_params
from utils.time_stamp import parse_utctime
from resource.desktop import get_terminal_mac
from constants import (
    LONG_STR_PARAMS,
    EXTRA_LONG_STR_PARAMS,
    FILE_CONTENT_PARAMS,
    NORMAL_STR_LEN,
    LONG_STR_LEN,
    EXTRA_LONG_STR_LEN,
    FILE_CONTENT_LEN,
)
import context
import constants as const

class RequestChecker:
    def __init__(self, sender):
        self.error = Error(ErrorCodes.INVALID_REQUEST_FORMAT)
        self.sender = sender

    def _trim_directive(self, directive):
        ''' trim directive '''
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
                logger.error("parameter [%s] should be string in directive [%s]" % (
                    param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_STR, param)
                return False
            
            directive[param] = strip_xss_chars(directive[param])
            byte_len = get_byte_len(directive[param])
            if param in LONG_STR_PARAMS:
                if byte_len > LONG_STR_LEN:
                    logger.error("parameter [%s] value too long [%s bytes] in directive [%s]" % (
                        param, byte_len, format_params(directive)))
                    self.set_error(
                        ErrorMsg.ERR_MSG_PARAMETER_VALUE_TOO_LONG, (param, LONG_STR_LEN))
                    return False
            elif param in EXTRA_LONG_STR_PARAMS:
                if byte_len > EXTRA_LONG_STR_LEN:
                    logger.error("parameter [%s] value too long [%s bytes] in directive [%s]" % (
                        param, byte_len, format_params(directive)))
                    self.set_error(
                        ErrorMsg.ERR_MSG_PARAMETER_VALUE_TOO_LONG, (param, EXTRA_LONG_STR_LEN))
                    return False
            elif param in FILE_CONTENT_PARAMS:
                if byte_len > FILE_CONTENT_LEN:
                    logger.error("parameter [%s] value too long [%s bytes] in directive [%s]" % (
                        param, byte_len, format_params(directive)))
                    self.set_error(
                        ErrorMsg.ERR_MSG_PARAMETER_VALUE_TOO_LONG, (param, FILE_CONTENT_LEN))
                    return False
            else:
                if byte_len > NORMAL_STR_LEN:
                    logger.error("parameter [%s] value too long [%s bytes] in directive [%s]" % (
                        param, byte_len, format_params(directive)))
                    self.set_error(
                        ErrorMsg.ERR_MSG_PARAMETER_VALUE_TOO_LONG, (param, NORMAL_STR_LEN))
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
                    logger.error("parameter [%s] should not be negative in directive [%s]" % (
                        param, format_params(directive)))
                    self.set_error(
                        ErrorMsg.ERR_MSG_PARAMETER_SHOULD_NOT_BE_NEGATIVE, param)
                    return False
                directive[param] = val
            else:
                logger.error("parameter [%s] should be integer in directive [%s]" % (
                    param, format_params(directive)))
                self.set_error(
                    ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_INTEGER, param)
                return False
        return True

    def _check_list_params(self, directive, params, notrim=[]):
        '''
            @param directive: the directive to check
            @param params: the params that should be list type.
        '''
        for param in params:
            if param not in directive:
                continue
            if not isinstance(directive[param], list):
                logger.error("parameter [%s] should be list in directive [%s]" % (
                    param, format_params(directive)))
                self.set_error(
                    ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_LIST, param)
                return False
            if notrim and param in notrim:
                continue
            directive[param] = self._trim_list(directive[param])
        return True

    def _check_time_params(self, directive, params):
        ''' check time params and format it to local datetime '''
        for param in params:
            if param not in directive:
                continue
            # time param should be string
            if not is_str(directive[param]):
                logger.error("parameter [%s] should be string in directive [%s]" % (
                    param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_STR, param)
                return False
            # parse UTC time string to local time stamp
            ts = parse_utctime(directive[param])
            if ts is None:
                logger.error("parameter [%s] should be UTC time in directive [%s]" % (
                    param, format_params(directive)))
                self.set_error(
                    ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_UTCTIME, param)
                return False
            directive[param] = ts
        return True

    def _check_filter_params(self, directive, params):
        ''' string or list of strings '''
        for param in params:
            if param not in directive:
                continue
            if is_str(directive[param]):
                directive[param] = [directive[param]]
            if not isinstance(directive[param], list):
                logger.error("parameter [%s] should be list in directive [%s]" % (
                    param, format_params(directive)))
                self.set_error(
                    ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_LIST, param)
                return False
            directive[param] = self._trim_list(directive[param])
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
                        logger.error("parameter [%s] should be integer in directive [%s]" % (
                            param, format_params(directive)))
                        self.set_error(
                            ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_INTEGER, param)
                        return False
                    vals.append(int(val))
                directive[param] = vals
            else:
                logger.error("parameter [%s] should be list in directive [%s]" % (
                    param, format_params(directive)))
                self.set_error(
                    ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_LIST, param)
                return False
        return True

    def _check_json_params(self, directive, params):
        ''' json string '''
        for param in params:
            if param not in directive or not directive[param] or isinstance(directive[param], dict):
                continue
            else:
                if not (isinstance(directive[param], str) or isinstance(directive[param], unicode)):
                    logger.error("parameter [%s] should be str in directive [%s]" % (
                        param, format_params(directive)))
                    self.set_error(
                        ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_STR, param)
                    return False
                if not json_load(directive[param]):
                    logger.error(
                        "parameter [%s] should be json str in directive [%s]" % (param, format_params(directive)))
                    self.set_error(
                        ErrorMsg.ERR_MSG_ILLEGAL_PARAMETER_FORMAT, param)
                    return False
        return True
    
    def _check_list_dict_params(self, directive, params):
        ''' the items in list should be dict '''
        for param in params:
            if param not in directive:
                continue
            if not isinstance(directive[param], list):
                logger.error("parameter [%s] should be list in directive [%s]" % (
                    param, format_params(directive)))
                self.set_error(
                    ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_LIST, param)
                return False
            for item in directive[param]:
                if not isinstance(item, dict):
                    logger.error("item [%s] should be dict in directive [%s]" % (
                        item, format_params(directive)))
                    self.set_error(
                        ErrorMsg.ERR_MSG_ILLEGAL_PARAMETER_FORMAT, param)
                    return False
        return True

    def _check_required_params(self, directive, params):
        '''
            @param directive: the directive to check
            @param params: the params that should be list type.
        '''
        for param in params:
            if param not in directive or directive[param] is None:
                logger.error("[%s] should be specified in directive [%s]" % (
                    param, format_params(directive)))
                self.set_error(ErrorMsg.ERR_MSG_MISSING_PARAMETER, param)
                return False
            if isinstance(directive[param], str) or isinstance(directive[param], unicode):
                if not directive[param]:
                    self.set_error(
                        ErrorMsg.ERR_MSG_PARAMETER_SHOULD_NOT_BE_EMPTY, param)
                    return False
            elif isinstance(directive[param], list) or isinstance(directive[param], dict):
                if len(directive[param]) == 0:
                    self.set_error(
                        ErrorMsg.ERR_MSG_PARAMETER_SHOULD_NOT_BE_EMPTY, param)
                    return False
        return True

    def _check_params(self, directive, required_params=[], str_params=[],
                      integer_params=[], list_params=[], time_params=[],
                      filter_params=[], list_dict_params=[], filter_integer_params=[],
                      json_params=[], notrim=[]):
        ''' check the param type for directive
        '''
        return self._check_required_params(directive, required_params) and \
            self._check_str_params(directive, str_params) and \
            self._check_integer_params(directive, integer_params) and \
            self._check_time_params(directive, time_params) and \
            self._check_list_params(directive, list_params, notrim) and \
            self._check_filter_params(directive, filter_params) and \
            self._check_list_dict_params(directive, list_dict_params) and \
            self._check_json_params(directive, json_params) and \
            self._check_filter_integer_params(directive, filter_integer_params)

    def get_error(self):
        ''' return the information describing the error occurred
            in Request Builder.
        '''
        return self.error

    def set_error(self, msg=None, *args):
        ''' set error '''
        _args = []
        for a in args:
            _args += to_list(a)
        self.error = Error(
            ErrorCodes.INVALID_REQUEST_FORMAT, msg, tuple(_args))

    def build_request(self, action, directive):
        ''' build internal request according to specified action.
        '''
        handler_map = {
            const.REQUEST_DESKTOP_SERVER_MODIFY_TERMINAL_ATTRIBUTES: self.modify_terminal_attributes,
            const.REQUEST_DESKTOP_SERVER_RESTART_TERMINALS: self.restart_terminals,
            const.REQUEST_DESKTOP_SERVER_STOP_TERMINALS: self.stop_terminals,
            const.REQUEST_DESKTOP_SERVER_ONLINE_UPGRADE_TERMINALS: self.online_upgrade_terminals
            }
        if action is None:
            logger.error("request without action field")
            self.set_error(ErrorMsg.ERR_MSG_MISSING_PARAMETER, "action")
            return None

        if not is_str(action) or len(action) == 0:
            logger.error("request without action field")
            self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_STR, "action")
            return None

        if directive is None:
            directive = {}

        self._trim_directive(directive)
        if action not in handler_map:
            logger.error("can not handler this action: [%s]" % action)
            self.set_error(ErrorMsg.ERR_MSG_CAN_NOT_HANDLE_REQUEST)
            return None

        # build request
        try:
            request = handler_map[action](directive)
            request.update({"action": action})
            request.update({"terminal_mac": self.sender["terminal_mac"]})
            request.update({"sender": self.sender})
        except Exception, e:
            logger.exception("request params error [%s]", e)
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_REQUEST)
            return None
        return request

    def modify_terminal_attributes(self, directive):
        '''
            @param directive : send message to vm
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["terminal_server_ip"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        body = {}
        body["terminal_server_ip"] = directive["terminal_server_ip"]
        return body

    def restart_terminals(self, directive):
        '''
            @param directive : send message to vm
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=['terminal_mac'],
                                  integer_params=[],
                                  list_params=[]):
            return None
        body = {}
        body["terminal_mac"] = directive["terminal_mac"]
        return body

    def stop_terminals(self, directive):
        '''
            @param directive : send message to vm
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=['terminal_mac'],
                                  integer_params=[],
                                  list_params=[]):
            return None
        body = {}
        body["terminal_mac"] = directive["terminal_mac"]
        return body

    def online_upgrade_terminals(self, directive):
        '''
            @param directive : send message to vm
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=['terminal_mac','upgrade_packet_name','upgrade_packet_path','upgrade_packet_md5'],
                                  integer_params=[],
                                  list_params=[]):
            return None
        body = {}
        body["terminal_mac"] = directive["terminal_mac"]
        body["upgrade_packet_name"] = directive["upgrade_packet_name"]
        body["upgrade_packet_path"] = directive["upgrade_packet_path"]
        body["upgrade_packet_md5"] = directive["upgrade_packet_md5"]
        return body

class DesktopServerRequest:

    def __init__(self, params):
        """Represents an request from internal.
        @param params - A dictionary object containing all given internal request parameters.  
        """
        self.params = self._get_params(params)
        self.sender = None
        self.error = None

    def __str__(self):
        return (('params(%s)') % (self.params))

    def _get_params(self, params):
        ''' get not empty params '''
        new_params = {}
        for k, v in params.items():
            new_params[k] = v
        return new_params

    def get_error(self):
        ''' return the information describing the error occurred
            in validating the request or building the internal request.
        '''
        return self.error

    def set_error(self, error):
        ''' set error '''
        self.error = error

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

    def _check_time_stamp(self):
        return True

    def _get_sender(self):

        try:
            terminal_id = self.params.get("terminal_id", "")
            if len(terminal_id) == 0:
                logger.error("terminal_id [%s] is empty" % (terminal_id))
                return None
            terminal_mac = get_terminal_mac(terminal_id)
            if terminal_mac is None:
                logger.error("terminal [%s] not found" % (terminal_id))
                return None

            ctx = context.instance()
            zones = ctx.zones
            for zone_id, _ in zones.items():
                zone_id = zone_id

            sender = {
                "terminal_id": self.params["terminal_id"],
                "terminal_mac": terminal_mac,
                "zone": zone_id
                }
            return sender
        except:
            return None

    def validate(self):
        ''' validate request '''
        # check request format

        if not self._check_params():
            return False

        if not self._check_time_stamp():
            return False

        self.sender = self._get_sender()
        if self.sender is None:
            return False

        return True

    def build_internal_request(self):
        ''' build request in internal format '''
        if not self.validate():
            return None
        builder = RequestChecker(self.sender)
        internal_request = builder.build_request(self.params["action"], self.params["params"])
        if internal_request is None:
            logger.error("build internal request failed [%s]" % format_params(self.params))
            self.set_error(builder.get_error())
            return None

        return internal_request
