'''
Created on 2017-3-8

@author: yunify
'''
import copy
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from common import (
    build_filter_conditions,
    is_admin_user,
    is_global_admin_user,
    is_console_admin_user,
    is_normal_user,
    get_sort_key,
    get_reverse, 
    is_normal_console,
    )
from common import (
    return_success, return_error, return_items
)
from db.data_types import (
    NotType,
    SearchWordType
)
from resource_control.user.user import (
    enable_users,
    disable_users,
    modify_user_role,
    modify_user_scope,
    describe_user_scope,
    get_user_resource_detail,
    format_user_groups,
    describe_user_login_record,
    format_user_set
)
from resource_control.permission import (
    check_user_resource_permission, 
    clear_user_scope_resource_action, 
)
import constants as const
from constants import(
    USER_ROLE_NORMAL, USER_ROLE_CONSOLE_ADMIN, USER_ROLE_GLOBAL_ADMIN, 
    GLOBAL_ADMIN_USER_ID,ACTION_VDI_GLOBAL_ADMIN_WHITE_LIST,GLOBAL_ADMIN_USER_NAME,
)
import db.constants as dbconst
import context
from utils.json import json_load
from utils.id_tool import get_resource_type
import resource_control.user.apply_approve as ApplyApprove
import api.user.user as APIUser
import resource_control.permission as Permission
import resource_control.auth.auth_user as AuthUser

def handle_get_zone_user_admins(req):

    ctx = context.instance()
    user_id = req.get("user_id", "")
    zone_id = req["sender"].get("zone", "")

    auth_zone = ctx.pgm.get_auth_zone(zone_id)
    if auth_zone is None:
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_NO_FOUND_ZONE_INFO, zone_id))
    auth_service_id = auth_zone["auth_service_id"]

    user_ou_id = ctx.pgm.get_user_ou_id(auth_service_id, user_id)
    if user_ou_id is None:
        return return_error(req, Error(ErrorCodes.USER_NOT_FOUND,
                                       ErrorMsg.ERR_MSG_USER_NOT_FOUND, user_id))

    resource_ids = ctx.pgm.get_ou_parent_ids(user_ou_id)
    if not resource_ids:
        rep = {'user_admins': []}
        return return_success(req, rep) 

    admin_ids = []
    user_scopes = ctx.pgm.get_resource_scope(resource_ids)
    if not user_scopes:
        user_scopes = []
    for user_scope in user_scopes:
        if user_scope.get("user_id") not in admin_ids:
            admin_ids.append(user_scope.get("user_id"))

    approve_group_admin_ids = []
    ret = ctx.pgm.get_apply_group_user(user_ids=user_id)
    if ret:
        apply_group_users = ret
        for user_id,apply_group_user in apply_group_users.items():
            apply_group_id = apply_group_user.get("apply_group_id")
            ret = ctx.pgm.get_apply_approve_group_maps(apply_group_ids=apply_group_id)
            if ret:
                apply_approve_group_maps = ret
                for approve_group_id,_ in apply_approve_group_maps.items():
                    approve_group_id = approve_group_id
                    ret = ctx.pgm.get_approve_group_user(approve_group_id=approve_group_id)
                    if ret:
                        approve_group_users = ret
                        for approve_group_user_id,approve_group_user in approve_group_users.items():
                            user_type = approve_group_user.get("user_type")
                            if const.USER_TYPE_USER == user_type:
                                if approve_group_user_id not in approve_group_admin_ids:
                                    approve_group_admin_ids.append(approve_group_user_id)
                            elif const.USER_TYPE_GROUP == user_type:
                                group_user_ids = ctx.pgm.get_desktop_user_form_user_group(user_group_id=approve_group_user_id)
                                for group_user_id in group_user_ids:
                                    if group_user_id not in approve_group_admin_ids:
                                        approve_group_admin_ids.append(group_user_id)
                            else:
                                logger.info("unknow user_type %s" % (user_type))

    else:
        ret = ctx.pgm.get_user_group(user_id=user_id)
        if ret:
            user_groups = ret
            for user_group_id in user_groups:
                ret = ctx.pgm.get_apply_group_user(user_ids=user_group_id)
                if ret:
                    apply_group_users = ret
                    for user_id, apply_group_user in apply_group_users.items():
                        apply_group_id = apply_group_user.get("apply_group_id")
                        ret = ctx.pgm.get_apply_approve_group_maps(apply_group_ids=apply_group_id)
                        if ret:
                            apply_approve_group_maps = ret
                            for approve_group_id, _ in apply_approve_group_maps.items():
                                approve_group_id = approve_group_id
                                ret = ctx.pgm.get_approve_group_user(approve_group_id=approve_group_id)
                                if ret:
                                    approve_group_users = ret
                                    for approve_group_user_id, approve_group_user in approve_group_users.items():
                                        user_type = approve_group_user.get("user_type")
                                        if const.USER_TYPE_USER == user_type:
                                            if approve_group_user_id not in approve_group_admin_ids:
                                                approve_group_admin_ids.append(approve_group_user_id)
                                        elif const.USER_TYPE_GROUP == user_type:
                                            group_user_ids = ctx.pgm.get_desktop_user_form_user_group(
                                                user_group_id=approve_group_user_id)
                                            for group_user_id in group_user_ids:
                                                if group_user_id not in approve_group_admin_ids:
                                                    approve_group_admin_ids.append(group_user_id)
                                        else:
                                            logger.info("unknow user_type %s" % (user_type))

    admins = []
    for admin_id in admin_ids:
        admin = ctx.pgm.get_desktop_user_detail(admin_id, columns=["user_id", "user_name", "real_name"])
        admins.append(admin)
    rep = {'user_admins': admins}

    approve_group_admins = []
    for approve_group_admin_id in approve_group_admin_ids:
        approve_group_admin = ctx.pgm.get_desktop_user_detail(approve_group_admin_id, columns=["user_id", "user_name", "real_name"])
        approve_group_admins.append(approve_group_admin)
    rep["approve_group_admins"] = approve_group_admins
    
    return return_success(req, rep)

