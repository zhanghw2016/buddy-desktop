from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import constants as const
import db.constants as dbconst
from utils.id_tool import (
    UUID_TYPE_DESKTOP_USER, 
    UUID_TYPE_DESKTOP_OU,
    get_uuid,
    UUID_TYPE_DESKTOP_USER_GROUP
)
from utils.misc import get_current_time
import resource_control.auth.user_resource as UserResource

def delete_zone_desktop_user(zone_ids=None, user_ids=None):
    
    ctx = context.instance()
    conditions = {}
    if user_ids:
        conditions["user_id"] = user_ids
    
    if zone_ids:
        conditions["zone_id"] = zone_ids
    
    if not conditions:
        return None
    
    ctx.pg.base_delete(dbconst.TB_ZONE_USER, conditions)

    return None

def set_zone_desktop_user_status(zone_id, user_id, status):
    
    ctx = context.instance()
    conditions = {"zone_id": zone_id, "user_id": user_id}
    if not ctx.pg.base_update(dbconst.TB_ZONE_USER, conditions, {"status": status}):
        logger.error("update zone %s user %s status %s fail" % (zone_id, user_id, status))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def set_desktop_user_zone(auth_zone, user_ids):
    
    ctx = context.instance()
    
    auth_service_id = auth_zone["auth_service_id"]
    zone_id = auth_zone["zone_id"]
    
    zone_base_dn = ctx.auth.format_base_dn(auth_zone["base_dn"])
    check_ids = []
    
    desktop_users = {}
    ret = ctx.pgm.search_users(auth_service_id, base_dn=zone_base_dn, index_id=True, user_ids=user_ids)
    if ret:
        desktop_users = ret
        check_ids.extend(desktop_users.keys())
    
    zone_users = ctx.pgm.get_zone_users(zone_id, user_ids)
    if not zone_users:
        zone_users = {}
    check_ids.extend(zone_users.keys())
    check_ids = list(set(check_ids))

    delete_zone_users = []
    new_zone_users = {}

    # check zone user group
    for user_id in check_ids:
        desktop_user = desktop_users.get(user_id)
        zone_user = zone_users.get(user_id)
        
        if not desktop_user:
            delete_zone_users.append(user_id)
            continue
        
        if zone_user:
            continue

        user_info = {
                    "zone_id": zone_id,
                    "user_id": user_id,
                    'user_name': desktop_user["user_name"],
                    "role": const.USER_ROLE_NORMAL,
                    }
        new_zone_users[user_id] = user_info

    if new_zone_users:
        if not ctx.pg.batch_insert(dbconst.TB_ZONE_USER, new_zone_users):
            logger.error("insert newly created zone user for [%s] to db failed" % (new_zone_users))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    if delete_zone_users:
        delete_zone_desktop_user(zone_id, delete_zone_users)
    
    return new_zone_users.keys()

def add_auth_desktop_users(auth_service_id, auth_users):
    
    ctx = context.instance()
    update_users = {}
    
    user_names = auth_users.keys()
    
    desktop_users = ctx.pgm.get_auth_desktop_users(auth_service_id, user_names)
    if desktop_users:
        logger.error("add auth user fail, has the same user %s" % (desktop_users.keys()))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_USER_EXISTED_IN_AD, desktop_users.keys())
    
    for user_name, auth_user in auth_users.items():
        user_id = get_uuid(UUID_TYPE_DESKTOP_USER, ctx.checker, long_format=True)

        ou_dn = auth_user["ou_dn"]
        ou_dn = ou_dn.replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
        ou_dn = ou_dn.replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")
        user_dn = auth_user["user_dn"]
        user_dn = user_dn.replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
        user_dn = user_dn.replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")
        user_info = {
               "user_id": user_id,
               "auth_service_id": auth_service_id,
               "user_name": user_name,
               "object_guid": auth_user["object_guid"],
               "real_name": auth_user["real_name"],
               "description": auth_user['description'],
               "ou_dn": ou_dn,
               "user_dn": user_dn,
               'user_control': auth_user.get("user_control", 65536),
               "status": auth_user["status"],
                "email": auth_user.get("email", ''),
               "create_time": get_current_time(),
               "update_time": get_current_time()
            }
        update_users[user_id] = user_info
    
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_USER, update_users):
        logger.error("insert newly created desktop user for [%s] to db failed" % (update_users))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    user_ids = update_users.keys()
    return user_ids

