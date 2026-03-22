from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
from utils.global_conf import get_zone_conf

import resource_control.zone.resource_limit as ResourceLimit

def init_zone_connection(zone):

    ctx = context.instance()
    zone_id = zone["zone_id"]
    zone_deploy =  ctx.zone_deploy

    ret = ctx.pgm.get_zone_connection(zone_id)
    if ret:
        return None

    if zone_deploy == const.DEPLOY_TYPE_STANDARD:
        zone_connection = {
            "zone_id": zone_id,
            "base_zone_id": '',
            "base_zone_name": '',
            "account_user_id": '',
            "account_user_name": '',
            "access_key_id": '',
            "secret_access_key": '',
            "host": '',
            "host_ip": '',
            "port": const.DEFAULT_PORT_80,
            "protocol": const.DEFAULT_PROTOCOL_HTTP,
            "http_socket_timeout": const.HTTP_SOCKET_TIMEOUT,
            "status": const.CONNECTION_STATUS_INVAILD,
            }
    elif zone_deploy == const.DEPLOY_TYPE_EXPRESS:
        zone_conf = get_zone_conf()
        if not zone_conf:
            logger.error("no found zone config")
            return -1

        zones = zone_conf.get("zones")
        for base_zone_id,zones_value in zones.items():

            base_zone_name = base_zone_id.upper()
            account_user_id = zones_value.get("user_id","")
            access_key_id = zones_value.get("qy_access_key_id", "")
            secret_access_key = zones_value.get("qy_secret_access_key", "")
            host = zones_value.get("host", "")

            zone_connection = {
                "zone_id": zone_id,
                "base_zone_id": base_zone_id,
                "base_zone_name": base_zone_name,
                "account_user_id": account_user_id,
                "account_user_name": '',
                "access_key_id": access_key_id,
                "secret_access_key": secret_access_key,
                "host": host,
                "host_ip": '',
                "port": const.DEFAULT_PORT_80,
                "protocol": const.DEFAULT_PROTOCOL_HTTP,
                "http_socket_timeout": const.HTTP_SOCKET_TIMEOUT,
                "status": const.CONNECTION_STATUS_INVAILD,
                }

    if not ctx.pg.insert(dbconst.TB_ZONE_CONNECTION, zone_connection):
        logger.error("insert newly created zone connection for [%s] to db failed" % (zone_connection))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return None

def init_zone_citrix_connection(zone):
    
    ctx = context.instance()
    zone_id = zone["zone_id"]
    if zone["platform"] != const.PLATFORM_TYPE_CITRIX:
        return None
    
    ret = ctx.pgm.get_zone_citrix_connection(zone_id)
    if ret:
        return None
    
    citrix_zone_connection = {
        "zone_id": zone_id,
        "host": '',
        "port": const.DEFAULT_PORT_10080,
        "protocol": const.DEFAULT_PROTOCOL_HTTP,
        "http_socket_timeout": const.HTTP_SOCKET_TIMEOUT,
        "status": const.CONNECTION_STATUS_INVAILD,
        "managed_resource": '',
        "storefront_uri": '',
        }
    
    if not ctx.pg.insert(dbconst.TB_ZONE_CITRIX_CONNECTION, citrix_zone_connection):
        logger.error("insert newly created zone citrix connection for [%s] to db failed" % (citrix_zone_connection))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return None

def init_zone_resource_limit(zone):

    ctx = context.instance()
    zone_id = zone["zone_id"]

    ret = ctx.pgm.get_zone_resource_limit(zone_id)
    if ret:
        return None

    ret = ResourceLimit.init_resource_limit(zone_id)
    if isinstance(ret, Error):
        return ret

    return None

def init_desktop_zone(zone_id):
    
    ctx = context.instance()
    zone = ctx.pgm.get_zone(zone_id)
    if not zone:
        logger.error("init zone fail, no found zone %s" % (zone_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)
    
    # init iaas connection
    ret = init_zone_connection(zone)
    if isinstance(ret, Error):
        return ret
    
    # init citrix connection
    ret = init_zone_citrix_connection(zone)
    if isinstance(ret, Error):
        return ret
    
    # init resource limit
    ret = init_zone_resource_limit(zone)
    if isinstance(ret, Error):
        return ret
    
    return None


    