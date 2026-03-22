'''
Created on 2017-10-17

@author: yunify
'''
import requests
import context
from db.constants import (
    TB_VDI_DESKTOP_MESSAGE,
    TB_GUEST
    )
from utils.misc import get_current_time
from utils.net import is_port_open
from utils.id_tool import UUID_TYPE_VDI_DESKTOP_MESSAGE, UUID_TYPE_VDHOST_REQUEST, get_uuid
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from log.logger import logger
from utils.json import json_dump, json_load
import constants as const


VDHOST_SERVER_API_URL = "http://%s:9780/api"

def _check_private_ips(desktop_ips):
    active_ips = []
    for desktop_ip in desktop_ips:
        ret = is_port_open(desktop_ip, const.VDHOST_SERVER_DEFAULT_PORT)
        if ret:
            active_ips.append(desktop_ip)
    if len(active_ips) == 0:
        return None
    return active_ips

def check_vdhost_server_status(desktop_id):
    ctx = context.instance()
    ips = [] 
    nics = ctx.pgm.get_nics(desktop_ids = [desktop_id])
    if not nics:
        logger.error("desktop [%s] have no nics.")
        return None
    for _,nic in nics.items():
        ips.append(nic["private_ip"])

    active_ips = _check_private_ips(ips)
    if active_ips is None:
        logger.error("active_ips size is 0.")
        return None;

    for vdhost_server in active_ips:
        url = VDHOST_SERVER_API_URL % vdhost_server
        req = {
            "action": const.REQUEST_VDHOST_SERVER_STATUS
            }
        rep = requests.post(url, data=json_dump(req))
        if rep is None:
            logger.error("vdhost server request error.")
            return None
        return json_load(rep.text)

    return None

def create_desktop_message(message):
    ''' send desktop message '''
    ctx = context.instance()

    try:
        # create desktop message
        curtime = get_current_time(to_seconds=False)
        message_id = get_uuid(UUID_TYPE_VDI_DESKTOP_MESSAGE, 
                              ctx.checker, 
                              long_format=True)

        message["create_time"] = curtime
        message['message_id'] = message_id
        if not ctx.pg.insert(TB_VDI_DESKTOP_MESSAGE, message):
            logger.error("create desktop message [%s] failed." % (message_id))
            return Error(ErrorCodes.SEND_GUEST_MESSAGE_ERROR,
                         ErrorMsg.ERR_MSG_SEND_GUEST_MESSAGE_ERROR)

        return message_id
    except Exception, e:
        logger.error("insert desktop message with Exception:%s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION, 
                     ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def describe_guest_connection_info(desktop_id):
    ''' get desktop spice connection info '''
    ctx = context.instance()
    spice_info = ctx.pg.get(TB_GUEST, desktop_id)
    if spice_info is None:
        return {}

    return spice_info

def delete_guest_connection_info(desktop_ids):
    ''' get desktop spice connection info '''
    ctx = context.instance()
    ret = ctx.pg.base_delete(TB_GUEST, {"desktop_id": desktop_ids})
    if ret < 0:
        return -1

    return 0

def get_spice_connection_number():
    ''' get desktop spice connection number '''
    ctx = context.instance()
    conn_number = ctx.pg.get_count(TB_GUEST, {"connect_status": 1})
    if conn_number is None:
        return 0

    return conn_number

def modify_guest_connect_info(desktop_id, hostname, conditions):
    ''' update guest by desktop_id and hostname'''
    ctx = context.instance()
    curtime = get_current_time(to_seconds=False)
    # get owner from db
    try:
        guest = ctx.pg.base_get(TB_GUEST,{"hostname": hostname})
        if not guest:
            conditions.update({"hostname": hostname})
            if desktop_id:
                conditions.update({"desktop_id": desktop_id})
            conditions.update({"connect_status": 0})
            conditions.update({"connect_time": curtime})
            conditions.update({"disconnect_time": curtime})
            result = ctx.pg.base_insert(TB_GUEST, conditions)
            if result < 0:
                return False
            return True

        result = ctx.pg.base_update(TB_GUEST,
                                    {"hostname": hostname},
                                    conditions)
        if result<0:
            logger.error("update guest by desktop_id:[%s] failed" % desktop_id)
            return False
        return True
    except Exception,e:
        logger.error("udate guest with Exception:%s" % e)
        return True