def handle_describe_zone_users(req):

    ctx = context.instance()
    sender = req["sender"]
    zone_id = sender["zone"]
    
    AuthUser.check_auth_unicode_param(req)

    # normal user
    if is_normal_console(req['sender']):
        users = ctx.pgm.get_desktop_users(req['sender']['owner'])
        if users:
            user = users[req['sender']['owner']]
            user["in_apply_group"] = ApplyApprove.user_is_in_apply_group(user["user_id"])
            user["in_approve_group"] = ApplyApprove.user_is_in_approve_group(user["user_id"])
            user["ou_dn"] = user['ou_dn']
            
            ret = ctx.pgm.get_zone_user(zone_id, user["user_id"])
            if ret:
                user.update(ret)

            user_set = {user["user_id"]: user}
            rep = {'total_count': len(user_set)}
            return return_items(req, user_set, "user", **rep)
        else:
            logger.error('user not exist!')
            return return_error(req, Error(ErrorCodes.INVALID_USER_ID))

    if APIUser.is_global_admin_user(sender):
        user_ids = req.get("users")
        if user_ids:
            ret = ctx.pgm.get_zone_users(zone_id,user_ids)
            if ret:
                rep = {'total_count': len(ret)}
                return return_items(req, ret, "user", **rep)

    # check must parameters
    filter_conditions = build_filter_conditions(req, dbconst.TB_ZONE_USER)

    filter_conditions.update({'zone_id': sender["zone"]})
    if is_global_admin_user(req['sender']):
        if "zones" in req:
            filter_conditions.update({'zone_id': req["zones"]})

    if "users" in req:
        filter_conditions.update({'user_id': req["users"]})
    else:
        excluded_user_ids = req.get('excluded_user_ids', None)
        if excluded_user_ids:
            filter_conditions.update({'user_id': NotType(excluded_user_ids)})

    if "user_names" in req:
        filter_conditions.update({'user_name':req["user_names"]})

    if "role" in req:
        if USER_ROLE_GLOBAL_ADMIN in req["role"]:
            req["role"].remove(USER_ROLE_GLOBAL_ADMIN)
        if len(req["role"]) > 0:
            filter_conditions.update({'role':req["role"]})
    else:
        if ("user_names" in req and GLOBAL_ADMIN_USER_NAME in req.get("user_names")) or ("users" in req and GLOBAL_ADMIN_USER_ID in req.get("users")):
            pass
        else: 
            filter_conditions.update({'role':[USER_ROLE_NORMAL, USER_ROLE_CONSOLE_ADMIN]})

    if is_console_admin_user(req['sender']) and not is_normal_console(req['sender']):
        ret = describe_user_scope(req['sender']['owner'],
                                          resource_type=[dbconst.RESTYPE_USER_OU])
        if not ret:
            return return_success(req, {'user_set':[], 'total_count':0})

    # global admin user can see all resources
    if is_global_admin_user(req['sender']):
        display_columns = dbconst.CONSOLE_ADMIN_COLUMNS[dbconst.TB_ZONE_USER]
    elif is_console_admin_user(req['sender']):
        display_columns = dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_ZONE_USER]
    else:
        display_columns = dbconst.PUBLIC_COLUMNS[dbconst.TB_ZONE_USER]

    user_set = ctx.pg.get_by_filter(dbconst.TB_ZONE_USER, filter_conditions, display_columns, 
                                    sort_key = get_sort_key(dbconst.TB_DESKTOP_USER, req.get("sort_key")),
                                    reverse = get_reverse(req.get("reverse")),
                                    offset = req.get("offset", 0),
                                    limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                    )
    if user_set is None:
        logger.error("describe user failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # Detect if the module_custom_user repeats
    format_user_set(sender, user_set,req.get("check_module_custom_user"))

    verbose = req.get("verbose", 0)
    if verbose > 0 and user_set:
        user_ids = user_set.keys()
        user_resource = get_user_resource_detail(sender, user_ids)
        for user_id, user in user_set.items():
            
            if "password" in user:
                del user["password"]

            # resources
            resource = user_resource.get(user_id)
            if not resource:
                user["resources"] = []
            else:
                user["resources"] = resource.values()

            # user groups 
            user_groups = format_user_groups(user)
            user["user_groups"] = user_groups

            # user ou
            columns = ["user_id", "ou_dn", "user_dn", "real_name", "user_name", "auth_service_id", "default_zone"]
            user_detail = ctx.pgm.get_desktop_user_detail(user_id, columns)
            user["user_detail"] = user_detail

            # platform
            zone = ctx.zones.get(sender["zone"])
            if zone:
                user["platform"] = zone.platform

            # user login record
            login_record = describe_user_login_record(user_id, sender["zone"])
            if login_record is not None:
                user["login_record"] = login_record

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_ZONE_USER, filter_conditions)
    if total_count is None:
        logger.error("get user count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    rep = {'total_count':total_count}

    return return_items(req, user_set, "user", **rep)


def handle_enable_zone_users(req):
    
    sender = req["sender"]
    ctx = context.instance()
    if not is_admin_user(req['sender']):
        logger.error("only admin can modify user's status")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    user_ids = req.get('user_ids', [])
    if GLOBAL_ADMIN_USER_ID in user_ids:
        user_ids.remove(GLOBAL_ADMIN_USER_ID)

    if len(user_ids) == 0:
        return return_success(req, {"user_ids": []})

    zone_id = req['sender']['zone']
    if is_console_admin_user(req['sender']):  
        for user_id in user_ids:
            user_role = ctx.pgm.get_user_role_by_user_id(user_id, zone_id)
            if user_role == USER_ROLE_CONSOLE_ADMIN:
                logger.error("user [%s] is console_admin, permission error!", 
                             (user_id))
                return return_error(req,Error(ErrorCodes.PERMISSION_DENIED, 
                                              ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                              (req['sender']["owner"], user_id)))

            auth_zone = ctx.pgm.get_auth_zone(zone_id)
            if auth_zone is None:
                return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                               ErrorMsg.ERR_MSG_NO_FOUND_ZONE_INFO, zone_id))
            auth_service_id = auth_zone["auth_service_id"]
            user_ou_id = ctx.pgm.get_user_ou_id(auth_service_id, user_id)
            ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_USER_OU, 
                                                 [user_ou_id], 
                                                 dbconst.RES_SCOPE_READONLY)
            if isinstance(ret, Error):
                logger.error("check user [%s] resource [%s] permission error!", 
                         (req['sender']['owner'], user_ou_id))
                return return_error(req, ret)
            if ret==None or len(ret)==0:
                return return_error(req,Error(ErrorCodes.PERMISSION_DENIED, 
                                              ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                              (req['sender']["owner"], user_ou_id)))

    ret = enable_users(user_ids, zone_id)
    if isinstance(ret, Error):
        logger.error("enable user [%s] error", user_ids)
        return return_error(req, ret)

    return return_success(req, {"user_ids": ret})


