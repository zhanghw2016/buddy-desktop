import context
import constants as const
from log.logger import logger
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.id_tool import get_resource_type
import db.constants as dbconst

from common import (
    is_normal_user,
    is_normal_console,
)
from api.user.user import is_admin_console


action_and_resource_map = {
    # desktop group
    const.ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES: ["desktop_group"],
    const.ACTION_VDI_MODIFY_DESKTOP_GROUP_STATUS: ["desktop_group"],
    const.ACTION_VDI_DELETE_DESKTOP_GROUPS: ["desktop_groups"],
    const.ACTION_VDI_DESCRIBE_DESKTOP_GROUPS: ["desktop_groups"],
    const.ACTION_VDI_APPLY_DESKTOP_GROUP: ["desktop_groups"],
    const.ACTION_VDI_DESCRIBE_DESKTOP_DISKS: ["desktop_group,"],

    # desktop network
    const.ACTION_VDI_DESCRIBE_DESKTOP_NETWORKS: ["networks"],
    const.ACTION_VDI_MODIFY_DESKTOP_NETWORK_ATTRIBUTES: ["network"],
    const.ACTION_VDI_DELETE_DESKTOP_NETWORKS: ["networks"],

    # desktop image
    const.ACTION_VDI_DESCRIBE_DESKTOP_IMAGES: ["desktop_images"],
    const.ACTION_VDI_DELETE_DESKTOP_IMAGES: ["desktop_images"],
    const.ACTION_VDI_MODIFY_DESKTOP_IMAGE_ATTRIBUTES: ["desktop_image"],

    # snapshot
    const.ACTION_VDI_DESCRIBE_SNAPSHOT_GROUPS: ["snapshot_groups"],
    const.ACTION_VDI_MODIFY_SNAPSHOT_GROUP: ["snapshot_group"],
    const.ACTION_VDI_DELETE_SNAPSHOT_GROUPS: ["snapshot_groups"],
    const.ACTION_VDI_ADD_RESOURCE_TO_SNAPSHOT_GROUP: ["snapshot_group"],
    const.ACTION_VDI_DELETE_RESOURCE_FROM_SNAPSHOT_GROUP: ["snapshot_group"],

    # policy group
    const.ACTION_VDI_DESCRIBE_POLICY_GROUPS: ["policy_groups"],
    const.ACTION_VDI_MODIFY_POLICY_GROUP_ATTRIBUTES: ["policy_group"],
    const.ACTION_VDI_DELETE_POLICY_GROUPS: ["policy_groups"],
    const.ACTION_VDI_ADD_RESOURCE_TO_POLICY_GROUP: ["policy_group"],
    const.ACTION_VDI_REMOVE_RESOURCE_FROM_POLICY_GROUP: ["policy_group"],
    const.ACTION_VDI_ADD_POLICY_TO_POLICY_GROUP: ["policy_groups"],
    const.ACTION_VDI_REMOVE_POLICY_FROM_POLICY_GROUP: ["policy_groups"],
    const.ACTION_VDI_APPLY_POLICY_GROUP: ["policy_group"],

    # scheduler
    const.ACTION_VDI_DESCRIBE_SCHEDULER_TASKS: ["scheduler_tasks"],
    const.ACTION_VDI_MODIFY_SCHEDULER_TASK_ATTRIBUTES: ["scheduler_task"],
    const.ACTION_VDI_DELETE_SCHEDULER_TASKS: ["scheduler_tasks"],
    const.ACTION_VDI_DESCRIBE_SCHEDULER_TASK_HISTORY: ["scheduler_task"],
    const.ACTION_VDI_ADD_RESOURCE_TO_SCHEDULER_TASK: ["scheduler_task"],
    const.ACTION_VDI_DELETE_RESOURCE_FROM_SCHEDULER_TASK: ["scheduler_task"],
    const.ACTION_VDI_SET_SCHEDULER_TASK_STATUS: ["scheduler_tasks"],
    const.ACTION_VDI_EXECUTE_SCHEDULER_TASK: ["scheduler_task"],
    const.ACTION_VDI_GET_SCHEDULER_TASK_RESOURCES: ["scheduler_task"],
    const.ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_COUNT: ["scheduler_task"],
    const.ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_IMAGE: ["scheduler_task"],

    # user ou
    const.ACTION_VDI_CREATE_AUTH_OU: "base_dn",
    const.ACTION_VDI_DELETE_AUTH_OU: "ou_dn",
    const.ACTION_VDI_MODIFY_AUTH_OU_ATTRIBUTES: "ou_dn",
    const.ACTION_VDI_DESCRIBE_AUTH_OUS: "base_dn",
    const.ACTION_VDI_CHANGE_AUTH_USER_IN_OU: "new_ou_dn",
    
    # delivery group
    const.ACTION_VDI_MODIFY_DELIVERY_GROUP_ATTRIBUTES: ["delivery_group"],
    const.ACTION_VDI_DELETE_DELIVERY_GROUPS: ["delivery_groups"],
    const.ACTION_VDI_DESCRIBE_DELIVERY_GROUPS: ["delivery_groups"],
}

