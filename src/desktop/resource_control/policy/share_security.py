from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
from common import (
    is_global_admin_user,
)
from utils.misc import get_current_time
from utils.id_tool import(
    UUID_TYPE_SECURITY_POLICY_SHARE,
    UUID_TYPE_SECURITY_RULE_SHARE
)
from utils.id_tool import(
    get_uuid
)
import resource_control.policy.security_policy as SecurityPolicy

def check_delete_share_security_policys(sender, policy_group_ids):
    
    ctx = context.instance()
    if is_global_admin_user(sender):
        return None
    
    for policy_group_id in policy_group_ids:
        ret = ctx.pgm.get_policy_group_policy(policy_group_id)
        if not ret:
            continue
        
        security_policy_ids = ret.keys()
        ret = ctx.pgm.get_security_policys(security_policy_ids, security_policy_type=const.SEC_POLICY_TYPE_SAHRE)
        if ret:
            logger.error("policy group has share policys %s" % ret.keys())
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_SHARE_POLICY_ADMIN_CANT_DELETE, policy_group_id)

    return None

def check_add_share_security_policys(sender, security_policy_ids):
    
    ctx = context.instance()
    
    share_policys = ctx.pgm.get_security_policys(security_policy_ids, security_policy_type=const.SEC_POLICY_TYPE_SAHRE, policy_mode=const.SECURITY_POLICY_MODE_MASTER)
    if not share_policys:
        return security_policy_ids, None
    
    if share_policys and not is_global_admin_user(sender):
        logger.error("add share to policy group deny %s" % security_policy_ids)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_SHARE_POLICY_ADMIN_CANT_DELETE, security_policy_ids)
    
    other_policys = []
    for security_policy_id in security_policy_ids:
        if security_policy_id in share_policys:
            continue
        
        other_policys.append(security_policy_id)

    return other_policys, share_policys.keys()

def create_share_security_poilcy(security_policy_name, description=""):

    ctx = context.instance()

    security_policy_id = get_uuid(UUID_TYPE_SECURITY_POLICY_SHARE, ctx.checker)
    security_policy = dict(security_policy_id=security_policy_id,
                           security_policy_name=security_policy_name,
                           security_policy_type=const.SEC_POLICY_TYPE_SAHRE,
                           create_time=get_current_time(False),
                           status_time = get_current_time(False),
                           description = description,
                           status="active",
                           zone = "",
                        )

    if not ctx.pg.batch_insert(dbconst.TB_SECURITY_POLICY, {security_policy_id: security_policy}):
        logger.error("insert newly created security policy [%s] to db failed" % (security_policy))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return security_policy_id

