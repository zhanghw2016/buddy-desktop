from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
from utils.id_tool import(
    UUID_TYPE_NOTICE_PUSH,
    UUID_TYPE_DESKTOP_USER_GROUP
)
import constants as const
from utils.id_tool import(
    get_uuid
)
from utils.misc import get_current_time, time_to_utc
import api.user.user as APIUser

def check_notice_zone_scope(sender, notice_ids=None):
    
    ctx = context.instance()
    zone_id = sender["zone"]
    user_id = sender["owner"]
    scope_notice_ids = []
    
    if APIUser.is_global_admin_user(sender):
        if notice_ids:
            return notice_ids
        else:
            return []
    elif APIUser.is_admin_console(sender):
        
        ret = ctx.pgm.get_notice_pushs(notice_ids, user_id=user_id)
        if ret:
            scope_notice_ids = ret.keys()
            
    else:
        
        user_zones = ctx.pgm.get_user_zone_by_id(user_id)
        if not user_zones:
            return None
        zone_ids = user_zones.keys()
        # get public
        ret = ctx.pgm.get_notice_pushs(notice_ids, const.NOTICE_SCOPE_PUBLIC)
        if ret:
            scope_notice_ids.extend(ret.keys())

        # get part
        user_part_notice_ids = []
        for zone_id in zone_ids:
            ret = ctx.pgm.get_zone_notice(zone_id, notice_ids, user_scope=const.NOTICE_SCOPE_PUBLIC)
            if ret:
                for _id in ret:
                    if _id in scope_notice_ids:
                        continue
                    scope_notice_ids.append(_id)

            ret = ctx.pgm.get_zone_notice(zone_id, notice_ids, user_scope=const.NOTICE_SCOPE_PART)
            if ret:
                ret = ctx.pgm.get_user_notice(user_id, ret, zone_id)
                if ret:
                    for _id in ret:
                        if _id in user_part_notice_ids:
                            continue
                        user_part_notice_ids.append(_id)

        scope_notice_ids.extend(user_part_notice_ids)

    if not scope_notice_ids:
        return None

    return scope_notice_ids

def format_notice_push(sender, notice_push_set):
    
    ctx = context.instance()
    zone_id = sender.get("zone_id")
    
    notice_pushs = {}
    zone_infos = ctx.pgm.get_zones()
    
    for notice_id, notice_push in notice_push_set.items():
        
        ret = refresh_notice_status(notice_id)
        if isinstance(ret, Error):
            return ret
        scope = notice_push["scope"]

        if APIUser.is_normal_console(sender) and notice_push["force_read"]:
            notice_read = ctx.pgm.get_notice_push_read(notice_id, sender["owner"])
            if notice_read:
                notice_push["already_readed"] = 1

        if scope == const.NOTICE_SCOPE_PUBLIC:
            notice_pushs[notice_id] = notice_push
            continue
        
        desktop_users = {}
        ret = ctx.pgm.get_notice_user(notice_id)
        if ret:
            user_ids = ret.keys()
            user_column = ["user_name", "user_id", "user_dn"]
            user_group_column = ["user_group_name", "user_group_id", "user_group_dn"]
            ret = ctx.pgm.get_user_and_user_group(user_ids, user_column, user_group_column)
            if ret:
                desktop_users = ret

        if APIUser.is_global_admin_user(sender):

            notice_zones = ctx.pgm.get_notice_zone(notice_id)
            if notice_zones:
                for zone_id, notice_zone in notice_zones.items():
                    
                    zone = zone_infos.get(zone_id)
                    if zone:
                        notice_zone["zone_name"] = zone["zone_name"]

                    user_scope = notice_zone["user_scope"]
                    notice_zone["scope"] = user_scope
                    del notice_zone["user_scope"]
                    if user_scope == const.NOTICE_SCOPE_PUBLIC:
                        continue

                    notice_users = ctx.pgm.get_notice_user(notice_id, zone_id)
                    if not notice_users:
                        notice_users = {}
                    
                    for user_id, notice_user in notice_users.items():
                        
                        desktop_user = desktop_users.get(user_id)
                        if desktop_user:
                            notice_user.update(desktop_user)

                    notice_zone["user_ids"] = notice_users.values()

                notice_push["zone_scope"] = notice_zones.values()
            
            notice_pushs[notice_id] = notice_push
        
        elif APIUser.is_console_admin_user(sender):
            
            if notice_push["owner"] != sender["owner"]:
                continue
            
            notice_zones = ctx.pgm.get_notice_zone(notice_id, zone_id)
            if notice_zones:
                for zone_id, notice_zone in notice_zones.items():

                    zone = zone_infos.get(zone_id)
                    if zone:
                        notice_zone["zone_name"] = zone["zone_name"]

                    user_scope = notice_zone["user_scope"]
                    notice_zone["scope"] = user_scope
                    del notice_zone["user_scope"]
                    if user_scope == const.NOTICE_SCOPE_PUBLIC:
                        continue

                    notice_users = ctx.pgm.get_notice_user(notice_id, zone_id)
                    if not notice_users:
                        notice_users = {}
                    
                    for user_id, notice_user in notice_users.items():
                        
                        desktop_user = desktop_users.get(user_id)
                        if desktop_user:
                            notice_user.update(desktop_user)
                    
                    notice_zone["user_ids"] = notice_users.values()
            
                notice_push["zone_scope"] = notice_zones.values()
            notice_pushs[notice_id] = notice_push
    
    return notice_pushs

