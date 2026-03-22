from log.logger import logger
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
import constants as const
import db.constants as dbconst
import context
from utils.misc import get_current_time
from send_request import push_topic_event,send_desktop_server_request
from utils.json import json_dump
import resource_control.guest.file_share as File_Share
import resource_control.guest.guest as Guest
from utils.id_tool import(
    get_uuid,
    UUID_TYPE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY,
)
import random


def _get_desktop_id(hostname):
    ''' get desktop id by hostname '''
    ctx = context.instance()
    desktops_set = ctx.pgm.get_desktops(hostname=hostname)
    if desktops_set is None or len(desktops_set) == 0:
        return None

    desktop_id = desktops_set.keys()[0]
    return desktop_id

def _get_desktop_hostname(desktop_id):
    ''' get desktop hostname by desktop_id '''
    ctx = context.instance()  
    columns = ["hostname"]
    # get hostname from db
    try:
        result = ctx.pg.get(dbconst.TB_DESKTOP, 
                            desktop_id, 
                            columns)
        if not result:
            logger.error("get desktop id [%s] hostname failed" % desktop_id)
            return None
    except Exception,e:
        logger.error("get desktop hostname with Exception:%s" % e)
        return None

    return result['hostname']

def _get_desktop_dn(desktop_id):
    ''' get desktop dn in domain by desktop_id '''
    ctx = context.instance()
    columns = ["desktop_dn", "in_domain"]
    # get owner from db
    try:
        result = ctx.pg.get(dbconst.TB_DESKTOP,
                            desktop_id,
                            columns)
        if not result or len(result) == 0:
            logger.error("get desktop_dn by desktop_id:[%s] failed" % desktop_id)
            return None
        if result["in_domain"] != 1 or result["desktop_dn"] is None or len(result["desktop_dn"]) == 0:
            logger.error("get desktop_dn error, [%s]" % result)
            return None
    except Exception,e:
        logger.error("get desktop desktop_dn with Exception:%s" % e)
        return None

    return result["desktop_dn"]

def _describe_guest(desktop_id):
    ''' get guest info by desktop_id '''
    ctx = context.instance()

    try:
        result = ctx.pg.get(dbconst.TB_GUEST,
                            desktop_id)
        if not result or len(result) == 0:
            return None
        return result
    except Exception,e:
        logger.error("describe guest with Exception:%s" % e)
        return None

def _update_guest(desktop_id, hostname, conditions):
    ''' update guest by desktop_id and hostname'''
    ctx = context.instance()
    # get owner from db
    try:
        if _describe_guest(desktop_id) is None:
            conditions.update({"desktop_id": desktop_id})
            conditions.update({"hostname": hostname})
            result = ctx.pg.insert(dbconst.TB_GUEST, conditions)
            if result is None:
                return False

        result = ctx.pg.update(dbconst.TB_GUEST,
                               desktop_id,
                               conditions)
        if not result:
            logger.error("update guest by desktop_id:[%s] failed" % desktop_id)
            return False
        return True
    except Exception,e:
        logger.error("pdate guest with Exception:%s" % e)
        return True


def _get_desktop_owner(desktop_id):
    ''' get desktop owner by desktop_id '''
    ctx = context.instance()  
    columns = ["owner"]
    # get owner from db
    try:
        result = ctx.pg.get(dbconst.TB_DESKTOP, 
                            desktop_id, 
                            columns)
        if not result or len(result) == 0:
            logger.error("get owner id [%s] hostname failed" % desktop_id)
            return None
    except Exception,e:
        logger.error("get desktop owner with Exception:%s" % e)
        return None

    return result['owner']

def _get_desktop_group_type(desktop_id):
    ''' get desktop group type by desktop_id '''
    ctx = context.instance()
    columns = ["desktop_group_type"]
    # get owner from db
    try:
        result = ctx.pg.get(dbconst.TB_DESKTOP,
                            desktop_id,
                            columns)
        if not result or len(result) == 0:
            logger.error("get group_type by desktop_id:[%s] failed" % desktop_id)
            return None
    except Exception,e:
        logger.error("get desktop group_type with Exception:%s" % e)
        return None

    return result['desktop_group_type']

