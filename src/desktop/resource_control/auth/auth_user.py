
from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import constants as const
import db.constants as dbconst
import api.user.user as APIUser
import resource_control.auth.sync_auth_user as SyncAuthUser
import resource_control.auth.auth_service as AuthService

import api.auth.auth_const as AuthConst
import resource_control.user.apply_approve as ApplyApprove
import datetime
from utils.misc import get_current_time

def format_auth_users(auth_service_id, auth_user_set, syn_desktop=0):
    ctx = context.instance()
    
    if not auth_user_set:
        return None
    
    user_names = auth_user_set.keys()
    desktop_users = ctx.pgm.get_auth_desktop_users(auth_service_id, user_names, index_guid=True)
    if not desktop_users:
        desktop_users = {}

    desktop_keys = ["user_id"]
    
    syn_desktop_guids = []
    auth_user_guids = {}
    for user_name, user in auth_user_set.items():
        object_guid = user["object_guid"]
        auth_user_guids[object_guid] = user_name
        desktop_user = desktop_users.get(object_guid)
        if not desktop_user:
            if syn_desktop:
                syn_desktop_guids.append(object_guid)
            continue

        user_id = desktop_user.get("user_id")
        if user_id:
            ret = ctx.pgm.get_user_group_detail(user_id)
            if not ret:
                ret = {}
            
            user_group_ids = ret.keys()
            if user_group_ids:
                ret = ctx.pgm.get_user_group_info(user_group_ids)
                
                user["user_groups"] = ret.values()

        ret = ctx.auth.check_user_change_password(user)
        if isinstance(ret, Error):
            user["account_control"] = const.CHANGE_PASSWORD
        else:
            user["account_control"] = const.DONT_CHNAGE_PASSWORD
        
        for key in desktop_keys:
            if key not in desktop_user:
                continue
            
            user[key] = desktop_user[key]
            user["in_apply_group"] = ApplyApprove.user_is_in_apply_group(user["user_id"])
            user["in_approve_group"] = ApplyApprove.user_is_in_approve_group(user["user_id"])
    
    if syn_desktop_guids:
        for guid in syn_desktop_guids:
            user_name = auth_user_guids.get(guid)
            if not user_name:
                continue
            del auth_user_set[user_name]
    
    return auth_user_set

def format_auth_user_ous(auth_service, auth_ou_set, syn_desktop=1):
    ctx = context.instance()
    
    auth_service_type = auth_service["auth_service_type"]
    if not auth_ou_set:
        return None
    
    syn_desktop_guids = []
    auth_ou_guids = {}
    desktop_ous = ctx.pgm.get_desktop_user_ous(auth_ou_set.keys(), index_guid=True)
    if not desktop_ous:
        desktop_ous = {}

    for ou_dn,ou in auth_ou_set.items():
        
        object_guid = ou["object_guid"]
        auth_ou_guids[object_guid] = ou_dn
        desktop_ou = desktop_ous.get(object_guid)
        if not desktop_ou:
            if syn_desktop:
                syn_desktop_guids.append(object_guid)
            continue
        ou["user_ou_id"] = desktop_ou["user_ou_id"]
        ou["auth_service_type"] = auth_service_type
    
    if syn_desktop_guids:
        for guid in syn_desktop_guids:
            ou_dn = auth_ou_guids.get(guid)
            if not ou_dn:
                continue
            del auth_ou_set[ou_dn]
    return None

def check_auth_service_permission(auth_service, check_sync=True, check_password=False):
    
    auth_service_name = auth_service["auth_service_name"]
    auth_service_id = auth_service["auth_service_id"]
    is_sync = auth_service["is_sync"]
    if check_sync and not is_sync:
        logger.error("auth service readonly %s" % auth_service_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_AUTH_SERVICE_READONLY, auth_service_name if auth_service_name else auth_service_id)
    
    modify_password = auth_service["modify_password"]
    if check_password and not modify_password:
        logger.error("auth service cant modify password %s" % auth_service_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_AUTH_SERVICE_CANT_MODIFY_PASSWORD, auth_service_name if auth_service_name else auth_service_id)
    
    return None