def handle_disable_zone_users(req):
    
    sender = req["sender"]
    ctx = context.instance()
    if not is_admin_user(req['sender']):
        logger.error("only admin can modify user's status")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))
  
    user_ids = req.get('user_ids', [])
    if GLOBAL_ADMIN_USER_ID in user_ids:
        user_ids.remove(GLOBAL_ADMIN_USER_ID)

    if len(user_ids) == 0:
        return return_success(req, {"user_ids": []})

    zone_id = req['sender']['zone']
    if is_console_admin_user(req['sender']):  
        for user_id in user_ids:
            user_role = ctx.pgm.get_user_role_by_user_id(user_id, zone_id)
            if user_role == USER_ROLE_CONSOLE_ADMIN:
                logger.error("user [%s] is console_admin, permission error!", 
                             (user_id))
                return return_error(req,Error(ErrorCodes.PERMISSION_DENIED, 
                                              ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                              (req['sender']["owner"], user_id)))
            auth_zone = ctx.pgm.get_auth_zone(zone_id)
            if auth_zone is None:
                return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                               ErrorMsg.ERR_MSG_NO_FOUND_ZONE_INFO, zone_id))
            auth_service_id = auth_zone["auth_service_id"]
            user_ou_id = ctx.pgm.get_user_ou_id(auth_service_id, user_id)
            ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_USER_OU, 
                                              [ ], 
                                              dbconst.RES_SCOPE_READONLY)
            if isinstance(ret, Error):
                logger.error("check user [%s] resource [%s] permission error!", 
                         (req['sender']['owner'], user_ou_id))
                return return_error(req, ret)
            if ret==None or len(ret)==0:
                logger.error("check user [%s] resource [%s] permission error!", 
                         (req['sender']['owner'], user_ou_id))
                return return_error(req,Error(ErrorCodes.PERMISSION_DENIED, 
                                              ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                              (req['sender']["owner"], user_ou_id)))

    ret = disable_users(user_ids, zone_id)
    if isinstance(ret, Error):
        logger.error("disable user [%s] error", user_ids)
        return return_error(req, ret)

    return return_success(req, {"user_ids": ret})


def handle_modify_zone_user_role(req):

    if not is_global_admin_user(req['sender']):
        logger.error("only global admin can modify user role")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))
    zone_id =  req['sender']['zone']  
    user_id = req.get('user_id', '')
    if user_id == GLOBAL_ADMIN_USER_ID:
        logger.error("global admin user role can not modify")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_MODIFY_SUPER_USER_ROLE)) 

    role = req.get('role', '')
    if role not in [USER_ROLE_NORMAL, USER_ROLE_CONSOLE_ADMIN]:
        logger.error("user role [%s] is error", role)
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE))

    if modify_user_role(user_id, role, zone_id):
        #update user scope
        if role == USER_ROLE_CONSOLE_ADMIN:
            pass
        
        if role == USER_ROLE_NORMAL:
            #clear user per mission scope
            ret = clear_user_scope_resource_action(user_id,zone_id)
            if not ret:
                logger.error("check user [%s] resource action error!", 
                         (user_id))
                return return_error(req, Error(ErrorCodes.CLEAR_USER_SCOPE_ERROR, 
                                               ErrorMsg.ERR_MSG_CLEAR_USER_SCOPE_ERROR)) 

        return return_success(req, {'user_id': user_id})
    else:
        logger.error("modify desktop user [%s] role error", user_id)
        return return_error(req, Error(ErrorCodes.MODIFY_DESKTOP_USER_ROLE_ERROR, 
                                       ErrorMsg.ERR_MSG_MODIY_DESKTOP_USER_ROLE_ERROR))