def _get_desktop_zone(desktop_id):
    ''' get desktop zone by desktop_id '''
    ctx = context.instance()  
    columns = ["zone"]
    # get owner from db
    try:
        result = ctx.pg.get(dbconst.TB_DESKTOP, 
                            desktop_id, 
                            columns)
        if not result or len(result) == 0:
            logger.error("get zone by desktop_id:[%s] failed failed" % desktop_id)
            return None
    except Exception,e:
        logger.error("get desktop zone with Exception:%s" % e)
        return None

    return result['zone']


def handle_register(req):

    hostname = req.get("hostname", "")
    if len(hostname) == 0:
        logger.error("hostname is empty.")
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                    ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "hostname", hostname)

    rep = {}
    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        # first register
        desktop_id = _get_desktop_id(hostname)
        if desktop_id is None:
            return Error(ErrorCodes.VDHOST_NOT_FOUND,
                        ErrorMsg.ERR_MSG_VDHOST_HOSTNAME_NOT_FOUND_ERROR, hostname)
        rep["desktop_id"] = desktop_id
    else:
        rep["desktop_id"] = desktop_id

    return rep

def handle_spice_connected(req):
    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    hostname = _get_desktop_hostname(desktop_id)
    if not hostname:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # update spice connect info
    conditions = {
        "login_user": req.get("login_user", ""),
        "client_ip": req.get("client_ip", ""),
        "connect_status": 1,
        "connect_time": get_current_time()
    }
    _update_guest(desktop_id, hostname, conditions)

    rep = {"desktop_id": desktop_id}
    return rep


def handle_spice_disconnected(req):
    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    hostname = _get_desktop_hostname(desktop_id)
    if not hostname:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # update spice connect info
    conditions = {
        "client_ip": "",
        "connect_status": 0,
        "disconnect_time": get_current_time()
    }
    _update_guest(desktop_id, hostname, conditions)

    rep = {"desktop_id": desktop_id}
    return rep

def handle_qdp_connected(req):
    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    hostname = _get_desktop_hostname(desktop_id)
    if not hostname:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # update spice connect info
    conditions = {
        "login_user": req.get("login_user", ""),
        "client_ip": req.get("client_ip", ""),
        "connect_status": 1,
        "connect_time": get_current_time()
    }
    _update_guest(desktop_id, hostname, conditions)

    rep = {"desktop_id": desktop_id}
    return rep


def handle_qdp_disconnected(req):
    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    hostname = _get_desktop_hostname(desktop_id)
    if not hostname:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # update spice connect info
    conditions = {
        "client_ip": "",
        "connect_status": 0,
        "disconnect_time": get_current_time()
    }
    _update_guest(desktop_id, hostname, conditions)

    rep = {"desktop_id": desktop_id}
    return rep

def handle_guest_system_logout(req):
    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    hostname = _get_desktop_hostname(desktop_id)
    if not hostname:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # update spice connect info
    conditions = {
        "login_user": ""
    }
    _update_guest(desktop_id, hostname, conditions)
    
    rep = {"desktop_id": desktop_id}
    return rep

def handle_guest_system_restart(req):
    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    hostname = _get_desktop_hostname(desktop_id)
    if not hostname:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # if desktop type is [static/random], send ACTION to desktop_server
    desktop_type = _get_desktop_group_type(desktop_id)
    if desktop_type in [const.DG_TYPE_STATIC, const.DG_TYPE_RANDOM, const.DG_TYPE_PERSONAL]:
        zone = _get_desktop_zone(desktop_id)
        desktop_req = {"type":"internal",
                       "params":{
                           "action": const.ACTION_VDI_RESTART_DESKTOPS,
                           "desktops": [desktop_id],
                           "zone": zone
                           },
                }
        desktop_rep = send_desktop_server_request(desktop_req)
        if desktop_rep.get("ret_code", -1) != 0:
            logger.error("send desktop server request [%s] fail" % req)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CAN_NOT_HANDLE_REQUEST)

    rep = {"desktop_id": desktop_id}
    return rep

