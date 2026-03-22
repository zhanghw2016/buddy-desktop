from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
from utils.id_tool import(
    UUID_TYPE_DESKTOP,
    UUID_TYPE_SECURITY_POLICY,
)

from utils.misc import get_current_time
from common import check_resource_transition_status
import copy

def format_policy_group(policy_group):
    
    ctx = context.instance()
    policy_group_id = policy_group["policy_group_id"]
    
    group_policys = ctx.pgm.get_policy_group_policy(policy_group_id, ignore_base=False)
    if not group_policys:
        group_policys = {}
    
    security_policy_ids = group_policys.keys()
    security_policys = ctx.pgm.get_security_policys(security_policy_ids)
    if not security_policys:
        security_policys = {}
    
    format_security_policys(security_policys, False)
    
    policy_group["security_policys"] = security_policys.values()

    desktops = ctx.pgm.get_desktops(zone=policy_group["zone"])
    if not desktops:
        desktops = {}
    
    free_desktops = copy.deepcopy(desktops.keys())
    resources = ctx.pgm.get_policy_group_resource(policy_group_id)
    if resources:
        resource_ids = resources.keys()       
        nics = ctx.pgm.get_desktop_nics(resource_ids)
        if not nics:
            nics = {}
        
        clear_resource = []
        policy_resource_key = ["instance_id", "desktop_group_name", "desktop_group_id",
                                   "hostname","status"]
        for resource_id in resource_ids:

            if not resource_id.startswith(UUID_TYPE_DESKTOP):
                continue
            
            if resource_id in free_desktops:
                free_desktops.remove(resource_id)
            
            desktop = desktops.get(resource_id)
            if not desktop:
                clear_resource.append(resource_id)
                continue
            
            resource_info = {}                
            for key, value in desktop.items():
                if key not in policy_resource_key:
                    continue
                
                resource_info[key] = value
            
            nic = nics.get(resource_id)
            if not nic:
                nic = []
            
            resource_info["nics"] = nic
            resources[resource_id].update(resource_info)
        
        if clear_resource:
            conditions = dict(policy_group_id=policy_group_id, 
                              resource_id=clear_resource)

            ctx.pg.base_delete(dbconst.TB_POLICY_GROUP_RESOURCE, conditions)
    else:
        resources = {}

    policy_group["resources"] = resources.values()
    policy_group["free_desktops"] = free_desktops
    
    return None