def check_auth_user_name_vaild(auth_service_id, user_name):

    ctx = context.instance()
    
    auth_service = ctx.pgm.get_auth_service(auth_service_id)
    if not auth_service:
        logger.error("no found auth service %s" % (auth_service_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_AUTH_SERVICE_NO_FOUND, auth_service_id)
    
    domain = auth_service["domain"]
    domain_dn = ctx.auth.get_domain_dn(domain)
    # check the same user
    ret = ctx.auth.get_auth_users(auth_service_id, ou_dn= domain_dn,user_names=user_name)
    if isinstance(ret, Error):
        return ret
    if ret:
        logger.error("user name [%s] existed in ad server" % user_name)
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_USER_EXISTED_IN_AD, user_name)
    
    # check the same user group
    ret = ctx.auth.get_auth_user_groups(auth_service_id, base_dn =domain_dn, user_group_names=user_name)
    if isinstance(ret, Error):
        return ret
    if ret:
        logger.error("user group [%s] existed in ad server" % user_name)
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_USER_GROUP_EXISTED_IN_AD, user_name)
    
    # check global admin user
    ret = ctx.pgm.get_global_admin_user(user_names=user_name, index_name=True)
    if ret:
        logger.error("global user [%s] existed in ad server" % user_name)
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_GLOBAL_USER_EXISTED_IN_AD, user_name)

    return None

def check_auth_cn_name_vaild(auth_service_id, user_name, ou_dn):

    ctx = context.instance()
    if not user_name:
        return None
    
    ret = ctx.auth.get_auth_users(auth_service_id, ou_dn, cn_name=user_name, scope=0)
    if isinstance(ret, Error):
        return ret
    if ret:
        logger.error("user display name [%s] existed in ad server" % user_name)
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_THE_SAME_OU_CANT_EXISTED_THE_SAME_REAL_NAME, user_name)

    ret = ctx.auth.get_auth_ous(auth_service_id, ou_dn, ou_names=user_name, scope=0)
    if isinstance(ret, Error):
        return ret
    if ret:
        logger.error("user ou [%s] existed in ad server" % user_name)
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_USER_EXISTED_IN_AD, user_name)

    ret = ctx.auth.get_auth_user_groups(auth_service_id, user_group_names=user_name)
    if isinstance(ret, Error):
        return ret
    if ret:
        logger.error("user group [%s] existed in ad server" % user_name)
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_USER_GROUP_EXISTED_IN_AD, user_name)
    
    return None

def check_add_auth_user(auth_service_id, ou_dn, user_name, cn_name=None):
    
    if not cn_name:
        cn_name = user_name

    ret = check_auth_user_name_vaild(auth_service_id, user_name)
    if isinstance(ret, Error):
        return ret
        
    ret = check_auth_cn_name_vaild(auth_service_id, cn_name, ou_dn)
    if isinstance(ret, Error):
        return ret

    return None

def check_auth_user_vaild(auth_service_id, user_names):

    ctx = context.instance()
    
    if not isinstance(user_names, list):
        user_names = [user_names]

    ret = ctx.auth.get_auth_users(auth_service_id, user_names=user_names)
    if isinstance(ret, Error):
        return ret
    
    auth_users = ret if ret is not None else {}

    for user_name in user_names:
        if user_name not in auth_users:
            logger.error("user %s not found" % user_name)
            return Error(ErrorCodes.USER_NOT_FOUND,
                         ErrorMsg.ERR_MSG_USER_NOT_FOUND, user_name)
    return auth_users

def check_auth_user_group_vaild(auth_service_id, user_group_dns):

    ctx = context.instance()
    
    if not isinstance(user_group_dns, list):
        user_group_dns = [user_group_dns]
    
    ret = ctx.pgm.get_desktop_user_groups(auth_service_id, user_group_dns=user_group_dns, index_dn=True)
    if isinstance(ret, Error):
        return ret
    
    auth_user_groups = ret if ret is not None else {}
    
    for user_group_dn in user_group_dns:
        if user_group_dn not in auth_user_groups:
            logger.error("user group %s not found" % user_group_dn)
            return Error(ErrorCodes.USER_NOT_FOUND,
                         ErrorMsg.ERR_MSG_USER_NOT_FOUND, user_group_dn)

    return auth_user_groups

def get_auth_user_id(auth_service, user_name):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    ret = ctx.pgm.get_user_id_by_user_name(user_name, auth_service_id)
    if not ret:
        return None
    
    return ret

