'''
Created on 2012-9-17

@author: yunify
'''
import random
import copy
from constants import (
    SYSTEM_LOG_TYPE_SUCCESS,
    SYSTEM_LOG_TYPE_ERROR,
    ACTION_VDI_ADD_SYSTEM_LOG_LIST,
    ACTION_VDI_NOT_ADD_SYSTEM_LOG_WITHOUT_PARAMS_LIST,
    PLATFORM_TYPE_CITRIX, 
    DEFAULT_LANG,
    PLATFORM_TYPE_QINGCLOUD
)
from db.constants import (
    INDEXED_COLUMNS, SEARCH_COLUMNS, SORT_COLUMNS,
    SEARCH_WORD_COLUMN_TABLE, SEARCH_WORD_COLUMN_NAME,
    TIMESTAMP_COLUMNS, RANGE_COLUMNS, NOT_COLUMNS, 
    RESTYPE_DESKTOP_GROUP
)
from db.data_types import SearchType, SearchWordType, TimeStampType, RangeType, NotType
from constants import (
    USER_ROLE_GLOBAL_ADMIN,
    USER_ROLE_CONSOLE_ADMIN,
    USER_ROLE_NORMAL,
    CHANNEL_API,
    CHANNEL_SESSION,
    CHANNEL_INTERNAL,
    USER_CONSOLE_ADMIN,
    GLOBAL_ADMIN_USER_ID,
    GLOBAL_ADMIN_USER_NAME,
    DESKTOP_RULE_SAVE,
    DESKTOP_RULE_NOSAVE
)
import os
from utils.time_stamp import format_utctime
from utils.misc import (
    explode_array,
    is_integer
)
from utils.id_tool import (
    get_resource_type,
    UUID_TYPE_NOT_DEFINED
)
from utils.json import json_dump
from utils.thread_local import get_msg_id, set_msg_id, get_flock_name, set_flock_obj, reset_flock_name
from log.logger import logger
import constants as const
from error.error import Error
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from contextlib import contextmanager
import traceback
from utils.misc import exec_cmd
from utils.net import get_hostname

# ok reply
REP_OK = json_dump({'ret_code' :0})
# ---------------------------------------------
#       Here puts common functions used in API
# ---------------------------------------------

@contextmanager
def transition_status(ctx, tb, keys, status, suppress_warning=False, noop=False):
    if noop:
        yield
        return

    if isinstance(keys, list) or isinstance(keys, set):
        for key in keys:
            ctx.pg.update(tb, key, {'transition_status': status}, suppress_warning=suppress_warning)
    else:
        ctx.pg.update(tb, keys, {'transition_status': status}, suppress_warning=suppress_warning)

    try:
        yield
    except:
        logger.critical("yield exits with exception: %s" % traceback.format_exc())

    if isinstance(keys, list):
        for key in keys:
            ctx.pg.update(tb, key, {'transition_status': ""}, suppress_warning=suppress_warning)
    else:
        ctx.pg.update(tb, keys, {'transition_status': ""}, suppress_warning=suppress_warning)

def format_set_time(items_set):

    ''' strftime for datetime parameters '''
    for _, res in items_set.items():
        for k, v in res.items():
            res[k] = format_utctime(v)
    return items_set

DECIMAL_PRECISION = 4

def is_normal_console(user):
    if user["console_id"] == USER_CONSOLE_ADMIN:
        return False
    return True

def is_admin_console(user):
    if user["console_id"] == USER_CONSOLE_ADMIN:
        return True
    return False

def is_normal_user(user):
    ''' check if user is normal user '''
    if user["role"] in [USER_ROLE_NORMAL]:
        return True
    return False

def is_admin_user(user):
    ''' check if user is admin user '''
    if user["role"] in [USER_ROLE_GLOBAL_ADMIN, USER_ROLE_CONSOLE_ADMIN]:
        return True
    return False

def is_console_admin_user(user):
    ''' check if user is console admin user '''
    if user["role"] in [USER_ROLE_CONSOLE_ADMIN]:
        return True
    return False

def is_global_admin_user(user):
    ''' check if user is global super user '''
    if user["role"] in [USER_ROLE_GLOBAL_ADMIN]:
        return True
    return False

def check_admin_console(user):
    if is_console_admin_user(user) and is_admin_console(user):
        return True
    return False

def check_global_admin_console(user):
    
    if is_global_admin_user(user) and is_admin_console(user):
        return True
    return False