def set_security_policy_apply(security_policy_id, is_apply=1):
    
    ctx = context.instance()

    resource_type = security_policy_id.split("-")[0]
    if resource_type in [UUID_TYPE_SECURITY_POLICY]:
        # update policy group
        policy_groups = ctx.pgm.get_security_policy_groups(security_policy_id)
        if policy_groups:
            policy_group_id = policy_groups.keys()[0]
            if not ctx.pg.batch_update(dbconst.TB_POLICY_GROUP, {policy_group_id: {"is_apply": is_apply}}):
                logger.error("update resource is_apply to policy group insert db fail %s" % security_policy_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    # update security_policy
    if not ctx.pg.batch_update(dbconst.TB_SECURITY_POLICY, {security_policy_id: {"is_apply": is_apply}}):
        logger.error("update resource is_apply to policy group insert db fail %s" % security_policy_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def set_policy_group_apply(policy_group_ids=None, security_policy_ids=None, resource_ids=None, is_apply=const.APPLY_TYPE_APPLY):

    ctx = context.instance()
    if not policy_group_ids and not security_policy_ids:
        return None

    if policy_group_ids and not isinstance(policy_group_ids, list):
        policy_group_ids = [policy_group_ids]

    if not policy_group_ids:
        ret = ctx.pgm.get_security_policy_groups(security_policy_ids)
        if not ret:
            return None

        policy_group_ids = ret.keys()
    
    group_resource = {}
    if resource_ids:
        ret = ctx.pgm.get_group_resource(resource_ids)
        if ret:
            group_resource = ret
        
    for policy_group_id in policy_group_ids:
        
        resource_ids = group_resource.get(policy_group_id)
        if not resource_ids:
            ret = ctx.pgm.get_policy_group_resource(policy_group_id)
            if not ret:
                continue
            resource_ids = ret.keys()

        desktop_instance = ctx.pgm.get_desktop_instance(resource_ids)
        if not desktop_instance:
            continue

        desktop_ids = desktop_instance.keys()
        for desktop_id in desktop_ids:

            conditions = dict(policy_group_id=policy_group_id, 
                              resource_id=desktop_id)

            update_resource = {"is_apply": is_apply}
            if not ctx.pg.base_update(dbconst.TB_POLICY_GROUP_RESOURCE, conditions, update_resource):
                logger.error("update resource is_apply to policy group insert db fail %s, %s" % (update_resource, conditions))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    for policy_group_id in policy_group_ids:
       
        if not ctx.pg.batch_update(dbconst.TB_POLICY_GROUP, {policy_group_id: {"is_apply": 1}}):
            logger.error("update resource is_apply to policy group insert db fail %s" % policy_group_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def format_security_rules(security_policys):
    
    ctx = context.instance()
    
    for security_policy_id, security_policy in security_policys.items():
        
        security_rules = ctx.pgm.get_security_rules(security_policy_ids=security_policy_id)
        if not security_rules:
            security_rules = {}
        
        security_policy["security_rules"] = security_rules.values()
    
    return security_policys

def format_security_policys(security_policy_set, is_load_rule=True):

    ctx = context.instance()
    
    slave_security_policys = []
    for security_policy_id, security_policy in security_policy_set.items():

        security_policy_type = security_policy["security_policy_type"]
        if security_policy_type == const.SEC_POLICY_TYPE_SAHRE:
            policy_mode = security_policy.get("policy_mode", const.SECURITY_POLICY_MODE_MASTER)
            if policy_mode == const.SECURITY_POLICY_MODE_SLAVE:
                slave_security_policys.append(security_policy_id)
                continue

            ret = ctx.pgm.get_share_security_policys(security_policy_id)
            if not ret:
                security_policy["share_policys"] = []
            else:
                share_policys = ret
                if is_load_rule:
                    format_security_rules(share_policys)
                security_policy["share_policys"] =share_policys.values()

            if is_load_rule:
                format_security_rules(security_policy_set)

            policy_groups = ctx.pgm.get_security_policy_groups(security_policy_id)
            if not policy_groups:
                policy_groups = {}
            security_policy["policy_groups"] = policy_groups.values()

        elif security_policy_type == const.SEC_POLICY_TYPE_SG:
            
            security_rules = ctx.pgm.get_security_rules(security_policy_ids=security_policy_id)
            if not security_rules:
                security_rules = {}
            
            security_policy["security_rules"] = security_rules.values()
        else:
            policy_groups = ctx.pgm.get_security_policy_groups(security_policy_id)
            if not policy_groups:
                policy_groups = {}
            security_policy["policy_groups"] = policy_groups.values()

            if is_load_rule:
                format_security_rules(security_policy_set)

    if slave_security_policys:
        for secuirty_policy_id in slave_security_policys:
            del security_policy_set[secuirty_policy_id]

    return security_policy_set

def add_resource_to_policy_group(sender, policy_group, resource_ids, is_lock=False):

    ctx = context.instance()
    policy_group_id = policy_group["policy_group_id"]
    existed_resources = ctx.pgm.get_policy_group_resource(resource_ids = resource_ids, policy_group_type=const.POLICY_TYPE_SECURITY)
    if not existed_resources:
        existed_resources = {}
    
    new_resources = {}
    update_resource = []
    for resource_id in resource_ids:
        
        if resource_id in existed_resources:
            policy_resource = existed_resources[resource_id]
            if policy_group_id == policy_resource["policy_group_id"]:
                continue
            
            update_resource.append(resource_id)
            continue
        
        update_info = {"policy_group_id": policy_group_id,
                       "resource_id": resource_id,
                       "status": const.POLICY_STATUS_ENABLED,
                       "policy_group_type": const.POLICY_TYPE_SECURITY,
                       "is_lock": 1 if is_lock else 0
                       }

        new_resources[resource_id] = update_info
    
    if new_resources:
        if not ctx.pg.batch_insert(dbconst.TB_POLICY_GROUP_RESOURCE, new_resources):
            logger.error("add resource to policy group insert db fail %s" % new_resources)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
        
    if update_resource:
        condition = {"resource_id": update_resource, "policy_group_type": const.POLICY_STATUS_ENABLED}
        update_info = {"policy_group_id": policy_group_id, 
                       "status": const.POLICY_STATUS_ENABLED,
                       "is_lock": 1 if is_lock else 0
                       }
        if not ctx.pg.base_update(dbconst.TB_POLICY_GROUP_RESOURCE, condition, update_info):
            logger.error("modify network config update db fail" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    set_policy_group_apply(policy_group_ids=policy_group_id, resource_ids=resource_ids)

    ret = apply_policy_group(sender, policy_group_id)
    if isinstance(ret, Error):
        return ret

    job_uuid = ret
    return job_uuid

def change_resource_to_policy_group(sender, policy_group, resource_ids, is_lock=0):

    ctx = context.instance()
    policy_group_id = policy_group["policy_group_id"]
    
    existed_resources = {}
    ret = ctx.pgm.get_policy_group_resource(resource_ids=resource_ids, policy_group_type=const.POLICY_TYPE_SECURITY)
    if ret:
        existed_resources = ret
    
    new_resources = {}
    update_resources = []
    for resource_id in resource_ids:
        
        if resource_id in existed_resources:
            policy_resource = existed_resources[resource_id]
            if policy_group_id == policy_resource["policy_group_id"]:
                continue
            update_resources.append(resource_id)
            continue
        
        update_info = {"policy_group_id": policy_group_id,
                       "resource_id": resource_id,
                       "status": const.POLICY_STATUS_ENABLED,
                       "policy_group_type": const.POLICY_TYPE_SECURITY,
                       "is_lock": is_lock
                       }

        new_resources[resource_id] = update_info
    
    if new_resources:
        if not ctx.pg.batch_insert(dbconst.TB_POLICY_GROUP_RESOURCE, new_resources):
            logger.error("add resource to policy group insert db fail %s" % update_resources)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    if update_resources:
        conditions = {"resource_id": update_resources, "policy_group_type": const.POLICY_TYPE_SECURITY}
        update_info = {"policy_group_id": policy_group_id, "is_lock": is_lock}
        if not ctx.pg.base_update(dbconst.TB_POLICY_GROUP_RESOURCE, conditions, update_info):
            logger.error("update resource is_apply to policy group insert db fail %s, %s" % (update_resources, conditions))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    set_policy_group_apply(policy_group_ids=policy_group_id, resource_ids=resource_ids, is_apply=const.APPLY_TYPE_APPLY)

    ret = apply_policy_group(sender, policy_group_id)
    if isinstance(ret, Error):
        return ret

    job_uuid = ret
    return job_uuid

def remove_resource_from_policy_group(sender, policy_group, resource_ids=None):

    ctx = context.instance()
    policy_group_id = policy_group["policy_group_id"]
    
    if not resource_ids:
        ret = ctx.pgm.get_policy_group_resource(policy_group_id)
        if not ret:
            return None
        resource_ids = ret.keys()
    set_policy_group_apply(policy_group_id, resource_ids=resource_ids, is_apply=const.APPLY_TYPE_REMOVE)

    ret = apply_policy_group(sender, policy_group_id)
    if isinstance(ret, Error):
        return ret

    job_uuid = ret

    return (None, job_uuid)

def check_policy_group_policy_vaild(policy_group, policy_ids, is_add=False, is_remove=False):

    ctx = context.instance()
    policy_group_id = policy_group["policy_group_id"]
    
    security_policys = ctx.pgm.get_security_policys(policy_ids)
    if not security_policys:
        logger.error("add policy to policy group insert db fail %s" % policy_ids)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    # check policy grouup transition status
    ret = check_resource_transition_status({policy_group_id: policy_group})
    if isinstance(ret, Error):
        return ret

    if is_add:
        ret = ctx.pgm.get_policy_group_policy(policy_group_id, policy_ids)
        if ret:
            logger.error("remove policy to policy group insert db fail %s" % policy_ids)
            return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                         ErrorMsg.ERR_MSG_RESOURCE_ALREADY_EXISTED)
        
        for policy_id in policy_ids:
            policy = security_policys.get(policy_id)
            if not policy:
                logger.error("check policy group policy no found policy %s" % policy_id)
                return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                             ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, policy_id)
            
            security_policy_type = policy["security_policy_type"]
            if security_policy_type not in [const.SEC_POLICY_TYPE_SGRS, const.SEC_POLICY_TYPE_SAHRE]:
                logger.error("check policy group policy no found policy %s" % policy_id)
                return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                             ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, policy_id)

    if is_remove:
        group_policys = ctx.pgm.get_policy_group_policy(policy_group_id, policy_ids)
        if not group_policys:
            group_policys = {}
        
        for policy_id in policy_ids:
            policy = group_policys.get(policy_id)
            if policy_id not in group_policys or not policy:
                logger.error("add resource to policy group insert db fail %s" % policy_ids)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
            
            is_base = policy["is_base"]
            if is_base:
                logger.error("add resource to policy group insert db fail %s" % policy_ids)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def init_policy_group(sender, policy_group):

    policy_group_id = policy_group["policy_group_id"]
    
    policy_group_name = policy_group["policy_group_name"]
    security_poilcy_name = policy_group_name if policy_group_name else policy_group_id

    ret = create_security_poilcy(sender, security_poilcy_name, const.SEC_POLICY_TYPE_SG)
    if isinstance(ret, Error):
        return ret
    security_poilcy_id = ret
    
    ret = add_policy_to_policy_group(sender, policy_group, security_poilcy_id, is_init=True)
    if isinstance(ret, Error):
        return ret
    return security_poilcy_id

def check_policy_group_resource_vaild(policy_group, resource_ids, is_add=False, is_remove=False):
    
    ctx = context.instance()
    policy_group_id = policy_group["policy_group_id"]

    desktops = ctx.pgm.get_desktops(resource_ids)
    if not desktops:
        logger.error("add resource to policy group no found resource %s" % resource_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, resource_ids)
    
    # check policy grouup transition status
    ret = check_resource_transition_status(desktops)
    if isinstance(ret, Error):
        return ret

    if is_add:
        ret = ctx.pgm.get_policy_group_resource(policy_group_id, resource_ids=resource_ids, policy_group_type=const.POLICY_TYPE_SECURITY)
        if ret:
            logger.error("add resource to policy group, resource existed %s" % ret)
            return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                         ErrorMsg.ERR_MSG_RESOURCE_ALREADY_EXISTED)

    if is_remove:
        ret = ctx.pgm.get_policy_group_resource(policy_group_id, resource_ids)
        if not ret:
            logger.error("remove resource form policy group, resource no found %s" % resource_ids)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, resource_ids)
        
        for resource_id in resource_ids:
            if resource_id not in ret:
                logger.error("remove resource form policy group, resource no found %s" % resource_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def check_ruleset_in_policy_group(sender, base_policy_id, ruleset_ids):
    
    ctx = context.instance()
    existed_rulesets = ctx.res.resource_describe_security_group_and_ruleset(sender["zone"], base_policy_id)
    if not existed_rulesets:
        existed_rulesets = {}
    
    if (len(existed_rulesets) + len(ruleset_ids)) > const.MAX_POILICY_RULESET_COUNT:
        logger.error("ruleset count exceed policy group max limit")
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_POLICY_GROUP_RULESET_EXCEED_MAX_LIMIT)
        
    return None

