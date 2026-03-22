from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
from utils.id_tool import(
    UUID_TYPE_POLICY_GROUP,
    UUID_TYPE_SNAPHSOT_GROUP,
    UUID_TYPE_DESKTOP_GROUP,
    UUID_TYPE_DELIVERY_GROUP
)
import constants as const
from utils.id_tool import(
    get_uuid
)

from common import (
    check_resource_transition_status,
    check_global_admin_console,
)
from utils.misc import get_current_time
import resource_control.desktop.job as Job
import resource_control.policy.security_policy as SecurityPolicy

def policy_adapter(policy_group):
    
    ctx = context.instance()

    if not isinstance(policy_group, dict):
        policy_group = ctx.pgm.get_policy_group(policy_group)
        if not policy_group:
            return None

    policy_group_type = policy_group["policy_group_type"]
    if policy_group_type == const.POLICY_TYPE_SECURITY:
        return SecurityPolicy
    
    return None

def format_policy_groups(policy_group_set):
    
    ctx = context.instance()
    if not policy_group_set:
        return None
        
    for policy_group_id, policy_group in policy_group_set.items():
        
        policy_adapter(policy_group).format_policy_group(policy_group)
        
        resource_group = ctx.pgm.get_policy_resource_group(policy_group_id)
        if not resource_group:
            resource_group = {}
        policy_group["resource_group"] = resource_group.values()
        
    return None

def check_policy_group_vaild(policy_group_ids, check_trans=True):
    
    ctx = context.instance()
    if not isinstance(policy_group_ids, list):
        policy_group_ids = [policy_group_ids]
    
    policy_groups = ctx.pgm.get_policy_groups(policy_group_ids)
    if not policy_groups:
        logger.error("check policy group no found policy group %s" % policy_group_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
    for policy_group_id in policy_group_ids:
        if policy_group_id not in policy_groups:
            logger.error("check policy group no found policy group %s" % policy_group_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
    # check policy grouup transition status
    if check_trans:
        ret = check_resource_transition_status(policy_groups)
        if isinstance(ret, Error):
            return ret

    return policy_groups

def check_policy_group_resource(policy_group, resource_ids, is_add=False, is_remove=False):
    
    if not isinstance(resource_ids, list):
        resource_ids = [resource_ids]

    policy_group_type = policy_group["policy_group_type"]
    support_resource_type = const.POLICY_GROUP_RESOURCE_MAP.get(policy_group_type)
    if not support_resource_type:
        logger.error("unsupported policy group type %s" % (policy_group_type))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_POLICY_GROUP_TYPE_UNSUPPORTED, (policy_group_type))

    for resource_id in resource_ids:
        prefix = resource_id.split("-")[0]
        if prefix not in support_resource_type:
            logger.error("policy group %s dont support resource %s" % (policy_group_type, resource_id))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_POLICY_GROUP_TYPE_DISMATCH_RESOURCE, (policy_group_type, resource_id))
    
    ret = check_policy_group_resource_vaild(policy_group, resource_ids, is_add, is_remove)
    if isinstance(ret, Error):
        return ret

    return None

def check_policy_group_policy(policy_group, policy_ids, is_add=False, is_remove=False):

    if not isinstance(policy_ids, list):
        policy_ids = [policy_ids]
    
    policy_group_type = policy_group["policy_group_type"]
    support_policy_type = const.POLICY_GROUP_POLICY_MAP.get(policy_group_type)
    if not support_policy_type:
        logger.error("unsupport policy group type %s" % (policy_group_type))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_POLICY_GROUP_TYPE_UNSUPPORTED, (policy_group_type))
    
    for policy_id in policy_ids:
        prefix = policy_id.split("-")[0]
        if prefix not in support_policy_type:
            logger.error("policy group %s dont support policy %s" % (policy_group_type, policy_id))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_POLICY_GROUP_TYPE_DISMATCH_RESOURCE, (policy_group_type, policy_id))
    
    ret = check_policy_group_policy_vaild(policy_group, policy_ids, is_add, is_remove)
    if isinstance(ret, Error):
        return ret

    return None