def check_normal_console(user):
    
    if is_normal_user(user) or is_normal_console(user):
        return True
    return False

def is_api_request(sender):
    if sender['channel'] == CHANNEL_API:
        return True
    return False


def is_session_request(sender):
    if sender['channel'] == CHANNEL_SESSION:
        return True
    return False

def build_filter_conditions(req, table, exact_matches=[]):
    sender = req["sender"]
    
    if not is_normal_user(sender) and not is_normal_console(sender):
        if "owner" in req:
            del req["owner"]

    filter_conditions = {}
    for k, v in req.items():
        if table in INDEXED_COLUMNS and k in INDEXED_COLUMNS[table]:
            filter_conditions[k] = v
        # single search column
        if table in SEARCH_COLUMNS and k in SEARCH_COLUMNS[table]:
            if k in exact_matches:
                filter_conditions[k] = v
            else:
                filter_conditions[k] = SearchType(v)
        # search word: combined search
        if k == SEARCH_WORD_COLUMN_NAME and table in SEARCH_WORD_COLUMN_TABLE:
            filter_conditions[k] = SearchWordType(v)
        # timestamp range filter
        if table in TIMESTAMP_COLUMNS and k in TIMESTAMP_COLUMNS[table]:
            filter_conditions[k] = TimeStampType(v)
        # range filter
        if table in RANGE_COLUMNS and k in RANGE_COLUMNS[table]:
            filter_conditions[k] = RangeType(v)
        # not filter
        if table in NOT_COLUMNS and k in NOT_COLUMNS[table]:
            # delete not prefix
            if k.startswith('excluded_'):
                k = k[9:]
            filter_conditions[k] = NotType(v)
    return filter_conditions

def get_sort_key(table, sort_key, default_key='create_time'):
    if table in SORT_COLUMNS and sort_key in SORT_COLUMNS[table]:
        return sort_key
    return default_key


def get_reverse(reverse, default_reverse=True):
    if reverse is None:
        return default_reverse
    return True if reverse else False

def get_resource(ctx, resource_id, is_full=False, cols=None):
    ''' get single resource '''
    rtype = get_resource_type(resource_id, verbose=0)
    if rtype == UUID_TYPE_NOT_DEFINED:
        logger.error("illegal resource type [%s]" % resource_id)
        return None

    tables = get_resource_type_table(rtype)
    tables = tables if isinstance(tables, list) else [tables]
    for table in tables:
        columns = cols if is_full else [
            get_resource_type_id(table), get_resource_type_name(table)]
        resource = ctx.pg.get(table, resource_id, columns)
        if resource is None:
            logger.error("get [%s] failed" % resource_id)
            continue

        if is_full:
            return resource

        return {'resource_id': resource[get_resource_type_id(table)],
                'resource_type': rtype,
                'resource_name': resource[get_resource_type_name(table)]}
    return None

def load_resource_limits(limits_conf):
    ''' load resource limits for each zone from global conf '''
    return load_limits(limits_conf)

def load_limits(limits):
    resource_limits = {}

    for k, v in limits.items():
        if k in ['valid_cpu_cores', 'valid_memory_size', 'valid_instance_classes',
                 'valid_volume_types', 'valid_resource_classes']:
            resource_limits[k] = explode_array(v, is_integer=True)
        elif k in ['disabled_actions', 'disabled_features']:
            resource_limits[k] = explode_array(v)
        elif k in ['valid_cpu_memory_pairs']:
            resource_limits[k] = {}
            for cpu, memorys in v.items():
                resource_limits[k][cpu] = explode_array(
                    memorys, is_integer=True)
        else:
            resource_limits[k] = v

    return resource_limits

def print_resource_limits(resource_limits):
    ''' print resource limits '''
    for zone_id, limits in resource_limits.items():
        limits_str = ""
        for k, v in limits.items():
            limits_str += "\t[%s]: %s\n" % (k, v)
        logger.info("resource limit for zone [%s]:\n%s" % (
            zone_id, limits_str))
    return

def get_super_sender():
    return {'owner': GLOBAL_ADMIN_USER_ID,
            'role': USER_ROLE_GLOBAL_ADMIN,
            'console_id': USER_CONSOLE_ADMIN,
            'channel': CHANNEL_INTERNAL,
            'user_name': GLOBAL_ADMIN_USER_NAME}