def add_policy_to_policy_group(sender, policy_group, security_policy_ids, is_init=False):

    ctx = context.instance()
    if not isinstance(security_policy_ids, list):
        security_policy_ids = [security_policy_ids]
    
    security_policys = ctx.pgm.get_security_policys(security_policy_ids)
    if not security_policys:
        logger.error("no found security policy %s" % security_policy_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    policy_group_id = policy_group["policy_group_id"]
    base_policy_id = ctx.pgm.get_base_policy(policy_group_id)
    
    ruleset_ids = []
    for policy_id, policy in security_policys.items():
        policy_type = policy["security_policy_type"]
        if policy_type == const.SEC_POLICY_TYPE_SG:
            if base_policy_id:
                logger.error("policy group %s has base policy %s" % (policy_group_id, base_policy_id))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_SECURITY_POLICY_NO_BASE_POLICY, policy_group_id)
            else:
                base_policy_id = policy_id
        else:
            ruleset_ids.append(policy_id)

    if ruleset_ids:
        
        ret = check_ruleset_in_policy_group(sender, base_policy_id, ruleset_ids)
        if isinstance(ret, Error):
            return ret

        if not base_policy_id:
            logger.error("add security policy no found base policy %s" % policy_group_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_SECURITY_POLICY_NO_BASE_POLICY, policy_group_id)

        ret = ctx.res.resource_add_security_group_rulesets(sender["zone"], base_policy_id, ruleset_ids)
        if not ret:
            logger.error("add security policy %s to base policy %s fail" % (ruleset_ids, base_policy_id))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    update_policys = {}
    for policy_id in security_policy_ids:
        update_info = {"policy_group_id": policy_group_id,
                       "policy_id": policy_id,
                       "status": const.POLICY_STATUS_ENABLED,
                       "is_base": 1 if policy_id == base_policy_id else 0
                       }
        update_policys[policy_id] = update_info

    if not ctx.pg.batch_insert(dbconst.TB_POLICY_GROUP_POLICY, update_policys):
        logger.error("add policy to policy group insert db fail %s" % update_policys)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    if not is_init:
        ret = set_policy_group_apply(policy_group_ids=policy_group_id)
        if isinstance(ret, Error):
            return ret

    return None