def create_auth_user(auth_service, base_dn, req, is_sync=True):

    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]

    ret = ctx.auth.create_auth_user(auth_service_id, base_dn, req)
    if isinstance(ret, Error):
        return ret
    user_dn = ret
    
    if not is_sync:
        return user_dn
    
    _, base_dn = ctx.auth.get_base_dn(user_dn)
    user_name = req["user_name"]

    ret = SyncAuthUser.sync_auth_users(auth_service_id, base_dn, user_name)
    if isinstance(ret, Error):
        return ret

    return user_dn

def modify_desktop_user_attributes(auth_service_id, user_name, need_maint_columns):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_user_by_user_names(user_name, auth_service_id)
    if not ret:
        return None
    
    user_id = ret[user_name]
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_USER, {user_id: need_maint_columns}):
        logger.error("modify desktop user attribute update DB fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)      
    return user_id

def modify_auth_user_attributes(auth_service, auth_user, need_maint_columns):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    user_dn = auth_user["user_dn"]

    ret = ctx.auth.modify_auth_user(auth_service_id, user_dn, need_maint_columns)
    if isinstance(ret, Error):
        return ret
    
    _, ou_dn = ctx.auth.get_base_dn(user_dn)
    user_name = auth_user["user_name"]
    ret = SyncAuthUser.sync_auth_users(auth_service_id, ou_dn, user_name)
    if isinstance(ret, Error):
        return ret
    
    return user_name

def delete_auth_users(auth_service, user_names):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    ret = ctx.auth.delete_auth_users(auth_service_id, user_names)
    if isinstance(ret, Error):
        return ret

    ret = SyncAuthUser.sync_auth_users(auth_service_id, auth_service["base_dn"], user_names)
    if isinstance(ret, Error):
        return ret

    return user_names

def modify_auth_user_password(auth_service, user_name, old_password, new_password):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    ret = ctx.auth.modify_auth_user_password(auth_service_id, user_name, old_password, new_password)
    if isinstance(ret, Error):
        return ret

    return user_name

def reset_auth_user_password(auth_service, user_name, password):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    ret = ctx.auth.reset_auth_user_password(auth_service_id, user_name, password)
    if isinstance(ret, Error):
        return ret
    
    return user_name

def create_auth_ou(auth_service, ou_name, base_dn=None, description=None):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    attrs = {"ou": str(ou_name)}
    if description:
        attrs["description"] = str(description)

    if not base_dn:
        base_dn = auth_service["base_dn"]
    
    ret = ctx.auth.create_auth_ou(auth_service_id, base_dn, attrs)
    if isinstance(ret, Error):
        return ret
    ou_dn = ret
    
    ret = SyncAuthUser.sync_auth_ous(auth_service_id, ou_dn)
    if isinstance(ret, Error):
        return ret

    return ou_dn

def modify_auth_ou_attributes(auth_service, ou_dn, need_maint_columns):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]

    ret = ctx.auth.modify_auth_ou(auth_service_id, ou_dn, need_maint_columns)
    if isinstance(ret, Error):
        return ret
    dn = ret

    ret = SyncAuthUser.sync_auth_ous(auth_service_id, ou_dn)
    if isinstance(ret, Error):
        return ret
    return dn
    
def delete_auth_ou(auth_service, ou_dn):

    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]

    ret = AuthService.refresh_auth_service(auth_service, ou_dn)
    if isinstance(ret, Error):
        return ret

    ret = ctx.pgm.get_ou_resource(auth_service_id, ou_dn)
    if ret:
        ou_name, _ = ctx.auth.get_base_dn(ou_dn)
        logger.error("ou has resource cant delete %s" % ou_name)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_OU_HAS_RESOURCE_CANT_DELETE, ou_name)

    ret = ctx.auth.delete_auth_ous(auth_service_id, ou_dn)
    if isinstance(ret, Error):
        return ret
    
    _, base_dn = ctx.auth.get_base_dn(ou_dn)
    ret = AuthService.refresh_auth_service(auth_service, base_dn)
    if isinstance(ret, Error):
        return ret

    return None

