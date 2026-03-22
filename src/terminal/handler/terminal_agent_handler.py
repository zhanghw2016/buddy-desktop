'''
Created on 2018-5-15

@author: yunify
'''
import context
import error.error_msg as ErrorMsg
import error.error_code as ErrorCodes
from error.error import Error
from common import return_error, return_success, return_items
from log.logger import logger
from utils.json import json_dump
from base_client import ReqLetter
from utils.misc import get_current_time
from resource.desktop import get_desktop_hostname
from resource.guest import update_guest
from resource.user import get_user_source
import resource.terminal as Terminal
from send_request import push_topic_event
import constants as const

def handle_ping(req):
    sender = req.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "sender", str(sender)))

    terminal_mac = sender.get("terminal_mac", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "terminal_mac", terminal_mac))

    rep = {"terminal_mac": terminal_mac}
    return return_success(req, rep)

def handle_register(req):
 
    ctx = context.instance()
    sender = req.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "sender", str(sender)))

    terminal_mac = sender.get("terminal_mac", "")
    role = req.get("role", "")

    rep = {}
    terminal_id = req.get("terminal_id", "")
    if len(terminal_id) == 0:
        # first register
        # register terminal info
        ret = Terminal.create_terminal_management(sender, req)
        if isinstance(ret, Error):
            return return_error(req, ret)
        terminal_id = ret

        rep["terminal_id"] = terminal_id
        rep["saved"] = 1
    else:
        # have registered
        rep["terminal_id"] = terminal_id
        rep["saved"] = 0

    rep["role"] = role

    ctx.terminals.update({terminal_mac: sender})

    return return_success(req, rep)

def handle_unregister(req):
    ctx = context.instance()
    sender = req.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "sender", str(sender)))

    terminal_mac = sender.get("terminal_mac", "")
    role = req.get("role", "")

    # register terminal info
    ret = Terminal.create_terminal_management(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    terminal_id = ret

    ctx.terminals.pop(terminal_mac)

    rep = {}
    rep["terminal_id"] = terminal_id
    rep["role"] = role

    return return_success(req, rep)

def handle_modify_terminal_response(rep):
    sender = rep.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return -1

    terminal_mac = sender.get("terminal_mac", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return -1

    request_id = rep.get("request_id", "")
    if len(request_id) == 0:
        logger.error("request_id is empty.")
        return -1

    result = {}
    ret_code = rep.get("ret_code", -1)
    if ret_code < 0:
        logger.error("ret_code is -1.")
        return -1
    elif ret_code > 0:
        msg = rep.get("msg", "")
        result["msg"] = msg
    result["ret_code"] = ret_code
    ctx = context.instance()
    ctx.terminal_request.update({request_id: result})

    # update terminal info
    ret = Terminal.update_terminal_management_status(sender,terminal_mac,status = const.TERMINAL_STATUS_INACTIVE)
    if isinstance(ret, Error):
        return return_error(rep, ret)

    return 0

def handle_restart_terminal_response(rep):
    sender = rep.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return -1

    terminal_mac = sender.get("terminal_mac", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return -1

    request_id = rep.get("request_id", "")
    if len(request_id) == 0:
        logger.error("request_id is empty.")
        return -1

    result = {}
    ret_code = rep.get("ret_code", -1)
    if ret_code < 0:
        logger.error("ret_code is -1.")
        return -1
    elif ret_code > 0:
        msg = rep.get("msg", "")
        result["msg"] = msg
    result["ret_code"] = ret_code
    ctx = context.instance()
    ctx.terminal_request.update({request_id: result})

    # update terminal info
    ret = Terminal.update_terminal_management_status(sender, terminal_mac, status=const.TERMINAL_STATUS_INACTIVE)
    if isinstance(ret, Error):
        return return_error(rep, ret)

    return 0

def handle_stop_terminal_response(rep):
    sender = rep.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return -1

    terminal_mac = sender.get("terminal_mac", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return -1

    request_id = rep.get("request_id", "")
    if len(request_id) == 0:
        logger.error("request_id is empty.")
        return -1

    result = {}
    ret_code = rep.get("ret_code", -1)
    if ret_code < 0:
        logger.error("ret_code is -1.")
        return -1
    elif ret_code > 0:
        msg = rep.get("msg", "")
        result["msg"] = msg
    result["ret_code"] = ret_code
    ctx = context.instance()
    ctx.terminal_request.update({request_id: result})

    # update terminal info
    ret = Terminal.update_terminal_management_status(sender, terminal_mac, status=const.TERMINAL_STATUS_INACTIVE)
    if isinstance(ret, Error):
        return return_error(rep, ret)

    return 0

def handle_online_upgrade_terminal_response(rep):

    sender = rep.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return -1

    terminal_mac = sender.get("terminal_mac", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return -1

    request_id = rep.get("request_id", "")
    if len(request_id) == 0:
        logger.error("request_id is empty.")
        return -1

    result = {}
    ret_code = rep.get("ret_code", -1)
    if ret_code < 0:
        logger.error("ret_code is -1.")
        return -1
    elif ret_code > 0:
        msg = rep.get("msg", "")
        result["msg"] = msg
    result["ret_code"] = ret_code
    ctx = context.instance()
    ctx.terminal_request.update({request_id: result})

    return 0

def handle_spice_connected(req):
    sender = req.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "sender", str(sender)))

    terminal_mac = sender.get("terminal_mac", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("terminal_mac", terminal_mac)))

    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id)))

    login_user_name = req.get("login_user_name", "")
    if len(login_user_name) == 0:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("login_user_name", login_user_name)))

    hostname = Terminal.get_desktop_hostname(desktop_id)
    if hostname is None:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id)))

    # update terminal info
    ret = Terminal.update_terminal_management_connection_status(sender, terminal_mac=terminal_mac,status=const.TERMINAL_STATUS_ACTIVE,hostname=hostname,login_user_name=login_user_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    rep = {"hostname": hostname}
    return return_success(req, rep)

def handle_spice_disconnected(req):
    sender = req.get("sender")
    if sender is None or len(sender) == 0:
        logger.error("sender is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "sender", str(sender)))

    terminal_mac = sender.get("terminal_mac", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("terminal_mac", terminal_mac)))

    desktop_id = req.get("desktop_id", "")
    if len(desktop_id) == 0:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id)))

    login_user_name = req.get("login_user_name", "")
    if len(login_user_name) == 0:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("login_user_name", login_user_name)))

    hostname = Terminal.get_desktop_hostname(desktop_id)
    if hostname is None:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, ("desktop_id", desktop_id)))

    # update terminal info
    ret = Terminal.update_terminal_management_connection_status(sender, terminal_mac=terminal_mac,status=const.TERMINAL_STATUS_ACTIVE,hostname=None,login_user_name=login_user_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    rep = {"hostname": hostname}
    return return_success(req, rep)