action_and_resource_type_map = {
    # desktop-group
    dbconst.RESTYPE_DESKTOP_GROUP: [
        # desktop group
        const.ACTION_VDI_CREATE_DESKTOP_GROUP,
        const.ACTION_VDI_CREATE_DESKTOP_GROUP,
        const.ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES,
        const.ACTION_VDI_MODIFY_DESKTOP_GROUP_STATUS,
        const.ACTION_VDI_DELETE_DESKTOP_GROUPS,
        const.ACTION_VDI_DESCRIBE_DESKTOP_GROUPS,


        # desktop group desktop
        const.ACTION_VDI_CREATE_DESKTOP,
        const.ACTION_VDI_DESCRIBE_NORMAL_DESKTOPS,
        const.ACTION_VDI_DESCRIBE_DESKTOPS,
        const.ACTION_VDI_DESCRIBE_DESKTOP_IPS,
        const.ACTION_VDI_APPLY_DESKTOP_GROUP,
        const.ACTION_VDI_CREATE_DESKTOP,
        const.ACTION_VDI_MODIFY_DESKTOP_ATTRIBUTES,
        const.ACTION_VDI_DELETE_DESKTOPS,
        const.ACTION_VDI_ATTACH_USER_TO_DESKTOP,
        const.ACTION_VDI_DETACH_USER_FROM_DESKTOP,
        const.ACTION_VDI_RESTART_DESKTOPS,
        const.ACTION_VDI_START_DESKTOPS,
        const.ACTION_VDI_STOP_DESKTOPS,
        const.ACTION_VDI_RESET_DESKTOPS,
        const.ACTION_VDI_SET_DESKTOP_MONITOR,
        const.ACTION_VDI_SET_DESKTOP_AUTO_LOGIN,
        const.ACTION_VDI_MODIFY_DESKTOP_DESCRIPTION,
        const.ACTION_VDI_CREATE_BROKERS,
        const.ACTION_VDI_DELETE_BROKERS,
        const.ACTION_VDI_DESKTOP_LEAVE_NETWORKS,
        const.ACTION_VDI_DESKTOP_JOIN_NETWORKS,
        const.ACTION_VDI_MODIFY_DESKTOP_IP,
        const.ACTION_VDI_APPLY_RANDOM_DESKTOP,
        const.ACTION_VDI_FREE_RANDOM_DESKTOPS,
        const.ACTION_VDI_CHECK_DESKTOP_HOSTNAME,
        const.ACTION_VDI_CREATE_DESKTOP_SNAPSHOTS,

        # single desktop
        const.ACTION_VDI_CREATE_DESKTOP_DISKS,
        const.ACTION_VDI_DELETE_DESKTOP_DISKS,
        const.ACTION_VDI_ATTACH_DISK_TO_DESKTOP,
        const.ACTION_VDI_DETACH_DISK_FROM_DESKTOP,
        const.ACTION_VDI_DESCRIBE_DESKTOP_DISKS,
        const.ACTION_VDI_RESIZE_DESKTOP_DISKS,
        const.ACTION_VDI_MODIFY_DESKTOP_DISK_ATTRIBUTES,

        # desktop group disk
        const.ACTION_VDI_DESCRIBE_DESKTOP_GROUP_DISKS,
        const.ACTION_VDI_CREATE_DESKTOP_GROUP_DISK,
        const.ACTION_VDI_MODIFY_DESKTOP_GROUP_DISK,
        const.ACTION_VDI_DELETE_DESKTOP_GROUP_DISKS,

        # desktop group network
        const.ACTION_VDI_DESCRIBE_DESKTOP_GROUP_NETWORKS,
        const.ACTION_VDI_CREATE_DESKTOP_GROUP_NETWORK,
        const.ACTION_VDI_MODIFY_DESKTOP_GROUP_NETWORK,
        const.ACTION_VDI_DELETE_DESKTOP_GROUP_NETWORKS,
        
        # desktop group user
        const.ACTION_VDI_DESCRIBE_DESKTOP_GROUP_USERS,
        const.ACTION_VDI_ATTACH_USER_TO_DESKTOP_GROUP,
        const.ACTION_VDI_DETACH_USER_FROM_DESKTOP_GROUP,
        const.ACTION_VDI_SET_DESKTOP_GROUP_USER_STATUS,
        
        ],

    # desktop group
    dbconst.RESTYPE_DESKTOP_NETWORK:[
        const.ACTION_VDI_CREATE_DESKTOP_NETWORK,
        const.ACTION_VDI_DESCRIBE_DESKTOP_NETWORKS,
        const.ACTION_VDI_MODIFY_DESKTOP_NETWORK_ATTRIBUTES,
        const.ACTION_VDI_DELETE_DESKTOP_NETWORKS,
        const.ACTION_VDI_DESCRIBE_SYSTEM_NETWORKS,
        const.ACTION_VDI_LOAD_SYSTEM_NETWORK,
        ],

    # image
    dbconst.RESTYPE_DESKTOP_IMAGE: [
        const.ACTION_VDI_CREATE_DESKTOP_IMAGE,
        const.ACTION_VDI_SAVE_DESKTOP_IMAGES,
        const.ACTION_VDI_DESCRIBE_DESKTOP_IMAGES,
        const.ACTION_VDI_DELETE_DESKTOP_IMAGES,
        const.ACTION_VDI_MODIFY_DESKTOP_IMAGE_ATTRIBUTES,
        const.ACTION_VDI_DESCRIBE_SYSTEM_IMAGES,
        const.ACTION_VDI_LOAD_SYSTEM_IMAGES,
        ],

    # snapshot
    dbconst.RESTYPE_SNAPSHOT_GROUP:[
        const.ACTION_VDI_DESCRIBE_DESKTOP_SNAPSHOTS,
        const.ACTION_VDI_DELETE_DESKTOP_SNAPSHOTS,
        const.ACTION_VDI_APPLY_DESKTOP_SNAPSHOTS,
        const.ACTION_VDI_MODIFY_DESKTOP_SNAPSHOT_ATTRIBUTES,
        const.ACTION_VDI_CAPTURE_DESKTOP_FROM_DESKTOP_SNAPSHOT,
        const.ACTION_VDI_CREATE_DISK_FROM_DESKTOP_SNAPSHOT,
        
        const.ACTION_VDI_DESCRIBE_SNAPSHOT_GROUPS,
        const.ACTION_VDI_CREATE_SNAPSHOT_GROUP,
        const.ACTION_VDI_MODIFY_SNAPSHOT_GROUP,
        const.ACTION_VDI_DELETE_SNAPSHOT_GROUPS,
        const.ACTION_VDI_ADD_RESOURCE_TO_SNAPSHOT_GROUP,
        const.ACTION_VDI_DELETE_RESOURCE_FROM_SNAPSHOT_GROUP,
        const.ACTION_VDI_DESCRIBE_SNAPSHOT_GROUP_SNAPSHOTS,
        ],

    # security group
    dbconst.RESTYPE_POLICY_GROUP: [
        const.ACTION_VDI_DESCRIBE_POLICY_GROUPS,
        const.ACTION_VDI_CREATE_POLICY_GROUP,
        const.ACTION_VDI_MODIFY_POLICY_GROUP_ATTRIBUTES,
        const.ACTION_VDI_DELETE_POLICY_GROUPS,
        const.ACTION_VDI_ADD_RESOURCE_TO_POLICY_GROUP,
        const.ACTION_VDI_REMOVE_RESOURCE_FROM_POLICY_GROUP,
        const.ACTION_VDI_ADD_POLICY_TO_POLICY_GROUP,
        const.ACTION_VDI_REMOVE_POLICY_FROM_POLICY_GROUP,
        const.ACTION_VDI_APPLY_POLICY_GROUP,
        const.ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_POLICYS,
        const.ACTION_VDI_CREATE_DESKTOP_SECURITY_POLICY,
        const.ACTION_VDI_MODIFY_DESKTOP_SECURITY_POLICY_ATTRIBUTES,
        const.ACTION_VDI_DELETE_DESKTOP_SECURITY_POLICYS,
        const.ACTION_VDI_APPLY_DESKTOP_SECURITY_POLICY,
        const.ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_RULES,
        const.ACTION_VDI_ADD_DESKTOP_SECURITY_RULES,
        const.ACTION_VDI_REMOVE_DESKTOP_SECURITY_RULES,
        const.ACTION_VDI_MODIFY_DESKTOP_SECURITY_RULE_ATTRIBUTES,
        const.ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_IPSETS,
        const.ACTION_VDI_CREATE_DESKTOP_SECURITY_IPSET,
        const.ACTION_VDI_DELETE_DESKTOP_SECURITY_IPSETS,
        const.ACTION_VDI_MODIFY_DESKTOP_SECURITY_IPSET_ATTRIBUTES,
        const.ACTION_VDI_APPLY_DESKTOP_SECURITY_IPSET,
        const.ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_POLICYS,
        const.ACTION_VDI_LOAD_SYSTEM_SECURITY_RULES,
        const.ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_IPSETS,
        const.ACTION_VDI_LOAD_SYSTEM_SECURITY_IPSETS,

        ],

    # scheduler
    dbconst.RESTYPE_SCHEDULER_TASK: [
        const.ACTION_VDI_DESCRIBE_SCHEDULER_TASKS,
        const.ACTION_VDI_CREATE_SCHEDULER_TASK,
        const.ACTION_VDI_MODIFY_SCHEDULER_TASK_ATTRIBUTES,
        const.ACTION_VDI_DELETE_SCHEDULER_TASKS,
        const.ACTION_VDI_DESCRIBE_SCHEDULER_TASK_HISTORY,
        const.ACTION_VDI_ADD_RESOURCE_TO_SCHEDULER_TASK,
        const.ACTION_VDI_DELETE_RESOURCE_FROM_SCHEDULER_TASK,
        const.ACTION_VDI_SET_SCHEDULER_TASK_STATUS,
        const.ACTION_VDI_EXECUTE_SCHEDULER_TASK,
        const.ACTION_VDI_GET_SCHEDULER_TASK_RESOURCES,
        const.ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_COUNT,
        const.ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_IMAGE,
        ],

    # user ou
    dbconst.RESTYPE_USER_OU: [
        const.ACTION_VDI_CREATE_AUTH_USER,
        const.ACTION_VDI_DELETE_AUTH_USERS,
        const.ACTION_VDI_MODIFY_AUTH_USER_ATTRIBUTES,
        const.ACTION_VDI_DESCRIBE_AUTH_USERS,
        const.ACTION_VDI_MODIFY_AUTH_USER_PASSWORD,
        const.ACTION_VDI_RESET_AUTH_USER_PASSWORD,
        const.ACTION_VDI_IMPORT_AUTH_USERS,
        
        const.ACTION_VDI_CREATE_AUTH_OU,
        const.ACTION_VDI_DELETE_AUTH_OU,
        const.ACTION_VDI_MODIFY_AUTH_OU_ATTRIBUTES,
        const.ACTION_VDI_DESCRIBE_AUTH_OUS,
        const.ACTION_VDI_CHANGE_AUTH_USER_IN_OU,
        
        const.ACTION_VDI_CREATE_AUTH_USER_GROUP,
        const.ACTION_VDI_MODIFY_AUTH_USER_GROUP_ATTRIBUTES,
        const.ACTION_VDI_DELETE_AUTH_USER_GROUPS,
        const.ACTION_VDI_DESCRIBE_AUTH_USER_GROUPS,
        const.ACTION_VDI_ADD_AUTH_USER_TO_USER_GROUP,
        const.ACTION_VDI_REMOVE_AUTH_USER_FROM_USER_GROUP,
        const.ACTION_VDI_RENAME_AUTH_USER_DN,
        ],

    # delivery group
    dbconst.RESTYPE_DELIVERY_GROUP:[
        const.ACTION_VDI_DESCRIBE_DELIVERY_GROUPS,
        const.ACTION_VDI_CREATE_DELIVERY_GROUP,
        const.ACTION_VDI_MODIFY_DELIVERY_GROUP_ATTRIBUTES,
        const.ACTION_VDI_DELETE_DELIVERY_GROUPS,
        const.ACTION_VDI_LOAD_DELIVERY_GROUPS,
        const.ACTION_VDI_ADD_DESKTOP_TO_DELIVERY_GROUP,
        const.ACTION_VDI_DEL_DESKTOP_FROM_DELIVERY_GROUP,
        const.ACTION_VDI_ADD_USER_TO_DELIVERY_GROUP,
        const.ACTION_VDI_DEL_USER_FROM_DELIVERY_GROUP,
        const.ACTION_VDI_ATTACH_DESKTOP_TO_DELIVERY_GROUP_USER,
        const.ACTION_VDI_DETACH_DESKTOP_FROM_DELIVERY_GROUP_USER,
        const.ACTION_VDI_SET_DELIVERY_GROUP_MODE,
        const.ACTION_VDI_SET_CITRIX_DESKTOP_MODE,
        ],    
}

