'''
Created on 2012-6-26

@author: yunify
'''
from request.consolidator.request_builder import RequestBuilder
import context
from utils.misc import is_integer, is_str, get_byte_len, strip_xss_chars, format_params
from utils.passwd import is_ascii_passwd
from utils.email_tool import is_email_valid
from utils.misc import to_list
from utils.time_stamp import parse_utctime
from utils.net import get_ip_network, is_valid_host
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.json import json_load
import re
from datetime import datetime
from constants import (
    EN,ZH_CN,
    VDI_SUPPORT_SYSTEM_CONFIG_ITEMS,
    # desktop group
    ACTION_VDI_CREATE_DESKTOP_GROUP,
    ACTION_VDI_DESCRIBE_DESKTOP_GROUPS,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_IMAGE,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_DESKTOP_COUNT,
    ACTION_VDI_DELETE_DESKTOP_GROUPS,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_STATUS,
    ACTION_VDI_DESCRIBE_DESKTOP_GROUP_DISKS,
    ACTION_VDI_CREATE_DESKTOP_GROUP_DISK,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_DISK,
    ACTION_VDI_DELETE_DESKTOP_GROUP_DISKS,
    ACTION_VDI_DESCRIBE_DESKTOP_GROUP_NETWORKS,
    ACTION_VDI_CREATE_DESKTOP_GROUP_NETWORK,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_NETWORK,
    ACTION_VDI_DELETE_DESKTOP_GROUP_NETWORKS,
    ACTION_VDI_DESCRIBE_DESKTOP_GROUP_USERS,
    ACTION_VDI_DESCRIBE_DESKTOP_IPS,
    ACTION_VDI_ATTACH_USER_TO_DESKTOP_GROUP,
    ACTION_VDI_DETACH_USER_FROM_DESKTOP_GROUP,
    ACTION_VDI_SET_DESKTOP_GROUP_USER_STATUS,
    ACTION_VDI_APPLY_DESKTOP_GROUP,
    # vxnet
    ACTION_VDI_DESCRIBE_DESKTOP_NETWORKS,
    ACTION_VDI_CREATE_DESKTOP_NETWORK,
    ACTION_VDI_MODIFY_DESKTOP_NETWORK_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOP_NETWORKS,
    ACTION_VDI_DESCRIBE_SYSTEM_NETWORKS,
    ACTION_VDI_LOAD_SYSTEM_NETWORK,
    ACTION_VDI_DESCRIBE_DESKTOP_ROUTERS,

    # desktop
    ACTION_VDI_CREATE_DESKTOP,
    ACTION_VDI_DESCRIBE_NORMAL_DESKTOPS,
    ACTION_VDI_DESCRIBE_DESKTOPS,
    ACTION_VDI_MODIFY_DESKTOP_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOPS,
    ACTION_VDI_ATTACH_USER_TO_DESKTOP,
    ACTION_VDI_DETACH_USER_FROM_DESKTOP,
    ACTION_VDI_RESTART_DESKTOPS,
    ACTION_VDI_START_DESKTOPS,
    ACTION_VDI_STOP_DESKTOPS,
    ACTION_VDI_RESET_DESKTOPS,
    ACTION_VDI_SET_DESKTOP_MONITOR,
    ACTION_VDI_SET_DESKTOP_AUTO_LOGIN,
    ACTION_VDI_MODIFY_DESKTOP_DESCRIPTION,
    ACTION_VDI_APPLY_RANDOM_DESKTOP,
    ACTION_VDI_FREE_RANDOM_DESKTOPS,
    ACTION_VDI_CREATE_BROKERS,
    ACTION_VDI_DELETE_BROKERS,
    ACTION_VDI_DESKTOP_LEAVE_NETWORKS,
    ACTION_VDI_DESKTOP_JOIN_NETWORKS,
    ACTION_VDI_MODIFY_DESKTOP_IP,
    ACTION_VDI_CHECK_DESKTOP_HOSTNAME,
    ACTION_VDI_REFRESH_DESKTOP_DB,
    # app
    ACTION_VDI_CREATE_APP_DESKTOP_GROUP,
    ACTION_VDI_DESCRIBE_APP_COMPUTES,
    ACTION_VDI_ADD_COMPUTE_TO_DESKTOP_GROUP,
    ACTION_VDI_DESCRIBE_APP_STARTMEMUS,
    ACTION_VDI_DESCRIBE_BROKER_APPS,
    ACTION_VDI_CREATE_BROKER_APPS,
    ACTION_VDI_MODIFY_BROKER_APP,
    ACTION_VDI_DELETE_BROKER_APPS,
    ACTION_VDI_ATTACH_BROKER_APP_TO_DELIVERY_GROUP,
    ACTION_VDI_DETACH_BROKER_APP_FROM_DELIVERY_GROUP,
    ACTION_VDI_CREATE_BROKER_FOLDER,
    ACTION_VDI_DELETE_BROKER_FOLDERS,
    ACTION_VDI_DESCRIBE_BROKER_FOLDERS,
    ACTION_VDI_CREATE_BROKER_APP_GROUP,
    ACTION_VDI_DELETE_BROKER_APP_GROUPS,
    ACTION_VDI_DESCRIBE_BROKER_APP_GROUPS,
    ACTION_VDI_ATTACH_BROKER_APP_TO_APP_GROUP,
    ACTION_VDI_DETACH_BROKER_APP_FROM_APP_GROUP,
    ACTION_VDI_REFRESH_BROKER_APPS,
    # job
    ACTION_VDI_DESCRIBE_DESKTOP_JOBS,
    ACTION_VDI_DESCRIBE_DESKTOP_TASKS,
    # monitor
    ACTION_VDI_GET_DESKTOP_MONITOR,
    # volume
    ACTION_VDI_CREATE_DESKTOP_DISKS,
    ACTION_VDI_DELETE_DESKTOP_DISKS,
    ACTION_VDI_ATTACH_DISK_TO_DESKTOP,
    ACTION_VDI_DETACH_DISK_FROM_DESKTOP,
    ACTION_VDI_DESCRIBE_DESKTOP_DISKS,
    ACTION_VDI_RESIZE_DESKTOP_DISKS,
    ACTION_VDI_MODIFY_DESKTOP_DISK_ATTRIBUTES,
    # image
    ACTION_VDI_CREATE_DESKTOP_IMAGE,
    ACTION_VDI_SAVE_DESKTOP_IMAGES,
    ACTION_VDI_DESCRIBE_DESKTOP_IMAGES,
    ACTION_VDI_DELETE_DESKTOP_IMAGES,
    ACTION_VDI_MODIFY_DESKTOP_IMAGE_ATTRIBUTES,
    ACTION_VDI_DESCRIBE_SYSTEM_IMAGES,
    ACTION_VDI_LOAD_SYSTEM_IMAGES,
    # scheduler
    ACTION_VDI_DESCRIBE_SCHEDULER_TASKS,
    ACTION_VDI_CREATE_SCHEDULER_TASK,
    ACTION_VDI_MODIFY_SCHEDULER_TASK_ATTRIBUTES,
    ACTION_VDI_DELETE_SCHEDULER_TASKS,
    ACTION_VDI_DESCRIBE_SCHEDULER_TASK_HISTORY,
    ACTION_VDI_ADD_RESOURCE_TO_SCHEDULER_TASK,
    ACTION_VDI_DELETE_RESOURCE_FROM_SCHEDULER_TASK,
    ACTION_VDI_SET_SCHEDULER_TASK_STATUS,
    ACTION_VDI_EXECUTE_SCHEDULER_TASK,
    ACTION_VDI_GET_SCHEDULER_TASK_RESOURCES,
    ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_COUNT,
    ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_IMAGE,

    # system
    ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_CONFIG,
    ACTION_VDI_MODIFY_DESKTOP_SYSTEM_CONFIG,
    ACTION_VDI_DESCRIBE_DESKTOP_BASE_SYSTEM_CONFIG,
    ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_LOGS,
    ACTION_VDI_CREATE_SYSLOG_SERVER,
    ACTION_VDI_MODIFY_SYSLOG_SERVER,
    ACTION_VDI_DELETE_SYSLOG_SERVERS,
    ACTION_VDI_DESCRIBE_SYSLOG_SERVERS,

    ACTION_VDI_MODIFY_APPROVALNOTICE_CONFIG,
    ACTION_VDI_DESCRIBE_APPROVALNOTICE_CONFIG,
    # policy
    ACTION_VDI_CREATE_USB_PROLICY,
    ACTION_VDI_MODIFY_USB_PROLICY,
    ACTION_VDI_DELETE_USB_PROLICY,
    ACTION_VDI_DESCRIBE_USB_PROLICY,
    # license
    ACTION_VDI_UPDATE_LICENSE,
    ACTION_VDI_DESCRIBE_LICENSE,

    # user desktop session
    ACTION_VDI_DESCRIBE_USER_DESKTOP_SESSION,
    ACTION_VDI_LOGOUT_USER_DESKTOP_SESSION,
    ACTION_VDI_MODIFY_USER_DESKTOP_SESSION,

    #log
    ACTION_VDI_DOWNLOAD_LOG
)
from constants import (
    LONG_STR_PARAMS,
    EXTRA_LONG_STR_PARAMS,
    FILE_CONTENT_PARAMS,
    NORMAL_STR_LEN,
    LONG_STR_LEN,
    EXTRA_LONG_STR_LEN,
    FILE_CONTENT_LEN,
    SUPPORTED_DG_TYPES,
    SUPPORTED_DESKTOP_GROUP_STATUS,
    SCHEDULER_TASK_TYPES,
    SUPPORT_DESKTOP_USER_STATUS,
    MIN_USER_NAME_LENGTH,
    MAX_USER_NAME_LENGTH,
    MAX_LIMIT_PARAM,
    SUPPORT_OS_SESSION_TYPE,
    SUPPORTED_CITIRX_ALLOC_TYPES,
    USB_POLICY_TYPE_BLACK, 
    USB_POLICY_TYPE_WHITE,
    SUPPORTED_QXL_NUMBER,
    SYSLOG_SERVER_STATUS_ACTINE,
    SYSLOG_SERVER_STATUS_INVALID,
    SYSLOG_SERVER_PROTOCOL_TCP,
    SYSLOG_SERVER_PROTOCOL_UDP,
    SUPPORTED_CITRIX_TYPES
)
    