def handle_modify_zone_user_scope(req):

    ctx = context.instance()
    if not is_global_admin_user(req['sender']):
        logger.error("only global admin can create user")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    zone_id = req['sender'].get('zone')
    user_id = req.get('user_id', '')

    user_role = ctx.pgm.get_user_role_by_user_id(user_id, zone_id)
    if user_role != const.USER_ROLE_CONSOLE_ADMIN:
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_ILLEGAL_ROLE, user_id))

    json_items = json_load(req.get('json_items', ''))
    for item in json_items:
        # if resource_type is RESTYPE_USER_OU, clean include relation
        if item['resource_type'] == dbconst.RESTYPE_USER_OU:
            if item.get('action_type', -1) > 0:
                user_scope_ou = describe_user_scope(user_id, dbconst.RESTYPE_USER_OU)
                if user_scope_ou:
                    res_id = item.get('resource_id', '')
                    res_ou_dn = ctx.pgm.get_user_ou_dn(res_id)
                    if res_ou_dn is None:
                        logger.error("resource [%s] not found" % res_id)
                        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                                       ErrorMsg.ERR_CODE_MSG_RESOURCE_NOT_FOUND))
                    for scope_ou in user_scope_ou:
                        cur_res_id = scope_ou["resource_id"]
                        if not cur_res_id:
                            continue
                        cur_res_ou_dn = ctx.pgm.get_user_ou_dn(cur_res_id)
                        if cur_res_ou_dn is None:
                            modify_user_scope(const.USER_SCOPE_OPERATION_DELETE, 
                                            user_id, 
                                            item['resource_type'], 
                                            cur_res_id, 
                                            item.get('action_type', -1),
                                            zone_id)

                        if cur_res_ou_dn is not None:
                            if res_ou_dn.find(cur_res_ou_dn) >=0 or cur_res_ou_dn.find(res_ou_dn) >= 0:
                                modify_user_scope(const.USER_SCOPE_OPERATION_DELETE, 
                                                user_id, 
                                                item['resource_type'], 
                                                cur_res_id, 
                                                item.get('action_type', -1),
                                                zone_id)

        ret = modify_user_scope(item['operation'], 
                                user_id, 
                                item['resource_type'], 
                                item.get('resource_id',''), 
                                item.get('action_type', -1),
                                zone_id)

        if isinstance(ret, Error):
            logger.error("modify user [%s] resource [%s] scope error",(user_id, item.get('resource_id')))
            return return_error(req, ret)

    return return_success(req, {'user_id': user_id})


