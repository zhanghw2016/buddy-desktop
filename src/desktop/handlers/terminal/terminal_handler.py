import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
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
from utils.misc import get_columns
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.terminal.terminal as Terminal
import api.user.user as APIUser
import constants as const

def handle_describe_terminal_managements(req):

    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_TERMINAL_MANAGEMENT)
    terminal_ids = req.get("terminals")
    if terminal_ids:
        filter_conditions["terminal_id"] = terminal_ids

    terminal_group_id = req.get("terminal_group")
    if terminal_group_id:
        filter_conditions["terminal_group_id"] = terminal_group_id

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_TERMINAL_MANAGEMENT]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_TERMINAL_MANAGEMENT]
    else:
        display_columns = []

    terminal_management_set = ctx.pg.get_by_filter(dbconst.TB_TERMINAL_MANAGEMENT, filter_conditions, display_columns,
                                      sort_key = get_sort_key(dbconst.TB_TERMINAL_GROUP, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if terminal_management_set is None:
        logger.error("describe terminal management info failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format terminal_management
    Terminal.format_terminal_management(sender, terminal_management_set, req.get("filter_joined_terminal_group", 0))

    # get terminal_management terminal_management_online_count
    ret = ctx.pgm.get_terminals(terminal_group_id=terminal_group_id,status=const.TERMINAL_STATUS_ACTIVE)
    if ret is None:
        terminal_management_online_count = 0
    else:
        terminal_management_online_count = len(ret)

    # get terminal_management terminal_management_offline_count
    ret = ctx.pgm.get_terminals(terminal_group_id=terminal_group_id,status=const.TERMINAL_STATUS_INACTIVE)
    if ret is None:
        terminal_management_offline_count = 0
    else:
        terminal_management_offline_count = len(ret)

    # get total count
    # total_count = ctx.pg.get_count(dbconst.TB_TERMINAL_MANAGEMENT, filter_conditions)
    total_count =len(terminal_management_set)
    if total_count is None:
        logger.error("get terminal management info count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count,"terminal_management_online_count":terminal_management_online_count,"terminal_management_offline_count":terminal_management_offline_count}
    return return_items(req, terminal_management_set, "terminal_management", **rep)

def handle_modify_terminal_management_attributes(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["terminals"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    terminal_id = req["terminals"]
    terminal_server_ip = req.get("terminal_server_ip","")

    need_maint_columns = get_columns(req, ["terminal_server_ip"])
    if need_maint_columns:

        ret = Terminal.check_terminal_vaild(terminal_id, status=const.TERMINAL_STATUS_ACTIVE)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = Terminal.modify_terminal_management_attributes(terminal_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

        extra = {"terminal_server_ip": terminal_server_ip}
        # send terminal job
        job_uuid = None
        if terminal_id:
            ret = Terminal.send_desktop_terminal_job(sender, terminal_id,const.JOB_ACTION_MODIFY_TERMINAL_MANAGEMENT_ATTRIBUTTES, extra)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret
        return return_success(req, None, job_uuid)

    return return_success(req, None)

def handle_delete_terminal_managements(req):

    ret = ResCheck.check_request_param(req, ["terminals"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    terminal_ids = req["terminals"]

    ret = Terminal.check_terminal_vaild(terminal_ids, status=const.TERMINAL_STATUS_INACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    terminals = ret

    ret = Terminal.check_terminal_group_valid(terminal_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    terminal_group_ids = ret

    if terminal_group_ids:
        for terminal_group_id in terminal_group_ids:
            ret = Terminal.delete_terminal_from_terminal_group(terminal_group_id, terminal_ids)
            if isinstance(ret, Error):
                return return_error(req, ret)

    ret = Terminal.delete_terminal_managements(terminals)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_restart_terminals(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["terminals"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    terminal_ids = req["terminals"]

    ret = Terminal.check_terminal_vaild(terminal_ids, status=const.TERMINAL_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # # send terminal job
    job_uuid = None
    if terminal_ids:
        ret = Terminal.send_desktop_terminal_job(sender, terminal_ids,const.JOB_ACTION_RESTART_TREMINALS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret
    return return_success(req, None, job_uuid)

def handle_stop_terminals(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["terminals"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    terminal_ids = req["terminals"]

    ret = Terminal.check_terminal_vaild(terminal_ids, status=const.TERMINAL_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # # send terminal job
    job_uuid = None
    if terminal_ids:
        ret = Terminal.send_desktop_terminal_job(sender, terminal_ids,const.JOB_ACTION_STOP_TREMINALS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret
    return return_success(req, None, job_uuid)

def handle_describe_terminal_groups(req):

    ctx = context.instance()
    sender = req["sender"]
    filter_conditions = build_filter_conditions(req, dbconst.TB_TERMINAL_GROUP)

    terminal_group_ids = req.get("terminal_groups")
    if terminal_group_ids:
        filter_conditions["terminal_group_id"] = terminal_group_ids

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_TERMINAL_GROUP]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_TERMINAL_GROUP]
    else:
        display_columns = []

    terminal_group_set = ctx.pg.get_by_filter(dbconst.TB_TERMINAL_GROUP, filter_conditions, display_columns,
                                      sort_key = get_sort_key(dbconst.TB_TERMINAL_GROUP, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )

    if terminal_group_set is None:
        logger.error("describe terminal group info failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format terminal group
    Terminal.format_terminal_groups(sender, terminal_group_set, req.get("verbose", 0))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_TERMINAL_GROUP, filter_conditions)
    if total_count is None:
        logger.error("get terminal group info count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count}
    return return_items(req, terminal_group_set, "terminal_group", **rep)


def handle_create_terminal_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["terminal_group_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    terminal_group_name = req["terminal_group_name"]
    description = req.get("description")

    # check terminal_group_name if existed
    ret = Terminal.check_terminal_group_name(terminal_group_name)
    if isinstance(ret, Error):
        return return_error(req, ret)
    terminal_group_name = ret

    ret = Terminal.register_terminal_group(sender, terminal_group_name, description)
    if isinstance(ret, Error):
        return return_error(req, ret)
    terminal_group_id = ret

    ret = {'terminal_group': terminal_group_id}
    return return_success(req, None, **ret)

def handle_modify_terminal_group_attributes(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["terminal_groups"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    terminal_group_id = req["terminal_groups"]
    terminal_group_name = req.get("terminal_group_name")
    description = req.get("description")

    ret = Terminal.check_terminal_group(sender, terminal_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Terminal.modify_terminal_group(terminal_group_id, terminal_group_name, description)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_delete_terminal_groups(req):

    # check request param
    ret = ResCheck.check_request_param(req, ["terminal_groups"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    terminal_group_id = req["terminal_groups"]

    ret = Terminal.delete_terminal_groups(terminal_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_add_terminal_to_terminal_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["terminal_groups", "terminals"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    terminal_group_id = req["terminal_groups"]
    terminal_ids = req["terminals"]

    ret = Terminal.check_terminal_valid(sender, terminal_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Terminal.check_terminal_group(sender, terminal_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Terminal.add_terminal_to_terminal_group(terminal_group_id, terminal_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_delete_terminal_from_terminal_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["terminal_groups", "terminals"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    terminal_group_id = req["terminal_groups"]
    terminal_ids = req["terminals"]

    ret = Terminal.check_terminal_valid(sender, terminal_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Terminal.check_terminal_group(sender, terminal_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Terminal.delete_terminal_from_terminal_group(terminal_group_id, terminal_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_describe_master_backup_ips(req):

    sender = req["sender"]
    ret = Terminal.describe_master_backup_ips(sender)
    if isinstance(ret, Error):
        return return_error(req, ret)
    (master_vdi_ip, backup_vdi_ip, backup_vdi2_ip, backup_vdi3_ip, backup_vdi4_ip, backup_vdi5_ip, backup_vdi6_ip,backup_vdi7_ip)= ret

    ret = {
            'master_vdi_ip': master_vdi_ip,
            'backup_vdi_ip':backup_vdi_ip,
            'backup_vdi2_ip': backup_vdi2_ip,
            'backup_vdi3_ip': backup_vdi3_ip,
            'backup_vdi4_ip': backup_vdi4_ip,
            'backup_vdi5_ip': backup_vdi5_ip,
            'backup_vdi6_ip': backup_vdi6_ip,
            'backup_vdi7_ip': backup_vdi7_ip,
    }
    logger.info("handle_describe_master_backup_ips ret == %s " %(ret))
    return return_success(req, None, **ret)

def handle_describe_cbserver_hosts(req):

    sender = req["sender"]

    ret = Terminal.describe_cbserver_hosts(sender)
    if isinstance(ret, Error):
        return return_error(req, ret)
    (cb0server_host,cb1server_host)= ret

    ret = {'cb0server_host': cb0server_host,'cb1server_host':cb1server_host}
    return return_success(req, None, **ret)