def get_resource_type_name(table):
    return "%s_name" % table


def get_resource_type_table(rtype):
    if rtype == RESTYPE_DESKTOP_GROUP:
        return []
    return rtype


def get_resource_type_id(table):
    return INDEXED_COLUMNS[table][0]

def load_json_conf(conf):
    _json = {}
    for k in conf.iterkeys():
        _json[k] = conf[k]

    return _json

def is_readonly_action(action):
    if action.startswith(("Describe", "Get")):
        return True

    return False

# shutting down return code
RETCODE_SHUTTING_DOWN = -99

# shutdown reply
REP_SHUTDOWN = json_dump({'ret_code' : RETCODE_SHUTTING_DOWN})

# throttle control return code
RETCODE_THROTTLE_CONTROL = -100

# throttle control
REP_THROTTLE_CONTROL = json_dump({'ret_code' : RETCODE_THROTTLE_CONTROL})

# error reply
REP_ERROR = json_dump({'ret_code' :-1})

KARG_SPLITER = "|"

KEY_ARG_TIMEOUT = "timeout"

def encode_kargs(*args):
    # must use str to make pure ascii string, otherwise send_unicode error will occur
    first_arg_list = [str(get_msg_id())]
    flock_name = get_flock_name()
    if flock_name:
        first_arg_list.append("%s@%s" % ("#".join(flock_name), get_hostname()))
    kargs_list = [",".join(first_arg_list)]
    for arg in args:
        kargs_list.append(str(arg))
    return KARG_SPLITER.join(kargs_list)

def decode_kargs(info):
    # rebuild kargs
    kargs = {}
    parts = info.split(KARG_SPLITER)
    kargs_len = len(parts)
    if kargs_len > 0:
        _pfirst = parts[0].split(",")
        set_msg_id(_pfirst[0])
        reset_flock_name()
        if len(_pfirst) > 1:
            _pflock = _pfirst[1].split("@")
            set_flock_obj(set(_pflock[0].split("#")), _pflock[1])
    if kargs_len > 1:
        kargs[KEY_ARG_TIMEOUT] = int(parts[1])  
    return kargs      

g_servers = {}
def register_server(url, server):
    global g_servers
    g_servers[url] = server
    
def get_server(url):
    global g_servers
    return g_servers.get(url)

def write_system_log(req, rep, log_type):
    ''' add system operation log '''
    from resource_control.user.system_config import add_system_log

    if 'sender' not in req.keys():
        return None
    if 'owner' not in req['sender'].keys():
        return None
    
    systemlog = {}
    user_id = req['sender']['owner']
    user = req['sender']
    systemlog['user_id'] = user_id
    systemlog['user_name'] = user['user_name']
    systemlog['user_role'] = user['role']
    req.pop('sender')
    if log_type == SYSTEM_LOG_TYPE_SUCCESS:
        systemlog['action_name'] = req.pop('action')
        systemlog['req_time'] = req.pop('expires')
    else:
        systemlog['action_name'] = req['params']['action'] if req.get('params') else req['action']
        systemlog['req_time'] = req['params']['expires'] if req.get('params') else req['expires']
    if systemlog['action_name'] in ACTION_VDI_NOT_ADD_SYSTEM_LOG_WITHOUT_PARAMS_LIST:
        systemlog['req_params'] = ''
    else:
        if log_type == SYSTEM_LOG_TYPE_SUCCESS:
            systemlog['req_params'] = str(req)
        else:
            systemlog['req_params'] = str(req['params'] if req.get('params') else req)
    if isinstance(rep, Error):
        systemlog['log_info'] = Error.get_message()
    else:
        systemlog['log_info'] = str(rep)
    systemlog['log_type'] = log_type
    add_system_log(systemlog)