def handle_describe_zone_user_scope(req):

    ctx = context.instance()
    sender = req["sender"]
    zone_id = sender.get('zone')

    # get desktop group set
    filter_conditions = build_filter_conditions(req, dbconst.TB_ZONE_USER_SCOPE)
    filter_conditions.update({"zone_id": zone_id})

    resource_type = req.get("resource_type", [])
    if resource_type:
        filter_conditions.update({"resource_type": resource_type})

    exclude_user_id = req.get("exclude_user")
    user_id = req.get("user")
    if not user_id:
        if not exclude_user_id:
            logger.error("no desktop user specified in request [%s]" % (req))
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                                           ErrorMsg.ERR_MSG_PUSH_SERVER_REQUEST_PARAMS_ERROR, ["user", "exclude_user"]))

    if user_id:
        desktop_users = ctx.pgm.get_desktop_users(user_id)
        if not desktop_users:
            logger.error("desktop user [%s] no found" % user_id)
            return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND,
                                           ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, user_id))
        filter_conditions.update({'user_id': user_id})
    else:
        exclude_user = ctx.pgm.get_desktop_users(exclude_user_id)
        if not exclude_user:
            logger.error("desktop user [%s] no found" % exclude_user_id)
            return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND,
                                           ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, exclude_user_id))
        if(len(resource_type) != 1):
            logger.error("exclude user must input only one resource_type")
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                                           ErrorMsg.ERR_MSG_PUSH_SERVER_REQUEST_PARAMS_ERROR, "resource_type"))

    if not is_admin_user(sender):
        logger.error("describe user [%s] cant access resource [%s]." % (sender["owner"], "user scope"))
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED, 
                                       (sender["owner"], "user scope")))

    if not user_id and exclude_user_id:
        filter_conditions = {'user_id': exclude_user_id,
                             'resource_type': resource_type,
                             'action_type': [1,2,3],
                             'zone_id': zone_id}
        user_scope_set = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, filter_conditions, 
                                         dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_ZONE_USER_SCOPE],
                                         offset = req.get("offset", 0),
                                         limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                      )
        if user_scope_set is None:
            logger.error("describe desktop group failed [%s]" % req)
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

        user_ous = []
        desktop_groups = []
        desktop_networks = []
        desktop_images = []
        delivery_groups = []
        desktop_snapshots = []
        scheduler_tasks = []
        policy_groups = []
        for user_scope in user_scope_set:
            resource_id = user_scope.get("resource_id", None)
            if resource_id:
                res_type = get_resource_type(resource_id)
                if res_type == dbconst.RESTYPE_USER_OU:
                    user_ou = ctx.pgm.get_user_ous(resource_id)
                    if user_ou:
                        user_ous.append(resource_id)
                elif res_type == dbconst.RESTYPE_DESKTOP_GROUP:
                    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id=resource_id)
                    if desktop_group:
                        desktop_groups.append(resource_id)
                elif res_type == dbconst.RESTYPE_DESKTOP_NETWORK:
                    desktop_network = ctx.pgm.get_networks(resource_id)
                    if desktop_network:
                        desktop_networks.append(resource_id)
                elif res_type == dbconst.RESTYPE_DESKTOP_IMAGE:
                    images = ctx.pgm.get_desktop_images(desktop_image=resource_id)
                    if images:
                        desktop_images.append(resource_id)
                elif res_type == dbconst.RESTYPE_DELIVERY_GROUP:
                    delivery_group = ctx.pgm.get_delivery_groups(delivery_group_ids=resource_id)
                    if delivery_group:
                        delivery_groups.append(resource_id)
                elif res_type == dbconst.RESTYPE_SNAPSHOT_GROUP:
                    desktop_snapshot = ctx.pgm.get_desktop_snapshots(snapshot_ids=resource_id)
                    if desktop_snapshot:
                        desktop_snapshots.append(resource_id)
                elif res_type == dbconst.RESTYPE_SCHEDULER_TASK:
                    scheduler_task = ctx.pgm.get_scheduler_tasks(scheduler_task_ids=resource_id)
                    if scheduler_task:
                        scheduler_tasks.append(resource_id)
                elif res_type == dbconst.RESTYPE_POLICY_GROUP:
                    policy_group = ctx.pgm.get_policy_groups(policy_group_ids=resource_id)
                    if policy_group:
                        policy_groups.append(resource_id)
                else:
                    pass

        user_scope_set = []
        user_ou_total_count = 0
        desktop_group_total_count = 0
        desktop_network_total_count = 0
        desktop_image_total_count = 0
        delivery_group_total_count = 0
        desktop_snapshot_total_count = 0
        scheduler_task_total_count = 0
        policy_group_total_count = 0
        rep = {}
        filter_conditions = {}
        if req.get("search_word"):
            filter_conditions.update({"search_word": SearchWordType(req.get("search_word"))})
        if dbconst.RESTYPE_USER_OU in resource_type:
            if user_ous:
                filter_conditions.update({"user_ou_id": NotType(user_ous)})
            user_ou_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_USER_OU, filter_conditions, 
                                                  dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_DESKTOP_USER_OU], 
                                                  sort_key = get_sort_key(dbconst.TB_DESKTOP_USER_OU, req.get("sort_key")),
                                                  reverse = get_reverse(req.get("reverse")),
                                                  offset = req.get("offset", 0),
                                                  limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                                  )
            if user_ou_set:
                user_ou_total_count = ctx.pg.get_count(dbconst.TB_DESKTOP_USER_OU, filter_conditions)
                rep.update({"total_count": user_ou_total_count})
                for user_ou in user_ou_set:
                    user_scope = {
                        "user_id": exclude_user_id,
                        "action_type": -1,
                        "resource_type": dbconst.RESTYPE_USER_OU,
                        "resource_id": user_ou,
                        "ou_dn": user_ou_set[0]
                    }
                    user_scope_set.append(user_scope)
        if dbconst.RESTYPE_DESKTOP_GROUP in resource_type:
            if desktop_groups:
                filter_conditions.update({'desktop_group_id': NotType(desktop_groups)})
            desktop_group_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_GROUP, filter_conditions, 
                                                     dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_DESKTOP_GROUP], 
                                                     sort_key = get_sort_key(dbconst.TB_DESKTOP_GROUP, req.get("sort_key")),
                                                     reverse = get_reverse(req.get("reverse")),
                                                     offset = req.get("offset", 0),
                                                     limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                                     )
            if desktop_group_set:
                desktop_group_total_count = ctx.pg.get_count(dbconst.TB_DESKTOP_GROUP, filter_conditions)
                rep.update({"total_count": desktop_group_total_count})
                for desktop_group in desktop_group_set.keys():
                    user_scope = {
                        "user_id": exclude_user_id,
                        "action_type": -1,
                        "resource_type": dbconst.RESTYPE_DESKTOP_GROUP,
                        "resource_id": desktop_group
                        }
                    user_scope_set.append(user_scope)

        if dbconst.RESTYPE_DESKTOP_NETWORK in resource_type:
            if desktop_networks:
                filter_conditions.update({"network_id": NotType(desktop_networks)})
            network_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_NETWORK, filter_conditions, 
                                               dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_DESKTOP_NETWORK], 
                                               sort_key = get_sort_key(dbconst.TB_DESKTOP_NETWORK, req.get("sort_key")),
                                               reverse = get_reverse(req.get("reverse")),
                                               offset = req.get("offset", 0),
                                               limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                               )
            if network_set:
                desktop_network_total_count = ctx.pg.get_count(dbconst.TB_DESKTOP_NETWORK, filter_conditions)
                rep.update({"total_count": desktop_network_total_count})
                for network in network_set:
                    user_scope = {
                        "user_id": exclude_user_id,
                        "action_type": -1,
                        "resource_type": dbconst.RESTYPE_DESKTOP_NETWORK,
                        "resource_id": network
                        }
                    user_scope_set.append(user_scope)

        if dbconst.RESTYPE_DESKTOP_IMAGE in resource_type:
            if desktop_images:
                filter_conditions.update({"desktop_image_id": NotType(desktop_images)})
            desktop_image_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_IMAGE, filter_conditions, 
                                                     dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_DESKTOP_IMAGE], 
                                                     sort_key = get_sort_key(dbconst.TB_DESKTOP_IMAGE, req.get("sort_key")),
                                                     reverse = get_reverse(req.get("reverse")),
                                                     offset = req.get("offset", 0),
                                                     limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                                     )
            if desktop_image_set:
                desktop_image_total_count = ctx.pg.get_count(dbconst.TB_DESKTOP_IMAGE, filter_conditions)
                rep.update({"total_count": desktop_image_total_count})
                for desktop_image in desktop_image_set:
                    user_scope = {
                        "user_id": exclude_user_id,
                        "action_type": -1,
                        "resource_type": dbconst.RESTYPE_DESKTOP_IMAGE,
                        "resource_id": desktop_image
                        }
                    user_scope_set.append(user_scope)
        if dbconst.RESTYPE_DELIVERY_GROUP in resource_type:
            if delivery_groups:
                filter_conditions.update({"delivery_group_id": NotType(delivery_groups)})
            delivery_group_set = ctx.pg.get_by_filter(dbconst.TB_DELIVERY_GROUP, filter_conditions, 
                                                     dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_DELIVERY_GROUP], 
                                                     sort_key = get_sort_key(dbconst.TB_DELIVERY_GROUP, req.get("sort_key")),
                                                     reverse = get_reverse(req.get("reverse")),
                                                     offset = req.get("offset", 0),
                                                     limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                                     )
            if delivery_group_set:
                delivery_group_total_count = ctx.pg.get_count(dbconst.TB_DELIVERY_GROUP, filter_conditions)
                rep.update({"total_count": delivery_group_total_count})
                for delivery_group in delivery_group_set:
                    user_scope = {
                        "user_id": exclude_user_id,
                        "action_type": -1,
                        "resource_type": dbconst.RESTYPE_DELIVERY_GROUP,
                        "resource_id": delivery_group
                        }
                    user_scope_set.append(user_scope)
        if dbconst.RESTYPE_SNAPSHOT_GROUP in resource_type:
            if desktop_snapshots:
                filter_conditions.update({"snapshot_group_id": NotType(desktop_snapshots)})
            desktop_snapshot_set = ctx.pg.get_by_filter(dbconst.TB_SNAPSHOT_GROUP, filter_conditions, 
                                                     dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_SNAPSHOT_GROUP], 
                                                     sort_key = get_sort_key(dbconst.TB_SNAPSHOT_GROUP, req.get("sort_key")),
                                                     reverse = get_reverse(req.get("reverse")),
                                                     offset = req.get("offset", 0),
                                                     limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                                     )
            if desktop_snapshot_set:
                desktop_snapshot_total_count = ctx.pg.get_count(dbconst.TB_SNAPSHOT_GROUP, filter_conditions)
                rep.update({"total_count": desktop_snapshot_total_count})
                for desktop_snapshot in desktop_snapshot_set:
                    user_scope = {
                        "user_id": exclude_user_id,
                        "action_type": -1,
                        "resource_type": dbconst.RESTYPE_SNAPSHOT_GROUP,
                        "resource_id": desktop_snapshot
                        }
                    user_scope_set.append(user_scope)
        if dbconst.RESTYPE_SCHEDULER_TASK in resource_type:
            if scheduler_tasks:
                filter_conditions.update({"scheduler_task_id": NotType(scheduler_tasks)})
            scheduler_task_set = ctx.pg.get_by_filter(dbconst.TB_SCHEDULER_TASK, filter_conditions, 
                                                     dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_SCHEDULER_TASK], 
                                                     sort_key = get_sort_key(dbconst.TB_SCHEDULER_TASK, req.get("sort_key")),
                                                     reverse = get_reverse(req.get("reverse")),
                                                     offset = req.get("offset", 0),
                                                     limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                                     )
            if scheduler_task_set:
                scheduler_task_total_count = ctx.pg.get_count(dbconst.TB_SCHEDULER_TASK, filter_conditions)
                rep.update({"total_count": scheduler_task_total_count})
                for scheduler_task in scheduler_task_set:
                    user_scope = {
                        "user_id": exclude_user_id,
                        "action_type": -1,
                        "resource_type": dbconst.RESTYPE_SCHEDULER_TASK,
                        "resource_id": scheduler_task
                        }
                    user_scope_set.append(user_scope)
        if dbconst.RESTYPE_POLICY_GROUP in resource_type:
            if policy_groups:
                filter_conditions.update({"policy_group_id": NotType(policy_groups)})
            policy_group_set = ctx.pg.get_by_filter(dbconst.TB_POLICY_GROUP, filter_conditions, 
                                                     dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_POLICY_GROUP], 
                                                     sort_key = get_sort_key(dbconst.TB_POLICY_GROUP, req.get("sort_key")),
                                                     reverse = get_reverse(req.get("reverse")),
                                                     offset = req.get("offset", 0),
                                                     limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                                     )
            if policy_group_set:
                policy_group_total_count = ctx.pg.get_count(dbconst.TB_POLICY_GROUP, filter_conditions)
                rep.update({"total_count": policy_group_total_count})
                for policy_group in policy_group_set:
                    user_scope = {
                        "user_id": exclude_user_id,
                        "action_type": -1,
                        "resource_type": dbconst.RESTYPE_POLICY_GROUP,
                        "resource_id": policy_group
                        }
                    user_scope_set.append(user_scope)
        rep.update({'user_scope_set':user_scope_set})
        return return_success(req, rep)

    action_types = req.get("action_type", [])
    if len(action_types) > 0:
        filter_conditions.update({'action_type': action_types})

    resource_ids = req.get("resources")
    if resource_ids:
        filter_conditions.update({'resource_id': resource_ids})
    
    for key in filter_conditions.keys():
        if not filter_conditions[key]:
            del filter_conditions[key]

    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_ZONE_USER_SCOPE]
    elif is_console_admin_user(sender):
        display_columns = dbconst.CONSOLE_ADMIN_COLUMNS[dbconst.TB_ZONE_USER_SCOPE]
    else:
        display_columns = dbconst.PUBLIC_COLUMNS[dbconst.TB_ZONE_USER_SCOPE]

    user_scope_set = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, filter_conditions, display_columns, 
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                      )
    if user_scope_set is None:
        logger.error("describe desktop group failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    for user_scope in user_scope_set:
        resource_id = user_scope.get("resource_id", None)
        if resource_id:
            res_type = get_resource_type(resource_id)
            if res_type == dbconst.RESTYPE_USER_OU:
                user_group = ctx.pgm.get_user_ous(resource_id)
                if not user_group:
                    user_scope_set.remove(user_scope)
                    logger.info("resource:  [%s]  not found" % resource_id)
                else:
                    user_scope["ou_dn"] = user_group[0]
            elif res_type == dbconst.RESTYPE_DESKTOP_GROUP:
                desktop_group = ctx.pgm.get_desktop_group(desktop_group_id=resource_id)
                if not desktop_group:
                    user_scope_set.remove(user_scope)
                    logger.info("resource:  [%s]  not found" % resource_id)
            elif res_type == dbconst.RESTYPE_DESKTOP_NETWORK:
                networks = ctx.pgm.get_networks(resource_id)
                if not networks:
                    user_scope_set.remove(user_scope)
                    logger.info("resource:  [%s]  not found" % resource_id)
            elif res_type == dbconst.RESTYPE_DESKTOP_IMAGE:
                images = ctx.pgm.get_desktop_images(desktop_image=resource_id)
                if not images:
                    user_scope_set.remove(user_scope)
                    logger.info("resource:  [%s]  not found" % resource_id)
            elif res_type == dbconst.RESTYPE_DELIVERY_GROUP:
                delivery_group = ctx.pgm.get_delivery_groups(delivery_group_ids=resource_id)
                if not delivery_group:
                    user_scope_set.remove(user_scope)
                    logger.info("resource:  [%s]  not found" % resource_id)
            elif res_type == dbconst.RESTYPE_SNAPSHOT_GROUP:
                desktop_snapshot = ctx.pgm.get_snapshot_groups(snapshot_group_ids=resource_id)
                if not desktop_snapshot:
                    user_scope_set.remove(user_scope)
                    logger.info("resource:  [%s]  not found" % resource_id)
            elif res_type == dbconst.RESTYPE_SCHEDULER_TASK:
                scheduler_task = ctx.pgm.get_scheduler_tasks(scheduler_task_ids=resource_id)
                if not scheduler_task:
                    user_scope_set.remove(user_scope)
                    logger.info("resource:  [%s]  not found" % resource_id)
            elif res_type == dbconst.RESTYPE_POLICY_GROUP:
                policy_group = ctx.pgm.get_policy_groups(policy_group_ids=resource_id)
                if not policy_group:
                    user_scope_set.remove(user_scope)
                    logger.info("resource:  [%s]  not found" % resource_id)
            else:
                pass

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_ZONE_USER_SCOPE, filter_conditions)
    if total_count is None:
        logger.error("get desktop count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count,
           'user_scope_set':user_scope_set} 
    return return_success(req, rep)

