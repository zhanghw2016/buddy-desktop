'''
Created on 2018

@author: tian
'''

import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    TB_RADIUS_SERVICE
)
from common import (
    build_filter_conditions,
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
import constants as const
import resource_control.desktop.resource_permission as ResCheck
import resource_control.auth.radius_service as RadiusService
import resource_control.auth.radius as Radius
import resource_control.user.session as Session
import resource_control.user.user as ZoneUser
import api.user.user as APIUser

def handle_describe_radius_services(req):
    
    ctx = context.instance()
    sender = req["sender"]

    # get auth service set
    filter_conditions = build_filter_conditions(req, TB_RADIUS_SERVICE)
    radius_service_ids = req.get("radius_services")
    if radius_service_ids:
        filter_conditions["radius_service_id"] = radius_service_ids

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_RADIUS_SERVICE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = []
    else:
        display_columns = []

    radius_service_set = ctx.pg.get_by_filter(TB_RADIUS_SERVICE, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_RADIUS_SERVICE, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if radius_service_set is None:
        logger.error("describe radius service failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {}
    if req.get("verbose", 0) > 0:
        RadiusService.format_radius_services(radius_service_set)
    
    # get total count
    
    if APIUser.is_global_admin_user(sender):
        total_count = ctx.pg.get_count(TB_RADIUS_SERVICE, filter_conditions)
        if total_count is None:
            logger.error("describe auth service total count fail")
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    else:
        total_count = 0

    rep['total_count'] = total_count
    return return_items(req, radius_service_set, "radius_service", **rep)

def handle_create_radius_service(req):
    
    ret = ResCheck.check_request_param(req, ["host", "port", "acct_session", "identifier", 
                                             "secret"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    host = req["host"]
    ret = RadiusService.check_radius_service_host(host)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = RadiusService.create_radius_service(req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    radius_service_id = ret

    resp = {'radius_service': radius_service_id}
    return return_success(req, None, **resp)

def handle_modify_radius_service_attributes(req):
    
    # check request param
    ret = ResCheck.check_request_param(req, ["radius_service"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    radius_service_id = req["radius_service"]
    
    ret = RadiusService.check_radius_service_vaild(radius_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    need_maint_columns = get_columns(req, ["radius_service_name", "host", "port", "acct_session",
                                           "identifier", "secret", "enable_radius", "ou_dn"])
    if need_maint_columns:
        ret = RadiusService.modify_radius_service_attributes(radius_service_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_delete_radius_services(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["radius_services"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    radius_service_ids = req["radius_services"]

    ret = RadiusService.check_radius_service_vaild(radius_service_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = RadiusService.delete_radius_services(radius_service_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_add_auth_radius_users(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["radius_service", "user_ids", "check_radius"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    radius_service_id = req["radius_service"]
    user_ids = req["user_ids"]
    check_radius = req["check_radius"]
    
    ret = RadiusService.check_radius_service_vaild(radius_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    radius_service = ret[radius_service_id]

    ret = RadiusService.check_add_auth_radius_users(sender, radius_service, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_users = ret

    ret = RadiusService.add_auth_radius_users(radius_service, desktop_users, check_radius)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_remove_auth_radius_users(req):
    
    ret = ResCheck.check_request_param(req, ["radius_service", "user_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    radius_service_id = req["radius_service"]
    user_ids = req["user_ids"]

    ret = RadiusService.check_radius_service_vaild(radius_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = RadiusService.check_remove_auth_radius_service(radius_service_id, user_ids)
    if ret:
        ret = RadiusService.remove_auht_radius_service(radius_service_id, user_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_modify_radius_user_attributes(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["user_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    user_id = req["user_id"]
    
    ret = RadiusService.check_auth_radius_users(user_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    need_maint_columns = get_columns(req, ["check_radius"])
    if need_maint_columns:
        ret = RadiusService.modify_radius_user_attributes(user_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)            

def handle_check_radius_token(req):
    
    ctx = context.instance()
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["user_id", "token"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    user_id = req["user_id"]
    token =  req['token']
    client_ip =  req.get('client_ip', '127.0.0.1')

    ret = APIUser.check_desktop_user(ctx, user_id, const.USER_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)

    if not ret:
        logger.error("[%s] not found in this request" % user_id)
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                                           ErrorMsg.ERR_MSG_MISSING_PARAMETER, user_id))
    
    desktop_user = ret[user_id]

    auth_radius = Radius.check_radius_user(desktop_user)
    if not auth_radius:
        auth_radius = None

    if auth_radius:
        ret = Radius.check_radius_token(auth_radius, desktop_user["user_name"], token)
        if isinstance(ret, Error):
            ZoneUser.create_user_login_record(user_id, sender["zone"], client_ip, status=const.LOGIN_STATUS_FAIL, errmsg="Check Radius Token Error")
            return return_error(req, ret)

    # create session
    ret = Session.create_session(user_id)
    if not ret:
        ZoneUser.create_user_login_record(user_id, sender["zone"], client_ip, status=const.LOGIN_STATUS_FAIL, errmsg="Create Session Error")
        return return_error(req, Error(ErrorCodes.SESSION_EXPIRED))
    
    rep = {}
    # record user login
    ZoneUser.create_user_login_record(user_id, sender["zone"], client_ip)

    rep["sk"] = ret
    rep["zone"] = sender["zone"]

    return return_success(req, rep)