def return_error(req, error=None, job_id=None, dump=True, **kwargs):
    ''' return error info when request can not be handled or has not been successfully handled
        @param req : original request
        @param error : error information.
        returned message format:
            - ret_code: error code
            - request:  the origin request send by client
    '''

    response = {}
    if job_id:
        response["job_id"] = job_id
    
    for k in kwargs:
        response[k] = kwargs[k]
    if error is None and ("ret_code" not in response or response["ret_code"] == -1):
        error = Error(ErrorCodes.INTERNAL_ERROR)
    if isinstance(error, Error):
        lang = DEFAULT_LANG if req is None or "sender" not in req else req["sender"].get("lang", DEFAULT_LANG)
        response["ret_code"] = error.get_code()
        if isinstance(error.message, str):
            response["message"] = error.message
        else:
            response["message"] = error.get_message(lang)

    # write system log (error)
    if req.get('params') and req.get('params').get('action') and req.get('params').get('action') in ACTION_VDI_ADD_SYSTEM_LOG_LIST:
        write_system_log(copy.deepcopy(req), copy.deepcopy(response), SYSTEM_LOG_TYPE_ERROR)
    if req.get('action') and req.get('action') in ACTION_VDI_ADD_SYSTEM_LOG_LIST:
        write_system_log(copy.deepcopy(req), copy.deepcopy(response), SYSTEM_LOG_TYPE_ERROR)

    if dump:
        return json_dump(response)
    else:
        return response

def return_success(req, rep, job_id=None, dump=True, **kwargs):
    ''' return successful message to client when client is submitting a job
        @params req: origin request, must has "action" key
        @params rep: reply content
        @param job_id: job id if any.
        returned message format:
            - action:   response action name
            - owner:    the access id of the client
            - job_id:   the unique identity of job,
                        for job status tracing in cassandra,
                        also the only info of job in dqueue that submitted to compute bot
            - kwargs:   other args that you want to return to client
    '''
    rep = {} if rep is None else rep
    rep["ret_code"] = 0
    rep["action"] = req["action"] + "Response"
    for k in kwargs:
        rep[k] = kwargs[k]
    
    if job_id:
        rep["job_id"] = job_id

    # write system log (success)
    if req.get('action') and req.get('action') in ACTION_VDI_ADD_SYSTEM_LOG_LIST:
        write_system_log(copy.deepcopy(req), copy.deepcopy(rep), SYSTEM_LOG_TYPE_SUCCESS)
    if dump:
        return json_dump(rep)
    else:
        return rep

def return_items(req, items_set=None, item_type="item", dump=True, **params):
    ''' return item set to client when client is requesting items
        @params req: origin request, must has "action" key
        @params items: the items set, {'item_id': 'item_properties'}
        @params item_type: the type of items, e.g. "image", "instance", "volume"
        returned message format:
            - action:           response action name
            - <item_type>_set:  the items set
    '''
    if items_set is None:
        items_set = {}
    # set content
    response = {}
    response["action"] = req["action"] + "Response"
    response["%s_set" % item_type] = format_set_time(items_set).values()
    response["ret_code"] = 0

    for k, v in params.items():
        response[k] = v

    item_count = len(items_set)
    logger.info("return [%d] matched %ss" % (item_count, item_type))

    if dump:
        return json_dump(response)
    else:
        return response

def is_iaas_error(ret):
   
    if not ret:
        logger.error("iaas error: %s " % ret)
        return True

    if ret["ret_code"] != 0:
        logger.error(ret)
        return True
    return False

def return_iaas_error(ret):
    
    if not ret:
        error_code = ErrorCodes.SERVER_BUSY
        error_msg = ErrorMsg.ERR_CODE_MSG_SERVER_BUSY
        logger.error(error_msg)
        return Error(error_code, error_msg)

    error_code = ret["ret_code"]
    error_msg = ret["message"]
    logger.error(error_msg)
    return Error(error_code, error_msg)

def filter_out_none(dictionary, keys=None):

    ret = {}
    if keys is None:
        keys = []
    for key, value in dictionary.items():
        if value is None or (keys and key not in keys):
            continue
        ret[key] = value

    return ret

# shutting down return code
RETCODE_SHUTTING_DOWN = -99

# shutdown reply
REP_SHUTDOWN = json_dump({'ret_code' : RETCODE_SHUTTING_DOWN})


g_disk_name = []
def generate_disk_name(prefix):
    global g_disk_name
    while True:
        disk_name = "%s-" % prefix
        for _ in range(4):
            disk_name += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012356789')

        if disk_name not in g_disk_name:
            g_disk_name.append(disk_name)
            return disk_name

    return prefix

def get_platform(ctx, zone_id):
    
    zone = ctx.zones.get(zone_id)
    if not zone:
        return PLATFORM_TYPE_QINGCLOUD
    
    return zone.platform

def is_citrix_platform(ctx, zone_id):
    
    zone = ctx.zones.get(zone_id)
    if not zone:
        return False
    
    if zone.platform == PLATFORM_TYPE_CITRIX:
        return True

    return False