def handle_describe_api_actions(req):

    sender = req["sender"]
    ctx = context.instance()
    if "resource_type" not in req or not req.get("resource_type"):
        logger.error("parameter miss specified in request [%s]" % (req))
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                                       ErrorMsg.ERR_MSG_MISSING_PARAMETER, "resource_type"))

    resource_type = req.get("resource_type")
    resource_ids = req.get("resources", [])
    req_action_api = req.get("action_api")
    real_action_api = []

    if resource_ids:
        res_type = Permission.check_resource_uuid(resource_ids)
        if res_type != resource_type:
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                           ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, resource_ids))

    action_scope = ctx.pgm.get_scope_action()
    if not action_scope:
        logger.error("action no found")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESCRIBE_USER_SCOPE_ACTIONS))

    # get desktop group set
    filter_conditions = {}
    resource_scope = {}

    if is_global_admin_user(sender):
        if req_action_api:
            real_action_api = []
            for action_api in req_action_api:
                action_id = resource_type + "-0"
                if action_api in action_scope[action_id]:
                    real_action_api.append(action_api)
                    continue
                action_id = resource_type + "-1"
                if action_api in action_scope[action_id]:
                    real_action_api.append(action_api)
                    continue
                action_id = resource_type + "-2"
                if action_api in action_scope[action_id]:
                    real_action_api.append(action_api)
                    continue
                action_id = resource_type + "-3"
                if action_api in action_scope[action_id]:
                    real_action_api.append(action_api)
                    continue
        else:
            real_action_api = req_action_api
        real_action_api = list(set(real_action_api))
        return return_success(req, {"api_action_set":[{"action_api": real_action_api}]})
    else:
        user_id = sender["owner"]
        filter_conditions["user_id"] = user_id
        for req_api in req_action_api:
            if req_api in ACTION_VDI_GLOBAL_ADMIN_WHITE_LIST:
                req_action_api.remove(req_api)

    if not req_action_api:
        logger.error("request action is null.")
        return return_success(req, {"api_action_set":[]})

    filter_conditions['resource_type'] = resource_type
    if resource_ids:
        for resource_id in resource_ids:
            
            conditions = copy.deepcopy(filter_conditions)

            if get_resource_type(resource_id) == dbconst.RESTYPE_USER_OU:
                res_ou_dn = ctx.pgm.get_user_ou_dn(resource_id)
                conds = {
                    "user_id": sender["owner"],
                    "resource_type": dbconst.RESTYPE_USER_OU,
                    "zone_id": sender["zone"]
                    }
                ou_scope_set = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, conds)
                if ou_scope_set:
                    flag = True
                    for ou_scope in ou_scope_set:
                        ou_id = ou_scope["resource_id"]
                        ou_dn = ctx.pgm.get_user_ou_dn(ou_id)
                        if res_ou_dn.find(ou_dn) >= 0:
                            conditions['resource_id'] = ou_id
                            flag = False
                            break
                    if flag:
                        conditions['resource_id'] = resource_id
                else:
                    conditions['resource_id'] = resource_id
            else:
                conditions['resource_id'] = resource_id      
            display_columns = dbconst.PUBLIC_COLUMNS[dbconst.TB_ZONE_USER_SCOPE]

            user_scope_set = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, conditions, display_columns)
            if user_scope_set is None:
                logger.error("user scope no found, conditions:[%s]" % conditions)
                continue

            real_api_list = []
            for user_scope in user_scope_set:
                action_id = "%s-%s" % (resource_type, user_scope["action_type"])
                api_list = action_scope.get(action_id)
                
                real_api_list = []
                if req_action_api:
                    for action in req_action_api:
                        if action in api_list:
                            real_api_list.append(action)
                else:
                    real_api_list = api_list

                
            resource_scope[resource_id] = {"resource_id": resource_id,
                                           "action_api": real_api_list}
        return return_items(req, resource_scope, "api_action")
    else:
        filter_conditions['action_type'] = dbconst.RES_SCOPE_CREATE
        display_columns = ["user_id", "resource_type", "action_type"]
        user_scope_set = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, filter_conditions, display_columns)
        if not user_scope_set:
            return return_success(req, {"api_action_set":[]})

        real_api_list = []
        for user_scope in user_scope_set:
            action_id = "%s-%s" % (resource_type, str(user_scope["action_type"]))
            api_list = action_scope[action_id]
            real_api_list = []
            if req_action_api:
                for action in req_action_api:
                    if action in api_list:
                        real_api_list.append(action)
            else:
                real_api_list = api_list

        return return_success(req, {"api_action_set":[{"action_api": real_api_list}]})

