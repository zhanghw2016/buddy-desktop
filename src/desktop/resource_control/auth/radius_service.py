from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
from utils.id_tool import(
    UUID_TYPE_RADIUS_SERVICE,
    UUID_TYPE_DESKTOP_USER
)

from utils.id_tool import(
    get_uuid
)
from utils.net import is_radius_port_open
from utils.misc import get_current_time
import api.user.user as APIUser
import constants as const

def format_radius_services(radius_service_set):
    
    ctx = context.instance()
    for radius_service_id, radius_service in radius_service_set.items():
        
        ret = ctx.pgm.get_radius_users(radius_service_id)
        if not ret:
            ret = {}
        
        radius_service["radius_users"] = ret.values()

    return radius_service_set

def check_radius_service_host(host):
    
    ctx = context.instance()
    ret = ctx.pgm.get_radius_service(host=host)
    if ret:
        logger.error("auth service host %s already existed" % (host))
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_RESOURCE_ALREADY_EXISTED)

    return None

def check_radius_service_status(host, port):
    
    status = const.SERVICE_STATUS_CONN_ACTIVE
    if not is_radius_port_open(host, port):
        status = const.SERVICE_STATUS_CONN_UNREACHABLE

    return status

def build_radius_service(req):
    
    ctx = context.instance()
    keys = ["host", "port", "acct_session", "identifier", "secret", "auth_service_id", "ou_dn"]
    
    radius_service_info = {}
    for key in keys:
        if key not in req:
            continue
        radius_service_info[key] = req[key]
    
    ou_dn = radius_service_info.get("ou_dn")
    if ou_dn:
        ret = ctx.pgm.get_ou_guid(ou_dn)
        if ret:
            radius_service_info["dn_guid"] = ret
        
    
    return radius_service_info