def check_citrix_action(ctx, zone_id, resource):
    
    platform = get_platform(ctx, zone_id)
    if platform != PLATFORM_TYPE_CITRIX:
        return False
    
    if not ctx.pass_citrix_pm:
        return True
    
    save_desk = resource.get("save_desk")
    if save_desk == DESKTOP_RULE_SAVE:
        return False

    return True

def check_citrix_random(ctx, zone_id, resource):
    
    platform = get_platform(ctx, zone_id)
    if platform != PLATFORM_TYPE_CITRIX:
        return False

    save_desk = resource.get("save_desk")
    if save_desk != DESKTOP_RULE_NOSAVE:
        return False

    return True

def check_resource_transition_status(resources):

    for res_id, res in resources.items():
        ret = check_single_resource_transition_status(res_id, res)
        if isinstance(ret, Error):
            return ret
    return resources

def check_single_resource_transition_status(resource_id, resource):

    if resource['transition_status']:
        logger.error("resource [%s] is [%s], please try later" % (resource_id, resource['transition_status']))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_IN_TRANSITION_STATUS, (resource_id, resource['transition_status']))
    return resource

def is_search_ip(search_word):
    if not search_word:
        return False
    segments = search_word.split('.')
    if not 2 <= len(segments) <= 4:
        return False
    for s in segments:
        if not is_integer(s) or not 0 <= int(s) <= 255:
            return False
    return True

g_dir_index = 0
def _get_dir_index():

    global g_dir_index
    if g_dir_index > 0:
        return g_dir_index

    index = 0
    for _, dirnames, _ in os.walk(const.STOREFRONT_CONNECT_FILE_DIR):
        break
    
    for item in dirnames:
        if int(item) >= index:
            index = int(item)

    return index

def _get_file_number(path):

    for _, _, filenames in os.walk(path):
        return len(filenames)
    
def _clean_connection_file( file_name, base_path = const.STOREFRONT_CONNECT_FILE_DIR):

    for dirpath, _, filenames in os.walk(base_path):
        if file_name in filenames:
            file_path = os.path.join(dirpath, file_name)
            os.remove(file_path)
    return None

def _rsync_connect_file(ctx,filename,path=None):

    hostname = get_hostname()
    zone_deploy = ctx.zone_deploy
    target_host = None
    num_of_desktop_server = 0

    ret = ctx.pgm.get_desktop_service_managements(service_type=const.LOADBALANCER_SERVICE_TYPE)
    if ret:
        num_of_desktop_server = len(ret)

    if num_of_desktop_server == 2:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_2
    elif num_of_desktop_server == 4:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_4
    elif num_of_desktop_server == 6:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_6
    elif num_of_desktop_server == 8:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_8
    else:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_2

    if zone_deploy == const.DEPLOY_TYPE_STANDARD:
        for target_host in target_host_list:
            os.system('ssh -o StrictHostKeyChecking=no root@%s "mkdir -p %s && chmod -R 777 %s"' % (target_host, path, path))
            cmd = "scp -r %s root@%s:%s" % (filename, target_host, filename)
            logger.info("cmd == %s" % (cmd))
            exec_cmd(cmd)
    else:
        if hostname.endswith(const.DESKTOP_SERVER_HOSTNAME_0):
            target_host = hostname.replace(const.DESKTOP_SERVER_HOSTNAME_0, const.DESKTOP_SERVER_HOSTNAME_1)
            os.system('ssh -o StrictHostKeyChecking=no root@%s "mkdir -p %s && chmod -R 777 %s"' % (target_host, path, path))
            cmd = "scp -r %s root@%s:%s" % (filename, target_host, filename)
            exec_cmd(cmd)
        if hostname.endswith(const.DESKTOP_SERVER_HOSTNAME_1):
            target_host = hostname.replace(const.DESKTOP_SERVER_HOSTNAME_1, const.DESKTOP_SERVER_HOSTNAME_0)
            os.system('ssh -o StrictHostKeyChecking=no root@%s "mkdir -p %s && chmod -R 777 %s"' % (target_host, path, path))
            cmd = "scp -r %s root@%s:%s" % (filename, target_host, filename)
            exec_cmd(cmd)

