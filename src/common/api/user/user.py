import db.constants as dbconst
import constants as const
from utils.id_tool import UUID_TYPE_DESKTOP_USER
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from log.logger import logger

def build_global_admin_info(ctx):
    
    global_users = ctx.pgm.get_global_admin_user()
    if not global_users:
        return {}
    
    users = {}
    for user_id, user in global_users.items():
        user_name = user["user_name"]
        users[user_id] = user
        users[user_name] = user
        
    return users

def check_gloabl_admin_user(ctx, user_id):
    
    if not user_id:
        return None
    
    user_name = user_id.split('@')[0]
    if not user_name:
        return None
    
    if user_name not in ctx.admin_users:
        return None
    
    return ctx.admin_users.get(user_name)

def update_user_last_zone(ctx, user_id, zone_id):
    
    if not zone_id:
        return None
    
    zones = ctx.pgm.get_zones()
    if not zones:
        zones = {}
    
    if zone_id not in zones:
        return None

    ret = ctx.pgm.get_desktop_users(user_id)
    if not ret:
        return None
    
    desktop_user = ret[user_id]
    if desktop_user["last_zone"] == zone_id:
        return None

    ctx.pg.batch_update(dbconst.TB_DESKTOP_USER, {user_id: {"last_zone": zone_id}})

    return zone_id

def select_user_zone(ctx, desktop_user, zone_ids=None):
    
    user_id = desktop_user["user_id"]
    if zone_ids and not isinstance(zone_ids, list):
        zone_ids = [zone_ids]

    default_zone = desktop_user["default_zone"]
    if not default_zone:
        default_zone = desktop_user["last_zone"]

    if default_zone:
        
        if not zone_ids:
            return default_zone
        
        elif default_zone in zone_ids:
            return default_zone

    if desktop_user["role"] == const.USER_ROLE_GLOBAL_ADMIN:
        ret = ctx.pgm.get_zone_resource_count()
        if ret is None:
            logger.error("user %s no avail zone " % (user_id))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                ErrorMsg.ERR_MSG_NO_AVAIL_ZONE, user_id)
        max_zone, _ = ret
        return max_zone
    else:
        ret = ctx.pgm.get_zone_resource_count(zone_ids, user_id)
        if ret is None:
            logger.error("user %s no avail zone " % (user_id))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                ErrorMsg.ERR_MSG_NO_AVAIL_ZONE, user_id)

        max_zone, _ = ret
        return max_zone

def get_auth_service_user(ctx, user_id, auth_service_id=None):
    
    conditions = {}
    
    if auth_service_id:
        conditions["auth_service_id"] = auth_service_id
    if user_id.startswith(UUID_TYPE_DESKTOP_USER):
        conditions["user_id"] = user_id
    else:
        user_name = user_id
        if "@" in user_id:
            user_name = user_id.split("@")[0]

        conditions["user_name"] = user_name
    
    ret = ctx.pg.base_get(dbconst.TB_DESKTOP_USER, conditions)
    if not ret:
        return None

    return ret

def check_multiple_domain_auth(ctx, domain):
        
        ret = ctx.pgm.get_auth_service_by_domain(domain)
        if not ret:
            return None
        
        return ret.keys()