def create_radius_service(req):

    ctx = context.instance()
    radius_service_id = get_uuid(UUID_TYPE_RADIUS_SERVICE, ctx.checker)
    status = check_radius_service_status(req["host"], req["port"])
    if not status:
        status = const.SERVICE_STATUS_UNKNOWN
    radius_service_info = build_radius_service(req)
    
    update_info = dict(
                      radius_service_id = radius_service_id,
                      radius_service_name = req.get("radius_service_name", ''),
                      description = req.get("description", ''),
                      enable_radius = req.get("enable_radius", 0),
                      status = status,
                      create_time = get_current_time(),
                      status_time = get_current_time(),
                      )
    update_info.update(radius_service_info)
    # register desktop group
    if not ctx.pg.insert(dbconst.TB_RADIUS_SERVICE, update_info):
        logger.error("insert newly created radius service for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return radius_service_id

def check_radius_service_vaild(radius_service_ids, status=None):
    
    ctx = context.instance()
    ret = ctx.pgm.get_radius_services(radius_service_ids)
    if not ret:
        logger.error("no found radius service %s" % (radius_service_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, radius_service_ids)
    radius_services = ret

    if status:
        for radius_service_id, radius_service in radius_services.items():
            if radius_service["status"] != status:
                logger.error("auth service %s status %s invaild" % (radius_service_id, radius_service["status"]))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
  
    return radius_services

def modify_radius_service_attributes(radius_service_id, need_maint_columns):

    ctx = context.instance()
    status = check_radius_service_status(need_maint_columns["host"], need_maint_columns["port"])
    if not status:
        status = const.SERVICE_STATUS_UNKNOWN
    need_maint_columns["status"] =  status     
    if not ctx.pg.batch_update(dbconst.TB_RADIUS_SERVICE, {radius_service_id: need_maint_columns}):
        logger.error("modify radius service update DB fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    return radius_service_id

def delete_radius_services(radius_service_ids):
    ctx = context.instance()

    for radius_service_id in radius_service_ids:
        
        remove_auht_radius_service(radius_service_id)
        
        ctx.pg.delete(dbconst.TB_RADIUS_SERVICE, radius_service_id)

    return None

def check_add_auth_radius_users(sender, radius_service, user_ids):

    ctx = context.instance()
    radius_service_id = radius_service["radius_service_id"]
    ou_dn = radius_service["ou_dn"]
    auth_service_id = radius_service["auth_service_id"]
    if not auth_service_id:
        logger.error("radius %s need config auth service" % radius_service_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RADIUS_NEED_CONFIG_AUTH_SERVICE, radius_service_id)
    
    users = ctx.pgm.get_user_and_user_group_names(user_ids)
    if not users:
        logger.error("no found user %s " % user_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_NO_FOUND_ZONE_USER, (sender["zone"], user_ids))
    
    user_names = users.values()
    auth_users = ctx.auth.get_auth_users(auth_service_id, ou_dn, user_names)
    if not auth_users:
        auth_users = {}
   
    auth_user_groups = ctx.auth.get_auth_user_groups(auth_service_id, ou_dn, user_names, index_name=True)
    if not auth_user_groups:
        auth_user_groups = {}
    
    auth_users.update(auth_user_groups)
    
    for user_id in user_ids:
        if user_id not in users:
            logger.error("no found user %s " % user_ids)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_NO_FOUND_ZONE_USER, (sender["zone"], user_ids))
        
        user_name = users[user_id]
        if user_name not in auth_users:
            logger.error("no found user %s, %s " % (user_name, auth_users))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_NO_FOUND_ZONE_USER, (sender["zone"], user_ids))

    ret = APIUser.check_desktop_user(ctx, user_ids, const.USER_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return ret
    desktop_users = ret
    radius_users = ctx.pgm.get_radius_users(user_ids = user_ids)
    if not radius_users:
        radius_users = {}
    for user_id, _ in desktop_users.items():
        if user_id in radius_users:
            logger.error("user %s existed in radius" % user_id)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_RADIUS_USER_EXISTED, user_id)

    return desktop_users

def add_auth_radius_users(radius_service, desktop_users, check_radius):

    ctx = context.instance()
    radius_service_id = radius_service["radius_service_id"]
    
    radius_users = {}
    for user_id, desktop_user in desktop_users.items():
        
        user_name = desktop_user.get("user_name")
        user_type = const.USER_TYPE_USER if user_id.startswith(UUID_TYPE_DESKTOP_USER) else const.USER_TYPE_GROUP
        
        if user_type == const.USER_TYPE_GROUP:
            user_name = desktop_user["user_group_name"]
        
        user_info = dict(
                        radius_service_id = radius_service_id,
                        user_id = user_id,
                        user_name = user_name,
                        user_type = user_type,
                        check_radius = check_radius,
                        )

        radius_users[user_id] = user_info

    if not ctx.pg.batch_insert(dbconst.TB_RADIUS_USER, radius_users):
        logger.error("insert newly created radius user for [%s] to db failed" % (radius_users))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def check_remove_auth_radius_service(radius_service_id, user_ids):
    
    ctx = context.instance()
    ret = ctx.pgm.get_radius_users(radius_service_id, user_ids)
    if not ret:
        return None
    
    return ret.keys()

def remove_auht_radius_service(radius_service_id, user_ids=None):

    ctx = context.instance()  

    conditions = {"radius_service_id": radius_service_id}
    if user_ids:
        conditions["user_id"] = user_ids
    
    ctx.pg.base_delete(dbconst.TB_RADIUS_USER, conditions)

def check_auth_radius_users(user_ids):

    ctx = context.instance()
    
    radius_users = ctx.pgm.get_radius_users(user_ids = user_ids)
    if not radius_users:
        radius_users = {}

    return radius_users

def modify_radius_user_attributes(user_id, need_maint_columns):

    ctx = context.instance()
    if not ctx.pg.base_update(dbconst.TB_RADIUS_USER, {"user_id": user_id},need_maint_columns):
        logger.error("modify radius service update DB fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None
    