def remove_resource_ruleset_from_security_group(sender, security_group_id, policy_ids):
    
    ctx = context.instance()
    security_groups = ctx.res.resource_describe_security_groups(sender["zone"], policy_ids, const.SEC_POLICY_TYPE_SGRS)
    if not security_groups:
        return None

    rulesets = ctx.res.resource_describe_security_group_and_ruleset(sender["zone"], security_group_id)
    if not rulesets:
        return None

    ruleset_ids = []
    for ruleset_id, _ in rulesets.items():
        if ruleset_id not in policy_ids:
            continue
        ruleset_ids.append(ruleset_id)
    
    if not ruleset_ids:
        return None

    ret = ctx.res.resource_remove_security_group_rulesets(sender["zone"], security_group_id, ruleset_ids)
    if ret is None:
        logger.error("remove-ruleset-from-policy-group no found policy group %s" % security_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, security_group_id)
    
    return ruleset_ids

def remove_policy_from_policy_group(sender, policy_group, policy_ids=None):
    
    ctx = context.instance()
    policy_group_id = policy_group["policy_group_id"]
    base_policy_id = ctx.pgm.get_base_policy(policy_group_id)
    if not base_policy_id:
        logger.error("policy group no found base policy %s" % policy_group_id)
        return None
    
    ret = ctx.pgm.get_policy_group_policy(policy_group_id, policy_ids, True)
    if not ret:
        return None
    
    group_policys = ret
    policy_ids = group_policys.keys()
    
    ruleset_ids = None
    # remove sgrs policy
    ret = ctx.pgm.get_security_policys(policy_ids, security_policy_type= const.SEC_POLICY_TYPE_SGRS)
    if ret:
        sgrs_policy_ids = ret.keys()
        ret = remove_resource_ruleset_from_security_group(sender, base_policy_id, sgrs_policy_ids)
        if isinstance(ret, Error):
            return ret
    
        ruleset_ids = ret
        
    # remove shre policy
    ret = ctx.pgm.get_security_policys(policy_ids, security_policy_type= const.SEC_POLICY_TYPE_SAHRE)
    if ret:
        share_policy_ids = ret.keys()
        from resource_control.policy.share_security import remove_share_policy_from_policy_group
        ret = remove_share_policy_from_policy_group(sender, policy_group, share_policy_ids)
        if isinstance(ret, Error):
            return ret
        
    if ruleset_ids:
        set_policy_group_apply(policy_group_id)

    for policy_id in policy_ids:
        conditions = dict(policy_group_id=policy_group_id, 
                          policy_id=policy_id)

        ctx.pg.base_delete(dbconst.TB_POLICY_GROUP_POLICY, conditions)

    return None

