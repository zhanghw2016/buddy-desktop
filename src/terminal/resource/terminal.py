'''
Created on 2018-5-16

@author: yunify
'''

from db.constants import TB_DESKTOP,TB_TERMINAL_MANAGEMENT
from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
from utils.id_tool import(
    UUID_TYPE_TERMINAL
)
import constants as const
from utils.id_tool import(
    get_uuid
)
import time
from utils.misc import get_current_time,exec_cmd
import api.user.user as APIUser
import os

from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
)

from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    PUBLIC_COLUMNS
)

def get_terminal_id(terminal_mac):

    ctx = context.instance()
    terminal_id = None
    ret = ctx.pgm.get_terminals(terminal_mac=terminal_mac)

    if ret is None:
        logger.info("get_terminal_ids fail %s" % (terminal_mac))
        return None
    terminals = ret
    terminal_id = terminals.keys()[0]

    return terminal_id

def get_terminal_mac(terminal_id):
    ''' get terminal_mac by terminal_id '''
    ctx = context.instance()
    columns = ["terminal_mac"]
    # get terminal_mac from db
    try:
        result = ctx.pg.get(TB_TERMINAL_MANAGEMENT,
                            terminal_id,
                            columns)
        if not result:
            logger.error("get terminal id [%s] terminal_mac failed" % terminal_id)
            return None
    except Exception,e:
        logger.error("get desktop hostname with Exception:%s" % e)
        return None

    return result['terminal_mac']

def get_desktop_hostname(desktop_id):

    ctx = context.instance()
    columns = ["hostname"]
    # get hostname from db
    try:
        result = ctx.pg.get(TB_DESKTOP,
                            desktop_id,
                            columns)
        if not result:
            logger.error("get desktop id [%s] hostname failed" % desktop_id)
            return None
    except Exception,e:
        logger.error("get desktop hostname with Exception:%s" % e)
        return None

    return result['hostname']

def create_terminal_management(sender,req):

    ctx = context.instance()
    terminal_serial_number = req.get("terminal_serial_number","")
    status = req.get("status","")
    login_user_name = req.get("login_user_name","")
    terminal_ip = req.get("terminal_ip","")
    terminal_mac = req.get("terminal_mac","")
    terminal_type = req.get("terminal_type",'')
    terminal_version_number = req.get("terminal_version_number","")
    login_hostname = req.get("login_hostname","")
    terminal_server_ip = req.get("terminal_server_ip", "")

    terminals = ctx.pgm.get_terminals(terminal_mac=terminal_mac)
    if terminals is None or len(terminals) == 0:
        terminal_id = get_uuid(UUID_TYPE_TERMINAL, ctx.checker)
        update_info = dict(
            terminal_id=terminal_id,
            terminal_serial_number=terminal_serial_number,
            status=status,
            terminal_ip=terminal_ip,
            terminal_mac=terminal_mac,
            terminal_type=terminal_type,
            terminal_version_number=terminal_version_number,
            login_hostname=login_hostname,
            create_time=get_current_time(),
            zone_id=sender["zone"],
            terminal_server_ip=terminal_server_ip
        )

        if not ctx.pg.insert(dbconst.TB_TERMINAL_MANAGEMENT, update_info):
            logger.error("insert newly created terminal management for [%s] to db failed" % (update_info))
            return Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_TERMINAL_REGISTER_FAILED,terminal_mac)
    else:
        for terminal_id,terminal in terminals.items():
            condition = {"terminal_id": terminal_id}
            if login_user_name:
                update_info = dict(
                    terminal_serial_number=terminal_serial_number,
                    status=status,
                    terminal_ip=terminal_ip,
                    terminal_mac=terminal_mac,
                    terminal_type=terminal_type,
                    terminal_version_number=terminal_version_number,
                    login_hostname=login_hostname,
                    login_user_name=login_user_name,
                    create_time=get_current_time(),
                    terminal_server_ip=terminal_server_ip
                )
            else:
                update_info = dict(
                    terminal_serial_number=terminal_serial_number,
                    status=status,
                    terminal_ip=terminal_ip,
                    terminal_mac=terminal_mac,
                    terminal_type=terminal_type,
                    terminal_version_number=terminal_version_number,
                    login_hostname=login_hostname,
                    create_time=get_current_time(),
                    terminal_server_ip=terminal_server_ip
                )

            if not ctx.pg.base_update(dbconst.TB_TERMINAL_MANAGEMENT, condition, update_info):
                logger.error("update terminal management for [%s] to db failed" % (update_info))
                return Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return terminal_id

def update_terminal_management_status(sender,terminal_mac,status = const.TERMINAL_STATUS_ACTIVE):

    ctx = context.instance()
    ret = ctx.pgm.get_terminal_id(terminal_mac=terminal_mac)
    if ret is None:
        logger.info("get_terminal_id fail %s" % (terminal_mac))
        return None
    terminal_id = ret

    condition = {"terminal_id": terminal_id}
    update_info = dict(
        status=status
    )

    if not ctx.pg.base_update(dbconst.TB_TERMINAL_MANAGEMENT, condition, update_info):
        logger.error("update terminal management for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

def update_terminal_management_connection_status(sender, terminal_mac, status=const.TERMINAL_STATUS_ACTIVE,hostname=None,login_user_name=None):

    ctx = context.instance()
    ret = ctx.pgm.get_terminal_id(terminal_mac=terminal_mac)

    if ret is None:
        logger.info("get_terminal_id fail %s" % (terminal_mac))
        return None
    terminal_id = ret

    condition = {"terminal_id": terminal_id}
    update_info = dict(
        status=status,
        login_hostname=hostname if hostname else '',
        login_user_name=login_user_name,
        connection_disconnection_time=get_current_time()
    )

    if not ctx.pg.base_update(dbconst.TB_TERMINAL_MANAGEMENT, condition, update_info):
        logger.error("update terminal management for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