def register_policy_group(sender, group_info):

    ctx = context.instance()

    policy_group_type = group_info["policy_group_type"]
    policy_group_id = get_uuid(UUID_TYPE_POLICY_GROUP, ctx.checker)
    policy_group_info = dict(
                              policy_group_id = policy_group_id,
                              policy_group_name = group_info.get("policy_group_name", ''),
                              policy_group_type = policy_group_type,
                              description = group_info.get("description", ''),
                              create_time = get_current_time(),
                              status = "active",
                              is_default = group_info.get("is_default", 0),
                              zone = sender["zone"]                              
                              )
    # register desktop group
    if not ctx.pg.insert(dbconst.TB_POLICY_GROUP, policy_group_info):
        logger.error("insert newly created policy group for [%s] to db failed" % (policy_group_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    ret = init_policy_group(sender, policy_group_info)
    if isinstance(ret, Error):
        ctx.pg.delete(dbconst.TB_POLICY_GROUP, policy_group_id)
        return ret

    return policy_group_id

def modify_policy_group_attributes(sender, policy_group, need_maint_columns):

    ctx = context.instance()
    policy_group_id = policy_group["policy_group_id"]

    ret = policy_adapter(policy_group).modify_policy_group_attributes(sender, policy_group, need_maint_columns)
    if isinstance(ret, Error):
        return ret

    if not ctx.pg.batch_update(dbconst.TB_POLICY_GROUP, {policy_group_id: need_maint_columns}):
        logger.error("modify policy group update f DB fail %s" % policy_group_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def check_delete_policy_groups(sender, policy_groups):
    
    ctx = context.instance()
    for policy_group_id, _ in policy_groups.items():
        
        ret = ctx.pgm.get_policy_group_resource(policy_group_id)
        if ret:
            logger.error("policy group has resource, cant delete" % (policy_group_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_POLICY_GROUP_HAS_RESOURCE_CANT_DELETE, policy_group_id)
        
        ret = ctx.pgm.get_policy_group_policy(policy_group_id)
        if not ret:
            continue

        security_policy_ids = ret.keys()
        ret = ctx.pgm.get_security_policys(security_policy_ids, security_policy_type= const.SEC_POLICY_TYPE_SAHRE)
        if ret:
            if not check_global_admin_console(sender):
                logger.error("policy group has share policy, cant delete" % (policy_group_id))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_SHARE_POLICY_ADMIN_CANT_DELETE, policy_group_id)

    return None

def delete_policy_groups(sender, policy_groups):

    ctx = context.instance()

    for policy_group_id, policy_group in policy_groups.items():

        ret = remove_policy_from_policy_group(sender, policy_group)
        if isinstance(ret, Error):
            return ret
        
        ret = delete_policy_group(sender, policy_group)
        if isinstance(ret, Error):
            return ret

        ctx.pg.delete(dbconst.TB_POLICY_GROUP, policy_group_id)

    return None

def format_desktop_policy(desktop_policy_set):
    
    ctx = context.instance()
    desktop_policys = {}
    for policy_type, policy_id in desktop_policy_set.items():
        
        desktop_policys[policy_type] = {}
        
        if policy_type == const.POLICY_TYPE_SECURITY:
            ret = ctx.pgm.get_policy_group(policy_id)
            if not ret:
                ret = {}
            
            desktop_policys[policy_type] = ret
        
        elif policy_type == const.POLICY_TYPE_SNAPSHOT:
            ret = ctx.pgm.get_snapshot_group(policy_id)
            if not ret:
                ret = {}
            policy = {}
            policy["policy_group_id"] = ret["snapshot_group_id"]
            policy["policy_group_name"] = ret["snapshot_group_name"]
            
            desktop_policys[policy_type] = policy
    return desktop_policys

def get_desktop_resource(resource_id, policy_id, is_delete=False):
    
    ctx = context.instance()

    policy_resource = {}
    if policy_id.startswith(UUID_TYPE_POLICY_GROUP):
        ret = ctx.pgm.get_policy_group_resource(policy_id, policy_group_type=const.POLICY_TYPE_SECURITY)
        if ret:
            policy_resource = ret
    elif policy_id.startswith(UUID_TYPE_SNAPHSOT_GROUP):
        ret = ctx.pgm.get_snapshot_group_resources(policy_id)
        if ret:
            policy_resource = ret
    
    if is_delete:
        return policy_resource

    resource_desktop = {}
    if resource_id.startswith(UUID_TYPE_DESKTOP_GROUP):
        ret = ctx.pgm.get_desktops(desktop_group_ids=resource_id)
        if ret:
            resource_desktop = ret
    
    elif resource_id.startswith(UUID_TYPE_DELIVERY_GROUP):
        ret = ctx.pgm.get_desktops(delivery_group_id=resource_id)
        if ret:
            resource_desktop = ret
    
    add_desktops = []
    for desktop_id, _ in resource_desktop.items():
        if desktop_id in policy_resource:
            continue
        
        add_desktops.append(desktop_id)
    
    return add_desktops

def check_resource_group_type(resource_group_id):
    
    ctx = context.instance()
    resource_type = dbconst.RESTYPE_DESKTOP_GROUP
    if resource_group_id.startswith(UUID_TYPE_DESKTOP_GROUP):
        ret = ctx.pgm.get_desktop_group(resource_group_id, extras=[])
        if not ret:
            logger.error("desktop group no found %s" % resource_group_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    elif resource_group_id.startswith(UUID_TYPE_DELIVERY_GROUP):
        ret = ctx.pgm.get_delivery_group(resource_group_id)
        if not ret:
            logger.error("desktop group no found %s" % resource_group_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
        resource_type = dbconst.RESTYPE_DELIVERY_GROUP
    else:
        logger.error("desktop group no found %s" % resource_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
        
    return resource_type

def check_policy_group_type(policy_groups):
    
    ctx = context.instance()
    for policy_group_type, policy_group_id in policy_groups.items():
        
        if not policy_group_id:
            continue
        
        if policy_group_type == const.POLICY_TYPE_SECURITY:
            ret = ctx.pgm.get_policy_group(policy_group_id)
            if not ret:
                logger.error("policy group no found %s" % policy_group_id)
                return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                             ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

        elif policy_group_type == const.POLICY_TYPE_SNAPSHOT:
            ret = ctx.pgm.get_snapshot_group(policy_group_id)
            if not ret:
                logger.error("policy group no found %s" % policy_group_id)
                return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                             ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
        else:
            logger.error("policy group no found %s" % policy_group_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
    return None

def check_resource_group_policy(resource_group_id, policy_groups):
    
    ctx = context.instance()

    curr_policys = ctx.pgm.get_resource_group_policy(resource_group_id)
    if not curr_policys:
        curr_policys = {}
    
    check_policys = {}
    for policy_group_id in policy_groups:
        policy_group_list = policy_group_id.split("|")
        if not policy_group_list:
            continue
        policy_group_type = policy_group_list[0]
        if len(policy_group_list) < 2 or not policy_group_list[1]:
            check_policys[policy_group_type] = ""
            continue
        
        curr_policy_id = curr_policys.get(policy_group_type)
        if curr_policy_id == policy_group_list[1]:
            continue
        
        check_policys[policy_group_type] = policy_group_list[1]
    
    ret = check_policy_group_type(check_policys)
    if isinstance(ret, Error):
        return ret
    
    return check_policys

def delete_resource_group_policy(sender, resource_group_id, policy_group_type, curr_policys):
    
    ctx = context.instance()
    policy_group_id = curr_policys.get(policy_group_type)
    if not policy_group_id:
        return None
    
    policy_group = ctx.pgm.get_policy_group(policy_group_id)
    if not policy_group:
        return None
    
    resource_ids = []
    if resource_group_id.startswith(UUID_TYPE_DESKTOP_GROUP):
        ret = ctx.pgm.get_desktops(desktop_group_ids=resource_group_id)
        if ret:
            resource_ids.extend(ret.keys())
    elif resource_group_id.startswith(UUID_TYPE_DELIVERY_GROUP):
        ret = ctx.pgm.get_desktops(delivery_group_id=resource_group_id)
        if ret:
            resource_ids.extend(ret.keys())
    
    ret = ctx.pgm.get_group_resources(resource_ids, is_lock=0)
    if not ret:
        return None
    resource_ids = ret
    
    if not resource_ids:
        return None

    ret = remove_resource_from_policy_group(sender, policy_group, resource_ids)
    if isinstance(ret, Error) or not ret:
        return ret
    _, job_uuid = ret

    return job_uuid

def add_resource_group_policy(sender, policy_group_id, resource_group_id, resource_group_type, policy_group_type):

    ctx = context.instance()
    
    policy_group = ctx.pgm.get_policy_group(policy_group_id)
    if not policy_group:
        return None
    
    new_info = {
        "policy_group_id": policy_group_id,
        "resource_group_id": resource_group_id,
        "resource_group_type": resource_group_type,
        "policy_group_type": policy_group_type
        }
    
    if not ctx.pg.insert(dbconst.TB_POLICY_RESOURCE_GROUP, new_info):
        logger.error("insert newly created policy group for [%s] to db failed" % (new_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    delivery_group_policys = ctx.pgm.get_policy_resource_groups(dbconst.RESTYPE_DELIVERY_GROUP)
    if not delivery_group_policys:
        delivery_group_policys = {}

    resource_ids = []
    if resource_group_type == dbconst.RESTYPE_DELIVERY_GROUP:
        ret = ctx.pgm.get_desktops(delivery_group_id=resource_group_id)
        if ret:
            resource_ids.extend(ret.keys())
    elif resource_group_type == dbconst.RESTYPE_DESKTOP_GROUP:
        ret = ctx.pgm.get_desktops(desktop_group_ids=resource_group_id)
        if ret:
            for desktop_id, desktop in ret.items():
                delivery_group_id = desktop.get("delivery_group_id")
                if delivery_group_id and delivery_group_id in delivery_group_policys:
                    continue
                
                resource_ids.append(desktop_id)

    existed_resource_ids = ctx.pgm.get_group_resources(resource_ids, is_lock=1)
    if not existed_resource_ids:
        existed_resource_ids = []

    new_resource_ids = []
    for resource_id in resource_ids:
        if resource_id in existed_resource_ids:
            continue
        new_resource_ids.append(resource_id)

    if not new_resource_ids:
        return None

    ret = add_resource_to_policy_group(sender, policy_group, new_resource_ids)
    if isinstance(ret, Error) or not ret:
        return ret
    if ret:
        job_uuid = ret

    return job_uuid

def change_resource_group_policy(sender, resource_group_id, policy_group_id, resource_group_type, policy_group_type, check_lock=True):

    ctx = context.instance()
    
    policy_group = ctx.pgm.get_policy_group(policy_group_id)
    if not policy_group:
        return None
    
    condition = {"resource_group_id": resource_group_id, "policy_group_type": policy_group_type}
    if not ctx.pg.base_update(dbconst.TB_POLICY_RESOURCE_GROUP, condition, {"policy_group_id": policy_group_id}):
        logger.error("modify policy group update f DB fail %s" % policy_group_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    delivery_group_policys = ctx.pgm.get_policy_resource_groups(dbconst.RESTYPE_DELIVERY_GROUP)
    if not delivery_group_policys:
        delivery_group_policys = {}
        
    resource_ids = []
    if resource_group_type == dbconst.RESTYPE_DELIVERY_GROUP:
        ret = ctx.pgm.get_desktops(delivery_group_id=resource_group_id)
        if ret:
            resource_ids.extend(ret.keys())
    elif resource_group_type == dbconst.RESTYPE_DESKTOP_GROUP:
        ret = ctx.pgm.get_desktops(desktop_group_ids=resource_group_id)
        if ret:
            for desktop_id, desktop in ret.items():
                delivery_group_id = desktop.get("delivery_group_id")
                if delivery_group_id and delivery_group_id in delivery_group_policys:
                    continue
                
                resource_ids.append(desktop_id)
    
    if not resource_ids:
        return None
    
    if check_lock:
        ret = ctx.pgm.get_group_resources(resource_ids, is_lock=0)
        if not ret:
            return None
        resource_ids = ret
    
    if not resource_ids:
        return None
    
    ret = change_resource_to_policy_group(sender, policy_group, resource_ids)
    if isinstance(ret, Error) or not ret:
        return ret
    if ret:
        job_uuid = ret

    return job_uuid

def delete_resource_from_policy_group(sender, resource_ids, policy_group_id=None):

    ctx = context.instance()
    
    ret = ctx.pgm.get_policy_group_resource(policy_group_id, resource_ids=resource_ids)
    if not ret:
        return None

    resource_group_policys = ctx.pgm.get_policy_resource_group()
    if not resource_group_policys:
        resource_group_policys = {}

    resource_policys = ret
    desktop_ids = resource_policys.keys()
    ret= ctx.pgm.get_desktops(desktop_ids)
    if not ret:
        return None
    desktops = ret
    
    delete_policy_resources = {}
    change_policy_resources = {}

    for resource_id, resource_policy in resource_policys.items():
        _policy_group_id = resource_policy["policy_group_id"]
        is_lock = resource_policy["is_lock"]
        desktop = desktops.get(resource_id)
        if not desktop:
            conditions = {"resource_id": resource_id}
            ctx.pg.base_delete(dbconst.TB_POLICY_GROUP_RESOURCE, conditions)
            continue
        
        resource_group_id = desktop["delivery_group_id"]
        if not resource_group_id:
            resource_group_id = desktop["desktop_group_id"]
        
        resource_group_policy = resource_group_policys.get(resource_group_id)
        if is_lock and resource_group_policy:
            group_policy_id = resource_group_policy["policy_group_id"]
            if group_policy_id not in change_policy_resources:
                change_policy_resources[group_policy_id] = []
            change_policy_resources[group_policy_id].append(resource_id)        
        else:
            if _policy_group_id not in delete_policy_resources:
                delete_policy_resources[_policy_group_id] = []
            delete_policy_resources[_policy_group_id].append(resource_id)
    
    job_uuids = []
    if delete_policy_resources:
        
        policy_groups = ctx.pgm.get_policy_groups(delete_policy_resources.keys())
        if not policy_groups:
            policy_groups = {}
        for _policy_group_id, _resource_ids in delete_policy_resources.items():
            
            policy_group = policy_groups.get(_policy_group_id)
            if not policy_group:
                continue
            ret = remove_resource_from_policy_group(sender, policy_group, _resource_ids)
            if isinstance(ret, Error) or not ret:
                return ret
            _, job_uuid = ret
            job_uuids.append(job_uuid)
            
    if change_policy_resources:
        policy_groups = ctx.pgm.get_policy_groups(delete_policy_resources.keys())
        if not policy_groups:
            policy_groups = {}
        
        for _policy_group_id, _resource_ids in change_policy_resources.items():
            policy_group = policy_groups.get(_policy_group_id)
            if not policy_group:
                continue
            ret = change_resource_to_policy_group(sender, policy_group, resource_ids, is_lock=0)
            if isinstance(ret, Error):
                return ret
            
            if ret:
                job_uuids.append(ret)
    return job_uuids

def set_resource_group_policy(sender, resource_group_id, new_policy_groups):

    ctx = context.instance()
    curr_policys = ctx.pgm.get_resource_group_policy(resource_group_id)
    if not curr_policys:
        curr_policys = {}

    ret = check_resource_group_type(resource_group_id)
    if isinstance(ret, Error):
        return ret
    resource_group_type = ret
    
    job_uuids = []
    for policy_group_type, policy_group_id in new_policy_groups.items():

        curr_policy = curr_policys.get(policy_group_type)
        if not curr_policy:

            ret = add_resource_group_policy(sender, policy_group_id, resource_group_id, resource_group_type, policy_group_type)
            if isinstance(ret, Error):
                return ret
            if ret:
                job_uuids.append(ret)
            continue
        
        if not policy_group_id:
            del_info = {
                "resource_group_id": resource_group_id,
                "policy_group_type": policy_group_type
                }
            ret = delete_resource_group_policy(sender, resource_group_id, policy_group_type, curr_policys)
            if isinstance(ret, Error):
                return ret

            if ret:
                job_uuids.append(ret)

            ctx.pg.base_delete(dbconst.TB_POLICY_RESOURCE_GROUP, del_info)
            continue

        ret = change_resource_group_policy(sender, resource_group_id, policy_group_id, resource_group_type, policy_group_type)
        if isinstance(ret, Error):
            return ret

        if ret:
            job_uuids.append(ret)

    return job_uuids

def init_policy_group(sender, policy_group):
    return policy_adapter(policy_group).init_policy_group(sender, policy_group)

def check_policy_group_policy_vaild(policy_group, policy_ids, is_add=False, is_remove=False):
    return policy_adapter(policy_group).check_policy_group_policy_vaild(policy_group, policy_ids, is_add, is_remove)

def check_policy_group_resource_vaild(policy_group, resource_ids, is_add=False, is_remove=False):
    return policy_adapter(policy_group).check_policy_group_resource_vaild(policy_group, resource_ids, is_add, is_remove)

def add_resource_to_policy_group(sender, policy_group, resource_ids, is_lock=False):
    return policy_adapter(policy_group).add_resource_to_policy_group(sender, policy_group, resource_ids, is_lock)

def change_resource_to_policy_group(sender, policy_group, resource_ids, is_lock=0):
    return policy_adapter(policy_group).change_resource_to_policy_group(sender, policy_group, resource_ids, is_lock)

def add_policy_to_policy_group(sender, policy_group, policy_ids=None, is_init=False):
    
    policy = policy_adapter(policy_group)
    if not policy:
        logger.error("policy group no found %s" % policy_group)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    return policy.add_policy_to_policy_group(sender, policy_group, policy_ids, is_init=is_init)

def remove_resource_from_policy_group(sender, policy_group, resource_ids=None):
    return policy_adapter(policy_group).remove_resource_from_policy_group(sender, policy_group, resource_ids)

def remove_policy_from_policy_group(sender, policy_group, policy_ids=None):
    return policy_adapter(policy_group).remove_policy_from_policy_group(sender, policy_group, policy_ids)

def apply_policy_group(sender, policy_group_id):
    return policy_adapter(policy_group_id).apply_policy_group(sender, policy_group_id)

def delete_policy_group(sender, policy_group):
    return policy_adapter(policy_group).delete_policy_group(sender, policy_group)
    
def send_policy_group_job(sender, desktop_group_ids, action, citrix_update=None):
    
    if not isinstance(desktop_group_ids, list):
        desktop_group_ids = [desktop_group_ids]
    
    directive = {
                "sender": sender,
                "action": action,
                "desktop_groups" : desktop_group_ids,
                }
    if citrix_update:
        directive["citrix_update"] = citrix_update

    ret= Job.submit_desktop_job(action, directive, desktop_group_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def set_resource_group_security_policy(resource_group_id, resource_id, curr_policy):
    
    ctx = context.instance()
    ret = ctx.pgm.get_resource_group_policy(resource_group_id, policy_group_type=const.POLICY_TYPE_SECURITY)
    if not ret:
        return None

    policy_group_id = ret.get(const.POLICY_TYPE_SECURITY)
    if not policy_group_id:
        return None
        
    if curr_policy.get("policy_group_id") == policy_group_id:
        return policy_group_id

    if not curr_policy:
        new_policy_resource = {
                                "policy_group_id": policy_group_id,
                                "resource_id": resource_id,
                                "policy_group_type": const.POLICY_TYPE_SECURITY,
                                "status": const.POLICY_STATUS_ENABLED,
                                "is_apply": const.APPLY_TYPE_APPLY,
                                }
        if not ctx.pg.base_insert(dbconst.TB_POLICY_GROUP_RESOURCE, new_policy_resource):
            logger.error("insert newly created desktop group disk config for [%s] to db failed" % (new_policy_resource))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    else:
        condition = {"resource_id": resource_id, "policy_group_type": const.POLICY_TYPE_SECURITY}
        update_desktop_policy = {
                                "policy_group_id": policy_group_id,
                                "is_apply": const.APPLY_TYPE_APPLY,
                                }
        if not ctx.pg.base_update(dbconst.TB_POLICY_GROUP_RESOURCE, condition, update_desktop_policy):
            logger.error("modify network config update db fail" % update_desktop_policy)
            return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return policy_group_id

def set_desktop_security_policy_group(sender, desktop_ids):

    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        return None
    
    policy_group_ids = []
    desktop_policys = ctx.pgm.get_policy_group_resource(resource_ids=desktop_ids, policy_group_type=const.POLICY_TYPE_SECURITY)
    if not desktop_policys:
        desktop_policys = {}
    
    for desktop_id, desktop in desktops.items():
        
        delivery_group_id = desktop["delivery_group_id"]
        desktop_group_id = desktop["desktop_group_id"]

        curr_policy = desktop_policys.get(desktop_id)
        if not curr_policy:
            curr_policy = {}
            
        # check delivery group_id
        if delivery_group_id:
            ret = set_resource_group_security_policy(delivery_group_id, desktop_id, curr_policy)
            if isinstance(ret, Error):
                return ret

            if ret:
                policy_group_ids.append(ret)
                continue

        if desktop_group_id:
            ret = set_resource_group_security_policy(desktop_group_id, desktop_id, curr_policy)
            if isinstance(ret, Error):
                return ret

            if ret:
                policy_group_ids.append(ret)
                continue

        if curr_policy:
            condition = {"resource_id": desktop_id, "policy_group_type": const.POLICY_TYPE_SECURITY}
            update_desktop_policy = {"is_apply": const.APPLY_TYPE_REMOVE}
            if not ctx.pg.base_update(dbconst.TB_POLICY_GROUP_RESOURCE, condition, update_desktop_policy):
                logger.error("update resource is_apply to policy group insert db fail %s" % desktop_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
            
            policy_group_ids.append(curr_policy["policy_group_id"])
    
    desktop_policy = ctx.pgm.get_policy_group_resource(resource_ids=desktop_ids, is_apply=[const.APPLY_TYPE_REMOVE, const.APPLY_TYPE_APPLY])
    if not desktop_policy:
        return None

    if policy_group_ids:
        ret = apply_policy_group(sender, policy_group_ids)
        if isinstance(ret, Error):
            return ret
    
        job_uuid = ret
        
        return job_uuid
    
    return None
        
