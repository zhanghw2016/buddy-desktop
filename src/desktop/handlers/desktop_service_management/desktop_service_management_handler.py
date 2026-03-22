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
    return_success,
    is_global_admin_user,
    is_console_admin_user,
    check_global_admin_console,
    filter_out_none,
)
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.desktop_service_management.desktop_service_management as DesktopServiceManagement
import api.user.user as APIUser
import constants as const

def handle_describe_desktop_service_managements(req):

    ctx = context.instance()
    sender = req["sender"]
    filter_conditions = build_filter_conditions(req, dbconst.TB_DESKTOP_SERVICE_MANAGEMENT)

    service_management_type = req.get("service_management_type")
    if service_management_type:
        filter_conditions["service_management_type"] = service_management_type
        if service_management_type == const.CITRIX_SERVICE_MANAGEMENT_TYPE:
            filter_conditions["zone_id"] = sender["zone"]

    service_type = req.get("service_type")
    if service_type:
        filter_conditions["service_type"] = service_type

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_DESKTOP_SERVICE_MANAGEMENT]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_DESKTOP_SERVICE_MANAGEMENT]
    else:
        display_columns = []

    desktop_service_management_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, filter_conditions, display_columns,
                                           sort_key=get_sort_key(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, req.get("sort_key")),
                                           reverse=get_reverse(req.get("reverse")),
                                           offset=req.get("offset", 0),
                                           limit=req.get("limit", DEFAULT_LIMIT),
                                           )
    if desktop_service_management_set is None:
        logger.error("describe desktop service management failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, filter_conditions)
    if total_count is None:
        logger.error("get desktop service management count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, desktop_service_management_set, "desktop_service_management", **rep)

def handle_modify_desktop_service_management_attributes(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["services","service_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopServiceManagement.modify_desktop_service_management_attributes(req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_refresh_deskop_service_management(req):

    ctx = context.instance()
    sender = req["sender"]
    zone_depoly = ctx.zone_deploy
    if const.DEPLOY_TYPE_STANDARD == zone_depoly:
        ret = DesktopServiceManagement.refresh_deskop_service_management(req)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_describe_desktop_service_instances(req):

    ctx = context.instance()
    sender = req["sender"]

    if not check_global_admin_console(sender):
        rep = {'total_count': 0}
        return return_items(req, None, "instance", **rep)

    search_word = req.get("search_word", "")
    if not search_word:
        rep = {'total_count': 0}
        return return_items(req, None, "instance", **rep)

    valid_keys = ["search_word", "limit", "offset"]
    body = filter_out_none(req, valid_keys)
    instances = {}
    ret = DesktopServiceManagement.filter_system_instances(sender, body)
    if ret:
        instances = ret
    total_count = len(instances)

    rep = {'total_count': total_count}
    return return_items(req, instances, "instance", **rep)

def handle_load_desktop_service_instances(req):

    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["instances","service_type","service_management_type"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    instance_ids = req["instances"]
    service_type = req["service_type"]
    service_management_type = req["service_management_type"]

    ret = DesktopServiceManagement.check_service_type_valid(sender,service_management_type,service_type)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopServiceManagement.load_desktop_service_instances(sender,service_management_type,service_type,instance_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_service_instance_ids = ret

    ret = {'desktop_service_instance': desktop_service_instance_ids}
    return return_success(req, None, **ret)

def handle_remove_desktop_service_instances(req):

    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["instances"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    instance_ids = req["instances"]
    service_type = req["service_type"]

    ret = DesktopServiceManagement.remove_desktop_service_instances(service_type,instance_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = {'desktop_service_instance': instance_ids}
    return return_success(req, None, **ret)