def check_etc_host(host_ip, host_url):

    cmd = "cat /etc/hosts |grep '%s %s'" %(host_ip,host_url)
    ret = exec_cmd(cmd=cmd)
    (_, output, _) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def set_etc_host(host_ip, host_url):

    if not os.path.exists("/etc/hosts"):
        return False
    
    if not host_ip or not host_url:
        return True

    ret = check_etc_host(host_ip,host_url)
    if ret:
        return True

    host_url = "%s\n" % (host_url)
    url_flag = 0
    contents = ""
    f = open("/etc/hosts", "r")
    lines = f.readlines()
    for line in lines:
        line_list = line.split(" ")
        if host_url in line_list:
            new_url = "%s %s" % (host_ip, host_url)
            contents += new_url
            url_flag = 1
        else:
            contents += line
    
    if not url_flag:
        new_url = "%s %s\n" % (host_ip, host_url)
        contents += new_url
    
    f.close()
    f = open("/etc/hosts", "w")
    f.write(contents)
    f.flush()
    f.close()

    return True

def clear_etc_host(host_url):
    
    if not os.path.exists("/etc/hosts"):
        return False

    host_url = "%s\n" % (host_url)
    contents = ""
    f = open("/etc/hosts", "r")
    lines = f.readlines()
    for line in lines:
        line_list = line.split(" ")
        if host_url in line_list:
            continue
        else:
            contents += line

    f.close()
    f = open("/etc/hosts", "w")
    f.write(contents)
    f.flush()
    f.close()

    return True

def get_target_host_list(ctx):

    num_of_desktop_server = 0
    hostname = get_hostname()
    target_host_list = []

    if const.DEPLOY_TYPE_STANDARD == ctx.zone_deploy:
        ret = ctx.pgm.get_desktop_service_managements(service_type=const.LOADBALANCER_SERVICE_TYPE)
        if ret:
            num_of_desktop_server = len(ret)

        if num_of_desktop_server == 2:
            for host in const.NUM_OF_DESKTOP_SERVER_2:
                if host not in target_host_list:
                    target_host_list.append(host)
        elif num_of_desktop_server == 4:
            for host in const.NUM_OF_DESKTOP_SERVER_4:
                if host not in target_host_list:
                    target_host_list.append(host)
        elif num_of_desktop_server == 6:
            for host in const.NUM_OF_DESKTOP_SERVER_6:
                if host not in target_host_list:
                    target_host_list.append(host)
        elif num_of_desktop_server == 8:
            for host in const.NUM_OF_DESKTOP_SERVER_8:
                if host not in target_host_list:
                    target_host_list.append(host)
        else:
            for host in const.NUM_OF_DESKTOP_SERVER_2:
                if host not in target_host_list:
                    target_host_list.append(host)

    elif const.DEPLOY_TYPE_EXPRESS == ctx.zone_deploy:

        target_host_list.append(hostname)
        if hostname.endswith(const.DESKTOP_SERVER_HOSTNAME_0):
            target_host = hostname.replace(const.DESKTOP_SERVER_HOSTNAME_0, const.DESKTOP_SERVER_HOSTNAME_1)
            target_host_list.append(target_host)

        if hostname.endswith(const.DESKTOP_SERVER_HOSTNAME_1):
            target_host = hostname.replace(const.DESKTOP_SERVER_HOSTNAME_1, const.DESKTOP_SERVER_HOSTNAME_0)
            target_host_list.append(target_host)

    return target_host_list

def unicode_to_string(attrs):
    
    if isinstance(attrs, dict):
        for key, value in attrs.items():
            if isinstance(value, unicode):
                attrs[key] = str(value).decode("string_escape").encode("utf-8")
            elif isinstance(value, dict):
                unicode_to_string(value)
            elif isinstance(value, list):
                value = unicode_to_string(value)
                attrs[key] = value
        
        return attrs
                
    elif isinstance(attrs, list):
        new_values = []
        for value in attrs:
            if isinstance(value, unicode):
                value = str(value).decode("string_escape").encode("utf-8")
            
            if isinstance(value, dict):
                unicode_to_string(value)

            new_values.append(value)
        
        return new_values
    elif isinstance(attrs, unicode):
        return str(attrs).decode("string_escape").encode("utf-8")
    
    return attrs

def dict_key_to_lower(attrs):
    
    new_attrs = {}
    if isinstance(attrs, dict):
        for key, value in attrs.items():
            
            new_attrs[key.lower()] = value
    
    return new_attrs
            
    