READONLY_API_RETURN_DATA_SET = {
    const.ACTION_VDI_DESCRIBE_DESKTOP_GROUPS: "desktop_group_set",
    const.ACTION_VDI_DESCRIBE_DESKTOPS: "desktop_set",
    const.ACTION_VDI_DESCRIBE_NORMAL_DESKTOPS: "desktop_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_GROUP_DISKS: "disk_config_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_GROUP_NETWORKS: "network_config_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_GROUP_USERS: "desktop_group_user_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_IPS: "desktop_ip_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_DISKS: "disk_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_NETWORKS: "desktop_network_set",
    const.ACTION_VDI_DESCRIBE_SYSTEM_NETWORKS: "system_network_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_IMAGES: "desktop_image_set",
    const.ACTION_VDI_DESCRIBE_SYSTEM_IMAGES: "image_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_SNAPSHOTS: "desktop_snapshot_set",
    const.ACTION_VDI_DESCRIBE_SNAPSHOT_GROUPS: "snapshot_group_set",
    const.ACTION_VDI_DESCRIBE_SNAPSHOT_GROUP_SNAPSHOTS: "snapshot_group_snapshots_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_POLICYS: "security_policy_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_RULES: "security_rule_set",
    const.ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_IPSETS: "security_ipset_set",
    const.ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_POLICYS : "security_policy_set",
    const.ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_IPSETS: "security_ipset_set",
    const.ACTION_VDI_DESCRIBE_POLICY_GROUPS: "delivery_group_set",
    const.ACTION_VDI_DESCRIBE_SCHEDULER_TASKS: "scheduler_task_set",
    const.ACTION_VDI_DESCRIBE_SCHEDULER_TASK_HISTORY: "scheduler_task_history_set",
    const.ACTION_VDI_DESCRIBE_ZONE_USERS: "user_set",
    const.ACTION_VDI_DESCRIBE_AUTH_USERS: "auth_user_set",
    const.ACTION_VDI_DESCRIBE_AUTH_OUS: "auth_ou_set",
    const.ACTION_VDI_DESCRIBE_AUTH_USER_GROUPS: "auth_user_group_set",
    const.ACTION_VDI_DESCRIBE_DELIVERY_GROUPS: "delivery_group_set",
    }

