import context
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import constants as const
import  db.constants as dbconst
from utils.id_tool import UUID_TYPE_SYSLOG_SERVER, get_uuid
from utils.misc import get_current_time

def check_syslog_server_host(host, port, syslog_server_id=None):
    ctx = context.instance()
    conds = {
        "host": host,
        "port": port
        }
    ret = ctx.pg.base_get(dbconst.TB_SYSLOG_SERVER, conds)
    if not ret:
        return True
    if syslog_server_id:
        if syslog_server_id == ret[0]["syslog_server_id"]:
            return True
    return False


def check_syslog_server_runtime(runtime, syslog_server_id=None):
    ctx = context.instance()
    conds = {"runtime": runtime}
    ret = ctx.pg.base_get(dbconst.TB_SYSLOG_SERVER, conds)
    if not ret:
        return True
    if syslog_server_id:
        if syslog_server_id == ret[0]["syslog_server_id"]:
            return True
    return False

def get_syslog_server(syslog_server_id):
    ctx = context.instance()
    conds = {"syslog_server_id": syslog_server_id}
    ret = ctx.pg.base_get(dbconst.TB_SYSLOG_SERVER, conds)
    if not ret:
        return None
    return ret[0]

def create_syslog_server(host, port, protocol, runtime):
    ctx = context.instance()

    current_time = get_current_time()
    syslog_server_id = get_uuid(UUID_TYPE_SYSLOG_SERVER,
                             ctx.checker, 
                             long_format=True)

    syslog_server = {}
    syslog_server['syslog_server_id'] = syslog_server_id
    syslog_server['host'] = host
    syslog_server['status'] = const.SYSLOG_SERVER_STATUS_ACTINE
    syslog_server['port'] = port
    syslog_server['protocol'] = protocol
    syslog_server['runtime'] = runtime
    syslog_server['create_time'] = current_time

    try:
        if not ctx.pg.insert(dbconst.TB_SYSLOG_SERVER, syslog_server):
            logger.error("create syslog server [%s] failed." % (syslog_server))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_SYSLOG_SERVER_CREATE_ERROR)

        return syslog_server_id
    except Exception,e:
        logger.error("create syslog server with Exception: %s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def modify_syslog_server(syslog_server_id, host=None, port=None, protocol=None, runtime=None, status=None):
    ctx = context.instance()

    attrs = {}

    if host:
        attrs["host"] = host
    if port:
        attrs["port"] = port
    if protocol:
        attrs["protocol"] = protocol
    if runtime:
        attrs["runtime"] = runtime
    if status:
        attrs["status"] = status

    try:
        if not ctx.pg.update(dbconst.TB_SYSLOG_SERVER, syslog_server_id, attrs):
            logger.error("modify syslog server [%s] failed." % (attrs))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_SYSLOG_SERVER_MODIFY_ERROR)

        return syslog_server_id
    except Exception,e:
        logger.error("modify syslog server with Exception: %s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_SYSLOG_SERVER_MODIFY_ERROR)

def delete_syslog_server(syslog_server_ids):
    ctx = context.instance()

    if not syslog_server_ids:
        return None

    syslog_servers = {"syslog_server_id": syslog_server_ids}

    try:
        if not ctx.pg.base_delete(dbconst.TB_SYSLOG_SERVER, syslog_servers):
            logger.error("delete syslog server [%s] failed." % (syslog_servers))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_SYSLOG_SERVER_DELETE_ERROR)

        return syslog_server_ids
    except Exception,e:
        logger.error("delete syslog server with Exception: %s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_SYSLOG_SERVER_DELETE_ERROR)