def set_notice_permanent_time(notice_id):
    
    ctx = context.instance()

    if not ctx.pg.batch_update(dbconst.TB_NOTICE_PUSH, {notice_id: {"expired_time": None, "execute_time": None}}):
        logger.error("modify notice expired time DB fail %s" % notice_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
    return None

def check_executime_and_expired_time(req):
    
    expired_time = req.get("expired_time")
    execute_time = req.get("execute_time")
    
    if expired_time:
        expired_time = time_to_utc(expired_time)
        req["expired_time"] = expired_time

    if execute_time:
        execute_time = time_to_utc(execute_time)
        req["execute_time"] = execute_time
    
    if not execute_time or not expired_time:
        return None
    
    if expired_time <= execute_time:
        logger.error("notice execute time %s and expired time %s dismatch %s" % (execute_time, expired_time))
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "expired_time")
    return

def build_notice_push(req):
    
    notice_type = req.get("notice_type")
    if not notice_type:
        req["notice_type"] = const.NOTICE_PUSH_TYPE_POST_LOGIN
    
    notice_level = req.get("notice_level")
    if not notice_level:
        req["notice_level"] = const.NOTICE_PUSH_LEVEL_NORMAL
    
    notice_push = {}
    notice_push_key =["title", "content", "scope", "notice_type", "notice_level", "expired_time", "execute_time", "force_read"]

    for key in notice_push_key:
        if key not in req:
            continue
        notice_push[key] = req[key]

    return notice_push

def check_set_notice_zone_user(sender, notice_id, zone_users):
    
    zone_id = sender["zone"]
    ctx = context.instance()
    
    new_zone_users = {}
    for zone_user in zone_users:
        zone_id = zone_user["zone_id"]
        new_zone_users[zone_id] = zone_user
    
    notice = ctx.pgm.get_notice_push(notice_id)
    if not notice:
        logger.error("no found notice %s" % notice_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, notice_id)

    ret = refresh_notice_status(notice_id)
    if isinstance(ret, Error):
        return ret

    if notice["owner"] != sender["owner"]:
        logger.error("zone owner %s dismatch notice user %s" % (notice["owner"], sender["owner"]))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_NOTICE_OWNER_DISMATCH, notice_id)

    if APIUser.is_console_admin_user(sender):
        if zone_id not in new_zone_users:
            logger.error("zone %s no found in zone_users" % zone_id)
            return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_NOTICE_NO_FOUND_ZONE_USER_CONFIG, notice_id)       
        return {zone_id: new_zone_users[zone_id]}

    return new_zone_users
    