def _get_resource_type(action):
    for res_type in action_and_resource_type_map.keys():
        if action in action_and_resource_type_map[res_type]:
            return res_type
    return None

def _get_action_type(resource_type, action):
    action_type = -1

    ctx = context.instance()
    for res_scope in dbconst.RES_SCOPE_LIST:
        action_id = "%s-%d" % (resource_type, res_scope);
        conds = {
            "action_id": action_id,
            "action_api": action
            }
        ret = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE_ACTION, conds)
        if ret:
            action_type = res_scope
            break

    return action_type

def check_resource_uuid(resource_ids):
    resource_type = None
    for resource_id in resource_ids:
        rt = get_resource_type(resource_id)
        if resource_type is None:
            resource_type = rt
        if resource_type != rt:
            return None
    return resource_type

def register_user_resource_scope(user_id, resource_type, resource_id, zone_id, action_type=dbconst.RES_SCOPE_DELETE):
    ''' set user perssion scope, when resource is created '''

    ctx = context.instance()
    if not user_id or not resource_type or not resource_id:
        logger.error("parameter error.")
        return False

    if user_id == const.GLOBAL_ADMIN_USER_ID or user_id=='system':
        return True

    action_info = {'user_id': user_id}
    action_info['resource_type'] = resource_type
    action_info['resource_id'] = resource_id
    action_info['action_type'] = action_type
    action_info['zone_id'] = zone_id
    # check resource existed
    conditions = {
                  "user_id": user_id,
                  "resource_id": resource_id
                  }
    res_scope = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, conditions)
    if res_scope:
        update_info = {
                       "resource_type": resource_type,
                       "action_type": action_type
                       }
        
        if not ctx.pg.base_update(dbconst.TB_ZONE_USER_SCOPE, conditions, update_info):
            logger.error("update user scope error,conditions=%s, update_info=%s" % (conditions, update_info))
            return False
    else:
        try:
            if not ctx.pg.insert(dbconst.TB_ZONE_USER_SCOPE, action_info):
                logger.error("insert user scope error, action_info=%s" % action_info)
                return False
        except Exception,e:
            logger.error('insert user scope with Exception: %s' % e)
            return False
    
    return True