from common import is_admin_user, is_citrix_platform, is_admin_console
from db.constants import RES_SCOPE_LIST,SUPPORT_SCOPE_RESOURCE_TYPE
import ast
from resource_control.user.session import refresh_session
from .security_policy.request_checker import SecurityPolicyRequestChecker
from .policy_group.request_checker import PolicyGroupRequestChecker
from .citrix_policy.request_checker import CitrixPolicyRequestChecker
from .zone.request_checker import ZoneRequestChecker
from .auth.request_checker import AuthRequestChecker
from .user.request_checker import DesktopUserRequestChecker
from .citrix.request_checker import CitrixRequestChecker
from .system.request_checker import SystemRequestChecker
from .snapshot.request_checker import SnapshotRequestChecker
from .terminal.request_checker import TerminalRequestChecker
from .module_custom.request_checker import ModuleCustomRequestChecker
from .system_custom.request_checker import SystemCustomRequestChecker
from .desktop_service_management.request_checker import DesktopServiceManagementRequestChecker
from .apply_approve.request_checker import ApplyApproveRequestChecker
from .workflow.request_checker import WorkFlowRequestChecker
from .component_version.request_checker import ComponentVersionRequestChecker
from .file_share.request_checker import FileShareRequestChecker
from .guest.request_checker import GuestRequestChecker

def parse_python_data(string):
    try:
        return ast.literal_eval(string)
    except:
        return None

