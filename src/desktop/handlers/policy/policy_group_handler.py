import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    PUBLIC_COLUMNS,
    TB_POLICY_GROUP    
)
import db.constants as dbconst
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
from utils.misc import get_columns
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.policy.policy_group as PolicyGroup
import resource_control.policy.default_security as DefaultSecurity
import resource_control.policy.share_security as ShareSecurity
import resource_control.policy.security_policy as SecurityPolicy
import resource_control.permission as Permission

def handle_describe_policy_groups(req):

    ctx = context.instance()
    sender = req["sender"]

    # get security group set
    filter_conditions = build_filter_conditions(req, TB_POLICY_GROUP)
    
    policy_group_ids = req.get("policy_groups")
    if policy_group_ids:
        filter_conditions["policy_group_id"] = policy_group_ids
    
    ignore_zone = req.get("ignore_zone")
    if ignore_zone:
        if "zone" in filter_conditions:
            del filter_conditions["zone"]
    
    DefaultSecurity.init_default_policy_group(sender["zone"])
    
    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_POLICY_GROUP]
    elif is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_POLICY_GROUP]
    else:
        display_columns = PUBLIC_COLUMNS[TB_POLICY_GROUP]

    policy_group_set = ctx.pg.get_by_filter(TB_POLICY_GROUP, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_POLICY_GROUP, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if policy_group_set is None:
        logger.error("describe policy group fail [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    verbose = req.get("verbose", 0)
    if verbose > 0:
        PolicyGroup.format_policy_groups(policy_group_set)
    
    # get total count
    total_count = ctx.pg.get_count(TB_POLICY_GROUP, filter_conditions)
    if total_count is None:
        logger.error("describe policy group total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {'total_count':total_count} 
    return return_items(req, policy_group_set, "policy_group", **rep)

def handle_create_policy_group(req):

    sender = req["sender"]
    ctx = context.instance()
    ret = ResCheck.check_request_param(req, ["policy_group_type"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = PolicyGroup.register_policy_group(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    policy_group_id = ret

    ret = DefaultSecurity.load_default_security_policy(sender, policy_group_id)
    if isinstance(ret, Error):
        
        policy_groups = ctx.pgm.get_policy_groups(policy_group_id)
        if policy_groups:
            PolicyGroup.delete_policy_groups(sender, policy_groups)

        return return_error(req, ret)
    
    ret = PolicyGroup.apply_policy_group(sender, policy_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    # register resource permission
    Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_POLICY_GROUP, policy_group_id, sender["zone"], dbconst.RES_SCOPE_DELETE)

    resp = {'policy_group': policy_group_id}
    return return_success(req, None, **resp)

def handle_modify_policy_group_attributes(req):

    # check request param
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["policy_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    policy_group_id = req["policy_group"]
    
    ret = PolicyGroup.check_policy_group_vaild(policy_group_id, False)
    if isinstance(ret, Error):
        return return_error(req, ret)
    policy_group = ret[policy_group_id]

    need_maint_columns = get_columns(req, ["policy_group_name", "description"])
    if need_maint_columns:
        ret = PolicyGroup.modify_policy_group_attributes(sender, policy_group, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    return return_success(req, None)

def handle_delete_policy_groups(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["policy_groups"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    policy_group_ids = req["policy_groups"]
    
    ret = PolicyGroup.check_policy_group_vaild(policy_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    policy_groups = ret
    
    ret = ShareSecurity.check_delete_share_security_policys(sender, policy_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = PolicyGroup.check_delete_policy_groups(sender, policy_groups)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = PolicyGroup.delete_policy_groups(sender, policy_groups)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # clear resource permission
    Permission.clear_user_resource_scope(resource_ids=policy_groups.keys())

    return return_success(req, None)

def handle_add_resource_to_policy_group(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["policy_group", "resources"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    policy_group_id = req["policy_group"]
    resource_ids = req["resources"]

    ret = PolicyGroup.check_policy_group_vaild(policy_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    policy_group = ret[policy_group_id]

    ret = PolicyGroup.check_policy_group_resource(policy_group, resource_ids, is_add=True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = PolicyGroup.change_resource_to_policy_group(sender, policy_group, resource_ids, is_lock=1)
    if isinstance(ret, Error) or not ret:
        return ret
    if ret:
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_remove_resource_from_policy_group(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["resources"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    resource_ids = req["resources"]

    ret = PolicyGroup.delete_resource_from_policy_group(sender, resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    job_uuids = ret
    
    return return_success(req, None, job_uuids)

def handle_add_policy_to_policy_group(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["policy_groups", "policys"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    policy_group_ids = req["policy_groups"]
    policy_ids = req["policys"]
    ret = PolicyGroup.check_policy_group_vaild(policy_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    policy_groups = ret

    ret = ShareSecurity.check_add_share_security_policys(sender, policy_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    security_policy_ids, share_security_policy_ids = ret

    for _, policy_group in policy_groups.items():
        ret = PolicyGroup.check_policy_group_policy(policy_group, policy_ids, is_add=True)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    for policy_group_id, policy_group in policy_groups.items():
        
        if share_security_policy_ids:
            ret = ShareSecurity.add_share_policy_to_policy_group(sender, policy_group, policy_ids)
            if isinstance(ret, Error):
                return return_error(req, ret)
            slave_policy_ids = ret

            ret = SecurityPolicy.apply_security_policy(sender, slave_policy_ids)
            if isinstance(ret, Error):
                return return_error(req, ret)

        if security_policy_ids:
                
            ret = PolicyGroup.add_policy_to_policy_group(sender, policy_group, policy_ids)
            if isinstance(ret, Error):
                return return_error(req, ret)
    
            ret = PolicyGroup.apply_policy_group(sender, policy_group_id)
            if isinstance(ret, Error):
                return return_error(req, ret)

    return return_success(req, None)

def handle_remove_policy_from_policy_group(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["policy_groups", "policys"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    policy_group_ids = req["policy_groups"]
    policy_ids = req["policys"]
    ret = PolicyGroup.check_policy_group_vaild(policy_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    policy_groups = ret
    
    ret = ShareSecurity.check_delete_share_security_policys(sender, policy_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    for _, policy_group in policy_groups.items():
        ret = PolicyGroup.check_policy_group_policy(policy_group, policy_ids, is_remove=True)
        if isinstance(ret, Error):
            return return_error(req, ret)

    for policy_group_id, policy_group in policy_groups.items():
        ret = PolicyGroup.remove_policy_from_policy_group(sender, policy_group, policy_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        ret = PolicyGroup.apply_policy_group(sender, policy_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_apply_policy_group(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["policy_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    policy_group_id = req["policy_group"]
    ret = PolicyGroup.check_policy_group_vaild(policy_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = PolicyGroup.apply_policy_group(sender, policy_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    job_uuid = ret
    return return_success(req, None, job_uuid)

def handle_modify_resource_group_policy(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["resource_group", "policy_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    resource_group_id = req["resource_group"]
    policy_group = req["policy_group"]
    
    job_uuid = None
    ret = PolicyGroup.check_resource_group_policy(resource_group_id, policy_group)
    if isinstance(ret, Error):
        return return_error(req, ret)
    new_policys = ret

    if new_policys:

        ret = PolicyGroup.set_resource_group_policy(sender, resource_group_id, new_policys)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        if ret:
            job_uuid = ret

    return return_success(req, None, job_uuid)