def clear_user_scope_resource_action(user_ids,zone_ids):
    ''' clear user perssion scope, when user is deleted'''
    if not user_ids:
        return False

    condition = {'user_id': user_ids,'zone_id':zone_ids}

    ctx = context.instance()
    try:
        ret = ctx.pg.base_delete(dbconst.TB_ZONE_USER_SCOPE, condition, True)
        if ret < 0:
            return False
    except Exception,e:
        logger.error('delete user scope with Exception: %s' % e)
        return False
    
    return True

def clear_user_resource_scope(resource_ids=None, user_ids=None):

    ''' clear resource ids, when resources is deleted '''
    if not resource_ids and not user_ids:
        return False

    condition = {}
    if resource_ids:
        condition["resource_id"] = resource_ids
 
    if user_ids:
        condition["user_id"] = user_ids
    
    ctx = context.instance()
    try:
        ret = ctx.pg.base_delete(dbconst.TB_ZONE_USER_SCOPE, condition, False)
        if ret < 0:
            return False

    except Exception,e:
        logger.error('delete user scope with Exception: %s' % e)
        return False
    
    return True

def check_user_resource_permission(sender, resource_type, resource_ids=None, action_type=dbconst.RES_SCOPE_READONLY):

    ''' check if request sender can access resource '''
    if resource_ids and not isinstance(resource_ids, list):
        resource_ids = [resource_ids]

    ctx = context.instance()

    # check resource id
    if resource_ids:
        real_res_type = check_resource_uuid(resource_ids)
        if real_res_type is None:
            logger.error("resource_ids [%s] is not same resource type [%s]." % (resource_ids, resource_type))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_TYPE_NOT_MATCH, resource_ids)

    if is_admin_console(sender) and is_normal_user(sender):
        return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_PRIVILEGE_ACCESS_DENIED)

    # normal console
    if is_normal_console(sender):
        return None

    # admin console and admin user 
    user_scope_resource_ids = ctx.pgm.get_user_scope_resource_ids(zone_id=sender['zone'], 
                                                                  user_id=sender['owner'], 
                                                                  resource_type=resource_type, 
                                                                  action_type=action_type)
    if not user_scope_resource_ids:
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESCRIBE_USER_SCOPE_ERROR)

    if not resource_ids:
        return user_scope_resource_ids
    else:
        for resource_id in resource_ids:
            if resource_id not in user_scope_resource_ids:
                resource_ids.remove(resource_id)
        if not resource_ids:
            return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_PRIVILEGE_ACCESS_DENIED)
        return resource_ids