def change_auth_user_ou_dn(auth_service, new_ou_dn, auth_users):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    ou_dns = []
    _, base_dn = ctx.auth.get_base_dn(new_ou_dn)
    ou_dns.append(base_dn)
    
    user_dns = {}
    for user_name, auth_user in auth_users.items():
        
        user_dn = auth_user["user_dn"]
        _, base_dn = ctx.auth.get_base_dn(user_dn)
        if base_dn not in ou_dns:
            ou_dns.append(base_dn)
        
        ret = ctx.auth.change_auth_user_ou_dn(auth_service_id, new_ou_dn, user_dn)
        if isinstance(ret, Error):
            return ret
        new_user_dn = ret
        user_dns[user_name] = new_user_dn
    
    base_root_dn = ctx.auth.get_root_base_dn(ou_dns)

    ret = AuthService.refresh_auth_service(auth_service, base_root_dn)
    if isinstance(ret, Error):
        return None

    return user_dns

def format_user_groups(auth_service_id, auth_user_group_set, syn_desktop=0):
    
    ctx = context.instance()

    desktop_user_groups = ctx.pgm.get_desktop_user_groups(auth_service_id, user_group_dns=auth_user_group_set.keys(), index_guid=True)
    if not desktop_user_groups:
        desktop_user_groups = {}
    
    syn_desktop_guids = []
    user_group_guids = {}
    for user_group_dn, user_group in auth_user_group_set.items():
        
        object_guid = user_group["object_guid"]
        user_group_guids[object_guid] = user_group_dn
        desktop_user_group = desktop_user_groups.get(object_guid)
        if not desktop_user_group:
            if syn_desktop:
                syn_desktop_guids.append(object_guid)
            continue
        user_group_id = desktop_user_group["user_group_id"]
        user_group["user_group_id"] = user_group_id
        
        ret = ctx.pgm.get_user_group_user(user_group_id)
        if not ret:
            ret = {}

        user_ids = ret.keys()
        if user_ids:
            ret = ctx.pgm.get_desktop_users(user_ids)
            user_group["users"] = ret.values() if ret else []
        else:
            user_group["users"] = []

    if syn_desktop_guids:
        for guid in syn_desktop_guids:
            user_group_dn = user_group_guids.get(guid)
            if not user_group_dn:
                continue
            del auth_user_group_set[user_group_dn]
    
    return None
    
def describe_auth_user_groups(auth_service, base_dn, user_group_names, user_names, search_name, scope):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    if not base_dn:
        base_dn = auth_service["base_dn"]
    
    ret = ctx.auth.get_auth_user_groups(auth_service_id, base_dn=base_dn, user_group_names=user_group_names, scope=scope, search_name=search_name)
    if isinstance(ret, Error):
        return ret
    
    return ret

def build_auth_user_group_info(req):
    
    user_group_info = {}
    user_group_info['name'] = str(req['user_group_name'])
    user_group_info['sAMAccountName'] = str(req['user_group_name'])
    if req.get('group_type'):
        user_group_info['groupType'] = str(req['group_type'])
    if req.get('description'):
        user_group_info['description'] = str(req['description'])

    return user_group_info

def create_auth_user_group(auth_service, base_dn, req):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    if not base_dn:
        base_dn = auth_service["base_dn"]
    
    auth_service_type = auth_service["auth_service_type"]
    
    user_group_info = {}
    
    if auth_service_type == const.AUTH_TYPE_LOCAL:
        user_group_info["user_group_name"] = str(req['user_group_name'])
        if req.get('description'):
            user_group_info['description'] = str(req['description'])
    else:
        user_group_info = build_auth_user_group_info(req)
    
    ret = ctx.auth.create_auth_user_group(auth_service_id, base_dn, user_group_info)
    if isinstance(ret, Error) or not ret:
        return ret
    user_group_dn = ret
    
    user_group_name, base_dn = ctx.auth.get_base_dn(user_group_dn)
    
    ret = SyncAuthUser.sync_auth_user_group(auth_service_id, base_dn, user_group_name)
    if isinstance(ret, Error):
        return ret

    return ret

def modify_auth_user_group_attributes(auth_service, user_group_dn, need_maint_columns):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    user_group_dn = ctx.auth.format_base_dn(user_group_dn)
    
    ret = ctx.auth.modify_auth_user_group(auth_service_id, user_group_dn, need_maint_columns)
    if isinstance(ret, Error):
        return ret
    
    user_group_name, base_dn = ctx.auth.get_base_dn(user_group_dn)
    
    ret = SyncAuthUser.sync_auth_user_group(auth_service_id, base_dn, user_group_name)
    if isinstance(ret, Error):
        return ret
    
    return ret