def handle_guest_system_shutdown(req):
    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    hostname = _get_desktop_hostname(desktop_id)
    if not hostname:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # if desktop type is [static/random], send ACTION to desktop_server
    desktop_type = _get_desktop_group_type(desktop_id)
    if desktop_type in [const.DG_TYPE_STATIC, const.DG_TYPE_RANDOM, const.DG_TYPE_PERSONAL]:
        zone = _get_desktop_zone(desktop_id)
        desktop_req = {"type":"internal",
                       "params":{
                           "action": const.ACTION_VDI_STOP_DESKTOPS,
                           "desktops": [desktop_id],
                           "zone": zone
                           },
                }
        desktop_rep = send_desktop_server_request(desktop_req)
        if desktop_rep.get("ret_code", -1) != 0:
            logger.error("send desktop server request [%s] fail" % req)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CAN_NOT_HANDLE_REQUEST)

    rep = {"desktop_id": desktop_id}
    return rep

def handle_guest_system_upgrade(req):
    ctx = context.instance()
    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    hostname = _get_desktop_hostname(desktop_id)
    if not hostname:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # check qingcloud_guest_tools_version
    rep = {}
    vm_qingcloud_guest_tools_version = req.get("vm_qingcloud_guest_tools_version","2.0.0-0")
    component_versions = ctx.pgm.get_component_versions(component_ids=const.DEFAULT_QINGCLOUD_GUEST_TOOLS_COMPONENT_ID)
    if component_versions:
        for _,component_version in component_versions.items():
            server_qingcloud_guest_tools_version = component_version["version"]
            server_qingcloud_guest_tools_filename = component_version["filename"]
            ret = cmp(server_qingcloud_guest_tools_version, vm_qingcloud_guest_tools_version)
            if ret > 0:
                rep["qingcloud_guest_tools_need_upgrade"] = 1
                rep["qingcloud_guest_tools_download_url"] = "/mnt/nasdata/%s" %(server_qingcloud_guest_tools_filename)
            else:
                rep["qingcloud_guest_tools_need_upgrade"] = 0

    rep["desktop_id"] = desktop_id
    return rep

def handle_get_file_share_groups(req):

    ctx = context.instance()
    sender = req.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "sender", str(sender))

    json_request = req.get("json_request")
    desktop_id = json_request.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # get zone
    zone = _get_desktop_zone(desktop_id)

    # get user_name
    username = json_request.get("username",'')
    username_list = username.split("\\")
    user_name = username_list[1]
    logger.info("user_name == %s" % (user_name))

    # get user_id
    if user_name == 'redirector' or user_name == 'Administrator':
        user_id = user_name
    else:
        zone_user_set = ctx.pgm.get_zone_user(zone_id=zone,user_name=user_name)
        if zone_user_set is None or len(zone_user_set) == 0:
            return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("user_name", user_name))
        user_id = zone_user_set.get("user_id")

    # get flag_id
    flag_id = json_request.get("flag_id",random.randint(1,65535))
    logger.info("flag_id == %s" % (flag_id))

    # build sender
    sender["zone"] = zone
    sender["user_name"] = user_name
    sender["owner"] = user_id
    sender["role"] = "normal"
    sender["flag_id"] = flag_id

    json_request["sender"] = sender

    file_share_group_set = File_Share.get_file_share_groups_info(sender, json_request)

    return file_share_group_set