def check_create_notice_push(sender, req):

    notice_type = req.get("notice_type", const.NOTICE_PUSH_TYPE_POST_LOGIN)
    if APIUser.is_console_admin_user(sender):
        if notice_type == const.NOTICE_PUSH_TYPE_PRE_LOGIN:
            return Error(ErrorCodes.PERMISSION_DENIED, 
                         ErrorMsg.ERR_MSG_NOTICE_PUSH_TYPE_DISMATCH_USER_ROLE, notice_type)
        
        req["scope"] = const.NOTICE_SCOPE_PART

    return None

def set_notice_zone(sender, notice_id):
    
    ctx = context.instance()
    zone_id = sender["zone"]
    
    ret = ctx.pgm.get_notice_zone(notice_id, zone_id)
    if ret:
        return None

    update_info = {"notice_id": notice_id, "zone_id": zone_id, "user_scope": const.NOTICE_SCOPE_PART}
    if not ctx.pg.insert(dbconst.TB_NOTICE_ZONE, update_info):
        logger.error("insert newly created radius service for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    return None

def create_notice_push(sender, req):

    ctx = context.instance()
    notice_id = get_uuid(UUID_TYPE_NOTICE_PUSH, ctx.checker)
    notice_info = build_notice_push(req)

    update_info = dict(
                      notice_id = notice_id,
                      status = const.NOTICE_STATUS_NORMAL,
                      create_time = get_current_time(),
                      owner = sender["owner"]
                      )
    update_info.update(notice_info)
    # register desktop group
    if not ctx.pg.insert(dbconst.TB_NOTICE_PUSH, update_info):
        logger.error("insert newly created notice push for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    ret = refresh_notice_status(notice_id)
    if isinstance(ret, Error):
        return ret
    
    scope = notice_info["scope"]
    if scope == const.NOTICE_SCOPE_PART and APIUser.is_console_admin_user(sender):
        ret = set_notice_zone(sender, notice_id)
        if isinstance(ret, Error):
            return ret

    return notice_id

def refresh_notice_status(notice_ids=None):
    
    ctx = context.instance()
    
    notices = ctx.pgm.get_notice_pushs(notice_ids)
    if not notices:
        return None
    
    for notice_id, notice in notices.items():
        expired_time = notice["expired_time"]
        execute_time = notice["execute_time"]
        
        status = const.NOTICE_STATUS_NORMAL
    
        if execute_time:
            status = const.NOTICE_STATUS_INEFFECTIVE
            _execute_time = execute_time.__format__('%Y-%m-%d %H:%M:%S')
            now = get_current_time()
            _now = now.__format__('%Y-%m-%d %H:%M:%S')   
            if _now > _execute_time:
                status = const.NOTICE_STATUS_NORMAL
    
        if expired_time:
            _expired_time = expired_time.__format__('%Y-%m-%d %H:%M:%S')
            now = get_current_time()
            _now = now.__format__('%Y-%m-%d %H:%M:%S')
    
            if _now >= _expired_time:
                status = const.NOTICE_STATUS_EXPIRED
    
        if status == notice["status"]:
            return None
        
        if not ctx.pg.batch_update(dbconst.TB_NOTICE_PUSH, {notice_id: {"status": status}}):
            logger.error("modify radius service update DB fail %s" % notice_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    return None


def refresh_notice_execute(notice_id):
    
    ctx = context.instance()
    
    notice = ctx.pgm.get_notice_push(notice_id)
    if not notice:
        return None

    execute_time = notice["execute_time"]
    if not execute_time:
        return None
    
    status = const.NOTICE_STATUS_INEFFECTIVE
    _execute_time = execute_time.__format__('%Y-%m-%d %H:%M:%S')
    now = get_current_time()
    _now = now.__format__('%Y-%m-%d %H:%M:%S')   
    if _now < _execute_time:
        status = const.NOTICE_STATUS_NORMAL
    
    if status == notice["status"]:
        return None
    
    if not ctx.pg.batch_update(dbconst.TB_NOTICE_PUSH, {notice_id: {"status": status}}):
        logger.error("refresh execute update DB fail %s" % notice_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    return None

def check_modify_notice_push_attributes(sender, notice_id):
    
    ctx = context.instance()
   
    notice = ctx.pgm.get_notice_push(notice_id)
    if not notice:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, notice_id)
    
    if APIUser.is_console_admin_user(sender):
        scope = notice["scope"]
        if scope == const.NOTICE_SCOPE_PUBLIC:
            return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
        if notice["owner"] != sender["owner"]:
            return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
    return notice
    
def modify_notice_push_attributes(notice_id, need_maint_columns):
    
    ctx = context.instance()
    if not ctx.pg.batch_update(dbconst.TB_NOTICE_PUSH, {notice_id: need_maint_columns}):
        logger.error("modify radius service update DB fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    notice = ctx.pgm.get_notice_push(notice_id)
    if not notice:
        return None    

    ret = refresh_notice_status(notice_id)
    if isinstance(ret, Error):
        return ret
    return None

def check_delete_notice(sender, notice_ids):
    
    ctx = context.instance()
    user_id = sender["owner"]
    notices = ctx.pgm.get_notice_pushs(notice_ids)
    if not notices:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, notice_ids)
    
    for _, notice in notices.items():
        owner = notice["owner"]
        if APIUser.is_console_admin_user(sender):
            if owner != user_id:
                return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, notice_ids)
    
    return notices

def delete_notice_pushs(notices):

    ctx = context.instance()
    for notice_id, notice in notices.items():
        scope = notice["scope"]
        conditions = {"notice_id": notice_id}
        if scope == const.NOTICE_SCOPE_PART:
            
            ctx.pg.base_delete(dbconst.TB_NOTICE_ZONE, conditions)
            ctx.pg.base_delete(dbconst.TB_NOTICE_USER, conditions)

        ctx.pg.base_delete(dbconst.TB_NOTICE_READ, conditions)
        ctx.pg.delete(dbconst.TB_NOTICE_PUSH, notice_id)

    return None

def set_notice_zone_scope(notice_id, zone_id, zone_user):
    
    ctx = context.instance()

    notice_zones = ctx.pgm.get_notice_zone(notice_id)
    if not notice_zones:
        notice_zones = {}
    notice_zone = notice_zones.get(zone_id)

    user_scope = zone_user.get("user_scope")
    user_ids = zone_user.get("user_ids")
    if not user_scope:
        if user_ids:
            user_scope = const.NOTICE_SCOPE_PART
        else:
            user_scope = const.NOTICE_SCOPE_PUBLIC
    
    if not notice_zone:
        update_info = {"notice_id": notice_id, "zone_id": zone_id, "user_scope": user_scope}
        if not ctx.pg.insert(dbconst.TB_NOTICE_ZONE, update_info):
            logger.error("insert newly created radius service for [%s] to db failed" % (update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    else:
        if notice_zone["user_scope"] != user_scope:
            condition = {"notice_id": notice_id, "zone_id": zone_id}
            if not ctx.pg.base_update(dbconst.TB_NOTICE_ZONE, condition, {"user_scope": user_scope}):
                logger.error("update TB_DESKTOP_GROUP_USER is_lock error")
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    ret = modify_notice_user_scope(notice_id, zone_id, user_ids)
    if isinstance(ret, Error):
        return ret

    return None

def clear_notice_zone_scope(notice_id, zone_ids=None):
    
    ctx = context.instance()
    
    conditions = {"notice_id": notice_id}
    if zone_ids:
        conditions["zone_id"] = zone_ids
    
    ret = ctx.pgm.get_notice_zone(notice_id, zone_ids)
    if not ret:
        return None
    
    for zone_id, _ in ret.items():
        conditions["zone_id"] = zone_id
        ctx.pg.base_delete(dbconst.TB_NOTICE_USER, conditions)
        ctx.pg.base_delete(dbconst.TB_NOTICE_ZONE, conditions)
    
    return None

def modify_notice_push_zone_user(sender, notice_id, zone_users, scope):
    
    ctx = context.instance()
    modify_zone_users = {}
    
    notice = ctx.pgm.get_notice_push(notice_id)
    if not notice:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, notice_id)
    
    if not scope:
        scope = notice["scope"]
    

    if scope == const.NOTICE_SCOPE_PUBLIC:
        clear_notice_zone_scope(notice_id)
    else:
        if APIUser.is_console_admin_user(sender):
            zone_id = sender["zone"]
            zone_user = zone_users.get(zone_id)
            if zone_user:            
                modify_zone_users[zone_id] = zone_user
    
        elif APIUser.is_global_admin_user(sender):
            modify_zone_users = zone_users

        for zone_id, zone_user in modify_zone_users.items():
    
            user_scope = zone_user["user_scope"]
            if user_scope != const.NOTICE_SCOPE_INVISIBLE:
                ret = set_notice_zone_scope(notice_id, zone_id, zone_user)
                if isinstance(ret, Error):
                    return ret
            else:
                ret = clear_notice_zone_scope(notice_id, zone_id)
                if isinstance(ret, Error):
                    return ret
    
    if scope != notice["scope"]:
        condition = {"notice_id": notice_id}
        if not ctx.pg.base_update(dbconst.TB_NOTICE_PUSH, condition, {"scope": scope}):
            logger.error("update TB_DESKTOP_GROUP_USER is_lock error")
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def modify_notice_user_scope(notice_id, zone_id, user_ids):

    ctx = context.instance()

    notice_zones = ctx.pgm.get_notice_zone(notice_id)
    if not notice_zones:
        notice_zones = {}
    notice_zone = notice_zones.get(zone_id)

    user_scope = notice_zone["user_scope"]
    if user_scope == const.NOTICE_SCOPE_PUBLIC:
       
        conditions = {"notice_id": notice_id, "zone_id": zone_id}
        ctx.pg.base_delete(dbconst.TB_NOTICE_USER, conditions)
        
        return None

    elif user_scope == const.NOTICE_SCOPE_PART:

        zone_users = ctx.pgm.get_zone_users(zone_id, user_ids, check_user=True)
        if not zone_users:
            zone_users = {}

        zone_user_group = ctx.pgm.get_zone_user_groups(zone_id, user_ids, check_user=True)
        if not zone_user_group:
            zone_user_group = {}

        zone_users.update(zone_user_group)
        
        new_user_ids = []
        delete_user_ids = []
        zone_user_ids = zone_users.keys()
        notice_user = ctx.pgm.get_notice_user(notice_id, zone_id)
        if not notice_user:
            new_user_ids = zone_user_ids
        
        else:
            for user_id in notice_user:
                if user_id not in zone_user_ids:
                    delete_user_ids.append(user_id)
            
            for user_id in zone_user_ids:
                if user_id not in notice_user:
                    new_user_ids.append(user_id)
        
        if new_user_ids:
            update_user = {}
            for user_id in new_user_ids:
                user_type = const.USER_TYPE_USER
                if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                    user_type = const.USER_TYPE_GROUP
                update_info = {
                    "zone_id": zone_id,
                    "notice_id": notice_id,
                    "user_id": user_id,
                    "user_type": user_type
                    }
                update_user[user_id] = update_info
            
            if not ctx.pg.batch_insert(dbconst.TB_NOTICE_USER, update_user):
                logger.error("insert newly created notice user for [%s] to db failed" % (update_user))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
        
        if delete_user_ids:
            conditions = {"notice_id": notice_id, "zone_id": zone_id, "user_id": delete_user_ids}
            ctx.pg.base_delete(dbconst.TB_NOTICE_USER, conditions)

    return None

def set_user_notice_read(notice_id, user_id):
        
    ctx = context.instance()
    
    desktop_users = ctx.pgm.get_desktop_users(user_id)
    if not desktop_users:
        return None
    
    desktop_user = desktop_users[user_id]
    
    notice_push = ctx.pgm.get_notice_push(notice_id)
    if not notice_push:
        return None
    
    force_read = notice_push.get("force_read")
    if not force_read:
        return None
    
    notice_read = ctx.pgm.get_notice_push_read(notice_id, user_id)
    if notice_read:
        return None
    
    update_read = {
        "notice_id": notice_id,
        "user_id": user_id,
        "user_name": desktop_user["user_name"]
        }
    
    if not ctx.pg.base_insert(dbconst.TB_NOTICE_READ, update_read):
        logger.error("insert newly created notice user for [%s] to db failed" % (update_read))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    return None
