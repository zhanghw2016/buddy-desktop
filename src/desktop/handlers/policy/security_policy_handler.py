import context
import constants as const
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    PUBLIC_COLUMNS,
    TB_SECURITY_POLICY,
    TB_SECURITY_IPSET,
    TB_SECURITY_RULE
)
from common import (
    build_filter_conditions,
    is_global_admin_user,
    is_console_admin_user,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success
)

from utils.id_tool import(
    UUID_TYPE_SECURITY_POLICY_SHARE,
    UUID_TYPE_SECURITY_POLICY_SGRS
)
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.policy.security_policy as SecurityPolicy
import resource_control.policy.share_security as ShareSecurity
from utils.misc import get_columns

def handle_describe_desktop_security_policys(req):

    ctx = context.instance()
    sender = req["sender"]

    # get security group set
    filter_conditions = build_filter_conditions(req, TB_SECURITY_POLICY)
    security_policy_ids = req.get("security_policys")
    if security_policy_ids:
        filter_conditions["security_policy_id"] = security_policy_ids

    policy_group_id = req.get("policy_group")
    if policy_group_id:
        filter_conditions["policy_group_id"] = policy_group_id

    security_policy_type = req.get("security_policy_type")
    if not security_policy_type:
        filter_conditions["security_policy_type"] = const.SEC_POLICY_TYPE_SGRS
    
    if security_policy_type and const.SEC_POLICY_TYPE_SAHRE in security_policy_type:
        security_policy_type = [const.SEC_POLICY_TYPE_SAHRE]
        if "zone" in filter_conditions:
            del filter_conditions["zone"]
        filter_conditions["security_policy_type"] = [const.SEC_POLICY_TYPE_SAHRE]

    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_SECURITY_POLICY]
    elif is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_SECURITY_POLICY]
    else:
        display_columns = PUBLIC_COLUMNS[TB_SECURITY_POLICY]

    security_policy_set = ctx.pg.get_by_filter(TB_SECURITY_POLICY, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_SECURITY_POLICY, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if security_policy_set is None:
        logger.error("describe security policy failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {}
    SecurityPolicy.format_security_policys(security_policy_set)
    
    # get total count
    filter_conditions["policy_mode"] = const.SECURITY_POLICY_MODE_MASTER
    total_count = ctx.pg.get_count(TB_SECURITY_POLICY, filter_conditions)
    if total_count is None:
        logger.error("describe security policy total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep['total_count'] = total_count
    return return_items(req, security_policy_set, "security_policy", **rep)

def handle_create_desktop_security_policy(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["security_policy_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    security_policy_name = req["security_policy_name"]
    description = req.get("description")
    security_policy_type = req.get("security_policy_type", const.SEC_POLICY_TYPE_SGRS)
    
    security_poilcy_id = ""
    if security_policy_type == const.SEC_POLICY_TYPE_SGRS:
        ret = SecurityPolicy.create_security_poilcy(sender, security_policy_name, description=description)
        if isinstance(ret, Error):
            return return_error(req, ret)
        security_poilcy_id = ret

    elif security_policy_type == const.SEC_POLICY_TYPE_SAHRE:
        ret = ShareSecurity.create_share_security_poilcy(security_policy_name, description=description)
        if isinstance(ret, Error):
            return return_error(req, ret)
        security_poilcy_id = ret

    resp = {'security_poilcy': security_poilcy_id}
    return return_success(req, None, **resp)

def handle_modify_desktop_security_policy_attributes(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["security_policy"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_policy_id = req["security_policy"]
    
    ret = SecurityPolicy.check_security_policy_vaild(security_policy_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_policys = ret

    security_policy = security_policys[security_policy_id]
    security_policy_type = security_policy["security_policy_type"]

    need_maint_columns = get_columns(req, ["security_policy_name", "description"])
    if need_maint_columns:
        if security_policy_type == const.SEC_POLICY_TYPE_SAHRE:
            ret = ShareSecurity.modify_share_security_policy_attributes(security_policy, need_maint_columns)
            if isinstance(ret, Error):
                return return_error(req, ret)
        else:
            ret = SecurityPolicy.modify_security_policy_attributes(sender, security_policy, need_maint_columns)
            if isinstance(ret, Error):
                return return_error(req, ret)

    return return_success(req, None)

def handle_delete_desktop_security_policys(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["security_policys"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    security_policy_ids = req["security_policys"]
    
    ret = SecurityPolicy.check_security_policy_vaild(security_policy_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    security_policys = ret
    
    ret = SecurityPolicy.check_delete_security_policy(security_policys)
    if isinstance(ret, Error):
        return return_error(req, ret)
    (normal_security_policys, share_security_policys) = ret
    
    if normal_security_policys:
        ret = SecurityPolicy.delete_security_policys(sender, normal_security_policys.keys())
        if isinstance(ret, Error):
            return return_error(req, ret)

    elif share_security_policys:
        ret = ShareSecurity.delete_share_security_policys(sender, share_security_policys)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    return return_success(req, None)

def handle_apply_desktop_security_policy(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["security_policy"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_policy_id = req["security_policy"]

    ret = SecurityPolicy.check_security_policy_vaild(security_policy_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    security_policy = ret[security_policy_id]
    security_policy_type = security_policy["security_policy_type"]

    job_uuids = []
    
    if security_policy_type == const.SEC_POLICY_TYPE_SAHRE:

        ret = SecurityPolicy.check_apply_share_security_policy(security_policy)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        zone_security_policys = ret
        for zone_id, share_security_policy_ids in zone_security_policys.items():

            sender["zone"] = zone_id
            ret = SecurityPolicy.apply_security_policy(sender, share_security_policy_ids)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuids.append(ret)
        
        SecurityPolicy.set_security_policy_apply(security_policy_id, 0)

    else:
        
        if security_policy_id.startswith(UUID_TYPE_SECURITY_POLICY_SGRS):
            
            ret = SecurityPolicy.apply_security_policy(sender, security_policy_id)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuids.append(ret)
            
        else:
            policy_groups = SecurityPolicy.check_security_policy_apply(security_policy_id)
            if policy_groups:
                policy_group_ids = policy_groups.keys()
        
                ret = SecurityPolicy.set_policy_group_apply(policy_group_ids)
                if isinstance(ret, Error):
                    return return_error(req, ret)
        
                ret = SecurityPolicy.apply_policy_group(sender, policy_group_ids)
                if isinstance(ret, Error):
                    return return_error(req, ret)
        
                job_uuids.append(ret)
    
    return return_success(req, None, job_uuids)

def handle_describe_desktop_security_rules(req):
    
    ctx = context.instance()
    sender = req["sender"]

    # get security group set
    filter_conditions = build_filter_conditions(req, TB_SECURITY_RULE)
    security_policy_id = req.get("security_policy")
    if security_policy_id:
        filter_conditions["security_policy_id"] = security_policy_id
    
    security_rule_ids = req.get("security_rules")
    if security_rule_ids:
        filter_conditions["security_rule_id"] = security_rule_ids
    
    if req.get("rule_action"):
        filter_conditions["action"] = req.get("rule_action")
        
    if security_policy_id:
        if security_policy_id.startswith(UUID_TYPE_SECURITY_POLICY_SHARE):
            if "zone" in filter_conditions:
                del filter_conditions["zone"]
    
    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_SECURITY_RULE]
    elif is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_SECURITY_RULE]
    else:
        display_columns = PUBLIC_COLUMNS[TB_SECURITY_RULE]
    
    security_rule_set = ctx.pg.get_by_filter(TB_SECURITY_RULE, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_SECURITY_RULE, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if security_rule_set is None:
        logger.error("describe security rule failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))        
    # get total count
    total_count = ctx.pg.get_count(TB_SECURITY_RULE, filter_conditions)
    if total_count is None:
        logger.error("describe security rule total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {'total_count':total_count} 
    return return_items(req, security_rule_set, "security_rule", **rep)

def handle_add_desktop_security_rules(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["security_policy", "rules"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    security_policy_id = req["security_policy"]
    rules = req["rules"]

    ret = SecurityPolicy.check_security_policy_vaild(security_policy_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_policys = ret
    security_policy = security_policys[security_policy_id]
    security_policy_type = security_policy["security_policy_type"]
    
    security_rule_ids = []
    
    if security_policy_type == const.SEC_POLICY_TYPE_SAHRE:
        
        ret = ShareSecurity.create_share_security_rules(security_policy, rules)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        security_rule_ids.extend(ret)
    else:

        ret = SecurityPolicy.create_security_rules(sender["zone"], security_policy, rules)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        security_rule_ids.extend(ret)

    resp = {'security_rules': security_rule_ids}
    return return_success(req, None, **resp)

def handle_remove_desktop_security_rules(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["security_rules", "security_policy"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    security_rule_ids = req["security_rules"]
    security_policy_id = req["security_policy"]
    
    ret = SecurityPolicy.check_security_policy_vaild(security_policy_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_policys = ret
    security_policy = security_policys[security_policy_id]
    
    ret = SecurityPolicy.check_security_rules_vaild(security_rule_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_rules = ret
    
    security_policy_type = security_policy["security_policy_type"]
    if security_policy_type == const.SEC_POLICY_TYPE_SAHRE:

        ret = ShareSecurity.remove_share_rule_from_security_policy(security_policy_id, security_rules)
        if isinstance(ret, Error):
            return return_error(req, ret)
    else:
        ret = SecurityPolicy.remove_rule_from_security_policy(sender, security_policy_id, security_rules)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    return return_success(req, None)

def handle_modify_desktop_security_rule_attributes(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["security_rule"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    security_rule_id = req["security_rule"]
    
    ret = SecurityPolicy.check_security_rules_vaild(security_rule_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_rule = ret[security_rule_id]
    
    security_policy_id = security_rule["security_policy_id"]
    ret = SecurityPolicy.check_security_policy_vaild(security_policy_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_policys = ret
    security_policy = security_policys[security_policy_id]
    security_policy_type = security_policy["security_policy_type"]

    # need maintenance mode
    need_maint_columns = get_columns(req, ["priority", "security_rule_name", "protocol", "rule_action", "direction", "val1", "val2",
                                           'val3', 'disabled'])

    if need_maint_columns:
        if security_policy_type == const.SEC_POLICY_TYPE_SAHRE:
            ret = SecurityPolicy.modify_share_security_rule_attributes(security_rule, need_maint_columns)
            if isinstance(ret, Error):
                return return_error(req, ret)
        else:
            ret = SecurityPolicy.modify_security_rule_attributes(sender, security_rule, need_maint_columns)
            if isinstance(ret, Error):
                return return_error(req, ret)
        
    return return_success(req, None)
        
def handle_describe_desktop_security_ipsets(req):
    
    ctx = context.instance()
    sender = req["sender"]

    # get security group set
    filter_conditions = build_filter_conditions(req, TB_SECURITY_IPSET)
    
    security_ipset_ids = req.get("security_ipsets")
    if security_ipset_ids:
        filter_conditions["security_ipset_id"] = security_ipset_ids
    
    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_SECURITY_IPSET]
    elif is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_SECURITY_IPSET]
    else:
        display_columns = PUBLIC_COLUMNS[TB_SECURITY_IPSET]

    security_ipset_set = ctx.pg.get_by_filter(TB_SECURITY_IPSET, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_SECURITY_IPSET, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if security_ipset_set is None:
        logger.error("describe security ipset failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
        
    if req.get("verbose", 0) > 0:
        SecurityPolicy.format_security_ipsets(security_ipset_set)
    
    # get total count
    total_count = ctx.pg.get_count(TB_SECURITY_IPSET, filter_conditions)
    if total_count is None:
        logger.error("describe security policy total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {'total_count':total_count} 
    return return_items(req, security_ipset_set, "security_ipset", **rep)

def handle_create_desktop_security_ipset(req):

    sender = req["sender"]
 
    ret = ResCheck.check_request_param(req, ["ipset_type", "val"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ipset_type = req["ipset_type"]
    val = req["val"]
    security_ipset_name = req.get("security_ipset_name")
    description = req.get("description")
    
    ret = SecurityPolicy.create_security_ipset(sender, ipset_type, val, security_ipset_name, description)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    security_ipset_id = ret
    resp = {'security_ipset': security_ipset_id}
    return return_success(req, None, **resp)

def handle_delete_desktop_security_ipsets(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["security_ipsets"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    security_ipset_ids = req["security_ipsets"]
    
    ret = SecurityPolicy.check_security_ipset_vaild(security_ipset_ids, is_delete=True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = SecurityPolicy.delete_security_ipsets(sender, security_ipset_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_modify_desktop_security_ipset_attributes(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["security_ipset"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_ipset_id = req["security_ipset"]

    ret = SecurityPolicy.check_security_ipset_vaild(security_ipset_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # need maintenance mode
    need_maint_columns = get_columns(req, ['security_ipset_name', 'description', 'val'])
    if need_maint_columns:

        ret = SecurityPolicy.modify_security_ipset_attributes(sender, security_ipset_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    return return_success(req, None)

def handle_apply_desktop_security_ipset(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["security_ipset"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_ipset_id = req["security_ipset"]

    ret = SecurityPolicy.check_security_ipset_vaild(security_ipset_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = SecurityPolicy.apply_security_ipset(sender, security_ipset_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_describe_system_security_policys(req):
    
    sender = req["sender"]
    security_policy_ids = req.get("security_policys")
    
    ret = SecurityPolicy.describe_system_security_policys(sender, security_policy_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    security_policy_set = ret
    rep = {'total_count': len(security_policy_set) if security_policy_set else 0} 
    return return_items(req, security_policy_set, "security_policy", **rep)

def handle_describe_system_security_ipsets(req):
    
    sender = req["sender"]
    security_ipset_ids = req.get("security_ipsets")
    
    ret = SecurityPolicy.describe_system_security_ipsets(sender, security_ipset_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    security_ipset_set = ret
    rep = {'total_count': len(security_ipset_set) if security_ipset_set else 0 } 
    return return_items(req, security_ipset_set, "security_ipset", **rep)

def handle_load_system_security_rules(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["security_rules", "security_policy"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_rule_ids = req["security_rules"]
    security_policy_id = req["security_policy"]

    ret = SecurityPolicy.check_security_policy_vaild(security_policy_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_policys = ret
    security_policy = security_policys[security_policy_id]
    
    ret = SecurityPolicy.load_security_rules(sender, security_policy, security_rule_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    resp = {'security_poilcy': ret}
    return return_success(req, None, **resp)

def handle_load_system_security_ipsets(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["security_ipsets"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    security_ipset_ids = req["security_ipsets"]

    ret = SecurityPolicy.load_security_ipsets(sender, security_ipset_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    resp = {'security_ipset': ret}
    return return_success(req, None, **resp)
