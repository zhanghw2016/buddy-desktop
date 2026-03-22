import context
from error.error import Error
from error.error import ErrorCodes
from error.error import ErrorMsg
import constants as const
from common import (
    return_success, return_error, return_items
)
from log.logger import logger
import resource_control.desktop.resource_permission as ResCheck
import resource_control.auth.auth_user as AuthUser
import resource_control.auth.auth_service as AuthService
import resource_control.auth.user_resource as UserResource
import resource_control.permission as Permission
from utils.misc import get_columns
from utils.json import json_load
from api.user.user import is_global_admin_user
import resource_control.user.user as ZoneUser
from utils.auth import get_hashed_password,check_password
import HTMLParser
import threading
add_user_to_group_lock = threading.Lock()
remove_user_to_group_lock = threading.Lock()
delete_user_lock = threading.Lock()
status_user_lock = threading.Lock()
create_ou_lock = threading.Lock()
create_user_lock = threading.Lock()
def handle_describe_auth_users(req):

    sender = req["sender"]
    ctx = context.instance()
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    base_dn = req.get('base_dn')
    user_names = req.get('user_names')
    search_name = req.get("search_name")
    scope = req.get("scope", 0)
    global_search = req.get("global_search")
    
    rep = {}
    auth_user_set = {}
    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        rep['total_count'] = len(auth_user_set)
        return return_items(req, auth_user_set, "auth_user", **rep)
    auth_service = ret[auth_service_id]

    ret = AuthService.check_auth_service_base_dn(sender, auth_service, base_dn)
    if isinstance(ret, Error) or not ret:
        rep['total_count'] = len(auth_user_set)
        return return_items(req, auth_user_set, "auth_user", **rep)
    base_dn = ret
    
    if global_search:
        base_dn = ctx.auth.get_domain_dn(auth_service["domain"])
    
    ret = ctx.auth.get_auth_users(auth_service_id, base_dn, user_names, search_name, scope)
    if isinstance(ret, Error):
        return return_error(req, ret)

    auth_user_set = ret
    syn_desktop = req.get("syn_desktop", 1)
    
    AuthUser.format_auth_users(auth_service_id, auth_user_set, syn_desktop)

    rep['total_count'] = len(auth_user_set) if auth_user_set else 0
    return return_items(req, auth_user_set, "auth_user", **rep)

