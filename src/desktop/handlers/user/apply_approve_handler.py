'''
Created on 2017-4-6

@author: yunify
'''
from log.logger import logger
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from common import (
    is_admin_user,
)
from utils.misc import get_columns
from common import (
    get_reverse,
    get_sort_key,
    build_filter_conditions,
    return_success, 
    return_error,
    return_items,
)
from db.constants import (
    PUBLIC_COLUMNS,
    GOLBAL_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
)
import context
import db.constants as dbconst
import resource_control.desktop.resource_permission as ResCheck
import resource_control.user.apply_approve as ApplyApporve

import api.user.user as APIUser

def handle_create_desktop_apply_form(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["apply_user_id", "approve_user_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = ApplyApporve.check_create_desktop_apply_form(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    apply_group_id = ret
    
    ret = ApplyApporve.check_starttime_and_endtime(req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = ApplyApporve.create_desktop_apply_form(sender, req, apply_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    apply_id = ret

    ret = {"apply_id": apply_id}
    return return_success(req, None, **ret)

def handle_describe_desktop_apply_form(req):

    ctx = context.instance()
    sender = req["sender"]

    apply_user_id = req.get('apply_user_id', '')
    if not is_admin_user(req['sender']):
        if apply_user_id:
            if apply_user_id != req['sender']['owner']:
                logger.error("apply form permission error, only describe self apply form.")
                return return_error(req, Error(ErrorCodes.APPLY_FORM_PERMISSION_ERROR,
                                               ErrorMsg.ERR_MSG_APPLY_FORM_PERMISSION_ERROR))
        else:
            apply_user_id = req['sender']['owner']
    
    ApplyApporve.refresh_apply_forms(zone_id = sender["zone"])
    
    filter_conditions = build_filter_conditions(req, dbconst.TB_APPLY)
    apply_ids = req.get("apply_ids")
    if apply_ids:
        filter_conditions["apply_id"] = apply_ids
    
    filter_conditions["zone_id"] = sender["zone"]

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_APPLY]
    elif APIUser.is_console_admin_user(sender):
        if "zone_id" in filter_conditions:
            del filter_conditions["zone_id"]
        display_columns = PUBLIC_COLUMNS[dbconst.TB_APPLY]
    else:
        if "zone_id" in filter_conditions:
            del filter_conditions["zone_id"]
        display_columns = PUBLIC_COLUMNS[dbconst.TB_APPLY]
    logger.info("filter_conditions == %s" %(filter_conditions))
    apply_set = ctx.pg.get_by_filter(dbconst.TB_APPLY, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_APPLY, req.get("sort_key")),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", DEFAULT_LIMIT),
                                           )

    if apply_set is None:
        logger.error("describe apply form failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format apply_set
    ApplyApporve.format_apply(apply_set)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_APPLY, filter_conditions)
    if total_count is None:
        logger.error("get apply form count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, apply_set, "apply", **rep)

def handle_modify_desktop_apply_form(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["apply_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_id = req["apply_id"]
    
    ret = ApplyApporve.check_apply_form_valid(apply_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    apply_forms = ret

    ret = ApplyApporve.check_starttime_and_endtime(req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.check_modify_apply_form(sender, apply_forms)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    need_maint_columns = get_columns(req, ["apply_title", "apply_parameter", "approve_user_id", "apply_description", "start_time", "end_time"])
    if need_maint_columns:
        ret = ApplyApporve.modify_apply_form(apply_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        if "start_time" in need_maint_columns or "end_time" in need_maint_columns:
            ret = ApplyApporve.refresh_apply_forms(apply_id)
            if isinstance(ret, Error):
                return return_error(req, ret)
        
    return return_success(req, None)

def handle_delete_desktop_apply_form(req):
    
    # check request param
    ret = ResCheck.check_request_param(req, ["applys"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_ids = req["applys"]
    
    ret = ApplyApporve.check_apply_form_valid(apply_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # delete apply form
    ret = ApplyApporve.delete_apply_form(apply_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, {'apply_ids': apply_ids})

def handle_deal_desktop_apply_form(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ['apply_id', 'approve_user_id', 'result'])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_id = req['apply_id']
    result = req['result']
    start_time = req.get("start_time")
    end_time = req.get("end_time")
    
    ret = ApplyApporve.check_apply_form_valid(apply_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    apply_form = ret[apply_id]
    
    ret = ApplyApporve.check_deal_desktop_apply_form(apply_form, sender["owner"])
    if isinstance(ret, Error): 
        return return_error(req, ret)

    ret = ApplyApporve.deal_desktop_apply_form(apply_form, result, start_time, end_time)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = ApplyApporve.refresh_apply_forms(apply_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, {'apply_id': apply_id})

def handle_create_resource_apply_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["apply_group_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    apply_group_name = req["apply_group_name"]
    
    ret = ApplyApporve.check_apply_group_name(sender, apply_group_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.create_apply_group_form(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    apply_group_id = ret

    ret = {"apply_group_id": apply_group_id}
    return return_success(req, None, **ret)

def handle_modify_resource_apply_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["apply_group_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_group_id = req["apply_group_id"]
    
    ret = ApplyApporve.check_apply_group_valid(apply_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    need_maint_columns = get_columns(req, ["apply_group_name", "description"])
    if need_maint_columns:
        
        if "apply_group_name" in need_maint_columns:
            apply_group_name = need_maint_columns["apply_group_name"]
            ret = ApplyApporve.check_apply_group_name(sender, apply_group_name, apply_group_id)
            if isinstance(ret, Error):
                return return_error(req, ret)
    
        ret = ApplyApporve.modify_apply_group(apply_group_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_describe_resource_apply_groups(req):

    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_APPLY_GROUP)
    apply_group_ids = req.get("apply_group_ids")
    if apply_group_ids:
        filter_conditions["apply_group_id"] = apply_group_ids

    apply_group_name = req.get("apply_group_name")
    if apply_group_name:
        filter_conditions["apply_group_name"] = apply_group_name

    filter_conditions["zone_id"] = sender["zone"]

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_APPLY_GROUP]
    elif APIUser.is_console_admin_user(sender):
        display_columns = []
    else:
        display_columns = []

    apply_group_set = ctx.pg.get_by_filter(dbconst.TB_APPLY_GROUP, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_APPLY_GROUP, req.get("sort_key")),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", DEFAULT_LIMIT),
                                           )

    if apply_group_set is None:
        logger.error("describe apply group form failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format apply_group_set
    check_resource_group = req.get("check_resource_group", 0)
    ApplyApporve.format_apply_group(apply_group_set, check_resource_group)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_APPLY_GROUP, filter_conditions)
    if total_count is None:
        logger.error("get apply group form count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, apply_group_set, "apply_group", **rep)

def handle_delete_resource_apply_groups(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["apply_group_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_group_ids = req["apply_group_ids"]

    ret = ApplyApporve.check_apply_group_valid(apply_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # delete apply group form
    ret = ApplyApporve.delete_apply_group_form(apply_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_insert_user_to_apply_group(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["apply_group_id", "user_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_group_id = req['apply_group_id']
    user_ids = req["user_ids"]

    ret = ApplyApporve.check_apply_group_valid(apply_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.check_apply_group_user_valid(apply_group_id, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.insert_user_to_apply_group(apply_group_id, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_remove_user_from_apply_group(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["apply_group_id","user_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_group_id = req['apply_group_id']
    user_ids = req['user_ids']

    ret = ApplyApporve.check_apply_group_valid(apply_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # remove user from apply group
    ret = ApplyApporve.remove_user_from_apply_group(apply_group_id, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_insert_resource_to_apply_group(req):
    
    # check request param
    ret = ResCheck.check_request_param(req, ["apply_group_id","resource_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_group_id = req['apply_group_id']
    resource_ids = req['resource_ids']

    ret = ApplyApporve.check_apply_group_valid(apply_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = ApplyApporve.check_add_resource_to_apply_group(apply_group_id, resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    # insert apply group user form
    ret = ApplyApporve.insert_resource_to_apply_group(apply_group_id,resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_remove_resource_from_apply_group(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["apply_group_id","resource_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_group_id = req['apply_group_id']
    resource_ids = req['resource_ids']

    ret = ApplyApporve.check_apply_group_valid(apply_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # remove apply group user form
    ret = ApplyApporve.remove_resource_from_apply_group(apply_group_id,resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_create_resource_approve_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["approve_group_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    approve_group_name = req["approve_group_name"]
    
    ret = ApplyApporve.check_approve_group_name(sender, approve_group_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.create_approve_group_form(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    approve_group_id = ret

    ret = {"approve_group_id": approve_group_id}
    return return_success(req, None, **ret)

def handle_modify_resource_approve_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["approve_group_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    approve_group_id = req["approve_group_id"]

    ret = ApplyApporve.check_approve_group_vaild(approve_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
   
    need_maint_columns = get_columns(req, ["approve_group_name", "description"])
    if need_maint_columns:
        
        if "approve_group_name" in need_maint_columns:
            approve_group_name = need_maint_columns["approve_group_name"]
            ret = ApplyApporve.check_approve_group_name(sender, approve_group_name, approve_group_id)
            if isinstance(ret, Error):
                return return_error(req, ret)

        ret = ApplyApporve.modify_approve_group_form(approve_group_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_describe_resource_approve_groups(req):

    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_APPROVE_GROUP)
    approve_group_ids = req.get("approve_group_ids")
    if approve_group_ids:
        filter_conditions["approve_group_id"] = approve_group_ids

    approve_group_name = req.get("approve_group_name")
    if approve_group_name:
        filter_conditions["approve_group_name"] = approve_group_name

    filter_conditions["zone_id"] = sender["zone"]

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_APPROVE_GROUP]
    elif APIUser.is_console_admin_user(sender):
        display_columns = []
    else:
        display_columns = []

    approve_group_set = ctx.pg.get_by_filter(dbconst.TB_APPROVE_GROUP, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_APPROVE_GROUP, req.get("sort_key")),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", DEFAULT_LIMIT),
                                           )

    if approve_group_set is None:
        logger.error("describe approve group form failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format approve_group_set
    ApplyApporve.format_approve_group(approve_group_set)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_APPROVE_GROUP, filter_conditions)
    if total_count is None:
        logger.error("get approve group form count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, approve_group_set, "approve_group", **rep)

def handle_delete_resource_approve_groups(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["approve_group_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    approve_group_ids = req["approve_group_ids"]

    ret = ApplyApporve.check_approve_group_vaild(approve_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.delete_resource_approve_groups(approve_group_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, {'approve_group_ids': approve_group_ids})

def handle_insert_user_to_approve_group(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["approve_group_id", "user_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    approve_group_id = req['approve_group_id']
    user_ids = req["user_ids"]

    ret = ApplyApporve.check_approve_group_user_valid(approve_group_id, user_ids, is_add=True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.insert_user_to_approve_group(approve_group_id, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_remove_user_from_approve_group(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["approve_group_id","user_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    approve_group_id = req['approve_group_id']
    user_ids = req['user_ids']
    # remove approve group user
    ret = ApplyApporve.remove_user_from_approve_group(approve_group_id, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, {'approve_group_id': approve_group_id})

def handle_map_apply_group_and_approve_group(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["apply_group_id","approve_group_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_group_id = req['apply_group_id']
    approve_group_id = req['approve_group_id']
    
    ret = ApplyApporve.check_apply_group_valid(apply_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.check_approve_group_vaild(approve_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.check_approve_apply_group_map(approve_group_id, approve_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.map_apply_group_and_approve_group(apply_group_id, approve_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_unmap_apply_group_and_approve_group(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["apply_group_id","approve_group_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_group_id = req['apply_group_id']
    approve_group_id = req['approve_group_id']

    ret = ApplyApporve.check_apply_group_valid(apply_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.check_approve_group_vaild(approve_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ApplyApporve.detach_approve_group_from_apply_group(apply_group_id, approve_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_get_approve_users(req):

    ctx = context.instance()
    # check request param
    ret = ResCheck.check_request_param(req, ["apply_user_id","resource_group_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    apply_user_id = req.get("apply_user_id", "")
    resource_group_id = req.get("resource_group_id", "")

    user_in_apply_groups = ApplyApporve.describe_user_in_apply_groups(apply_user_id)
    resource_in_apply_groups = ApplyApporve.describe_resource_in_apply_groups(resource_group_id)
    
    apply_groups = []
    for user_in_apply_group in user_in_apply_groups:
        for resource_in_apply_group in resource_in_apply_groups:
            if user_in_apply_group == resource_in_apply_group:
                apply_groups.append(user_in_apply_group)

    if len(apply_groups) == 0:
        return return_success(req, {"approve_user_set": []})

    approve_groups = ApplyApporve.describe_map_apply_group_and_approve_group(apply_groups, None)
    approve_user_set = []
    for approve_group in approve_groups:
        approve_group_id = approve_group["approve_group_id"]
        users = ApplyApporve.describe_approve_group_users(approve_group_id)
        user_ids = users.keys()
        for user_id in user_ids:
            user = ctx.pgm.get_desktop_user_detail(user_id, columns=["user_id", "user_name", "real_name"])
            approve_user_set.append(user)

    return return_success(req, {"approve_user_set": approve_user_set})