def delete_auth_user_groups(auth_service, user_group_dns):
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    ret = ctx.auth.delete_auth_user_groups(auth_service_id, user_group_dns) 
    if isinstance(ret, Error):
        return ret
    
    for user_group_dn in user_group_dns:
        user_group_name, base_dn = ctx.auth.get_base_dn(user_group_dn)
        
        ret = SyncAuthUser.sync_auth_user_group(auth_service_id, base_dn, user_group_name)
        if isinstance(ret, Error):
            return ret
    
    return ret

def add_auth_user_to_user_group(auth_service, user_names, user_group_dn):

    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    user_group_dn = ctx.auth.format_base_dn(user_group_dn)
    
    existed_users = ctx.pgm.get_user_group_user_name_by_dn(user_group_dn)
    if not existed_users:
        existed_users = {}
    
    new_user_names = []
    for user_name in user_names:
        if user_name in existed_users:
            continue
        new_user_names.append(user_name)
    
    if not new_user_names:
        return None
    
    ret = ctx.auth.add_auth_user_to_user_group(auth_service_id, new_user_names, user_group_dn) 
    if isinstance(ret, Error):
        return ret
    
    ret = ctx.pgm.get_desktop_user_groups(auth_service_id, user_group_dns=user_group_dn)
    if not ret:
        return None

    user_group_id = ret.keys()[0]

    ret = SyncAuthUser.sync_auth_user_group_user(user_group_id)
    if isinstance(ret, Error):
        return ret

    return ret

def remove_auth_user_from_user_group(auth_service, user_names, user_group_dn):

    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    ret = ctx.auth.remove_auth_user_from_user_group(auth_service_id, user_names, user_group_dn) 
    if isinstance(ret, Error):
        return ret

    ret = ctx.pgm.get_desktop_user_groups(auth_service_id, user_group_dns=user_group_dn)
    if not ret:
        return None

    user_group_id = ret.keys()[0]

    ret = SyncAuthUser.sync_auth_user_group_user(user_group_id)
    if isinstance(ret, Error):
        return ret

    return ret

def check_auth_unicode_param(user, params=[]):
    
    if not user:
        return user
    
    check_keys = ["user_names", 'search_name', 'base_dn', 'user_group', "real_name", "user_dns",
                  "user_name", "ou_name", "ou_dn", "new_ou_dn", "user_group_names", "user_group_name",
                  "user_group_dn", "user_group_dns", "new_name", "login_name"]
    if params:
        if isinstance(params, list):
            check_keys.extend(params)
        else:
            check_keys.append(params)

    if isinstance(user, dict):
        for key, value in user.items():
            if key not in check_keys:
                continue
            if isinstance(value, unicode):
                a = str(value).decode("string_escape").encode("utf-8")
                user[key] = a
            elif isinstance(value, list):
                new_values = []
                for _value in value:
                    _value = check_auth_unicode_param(_value)
                    new_values.append(_value)
                user[key] = new_values

    elif isinstance(user, list):
        new_values = []
        for value in user:
            if isinstance(value, unicode):
                value = str(value).decode("string_escape").encode("utf-8")
                new_values.append(value)
                continue
            new_values.append(value)
        return new_values
    
    elif isinstance(user, unicode):
        return str(user).decode("string_escape").encode("utf-8")

    return user

def format_auth_service_dn(check_param):
    
    if not check_param:
        return check_param
    
    if isinstance(check_param, list):
        temp_list = []
        for _param in check_param:
            if isinstance(_param, unicode):
                _param = str(_param).decode("string_escape").encode("utf-8")

            temp_list.append(_param)
        return temp_list

    elif isinstance(check_param, unicode):
        _param = str(check_param).decode("string_escape").encode("utf-8")
        return _param
    
    return check_param

