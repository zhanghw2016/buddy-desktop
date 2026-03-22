
import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    TB_AUTH_SERVICE
)
from common import (
    build_filter_conditions,

    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success
)
import constants as const
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.auth.auth_service as AuthService
from utils.misc import get_columns
import api.user.user as APIUser
import resource_control.auth.auth_user as AuthUser

def handle_describe_auth_services(req):

    ctx = context.instance()
    sender = req["sender"]

    # get auth service set
    filter_conditions = build_filter_conditions(req, TB_AUTH_SERVICE)
    auth_service_ids = req.get("auth_services")
    if auth_service_ids:
        filter_conditions["auth_service_id"] = auth_service_ids

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_AUTH_SERVICE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = []
    else:
        display_columns = []

    auth_service_set = ctx.pg.get_by_filter(TB_AUTH_SERVICE, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_AUTH_SERVICE, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if auth_service_set is None:
        logger.error("describe auth service failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {}
    if req.get("verbose", 0) > 0:
        AuthService.format_auth_services(auth_service_set)
    
    # get total count
   
    if APIUser.is_global_admin_user(sender):
        total_count = ctx.pg.get_count(TB_AUTH_SERVICE, filter_conditions)
        if total_count is None:
            logger.error("describe auth service total count fail")
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    else:
        total_count = 0

    rep['total_count'] = total_count
    return return_items(req, auth_service_set, "auth_service", **rep)

def handle_create_auth_service(req):

    ret = ResCheck.check_request_param(req, ["auth_service_type", "admin_name", "admin_password", "base_dn", 
                                             "domain"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    auth_service_type = req["auth_service_type"]
    
    AuthUser.check_auth_unicode_param(req)
    
    if auth_service_type != const.AUTH_TYPE_LOCAL:
        ret = AuthService.check_auth_service_config(req)
        if isinstance(ret, Error):
            return return_error(req, ret)

    ret = AuthService.check_auth_service_domain(req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthService.create_auth_service(req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    auth_service_id = ret

    resp = {'auth_service': auth_service_id}
    return return_success(req, None, **resp)

def handle_check_auth_service_ous(req):

    ret = ResCheck.check_request_param(req, ["auth_service_type", "admin_name", "admin_password", 
                                             "domain", "host", "port", "secret_port"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = AuthService.check_auth_service_config(req, scope=1)
    if isinstance(ret, Error):
        return return_error(req, ret)    
    
    ret = AuthService.format_check_auth_ous(ret, req["domain"])
    
    rep = {}
    rep['total_count'] = len(ret)
    return return_items(req, ret, "auth_ous", **rep)

def handle_modify_auth_service_attributes(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["auth_service"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    auth_service_id = req["auth_service"]
    
    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthService.check_auth_service_config(req, auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    need_maint_columns = get_columns(req, ["auth_service_name", "admin_name", "admin_password",
                                             "host", "port", "secret_port", "is_sync", "description", "modify_password"])

    if need_maint_columns:
        ret = AuthService.modify_auth_service_attributes(auth_service_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    return return_success(req, None)

def handle_delete_auth_services(req):
    
    # check request param
    ret = ResCheck.check_request_param(req, ["auth_services"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    auth_service_ids = req["auth_services"]
    
    ret = AuthService.check_auth_service_vaild(auth_service_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_services = ret

    ret = AuthService.check_delete_auth_service(auth_service_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthService.delete_auth_services(auth_services)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_add_auth_service_to_zone(req):
    
    ret = ResCheck.check_request_param(req, ["auth_service", "zone_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    zone_id = req["zone_id"]
    base_dn = req.get("base_dn")

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthService.check_auth_zone(zone_id, is_add=True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = AuthService.add_auth_service_to_zone(auth_service, zone_id, base_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_remove_auth_service_from_zones(req):
    
    ret = ResCheck.check_request_param(req, ["auth_service", "zone_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    auth_service_id = req["auth_service"]
    zone_ids = req["zone_ids"]

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    for zone_id in zone_ids:

        ret = AuthService.check_auth_zone(zone_id)
        if isinstance(ret, Error):
            return return_error(req, ret)

    ret = AuthService.remove_auth_service_from_zones(auth_service_id, zone_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_refresh_auth_service(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["auth_service"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    AuthUser.check_auth_unicode_param(req)
    
    auth_service_id = req["auth_service"]
    base_dn = req.get("base_dn")

    ret = AuthService.check_auth_service_vaild(auth_service_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    auth_service = ret[auth_service_id]

    ret = AuthService.check_auth_service_base_dn(sender, auth_service, base_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)
    base_dn = ret

    ret = AuthService.refresh_auth_service(auth_service, base_dn)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

