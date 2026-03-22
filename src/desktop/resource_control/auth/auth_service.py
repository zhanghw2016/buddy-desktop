from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
from utils.id_tool import(
    UUID_TYPE_AUTH_SERVICE,
    UUID_TYPE_DESKTOP_OU
)
import constants as const
from utils.id_tool import(
    get_uuid
)
from utils.net import is_port_open
from utils.misc import get_current_time

import resource_control.auth.sync_auth_user as SyncAuthUser
import api.user.user as APIUser
from resource_control.zone.zone import zone_sync_to_other_server

def check_auth_service_base_dn(sender, auth_service, base_dn=None):

    ctx = context.instance()
    if base_dn:
        base_dn = ctx.auth.format_base_dn(base_dn)
        if base_dn != auth_service["base_dn"] and base_dn in auth_service["base_dn"]:
            base_dn = auth_service["base_dn"]
    else:
        base_dn = auth_service["base_dn"]
    
    if APIUser.is_global_admin_user(sender):
        return base_dn

    zone_id = sender.get("zone")
    auth_zone = ctx.pgm.get_auth_zone(zone_id)
    if auth_zone:
        zone_base_dn = ctx.auth.format_base_dn(auth_zone["base_dn"])
        if zone_base_dn != base_dn and base_dn in zone_base_dn:
            base_dn = zone_base_dn

    return base_dn

def format_auth_services(auth_service_set):
    
    ctx = context.instance()
    for auth_service_id, auth_service in auth_service_set.items():
        
        ret = ctx.pgm.get_auth_zones(auth_service_id)
        if not ret:
            auth_service["zones"] = []
        
        else:
            auth_service["zones"] = ret.values()
            
        ret = ctx.pgm.get_auth_radius(auth_service_id)
        if not ret:
            auth_service["radius"] = ''
            
        else:
            auth_service["radius"] = ret["radius_service_id"]

    return auth_service_set

def check_auth_service_status(host, port, secret_port):

    status = const.SERVICE_STATUS_CONN_ACTIVE
    if not is_port_open(host, port) or not is_port_open(host, secret_port):
        status = const.SERVICE_STATUS_CONN_UNREACHABLE

    return status

def build_auth_service(req):
    
    keys = ["auth_service_type", "admin_name", "admin_password", "base_dn",
            "domain", "host", "port", "secret_port", "secondary_host"]
    
    auth_service_info = {}
    for key in keys:
        if key not in req:
            continue
        auth_service_info[key] = req[key]
    return auth_service_info

def check_auth_service_config(req, auth_service_id=None, scope=0):
    
    ctx = context.instance()
    check_keys = ["domain", "admin_name", "admin_password", "host", "port", "secret_port", "auth_service_type"]
    if auth_service_id:
        ret = ctx.pgm.get_auth_service(auth_service_id)
        if not ret:
            logger.error("no found auth service %s" % (auth_service_id))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_AUTH_SERVICE_NO_FOUND, auth_service_id)
        auth_service = ret
        for key in check_keys:
            if key not in req:
                req[key] = auth_service[key]
        
        req["base_dn"] = auth_service["base_dn"]
        
    else:
        
        base_dn = req.get("base_dn")
        if not base_dn:
            req["base_dn"] = ctx.auth.get_domain_dn(req["domain"])

    ret = ctx.auth.test_auth_service(req, scope=scope)
    if isinstance(ret, Error):
        return ret

    return ret    

def build_domain_auth_ou(domain):
    
    ctx = context.instance()
    
    domain_ou = {
        "ou_dn": ctx.auth.get_domain_dn(domain),
        "description": '',
        "base_dn": ctx.auth.get_domain_dn(domain),
        "object_guid": '',
        "path": '',
        "is_import": 0,
        "ou_name": domain
        }

    return domain_ou

def format_check_auth_ous(auth_ous, domain):
    
    ctx = context.instance()
    
    if not auth_ous:
        auth_ous = {}
    
    ret = build_domain_auth_ou(domain)
    auth_ous[ret["ou_dn"]] = ret
    
    for ou_dn, auth_ou in auth_ous.items():
        
        ret = ctx.pgm.search_user_ous(ou_dn)
        if not ret:
            auth_ou["is_import"] = 0
        else:
            auth_ou["is_import"] = 1
    
    return auth_ous

def check_auth_service_domain(req):
    
    ctx = context.instance()
    domain = req["domain"]
    base_dn = req["base_dn"]

    ret =  ctx.pgm.get_auth_service_by_domain(domain=domain)
    if not ret:
        return None

    auth_services = ret
    base_dn = ctx.auth.format_base_dn(base_dn)
    for auth_service_id, auth_service in auth_services.items():

        if base_dn in auth_service["base_dn"]:
            logger.error("auth service include base dn %s" % (base_dn))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_AUTH_SERVICE_BASE_DN_EXISTED, base_dn)
        
        ou_name,_ = ctx.auth.get_base_dn(base_dn)
        ret = ctx.auth.get_auth_ous(auth_service_id, auth_service["base_dn"], ou_name)
        if ret:
            logger.error("auth service base dn %s,%s conflict" % (base_dn, ou_name))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_AUTH_SERVICE_BASE_DN_EXISTED, base_dn)
    
    return None