def handle_describe_zone_user_login_record(req):
    ctx = context.instance()
    sender = req["sender"]
    
    # normal user
    if is_normal_user(sender) or is_normal_console(sender):
        logger.error("unsupport normal console.")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_ADMIN_CONSOLE_ONLY))

    # check must parameters
    filter_conditions = build_filter_conditions(req, dbconst.TB_USER_LOGIN_RECORD)

    filter_conditions.update({'zone_id': sender["zone"]})
    if "zones" in req:
        filter_conditions.update({'zone_id': req["zones"]})

    if "users" in req:
        filter_conditions.update({'user_id': req["users"]})
    if "user_login_records" in req:
        filter_conditions.update({'user_login_record_id': req["user_login_records"]})
        
    display_columns = dbconst.PUBLIC_COLUMNS[dbconst.TB_USER_LOGIN_RECORD]
    user_login_set = ctx.pg.get_by_filter(dbconst.TB_USER_LOGIN_RECORD, filter_conditions, display_columns, 
                                    sort_key = get_sort_key(dbconst.TB_USER_LOGIN_RECORD, req.get("sort_key")),
                                    reverse = get_reverse(req.get("reverse")),
                                    offset = req.get("offset", 0),
                                    limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                    )
    if user_login_set is None:
        logger.error("describe user login record failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_USER_LOGIN_RECORD, filter_conditions)
    if total_count is None:
        logger.error("get user count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    rep = {'total_count':total_count}

    return return_items(req, user_login_set, "user", **rep)