def handle_get_file_share_files(req):

    ctx = context.instance()
    sender = req.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "sender", str(sender))

    json_request = req.get("json_request")
    desktop_id = json_request.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # get zone
    zone = _get_desktop_zone(desktop_id)

    # get user_name
    username = json_request.get("username",'')
    username_list = username.split("\\")
    user_name = username_list[1]

    # get user_id
    if user_name == 'redirector' or user_name == 'Administrator':
        user_id = user_name
    else:
        zone_user_set = ctx.pgm.get_zone_user(zone_id=zone,user_name=user_name)
        if zone_user_set is None or len(zone_user_set) == 0:
            return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("user_name", user_name))
        user_id = zone_user_set.get("user_id")

    # get flag_id
    flag_id = json_request.get("flag_id",random.randint(1,65535))
    logger.info("flag_id == %s" % (flag_id))

    # build sender
    sender["zone"] = zone
    sender["user_name"] = user_name
    sender["owner"] = user_id
    sender["role"] = "normal"
    sender["flag_id"] = flag_id

    json_request["sender"] = sender

    # get_file_share_group_files
    file_share_group_file_set = File_Share.get_file_share_group_files_info(sender, json_request)

    return file_share_group_file_set

def register_download_file_share_group_file_history(sender, json_request):

    ctx = context.instance()
    file_share_group_file_ids = json_request.get("file_share_group_files")
    if file_share_group_file_ids and not isinstance(file_share_group_file_ids,list):
        file_share_group_file_ids = [file_share_group_file_ids]
    logger.info("file_share_group_file_ids == %s" %(file_share_group_file_ids))
    user_name = sender["user_name"]
    user_id = sender["owner"]

    file_download_history_ids = []
    for file_share_group_file_id in file_share_group_file_ids:
        file_download_history_id = get_uuid(UUID_TYPE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, ctx.checker)
        file_download_history_info = dict(
                                file_download_history_id=file_download_history_id,
                                file_share_group_file_id=file_share_group_file_id,
                                user_id=user_id if user_id else 'Administrator',
                                user_name=user_name,
                                create_time=get_current_time(),
                                update_time=get_current_time()
                                )
        logger.info("file_download_history_info == %s" %(file_download_history_info))
        if not ctx.pg.batch_insert(dbconst.TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY, {file_download_history_id: file_download_history_info}):
            logger.error("insert newly created file_share_group_file_download_history [%s] to db failed" % (file_download_history_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

        if file_download_history_id not in file_download_history_ids:
            file_download_history_ids.append(file_download_history_id)

    return file_download_history_ids

def handle_download_file_share_files(req):

    ctx = context.instance()
    sender = req.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "sender", str(sender))

    json_request = req.get("json_request")
    desktop_id = json_request.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # get zone
    zone = _get_desktop_zone(desktop_id)

    # get user_name
    username = json_request.get("username", '')
    username_list = username.split("\\")
    user_name = username_list[1]

    # get user_id
    if user_name == 'redirector' or user_name == 'Administrator':
        user_id = user_name
    else:
        zone_user_set = ctx.pgm.get_zone_user(zone_id=zone, user_name=user_name)
        if zone_user_set is None or len(zone_user_set) == 0:
            return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("user_name", user_name))
        user_id = zone_user_set.get("user_id")

    # build sender
    sender["zone"] = zone
    sender["user_name"] = user_name
    sender["owner"] = user_id

    json_request["sender"] = sender

    ret = register_download_file_share_group_file_history(sender, json_request)

    rep = {}

    return rep

def handle_get_file_share_tools_component_version(req):

    ctx = context.instance()
    sender = req.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "sender", str(sender))

    json_request = req.get("json_request")
    desktop_id = json_request.get("desktop_id", "")
    if len(desktop_id) == 0:
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id))

    # get zone
    zone = _get_desktop_zone(desktop_id)

    # get user_name
    username = json_request.get("username", '')
    username_list = username.split("\\")
    user_name = username_list[1]

    # get user_id
    if user_name == 'redirector' or user_name == 'Administrator':
        user_id = user_name
    else:
        zone_user_set = ctx.pgm.get_zone_user(zone_id=zone, user_name=user_name)
        if zone_user_set is None or len(zone_user_set) == 0:
            return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("user_name", user_name))
        user_id = zone_user_set.get("user_id")

    # build sender
    sender["zone"] = zone
    sender["user_name"] = user_name
    sender["owner"] = user_id

    json_request["sender"] = sender

    # get_file_share_tools_component_version_info
    file_share_tools_component_version_set = File_Share.get_file_share_tools_component_version_info(sender, json_request)

    return file_share_tools_component_version_set