def modify_policy_group_attributes(sender, policy_group, need_maint_columns):
    
    ctx = context.instance()
    policy_group_id = policy_group["policy_group_id"]
    
    update_info = {}
    modify_key = ["policy_group_name", "description"]
    for key in modify_key:
        if key not in need_maint_columns:
            continue

        if need_maint_columns.get(key) == policy_group[key]:
            continue

        update_info[key] = need_maint_columns[key]
        
    if not update_info:
        return None

    security_group_id = ctx.pgm.get_base_policy(policy_group_id)
    if not security_group_id:
        logger.error("no found polciy group base policy %s" % (policy_group_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_SECURITY_POLICY_NO_BASE_POLICY, policy_group_id)

    ret = ctx.res.resource_modify_security_group_attributes(sender["zone"], security_group_id, **update_info)
    if ret is None:
        logger.error("modify resource security policy info fail %s, %s" % (policy_group_id, update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, policy_group_id)
    return None

def delete_resource_security_group(sender, security_group_ids):
    
    ctx = context.instance()
    security_groups = ctx.res.resource_describe_security_groups(sender["zone"], security_group_ids)
    if not security_groups:
        return None
    
    for _id, sg in security_groups.items():
        resources = sg.get("resources")
        if resources:
            logger.error("delete security group have resource %s %s" % (_id, resources))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, _id)
            
    sg_ids = security_groups.keys()
    
    ret = ctx.res.resource_delete_security_groups(sender["zone"], sg_ids)
    if ret is None:
        logger.error("add-policy-to-policy-group no found policy group %s" % sg_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, sg_ids)

    return sg_ids

def delete_policy_group(sender, policy_group):
    
    ctx = context.instance()
    policy_group_id = policy_group["policy_group_id"]

    base_policy_id = ctx.pgm.get_base_policy(policy_group_id)
    if not base_policy_id:
        return None

    # check policy group resource
    ret = ctx.pgm.get_policy_group_resource(policy_group_id)
    if ret:
        logger.error("modify policy name fail %s" % (policy_group_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, policy_group_id)

    # check policy group policy
    ret = ctx.pgm.get_policy_group_policy(policy_group_id)
    if ret:
        logger.error("modify policy name fail %s" % (policy_group_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, policy_group_id)
    
    ret = delete_resource_security_group(sender, base_policy_id)
    if isinstance(ret, Error):
        return ret
    
    conditions = dict(policy_group_id=policy_group_id, 
                      policy_id=base_policy_id)

    ctx.pg.base_delete(dbconst.TB_POLICY_GROUP_POLICY, conditions)
    
    return base_policy_id

def send_security_policy_job(sender, policy_group_ids, action):
    
    if not isinstance(policy_group_ids, list):
        policy_group_ids = [policy_group_ids]
        
    directive = {
                "sender": sender,
                "action": action,
                "policy_groups" : policy_group_ids,
                }

    from resource_control.desktop.job import submit_desktop_job
    ret= submit_desktop_job(action, directive, policy_group_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def send_security_ipset_job(sender, security_ipset_ids, action):
    
    if not isinstance(security_ipset_ids, list):
        security_ipset_ids = [security_ipset_ids]
        
    directive = {
                "sender": sender,
                "action": action,
                "security_ipsets" : security_ipset_ids,
                }

    from resource_control.desktop.job import submit_desktop_job
    ret= submit_desktop_job(action, directive, security_ipset_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def check_security_policy_apply(security_policy_ids):
    
    ctx = context.instance()
    ret = ctx.pgm.get_security_policys(security_policy_ids, is_apply=1)
    if not ret:
        return None
    
    apply_ids = ret.keys()

    ret = ctx.pgm.get_security_policy_groups(apply_ids)
    if not ret:
        return None

    return ret

def check_apply_share_security_policy(security_policy):

    ctx = context.instance()
    security_policy_id = security_policy["security_policy_id"]
    policy_mode = security_policy["policy_mode"]
    
    if policy_mode == const.SECURITY_POLICY_MODE_SLAVE:
        logger.error("security policy mode is slave %s, cant apply" % (security_policy_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_SHARE_SECURITY_POLICY_CANT_APPLY, security_policy_id)

    slave_policys = ctx.pgm.get_share_security_policys(security_policy_id)
    if not slave_policys:
        slave_policys = {}
    
    zone_share_policys = {}

    for _policy_id, policy in slave_policys.items():
        
        zone_id = policy["zone"]        
        if zone_id not in zone_share_policys:
            zone_share_policys[zone_id] = []
        
        zone_share_policys[zone_id].append(_policy_id)

    return zone_share_policys
    
def apply_policy_group(sender, policy_group_ids=None, security_policy_ids=None):
    
    ctx = context.instance()
    
    if not policy_group_ids:
        ret = ctx.pgm.get_security_policy_groups(security_policy_ids)
        if not ret:
            return None
        else:
            policy_group_ids = ret.keys()
    
    if not isinstance(policy_group_ids, list):
        policy_group_ids = [policy_group_ids]

    ret = send_security_policy_job(sender, policy_group_ids, const.JOB_ACTION_APPLY_SECURITY_POLICYS)
    if isinstance(ret, Error):
        return ret

    job_uuid = ret
    return job_uuid

def apply_security_policy(sender, security_policy_ids):
       
    if not isinstance(security_policy_ids, list):
        security_policy_ids = [security_policy_ids]

    ret = send_security_policy_job(sender, security_policy_ids, const.JOB_ACTION_APPLY_SECURITY_POLICYS)
    if isinstance(ret, Error):
        return ret

    job_uuid = ret
    return job_uuid

def apply_security_ipset(sender, security_ipset_ids):

    if not isinstance(security_ipset_ids, list):
        security_ipset_ids = [security_ipset_ids]

    ret = send_security_ipset_job(sender, security_ipset_ids, const.JOB_ACTION_APPLY_SECURITY_IPSETS)
    if isinstance(ret, Error):
        return ret

    job_uuid = ret
    return job_uuid

def create_security_poilcy(sender, security_policy_name, group_type=const.SEC_POLICY_TYPE_SGRS, description=""):

    ctx = context.instance()
    zone_id = sender["zone"]

    ret = ctx.res.resource_create_security_group(zone_id, security_policy_name, group_type)
    if not ret:
        logger.error("resource create security group %s fail" % security_policy_name)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    security_group_id = ret

    security_policy = dict(security_policy_id=security_group_id,
                           security_policy_name=security_policy_name,
                           security_policy_type=group_type,
                           create_time=get_current_time(False),
                           status_time = get_current_time(False),
                           description = description,
                           status="active",
                           zone=sender["zone"],
                        )

    if not ctx.pg.batch_insert(dbconst.TB_SECURITY_POLICY, {security_group_id: security_policy}):
        logger.error("insert newly created security policy [%s] to db failed" % (security_policy))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return security_group_id

def check_security_policy_vaild(security_policy_ids):
    
    ctx = context.instance()
    if security_policy_ids and not isinstance(security_policy_ids, list):
        security_policy_ids = [security_policy_ids]

    security_policys = ctx.pgm.get_security_policys(security_policy_ids)
    if not security_policys:
        logger.error("get security policy no found %s" % security_policy_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, security_policy_ids)

    return security_policys

def check_security_rules_vaild(security_rule_ids):

    ctx = context.instance()
    if security_rule_ids and not isinstance(security_rule_ids, list):
        security_rule_ids = [security_rule_ids]
    
    security_rules = ctx.pgm.get_security_rules(security_rule_ids)
    if not security_rules:
        logger.error("describe security rule no found %s" % security_rule_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, security_rule_ids)

    return security_rules
    
def modify_security_policy_attributes(sender, security_group, need_maint_columns):
    
    ctx = context.instance()
    security_policy_id = security_group["security_policy_id"]
    
    if not need_maint_columns:
        return None
    
    security_policy_name = need_maint_columns.get("security_policy_name")
    description = need_maint_columns.get("description")
    ret = ctx.res.resource_describe_security_groups(sender["zone"], security_policy_id, group_type=const.SEC_POLICY_TYPE_SGRS)
    if not ret:
        logger.error("modify security group update fail %s" % security_policy_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    ret = ctx.res.resource_modify_security_group_attributes(sender["zone"], security_policy_id, security_policy_name, description)
    if not ret:
        logger.error("modify security group update fail %s" % security_policy_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    if not ctx.pg.batch_update(dbconst.TB_SECURITY_POLICY, {security_policy_id: need_maint_columns}):
        logger.error("modify security group update fail %s" % security_policy_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def check_delete_security_policy(security_policys):

    ctx = context.instance()
    
    normal_security_policys = {}
    share_security_policys = {}
    
    for security_policy_id, security_policy in security_policys.items():
        
        ret = ctx.pgm.get_security_policy_groups(security_policy_id)
        if ret:
            logger.error("security policy %s in policy group %s" % (security_policy_id, ret.keys()))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_SECURITY_POLICY_IN_USED, security_policy_id)
        
        security_policy_type = security_policy["security_policy_type"]
        if security_policy_type != const.SEC_POLICY_TYPE_SAHRE:
            normal_security_policys[security_policy_id] = security_policy
            continue
        
        share_security_policys[security_policy_id] = security_policy

        policy_mode = security_policy["policy_mode"]
        if policy_mode == const.SECURITY_POLICY_MODE_SLAVE:
            logger.error("slave security policy %s cant delete" % (security_policy_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_SLAVE_SECURITY_POLICY_CANT_DELETE, security_policy_id)

        ret = ctx.pgm.get_share_security_policys(security_policy_id)
        if not ret:
            continue

        slave_policy_ids = ret.keys()
        ret = ctx.pgm.get_security_policy_groups(slave_policy_ids)
        if ret:
            logger.error("security policy %s in policy group %s" % (slave_policy_ids, ret.keys()))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_SECURITY_POLICY_IN_USED, security_policy_id)

    return (normal_security_policys, share_security_policys)

def delete_security_policys(sender, security_policy_ids):

    ctx = context.instance()
    zone_id = sender["zone"]
    
    if not isinstance(security_policy_ids, list):
        security_policy_ids = [security_policy_ids]

    ret = ctx.res.resource_describe_security_groups(zone_id, security_policy_ids, const.SEC_POLICY_TYPE_SGRS)
    if ret:
        security_groups = ret
        ret = ctx.res.resource_delete_security_groups(zone_id, security_groups.keys())
        if isinstance(ret, Error):
            return ret

    for security_policy_id in security_policy_ids:
        
        security_rules = ctx.pgm.get_security_rules(security_policy_ids=security_policy_id)
        if security_rules:
            cons = {"security_policy_id": security_policy_id}
            ctx.pg.base_delete(dbconst.TB_SECURITY_RULE, cons)

        ctx.pg.delete(dbconst.TB_SECURITY_POLICY, security_policy_id)

    return None

def create_security_rules(zone_id, security_policy, rules):
    
    ctx = context.instance()
    security_policy_id = security_policy["security_policy_id"]
    
    new_rules = []
    keys = ["protocol","val1","val2","val3","priority","action","disabled", "direction"]
    for rule in rules:
        
        rule_info = {}
        for k, v in rule.items():
            if k in keys:
                rule_info[k] = v
        
        new_rules.append(rule_info)

    ret = ctx.res.resource_add_security_group_rules(zone_id, security_policy_id, new_rules)
    if ret is None:
        logger.error("add rule to security policy fail %s, %s" % (security_policy_id, rules))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_CLOUD_RESOURCE_FAILED, security_policy_id)
    security_group_rule_ids = ret

    ret = ctx.res.resource_describe_security_group_rules(zone_id, security_policy_id, security_group_rule_ids)
    if ret is None:
        logger.error("describe security policy rules fail %s" % (security_group_rule_ids))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, security_group_rule_ids)

    security_group_rules = ret
    if not security_group_rules:
        logger.error("security_group_rules: [%s]" % security_group_rules)
        return None
    
    existed_sec_rules = ctx.pgm.get_security_rules(security_policy_ids=security_policy_id)
    if not existed_sec_rules:
        existed_sec_rules = {}
    
    new_rules = {}
    keys = ["protocol","val1","val2","val3","priority","action","disabled", "direction"]
    for rule_id, rule in security_group_rules.items():
        
        if rule_id in existed_sec_rules:
            continue
        
        rule_info = {}
        for k, v in rule.items():
            if k in keys:
                rule_info[k] = v
        
        rule_info["security_rule_id"] = rule_id
        rule_info["security_rule_name"] = rule["security_group_rule_name"]
        rule_info["security_policy_id"] = security_policy_id
        rule_info["security_policy_name"] = security_policy["security_policy_name"]
        rule_info["zone"] = zone_id
        
        new_rules[rule_id] = rule_info
    
    if new_rules:
        if not ctx.pg.batch_insert(dbconst.TB_SECURITY_RULE, new_rules):
            logger.error("insert newly created security rule [%s] to db failed" % (new_rules))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    set_security_policy_apply(security_policy_id)

    return new_rules.keys()

def remove_rule_from_security_policy(sender, security_policy_id, security_rules):

    ctx = context.instance()
    security_rule_ids = security_rules.keys()

    ret = ctx.res.resource_describe_security_group_rules(sender["zone"], security_group_id=security_policy_id, security_group_rule_ids=security_rule_ids)
    if ret:
        ret = ctx.res.resource_delete_security_group_rules(sender["zone"], ret.keys())
        if not ret:
            logger.error("delete newly created security rule [%s] to db failed" % (security_rules.keys()))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, security_rules.keys())

    if security_rule_ids:
        if ctx.pg.base_delete(dbconst.TB_SECURITY_RULE, condition={"security_rule_id": security_rule_ids}) < 0:
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_SECURITY_RULES_REMOVE, security_rule_ids)

    set_security_policy_apply(security_policy_id)

    return security_rule_ids

def modify_security_rule_attributes(sender, security_rule, need_maint_columns):
    
    ctx = context.instance()
    security_rule_id = security_rule["security_rule_id"]
    security_policy_id = security_rule["security_policy_id"]
    
    ret = ctx.res.resource_describe_security_group_rules(sender["zone"], security_group_rule_ids=security_rule_id)
    if not ret:
        logger.error("no found security rule %s" % security_rule_id)
        return None

    ret = ctx.res.resource_modify_security_group_rule_attributes(sender["zone"], security_rule_id, need_maint_columns)
    if ret is None:
        logger.error("delete newly created security rule [%s] to db failed" % (security_rule_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, security_rule_id)
    
    if "rule_action" in need_maint_columns:
        need_maint_columns["action"] = need_maint_columns["rule_action"]
        del need_maint_columns["rule_action"]
    
    if "security_group_rule_name" in need_maint_columns:
        need_maint_columns["security_rule_name"] = need_maint_columns["security_group_rule_name"]
        del need_maint_columns["security_group_rule_name"]
    
    if not ctx.pg.batch_update(dbconst.TB_SECURITY_RULE, {security_rule_id: need_maint_columns}):
        logger.error("modify security group update fail %s" % security_rule_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    set_security_policy_apply(security_policy_id)
    
    return security_rule_id

def modify_share_security_rule(security_policy, security_rule_id, need_maint_columns):
    
    ctx = context.instance()
    security_policy_id = security_policy["security_policy_id"]
    zone_id = security_policy["zone"]
    
    share_rules = ctx.pgm.get_share_security_rules(security_rule_id, security_policy_id)
    if not share_rules:
        return None
    
    share_rule_id = share_rules.keys()[0]

    ret = ctx.res.resource_describe_security_group_rules(zone_id, security_group_rule_ids=share_rule_id)
    if not ret:
        logger.error("no found security rule %s" % security_rule_id)
        return None

    ret = ctx.res.resource_modify_security_group_rule_attributes(zone_id, security_rule_id, need_maint_columns)
    if ret is None:
        logger.error("delete newly created security rule [%s] to db failed" % (security_rule_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, security_rule_id)
    
    if "rule_action" in need_maint_columns:
        need_maint_columns["action"] = need_maint_columns["rule_action"]
        del need_maint_columns["rule_action"]
    
    if "security_group_rule_name" in need_maint_columns:
        need_maint_columns["security_rule_name"] = need_maint_columns["security_group_rule_name"]
        del need_maint_columns["security_group_rule_name"]
    
    if not ctx.pg.batch_update(dbconst.TB_SECURITY_RULE, {share_rule_id: need_maint_columns}):
        logger.error("modify security group update fail %s" % share_rule_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def modify_share_security_rule_attributes(security_rule, need_maint_columns):
    
    ctx = context.instance()
    security_rule_id = security_rule["security_rule_id"]
    security_policy_id = security_rule["security_policy_id"]
    
    share_policys = ctx.pgm.get_share_security_policys(security_policy_id)
    if not share_policys:
        return None
    
    for _, share_policy in share_policys.items():
    
        ret = modify_share_security_rule(share_policy, security_rule_id, need_maint_columns)
        if isinstance(ret, Error):
            return ret

    if "rule_action" in need_maint_columns:
        need_maint_columns["action"] = need_maint_columns["rule_action"]
        del need_maint_columns["rule_action"]
    
    if "security_group_rule_name" in need_maint_columns:
        need_maint_columns["security_rule_name"] = need_maint_columns["security_group_rule_name"]
        del need_maint_columns["security_group_rule_name"]

    if not ctx.pg.batch_update(dbconst.TB_SECURITY_RULE, {security_rule_id: need_maint_columns}):
        logger.error("modify security group update fail %s" % security_rule_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    set_security_policy_apply(security_policy_id)

    return security_rule_id

def format_security_ipsets(security_ipset_set):

    ctx = context.instance()
    
    for security_ipset_id, security_ipset in security_ipset_set.items():
        security_policys = {}
        ret = ctx.pgm.get_security_policy_by_ipset(security_ipset_id)
        if ret:
            security_policy_ids = ret
            ret = ctx.pgm.get_security_policys(security_policy_ids)
            if ret:
                security_policys = ret
        
        security_ipset["security_policys"] = security_policys.values()
    
    return None

def create_security_ipset(sender, ipset_type, val, security_ipset_name=None, description=None):
    
    ctx = context.instance()
    
    ret = ctx.res.resource_create_security_group_ipset(sender["zone"], ipset_type, val, security_ipset_name)
    if not ret:
        logger.error("resource create security ipset fail %s, %s, %s" % (security_ipset_name, ipset_type, val))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_CLOUD_RESOURCE_FAILED, "ipset")
    
    security_ipset_id = ret
    
    security_ipset_info = dict(
                              security_ipset_id = security_ipset_id,
                              ipset_type = ipset_type,
                              security_ipset_name = security_ipset_name if security_ipset_name else '',
                              val = val,
                              description = description if description else '',
                              create_time = get_current_time(),
                              is_apply = 0,
                              zone = sender["zone"]                              
                              )
    # register desktop group
    if not ctx.pg.insert(dbconst.TB_SECURITY_IPSET, security_ipset_info):
        logger.error("insert newly created security ipset for [%s] to db failed" % (security_ipset_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return security_ipset_id

def check_security_ipset_vaild(security_ipset_ids, is_delete=False):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_security_ipsets(security_ipset_ids)
    if not ret:
        logger.error("no found security ipsets %s" % security_ipset_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, security_ipset_ids)
    security_ipsets = ret
    
    if is_delete:
        ret = ctx.pgm.get_security_policy_by_ipset(security_ipset_ids)
        if ret:
            logger.error("security ipsets %s in use, cant delete" % security_ipset_ids)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_SECURITY_IPSET_IN_USED, security_ipset_ids)           

    return security_ipsets

def set_security_ipset_apply(security_ipset_id, is_apply=1):
    
    ctx = context.instance()
    ret = ctx.pgm.get_security_policy_by_ipset(security_ipset_id)
    if not ret:
        return None

    if not ctx.pg.batch_update(dbconst.TB_SECURITY_IPSET, {security_ipset_id: {"is_apply": is_apply}}):
        logger.error("update resource is_apply to policy group insert db fail %s" % security_ipset_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def modify_security_ipset_attributes(sender, security_ipset_id, need_maint_columns):
    
    ctx = context.instance()
    ret = ctx.res.resource_describe_security_group_ipsets(sender["zone"], security_ipset_id)
    if ret is None:
        return None
    
    security_group_ipset_name = need_maint_columns.get("security_group_ipset_name")
    description = need_maint_columns.get("description")
    val = need_maint_columns.get("val")
    
    ret = ctx.res.resource_modify_security_group_ipset_attributes(sender["zone"],security_ipset_id, security_group_ipset_name, description, val)
    if not ret:
        logger.error("modify security ipset fail %s" % security_ipset_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    if not ctx.pg.batch_update(dbconst.TB_SECURITY_IPSET, {security_ipset_id: need_maint_columns}):
        logger.error("modify security ipset update fail %s" % security_ipset_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    if security_group_ipset_name or val:
        set_security_ipset_apply(security_ipset_id, 1)

    return None

def delete_security_ipsets(sender, security_ipset_ids):
    
    ctx = context.instance()
    
    ret = ctx.res.resource_describe_security_group_ipsets(sender["zone"], security_ipset_ids)
    if ret:
        ret = ctx.res.resource_delete_security_group_ipsets(sender["zone"], security_ipset_ids)
        if not ret:
            logger.error("delete resource security ipset fail %s" % security_ipset_ids)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_RESOURCE_FAILED)

    for security_ipset_id in security_ipset_ids:
        ctx.pg.delete(dbconst.TB_SECURITY_IPSET, security_ipset_id)
    
    return security_ipset_ids

def describe_system_security_policys(sender, security_policy_ids=None):
    
    ctx = context.instance()

    ret = ctx.res.resource_describe_security_groups(sender["zone"], security_policy_ids)
    if ret is None:
        return None

    security_groups = ret
    for security_group_id, security_group in security_groups.items():

        if "resources" in security_group:
            del security_group["resources"]

        security_rules = ctx.res.resource_describe_security_group_rules(sender["zone"], security_group_id)
        if not security_rules:
            security_rules = {}

        security_group["security_rules"] = security_rules.values()

    return security_groups

def describe_system_security_ipsets(sender, security_ipset_ids=None):

    ctx = context.instance()

    ret = ctx.res.resource_describe_security_group_ipsets(sender["zone"], security_ipset_ids)
    if ret is None:
        return None
    security_ipsets = ret    
    
    existed_ipsets = ctx.pgm.get_security_ipsets(security_ipsets.keys())
    if not existed_ipsets:
        existed_ipsets = {}
    
    ipsets = {}    
    for ipset_id, ipset in security_ipsets.items():
        
        if ipset_id in existed_ipsets:
            continue
        
        if "resources" in ipset:
            del ipset["resources"]
        
        ipsets[ipset_id] = ipset

    return ipsets

def build_security_rules(security_rules):
    
    rule_key = ["protocol","val1","val2","val3", "val4","priority","action","disabled", "direction"]

    rules = []
    for _, security_rule in security_rules.items():
        
        rule_info = {}
        for key in rule_key:
            if key not in security_rule:
                continue
            rule_info[key] = security_rule[key]

        rules.append(rule_info)
    
    return rules

def load_security_rules(sender, security_policy, security_rule_ids):
    
    ctx = context.instance()
    security_policy_id = security_policy["security_policy_id"]
    security_rules = ctx.res.resource_describe_security_group_rules(sender["zone"], security_group_rule_ids=security_rule_ids)
    if not security_rules:
        return None
    
    rules = build_security_rules(security_rules)
    if not rules:
        return None
    
    security_policy_type = security_policy["security_policy_type"]
    
    rule_ids = []
    if security_policy_type == const.SEC_POLICY_TYPE_SAHRE:
        from resource_control.policy.share_security import create_share_security_rules
        ret = create_share_security_rules(security_policy, rules)
        if isinstance(ret, Error):
            return ret
        
        rule_ids.extend(ret)
    else:

        ret = create_security_rules(sender["zone"], security_policy, rules)
        if isinstance(ret, Error):
            return ret
        
        rule_ids.extend(ret)
    
    set_security_policy_apply(security_policy_id)
    
    return rule_ids

def build_security_ipsets(security_ipsets):
    ipset_key = ["ipset_type","val", "security_ipset_name", "description"]
    ipsets = []
    for _, security_ipset in security_ipsets.items():
        ipset_info = {}
        for key in ipset_key:
            if key not in security_ipset:
                continue
            ipset_info[key] = security_ipset[key]

        ipsets.append(ipset_info)
    return ipsets

def load_security_ipsets(sender, security_ipset_ids):
    
    ctx = context.instance()
    
    existed_ipsets = ctx.pgm.get_security_ipsets(security_ipset_ids)
    if not existed_ipsets:
        existed_ipsets = {}

    security_ipsets = ctx.res.resource_describe_security_group_ipsets(sender["zone"], security_ipset_ids)
    if not security_ipsets:
        return None

    for security_ipset_id, security_ipset in security_ipsets.items():
        if security_ipset_id in existed_ipsets:
            continue

        security_ipset_info = dict(
                                  security_ipset_id = security_ipset_id,
                                  ipset_type = security_ipset["ipset_type"],
                                  security_ipset_name = security_ipset["security_group_ipset_name"],
                                  val = security_ipset["val"],
                                  description = security_ipset["description"],
                                  create_time = get_current_time(),
                                  zone = sender["zone"]                              
                                  )
        # register desktop group
        if not ctx.pg.insert(dbconst.TB_SECURITY_IPSET, security_ipset_info):
            logger.error("insert newly created security ipset for [%s] to db failed" % (security_ipset_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return security_ipsets.keys()
