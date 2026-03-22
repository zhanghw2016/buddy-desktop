'''
Created on 2017-3-8

@author: yunify
'''
import context
from log.logger import logger
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from common import return_success, return_error, return_items, build_filter_conditions, get_sort_key, get_reverse
from common import is_global_admin_user
import db.constants as dbconst
import resource_control.desktop.resource_permission as ResCheck
import resource_control.syslog_server as SyslogServer

def handle_create_syslog_server(req):
    if not is_global_admin_user(req['sender']):
        logger.error("only global admin can modify system config.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    ret = ResCheck.check_request_param(req, ["host", "port", "protocol", "runtime"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    host = req.get("host")
    port = req.get("port")
    protocol = req.get("protocol")
    runtime = req.get("runtime")

    if host:
        ret = SyslogServer.check_syslog_server_host(host, port)
        if not ret:
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                           ErrorMsg.ERR_MSG_SYSLOG_SERVER_HAVE_EXIST_ERROR))
    if runtime:
        ret = SyslogServer.check_syslog_server_runtime(runtime)
        if not ret:
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                           ErrorMsg.ERR_MSG_SYSLOG_SERVER_RUNTIME_ERROR))

    ret = SyslogServer.create_syslog_server(host, port, protocol, runtime)
    if isinstance(ret, Error):
        logger.error("create syslog server error.")
        return return_error(req, ret)

    rep = {"syslog_server_id": ret}
   
    return return_success(req, rep)

def handle_modify_syslog_server(req):
    if not is_global_admin_user(req['sender']):
        logger.error("only global admin can modify system config.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    ret = ResCheck.check_request_param(req, ["syslog_server"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    syslog_server_id = req.get("syslog_server")
    host = req.get("host")
    port = req.get("port")
    protocol = req.get("protocol")
    runtime = req.get("runtime")
    status = req.get("status")

    syslog_server = SyslogServer.get_syslog_server(syslog_server_id)
    if not syslog_server:
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                           ErrorMsg.ERR_MSG_SYSLOG_SERVER_NOT_EXIST_ERROR))
    if host and port:
        ret = SyslogServer.check_syslog_server_host(host, port, syslog_server_id)
        if not ret:
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                           ErrorMsg.ERR_MSG_SYSLOG_SERVER_HAVE_EXIST_ERROR))
    else:
        if host:
            port = syslog_server["port"]
            ret = SyslogServer.check_syslog_server_host(host, port, syslog_server_id)
            if not ret:
                return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                               ErrorMsg.ERR_MSG_SYSLOG_SERVER_HAVE_EXIST_ERROR))
        if port:
            host = syslog_server["host"]
            ret = SyslogServer.check_syslog_server_host(host, port, syslog_server_id)
            if not ret:
                return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                               ErrorMsg.ERR_MSG_SYSLOG_SERVER_HAVE_EXIST_ERROR))

    if runtime:
        ret = SyslogServer.check_syslog_server_runtime(runtime, syslog_server_id)
        if not ret:
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                           ErrorMsg.ERR_MSG_SYSLOG_SERVER_RUNTIME_ERROR))

    ret = SyslogServer.modify_syslog_server(syslog_server_id, host, port, protocol, runtime, status)
    if isinstance(ret, Error):
        logger.error("create syslog server error.")
        return return_error(req, ret)

    rep = {"syslog_server_id": ret}
   
    return return_success(req, rep)

def handle_delete_syslog_servers(req):
    if not is_global_admin_user(req['sender']):
        logger.error("only global admin can modify system config.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    syslog_server_ids = req.get("syslog_servers")

    ret = SyslogServer.delete_syslog_server(syslog_server_ids)
    if isinstance(ret, Error):
        logger.error("create syslog server error.")
        return return_error(req, ret)

    rep = {"syslog_server_id": syslog_server_ids}
   
    return return_success(req, rep)

def handle_describe_syslog_servers(req):
    if not is_global_admin_user(req['sender']):
        logger.error("only global admin can modify system config.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))
    ctx = context.instance()

    filter_conditions = build_filter_conditions(req, dbconst.TB_SYSLOG_SERVER)
    if "syslog_servers" in req:
        filter_conditions.update({'syslog_server_id':req["syslog_servers"]})
    if "host" in req:
        filter_conditions.update({'host':req["host"]})
    if "protocol" in req:
        filter_conditions.update({'protocol':req["protocol"]})
    if "status" in req:
        filter_conditions.update({'status':req["status"]})
    if "port" in req:
        filter_conditions.update({'port':req["port"]})

    display_columns = dbconst.PUBLIC_COLUMNS[dbconst.TB_SYSLOG_SERVER]

    logger.info(filter_conditions)
    syslog_server_set = ctx.pg.get_by_filter(dbconst.TB_SYSLOG_SERVER, filter_conditions, display_columns,
                                     sort_key=get_sort_key(dbconst.TB_SYSLOG_SERVER, req.get("sort_key")),
                                     reverse=get_reverse(req.get("reverse")),
                                     offset=req.get("offset", 0),
                                     limit=req.get("limit", dbconst.DEFAULT_LIMIT))
    logger.info(syslog_server_set)
    if syslog_server_set is None:
        logger.error("describe syslog server form failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_SYSLOG_SERVER, filter_conditions)
    if total_count is None:
        logger.error("get syslog server form count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    rep = {'total_count':total_count}

    return return_items(req, syslog_server_set, "syslog_server", **rep)