def check_user_resource_create_permission(sender, resource_type):

    ctx = context.instance()
    conditions = {
        "zone_id": sender["zone"],
        "user_id": sender["owner"],
        "resource_type": resource_type,
        "action_type": 0
        }

    create_scopes = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, conditions)
    if not create_scopes:
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_PRIVILEGE_CANT_CREATE_DENIED)
    return True

def check_user_ou_permission(req, base_dn, action_type):
    ctx = context.instance()
    sender = req["sender"]

    if base_dn is None:
        return False

    base_dn = base_dn.replace("OU=", "ou=").replace("Ou=", "ou=").replace("oU=", "ou=")
    base_dn = base_dn.replace("DC=", "dc=").replace("Dc=", "dc=").replace("dC=", "dc=")

    conditions = {
        "user_id": sender["owner"],
        "resource_type": dbconst.RESTYPE_USER_OU,
        "zone_id": sender["zone"]
        }
    if action_type >= 0:
        action_types = []
        for i in range(action_type, dbconst.RES_SCOPE_DELETE+1):
            action_types.append(i)
        conditions["action_type"] = action_types

    resources = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, conditions, columns={"resource_id"})
    if resources is None or len(resources) == 0:
        return False

    for res in resources:
        ou_dn = ctx.pgm.get_user_ou_dn(res["resource_id"])
        if ou_dn and base_dn.find(ou_dn) >=0:
            return True

    return False

