
import random
import sys
import time
import uuid
from .auth import QuerySignatureAuthHandler
from base_connection import HttpConnection, HTTPRequest
from utils.json import json_load, json_dump
from utils.misc import filter_out_none
from consolidator import RequestChecker
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import constants as const

class DesktopConnection(HttpConnection):

    """ Public connection to qingcloud service
    """
    req_checker = RequestChecker()

    def __init__(self, zone, conn, pool=None, expires=None,
                 retry_time=3, http_socket_timeout=60, debug=False, owner=None):
        """
        @param qy_access_key_id - the access key id
        @param qy_secret_access_key - the secret access key
        @param zone - the zone id to access
        @param host - the host to make the connection to
        @param port - the port to use when connect to host
        @param protocol - the protocol to access to web server, "http" or "https"
        @param pool - the connection pool
        @param retry_time - the retry_time when message send fail
        """
        if not conn:
            logger.error("vdi api connection config error.")
            return None

        qy_access_key_id = conn.get("qy_access_key_id")
        if not qy_access_key_id:
            qy_access_key_id = conn.get("access_key_id")

        qy_secret_access_key = conn.get("qy_secret_access_key")
        if not qy_secret_access_key:
            qy_secret_access_key = conn.get("secret_access_key")

        host = conn["host"]
        port = conn["port"]
        protocol = conn["protocol"]

        self.owner = owner
        # Set default zone
        self.zone = zone
        # Set retry times
        self.retry_time = retry_time

        super(DesktopConnection, self).__init__(
            qy_access_key_id, qy_secret_access_key, host, port, protocol,
            pool, expires, http_socket_timeout, debug)

        self._auth_handler = QuerySignatureAuthHandler(self.host,
                                                       self.qy_access_key_id, self.qy_secret_access_key)

    def send_request(self, action, body, url="/api/", verb="GET"):
        """ Send request
        """

        if "owner" not in body:
            body["owner"] = const.GLOBAL_ADMIN_USER_ID
        if "console_id" not in body:
            body["console_id"] = const.USER_CONSOLE_ADMIN
        
        request = body
        request['action'] = action
        request.setdefault('zone', self.zone)
        if self.debug:
            print(json_dump(request))
            sys.stdout.flush()

        if self.expires:
            request['expires'] = self.expires

        retry_time = 0
        while retry_time < self.retry_time:
            # Use binary exponential backoff to desynchronize client requests
            next_sleep = random.random() * (2 ** retry_time)
            try:

                response = self.send(verb, url, request)

                if response.status == 200:
                    resp_str = response.read()
                    if type(resp_str) != str:
                        resp_str = resp_str.decode()

                    if self.debug:
                        print(resp_str)
                        sys.stdout.flush()
                    
                    result = json_load(resp_str) if resp_str else None
                    if not result:
                        logger.error("send request failure: %s, %s" % (action, body))
                    return result
            except Exception, e:
                logger.error("send request exception : %s, %s, %s" % (e, action, body))
                if retry_time < self.retry_time - 1:
                    self._get_conn(self.host, self.port)
                else:
                    return None

            time.sleep(next_sleep)
            retry_time += 1

    def _gen_req_id(self):
        return uuid.uuid4().hex

    def build_http_request(self, verb, url, base_params, auth_path=None,
                           headers=None, host=None, data=""):
        params = {}
        for key, values in base_params.items():
            if values is None:
                continue
            if isinstance(values, list):
                for i in range(1, len(values) + 1):
                    if isinstance(values[i - 1], dict):
                        for sk, sv in values[i - 1].items():
                            if isinstance(sv, dict) or isinstance(sv, list):
                                sv = json_dump(sv)
                            params['%s.%d.%s' % (key, i, sk)] = sv
                    else:
                        params['%s.%d' % (key, i)] = values[i - 1]
            else:
                params[key] = values
        
        _host = host if host else self.host
        return HTTPRequest(verb, self.protocol, headers, _host, self.port,
                           url, params, auth_path, data)

    def return_param_invaild(self, action, param):
        logger.error("param error : %s, %s" % (action, param))
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, (action, param))

    # error
    def check_res_error(self, ret, body):

        if not ret:
            logger.error("API Response is None: %s " % (body))
            return True

        if ret["ret_code"] != 0:
            logger.error("%s, %s" % (ret, body))
            return True

        return False

    def describe_desktop_groups(self, param):

        action = const.ACTION_VDI_DESCRIBE_DESKTOP_GROUPS
        
        valid_keys = ['desktop_groups', 'offset', 'limit']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=['offset', 'limit'],
                                             list_params=['desktop_groups']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def restart_desktops(self, param):

        action = const.ACTION_VDI_RESTART_DESKTOPS
        
        valid_keys = ['desktop_group', "desktops"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_desktops(self, desktops):

        action = const.ACTION_VDI_DESCRIBE_DESKTOPS

        valid_keys = ['desktops']
        body = filter_out_none(locals(), valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def start_desktops(self, param):

        action = const.ACTION_VDI_START_DESKTOPS

        valid_keys = ['desktop_group', "desktops"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def stop_desktops(self, param):

        action = const.ACTION_VDI_STOP_DESKTOPS
        valid_keys = ['desktop_group', "desktops"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_desktop_group_attributes(self, param):

        action = const.ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES
    
        valid_keys = ['desktop_group', "desktop_count", "desktop_image"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["desktop_group"],
                                             integer_params=["desktop_count"],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_desktop_group_status(self, param):

        action = const.ACTION_VDI_MODIFY_DESKTOP_GROUP_STATUS
        valid_keys = ['desktop_group', 'status']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["desktop_group", "status"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def apply_desktop_group(self, param):

        action = const.ACTION_VDI_APPLY_DESKTOP_GROUP

        valid_keys = ['desktop_group']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["desktop_group"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_desktop_group(self, param):

        action = const.ACTION_VDI_CREATE_DESKTOP_GROUP

        valid_keys = ["description", "desktop_group_name", "desktop_group_type", "disk_name",
                      "naming_rule", "desktop_image", "desktop_dn", "managed_resource", "allocation_type", "place_group_id",
                      "desktop_count", "gpu", "gpu_class", "is_create", "save_disk", "save_desk", "disk_size",
                      "usbredir", "clipboard", "filetransfer", "qxl_number", "cpu", "memory", "instance_class",
                      "users", "networks", "ivshmem", "is_load"]
    
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                              required_params=["desktop_image", "cpu", "memory", "desktop_group_type", "naming_rule", "instance_class"],
                                              integer_params=["desktop_count", "gpu", "gpu_class", "is_create", "save_disk", "save_desk",
                                                              "usbredir", "clipboard", "filetransfer", "qxl_number", "cpu", "memory", "instance_class", "is_load"],
                                              list_params=["users", "networks", "ivshmem"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_app_desktop_group(self, param):

        action = const.ACTION_VDI_CREATE_APP_DESKTOP_GROUP

        valid_keys = ["description", "desktop_group_name", "managed_resource", "is_load"]

        body = filter_out_none(param, valid_keys)
        logger.error("create_app_desktop_group %s" % body)
        if not self.req_checker.check_params(body,
                                              required_params=["desktop_group_name", "managed_resource"],
                                              integer_params=["is_load"],
                                              list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def add_desktop_to_delivery_group(self, param):
        '''
            @param directive : the dictionary of params
        '''
        
        action = const.ACTION_VDI_ADD_DESKTOP_TO_DELIVERY_GROUP
        valid_keys = ['desktop_user', 'delivery_group']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                  required_params=['desktop_user', 'delivery_group'],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return self.return_param_invaild(action, body)
        
        return self.send_request(action, body)
    
    def delete_desktop_from_delivery_group(self, param):
        '''
            @param directive : the dictionary of params
        '''
        
        action = const.ACTION_VDI_DEL_DESKTOP_FROM_DELIVERY_GROUP
        valid_keys = ['desktops']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                  required_params=['desktops'],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return self.return_param_invaild(action, body)
        
        return self.send_request(action, body)    
    
    def detach_desktop_from_delivery_group_user(self, param):
        '''
            @param directive : the dictionary of params
        '''
        
        action = const.ACTION_VDI_DETACH_DESKTOP_FROM_DELIVERY_GROUP_USER
        valid_keys = ['desktop']
        body = filter_out_none(param, valid_keys)

        if not self.req_checker.check_params(body,
                                  required_params=['desktop'],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return self.return_param_invaild(action, body)
        
        return self.send_request(action, body)        

    def add_user_to_delivery_group(self, param):

        action = const.ACTION_VDI_ADD_USER_TO_DELIVERY_GROUP

        valid_keys = ['users', 'delivery_group']

        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["delivery_group", "users"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def detach_user_from_desktop(self, param):

        action = const.ACTION_VDI_DETACH_USER_FROM_DESKTOP

        valid_keys = ['desktops']

        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["desktops"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_desktops(self, param):

        action = const.ACTION_VDI_DELETE_DESKTOPS

        valid_keys = ['desktops']

        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["desktops"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def del_user_from_delivery_group(self, param):

        action = const.ACTION_VDI_DEL_USER_FROM_DELIVERY_GROUP

        valid_keys = ['users', 'delivery_group']

        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["delivery_group", "users"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_jobs(self, jobs, offset=0, limit=100):

        action = const.ACTION_VDI_DESCRIBE_DESKTOP_JOBS
        valid_keys = ['jobs', "offset", "limit"]
        body = filter_out_none(locals(), valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["jobs"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_task(self, jobs, offset=0, limit=100):

        action = const.ACTION_VDI_DESCRIBE_DESKTOP_TASKS
        valid_keys = ['jobs', "offset", "limit"]
        body = filter_out_none(locals(), valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["jobs"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)


    def create_desktop_snapshots(self, param):

        action = const.ACTION_VDI_CREATE_DESKTOP_SNAPSHOTS

        valid_keys = ['resources', "snapshot_group","is_full"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_desktop_snapshots(self, snapshots):
        '''
            @param directive : the dictionary of params
        '''
        action = const.ACTION_VDI_DELETE_DESKTOP_SNAPSHOTS

        valid_keys = ['snapshots']
        body = filter_out_none(locals(), valid_keys)

        if not self.req_checker.check_params(body,
                                             required_params=["snapshots"],
                                             integer_params=[],
                                             list_params=["snapshots"]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

    def describe_auth_users(self, auth_service_id, user_names=None, base_dn=None, search_name=None, scope=1, global_search=None):

        action = const.ACTION_VDI_DESCRIBE_AUTH_USERS

        valid_keys = ['user_names', 'base_dn', 'search_name', 'scope', 'global_search']
        body = filter_out_none(locals(), valid_keys)
        
        body["auth_service"] = auth_service_id

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

    def create_auth_user(self, auth_service_id, user_info):
        
        action = const.ACTION_VDI_CREATE_AUTH_USER

        valid_keys = ['user_name', 'password', "base_dn", "account_control", "real_name", "email", "description", "auth_service",
                      'position', 'title', 'personal_phone', 'company_phone']
        body = filter_out_none(user_info, valid_keys)
        body["auth_service"] = auth_service_id
        if "ou_dn" in user_info:
            body["base_dn"] = user_info["ou_dn"]

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service", "user_name", 'password', "base_dn"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

    def modify_auth_user_attributes(self, auth_service_id, user_info):
        
        action = const.ACTION_VDI_MODIFY_AUTH_USER_ATTRIBUTES

        valid_keys = ['user_name', "real_name", "email", "description",
                      'position', 'title', 'personal_phone', 'company_phone']
        body = filter_out_none(user_info, valid_keys)
        
        body["auth_service"] = auth_service_id

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service", "user_name"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)


    def reset_auth_user_password(self, auth_service_id, user_name, password):
        
        action = const.ACTION_VDI_RESET_AUTH_USER_PASSWORD

        valid_keys = ['user_name', "password"]
        body = filter_out_none(locals(), valid_keys)
        
        body["auth_service"] = auth_service_id

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service", "user_name", "password"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

    def delete_auth_users(self, auth_service_id, user_names):
        
        action = const.ACTION_VDI_DELETE_AUTH_USERS

        valid_keys = ['user_names']
        body = filter_out_none(locals(), valid_keys)
        
        body["auth_service"] = auth_service_id

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service", "user_names"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

    def set_auth_user_status(self, auth_service_id, user_names, status):
        
        action = const.ACTION_VDI_SET_AUTH_USER_STATUS

        valid_keys = ['user_names', 'status']
        body = filter_out_none(locals(), valid_keys)
        
        body["auth_service"] = auth_service_id

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service", "user_names", "status"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

    def refresh_auth_service(self, auth_service_id, base_dn):
        
        action = const.ACTION_VDI_REFRESH_AUTH_SERVICE

        valid_keys = ['base_dn']
        body = filter_out_none(locals(), valid_keys)
        
        body["auth_service"] = auth_service_id

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service", "base_dn"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

    def resource_describe_auth_ous(self, auth_service_id, base_dn,ou_names, scope, syn_desktop):

        action = const.ACTION_VDI_DESCRIBE_AUTH_OUS

        valid_keys = ['base_dn','ou_name','scope','syn_desktop']
        body = filter_out_none(locals(), valid_keys)
        
        body["auth_service"] = auth_service_id
        body["ou_names"] = ou_names
        body["scope"] = scope
        body["syn_desktop"] = syn_desktop

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

    def create_auth_ou(self, auth_service_id, base_dn, ou_name, description=''):

        action = const.ACTION_VDI_CREATE_AUTH_OU

        valid_keys = ['base_dn', 'ou_name']
        body = filter_out_none(locals(), valid_keys)
        
        body["auth_service"] = auth_service_id

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service", "base_dn", "ou_name"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

    def add_auth_user_to_user_group(self, auth_service_id, user_group_dn, user_names):

        action = const.ACTION_VDI_ADD_AUTH_USER_TO_USER_GROUP

        valid_keys = ['user_group_dn', 'user_names']
        body = filter_out_none(locals(), valid_keys)
        body["auth_service"] = auth_service_id

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service", "user_group_dn", "user_names"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

    def remove_auth_user_from_user_group(self, auth_service_id, user_group_dn, user_names):

        action = const.ACTION_VDI_REMOVE_AUTH_USER_FROM_USER_GROUP

        valid_keys = ['user_group_dn', 'user_names']
        body = filter_out_none(locals(), valid_keys)
        
        body["auth_service"] = auth_service_id

        if not self.req_checker.check_params(body,
                                             required_params=["auth_service", "user_group_dn", "user_names"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
    
        return self.send_request(action, body)

