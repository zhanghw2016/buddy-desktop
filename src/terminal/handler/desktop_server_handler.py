'''
Created on 2019-09-26

@author: yunify
'''
import error.error_msg as ErrorMsg
import error.error_code as ErrorCodes
from error.error import Error
from common import return_error, return_success
from log.logger import logger
from utils.json import json_dump
from utils.id_tool import  get_uuid,UUID_TYPE_TERMINAL_REQUEST
from base_client import ReqLetter
import context
import constants as const
from response.response_handler import wait_terminal_response

def handle_modify_terminal_attributes(req):

    ctx = context.instance()
    terminal_mac = req.get("terminal_mac", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "terminal_mac", terminal_mac))

    terminal_server_ip = req.get("terminal_server_ip", "")

    server = ctx.terminals.get(terminal_mac, {}).get("server", None)
    sock = ctx.terminals.get(terminal_mac, {}).get("sock", None)

    if server is None or sock is None:
        logger.error("can't find terminal [%s] connected." % terminal_mac)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_NOT_CONNECT_ERROR, terminal_mac))

    request_id = get_uuid(UUID_TYPE_TERMINAL_REQUEST,
                          None,
                          long_format=True)

    request = {
        "request_id": request_id,
        "action": const.REQUEST_TERMINAL_SERVER_MODIFY_TERMINAL,
        "terminal_mac": terminal_mac,
        "terminal_server_ip":terminal_server_ip,
        "ret_code":0
        }
    request_buf = json_dump(request)
    try:
        server.send(sock, request_buf, len(request_buf))
        ctx.terminal_request.update({request_id: None})
    except Exception, e:
        logger.error("send request to terminal with exception: %s" % e)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_SERVER_SEND_REQUEST_ERROR, request_id))

    rep = wait_terminal_response(request_id, timeout=10)
    if rep is None:
        logger.error("wait response [%s] timeout" % request_id)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_WAIT_RESPONSE_TIMEOUT_ERROR, request_id))
    if isinstance(rep, Error):
        logger.error("wait response [%s] error" % request_id)
        return return_error(req, rep)

    return return_success(req, None)

def handle_restart_terminals(req):

    ctx = context.instance()
    terminal_mac = req.get("terminal_mac", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "terminal_mac", terminal_mac))

    server = ctx.terminals.get(terminal_mac, {}).get("server", None)
    sock = ctx.terminals.get(terminal_mac, {}).get("sock", None)

    if server is None or sock is None:
        logger.error("can't find terminal [%s] connected." % terminal_mac)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_NOT_CONNECT_ERROR, terminal_mac))

    request_id = get_uuid(UUID_TYPE_TERMINAL_REQUEST,
                          None,
                          long_format=True)

    request = {
        "request_id": request_id,
        "action": const.REQUEST_TERMINAL_SERVER_RESTART_TERMINAL,
        "terminal_mac": terminal_mac,
        "ret_code":0
        }
    request_buf = json_dump(request)
    try:
        server.send(sock, request_buf, len(request_buf))
        ctx.terminal_request.update({request_id: None})
    except Exception, e:
        logger.error("send request to terminal with exception: %s" % e)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_SERVER_SEND_REQUEST_ERROR, request_id))

    rep = wait_terminal_response(request_id, timeout=10)
    if rep is None:
        logger.error("wait response [%s] timeout" % request_id)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_WAIT_RESPONSE_TIMEOUT_ERROR, request_id))
    if isinstance(rep, Error):
        logger.error("wait response [%s] error" % request_id)
        return return_error(req, rep)

    return return_success(req, None)

def handle_stop_terminals(req):

    ctx = context.instance()
    terminal_mac = req.get("terminal_mac", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "terminal_mac", terminal_mac))

    server = ctx.terminals.get(terminal_mac, {}).get("server", None)
    sock = ctx.terminals.get(terminal_mac, {}).get("sock", None)

    if server is None or sock is None:
        logger.error("can't find terminal [%s] connected." % terminal_mac)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_NOT_CONNECT_ERROR, terminal_mac))

    request_id = get_uuid(UUID_TYPE_TERMINAL_REQUEST,
                          None,
                          long_format=True)

    request = {
        "request_id": request_id,
        "action": const.REQUEST_TERMINAL_SERVER_STOP_TERMINAL,
        "terminal_mac": terminal_mac,
        "ret_code":0
        }
    request_buf = json_dump(request)
    try:
        server.send(sock, request_buf, len(request_buf))
        ctx.terminal_request.update({request_id: None})
    except Exception, e:
        logger.error("send request to terminal with exception: %s" % e)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_SERVER_SEND_REQUEST_ERROR, request_id))

    rep = wait_terminal_response(request_id, timeout=10)
    if rep is None:
        logger.error("wait response [%s] timeout" % request_id)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_WAIT_RESPONSE_TIMEOUT_ERROR, request_id))
    if isinstance(rep, Error):
        logger.error("wait response [%s] error" % request_id)
        return return_error(req, rep)

    return return_success(req, None)

def handle_online_upgrade_terminals(req):

    ctx = context.instance()
    terminal_mac = req.get("terminal_mac", "")
    upgrade_packet_name = req.get("upgrade_packet_name", "")
    upgrade_packet_path = req.get("upgrade_packet_path", "")
    upgrade_packet_md5 = req.get("upgrade_packet_md5", "")
    if len(terminal_mac) == 0:
        logger.error("terminal_mac is empty.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE, "terminal_mac", terminal_mac))

    server = ctx.terminals.get(terminal_mac, {}).get("server", None)
    sock = ctx.terminals.get(terminal_mac, {}).get("sock", None)

    if server is None or sock is None:
        logger.error("can't find terminal [%s] connected." % terminal_mac)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_NOT_CONNECT_ERROR, terminal_mac))

    request_id = get_uuid(UUID_TYPE_TERMINAL_REQUEST,
                          None,
                          long_format=True)

    request = {
        "request_id": request_id,
        "action": const.REQUEST_TERMINAL_SERVER_ONLINE_UPGRADE_TERMINAL,
        "terminal_mac": terminal_mac,
        "upgrade_packet_name": upgrade_packet_name,
        "upgrade_packet_path": upgrade_packet_path,
        "upgrade_packet_md5": upgrade_packet_md5,
        "ret_code":0
        }
    request_buf = json_dump(request)
    try:
        server.send(sock, request_buf, len(request_buf))
        ctx.terminal_request.update({request_id: None})
    except Exception, e:
        logger.error("send request to terminal with exception: %s" % e)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_SERVER_SEND_REQUEST_ERROR, request_id))

    rep = wait_terminal_response(request_id, timeout=10)
    if rep is None:
        logger.error("wait response [%s] timeout" % request_id)
        return return_error(req, Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_TERMINAL_WAIT_RESPONSE_TIMEOUT_ERROR, request_id))
    if isinstance(rep, Error):
        logger.error("wait response [%s] error" % request_id)
        return return_error(req, rep)

    return return_success(req, None)

