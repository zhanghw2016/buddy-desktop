from log.logger import logger
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
)
import constants as const
import db.constants as dbconst
from utils.json import json_dump,json_load
from common import is_global_admin_user, is_admin_user, is_console_admin_user, is_normal_console, is_admin_console
from resource_control.permission import check_user_resource_permission
import resource_control.desktop.resource_permission as ResCheck
import resource_control.guest.desktop_maintainer as DesktopMaintainer
import context
import api.user.user as APIUser
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    PUBLIC_COLUMNS
)

def handle_create_desktop_maintainer(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop_maintainer_name", "desktop_maintainer_type", "json_detail"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_maintainer_name = req.get("desktop_maintainer_name")
    ret = DesktopMaintainer.check_desktop_maintainer_name_valid(sender,desktop_maintainer_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    json_detail = req.get("json_detail")
    if not json_detail:
        logger.error("json_detail value [%s] is invalid" % json_detail)
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "json_detail"))

    ret = DesktopMaintainer.create_desktop_maintainer(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    rep = {"desktop_maintainer_id": ret}
    return return_success(req, None, **rep)

def handle_modify_desktop_maintainer_attributes(req):

    ret = ResCheck.check_request_param(req, ["desktop_maintainers"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_maintainer_id = req["desktop_maintainers"]

    ret = DesktopMaintainer.check_modify_desktop_maintainer_attributes(req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    need_maint_columns = ret

    need_maint_columns["description"] = req.get("description","")
    if need_maint_columns:
        ret = DesktopMaintainer.modify_desktop_maintainer_attributes(desktop_maintainer_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_delete_desktop_maintainers(req):

    ret = ResCheck.check_request_param(req, ["desktop_maintainers"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_maintainer_ids = req["desktop_maintainers"]

    ret = DesktopMaintainer.check_desktop_maintainer_transition_status(desktop_maintainer_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopMaintainer.check_desktop_maintainer_valid(desktop_maintainer_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopMaintainer.delete_desktop_maintainers(desktop_maintainer_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_describe_desktop_maintainers(req):

    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_DESKTOP_MAINTAINER)

    desktop_maintainer_ids = req.get("desktop_maintainers")
    if desktop_maintainer_ids:
        filter_conditions["desktop_maintainer_id"] = desktop_maintainer_ids

    filter_conditions["zone_id"] = sender["zone"]

    logger.info("filter_conditions == %s" % (filter_conditions))
    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_DESKTOP_MAINTAINER]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_DESKTOP_MAINTAINER]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_DESKTOP_MAINTAINER]

    desktop_maintainer_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_MAINTAINER, filter_conditions, display_columns,
                                                sort_key=get_sort_key(dbconst.TB_DESKTOP_MAINTAINER, req.get("sort_key")),
                                                reverse=get_reverse(req.get("reverse")),
                                                offset=req.get("offset", 0),
                                                limit=req.get("limit", DEFAULT_LIMIT),
                                                )

    logger.info("desktop_maintainer_set == %s" %(desktop_maintainer_set))
    if desktop_maintainer_set is None:
        logger.error("describe desktop maintainer failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))


    # format desktop_maintainer_set
    verbose = req.get("verbose",0)
    DesktopMaintainer.format_desktop_maintainer(sender, desktop_maintainer_set,verbose)

    # get total count
    total_count = len(desktop_maintainer_set)
    rep = {'total_count': total_count}
    return return_items(req, desktop_maintainer_set, "desktop_maintainer", **rep)

def handle_guest_check_desktop_maintainer(req):
    return

def handle_apply_desktop_maintainer(req):

    sender = req["sender"]
    ctx = context.instance()
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_maintainer"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_maintainer_id = req["desktop_maintainer"]

    ret = DesktopMaintainer.check_desktop_maintainer_valid(desktop_maintainer_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_maintainers = ret

    ret = DesktopMaintainer.check_desktop_maintainer_transition_status(desktop_maintainer_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopMaintainer.check_desktop_maintainer_resource(desktop_maintainer_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktops = ret

    # extra
    network_value = 0
    registry_value = []
    for desktop_maintainer_id,desktop_maintainer in desktop_maintainers.items():
        json_detail = desktop_maintainer.get("json_detail")
        logger.info("1 json_detail == %s" %(json_detail))
        json_detail = json_load(json_detail)
        logger.info("2 json_detail == %s" % (json_detail))
        for key,value in json_detail.items():
            if key == "network":
                if value == 1:
                    network_value = 1
                else:
                    network_value = 0

            if key == "registry":
                registry_value = value
    extra = {"desktops":desktops,"network_value":network_value,"registry_value":registry_value}
    logger.info("extra == %s" %(extra))

    # send desktop_maintainer job
    job_uuid = None
    if desktops:
        ret = DesktopMaintainer.send_desktop_maintainer_job(sender, desktop_maintainer_id,const.JOB_ACTION_APPLY_DESKTOP_MAINTAINER,extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_attach_resource_to_desktop_maintainer(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_maintainer", "resources"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_maintainer_id = req["desktop_maintainer"]
    resource_ids = req["resources"]

    ret = DesktopMaintainer.check_desktop_maintainer_valid(desktop_maintainer_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopMaintainer.check_desktop_maintainer_transition_status(desktop_maintainer_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopMaintainer.check_desktop_maintainer_resource_valid(sender, resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopMaintainer.attach_resource_to_desktop_maintainer(sender,desktop_maintainer_id, resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_detach_resource_from_desktop_maintainer(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_maintainer", "resources"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_maintainer_id = req["desktop_maintainer"]
    resource_ids = req["resources"]

    ret = DesktopMaintainer.check_desktop_maintainer_valid(desktop_maintainer_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopMaintainer.check_desktop_maintainer_transition_status(desktop_maintainer_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopMaintainer.check_desktop_maintainer_resource_valid(sender, resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopMaintainer.detach_resource_from_desktop_maintainer(sender,desktop_maintainer_id, resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_run_guest_shell_command(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["command", "resource_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    command = req["command"]
    resource_id = req["resource_id"]

    ret = DesktopMaintainer.register_guest_shell_command(sender,req)
    logger.info("register_guest_shell_command ret == %s" %(ret))
    if isinstance(ret, Error):
        return return_error(req, ret)
    guest_shell_command_id = ret

    ret = DesktopMaintainer.register_guest_shell_command_resource(sender,guest_shell_command_id,resource_id)
    logger.info("register_guest_shell_command_resource ret == %s" %(ret))
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopMaintainer.register_guest_shell_command_run_history(sender,guest_shell_command_id,resource_id)
    logger.info("register_guest_shell_command_run_history ret == %s" %(ret))
    if isinstance(ret, Error):
        return return_error(req, ret)

    # extra
    extra = {"desktops":resource_id,"command":command}
    logger.info("extra == %s" %(extra))

    # send_guest_shell_command_job
    job_uuid = None
    ret = DesktopMaintainer.send_guest_shell_command_job(sender, guest_shell_command_id,const.JOB_ACTION_RUN_GUEST_SHELL_COMMAND,extra)
    if isinstance(ret, Error):
        return return_error(req, ret)
    job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_describe_guest_shell_commands(req):
    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_GUEST_SHELL_COMMAND)

    guest_shell_command_ids = req.get("guest_shell_commands")
    if guest_shell_command_ids:
        filter_conditions["guest_shell_command_id"] = guest_shell_command_ids

    logger.info("filter_conditions == %s" % (filter_conditions))
    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_GUEST_SHELL_COMMAND]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_GUEST_SHELL_COMMAND]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_GUEST_SHELL_COMMAND]

    guest_shell_command_set = ctx.pg.get_by_filter(dbconst.TB_GUEST_SHELL_COMMAND, filter_conditions, display_columns,
                                                  sort_key=get_sort_key(dbconst.TB_GUEST_SHELL_COMMAND,
                                                                        req.get("sort_key")),
                                                  reverse=get_reverse(req.get("reverse")),
                                                  offset=req.get("offset", 0),
                                                  limit=req.get("limit", DEFAULT_LIMIT),
                                                  )

    if guest_shell_command_set is None:
        logger.error("describe guest_shell_command failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format guest_shell_command_set
    verbose = req.get("verbose",0)
    DesktopMaintainer.format_guest_shell_command(sender, guest_shell_command_set,verbose)

    # get total count
    total_count = len(guest_shell_command_set)
    rep = {'total_count': total_count}
    return return_items(req, guest_shell_command_set, "guest_shell_command", **rep)

def handle_guest_check_shell_command(req):
    return