def get_user(ctx, user_id, zone_id=None, auth_service_id=None):
    
    # chekc global admin
    user = check_gloabl_admin_user(ctx, user_id)
    if user:
        return user
   
    domain = None
    if not user_id.startswith(UUID_TYPE_DESKTOP_USER):
        if "@" in user_id:
            if len(user_id.split("@")) > 1:
                domain = user_id.split("@")[1]
                ret = check_multiple_domain_auth(ctx, domain)
                if ret:
                    auth_service_id = ret
                    user_id = user_id.split("@")[0]
                else:
                    logger.error("auth user %s no found %s" % (user_id, auth_service_id))
                    return Error(ErrorCodes.PERMISSION_DENIED,
                                 ErrorMsg.ERR_MSG_USER_DOMAIN_NO_FOUND, domain)

    desktop_user = ctx.pgm.search_user_by_name(user_id, auth_service_id)
    if not desktop_user:
        logger.error("auth user %s no found %s" % (user_id, auth_service_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_USER_NO_FOUND, user_id)
    
    if len(desktop_user) > 1:
        logger.error("check user, user %s conflict %s" % (user_id, desktop_user))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_USER_NAME_CONFLICT, user_id)
    
    desktop_user = desktop_user.values()[0]
    desktop_user_id = desktop_user["user_id"]
    ret = ctx.pgm.get_user_zone(desktop_user_id, zone_id)
    if not ret:
        ret = {}
    
    zone_user = None
    if zone_id:
        zone_user = ret.get(zone_id)
    elif ret:
        zone_id = ret.keys()[0]
        zone_user = ret[zone_id]

    if not zone_user:
        logger.error("check zone user, user %s no found availe zone" % (user_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_NO_AVAIL_ZONE, user_id)

    desktop_user["zone"] = zone_id
    desktop_user["role"] = zone_user["role"]
    if domain:
        desktop_user["domain"] = domain
    return desktop_user

def is_normal_console(user):

    if user["console_id"] == const.USER_CONSOLE_ADMIN:
        return False
    return True

def is_admin_console(user):

    if user["console_id"] == const.USER_CONSOLE_ADMIN:
        return True
    return False

def is_global_admin_user(user):

    ''' check if user is global super user '''
    if user["role"] in [const.USER_ROLE_GLOBAL_ADMIN]:
        return True
    return False

def is_admin_user(user):
    ''' check if user is admin user '''
    if user["role"] in [const.USER_ROLE_GLOBAL_ADMIN, const.USER_ROLE_CONSOLE_ADMIN]:
        return True
    return False

def is_normal_user(user):
    if user["role"] in [const.USER_CONSOLE_NORMAL]:
        return True
    return False

def is_console_admin_user(user):
    ''' check if user is console admin user '''
    if user["role"] in [const.USER_ROLE_CONSOLE_ADMIN]:
        return True
    return False

def check_zone_user_vaild(ctx, zone_id, user_ids, status=None):
    
    if user_ids and not isinstance(user_ids, list):
        user_ids = [user_ids]
    
    users = ctx.pgm.get_zone_users(zone_id, user_ids)
    if not users:
        logger.error("getuser, no found user %s in any zone" % user_ids)
        return Error(ErrorCodes.USER_NAME_ERROR,
                         ErrorMsg.ERR_MSG_USER_NO_FOUND, user_ids)
    
    for user_id in user_ids:
        
        zone_user = users.get(user_id)
        if not zone_user:
            logger.error("getuser, no found user %s in any zone" % user_id)
            return Error(ErrorCodes.USER_NAME_ERROR,
                            ErrorMsg.ERR_MSG_USER_NO_FOUND, user_id)

        if status and zone_user["status"] != status:
            logger.error("check zone user, user %s status %s dismatch" % (user_id, zone_user["status"]))
            return Error(ErrorCodes.PERMISSION_DENIED,
                            ErrorMsg.ERR_MSG_USER_STATUS_NO_ACTIVE, user_id)
    
    return users

def check_desktop_user(ctx, user_ids, status=None):
    
    if not isinstance(user_ids, list):
        user_ids = [user_ids]
    
    desktop_users = ctx.pgm.get_user_and_user_group(user_ids)
    if not desktop_users:
        desktop_users = {}
    
    for user_id in user_ids:
        if user_id not in desktop_users:
            logger.error("no found desktop user %s" % user_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_USER_NO_FOUND, user_id)
    
        user = desktop_users[user_id]
        if status and user.get("status") and user["status"] != status:
            logger.error("desktop user status %s dismatch" % user_id)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_USER_STATUS_NO_ACTIVE, user_id)

    return desktop_users
