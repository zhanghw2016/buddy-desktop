import random
import sys
import time
import uuid
from .auth import QuerySignatureAuthHandler
from base_connection import HttpConnection, HTTPRequest
from utils.json import json_load, json_dump
from utils.misc import filter_out_none
from citrix import const as const
from consolidator import RequestChecker
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from constants import (
    PROVISION_TYPE_MCS,
)

NA = 'NA'
STEPS = {
    '5m': 300,
    '15m': 900,
    '30m': 1800,
    '1h': 3600,
    '2h': 7200,
    '1d': 24 * 3600,
}

class CitrixConnection(HttpConnection):
    """ Public connection to citrix service
    """
    req_checker = RequestChecker()

    def __init__(self, zone, conn, pool=None, expires=None,
                 retry_time=3, http_socket_timeout=120, debug=False, owner=None):
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
            logger.error("qingcloud api connection config error.")
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

        super(CitrixConnection, self).__init__(
            qy_access_key_id, qy_secret_access_key, host, port, protocol,
            pool, expires, http_socket_timeout, debug)

        self._auth_handler = QuerySignatureAuthHandler(self.host,
                                                       self.qy_access_key_id, self.qy_secret_access_key)

    def send_request(self, action, body, url="/api/", verb="GET"):
        """ Send request
        """

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
            logger.error("api response is None %s " % (body))
            return True

        if ret["ret_code"] != 0:
            logger.error("error message: %s, %s" % (ret, body))
            return True

        return False

    # computer catalogs
    def describe_computer_catalogs(self, param):

        action = const.ACTION_DESCRIBE_COMPUTER_CATALOGS
        valid_keys = ['catalog_names', 'verbose']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=["verbose"],
                                             list_params=['catalog_names']
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_computer_catalog(self, param):

        action = const.ACTION_CREATE_COMPUTER_CATALOG
        
        provision_type = param.get("provision_type", PROVISION_TYPE_MCS)
        if provision_type == PROVISION_TYPE_MCS:
            
            valid_keys = ["catalog_name", "hosting_unit", "allocation_type", "persist_user_changes", "session_type", "base_image",
                          "desktop_dn", "base_networks", "pri_networks", "cpu", "memory", "instance_class", "name_regular_pre", "description", "gpu", "gpu_class",
                          "place_group_id", "cpu_model", "cpu_topology", "ivshmem"]

            body = filter_out_none(param, valid_keys)
            if not self.req_checker.check_params(body,
                                                 required_params=["catalog_name", "hosting_unit", "allocation_type", "persist_user_changes", "session_type", "base_image",
                                                                  "desktop_dn", "cpu", "memory", "instance_class", "name_regular_pre"],
                                                 integer_params=["cpu", "memory", "instance_class", "gpu", "gpu_class"],
                                                 list_params=["base_networks", "pri_networks"]
                                                 ):
                return self.return_param_invaild(action, body)
        
        else:
            valid_keys = ["catalog_name", "allocation_type", "provision_type", "description", "session_type", "persist_user_changes"]
            body = filter_out_none(param, valid_keys)
            if not self.req_checker.check_params(body,
                                                 required_params=["catalog_name", "allocation_type"],
                                                 str_params=["catalog_name", "allocation_type", "provision_type", "description", "session_type"],
                                                 list_params=[]
                                                 ):
                return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_computer_catalog(self, param):

        action = const.ACTION_MODIFY_COMPUTER_CATALOG
        valid_keys = ['catalog_name', 'description', 'ivshmem', "desktop_dn", "gpu" ,"gpu_class", "cpu", "memory"]
        body = filter_out_none(param, valid_keys)
        if "desktop_dn" in body:
            body["ou"] = body["desktop_dn"]
        
        if not self.req_checker.check_params(body,
                                             required_params=['catalog_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def update_catalog_master_image(self, param):
        
        action = const.ACTION_UPDATE_CATALOG_MASTER_IMAGE
        valid_keys = ['catalog_name', 'hosting_unit', "new_base_image"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['catalog_name', 'hosting_unit', "new_base_image"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_computer_catalog(self, param):

        action = const.ACTION_DELETE_COMPUTER_CATALOG
        valid_keys = ['catalog_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["catalog_name"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)
    
    # delivery group
    def describe_delivery_groups(self, param):

        action = const.ACTION_DESCRIBE_DELIVERY_GROUPS
        valid_keys = ['delivery_group_names']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=["delivery_group_names"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_delivery_group(self, param):

        action = const.ACTION_CREATE_DELIVERY_GROUP
        valid_keys = ['delivery_group_name', 'session_type', 'desktop_kind', 'description', "delivery_type"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['delivery_group_name', 'session_type', 'desktop_kind'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_delivery_group(self, param):

        action = const.ACTION_MODIFY_DELIVERY_GROUP
        valid_keys = ['delivery_group_name', 'new_delivery_group_name', 'description']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['delivery_group_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_delivery_group(self, param):

        action = const.ACTION_DELETE_DELIVERY_GROUP
        valid_keys = ['delivery_group_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['delivery_group_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def attach_computer_to_delivery_group(self, param):

        action = const.ACTION_ATTACH_COMPUTER_TO_DELIVERY_GROUP
        valid_keys = ['delivery_group_name', 'machine_user_names']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['delivery_group_name', 'machine_user_names'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def detach_computer_from_delivery_group(self, param):

        action = const.ACTION_DETACH_COMPUTER_FROM_DELIVERY_GROUP
        valid_keys = ['delivery_group_name', 'machine_names']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['delivery_group_name', 'machine_names'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def attach_user_to_delivery_group(self, param):

        action = const.ACTION_ATTACH_USER_TO_DELIVERY_GROUP
        valid_keys = ['delivery_group_name', 'user_names']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['delivery_group_name', 'user_names'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def detach_user_from_delivery_group(self, param):

        action = const.ACTION_DETACH_USER_FROM_DELIVERY_GROUP
        valid_keys = ['delivery_group_name', 'user_names']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['delivery_group_name', 'user_names'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)


    def reset_users_to_delivery_group(self, param):

        action = const.ACTION_RESET_USER_TO_DELIVERY_GROUP
        valid_keys = ['delivery_group_name', 'delivery_group_usernames', "desktop_kind"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['delivery_group_name', 'delivery_group_usernames', "desktop_kind"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def set_delivery_group_mode(self, param):

        action = const.ACTION_SET_DELIVERY_GROUP_MODE
        valid_keys = ['delivery_group_name', "mode"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['delivery_group_name', "mode"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    # computer
    def describe_computers(self, param):

        action = const.ACTION_DESCRIBE_COMPUTERS
        valid_keys = ['catalog_names', 'machine_names', "deliverygroup_names", "offset", "limit"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_computer(self, param):

        action = const.ACTION_CREATE_COMPUTER
        valid_keys = ['catalog_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["catalog_name"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def start_computer(self, param):

        action = const.ACTION_START_COMPUTER
        valid_keys = ['machine_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['machine_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_computer(self, param):

        action = const.ACTION_DELETE_COMPUTER
        valid_keys = ['catalog_name', 'machine_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['catalog_name', 'machine_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def stop_computer(self, param):

        action = const.ACTION_STOP_COMPUTER
        valid_keys = ['machine_name', 'force']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['machine_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)
    
    def restart_computer(self, param):

        action = const.ACTION_RESTART_COMPUTER
        valid_keys = ['machine_name', 'force']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['machine_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def attach_computer_to_user(self, param):

        action = const.ACTION_ATTACH_COMPUTER_TO_USER
        valid_keys = ['user_name', 'machine_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['user_name', 'machine_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def detach_computer_from_user(self, param):

        action = const.ACTION_DETACH_COMPUTER_FROM_USER
        valid_keys = ['user_name', 'machine_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['user_name', 'machine_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def set_computer_mode(self, param):

        action = const.ACTION_SET_COMPUTER_MODE
        valid_keys = ['machine_name', 'desktop_kind', "mode"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['machine_name', 'desktop_kind', "mode"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)
    
    # job
    def describe_jobs(self, param):

        action = const.ACTION_DESCRIBE_JOBS
        valid_keys = ['jobs']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['jobs'],
                                             integer_params=[],
                                             list_params=["jobs"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)
    
    def reload_image(self, param):

        action = const.ACTION_RELOAD_IMAGE
        valid_keys = ['image_id']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['image_id'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def stop_broker_session(self, param):

        action = const.ACTION_STOP_BROKER_SESSION
        valid_keys = ['session_uid']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['session_uid'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def add_computer(self, param):

        action = const.ACTION_ADD_COMPUTER
        valid_keys = ["catalog_name", "machine_name", "machine_sid", "machine_id", "host_unit"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["catalog_name", "machine_name", "machine_sid", "host_unit", "machine_id"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_app_computer(self, param):

        action = const.ACTION_DELETE_APP_COMPUTER
        valid_keys = ["machine_name"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["machine_name"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_app_start_memu(self, param):

        action = const.ACTION_DESCRIBE_APP_STARTMEMU
        valid_keys = ['machine_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['machine_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_broker_apps(self, param):

        action = const.ACTION_DESCRIBE_BROKER_APPS
        valid_keys = ['app_names', "delivery_group_uids", "app_group_uids"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_broker_app(self, param):

        action = const.ACTION_CREATE_BROKER_APP
        valid_keys = ['delivery_group_name', "cmd_exe_path", "cmd_argument", "display_name", "shortcut_path",
                      "folder_full_name", "short_path", "machine_name", "local_exe_flag"]

        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['delivery_group_name', "cmd_exe_path", "cmd_argument", "display_name"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def modify_broker_app(self, param):

        action = const.ACTION_MODIFY_BROKER_APP
        valid_keys = ['app_uid', "normal_display_name", "admin_display_name", "description"]

        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['app_uid'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)
        
        return self.send_request(action, body)

    def add_broker_app(self, param):

        action = const.ACTION_ADD_BROKER_APP
        valid_keys = ["delivery_group_name", "app_name", "app_group_name"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["app_name"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def remove_broker_app(self, param):

        action = const.ACTION_REMOVE_BROKER_APP
        valid_keys = ["app_names", "delivery_group_uid", "app_group_uid"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['app_names'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def new_broker_folder(self, param):

        action = const.ACTION_NEW_BROKER_FOLDER
        valid_keys = ['session_uid']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['session_uid'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def remove_broker_folder(self, param):

        action = const.ACTION_REMOVE_BROKER_FOLDER
        valid_keys = ['session_uid']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['session_uid'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_broker_folder(self, param):

        action = const.ACTION_DESCRIBE_BROKER_FOLDER
        valid_keys = ['session_uid']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['session_uid'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def describe_broker_app_groups(self, param):

        action = const.ACTION_DESCRIBE_BROKER_APP_GROUPS
        valid_keys = ['app_group_names', "delivery_group_uids"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=["app_group_names"]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def add_broker_app_group(self, param):

        action = const.ACTION_ADD_BROKER_APP_GROUP
        valid_keys = ['app_group_name', "delivery_group_name"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['app_group_name', "delivery_group_name"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def create_broker_app_group(self, param):

        action = const.ACTOPN_CREATE_BROKER_APP_GROUP
        valid_keys = ['app_group_name', "description"]
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['app_group_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def delete_broker_app_group(self, param):

        action = const.ACTOPN_DELETE_BROKER_APP_GROUP
        valid_keys = ['app_group_name', 'delivery_group_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['app_group_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def resource_create_citrix_policy(self, param):

        action = const.ACTION_CREATE_CITRIX_POLICY
        valid_keys = ['citrix_policy_name','description','policy_state']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['citrix_policy_name'],
                                             integer_params=["policy_state"],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)

    def resource_config_citrix_policy_item(self, param):

        action = const.ACTION_CONFIG_CITRIX_POLICY_ITEM
        valid_keys = ['citrix_policy_name','policy_items']        
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["citrix_policy_name","policy_items"],
                                             integer_params=[],
                                             list_params=[]   
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)    

    def resource_describe_citrix_policy_items(self, param):
        action = const.ACTION_DESCRIBE_CITRIX_POLICY_ITEM
        valid_keys = ['citrix_policy_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['citrix_policy_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)   


    def resource_delete_citrix_policy(self, param):

        action = const.ACTION_DELETE_CITRIX_POLICY
        valid_keys = ['citrix_policy_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["citrix_policy_name"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)     
    
    def resource_modify_citrix_policy(self, param):

        action = const.ACTION_MODIFY_CITRIX_POLICY
        valid_keys = ['citrix_policy_name','description','policy_state']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["citrix_policy_name"],
                                             integer_params=["policy_state"],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)        

    def resource_rename_citrix_policy(self, param):

        action = const.ACTION_RENAME_CITRIX_POLICY
        valid_keys = ['citrix_policy_old_name','citrix_policy_new_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["citrix_policy_old_name","citrix_policy_new_name"],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)   
     

    def resource_describe_citrix_policies(self, param):

        action = const.ACTION_DESCRIBE_CITRIX_POLICY
        valid_keys = ['citrix_policy_names']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=[],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)        
    
    def resource_set_citrix_policy_priority(self, param):

        action = const.ACTION_SET_CITRIX_POLICY_PRIORITY
        valid_keys = ['citrix_policy_name','policy_priority']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['citrix_policy_name','policy_priority'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)  
       
     

    def resource_add_citrix_policy_filter(self, param):
        action = const.ACTION_ADD_CITRIX_POLICY_FILTER
        valid_keys = ['citrix_policy_name','policy_filters']        
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["citrix_policy_name","policy_filters"],
                                             integer_params=[],
                                             list_params=[]   
                                             ):
            return self.return_param_invaild(action, body)
        return self.send_request(action, body)  

    def resource_modify_citrix_policy_filter(self, param):
        action = const.ACTION_MODIFY_CITRIX_POLICY_FILTER
        valid_keys = ['citrix_policy_name','policy_filters']        
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["citrix_policy_name","policy_filters"],
                                             integer_params=[],
                                             list_params=[]   
                                             ):
            return self.return_param_invaild(action, body)
        return self.send_request(action, body)  

    def resource_describe_citrix_policy_filters(self, param):
        action = const.ACTION_DESCRIBE_CITRIX_POLICY_FILTER
        valid_keys = ['citrix_policy_name']
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=['citrix_policy_name'],
                                             integer_params=[],
                                             list_params=[]
                                             ):
            return self.return_param_invaild(action, body)

        return self.send_request(action, body)   

    def resource_delete_citrix_policy_filter(self, param):
        action = const.ACTION_DELETE_CITRIX_POLICY_FILTER
        valid_keys = ['citrix_policy_name','policy_filters']        
        body = filter_out_none(param, valid_keys)
        if not self.req_checker.check_params(body,
                                             required_params=["citrix_policy_name","policy_filters"],
                                             integer_params=[],
                                             list_params=[]   
                                             ):
            return self.return_param_invaild(action, body)
        return self.send_request(action, body)      
		