def check_rename_user_dn(auth_service_id, user_dn, dn_type, new_name = None, login_name=None):
    
    ctx = context.instance()
    
    if dn_type == const.USER_DN_TYPE_OU:
        ou_name, base_dn = ctx.auth.get_base_dn(user_dn)
        if ou_name == new_name:
            return None
               
        ret = check_auth_cn_name_vaild(auth_service_id, new_name, base_dn)
        if isinstance(ret, Error):
            return ret

        ret = check_rename_auth_service_domain(user_dn)
        if isinstance(ret, Error):
            return ret

    elif dn_type == const.USER_DN_TYPE_USER:
        _, base_dn = ctx.auth.get_base_dn(user_dn)
        ret = ctx.pgm.get_user_by_user_dn(auth_service_id, user_dn)
        if not ret:
            logger.error("no found user by user_dn %s" % user_dn)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_USER_NO_FOUND, user_dn)
        desktop_user = ret[user_dn]

        user_name = desktop_user["user_name"]
        if login_name and login_name != user_name:
            ret = check_auth_user_name_vaild(auth_service_id, login_name)
            if isinstance(ret, Error):
                return ret
        
        if new_name and new_name != desktop_user["real_name"]:
            ret = check_auth_cn_name_vaild(auth_service_id, new_name, base_dn)
            if isinstance(ret, Error):
                return ret
    elif dn_type == const.USER_DN_TYPE_USER_GROUP:
        user_group_name, base_dn = ctx.auth.get_base_dn(user_dn)
        if user_group_name == new_name:
            return None
        ret = check_auth_user_name_vaild(auth_service_id, new_name)
        if isinstance(ret, Error):
            return ret

        ret = check_auth_cn_name_vaild(auth_service_id, new_name, base_dn)
        if isinstance(ret, Error):
            return ret

    return new_name
    
def check_rename_auth_service_domain(user_dn):
    
    ctx = context.instance()

    auth_services = ctx.pgm.get_auth_service_by_ou_dn(user_dn)
    if auth_services:
        logger.error("cant modify authservice domain %s" % (user_dn))
        return Error(ErrorCodes.PERMISSION_DENIED,
                ErrorMsg.ERR_MSG_ZONE_AUTH_SERVICE_IN_USED, user_dn)
    
    return None

def check_auth_zone_base_dn():
    
    ctx = context.instance()
    ret = ctx.pgm.get_auth_service_zone()
    if not ret:
        return None
    
    update_zone = {}
    for zone_id, auth_zone in ret.items():
        
        object_guid = auth_zone["object_guid"]
        if not object_guid:
            continue
        
        ret = ctx.pgm.get_user_ous(object_guids=object_guid, index_guid=True)
        if not ret:
            continue
        
        user_ou = ret.get(object_guid)
        if not user_ou:
            continue
        
        if user_ou["ou_dn"] != auth_zone["base_dn"]:
            update_zone[zone_id] = {"base_dn": user_ou["ou_dn"]}
    
    if update_zone:
        if not ctx.pg.batch_update(dbconst.TB_ZONE_AUTH, update_zone):
            logger.error("update desktop %s ou info fail" % (update_zone))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def rename_auth_user_dn(auth_service, user_dn, new_name, dn_type, login_name=None):

    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    
    ret = ctx.auth.rename_auth_user_dn(auth_service_id, user_dn, new_name, dn_type, login_name) 
    if isinstance(ret, Error):
        return ret

    if dn_type == const.USER_DN_TYPE_OU:

        ret = check_auth_zone_base_dn()
        if isinstance(ret, Error):
            return ret

        _, base_dn = ctx.auth.get_base_dn(user_dn)
        ret = AuthService.refresh_auth_service(auth_service, base_dn)
        if isinstance(ret, Error):
            return ret

    elif dn_type == const.USER_DN_TYPE_USER:
        _, base_dn = ctx.auth.get_base_dn(user_dn)
        
        ret = ctx.pgm.get_user_by_user_dn(auth_service_id, user_dn)
        if not ret:
            return None
        
        desktop_user = ret[user_dn]
        user_name = desktop_user["user_name"]
        old_name = desktop_user["user_name"]
        if login_name and user_name != login_name:
            user_name = login_name

        ret = SyncAuthUser.sync_auth_users(auth_service_id, base_dn, user_name, old_name=old_name)
        if isinstance(ret, Error):
            return ret

    elif dn_type == const.USER_DN_TYPE_USER_GROUP:
        old_group_name, base_dn = ctx.auth.get_base_dn(user_dn)

        ret = SyncAuthUser.sync_auth_user_group(auth_service_id, base_dn, new_name, old_group_name=old_group_name)
        if isinstance(ret, Error):
            return ret

    return new_name