def create_auth_service(req):

    ctx = context.instance()
    auth_service_id = get_uuid(UUID_TYPE_AUTH_SERVICE, ctx.checker)
    
    auth_service_type = req["auth_service_type"]
    status = const.SERVICE_STATUS_ACTIVE
    if auth_service_type != const.AUTH_TYPE_LOCAL:
        status = check_auth_service_status(req["host"], req["port"], req["secret_port"])
        if not status:
            status = const.SERVICE_STATUS_UNKNOWN

    auth_service_info = build_auth_service(req)
    auth_service_info["base_dn"] = auth_service_info["base_dn"]
    auth_service_info["base_dn"] = auth_service_info["base_dn"].replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
    auth_service_info["base_dn"] = auth_service_info["base_dn"].replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")
    is_sync = req.get("is_sync", 0)
    if auth_service_type == const.AUTH_TYPE_LOCAL:
        is_sync = 1

    modify_password = req.get("modify_password")
    if modify_password is None:
        modify_password = is_sync
        
    update_info = dict(
                      auth_service_id = auth_service_id,
                      auth_service_name = req.get("auth_service_name", ''),
                      description = req.get("description", ''),
                      status = status,
                      is_sync = is_sync,
                      modify_password = modify_password,
                      create_time = get_current_time(),
                      status_time = get_current_time(),
                      )
    update_info.update(auth_service_info)
    # register desktop group
    if not ctx.pg.insert(dbconst.TB_AUTH_SERVICE, update_info):
        logger.error("insert newly created policy group for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    ret = refresh_auth_service(update_info, auth_service_info["base_dn"])
    if isinstance(ret, Error):
        return ret

    base_dn = auth_service_info["base_dn"]
    ret = ctx.pgm.get_ou_guid(base_dn)
    if ret:
        conditions = {"auth_service_id": auth_service_id}
        update_guid = {"dn_guid":ret}
        if not ctx.pg.base_update(dbconst.TB_AUTH_SERVICE, conditions, update_guid):
            logger.error("update auth service guid %s ou info %s fail" % (conditions, update_guid))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
    if "ou=" not in auth_service_info["base_dn"]:
        user_ou_id = "%s-%s" % (UUID_TYPE_DESKTOP_OU, auth_service_info["domain"])

        ret = ctx.pgm.get_user_ou_dn(user_ou_id)
        if ret:
            return None

        base_dn_info = {
            "user_ou_id": user_ou_id,
            "auth_service_id": auth_service_id,
            "ou_name": auth_service_info["domain"],
            "object_guid": "",
            "ou_dn": auth_service_info["base_dn"],
            "base_dn": auth_service_info["base_dn"],
            }

        if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_USER_OU, {user_ou_id: base_dn_info}):
            logger.error("insert newly created desktop ou for [%s] to db failed" % (base_dn_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return auth_service_id
    
def check_auth_service_vaild(auth_service_ids, status=None):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_auth_services(auth_service_ids)
    if not ret:
        logger.error("no found auth service %s" % (auth_service_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_AUTH_SERVICE_NO_FOUND, auth_service_ids)
    auth_services = ret

    if not status:
        return auth_services
        
    for auth_service_id, auth_service in auth_services.items():
        if auth_service["status"] != status:
            logger.error("auth service %s status %s invaild" % (auth_service_id, auth_service["status"]))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return auth_services

def modify_auth_service_attributes(auth_service_id, need_maint_columns):
    
    ctx = context.instance()

    if not ctx.pg.batch_update(dbconst.TB_AUTH_SERVICE, {auth_service_id: need_maint_columns}):
        logger.error("modify auth service update DB fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
    ctx.auth.update_auth_service(auth_service_id)

    return None

def check_delete_auth_service(auth_service_ids):

    ctx = context.instance()

    for auth_service_id in auth_service_ids:
        ret = ctx.pgm.get_auth_zones(auth_service_id)
        if ret:
            logger.error("auth service has zone %s in used" % ret.keys())
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_AUTH_SERVICE_HAS_ZONE_IN_USED, auth_service_id)

    return None

def clear_auth_service_users(auth_service_id):
    
    ctx = context.instance()

    condition = {"auth_service_id": auth_service_id}
    ctx.pg.base_delete(dbconst.TB_DESKTOP_USER, condition)
    
    user_groups = ctx.pgm.get_desktop_user_groups(auth_service_id)
    if user_groups:
        group_condition = {"user_group_id": user_groups.keys()}
        ctx.pg.base_delete(dbconst.TB_DESKTOP_USER_GROUP_USER, group_condition)

    ctx.pg.base_delete(dbconst.TB_DESKTOP_USER_GROUP, condition)
    ctx.pg.base_delete(dbconst.TB_DESKTOP_USER_OU, condition)
    
    return None


def delete_auth_services(auth_services):
    ctx = context.instance()

    for auth_service_id, auth_service in auth_services.items():
        
        ret = ctx.pgm.get_auth_zones(auth_service_id)
        if ret:
            continue

        clear_auth_service_users(auth_service_id)
        ctx.pg.delete(dbconst.TB_AUTH_SERVICE, auth_service_id)
        
        user_ou_id = "%s-%s" % (UUID_TYPE_DESKTOP_OU, auth_service["domain"])
        ret = ctx.pgm.get_user_ou_dn(user_ou_id)
        if ret:
            ctx.pg.delete(dbconst.TB_DESKTOP_USER_OU, user_ou_id)

    return None

def refresh_auth_service(auth_service, base_dn):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    base_dn = ctx.auth.format_base_dn(base_dn)

    ret = SyncAuthUser.check_auth_ou_base_dn(auth_service, base_dn)
    if isinstance(ret, Error):
        return ret

    if not ret:
        logger.error("auth ou %s no found" % base_dn)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_REFRESH_AUTH_OUS_DN_FAIL, base_dn)
    new_base_dn = ret
    
    ret = SyncAuthUser.sync_auth_ous(auth_service_id, new_base_dn, old_ou_dn=base_dn)
    if isinstance(ret, Error):
        return ret

    ret = SyncAuthUser.sync_auth_users(auth_service_id, new_base_dn, old_ou_dn=base_dn)
    if isinstance(ret, Error):
        return ret

    ret = SyncAuthUser.sync_auth_user_group(auth_service_id, new_base_dn, old_ou_dn=base_dn)
    if isinstance(ret, Error):
        return ret

    return None

def check_auth_zone(zone_id, is_add=False):
    
    ctx = context.instance()
      
    zone = ctx.pgm.get_zone(zone_id)
    if not zone:
        logger.error("no found zone %s" % (zone_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)
    
    ret = ctx.pgm.get_auth_zone(zone_id)   
    if is_add:

        if ret:
            logger.error("zone already has auth service %s" % (zone_id))
            return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                         ErrorMsg.ERR_MSG_ZONE_HAS_AUTH_SERVICE, zone_id)
    else:
        if not ret:
            logger.error("no found zone %s" % (zone_id))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)
    
    if not ret:
        return zone

    auth_zone = ret
    auth_service_id = auth_zone["auth_service_id"]
    auth_dn = auth_zone["base_dn"]
    object_guid = auth_zone["object_guid"]

    _, base_dn = ctx.auth.get_base_dn(auth_dn)

    ret = ctx.auth.get_auth_ous(auth_service_id, base_dn)
    if isinstance(ret, Error):
        return ret

    if not ret:
        return None
    
    auth_ous = ret
    for _, auth_ou in auth_ous.items():
        if auth_ou["object_guid"] != object_guid:
            continue
        
        if auth_ou["ou_dn"].lower() != auth_dn.lower():
            
            ou_dn = ctx.auth.format_base_dn(auth_ou["ou_dn"])
            if not ctx.pg.batch_update(dbconst.TB_ZONE_AUTH, {zone_id: {"base_dn": ou_dn}}):
                logger.error("update zone auth fail %s" % zone_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    return zone

def add_auth_service_to_zone(auth_service, zone_id, base_dn=None):

    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]

    if not base_dn:
        base_dn = auth_service["base_dn"]
    
    ret = ctx.auth.get_auth_ous(auth_service_id, base_dn)
    if isinstance(ret, Error) or not ret:
        return ret
    
    auth_ou = ret.get(base_dn, {})

    update_info = dict(
                      zone_id = zone_id,
                      auth_service_id = auth_service_id,
                      base_dn = base_dn,
                      object_guid = auth_ou.get("object_guid", "")
                      )
    # register desktop group
    if not ctx.pg.insert(dbconst.TB_ZONE_AUTH, update_info):
        logger.error("insert newly created policy group for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    ret = ctx.zone_builder.update_zone_status(zone_id)
    if isinstance(ret, Error):
        return ret

    ctx.zone_builder.load_zone(zone_id)
    zone_sync_to_other_server(zone_id)
    
    ret = refresh_auth_service(auth_service, base_dn)
    if isinstance(ret, Error):
        return ret

    return ret

def remove_auth_service_from_zones(auth_service_id, zone_ids):

    ctx = context.instance()
    if not isinstance(zone_ids, list):
        zone_ids = [zone_ids]

    for zone_id in zone_ids:
        
        ctx.pg.base_delete(dbconst.TB_ZONE_USER, {"zone_id": zone_id})
        ctx.pg.base_delete(dbconst.TB_ZONE_USER_GROUP, {"zone_id": zone_id})
        ctx.pg.base_delete(dbconst.TB_ZONE_USER_SCOPE, {"zone_id": zone_id})
        
        condition = dict(
                          zone_id = zone_id,
                          auth_service_id = auth_service_id,
                          )
        
        ctx.pg.base_delete(dbconst.TB_ZONE_AUTH, condition)

        ret = ctx.zone_builder.update_zone_status(zone_id)
        if isinstance(ret, Error):
            return ret

    return None

