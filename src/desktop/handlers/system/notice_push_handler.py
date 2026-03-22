import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    PUBLIC_COLUMNS,
    DEFAULT_LIMIT,
)
import db.constants as dbconst
from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success
)
from utils.json import json_load
from utils.misc import get_columns
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.system.notice_push as NoticePush
import api.user.user as APIUser
import constants as const

def handle_describe_notice_pushs(req):
    
    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_NOTICE_PUSH)
    notice_ids = req.get("notices")
    if notice_ids:
        filter_conditions["notice_id"] = notice_ids

    ret = NoticePush.check_notice_zone_scope(sender, notice_ids)
    if ret is None:
        rep = {'total_count': 0} 
        return return_items(req, None, "notice_push", **rep)
    
    if ret:
        filter_conditions["notice_id"] = ret

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_NOTICE_PUSH]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_NOTICE_PUSH]        
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_NOTICE_PUSH]
    
    if APIUser.is_normal_console(sender) and "zone" in filter_conditions:
        del filter_conditions["zone"]

    if APIUser.is_normal_console(sender):
        filter_conditions["status"] = const.NOTICE_STATUS_NORMAL

    notice_push_set = ctx.pg.get_by_filter(dbconst.TB_NOTICE_PUSH, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(dbconst.TB_NOTICE_PUSH, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if notice_push_set is None:
        logger.error("describe notice push failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    NoticePush.format_notice_push(sender, notice_push_set)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_NOTICE_PUSH, filter_conditions)
    if total_count is None:
        logger.error("get notice push count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, notice_push_set, "notice_push", **rep)

def handle_create_notice_push(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["title", "content"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = NoticePush.check_create_notice_push(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = NoticePush.check_executime_and_expired_time(req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = NoticePush.create_notice_push(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    notice_id = ret
    
    ret = {"notice_id": notice_id}
    return return_success(req, None, **ret)

def handle_modify_notice_push_attributes(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["notice"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    notice_id = req["notice"]

    need_maint_columns = get_columns(req, ["title", "content", "notice_level", "expired_time", "execute_time", "is_permanent", "force_read"])

    ret = NoticePush.check_modify_notice_push_attributes(sender, notice_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    if need_maint_columns:
        
        is_permanent = need_maint_columns.get("is_permanent", 0)
        if is_permanent:
            ret = NoticePush.set_notice_permanent_time(notice_id)
            if isinstance(ret, Error):
                return return_error(req, ret)

            if "expired_time" in need_maint_columns:
                del need_maint_columns["expired_time"]
            if "execute_time" in need_maint_columns:
                del need_maint_columns["execute_time"]
        else:
            ret = NoticePush.check_executime_and_expired_time(need_maint_columns)
            if isinstance(ret, Error):
                return return_error(req, ret)
        
        if "is_permanent" in need_maint_columns:
            del need_maint_columns["is_permanent"]
        
        ret = NoticePush.modify_notice_push_attributes(notice_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    return return_success(req, None)

def handle_delete_notice_pushs(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["notices"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    notice_ids = req["notices"]
    
    ret = NoticePush.check_delete_notice(sender, notice_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    notices = ret
    
    ret = NoticePush.delete_notice_pushs(notices)
    if isinstance(ret, Error):
        return return_error(req, ret)
    return return_success(req, None)

def handle_modify_notice_push_zone_user(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["notice", "zone_users"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    zone_users = json_load(req["zone_users"])
    notice_id = req["notice"]
    scope = req.get("scope")

    ret = NoticePush.check_set_notice_zone_user(sender, notice_id, zone_users)
    if isinstance(ret, Error):
        return return_error(req, ret)
    if not ret:
        zone_users = {}
    else:
        zone_users = ret

    ret = NoticePush.modify_notice_push_zone_user(sender, notice_id, zone_users, scope)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_set_user_notice_read(req):
    
    ret = ResCheck.check_request_param(req, ["notice", "user_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    notice_id = req["notice"]
    user_id = req["user_id"]
    
    ret = NoticePush.set_user_notice_read(notice_id, user_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)