def check_auth_user_password(sender, user, auth_service_id, lock_out_time = None):
    
    ctx = context.instance()
    
    if APIUser.is_global_admin_user(sender):
        return None
    
    pwd_conf = ctx.pgm.get_auth_password_config()
    if not pwd_conf:
        return None
    
    bad_password_count = int(pwd_conf.get(const.CUSTOM_ITEM_KEY_BADPWDCOUNT, 0))
    if not bad_password_count:
        return None

    user_name = user["user_name"]

    # get auth user
    ret = ctx.auth.get_auth_users(auth_service_id, user_names=user_name)
    if not ret:
        logger.error("user %s no found" % (user_name))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                ErrorMsg.ERR_MSG_USER_NO_FOUND, user_name)
    
    auth_user = ret[user_name]

    # check password
    auth_bad_count = int(auth_user.get('badPwdCount'))
    badPasswordTime = auth_user.get("badPasswordTime", 0)
    lock_password = pwd_conf.get(const.CUSTOM_ITEM_KEY_LOCK_PASSWORD_TIME, 0)
    
    if isinstance(badPasswordTime, str):
        badPasswordTime = datetime.datetime.strptime(badPasswordTime,'%Y-%m-%d %H:%M:%S')
    
    if auth_bad_count < bad_password_count:
        return None

    if not lock_password:
        logger.error("user error time exceed %s" % (user_name))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_USER_ERROR_TIME_EXCEED_LIMIT)
    
    curr_time = get_current_time()
    delta = datetime.timedelta(minutes=int(lock_password))
    if badPasswordTime + delta >= curr_time:
        if lock_out_time is not None:
            lock_out_time["lock_time"] = badPasswordTime + delta
        logger.error("user %s password lock %s" % (user_name, badPasswordTime + delta))
        
        lock_time = badPasswordTime + delta-curr_time
        return Error(AuthConst.ERROR_CODE_HEX_MAP[AuthConst.ERROR_ACCOUNT_LOCKED_OUT],
                     AuthConst.ERR_MSG_PASSWORD_EXCEED_ERROR_TIME_LOCKED_OUT, (lock_time.seconds))
    
    return None    

def build_auth_user_info(user_data):
    
    user = {}
    user_name = user_data.get("user_name")
    if not user_name:
        return None

    user['user_name'] = user_name
    user['userPassword'] = user_data["password"]
    base_dn = user_data.get("base_dn")
    if base_dn:
        user['base_dn'] = base_dn
    
    real_name = user_data.get("real_name")
    if not real_name:
        real_name = user_name
    user['displayName'] = real_name
    
    if user_data.get("email"):
        user['email'] = user_data["email"]
    
    description = user_data.get("description", "")
    if description:
        user['description'] = description

    position = user_data.get("position", "")
    if position:
        user['physicalDeliveryOfficeName'] = position
    
    title =user_data.get("title")
    if title:
        user['title'] = title
    
    personal_phone = user_data.get("personal_phone", "")
    if personal_phone:
        user['telephoneNumber'] = personal_phone

    company_phone = user_data.get("company_phone", "")
    if company_phone:
        user['homePhone'] = company_phone
    
    account_control = user_data.get("account_control", 0)
    if account_control is not None:
        user['account_control'] = account_control

    for key, value in user.items():
        if isinstance(value, unicode):
            user[key] = str(value).decode("string_escape").encode("utf-8")

    return user

def set_auth_user_status(auth_service, auth_users, status):
    
    ctx = context.instance()
    auth_service_id = auth_service["auth_service_id"]
    user_names = auth_users.keys()
    
    for user_name, auth_user in auth_users.items():
        user_dn = auth_user["user_dn"]

        ret = ctx.auth.set_auth_user_status(auth_service_id, user_name, user_dn, status)
        if isinstance(ret, Error):
            return ret
    
        _, ou_dn = ctx.auth.get_base_dn(user_dn)
   
        ret = SyncAuthUser.sync_auth_users(auth_service_id, ou_dn, user_name)
        if isinstance(ret, Error):
            return ret
    
    return user_names