def create_share_slave_security_policy(sender, share_policy, policy_group):
    
    ctx = context.instance()
    zone_id = sender["zone"]
    security_policy_id = share_policy["security_policy_id"]
    share_policy_name = share_policy["security_policy_name"]
    slave_policy_name = "%s-%s" % (share_policy_name, zone_id)

    ret = SecurityPolicy.create_security_poilcy(sender, slave_policy_name)
    if isinstance(ret, Error):
        return ret

    slave_security_group_id = ret
    update_info = {
        "share_policy_id": security_policy_id,
        "policy_mode": const.SECURITY_POLICY_MODE_SLAVE,
        "security_policy_type": const.SEC_POLICY_TYPE_SAHRE,
        "zone": policy_group["zone"]
        }
    
    if not ctx.pg.batch_update(dbconst.TB_SECURITY_POLICY, {slave_security_group_id: update_info}):
        logger.error("modify security group update fail %s" % security_policy_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    zone_id = policy_group["zone"]

    ret = ctx.pgm.get_security_policys(slave_security_group_id)
    if not ret:
        return None
    share_policy = ret[slave_security_group_id]

    ret = ctx.pgm.get_security_rules(security_policy_ids=security_policy_id)
    if not ret:
        return slave_security_group_id

    slave_rules = ret.values()
    ret = SecurityPolicy.create_security_rules(zone_id, share_policy, slave_rules)
    if isinstance(ret, Error):
        return ret
    
    slave_rule_ids = ret
    update_info = {
        "security_rule_type": const.SEC_POLICY_TYPE_SAHRE
        }
    update_infos = {}
    for rule_id in slave_rule_ids:
        update_infos[rule_id] = update_info
    
    if not ctx.pg.batch_update(dbconst.TB_SECURITY_RULE, update_infos):
        logger.error("modify security group update fail %s" % security_policy_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return slave_security_group_id

def modify_share_security_policy_attributes(security_group, need_maint_columns):
    
    ctx = context.instance()
    security_policy_id = security_group["security_policy_id"]
    
    if not need_maint_columns:
        return None
    
    security_policy_name = need_maint_columns.get("security_policy_name")
    description = need_maint_columns.get("description")

    share_policys = {}
    policy_mode = security_group["policy_mode"]
    if policy_mode == const.SECURITY_POLICY_MODE_MASTER:

        ret = ctx.pgm.get_share_security_policys(security_policy_id)
        if ret:
            share_policys.update(ret)

    else:
        share_policys[security_policy_id] = security_group
    
    for _policy_id, share_policy in share_policys.items():
        
        zone_id = share_policy["zone"]
        ret = ctx.res.resource_describe_security_groups(zone_id, _policy_id, group_type=const.SEC_POLICY_TYPE_SGRS)
        if not ret:
            continue

        ret = ctx.res.resource_modify_security_group_attributes(zone_id, _policy_id, security_policy_name, description)
        if not ret:
            logger.error("modify security group update fail %s" % _policy_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

        if not ctx.pg.batch_update(dbconst.TB_SECURITY_POLICY, {_policy_id: need_maint_columns}):
            logger.error("modify security group update fail %s" % _policy_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    if policy_mode == const.SECURITY_POLICY_MODE_MASTER:

        if not ctx.pg.batch_update(dbconst.TB_SECURITY_POLICY, {security_policy_id: need_maint_columns}):
            logger.error("modify security group update fail %s" % security_policy_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def remove_resource_ruleset_from_share_security_group(sender, security_group_id, slave_policy_ids):
    
    ctx = context.instance()

    rulesets = ctx.res.resource_describe_security_group_and_ruleset(sender["zone"], security_group_id)
    if not rulesets:
        rulesets = {}

    ruleset_ids = []
    for ruleset_id, _ in rulesets.items():
        if ruleset_id not in slave_policy_ids:
            continue
        ruleset_ids.append(ruleset_id)
    
    if ruleset_ids:
        ret = ctx.res.resource_remove_security_group_rulesets(sender["zone"], security_group_id, ruleset_ids)
        if ret is None:
            logger.error("remove-ruleset-from-policy-group no found policy group %s" % security_group_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, security_group_id)

    return ruleset_ids

def delete_share_security_policys(sender, security_policys):

    ctx = context.instance()
    security_policy_ids = security_policys.keys()
    
    for security_policy_id, security_policy in security_policys.items():
        policy_mode = security_policy["policy_mode"]
        if policy_mode != const.SECURITY_POLICY_MODE_MASTER:
            continue

        ret = ctx.pgm.get_share_security_policys(security_policy_id)
        if not ret:
            continue

        slave_policy_ids = ret.keys()
        ret = SecurityPolicy.delete_security_policys(sender, slave_policy_ids)
        if isinstance(ret, Error):
            return ret

    for security_policy_id in security_policy_ids:
        ctx.pg.delete(dbconst.TB_SECURITY_POLICY, security_policy_id)

    return None

def remove_share_policy_from_policy_group(sender, policy_group, security_policy_ids=None):
    
    ctx = context.instance()
    zone_id = sender["zone"]

    policy_group_id = policy_group["policy_group_id"]
    base_policy_id = ctx.pgm.get_base_policy(policy_group_id)
    if not base_policy_id:
        return None
    
    ret = ctx.pgm.get_policy_group_policy(policy_group_id, security_policy_ids)
    if not ret:
        return None
    
    group_policys = ret
    security_policy_ids = group_policys.keys()

    # remove share policy
    for security_policy_id in security_policy_ids:
        ret = ctx.pgm.get_share_security_policys(security_policy_id, zone_id)
        if not ret:
            continue

        slave_policy_ids = ret.keys()

        ret = remove_resource_ruleset_from_share_security_group(sender, base_policy_id, slave_policy_ids)
        if isinstance(ret, Error):
            return ret
        
        slave_policys = ctx.pgm.get_security_policys(slave_policy_ids)
        if not slave_policys:
            slave_policys = {}
        
        if slave_policys:
            ret = SecurityPolicy.delete_security_policys(sender, slave_policys.keys())
            if isinstance(ret, Error):
                return ret
   
    return security_policy_ids

def create_share_security_rules(security_policy, rules):
    
    ctx = context.instance()
    security_policy_id = security_policy["security_policy_id"]

    new_rules = {}
    keys = ["protocol","val1","val2","val3","priority","action","disabled", "direction"]
    for rule in rules:
        
        rule_info = {}
        for k, v in rule.items():
            if k in keys:
                rule_info[k] = v
        
        share_rule_id = get_uuid(UUID_TYPE_SECURITY_RULE_SHARE, ctx.checker)
        rule_info["security_rule_id"] = share_rule_id
        rule_info["security_rule_type"] = const.SEC_POLICY_TYPE_SAHRE
        rule_info["security_rule_name"] = rule.get("security_rule_name", "")
        rule_info["security_policy_id"] = security_policy_id
        rule_info["security_policy_name"] = security_policy["security_policy_name"]
        rule_info["zone"] = ''
        
        new_rules[share_rule_id] = rule_info

    if not ctx.pg.batch_insert(dbconst.TB_SECURITY_RULE, new_rules):
        logger.error("insert newly created security rule [%s] to db failed" % (new_rules))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    SecurityPolicy.set_security_policy_apply(security_policy_id)
    
    ret = ctx.pgm.get_share_security_policys(security_policy_id)
    if not ret:
        return share_rule_id

    slave_policys = ret
    
    for _, policy in slave_policys.items():
        zone_id = policy["zone"]
        ret = SecurityPolicy.create_security_rules(zone_id, policy, rules)
        if isinstance(ret, Error):
            return ret
    
    return new_rules.keys()

def remove_share_security_policy_rules(zone_id, _policy_id, security_rule_ids):
    
    ctx = context.instance()

    ret = ctx.pgm.get_share_security_rules(security_rule_ids, _policy_id)
    if not ret:
        return None

    share_rule_ids = ret.keys()
    
    ret = ctx.res.resource_describe_security_group_rules(zone_id, security_group_id=_policy_id, security_group_rule_ids=share_rule_ids)
    if ret:
        ret = ctx.res.resource_delete_security_group_rules(zone_id, ret.keys())
        if not ret:
            logger.error("delete newly created security rule [%s] to db failed" % (share_rule_ids))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, share_rule_ids)


    if not ctx.pg.base_delete(dbconst.TB_SECURITY_RULE, condition={"security_rule_id": share_rule_ids}):
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_SECURITY_RULES_REMOVE, security_rule_ids)
    
    return None
    
def remove_share_rule_from_security_policy(security_policy_id, security_rules):

    ctx = context.instance()
    security_rule_ids = security_rules.keys()
    
    ret = ctx.pgm.get_share_security_policys(security_policy_id)
    if not ret:
        return None

    slave_policys = ret
    for _policy_id, policy in slave_policys.items():

        zone_id = policy["zone"]
        ret = remove_share_security_policy_rules(zone_id, _policy_id, security_rule_ids)
        if isinstance(ret, Error):
            return ret
    
    if not ctx.pg.base_delete(dbconst.TB_SECURITY_RULE, condition={"security_rule_id": security_rule_ids}):
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_SECURITY_RULES_REMOVE, security_rule_ids)

    SecurityPolicy.set_security_policy_apply(security_policy_id)

    return security_rule_ids

def add_share_policy_to_policy_group(sender, policy_group, security_policy_ids):
    
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
    
    share_policys = {}
    for policy_id, policy in security_policys.items():
        policy_type = policy["security_policy_type"]
        
        if policy_type != const.SEC_POLICY_TYPE_SAHRE:
            continue

        share_policys[policy_id] = policy
    
    slave_policys = []
    
    for policy_id, policy in share_policys.items():

        zone_id = sender["zone"]
        if policy_group.get("zone"):
            zone_id = policy_group["zone"]
        slave_sender = {"zone": zone_id}

        ret = create_share_slave_security_policy(slave_sender, policy, policy_group)
        if isinstance(ret, Error):
            return ret
        if ret:
            slave_policys.append(ret)

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

    return slave_policys