def handle_import_auth_users(req):

    sender = req["sender"]
    ctx = context.instance()
    
    ret = ResCheck.check_request_param(req, ["base_dn", "json_items", "auth_service"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    AuthUser.check_auth_unicode_param(req)

    json_items = json_load(req.get('json_items', ''))
    base_dn = req['base_dn']
    auth_service_id = req["auth_service"]
    user_group = req.get("user_group")
   
    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthService.check_auth_service_base_dn(sender, auth_service, base_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)
    base_dn = ret
    
    user_info = {}
    for item in json_items:
        AuthUser.check_auth_unicode_param(item)
        user_data = AuthUser.build_auth_user_info(item)
        user_name = user_data["user_name"]
        cn_name = user_data["displayName"]

        ret = AuthUser.check_add_auth_user(auth_service_id, base_dn, user_name, cn_name)
        if isinstance(ret, Error):
            return return_error(req, ret)

        user_info[user_name] = user_data
   
    user_dns = []
    for user_name, user in user_info.items():

        ret = AuthUser.create_auth_user(auth_service, base_dn, user, is_sync=False)
        if isinstance(ret, Error):
            return return_error(req, ret)
        user_dn = ret

        if user_group:

            ret = ctx.pgm.get_desktop_user_group_by_dn(user_group)
            if ret:
                ret = AuthUser.add_auth_user_to_user_group(auth_service, user['user_name'], user_group)
                if isinstance(ret, Error):
                    return return_error(req, ret)

        user_dns.append(user_dn)

    ret = AuthService.refresh_auth_service(auth_service, base_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    rep = {
        "user_dn": user_dns,
        "user_dn_count": len(user_dns)
        }
    return return_success(req, rep)

def handle_create_auth_user(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["auth_service", 'user_name', 'userPassword', 'base_dn'])
    if isinstance(ret, Error):
        return return_error(req, ret)

    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    user_name = req["user_name"]
    base_dn = req['base_dn']

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthService.check_auth_service_base_dn(sender, auth_service, base_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)
    base_dn = ret
    
    cn_name = req.get("displayName")
    if not cn_name:
        cn_name = req["user_name"]
        req["displayName"] = cn_name


    global create_user_lock
    create_user_lock.acquire()
    ret = AuthUser.check_add_auth_user(auth_service_id, base_dn, user_name, cn_name)
    if isinstance(ret, Error):
        create_user_lock.release() 
        return return_error(req, ret)
    password=req["userPassword"]
    html_parser = HTMLParser.HTMLParser()
    password=html_parser.unescape(password)      
    req["userPassword"]=password
    ret = AuthUser.create_auth_user(auth_service, base_dn, req)
    if isinstance(ret, Error):
        create_user_lock.release() 
        return return_error(req, ret)
    create_user_lock.release() 
    
    user_dn = ret
    user_id = AuthUser.get_auth_user_id(auth_service, user_name)
    if not user_id:
        user_id = ''
    
    return return_success(req, {'user_dn': user_dn, "user_id": user_id})

def handle_modify_auth_user_attributes(req):
    
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ["auth_service", 'user_name'])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    user_name = req["user_name"]

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_user_vaild(auth_service_id, user_name)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_user = ret.get(user_name)

    ou_dn = auth_user["ou_dn"]
    ret = AuthService.check_auth_service_base_dn(sender, auth_service, ou_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    need_maint_columns = get_columns(req, ["description", "physicalDeliveryOfficeName", 
                                           "title", "mail", "telephoneNumber", "homePhone"])

    if need_maint_columns:
        ret = AuthUser.modify_auth_user_attributes(auth_service, auth_user, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, {'user_name': user_name})

def handle_delete_auth_users(req):
    
    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["auth_service", 'user_names'])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    user_names = req["user_names"]

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_user_vaild(auth_service_id, user_names)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    auth_users = ret

    for user_name in user_names:

        auth_user = auth_users.get(user_name)
        if not auth_user:
            continue
        
        ou_dn = auth_user["ou_dn"]
        ret = AuthService.check_auth_service_base_dn(sender, auth_service, ou_dn)
        if isinstance(ret, Error):
            return return_error(req, ret)
   
    desktop_users = ctx.pgm.get_user_by_user_names(user_names, auth_service_id)
 
    global delete_user_lock
    delete_user_lock.acquire()
    ret = AuthUser.delete_auth_users(auth_service, user_names)
    delete_user_lock.release() 

    if isinstance(ret, Error):
        return return_error(req, ret)

    if desktop_users:
        for _, user_id in desktop_users.items():
            UserResource.check_auth_user_resource(sender, user_id)
    
    return return_success(req, None)

def handle_modify_auth_user_password(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["auth_service", 'user_name', 'old_password', "new_password"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)

    auth_service_id = req["auth_service"]
    user_name = req["user_name"]
    old_password = req['old_password']
    new_password = req['new_password']
    html_parser = HTMLParser.HTMLParser()
    old_password=html_parser.unescape(old_password)    
    new_password=html_parser.unescape(new_password)  
    if is_global_admin_user(sender) and user_name == const.GLOBAL_ADMIN_USER_NAME:
        ret = ZoneUser.get_user_password(user_name)
        if ret is None:
            logger.error("get user password error.")
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                           ErrorMsg.ERR_MSG_RESET_PASSWD_FAILED, user_name))
        hashed_password = ret
        if check_password(old_password, hashed_password) or hashed_password == old_password:
            if ZoneUser.reset_user_password(user_name, get_hashed_password(new_password)):
                return return_success(req, {'user_name': user_name})
        else:
            logger.error("check user [%s] password [%s] error!", (user_name, old_password))
            return return_error(req, Error(ErrorCodes.RESET_PASSWD_FAILED,
                                           ErrorMsg.ERR_MSG_CHANGE_PASSWD_FAILED))
    
    if sender["user_name"].lower() == user_name.lower() and sender["user_name"] != user_name:
        user_name = sender["user_name"]
    
    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service, False, True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_user_vaild(auth_service_id, user_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    auth_user = ret[user_name]
    ou_dn = auth_user["ou_dn"]
    ret = AuthService.check_auth_service_base_dn(sender, auth_service, ou_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.modify_auth_user_password(auth_service, user_name, old_password, new_password)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_reset_auth_user_password(req):

    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ['user_name', "password"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)

    user_name = req["user_name"]
    user_id = None
    user_role = sender["role"]
    logger.info("user_role == %s" %(user_role))
    # if user_role == const.USER_ROLE_NORMAL or user_role == const.USER_ROLE_CONSOLE_ADMIN:
    if user_role == const.USER_ROLE_NORMAL:
        user_name = sender["user_name"]
        user_id = sender["owner"]
    
    password = req['password']
    html_parser = HTMLParser.HTMLParser()
    password=html_parser.unescape(password)    
  
    auth_service_id = req.get("auth_service")
    logger.info("user_name == %s" %(user_name))
    if not auth_service_id:
        
        if not user_id:
            auth_service_ids = ctx.pgm.get_auth_service_by_username(user_name)
            if auth_service_ids is None:
                return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                               ErrorMsg.ERR_MSG_USER_NOT_FOUND, user_name))
            if len(auth_service_ids) != 1:
                return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                               ErrorMsg.ERR_MSG_USER_NAME_CONFLICT, user_name))
            auth_service_id = auth_service_ids[0]
        else:
            auth_users = ctx.pgm.get_desktop_users(user_id)
            if not auth_users:
                return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                               ErrorMsg.ERR_MSG_USER_NOT_FOUND, user_name))
            
            auth_user = auth_users[user_id]
            auth_service_id = auth_user["auth_service_id"]

    if is_global_admin_user(sender) and user_name == const.GLOBAL_ADMIN_USER_NAME:
        ret = ZoneUser.reset_user_password(user_name, get_hashed_password(password))
        if ret:
            return return_success(req, None)
        else:
            logger.error("reset password error. %s" % user_name)
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                           ErrorMsg.ERR_MSG_RESET_PASSWD_FAILED, user_name))
    
    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service, False, True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_user_vaild(auth_service_id, user_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    auth_user = ret[user_name]
    ou_dn = auth_user["ou_dn"]
    ret = AuthService.check_auth_service_base_dn(sender, auth_service, ou_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.reset_auth_user_password(auth_service, user_name, password)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_describe_auth_ous(req):
    
    sender = req["sender"]
    ctx = context.instance()
    
    AuthUser.check_auth_unicode_param(req)
    
    base_dn = req.get('base_dn')
    
    ou_names=None
    if "ou_names" in req:
        ou_names =req['ou_names']
        
    ret = ResCheck.check_request_param(req, ["auth_service"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service_id = req["auth_service"]
    scope = req.get("scope")

    rep = {}

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthService.check_auth_service_base_dn(sender, auth_service, base_dn)
    if isinstance(ret, Error) or not ret:
        rep['total_count'] = 0
        return return_items(req, None, "auth_ou", **rep)
    base_dn = ret
    ret = ctx.auth.get_auth_ous(auth_service_id, base_dn, ou_names=ou_names,scope=scope)
    if isinstance(ret, Error):
        return return_error(req, ret)

    if not ret:
        ret = {}
    auth_ou_set = ret
    syn_desktop = req.get("syn_desktop", 1)
    AuthUser.format_auth_user_ous(auth_service, auth_ou_set, syn_desktop)

    rep['total_count'] = len(auth_ou_set)
    return return_items(req, auth_ou_set, "auth_ou", **rep)

def handle_create_auth_ou(req):
    
    ret = ResCheck.check_request_param(req, ["auth_service", "ou_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    AuthUser.check_auth_unicode_param(req)

    auth_service_id = req["auth_service"]
    base_dn = req.get("base_dn")
    ou_name = req["ou_name"]
    description = req.get("description")
    
    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    global create_ou_lock 
    create_ou_lock.acquire()  
    ret = AuthUser.check_auth_cn_name_vaild(auth_service_id, ou_name, base_dn)
    if isinstance(ret, Error):
        create_ou_lock.release() 
        return return_error(req, ret)

    ret = AuthUser.create_auth_ou(auth_service, ou_name, base_dn, description)
    if isinstance(ret, Error):
        create_ou_lock.release() 
        return return_error(req, ret)
    create_ou_lock.release()   
    
    return return_success(req, {'ou_dn': ret})

def handle_modify_auth_ou_attributes(req):
    
    ret = ResCheck.check_request_param(req, ["auth_service", "ou_dn"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    ou_dn = req["ou_dn"]

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    need_maint_columns = get_columns(req, ["description"])
    if need_maint_columns:
        ret = AuthUser.modify_auth_ou_attributes(auth_service, ou_dn, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_delete_auth_ou(req):
    
    ret = ResCheck.check_request_param(req, ["auth_service", "ou_dn"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    ou_dn = req["ou_dn"]

    ctx = context.instance()
    ou_id = ctx.pgm.get_desktop_user_ou_id_by_ou_dn(auth_service_id, ou_dn)

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.delete_auth_ou(auth_service, ou_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # clear resource permission
    Permission.clear_user_resource_scope(resource_ids=ou_id)

    return return_success(req, None)

def handle_change_auth_user_in_ou(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["auth_service", "user_names", "new_ou_dn"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    user_names = req["user_names"]
    new_ou_dn = req["new_ou_dn"]

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthService.check_auth_service_base_dn(sender, auth_service, new_ou_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_user_vaild(auth_service_id, user_names)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    auth_users = ret
    
    real_names = []
    
    for user_name in user_names:
        
        auth_user = auth_users.get(user_name)
        real_name = auth_user["real_name"]
        if real_name in real_names:
            logger.error("user %s conflict" % real_name)
            return return_error(req, Error(ErrorCodes.USER_ALREADY_EXISTED,
                                           ErrorMsg.ERR_MSG_AUTH_USER_EXISTED, real_name))

        real_names.append(real_name)
        ret = AuthUser.check_auth_cn_name_vaild(auth_service_id, real_name, new_ou_dn)
        if isinstance(ret, Error):
            return return_error(req, ret)

    ret = AuthUser.change_auth_user_ou_dn(auth_service, new_ou_dn, auth_users)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_describe_auth_user_groups(req):

    ret = ResCheck.check_request_param(req, ["auth_service"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    base_dn = req.get("base_dn")
    user_group_names = req.get("user_group_names")
    user_names= req.get("user_names")
    search_name= req.get("search_name")
    scope = req.get("scope", 0)
    
    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.describe_auth_user_groups(auth_service, base_dn, user_group_names, user_names, search_name, scope)
    if isinstance(ret, Error):
        return return_error(req, ret)

    auth_user_group_set = ret
    
    syn_desktop = req.get("syn_desktop", 1)
    AuthUser.format_user_groups(auth_service_id, auth_user_group_set, syn_desktop)

    rep = {}
    rep['total_count'] = len(auth_user_group_set)
    return return_items(req, auth_user_group_set, "auth_user_group", **rep)

def handle_create_auth_user_group(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["auth_service", "user_group_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    base_dn = req.get("base_dn")
    user_group_name = req["user_group_name"]

    rep = {}
    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthService.check_auth_service_base_dn(sender, auth_service, base_dn)
    if isinstance(ret, Error) or not ret:
        rep['total_count'] = 0
        return return_items(req, None, "auth_user_group", **rep)

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_add_auth_user(auth_service_id, base_dn, user_group_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.create_auth_user_group(auth_service, base_dn, req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, {'auth_user_group': ret})

def handle_modify_auth_user_group_attributes(req):
    
    ret = ResCheck.check_request_param(req, ["auth_service", "user_group_dn"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    user_group_dn = req["user_group_dn"]

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_user_group_vaild(auth_service_id, user_group_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    need_maint_columns = get_columns(req, ["description"])
    if need_maint_columns:
        ret = AuthUser.modify_auth_user_group_attributes(auth_service, user_group_dn, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_delete_auth_user_groups(req):
    
    sender = req["sender"]
    ctx = context.instance()
    ret = ResCheck.check_request_param(req, ["auth_service", "user_group_dns"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    user_group_dns = req["user_group_dns"]

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_user_group_vaild(auth_service_id, user_group_dns)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.delete_auth_user_groups(auth_service, user_group_dns)
    if isinstance(ret, Error):
        return return_error(req, ret)

    user_groups = ctx.pgm.get_desktop_user_groups(auth_service_id, user_group_dns=user_group_dns)

    if user_groups:
        for user_group_id, _ in user_groups.items():
            UserResource.check_auth_user_group_resource(sender, user_group_id)

    return return_success(req, None)

def handle_add_auth_user_to_user_group(req):
    
    ret = ResCheck.check_request_param(req, ["auth_service", "user_names", "user_group_dn"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    user_names = req["user_names"]
    user_group_dn = req["user_group_dn"]

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_user_vaild(auth_service_id, user_names)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = AuthUser.check_auth_user_group_vaild(auth_service_id, user_group_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    global add_user_to_group_lock 
    add_user_to_group_lock.acquire()
    ret = AuthUser.add_auth_user_to_user_group(auth_service, user_names, user_group_dn)
    add_user_to_group_lock.release()

    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_remove_auth_user_from_user_group(req):
    
    ret = ResCheck.check_request_param(req, ["auth_service", "user_names", "user_group_dn"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    user_names = req["user_names"]
    user_group_dn = req["user_group_dn"]

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_user_vaild(auth_service_id, user_names)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_user_group_vaild(auth_service_id, user_group_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    global remove_user_to_group_lock 
    remove_user_to_group_lock.acquire()
    ret = AuthUser.remove_auth_user_from_user_group(auth_service, user_names, user_group_dn)
    remove_user_to_group_lock.release()

    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_rename_auth_user_dn(req):
    
    ret = ResCheck.check_request_param(req, ["auth_service", "user_dn", "new_name", 'dn_type'])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    user_dn = req["user_dn"]
    new_name = req.get("new_name")
    dn_type = req["dn_type"]
    login_name = req.get("login_name")
    
    user_dn = AuthUser.format_auth_service_dn(user_dn)
    if new_name:
        new_name = AuthUser.format_auth_service_dn(new_name)
    
    if login_name:
        login_name = AuthUser.format_auth_service_dn(login_name)
    
    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_rename_user_dn(auth_service_id, user_dn, dn_type, new_name, login_name)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = AuthUser.rename_auth_user_dn(auth_service, user_dn, new_name, dn_type, login_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_set_auth_user_status(req):
    
    ret = ResCheck.check_request_param(req, ["auth_service", "user_names", "status"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    user_names = req["user_names"]
    status = req["status"]

    user_names = AuthUser.format_auth_service_dn(user_names)

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthUser.check_auth_service_permission(auth_service)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthUser.check_auth_user_vaild(auth_service_id, user_names)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_users = ret

    global status_user_lock 
    status_user_lock.acquire()
    ret = AuthUser.set_auth_user_status(auth_service, auth_users, status)
    status_user_lock.release()

    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)