def update_auth_desktop_users(users):
    
    ctx = context.instance()
    
    for user_id, update_info in users.items():
                
        user_name = update_info.get("user_name")
        if user_name:
            sync_auth_user_names(user_id, user_name)

        conditions = {}
        conditions["user_id"] = user_id
        if not ctx.pg.base_update(dbconst.TB_DESKTOP_USER, conditions, update_info):
            logger.error("update desktop %s user info %s fail" % (user_id, update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def check_auth_user_info(auth_user, desktop_user):
    
    check_user_keys = ['real_name', 'ou_dn', 'user_dn', 'user_control', 'user_name', 'ou_guid']
    update_user = {}
    
    for user_key in check_user_keys:
        if user_key not in auth_user:
            continue
        if auth_user[user_key] == desktop_user[user_key]:
            continue
        update_user[user_key] = auth_user[user_key]
    
    if "user_control" in update_user:
        status = int(update_user.get('user_control'))
        update_user['status'] = const.AUTH_USER_STATUS_DISABLED if status & const.AUTH_USER_ACCOUNT_CONTROL_ACCOUNTDISABLE > 0 else const.AUTH_USER_STATUS_ACTIVE
    
    return update_user

def delete_desktop_users(user_ids):
    
    ctx = context.instance()
    
    for user_id in user_ids:
        zone_users = ctx.pgm.get_user_zone_by_id(user_id)
        if not zone_users:
            continue
        
        for zone_id, _ in zone_users.items():
            sender = {"owner": user_id, "zone": zone_id}
            UserResource.check_auth_user_resource(sender, user_id)

    delete_zone_desktop_user(user_ids=user_ids)
    delete_user_group_users(user_ids=user_ids)

    conditions = {"user_id": user_ids}
    ctx.pg.base_delete(dbconst.TB_DESKTOP_USER, conditions)

def sync_auth_user_names(user_id, user_name):

    ctx = context.instance()
    for update_table, update_key in dbconst.UPDATE_AUTH_USER_NAMES.items():
        conditions = {update_key: user_id}
        update_info = {"user_name": user_name}
        ctx.pg.base_update(update_table, conditions, update_info)

    return None

def sync_auth_users(auth_service_id, ou_dn, user_names=None, old_ou_dn=None, old_name=None):

    ctx = context.instance()
    if user_names and not isinstance(user_names, list):
        user_names = [user_names]

    auth_service = ctx.pgm.get_auth_service(auth_service_id)
    if not auth_service:
        return None

    # get auth user
    ret = ctx.auth.get_auth_users(auth_service_id, ou_dn=ou_dn, user_names=user_names)
    if isinstance(ret, Error):
        return ret
    auth_users = ret
    if not auth_users:
        auth_users = {}
        
    if not old_ou_dn:
        old_ou_dn = ou_dn
    
    if not old_name:
        old_name = user_names
    # get desktop user
    desktop_users = ctx.pgm.search_users(auth_service_id, base_dn=old_ou_dn, user_names=old_name, index_guid=True)
    if not desktop_users:
        desktop_users = {}

    new_users = {}
    update_users = {}
    delete_users = []
    user_ids = []
    user_guids = []

    for user_name, auth_user in auth_users.items():
        object_guid = auth_user["object_guid"]
        user_guids.append(object_guid)

        desktop_user = desktop_users.get(object_guid)
        if not desktop_user:
            guid_users = ctx.pgm.search_users(auth_service_id, index_guid=True, object_guids=object_guid)
            if not guid_users:
                desktop_user = {}
            else:
                desktop_user = guid_users[object_guid]
                desktop_users[object_guid] = desktop_user

            if not desktop_user:
                new_users[user_name] = auth_user
                continue

        user_id = desktop_user["user_id"]
        ret = check_auth_user_info(auth_user, desktop_user)
        if not ret:
            continue

        user_id = desktop_user["user_id"]
        update_users[user_id] = ret

    for guid, desktop_user in desktop_users.items():

        if guid in user_guids:
            continue
        domain_dn = ctx.auth.get_domain_dn(auth_service["domain"])
        ret = ctx.auth.get_auth_users(auth_service_id, ou_dn = domain_dn, object_guid=guid, index_uuid=True)
        if ret:
            auth_user = ret[guid]
            user_id = desktop_user["user_id"]
            ret = check_auth_user_info(auth_user, desktop_user)
            if not ret:
                continue
    
            user_id = desktop_user["user_id"]
            update_users[user_id] = ret
        else:
            user_id = desktop_user["user_id"]
            delete_users.append(user_id)

    if delete_users:
        delete_desktop_users(delete_users)

    if new_users:
        ret = add_auth_desktop_users(auth_service_id, new_users)
        if isinstance(ret, Error):
            return ret
        user_ids.extend(ret)

    if update_users:
        ret = update_auth_desktop_users(update_users)
        if isinstance(ret, Error):
            return ret

    auth_zones = {}
    ret = ctx.pgm.get_auth_zones(auth_service_id)
    if ret:
        auth_zones = ret

    for _, auth_zone in auth_zones.items():
        ret = set_desktop_user_zone(auth_zone, user_ids)
        if isinstance(ret, Error):
            return ret

    return None

def add_auth_desktop_ou(auth_service_id, auth_ous):
    
    ctx = context.instance()
    ou_guids = []
    for ou_dn, auth_ou in auth_ous.items():
        object_guid = auth_ou["object_guid"]
        ou_guids.append(object_guid)
    
    existed_ous = ctx.pgm.search_user_ous(auth_service_id, index_guid=True, object_guid=ou_guids)
    if not existed_ous:
        existed_ous = {}
    
    new_ous = {}
    for ou_dn, auth_ou in auth_ous.items():
        object_guid = auth_ou["object_guid"]
        if object_guid in existed_ous:
            continue

        user_ou_id = get_uuid(UUID_TYPE_DESKTOP_OU, ctx.checker, long_format=True)
        base_dn = auth_ou["base_dn"]
        base_dn = base_dn.replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
        base_dn = base_dn.replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")
        ou_dn = ou_dn.replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
        ou_dn = ou_dn.replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")
        ou_info = {
               "user_ou_id": user_ou_id,
               "auth_service_id": auth_service_id,
               "ou_name": auth_ou["ou_name"],
               "object_guid": auth_ou["object_guid"],
               "description": auth_ou['description'],
               "ou_dn": ou_dn,
               "base_dn": base_dn,
               "create_time": get_current_time(),
               "update_time": get_current_time()
            }
        new_ous[user_ou_id] = ou_info
    
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_USER_OU, new_ous):
        logger.error("insert newly created desktop ou for [%s] to db failed" % (new_ous))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return new_ous.keys()

def check_update_auth_ou(auth_ou, desktop_ou):

    check_key = ["ou_name", "ou_dn", "base_dn", "description"]
    update_ou = {}
    for key in check_key:
        if key not in auth_ou:
            continue
        if auth_ou[key] == desktop_ou[key]:
            continue
        update_ou[key] = auth_ou[key]

    return update_ou

def delete_desktop_ous(delete_ous):

    ctx = context.instance()
    
    for guid, _ in delete_ous.items():

        for table, key_value in dbconst.UPDATE_AUTH_BASE_DN.items():
    
            for key, value in key_value.items():
                conditions = {key: guid}
                ret = ctx.pg.get_all(table, conditions)
                if ret:
                    ctx.pg.base_update(table, conditions, {value: "", key: ""})

    conditions = {"user_ou_id": delete_ous.values()}
    ctx.pg.base_delete(dbconst.TB_DESKTOP_USER_OU, conditions)

def update_auth_ou_dn(update_ous):
    
    ctx = context.instance()
   
    for guid, update_info in update_ous.items():
        
        ou_dn = update_info.get("ou_dn")
        if ou_dn:
            for table, key_value in dbconst.UPDATE_AUTH_BASE_DN.items():

                for key, value in key_value.items():
                    conditions = {key: guid}
                    ctx.pg.base_update(table, conditions, {value: ou_dn})

        conditions = {"object_guid": guid}
        if not ctx.pg.base_update(dbconst.TB_DESKTOP_USER_OU, conditions, update_info):
            logger.error("update desktop %s ou info %s fail" % (conditions, update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def check_auth_ou_base_dn(auth_service, check_dn):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    ou_name, base_dn = ctx.auth.get_base_dn(check_dn)
    
    desktop_ous = ctx.pgm.search_user_ous(base_dn, auth_service_id, ou_names=ou_name)
    if not desktop_ous or check_dn not in desktop_ous:
        return check_dn

    desktop_ou = desktop_ous[check_dn]

    auth_ous = ctx.auth.get_auth_ous(auth_service_id, base_dn=base_dn, ou_names=ou_name)
    if not auth_ous or isinstance(auth_ous, Error):
        auth_ous = {}
    
    auth_ou = auth_ous.get(check_dn)
    if auth_ou and desktop_ou["object_guid"] == auth_ou.get("object_guid", ""):
        return check_dn

    domain = auth_service["domain"]
    domian_dn = ctx.auth.get_domain_dn(domain)
    ret = ctx.auth.get_auth_ous(auth_service_id, base_dn=domian_dn)
    if isinstance(ret, Error):
        return ret
    domain_auth_ous = ret
    
    new_ou_dn = None
    for _, _ou in domain_auth_ous.items():
        
        if _ou["object_guid"] == desktop_ou["object_guid"]:
            new_ou_dn = _ou["ou_dn"]
            break
        
    return new_ou_dn

def sync_auth_ous(auth_service_id, base_dn, old_ou_dn=None):
    
    ctx = context.instance()
    
    auth_ous = {}
    ret = ctx.auth.get_auth_ous(auth_service_id, base_dn=base_dn)
    if isinstance(ret, Error):
        return ret
    if ret:
        auth_ous = ret
    
    if not old_ou_dn:
        old_ou_dn = base_dn
    
    desktop_ous = ctx.pgm.search_user_ous(old_ou_dn, auth_service_id, index_guid=True)
    if not desktop_ous:
        desktop_ous = {}

    auth_ou_guids = []
    update_ous = {}
    new_ous = {}
    delete_ous = {}
    for ou_dn, auth_ou in auth_ous.items():
        
        object_guid = auth_ou["object_guid"]
        auth_ou_guids.append(object_guid)

        desktop_ou = desktop_ous.get(object_guid)
        if not desktop_ou:

            uuid_desktop_ous = ctx.pgm.search_user_ous(auth_service_id, index_guid=True, object_guid=object_guid)
            if not uuid_desktop_ous:
                desktop_ou = {}
            else:
                desktop_ou = uuid_desktop_ous[object_guid]
                desktop_ous[object_guid] = desktop_ou

            if not desktop_ou:
                new_ous[ou_dn] = auth_ou
                continue

        ret = check_update_auth_ou(auth_ou, desktop_ou)
        if ret:
            update_ous[object_guid] = ret

    for guid, desktop_ou in desktop_ous.items():
        user_ou_id = desktop_ou["user_ou_id"]
        if guid and guid not in auth_ou_guids:
            delete_ous[guid] = user_ou_id

    if delete_ous:
        delete_desktop_ous(delete_ous)

    if new_ous:
        ret = add_auth_desktop_ou(auth_service_id, new_ous)
        if isinstance(ret, Error):
            return ret

    if update_ous:
        ret = update_auth_ou_dn(update_ous)
        if isinstance(ret, Error):
            return ret

    return None

def set_desktop_user_group_zone(auth_zone, user_group_ids=None):
    
    ctx = context.instance()
    
    auth_service_id = auth_zone["auth_service_id"]
    zone_id = auth_zone["zone_id"]

    if user_group_ids and not isinstance(user_group_ids, list):
        user_group_ids = [user_group_ids]

    zone_base_dn = ctx.auth.format_base_dn(auth_zone["base_dn"])
    check_ids = []
    
    desktop_user_groups = {}
    if not user_group_ids:
        ret = ctx.pgm.search_user_groups(auth_service_id, base_dn=zone_base_dn, index_id=True)
        if ret:
            desktop_user_groups = ret
            user_group_ids = ret.keys()
    else:
        desktop_user_groups = ctx.pgm.get_desktop_user_groups(auth_service_id, user_group_ids)
        if not desktop_user_groups:
            desktop_user_groups = {}

    check_ids.extend(desktop_user_groups.keys())

    zone_user_groups = ctx.pgm.get_zone_user_groups(zone_id, user_group_ids)
    if not zone_user_groups:
        zone_user_groups = {}
    check_ids.extend(zone_user_groups.keys())

    check_ids = list(set(check_ids))
    
    delete_zone_groups = []
    new_zone_groups = {}
    # check zone user group
    for user_group_id in check_ids:

        if user_group_id not in desktop_user_groups:
            delete_zone_groups.append(user_group_id)
            continue
        
        if user_group_id not in zone_user_groups:
            new_zone_groups[user_group_id] = {"zone_id": zone_id,
                                              "user_group_id": user_group_id,}

    if new_zone_groups:
        if not ctx.pg.batch_insert(dbconst.TB_ZONE_USER_GROUP, new_zone_groups):
            logger.error("insert newly created zone user group for [%s] to db failed" % (new_zone_groups))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    if delete_zone_groups:
        delete_zone_desktop_user_group(zone_id, delete_zone_groups)

    return None

def add_auth_desktop_user_group(auth_service_id, auth_user_groups):

    ctx = context.instance()
    
    user_groups = {}
    for user_group_dn, auth_user_group in auth_user_groups.items():
    
        user_group_id = get_uuid(UUID_TYPE_DESKTOP_USER_GROUP, ctx.checker, long_format=True)
        
        user_group_dn = user_group_dn.replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
        user_group_dn = user_group_dn.replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")
        base_dn = auth_user_group["base_dn"]
        base_dn = base_dn.replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
        base_dn = base_dn.replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")
        
        user_group_info = {
               "user_group_id": user_group_id,
               "auth_service_id": auth_service_id,
               "user_group_name": auth_user_group["user_group_name"],
               "object_guid": auth_user_group["object_guid"],
               "description": auth_user_group.get('description', ""),
               "user_group_dn": user_group_dn,
               "base_dn": base_dn,
               "create_time": get_current_time(),
               "update_time": get_current_time()
            }
        user_groups[user_group_id] = user_group_info
    
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_USER_GROUP, user_groups):
        logger.error("insert newly created desktop user group for [%s] to db failed" % (user_groups))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    user_group_ids = user_groups.keys()
    return user_group_ids

def delete_user_group_users(user_group_id=None, user_ids=None):
    
    ctx = context.instance()
    conditions = {}
    if user_group_id:
        conditions["user_group_id"] = user_group_id
    if user_ids:
        conditions["user_id"] = user_ids
    
    if not conditions:
        return None

    ctx.pg.base_delete(dbconst.TB_DESKTOP_USER_GROUP_USER, conditions)

def sync_auth_user_group_user(user_group_id):
    
    ctx = context.instance()

    desktop_user_group = ctx.pgm.get_desktop_user_group(user_group_id)
    if not desktop_user_group:
        delete_user_group_users(user_group_id)
        return None

    group_user_ids = ctx.pgm.get_desktop_user_form_user_group(user_group_id)
    if not group_user_ids:
        group_user_ids = []

    auth_service_id = desktop_user_group["auth_service_id"]
    user_group_dn = desktop_user_group["user_group_dn"]
    user_group_name, base_dn = ctx.auth.get_base_dn(user_group_dn)

    ret = ctx.auth.get_auth_user_groups(auth_service_id, base_dn, user_group_name)
    if isinstance(ret, Error):
        return ret

    if not ret:
        auth_user_group = {}
    else:
        auth_user_group = ret[user_group_dn]

    member_user_dns = auth_user_group.get("member")
    if not member_user_dns:
        member_user_dns = []
    
    desktop_users = ctx.pgm.get_user_by_user_dn(auth_service_id, member_user_dns)
    if not desktop_users:
        desktop_users = {}

    desktop_user_ids = []
    
    new_group_users = {}
    for _, user in desktop_users.items():
        user_id = user["user_id"]
        user_name = user["user_name"]
        desktop_user_ids.append(user_id)
        if user_id not in group_user_ids:
            new_group_users[user_id] = {"user_id": user_id, "user_group_id": user_group_id, "user_name":user_name}
    
    del_group_users = []
    for user_id in group_user_ids:
        if user_id not in desktop_user_ids:
            del_group_users.append(user_id)

    if del_group_users:
        delete_user_group_users(user_group_id, del_group_users)

    if new_group_users:
        if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_USER_GROUP_USER, new_group_users):
            logger.error("user group user insert new db fail %s" % new_group_users)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def check_update_auth_user_group(auth_user_group, desktop_user_group):

    check_key = ["user_group_name", "description", "base_dn", "user_group_dn"]

    update_user_group = {}
    for key in check_key:
        if key not in auth_user_group:
            continue

        if auth_user_group[key] == desktop_user_group[key]:
            continue

        update_user_group[key] = auth_user_group[key]

    return update_user_group

def delete_zone_desktop_user_group(zone_id, user_group_ids):
    
    ctx = context.instance()
    conditions = {"zone_id": zone_id, "user_group_id": user_group_ids}
    ctx.pg.base_delete(dbconst.TB_ZONE_USER_GROUP, conditions)

    return None

def delete_desktop_user_group(user_group_ids):
    ctx = context.instance()
    
    for user_group_id in user_group_ids:

        zone_users = ctx.pgm.get_user_group_zone_by_id(user_group_id)
        if not zone_users:
            zone_users = {}
        for zone_id, user_group_id in zone_users.items():
            sender = {"zone": zone_id}
            UserResource.check_auth_user_group_resource(sender, user_group_id)
        delete_user_group_users(user_group_id)

    conditions = {"user_group_id": user_group_ids}
    ctx.pg.base_delete(dbconst.TB_DESKTOP_USER_GROUP, conditions)
    
    return None

def sync_auth_user_group(auth_service_id, ou_dn, user_group_names=None, old_ou_dn=None, old_group_name=None):

    ctx = context.instance()
    
    if user_group_names and not isinstance(user_group_names, list):
        user_group_names = [user_group_names]

    ret = ctx.auth.get_auth_user_groups(auth_service_id, base_dn=ou_dn, user_group_names=user_group_names)
    if isinstance(ret, Error):
        return ret
    auth_user_groups = ret
    if not auth_user_groups:
        auth_user_groups = {}
    
    if not old_ou_dn:
        old_ou_dn = ou_dn
    
    if not old_group_name:
        old_group_name = user_group_names
    
    desktop_user_groups = ctx.pgm.search_user_groups(auth_service_id, old_ou_dn, old_group_name, index_guid=True)
    if not desktop_user_groups:
        desktop_user_groups = {}
       
    user_group_ids = []
    user_group_guids = []
    new_user_groups = {}
    update_user_groups = {}
    delete_user_groups = []

    for user_group_dn, auth_user_group in auth_user_groups.items():
        
        object_guid = auth_user_group["object_guid"]
        user_group_guids.append(object_guid)
        
        desktop_user_group = desktop_user_groups.get(object_guid)
        if not desktop_user_group:
            guid_user_groups = ctx.pgm.search_user_groups(auth_service_id, index_guid=True, object_guids=object_guid)
            if not guid_user_groups:
                desktop_user_group = {}
            else:
                desktop_user_group = guid_user_groups[object_guid]
                desktop_user_groups[object_guid] = desktop_user_group

            if not desktop_user_group:
                new_user_groups[user_group_dn] = auth_user_group
                continue

        ret = check_update_auth_user_group(auth_user_group, desktop_user_group)
        if ret:
            update_user_groups[object_guid] = ret
    
    for guid, desktop_user_group in desktop_user_groups.items():
        
        user_group_id = desktop_user_group["user_group_id"]
        if guid not in user_group_guids:
            delete_user_groups.append(user_group_id)

    if delete_user_groups:
        delete_desktop_user_group(delete_user_groups)
        user_group_ids.extend(delete_user_groups)

    if new_user_groups:
        ret = add_auth_desktop_user_group(auth_service_id, new_user_groups)
        if isinstance(ret, Error):
            return ret

        user_group_ids.extend(ret)
    
    if update_user_groups:
        for object_guid, update_info in update_user_groups.items():
            conditions = {}
            conditions["object_guid"] = object_guid
            if not ctx.pg.base_update(dbconst.TB_DESKTOP_USER_GROUP, conditions, update_info):
                logger.error("update desktop %s user group info %s fail" % (conditions, update_info))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    auth_zones = ctx.pgm.get_auth_zones(auth_service_id)
    if not auth_zones:
        auth_zones = {}
    # sync zone user group
    for _, auth_zone in auth_zones.items():

        ret = set_desktop_user_group_zone(auth_zone, user_group_ids)
        if isinstance(ret, Error):
            return ret

    desktop_user_groups = ctx.pgm.search_user_groups(auth_service_id, ou_dn, user_group_names, index_id=True)
    if not desktop_user_groups:
        desktop_user_groups = {}
    
    for user_group_id, _ in desktop_user_groups.items():
        ret = sync_auth_user_group_user(user_group_id)
        if isinstance(ret, Error):
            return ret

    return user_group_ids