class RequestChecker(object):

    ''' api request format checking '''

    # parameters that can be negative
    SPECIAL_INTEGER_PARAMS = ["auto_backup_time", "invoice_fee"]

    def __init__(self, sender):
        '''
        @param sender - the id of the sender of the request
        '''
        self.sender = sender                    # sender information
        self.builder = RequestBuilder(sender)   # api request builder
        self.zone = None                        # zone id in request
        # error message
        self.error = Error(ErrorCodes.INVALID_REQUEST_FORMAT)

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

    def _limit_parameter(self, directive):
        if not is_admin_user(self.sender):
            if 'limit' in directive and is_integer(directive['limit']) and int(directive['limit']) > MAX_LIMIT_PARAM:
                directive['limit'] = MAX_LIMIT_PARAM
        return

    def _check_router_network(self, network):
        ''' check ip network for vxnet in router '''
        ip_network = get_ip_network(network)
        if ip_network is None or ip_network.prefixlen != 24 \
                or str(ip_network) != network:
            logger.error("illegal ip network [%s]" % (network))
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_IP_NETWORK, network)
            return False

        return True

    def _check_dhcp_ip(self, ip_address):

        ip = get_ip_network(ip_address)
        if ip is None or ip.prefixlen != 32:
            logger.error("illegal dhcp ip address [%s]" % (str(ip)))
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_DHCP_IP)
            return None

        ip_seq = int(str(ip[0]).split('.')[-1])
        if ip_seq < 1 or ip_seq > 254:
            logger.error("illegal dhcp ip address [%s]" % (str(ip)))
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_DHCP_IP)
            return None
    
        return str(ip[0])

    def _check_router_dhcp_ip(self, directive):
    
        for param in ["start_ip", "end_ip"]:
            if param in directive:
                ip = self._check_dhcp_ip(directive[param])
                if ip is None:
                    return None
                directive[param] = ip

        if "start_ip" in directive and "end_ip" in directive:
            if get_ip_network(directive['start_ip']) > get_ip_network(directive['end_ip']):
                logger.error("DHCP starting IP address [%s] should be smaller that ending address [%s]" % (directive['start_ip'], directive['end_ip']))
                self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_DYN_IP_START_SHOULD_SMALLER_THAT_IP_END, (directive['start_ip'], directive['end_ip']))
                return False
            
        return True

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

    def _check_email(self, email):
        ''' check email '''
        if not is_email_valid(email):
            logger.error("invalid email format [%s]" % (email))
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_EMAIL_ADDR)
            return False
        return True

    def _check_user_name(self, username):
        ''' check user password '''
        username = username.strip()
        if not is_ascii_passwd(username):
            logger.error("user name [%s] should be ASCII" % (username))
            self.set_error(ErrorMsg.ERR_MSG_PASSWD_SHOULD_BE_ASCII)
            return False
        if len(username) < MIN_USER_NAME_LENGTH or len(username) > MAX_USER_NAME_LENGTH:
            logger.error("user name [%s] is length  4-20 letters" % (username))
            self.set_error(ErrorMsg.ERR_MSG_USER_NAME_LENGTH)
            return False
        if (isinstance(username, unicode) and not re.search(u'^[a-zA-Z0-9_\s]*$',username)) or \
        (isinstance(username, str) and not re.search(r'^[a-zA-Z0-9_\s]*$',username)):
            self.set_error(ErrorMsg.ERR_MSG_USER_NAME_REGULAR)
            return False
        return True

    def _check_user_scope_items(self, json_str):

        json_items = json_load(json_str)
        if not isinstance(json_items, list):
            return False
        
        if len(json_items) == 0:
            return False
        
        for item in json_items:
            if 'resource_type' not in item.keys():
                self.set_error(ErrorMsg.ERR_MSG_CHECK_USER_SCOPE_RESOURCE_TYPE)
                return False
            if item['resource_type'] not in SUPPORT_SCOPE_RESOURCE_TYPE:
                self.set_error(ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, item['resource_type'])
                return False

            if 'operation' not in item.keys():
                self.set_error(ErrorMsg.ERR_MSG_CHECK_USER_SCOPE_OPERATION)
                return False

            if 'action_type' in item.keys():
                if not isinstance(item['action_type'], int):
                    self.set_error(ErrorMsg.ERR_MSG_CHECK_USER_SCOPE_ACTION_TYPE_NOT_INT)
                    return False

                if item['action_type'] not in RES_SCOPE_LIST:
                    self.set_error(ErrorMsg.ERR_MSG_CHECK_USER_SCOPE_ACTION_TYPE_VALUE)
                    return False

        return True

    def _check_system_config_items(self, json_str):

        json_items = json_load(json_str)
        if not isinstance(json_items, dict):
            logger.error("json_items is not dict.")
            return False
        
        if len(json_items) == 0:
            logger.error("json_items len = 0.")
            return False
        
        for item in json_items.keys():
            if item not in VDI_SUPPORT_SYSTEM_CONFIG_ITEMS:
                logger.error("[%s] is not in VDI_SUPPORT_SYSTEM_CONFIG_ITEMS" % item)
                self.set_error(ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER, item)
                return False
            if 'lang'==item and json_items['lang'] not in [EN, ZH_CN]:
                logger.error("lang [%s] is invalid" % json_items['lang'])
                self.set_error(ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, json_items['lang'])
                return False

        return True

    def _check_instance_class(self, zone, instance_class):

        ctx = context.instance()
        
        ret = ctx.zone_checker.check_instance_class(zone, instance_class)
        if isinstance(ret, Error):
            self.error = ret
            return False

        return True

    def _check_disk_size(self, zone, size):

        ctx = context.instance()

        ret = ctx.zone_checker.check_disk_size(zone, size)
        if isinstance(ret, Error):
            self.error = ret
            return False

        return True
    
    def _check_cpu_memory_pair(self, zone, cpu, memory):
        
        ctx = context.instance()
        
        if not cpu or not memory:
            logger.error("no cpu or memory param %s, %s" % (cpu, memory))
            self.set_error(ErrorMsg.ERR_MSG_MISSING_PARAMETER, ('cpu' if memory else "memory"))
            return False

        ret = ctx.zone_checker.check_cpu_memory_pairs(zone, cpu, memory)
        if isinstance(ret, Error):
            self.error = ret
            return False

        return True

    def _check_desktop_hostname(self, zone, hostname, max_length=10, max_label_length=10):
        
        ctx = context.instance()
        if is_citrix_platform(ctx, zone):
            return True
        
        if not is_valid_host(hostname, max_length, max_label_length):
            logger.error("illegal hostname name [%s]" % hostname)
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_HOST_NAME, hostname)
            return False
    
        return True

    def _check_desktop_group_type(self, desktop_group_types):

        if not isinstance(desktop_group_types, list):
            desktop_group_types = [desktop_group_types]

        for desktop_group_type in desktop_group_types:
            if desktop_group_type not in SUPPORTED_DG_TYPES:
                logger.error("illegal desktop group type [%s]" % (desktop_group_type))
                self.set_error(ErrorMsg.ERR_MSG_UNSUPPORTED_DESKTOP_GROUP_TYPE, desktop_group_type)
                return False

        return True

    def _check_delivery_group_type(self, delivery_group_types):
        '''
            @param group_type: desktop group type
        '''
        if not isinstance(delivery_group_types, list):
            delivery_group_types = [delivery_group_types]

        for delivery_group_type in delivery_group_types:
            if delivery_group_type not in SUPPORT_OS_SESSION_TYPE:
                logger.error("illegal delivery group type [%s]" % (delivery_group_type))
                self.set_error(ErrorMsg.ERR_MSG_UNSUPPORTED_DELIVERY_GROUP_TYPE, delivery_group_type)
                return False
        return True

    def _check_allocation_type_type(self, allocation_types):
        '''
            @param group_type: desktop group type
        '''
        if not isinstance(allocation_types, list):
            allocation_types = [allocation_types]

        for allocation_type in allocation_types:
            if allocation_type not in SUPPORTED_CITIRX_ALLOC_TYPES:
                logger.error("illegal delivery group type [%s]" % (allocation_type))
                self.set_error(ErrorMsg.ERR_MSG_UNSUPPORTED_CITRIX_ALLOC_TYPE, allocation_type)
                return False
        return True

    def _check_hide_desktop_type(self, hide_desktop):
        '''
            @param group_type: desktop group type
        '''
        if hide_desktop not in [0, 1]:
            logger.error("illegal hide desktop type [%s]" % (hide_desktop))
            self.set_error(ErrorMsg.ERR_MSG_HIDE_MODE_VALUE_ERROR, hide_desktop)
            return False
        return True

    def _check_delivery_type(self, delivery_types):
        '''
            @param group_type: desktop group type
        '''
        if not isinstance(delivery_types, list):
            delivery_types = [delivery_types]

        for delivery_type in delivery_types:
            if delivery_type not in SUPPORTED_CITRIX_TYPES:
                logger.error("illegal delivery_type [%s]" % (delivery_type))
                self.set_error(ErrorMsg.ERR_MSG_UNSUPPORTED_CITRIX_DELIVERY_TYPE, delivery_type)
                return False
        return True

    def _check_desktop_group_user_status(self, status):
        '''
            @param group_type: desktop group type
        '''
        if status not in SUPPORT_DESKTOP_USER_STATUS:
            logger.error("illegal desktop group user status [%s]" % (status))
            self.set_error(ErrorMsg.ERR_MSG_UNSUPPORTED_DESKTOP_GROUP_USER_STATUS, status)
            return False
        return True

    def _check_network_type(self, zone, network_types):

        ctx = context.instance()
        
        if not isinstance(network_types, list):
            network_types = [network_types]
        
        for network_type in network_types:
            ret = ctx.zone_checker.check_network_type(zone, network_type)
            if isinstance(ret, Error):
                self.error = ret
                return False

        return True

    def _check_desktop_group_status(self, status):
        
        if not isinstance(status, list):
            status = [status]
        
        for _status in status:
            if _status not in SUPPORTED_DESKTOP_GROUP_STATUS:
                logger.error("illegal desktop group type [%s]" % (_status))
                self.set_error(ErrorMsg.ERR_MSG_UNSUPPORTED_DESKTOP_GROUP_MODE, _status)
                return False

        return True

    def _check_task_type(self, task_type):
    
        if task_type not in SCHEDULER_TASK_TYPES:
            logger.error("illegal scheduler task type [%s]" % (task_type))
            self.set_error(ErrorMsg.ERR_MSG_UNSUPPORTED_TASK_TYPE, task_type)
            return False

        return True

    def _check_period(self, directive):
        ''' scheduler period format:
        * daily
        * weekly:1,2,3...7
        * monthly:1,2,3...-1
        '''
        period = directive['period']
        if period == 'daily':
            return True

        patterns = (
            "^daily$",
            "^weekly\:(\-?\d+(\,\-?\d+)*)$",
            "^monthly\:(\-?\d+(\,\-?\d+)*)$",
        )
        match = re.match("|".join(patterns), period)
        if not match:
            logger.error("invalid scheduler period [%s]", period)
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_SCHEDULER_PARAMETER, 'period')
            return False

        period_type, days = period.split(':')
        days = map(int, days.split(','))
        days_range = []
        if period_type == 'weekly':
            days_range = range(1, 8)
        elif period_type == 'monthly':
            days_range = range(1, 32) + [-1] # -1 means the end of month

        if any(d not in days_range for d in days):
            logger.error("invalid scheduler period days [%s]", period)
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_SCHEDULER_PARAMETER, 'period')
            return False

        # sort period days
        days = map(str, sorted(list(set(days))))
        directive['period'] = '%s:%s' % (period_type, ','.join(days))
        return True

    def _check_ymd(self, ymd):
        try:
            return bool(datetime.strptime(ymd, '%Y-%m-%d'))
        except:
            logger.error("invalid scheduler run time [%s], should be yyyy-mm-dd", ymd)
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_SCHEDULER_PARAMETER, 'ymd')
            return False

    def _refresh_session(self):
        try:
            sk = self.sender.get("sk")
            if is_admin_console(self.sender) and is_admin_user(self.sender):
                if sk is not None:
                    refresh_session(sk)
        except Exception,e:
            logger.error("refresh sender:[%s] session with Exception: %s." % (self.sender, e));
            pass

    def _check_hhmm(self, hhmm):
        match = re.match('^(\d{1,2})\:(\d{1,2})$', hhmm)
        if not match:
            logger.error("invalid scheduler run time [%s], should be hh:mm", hhmm)
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_SCHEDULER_PARAMETER, 'hhmm')
            return False

        hh, mm = map(int, match.groups())
        if hh > 23 or mm > 59:
            logger.error("invalid scheduler run time [%s], exceed hour/minute number", hhmm)
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_SCHEDULER_PARAMETER, 'hhmm')
            return False

        return True
    
    def _check_managed_resource(self, zone_id, managed_resource):
        
        ctx = context.instance()
        ret = ctx.zone_checker.check_managed_resource(zone_id, managed_resource)
        if isinstance(ret, Error):
            self.error = ret
            return False

        return True
    
    def build_request(self, action, directive):
        ''' build internal request according to specified action.
        '''
        handler_map = {
            # desktop group
            ACTION_VDI_DESCRIBE_DESKTOP_GROUPS: self.describe_desktop_groups, 
            ACTION_VDI_CREATE_DESKTOP_GROUP: self.create_desktop_group,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES: self.modify_desktop_group_attributes,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_IMAGE: self.modify_desktop_group_image,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_DESKTOP_COUNT: self.modify_desktop_group_desktop_count,
            ACTION_VDI_DELETE_DESKTOP_GROUPS: self.delete_desktop_groups,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_STATUS: self.modify_desktop_group_status,
            ACTION_VDI_DESCRIBE_DESKTOP_GROUP_DISKS: self.describe_desktop_group_disks,
            ACTION_VDI_CREATE_DESKTOP_GROUP_DISK: self.create_desktop_group_disk,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_DISK: self.modify_desktop_group_disk,
            ACTION_VDI_DELETE_DESKTOP_GROUP_DISKS: self.delete_desktop_group_disks,
            ACTION_VDI_DESCRIBE_DESKTOP_GROUP_NETWORKS: self.describe_desktop_group_networks,
            ACTION_VDI_DESCRIBE_DESKTOP_GROUP_USERS: self.describe_desktop_group_users,
            ACTION_VDI_DESCRIBE_DESKTOP_IPS: self.describe_desktop_ips,
            ACTION_VDI_CREATE_DESKTOP_GROUP_NETWORK: self.create_desktop_group_network,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_NETWORK: self.modify_desktop_group_network,
            ACTION_VDI_DELETE_DESKTOP_GROUP_NETWORKS: self.delete_desktop_group_networks,
            ACTION_VDI_ATTACH_USER_TO_DESKTOP_GROUP: self.attach_user_to_desktop_group,
            ACTION_VDI_DETACH_USER_FROM_DESKTOP_GROUP: self.detach_user_from_desktop_group,
            ACTION_VDI_SET_DESKTOP_GROUP_USER_STATUS: self.set_desktop_group_user_status,
            ACTION_VDI_APPLY_DESKTOP_GROUP: self.apply_desktop_group,
            # vxnets
            ACTION_VDI_DESCRIBE_DESKTOP_NETWORKS: self.describe_desktop_networks,
            ACTION_VDI_CREATE_DESKTOP_NETWORK: self.create_desktop_network,
            ACTION_VDI_MODIFY_DESKTOP_NETWORK_ATTRIBUTES: self.modify_desktop_network_attributes,
            ACTION_VDI_DELETE_DESKTOP_NETWORKS: self.delete_desktop_networks,
            ACTION_VDI_DESCRIBE_SYSTEM_NETWORKS: self.describe_system_networks,
            ACTION_VDI_LOAD_SYSTEM_NETWORK: self.load_system_network,
            ACTION_VDI_DESCRIBE_DESKTOP_ROUTERS: self.describe_desktop_routers,

            # desktop
            ACTION_VDI_CREATE_DESKTOP: self.create_desktop,
            ACTION_VDI_DESCRIBE_NORMAL_DESKTOPS: self.describe_normal_desktops,
            ACTION_VDI_DESCRIBE_DESKTOPS: self.describe_desktops,
            ACTION_VDI_MODIFY_DESKTOP_ATTRIBUTES: self.modify_desktop_attributes,
            ACTION_VDI_DELETE_DESKTOPS: self.delete_desktops,
            ACTION_VDI_ATTACH_USER_TO_DESKTOP: self.attach_user_to_desktop,
            ACTION_VDI_DETACH_USER_FROM_DESKTOP: self.detach_user_from_desktop,
            ACTION_VDI_RESTART_DESKTOPS: self.restart_desktops,
            ACTION_VDI_START_DESKTOPS: self.start_desktops,
            ACTION_VDI_STOP_DESKTOPS: self.stop_desktops,
            ACTION_VDI_RESET_DESKTOPS: self.reset_desktops,
            ACTION_VDI_SET_DESKTOP_MONITOR: self.set_desktop_monitor,
            ACTION_VDI_SET_DESKTOP_AUTO_LOGIN: self.set_desktop_auto_login,
            ACTION_VDI_MODIFY_DESKTOP_DESCRIPTION: self.modify_desktop_description,
            ACTION_VDI_APPLY_RANDOM_DESKTOP: self.apply_random_desktop,
            ACTION_VDI_FREE_RANDOM_DESKTOPS: self.free_random_desktops,
            ACTION_VDI_CREATE_BROKERS: self.create_brokers,
            ACTION_VDI_DELETE_BROKERS: self.delete_brokers,
            ACTION_VDI_DESKTOP_LEAVE_NETWORKS: self.desktop_leave_networks,
            ACTION_VDI_DESKTOP_JOIN_NETWORKS: self.desktop_join_networks,
            ACTION_VDI_MODIFY_DESKTOP_IP: self.modify_desktop_ip,
            ACTION_VDI_DESCRIBE_DESKTOP_JOBS: self.describe_desktop_jobs,
            ACTION_VDI_DESCRIBE_DESKTOP_TASKS: self.describe_desktop_tasks,
            ACTION_VDI_GET_DESKTOP_MONITOR: self.get_desktop_monitor,
            ACTION_VDI_CHECK_DESKTOP_HOSTNAME: self.check_desktop_hostname,
            ACTION_VDI_REFRESH_DESKTOP_DB: self.refresh_desktop_db,
            # app
            ACTION_VDI_CREATE_APP_DESKTOP_GROUP: self.create_app_desktop_group,
            ACTION_VDI_DESCRIBE_APP_COMPUTES: self.describe_app_computes,
            ACTION_VDI_ADD_COMPUTE_TO_DESKTOP_GROUP: self.add_compute_to_desktop_group,
            ACTION_VDI_DESCRIBE_APP_STARTMEMUS: self.describe_app_startmemus,
            ACTION_VDI_DESCRIBE_BROKER_APPS: self.describe_broker_apps,
            ACTION_VDI_CREATE_BROKER_APPS: self.create_broker_apps,
            ACTION_VDI_MODIFY_BROKER_APP: self.modify_broker_app,
            ACTION_VDI_DELETE_BROKER_APPS: self.delete_broker_apps,
            ACTION_VDI_CREATE_BROKER_APP_GROUP: self.create_broker_app_group,
            ACTION_VDI_DELETE_BROKER_APP_GROUPS: self.delete_broker_app_groups,
            ACTION_VDI_DESCRIBE_BROKER_APP_GROUPS: self.describe_broker_app_groups,
            ACTION_VDI_ATTACH_BROKER_APP_TO_APP_GROUP: self.attach_broker_app_to_app_group,
            ACTION_VDI_DETACH_BROKER_APP_FROM_APP_GROUP: self.detach_broker_app_from_app_group,
            ACTION_VDI_REFRESH_BROKER_APPS: self.refresh_broker_apps,
            
            ACTION_VDI_ATTACH_BROKER_APP_TO_DELIVERY_GROUP: self.attach_broker_app_to_delivery_group,
            ACTION_VDI_DETACH_BROKER_APP_FROM_DELIVERY_GROUP: self.detach_broker_app_from_delivery_group,
            ACTION_VDI_CREATE_BROKER_FOLDER: self.create_broker_folder,
            ACTION_VDI_DELETE_BROKER_FOLDERS: self.delete_broker_folders,
            ACTION_VDI_DESCRIBE_BROKER_FOLDERS: self.describe_broker_folers,
            # volume
            ACTION_VDI_CREATE_DESKTOP_DISKS: self.create_desktop_disks,
            ACTION_VDI_DELETE_DESKTOP_DISKS: self.delete_desktop_disks,
            ACTION_VDI_ATTACH_DISK_TO_DESKTOP: self.attach_disk_to_desktop,
            ACTION_VDI_DETACH_DISK_FROM_DESKTOP: self.detach_disk_from_desktop,
            ACTION_VDI_DESCRIBE_DESKTOP_DISKS: self.describe_desktop_disks,
            ACTION_VDI_RESIZE_DESKTOP_DISKS: self.resize_desktop_disks,
            ACTION_VDI_MODIFY_DESKTOP_DISK_ATTRIBUTES: self.modify_desktop_disk_attributes,
            # image
            ACTION_VDI_CREATE_DESKTOP_IMAGE: self.create_desktop_image,
            ACTION_VDI_SAVE_DESKTOP_IMAGES: self.save_desktop_images,
            ACTION_VDI_DESCRIBE_DESKTOP_IMAGES: self.describe_desktop_images,
            ACTION_VDI_DELETE_DESKTOP_IMAGES: self.delete_desktop_images,
            ACTION_VDI_MODIFY_DESKTOP_IMAGE_ATTRIBUTES: self.modify_desktop_image_attributes,
            ACTION_VDI_DESCRIBE_SYSTEM_IMAGES: self.describe_system_images,
            ACTION_VDI_LOAD_SYSTEM_IMAGES: self.load_system_images,
    
            # schduler
            ACTION_VDI_DESCRIBE_SCHEDULER_TASKS: self.describe_scheduler_tasks,
            ACTION_VDI_CREATE_SCHEDULER_TASK: self.create_scheduler_task,
            ACTION_VDI_MODIFY_SCHEDULER_TASK_ATTRIBUTES: self.modify_scheduler_task_attributes,
            ACTION_VDI_DELETE_SCHEDULER_TASKS: self.delete_scheduler_tasks,
            ACTION_VDI_DESCRIBE_SCHEDULER_TASK_HISTORY: self.describe_scheduler_task_history,
            ACTION_VDI_ADD_RESOURCE_TO_SCHEDULER_TASK: self.add_resource_to_scheduler_task,
            ACTION_VDI_DELETE_RESOURCE_FROM_SCHEDULER_TASK: self.delete_resource_from_scheduler_task,
            ACTION_VDI_SET_SCHEDULER_TASK_STATUS: self.set_scheduler_task_status,
            ACTION_VDI_EXECUTE_SCHEDULER_TASK: self.execute_scheduler_task,
            ACTION_VDI_GET_SCHEDULER_TASK_RESOURCES: self.get_scheduler_task_resources,
            ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_COUNT: self.modify_scheduler_resource_desktop_count,
            ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_IMAGE: self.modify_scheduler_resource_desktop_image,

            # system config
            ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_CONFIG: self.describe_system_config,
            ACTION_VDI_MODIFY_DESKTOP_SYSTEM_CONFIG: self.modify_system_config,
            ACTION_VDI_DESCRIBE_DESKTOP_BASE_SYSTEM_CONFIG: self.describe_base_system_config,
            ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_LOGS: self.describe_desktop_system_logs,
            ACTION_VDI_CREATE_SYSLOG_SERVER: self.create_syslog_server,
            ACTION_VDI_MODIFY_SYSLOG_SERVER: self.modify_syslog_server,
            ACTION_VDI_DELETE_SYSLOG_SERVERS: self.delete_syslog_servers,
            ACTION_VDI_DESCRIBE_SYSLOG_SERVERS: self.describe_syslog_servers,
            ACTION_VDI_MODIFY_APPROVALNOTICE_CONFIG: self.modify_approvalnotice_config,
            ACTION_VDI_DESCRIBE_APPROVALNOTICE_CONFIG: self.describe_approvalnotice_config,
            # policy
            ACTION_VDI_CREATE_USB_PROLICY: self.create_desktop_usb_policy,
            ACTION_VDI_MODIFY_USB_PROLICY: self.modify_desktop_usb_policy,
            ACTION_VDI_DELETE_USB_PROLICY: self.delete_desktop_usb_policy,
            ACTION_VDI_DESCRIBE_USB_PROLICY: self.describe_desktop_usb_policy,

            # license
            ACTION_VDI_UPDATE_LICENSE: self.update_license,
            ACTION_VDI_DESCRIBE_LICENSE: self.describe_license,

            # user desktop session
            ACTION_VDI_DESCRIBE_USER_DESKTOP_SESSION: self.describe_user_desktop_session,
            ACTION_VDI_LOGOUT_USER_DESKTOP_SESSION: self.logout_user_desktop_session,
            ACTION_VDI_MODIFY_USER_DESKTOP_SESSION: self.modify_user_desktop_session,

            #log
            ACTION_VDI_DOWNLOAD_LOG: self.download_log
        }
        
        handler_map.update(SecurityPolicyRequestChecker(self, self.sender).handler_map)
        handler_map.update(PolicyGroupRequestChecker(self, self.sender).handler_map)
        handler_map.update(CitrixPolicyRequestChecker(self, self.sender).handler_map)
        handler_map.update(ZoneRequestChecker(self, self.sender).handler_map)
        handler_map.update(AuthRequestChecker(self, self.sender).handler_map)
        handler_map.update(DesktopUserRequestChecker(self, self.sender).handler_map)
        handler_map.update(CitrixRequestChecker(self, self.sender).handler_map)
        handler_map.update(SystemRequestChecker(self, self.sender).handler_map)
        handler_map.update(SnapshotRequestChecker(self, self.sender).handler_map)
        handler_map.update(TerminalRequestChecker(self, self.sender).handler_map)
        handler_map.update(ModuleCustomRequestChecker(self, self.sender).handler_map)
        handler_map.update(SystemCustomRequestChecker(self, self.sender).handler_map)
        handler_map.update(DesktopServiceManagementRequestChecker(self, self.sender).handler_map)
        handler_map.update(ApplyApproveRequestChecker(self, self.sender).handler_map)
        handler_map.update(WorkFlowRequestChecker(self, self.sender).handler_map)
        handler_map.update(ComponentVersionRequestChecker(self, self.sender).handler_map)
        handler_map.update(FileShareRequestChecker(self, self.sender).handler_map)
        handler_map.update(GuestRequestChecker(self, self.sender).handler_map)

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

        # limitation on limit parameter
        self._limit_parameter(directive)
        
        # build request
        try:
            self.zone = directive.get("zone", None)
            request = handler_map[action](directive)
            # refresh session
            self._refresh_session()
        except Exception, e:
            logger.exception("request params error [%s]", e)
            self.set_error(ErrorMsg.ERR_MSG_ILLEGAL_REQUEST)
            return None
        return request

    def create_desktop_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_image", "cpu", "memory", "desktop_group_type", "naming_rule", "instance_class"],
                                  str_params=["zone", "description", "desktop_group_name", "desktop_group_type", "disk_name",
                                              "naming_rule", "desktop_image", "desktop_dn", "managed_resource", "allocation_type", "place_group_id", 
                                              "cpu_model", "cpu_topology", "security_group", "provision_type"],
                                  integer_params=["desktop_count", "gpu", "gpu_class", "is_create", "save_disk", "save_desk", "is_load",
                                                  "usbredir", "clipboard", "filetransfer", "cpu", "memory", "instance_class", "ivshmem",
                                                  "qxl_number"],
                                  list_params=["users", "networks"]):
            return None
        
        zone = directive["zone"]
        # check cpu/memory
        cpu = directive['cpu']
        memory = directive['memory']
        if not self._check_cpu_memory_pair(zone, cpu, memory):
            return None
        
        # check desktop group type
        desktop_group_type = directive["desktop_group_type"]
        if not self._check_desktop_group_type(desktop_group_type):
            return None

        instance_class = directive["instance_class"]
        if not self._check_instance_class(zone, instance_class):
            return None
       
        if "qxl_number" in directive and directive["qxl_number"] not in SUPPORTED_QXL_NUMBER:
            self.set_error(ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, ("qxl_number"))
            return None

        if "naming_rule" in directive and directive['naming_rule'] and not self._check_desktop_hostname(zone, directive['naming_rule']):
            return None
        
        if "managed_resource" in directive and not self._check_managed_resource(zone, directive["managed_resource"]):
            return None
        
        if "allocation_type" in directive and not self._check_allocation_type_type(directive["allocation_type"]):
            return None
        
        return self.builder.create_desktop_group(**directive)

    def describe_desktop_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "search_word", "sort_key", "user", "desktop_image"],
                                  integer_params=["limit", "offset", "verbose","check_desktop_dn"],
                                  list_params=["status", "desktop_groups", "desktop_group_type", "session_type", "provision_type"],
                                  filter_params=[]):
            return None

        desktop_group_type = directive.get("desktop_group_type")
        if desktop_group_type and not self._check_desktop_group_type(desktop_group_type):
            return None

        status = directive.get("status")
        if status and not self._check_desktop_group_status(status):
            return None
        
        return self.builder.describe_desktop_groups(**directive)

    def modify_desktop_group_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group"],
                                  str_params=["zone", "desktop_group", "desktop_group_name", "description", "desktop_dn"],
                                  integer_params=["cpu", "memory", "usbredir", "clipboard", "filetransfer", 
                                                  "is_create", "gpu", "gpu_class", "ivshmem_enable", "qxl_number"],
                                  list_params=[]):
            return None
        
        zone = directive["zone"]
    
        cpu = directive.get('cpu')
        memory = directive.get('memory')
        if cpu or memory:
            if not self._check_cpu_memory_pair(zone, cpu, memory):
                return None

        if "qxl_number" in directive and directive["qxl_number"] not in SUPPORTED_QXL_NUMBER:
            self.set_error(ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, ("qxl_number"))
            return None

        return self.builder.modify_desktop_group_attributes(**directive)

    def modify_desktop_group_image(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group"],
                                  str_params=["zone", "desktop_group", "desktop_image_id"],
                                  integer_params=[],
                                  list_params=[]):
            return None

        return self.builder.modify_desktop_group_image(**directive)

    def modify_desktop_group_desktop_count(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["desktop_group"],
                                  str_params=["desktop_group"],
                                  integer_params=["desktop_count"],
                                  list_params=[]):
            return None

        return self.builder.modify_desktop_group_desktop_count(**directive)

    def delete_desktop_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_groups"],
                                  str_params=["zone"],
                                  list_params=["desktop_groups"]):
            return None

        return self.builder.delete_desktop_groups(**directive)

    def modify_desktop_group_status(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group", "status"],
                                  str_params=["zone", "desktop_group", "status"],
                                  list_params=[]):
            return None

        if not self._check_desktop_group_status(directive["status"]):
            return None

        return self.builder.modify_desktop_group_status(**directive) 

    def describe_desktop_group_disks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group"],
                                  str_params=["zone", "desktop_group", "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["disk_config"]):
            return None
        return self.builder.describe_desktop_group_disks(**directive) 

    def create_desktop_group_disk(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group", "disk_size"],
                                  integer_params=["disk_size", "is_load"],
                                  str_params=["zone", "disk_name"],
                                  list_params=[]):
            return None
        return self.builder.create_desktop_group_disk(**directive)

    def modify_desktop_group_disk(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "disk_config"],
                                  integer_params=["size"],
                                  str_params=["zone", "disk_config", "disk_name"],
                                  list_params=[]):
            return None
        return self.builder.modify_desktop_group_disk(**directive) 

    def delete_desktop_group_disks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "disk_configs"],
                                  integer_params=[],
                                  str_params=["zone"],
                                  list_params=["disk_configs"]):
            return None
        return self.builder.delete_desktop_group_disks(**directive) 
    
    def describe_desktop_group_networks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "desktop_group", "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["network_config", "network_type"]):
            return None
        return self.builder.describe_desktop_group_networks(**directive) 

    def create_desktop_group_network(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group", "network"],
                                  str_params=["zone", "desktop_group", "start_ip", "end_ip", "network"],
                                  list_params=[]):
            return None

        return self.builder.create_desktop_group_network(**directive) 
    
    def modify_desktop_group_network(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "network_config", "start_ip", "end_ip"],
                                  str_params=["zone", "network_config", "start_ip", "end_ip"],
                                  list_params=[]):
            return None
        return self.builder.modify_desktop_group_network(**directive)
    
    def delete_desktop_group_networks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "network_configs"],
                                  str_params=["zone"],
                                  list_params=["network_configs"]):
            return None
        return self.builder.delete_desktop_group_networks(**directive) 

    def describe_desktop_group_users(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group"],
                                  str_params=["zone", "search_word", "sort_key", "desktop_group"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["users", "status"]):
            return None
        return self.builder.describe_desktop_group_users(**directive) 

    def describe_desktop_ips(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "search_word", "sort_key", "desktop_group", "network", "desktop"],
                                  integer_params=["limit", "offset", "verbose", "reverse", "is_free"],
                                  list_params=["private_ips", "status"]):
            return None
        return self.builder.describe_desktop_ips(**directive)

    def attach_user_to_desktop_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group", "users"],
                                  str_params=["zone", "desktop_group"],
                                  list_params=["users"]):
            return None
        return self.builder.attach_user_to_desktop_group(**directive) 
    
    def detach_user_from_desktop_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group", "users"],
                                  integer_params=[],
                                  str_params=["zone", "desktop_group"],
                                  list_params=["users"]):
            return None
        return self.builder.detach_user_from_desktop_group(**directive) 

    def set_desktop_group_user_status(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group", "users", "status"],
                                  str_params=["zone", "desktop_group", "status"],
                                  integer_params=[],
                                  list_params=["users"]):
            return None
        
        status = directive.get('status')
        if status and not self._check_desktop_group_user_status(status):
            return None

        return self.builder.set_desktop_group_user_status(**directive) 

    def apply_desktop_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group"],
                                  str_params=["zone", "desktop_group"],
                                  list_params=[]):
            return None
        return self.builder.apply_desktop_group(**directive)

    def describe_desktop_networks(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "reverse"],
                                  list_params=["networks", "network_type", "status"]):
            return None
        
        return self.builder.describe_desktop_networks(**directive)

    def create_desktop_network(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "ip_network"],
                                  str_params=["zone", "network_name", "ip_network", "start_ip", "end_ip", "description"],
                                  list_params=[]):
            return None

        if not self._check_router_network(directive["ip_network"]):
            return None
    
        if not self._check_router_dhcp_ip(directive):
            return None

        return self.builder.create_desktop_network(**directive)
    
    def modify_desktop_network_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "network"],
                                  str_params=["zone", "network_name", "description", "start_ip", "end_ip"],
                                  list_params=[]):
            return None

        if not self._check_router_dhcp_ip(directive):
            return None

        return self.builder.modify_desktop_network_attributes(**directive)

    def delete_desktop_networks(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "networks"],
                                  str_params=["zone"],
                                  list_params=["networks"]):
            return None

        return self.builder.delete_desktop_networks(**directive)

    def describe_system_networks(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone"],
                                  integer_params=["offset", "limit"],
                                  list_params=[]):
            return None

        return self.builder.describe_system_networks(**directive)

    def load_system_network(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "network"],
                                  str_params=["zone", "network", "network_name", "start_ip", "end_ip"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        if not self._check_router_dhcp_ip(directive):
            return None

        return self.builder.load_system_network(**directive)

    def describe_desktop_routers(self, directive):

        if not self._check_params(directive,
                                  required_params=['zone'],
                                  str_params=['zone', 'search_word'],
                                  integer_params=[ 'verbose', 'offset', 'limit', 'reverse', 'is_and'],
                                  list_params=['routers'],
                                  filter_params=[]):
            return None

        return self.builder.describe_desktop_routers(**directive)

    def create_desktop(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_image", "cpu", "memory", "hostname", "instance_class"],
                                  str_params=["zone", "desktop_image", "description",  
                                              "hostname", "user", "desktop_dn", "disk_name"],
                                  integer_params=["cpu", "memory", "instance_class", "gpu", "gpu_class", "qxl_number",
                                                  "usbredir", "clipboard", "filetransfer", "disk_size","ivshmem"],
                                  list_params=["disks", "networks"]):
            return None
        zone = directive["zone"]

        cpu = directive['cpu']
        memory = directive['memory']
        if not self._check_cpu_memory_pair(zone, cpu, memory):
            return None

        if "hostname" in directive and directive["hostname"] and not self._check_desktop_hostname(zone, directive["hostname"], max_length=15, max_label_length=15):
            return None

        instance_class = directive["instance_class"]
        if not self._check_instance_class(zone, instance_class):
            return None

        if "qxl_number" in directive and directive["qxl_number"] not in SUPPORTED_QXL_NUMBER:
            self.set_error(ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, ("qxl_number"))
            return None

        return self.builder.create_desktop(**directive)

    def describe_normal_desktops(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["hostname", "search_word", "sort_key", "user", "desktop_group","sf_cookies","user_name","password"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["desktops", "status"]):
            return None
        return self.builder.describe_normal_desktops(**directive) 

    def describe_desktops(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "hostname", "search_word", "sort_key", "user", "desktop_group","sf_cookie","delivery_group"],
                                  integer_params=["with_monitor","need_monitor", "limit", "offset", "verbose", "reverse", 'no_delivery_group'],
                                  list_params=["desktops", "desktop_image", "status", "instance_class"]):
            return None
        return self.builder.describe_desktops(**directive) 

    def modify_desktop_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop"],
                                  str_params=["zone", "desktop", "description"],
                                  integer_params=["cpu", "memory", "gpu", "usbredir", "clipboard", "filetransfer", 
                                                  "no_sync", "ivshmem", "qxl_number"],
                                  list_params=[]):
            return None

        zone = directive["zone"]
        cpu = directive.get('cpu')
        memory = directive.get('memory')
        if cpu or memory:
            if not self._check_cpu_memory_pair(zone, cpu, memory):
                return None

        if "qxl_number" in directive and directive["qxl_number"] not in SUPPORTED_QXL_NUMBER:
            self.set_error(ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, ("qxl_number"))
            return None

        return self.builder.modify_desktop_attributes(**directive) 
    
    def delete_desktops(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktops"],
                                  str_params=["zone"],
                                  integer_params=["save_disk"],
                                  list_params=["desktops"]):
            return None
        return self.builder.delete_desktops(**directive) 
    
    def attach_user_to_desktop(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop", "user_ids"],
                                  str_params=["zone", "desktop"],
                                  list_params=["user_ids"]):
            return None
        return self.builder.attach_user_to_desktop(**directive) 
    
    def detach_user_from_desktop(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_id", "user_ids"],
                                  str_params=["zone", "desktop_id"],
                                  list_params=["user_ids"]):
            return None
        return self.builder.detach_user_from_desktop(**directive) 

    def restart_desktops(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "desktop_group"],
                                  integer_params=[],
                                  list_params=["desktops"]):
            return None
        return self.builder.restart_desktops(**directive) 
    
    def start_desktops(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "desktop_group"],
                                  list_params=["desktops"]):
            return None
        return self.builder.start_desktops(**directive) 

    def stop_desktops(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "desktop_group"],
                                  list_params=["desktops"]):
            return None
        return self.builder.stop_desktops(**directive) 
    
    def reset_desktops(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "desktop_group"],
                                  integer_params=[],
                                  list_params=["desktops"]):
            return None
        return self.builder.reset_desktops(**directive) 

    def set_desktop_monitor(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktops", "monitor"],
                                  str_params=["zone"],
                                  integer_params=["monitor"],
                                  list_params=["desktops"]):
            return None
        return self.builder.set_desktop_monitor(**directive) 

    def set_desktop_auto_login(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop", "auto_login"],
                                  str_params=["zone", "desktop"],
                                  integer_params=["auto_login"],
                                  list_params=[]):
            return None
        return self.builder.set_desktop_auto_login(**directive) 

    def modify_desktop_description(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop"],
                                  str_params=["zone", "description", "desktop"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        return self.builder.modify_desktop_description(**directive) 

    def apply_random_desktop(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group", "user"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        return self.builder.apply_random_desktop(**directive) 

    def free_random_desktops(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktops"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        return self.builder.free_random_desktops(**directive) 

    def create_brokers(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "desktop_image", "desktop","sf_cookie", "protocol_type", "client_ip"],
                                  integer_params=["full_screen"],
                                  list_params=[]):
            return None
        return self.builder.create_brokers(**directive) 
    
    def delete_brokers(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone"],
                                  list_params=["desktops"]):
            return None
        return self.builder.delete_brokers(**directive) 

    def create_desktop_disks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "size", "desktops"],
                                  str_params=["zone", "disk_name"],
                                  integer_params=["size"],
                                  list_params=["desktops"]):
            return None
        
        zone = directive["zone"]
        size = directive["size"]
        if not self._check_disk_size(zone, size):
            return None

        return self.builder.create_desktop_disks(**directive) 

    def delete_desktop_disks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "disks"],
                                  str_params=["zone"],
                                  list_params=["disks"]):
            return None
        return self.builder.delete_desktop_disks(**directive) 
    
    def attach_disk_to_desktop(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "disks", 'desktop'],
                                  str_params=["zone", "desktop"],
                                  list_params=["disks"]):
            return None
        return self.builder.attach_disk_to_desktop(**directive) 

    def detach_disk_from_desktop(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "disks"],
                                  str_params=["zone"],
                                  list_params=["disks"]):
            return None
        return self.builder.detach_disk_from_desktop(**directive) 
    
    def describe_desktop_disks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["search_word", "sort_key", "owner", "desktop_group", "user", "desktop", "disk_config"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["disks", "status", "disk_type"]):
            return None
        return self.builder.describe_desktop_disks(**directive) 
    
    def resize_desktop_disks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "size", "disks"],
                                  str_params=["zone"],
                                  integer_params=["size"],
                                  list_params=["disks"]):
            return None
        zone = directive["zone"]
        size = directive["size"]
        if not self._check_disk_size(zone, size):
            return None
        return self.builder.resize_desktop_disks(**directive)

    def modify_desktop_disk_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","disk"],
                                  str_params=["zone","disk_name", "description"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        return self.builder.modify_desktop_disk_attributes(**directive)

    def desktop_join_networks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktops", "network"],
                                  str_params=["zone", "network"],
                                  list_params=["desktops"]):
            return None
        return self.builder.desktop_join_networks(**directive) 

    def desktop_leave_networks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktops", "network"],
                                  str_params=["zone", "network"],
                                  list_params=["desktops"]):
            return None
        return self.builder.desktop_leave_networks(**directive)

    def modify_desktop_ip(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop", "network", "private_ip"],
                                  str_params=["zone", "network", "desktop", "private_ip"],
                                  list_params=[]):
            return None
        return self.builder.modify_desktop_ip(**directive) 

    def describe_desktop_jobs(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "reverse"],
                                  list_params=["jobs", "status"]):
            return None
        return self.builder.describe_desktop_jobs(**directive) 

    def describe_desktop_tasks(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["search_word", "sort_key"],
                                  integer_params=["limit", "offset", "reverse"],
                                  list_params=["jobs", "status", "tasks"]):
            return None
        return self.builder.describe_desktop_tasks(**directive) 

    def get_desktop_monitor(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[
                                      "zone", "resource", "meters", "step", "start_time", "end_time"],
                                  str_params=["zone", "resource", "step"],
                                  integer_params=[],
                                  list_params=["meters"]):
            return None
        
        return self.builder.get_desktop_monitor(**directive)

    def check_desktop_hostname(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "hostname", "name_type"],
                                  str_params=["zone", "hostname", "name_type"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.check_desktop_hostname(**directive)

    def create_desktop_image(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_image", "cpu", "memory", "instance_class"],
                                  str_params=["zone", "image_name", "description", "desktop_image", "network", "private_ip"],
                                  integer_params=["cpu", "memory", "instance_class", "image_size"],
                                  list_params=[]):
            return None
        return self.builder.create_desktop_image(**directive)

    def save_desktop_images(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_images"],
                                  str_params=["zone"],
                                  list_params=["desktop_images"]):
            return None
        return self.builder.save_desktop_images(**directive) 
   
    def describe_desktop_images(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "owner", "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["desktop_images", "image_type", "status", "os_version", "session_type"]):
            return None
        return self.builder.describe_desktop_images(**directive) 
    
    def delete_desktop_images(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone"],
                                  list_params=["desktop_images"]):
            return None
        return self.builder.delete_desktop_images(**directive) 

    def modify_desktop_image_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_image"],
                                  str_params=["zone", "desktop_image", "image_name", "description"],
                                  list_params=[]):
            return None
        return self.builder.modify_desktop_image_attributes(**directive) 

    def describe_system_images(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["provider", "os_family"],
                                  integer_params=["limit", "offset"],
                                  list_params=["images"]):
            return None

        return self.builder.describe_system_images(**directive)

    def load_system_images(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "images"],
                                  str_params=["session_type", "os_version", "image_name"],
                                  list_params=["images"]):
            return None
        return self.builder.load_system_images(**directive)

    def describe_scheduler_tasks(self, directive):
    
        if not self._check_params(directive,
                                  required_params=['zone'],
                                  str_params=['zone', 'task_name', 'search_word', 'sort_key', 'task_type'],
                                  integer_params=['verbose', 'offset', 'limit', 'reverse'],
                                  list_params=['scheduler_tasks', 'resources', "status"]):
            return None

        return self.builder.describe_scheduler_tasks(**directive)

    def create_scheduler_task(self, directive):
    
        required_params = ['zone', 'repeat', 'hhmm', 'task_type']
        if str(directive.get('repeat')) == '1':
            required_params.append('period')
        else:
            required_params.append('ymd')

        if not self._check_params(directive,
                                  required_params=required_params,
                                  str_params=['zone', 'task_name', 'description', 'period', 'hhmm', "task_type", "description", 'term_time', 'resource_type'],
                                  integer_params=['repeat'],
                                  list_params=['resources']):
            return None
        
        ymd = directive.get("ymd")
        if ymd and not self._check_ymd(ymd):
            return None

        if not self._check_hhmm(directive['hhmm']):
            return None

        if 'period' in directive and not self._check_period(directive):
            return None

        return self.builder.create_scheduler_task(**directive)

    def modify_scheduler_task_attributes(self, directive):
    
        required_params = ['zone', 'scheduler_task']
        if 'repeat' in directive:
            if str(directive['repeat']) == '1':
                required_params.append('period')
            else:
                required_params.append('ymd')

        if not self._check_params(directive,
                                  required_params=required_params,
                                  str_params=['zone', 'task_name', 'description', 'period', 'hhmm', 'term_time'],
                                  integer_params=['repeat'],
                                  list_params=[]):
            return None

        if 'ymd' in directive and not self._check_ymd(directive['ymd']):
            return None

        if 'hhmm' in directive and not self._check_hhmm(directive['hhmm']):
            return None

        if 'period' in directive and not self._check_period(directive):
            return None

        return self.builder.modify_scheduler_task_attributes(**directive)

    def delete_scheduler_tasks(self, directive):
    
        if not self._check_params(directive,
                                  required_params=['zone', 'scheduler_tasks'],
                                  str_params=['zone'],
                                  integer_params=[],
                                  list_params=['scheduler_tasks']):
            return None

        return self.builder.delete_scheduler_tasks(**directive)

    def describe_scheduler_task_history(self, directive):
    
        if not self._check_params(directive,
                                  required_params=['zone', 'scheduler_task'],
                                  str_params=['zone', 'scheduler_task'],
                                  integer_params=['verbose', 'offset', 'limit'],
                                  list_params=["resources"]):
            return None

        return self.builder.describe_scheduler_task_history(**directive)

    def add_resource_to_scheduler_task(self, directive):

        if not self._check_params(directive,
                                  required_params=['zone', 'scheduler_task', 'resources'],
                                  str_params=['zone', 'scheduler_task'],
                                  list_params=["resources"]):
            return None
        
        return self.builder.add_resource_to_scheduler_task(**directive)

    def delete_resource_from_scheduler_task(self, directive):

        if not self._check_params(directive,
                                  required_params=['zone', 'scheduler_task', 'resources'],
                                  str_params=['zone', 'scheduler_task'],
                                  list_params=["resources"]):
            return None
        
        return self.builder.delete_resource_from_scheduler_task(**directive)

    def set_scheduler_task_status(self, directive):
    
        if not self._check_params(directive,
                                  required_params=['zone', 'scheduler_tasks', "status"],
                                  str_params=['zone', "status"],
                                  integer_params=[],
                                  list_params=['scheduler_tasks']):
            return None

        return self.builder.set_scheduler_task_status(**directive)

    def execute_scheduler_task(self, directive):
    
        if not self._check_params(directive,
                                  required_params=['zone', 'scheduler_task'],
                                  str_params=['zone', 'scheduler_task'],
                                  integer_params=[],
                                  list_params=[]):
            return None

        return self.builder.execute_scheduler_task(**directive)

    def get_scheduler_task_resources(self, directive):
    
        if not self._check_params(directive,
                                  required_params=['zone', 'scheduler_task'],
                                  str_params=['zone', 'scheduler_task', 'search_word', 'sort_key', "resource_type"],
                                  integer_params=['offset', 'limit', 'reverse'],
                                  list_params=[]):
            return None

        return self.builder.get_scheduler_task_resources(**directive)

    def modify_scheduler_resource_desktop_count(self, directive):
    
        if not self._check_params(directive,
                                  required_params=['zone', 'scheduler_task', "resource", "desktop_count"],
                                  str_params=['zone', 'scheduler_task', 'resource'],
                                  integer_params=["desktop_count"],
                                  list_params=[]):
            return None

        return self.builder.modify_scheduler_resource_desktop_count(**directive)

    def modify_scheduler_resource_desktop_image(self, directive):
    
        if not self._check_params(directive,
                                  required_params=['zone', 'scheduler_task', "resource", "desktop_image"],
                                  str_params=['zone', 'scheduler_task', 'resource', "desktop_image"],
                                  integer_params=[],
                                  list_params=[]):
            return None

        return self.builder.modify_scheduler_resource_desktop_image(**directive)

 
    def describe_system_config(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  list_params=["keys"]):
            return None

        return self.builder.describe_system_config(**directive)
    
    def modify_system_config(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['config_items'],
                                  json_params=['config_items']):
            return None
        if not self._check_system_config_items(directive['config_items']):
            logger.error("check config_items error")
            return None
        return self.builder.modify_system_config(**directive)
    
    def describe_base_system_config(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive):
            return None
        return self.builder.describe_base_system_config(**directive)

    def describe_desktop_system_logs(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=['user_id', 'user_name','user_role', 
                                              'action_name', 'sort_key', "search_word"],
                                  list_params = ['system_log_ids', 'columns','log_type'],
                                  integer_params=['offset', 'limit', 'reverse', 'is_and']):
            return None
        
        return self.builder.describe_desktop_system_logs(**directive)


    def create_syslog_server(self, directive):
        if not self._check_params(directive,
                                  required_params=['host', 'port', 'protocol', 'runtime'],
                                  integer_params=['port'],
                                  time_params=[],
                                  str_params=['host', 'protocol', 'runtime'],
                                  list_params = []):
            return None

        if "protocol" in directive and directive["protocol"] not in [SYSLOG_SERVER_PROTOCOL_TCP,SYSLOG_SERVER_PROTOCOL_UDP]:
            self.set_error("protocol value must be [TCP, UDP]")
            return None
        
        return self.builder.create_syslog_server(**directive)

    def modify_syslog_server(self, directive):
        if not self._check_params(directive,
                                  required_params=['syslog_server'],
                                  integer_params=['port'],
                                  time_params=[],
                                  str_params=['syslog_server', 'host', 'protocol', 'status', 'runtime'],
                                  list_params = []):
            return None

        if "status" in directive and directive["status"] not in [SYSLOG_SERVER_STATUS_ACTINE,SYSLOG_SERVER_STATUS_INVALID]:
            self.set_error("status value must be [active, invalid]")
            return None

        if "protocol" in directive and directive["protocol"] not in [SYSLOG_SERVER_PROTOCOL_TCP,SYSLOG_SERVER_PROTOCOL_UDP]:
            self.set_error("protocol value must be [TCP, UDP]")
            return None
        
        return self.builder.modify_syslog_server(**directive)

    def delete_syslog_servers(self, directive):
        if not self._check_params(directive,
                                  list_params = ["syslog_servers"]):
            return None
        
        return self.builder.delete_syslog_servers(**directive)

    def describe_syslog_servers(self, directive):
        if not self._check_params(directive,
                                  str_params=['host', 'protocol', 'sort_key', "search_word"],
                                  list_params = ['syslog_servers', 'status', 'columns'],
                                  integer_params=['port', 'offset', 'limit', 'reverse', 'is_and']):
            return None
        
        return self.builder.describe_syslog_servers(**directive)

    def create_desktop_usb_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['object_id', 'policy_type', 'priority', 'allow'],
                                  str_params=['policy_type', 'class_id', 'vendor_id', 'product_id', 'version_id'],
                                  integer_params=['priority', 'allow']):
            return None
        if 'policy_type' not in directive or directive['policy_type'] not in [USB_POLICY_TYPE_BLACK, USB_POLICY_TYPE_WHITE]:
            return None
        if 'allow' not in directive or directive['allow'] not in [0, 1]:
            return None
        if 'priority' not in directive or directive['priority'] < 0:
            return None

        return self.builder.create_desktop_usb_policy(**directive)
    
    def modify_desktop_usb_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['usb_policy_id'],
                                  str_params=['usb_policy_id', 'class_id', 'vendor_id', 'product_id', 'version_id'],
                                  integer_params=['priority', 'allow']):
            return None
        
        return self.builder.modify_desktop_usb_policy(**directive)
    
    def delete_desktop_usb_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  list_params = ['usb_policy_ids']):
            return None
        
        return self.builder.delete_desktop_usb_policy(**directive)
    
    def describe_desktop_usb_policy(self, directive):
        '''
            @param directive : the dictionary of params
        ''' 
        if not self._check_params(directive,
                                  str_params=['policy_type', 'class_id', 'vendor_id', 'product_id', 'version_id', 'sort_key'],
                                  integer_params=['priority', 'allow', 'offset', 'limit', 'reverse', 'is_and'],
                                  list_params = ['usb_policy_ids', 'object_ids', 'columns']):
            return None
        
        return self.builder.describe_desktop_usb_policy(**directive)

    def update_license(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['license_str'],
                                  str_params=['license_str']):
            return None
        return self.builder.update_license(**directive)

    def describe_license(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        return self.builder.describe_license(**directive)

    

    def describe_user_desktop_session(self, directive):

        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["approveEmpId", "approveState"],
                                  integer_params=["pageNo"]):
            return None
        
        return self.builder.describe_user_desktop_session(**directive)

    def logout_user_desktop_session(self, directive):

        if not self._check_params(directive,
                                  required_params=["workerUid"],
                                  str_params=["workerUid"]):
            return None
        
        return self.builder.logout_user_desktop_session(**directive)
    
    def modify_user_desktop_session(self, directive):

        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["applyEmpId", "hostname", "deliverGrpName"],
                                  integer_params=[]):
            return None
        
        return self.builder.modify_user_desktop_session(**directive)
    
    def modify_approvalnotice_config(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["approval_notice","approval_notice_title"],
                                  filter_params=[]):
            return None
        
        return self.builder.modify_approvalnotice_config(**directive)

    def describe_approvalnotice_config(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone"]):
            return None
        
        return self.builder.describe_approvalnotice_config(**directive)  

    def download_log(self, directive):

        if not self._check_params(directive,
                                  required_params=["date"],
                                  str_params=["date"]):
            return None

        return self.builder.download_log(**directive)
    
    def refresh_desktop_db(self, directive):

        if not self._check_params(directive,
                                  required_params=["db_type"],
                                  str_params=["db_type"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.refresh_desktop_db(**directive)

    def create_app_desktop_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group_name", "managed_resource"],
                                  str_params=["zone","desktop_group_name", "managed_resource"],
                                  integer_params=["is_load"],
                                  list_params=[]):
            return None
        
        return self.builder.create_app_desktop_group(**directive)

    def describe_app_computes(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "search_word"],
                                  str_params=["zone","search_word"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.describe_app_computes(**directive)

    def add_compute_to_desktop_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "desktop_group", "instance_id"],
                                  str_params=["zone", "desktop_group", "instance_id"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.add_compute_to_desktop_group(**directive)

    def describe_app_startmemus(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "delivery_group", "desktop"],
                                  str_params=["zone","delivery_group", "desktop"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.describe_app_startmemus(**directive)

    def describe_broker_apps(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["delivery_group", "search_word"],
                                  integer_params=["offset", "limit"],
                                  list_params=["broker_apps", "filter_delivery_groups", "broker_app_names"]):
            return None
        
        return self.builder.describe_broker_apps(**directive)

    def create_broker_apps(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "delivery_group", "desktop", "app_datas"],
                                  str_params=["zone", "delivery_group", "app_folder", "desktop"],
                                  integer_params=["is_startmemu"],
                                  list_params=[]):
            return None
        
        return self.builder.create_broker_apps(**directive)

    def modify_broker_app(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "broker_app"],
                                  str_params=["zone", "broker_app", "admin_display_name", "normal_display_name", "description"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.modify_broker_app(**directive)

    def delete_broker_apps(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "broker_apps"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["broker_apps"]):
            return None
        
        return self.builder.delete_broker_apps(**directive)

    def attach_broker_app_to_delivery_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone","delivery_group"],
                                  str_params=["zone","delivery_group"],
                                  integer_params=[],
                                  list_params=["broker_apps", "broker_app_groups"]):
            return None
        
        return self.builder.attach_broker_app_to_delivery_group(**directive)

    def detach_broker_app_from_delivery_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone","delivery_group"],
                                  str_params=["zone","delivery_group"],
                                  integer_params=[],
                                  list_params=["broker_app_groups", "broker_apps"]):
            return None
        
        return self.builder.detach_broker_app_from_delivery_group(**directive)

    def create_broker_folder(self, directive):

        if not self._check_params(directive,
                                  required_params=["db_type"],
                                  str_params=["db_type"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.create_broker_folder(**directive)

    def delete_broker_folders(self, directive):

        if not self._check_params(directive,
                                  required_params=["db_type"],
                                  str_params=["db_type"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.delete_broker_folders(**directive)

    def describe_broker_folers(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.describe_broker_folers(**directive)

    def create_broker_app_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "broker_app_group_name"],
                                  str_params=["zone", "broker_app_group_name","description"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.create_broker_app_group(**directive)

    def describe_broker_app_groups(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "search_word"],
                                  integer_params=["is_system", "offset", "limit"],
                                  list_params=["broker_app_groups"]):
            return None
        
        return self.builder.describe_broker_app_groups(**directive)

    def delete_broker_app_groups(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "broker_app_groups"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["broker_app_groups"]):
            return None
        
        return self.builder.delete_broker_app_groups(**directive)

    def attach_broker_app_to_app_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "broker_app_group", "broker_apps"],
                                  str_params=["zone", "broker_app_group"],
                                  integer_params=[],
                                  list_params=["broker_apps"]):
            return None
        
        return self.builder.attach_broker_app_to_app_group(**directive)

    def detach_broker_app_from_app_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "broker_app_group", "broker_apps"],
                                  str_params=["zone", "broker_app_group"],
                                  integer_params=[],
                                  list_params=["broker_apps"]):
            return None
        
        return self.builder.detach_broker_app_from_app_group(**directive)

    def refresh_broker_apps(self, directive):

        if not self._check_params(directive,
                                  required_params=["zone", "sync_type"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=[]):
            return None
        
        return self.builder.refresh_broker_apps(**directive)