def check_user_scope_permission(req):
    action = req["action"]
    sender = req["sender"]
    param_names = action_and_resource_map.get(action)
    resource_type = _get_resource_type(action)
    action_type = _get_action_type(resource_type, action)

    if action_type < 0:
        return True

    if action_type == dbconst.RES_SCOPE_CREATE:
        return check_user_resource_create_permission(sender, resource_type)

    if param_names is None:
        return True

    if resource_type == dbconst.RESTYPE_USER_OU:
        if check_user_ou_permission(req, req.get(param_names), action_type):
            return True
        else:
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_PERMISSION_DENIED_WITH_REASON, "Unauthorized")

    main_res = True
    for param_name in param_names:
        resource_ids = req.get(param_name)
        is_str = False
        copy_resource_ids = resource_ids
        if main_res:
            if isinstance(resource_ids, str):
                is_str = True
            resources = check_user_resource_permission(sender, resource_type, resource_ids, action_type)
            if isinstance(resources, Error):
                return resources
            if resources:
                if is_str:
                    req[param_name] = copy_resource_ids
                else:
                    req[param_name] = resources
        else:
            if resource_ids:
                resources = check_user_resource_permission(sender, resource_type, resource_ids, action_type)
                if isinstance(resources, Error):
                    return resources
                if resources:
                    if is_str:
                        req[param_name] = copy_resource_ids
                    else:
                        req[param_name] = resources
        main_res = False
    return True
