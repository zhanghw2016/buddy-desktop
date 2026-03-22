from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
from utils.id_tool import (
    get_uuid,
    UUID_TYPE_DESKTOP_MAINTAINER,
    UUID_TYPE_DESKTOP,
    UUID_TYPE_DESKTOP_DISK,
    UUID_TYPE_VDHOST_REQUEST,
    UUID_TYPE_GUEST_SHELL_COMMAND,
    UUID_TYPE_GUEST_SHELL_COMMAND_RUN_HISTORY,
    )
from utils.misc import get_current_time
from utils.json import json_dump,json_load
from common import check_resource_transition_status
import resource_control.desktop.job as Job
from utils.net import is_port_open
import time
import requests

# def format_desktop_maintainer(sender, desktop_maintainer_set,verbose):
#     logger.info("format_desktop_maintainer desktop_maintainer_set == %s" %(desktop_maintainer_set))
#     ctx = context.instance()
#     if verbose:
#         for desktop_maintainer_id,desktop_maintainer in desktop_maintainer_set.items():
#             ret = ctx.pgm.get_desktop_maintainer_resources(desktop_maintainer_id=desktop_maintainer_id)
#             if not ret:
#                 continue
#             desktop_maintainer_resources = ret
#             resource_ids = desktop_maintainer_resources.keys()
#             logger.info("resource_ids == %s" %(resource_ids))
#             desktop_maintainer ["resource_ids"] = resource_ids
#
#     return None

def format_desktop_maintainer(sender, desktop_maintainer_set,verbose):

    ctx = context.instance()
    for desktop_maintainer_id, _ in desktop_maintainer_set.items():
        if verbose:
            ret = ctx.pgm.get_desktop_maintainer_resource_detail(desktop_maintainer_id)
            if ret:
                desktop_maintainer_set[desktop_maintainer_id] = ret

        # get desktop_maintainer resource_count
        ret = ctx.pgm.get_desktop_maintainer_resources(desktop_maintainer_id=desktop_maintainer_id)
        if ret is None:
            resource_count = 0
        else:
            resource_count = len(ret)
        desktop_maintainer_set[desktop_maintainer_id]["resource_count"] = resource_count

    return desktop_maintainer_set

def format_guest_shell_command(sender, guest_shell_command_set,verbose):

    ctx = context.instance()
    if verbose:
        for guest_shell_command_id,guest_shell_command in guest_shell_command_set.items():
            ret = ctx.pgm.get_guest_shell_command_resources(guest_shell_command_id=guest_shell_command_id)
            if not ret:
                continue
            guest_shell_command_resources = ret
            resource_ids = guest_shell_command_resources.keys()
            logger.info("resource_ids == %s" %(resource_ids))
            resource_names = get_desktop_maintaine_resource_name(resource_ids)
            guest_shell_command ["resource_names"] = resource_names.get(resource_ids[0], '')

    return None

def check_desktop_maintainer_name_valid(sender,desktop_maintainer_name):

    ctx = context.instance()
    zone_id = sender["zone"]
    ret = ctx.pgm.get_desktop_maintainers(zone_id=zone_id,desktop_maintainer_name=desktop_maintainer_name)
    if isinstance(ret, Error):
        return ret
    if ret:
        logger.error("desktop_maintainer_name [%s] is existed" % desktop_maintainer_name)
        return Error(ErrorCodes.DESKTOP_MAINTAINER_ERROR,
                     ErrorMsg.ERROR_MSG_DESKTOP_MAINTAINER_NAME_EXISTED_ERROR,desktop_maintainer_name)

    return None

def build_desktop_maintainer(req):

    modify_keys = ["desktop_maintainer_name", "desktop_maintainer_type","description","json_detail"]
    dump_keys = ['desktop_maintainer_type']

    desktop_maintainer = {}
    for modify_key in modify_keys:
        if modify_key not in req:
            continue

        value = req[modify_key]
        if modify_key in dump_keys:
            value = json_dump(value)

        desktop_maintainer[modify_key] = value

    return desktop_maintainer

def create_desktop_maintainer(sender, req):

    ctx = context.instance()
    desktop_maintainer_id = get_uuid(UUID_TYPE_DESKTOP_MAINTAINER, ctx.checker)
    desktop_maintainer_info = build_desktop_maintainer(req)
    zone_id = sender["zone"]
    update_info = dict(
        desktop_maintainer_id=desktop_maintainer_id,
        zone_id=zone_id,
        is_apply=0,
        create_time=get_current_time()
    )
    update_info.update(desktop_maintainer_info)
    logger.info("create_desktop_maintainer update_info == %s" %(update_info))
    # register desktop_maintainer
    if not ctx.pg.insert(dbconst.TB_DESKTOP_MAINTAINER, update_info):
        logger.error("insert newly created desktop maintainer for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return desktop_maintainer_id

def check_modify_desktop_maintainer_attributes(req):

    ctx = context.instance()
    desktop_maintainer_id = req.get("desktop_maintainers")
    desktop_maintainer = ctx.pgm.get_desktop_maintainers(desktop_maintainer_ids=desktop_maintainer_id)
    if not desktop_maintainer:
        logger.error("modify desktop maintainer [%s] no found" % desktop_maintainer_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_maintainer_id)

    modify_keys = ["desktop_maintainer_name", "desktop_maintainer_type","description","json_detail"]
    dump_keys = ['desktop_maintainer_type']

    need_maint_columns = {}
    for modify_key in modify_keys:
        if modify_key not in req:
            continue

        value = req[modify_key]
        if modify_key in dump_keys:
            value = json_dump(value)

        need_maint_columns[modify_key] = value

    return need_maint_columns

def modify_desktop_maintainer_attributes(desktop_maintainer_id, need_maint_columns):
    logger.info("modify_desktop_maintainer_attributes desktop_maintainer_id == %s need_maint_columns == %s" %(desktop_maintainer_id,need_maint_columns))
    ctx = context.instance()
    if need_maint_columns:
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_MAINTAINER, {desktop_maintainer_id: need_maint_columns}):
            logger.error("modify desktop maintainer update DB fail %s" % need_maint_columns)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def check_desktop_maintainer_transition_status(desktop_maintainer_ids):

    ctx = context.instance()
    desktop_maintainers = ctx.pgm.get_desktop_maintainers(desktop_maintainer_ids=desktop_maintainer_ids)
    if not desktop_maintainers:
        return None

    # check desktop_maintainer transition status
    ret = check_resource_transition_status(desktop_maintainers)
    if isinstance(ret, Error):
        return ret

    return None

def delete_desktop_maintainers(desktop_maintainer_ids):

    ctx = context.instance()
    if desktop_maintainer_ids and not isinstance(desktop_maintainer_ids, list):
        desktop_maintainer_ids = [desktop_maintainer_ids]

    for desktop_maintainer_id in desktop_maintainer_ids:
        conditions = {"desktop_maintainer_id": desktop_maintainer_id}
        ctx.pg.base_delete(dbconst.TB_DESKTOP_MAINTAINER, conditions)
        ctx.pg.base_delete(dbconst.TB_DESKTOP_MAINTAINER_RESOURCE, conditions)

    return None

def check_desktop_maintainer_resource_valid(sender, resource_ids=None):

    ctx = context.instance()
    for resource_id in resource_ids:
        desktop_ids = resource_id
        if desktop_ids:
            desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids)
            if not desktops:
                logger.error("desktop_resource %s no instance" % desktop_ids)
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_DESKTOP_MAINTAINER_NO_DESKTOP_INSTANCE, desktop_ids)
    return None

def check_desktop_maintainer_valid(desktop_maintainer_ids=None):

    ctx = context.instance()
    if desktop_maintainer_ids and not isinstance(desktop_maintainer_ids, list):
        desktop_maintainer_ids = [desktop_maintainer_ids]

    desktop_maintainers = {}
    for desktop_maintainer_id in desktop_maintainer_ids:
        desktop_maintainers = ctx.pgm.get_desktop_maintainers(desktop_maintainer_ids=desktop_maintainer_id)
        if not desktop_maintainers:
            logger.error("desktop_maintainers %s no found" % (desktop_maintainer_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERROR_MSG_DESKTOP_MAINTAINER_NO_FOUND_ERROR, desktop_maintainer_id)
    return desktop_maintainers

def get_desktop_maintaine_resource_name(resource_ids):
    ctx = context.instance()
    resource_name = {}
    desktop_ids = []
    disk_ids = []

    for resource_id in resource_ids:
        prefix = resource_id.split("-")[0]
        if prefix in [UUID_TYPE_DESKTOP]:
            desktop_ids.append(resource_id)
        elif prefix in [UUID_TYPE_DESKTOP_DISK]:
            disk_ids.append(resource_id)
        else:
            continue

    if desktop_ids:
        desktops = ctx.pgm.get_desktops(desktop_ids)
        if desktops:
            for desktop_id, desktop in desktops.items():
                hostname = desktop["hostname"]
                resource_name[desktop_id] = hostname

    if disk_ids:
        disks = ctx.pgm.get_disks(disk_ids)
        if disks:
            for disk_id, disk in disks.items():
                disk_name = disk["disk_name"]
                resource_name[disk_id] = disk_name

    return resource_name

def attach_resource_to_desktop_maintainer(sender,desktop_maintainer_id, resource_ids):

    ctx = context.instance()
    existed_resource_ids = []
    ret = ctx.pgm.get_desktop_maintainer_resources(desktop_maintainer_id=desktop_maintainer_id, resource_ids=resource_ids)
    if ret:
        desktop_maintainer_resources = ret
        for resource_id,_ in desktop_maintainer_resources.items():
            existed_resource_ids.append(resource_id)
        logger.error("attach resource to desktop maintainer %s, resource %s existed" % (desktop_maintainer_id, existed_resource_ids))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_ALREAY_EXISTED_DESKTOP_MAINTAINER, (existed_resource_ids, desktop_maintainer_id))

    resource_names = get_desktop_maintaine_resource_name(resource_ids)
    new_desktop_maintainer_resource_info = {}
    for resource_id in resource_ids:
        desktop_maintainer_resource_info = dict(
                         desktop_maintainer_id=desktop_maintainer_id,
                         resource_id = resource_id,
                         resource_type=const.DESKTOP_MAINTAINER_RESOURCE_TYPE_DESKTOP,
                         resource_name = resource_names.get(resource_id, ''),
                         zone_id=sender["zone"],
                         create_time=get_current_time()
                         )
        new_desktop_maintainer_resource_info[resource_id] = desktop_maintainer_resource_info
    logger.info("new_desktop_maintainer_resource_info == %s" %(new_desktop_maintainer_resource_info))
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_MAINTAINER_RESOURCE, new_desktop_maintainer_resource_info):
        logger.error("insert newly created desktop maintainer resource [%s] to db failed" % (new_desktop_maintainer_resource_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_DESKTOP_MAINTAINER_RESOURCE_FAILED)

    return None

def detach_resource_from_desktop_maintainer(sender,desktop_maintainer_id, resource_ids):

    ctx = context.instance()
    ret = ctx.pgm.get_desktop_maintainer_resources(desktop_maintainer_id=desktop_maintainer_id,resource_ids=resource_ids)
    if not ret:
        logger.error("detach resource from desktop maintainer %s, resource %s not exist" % (desktop_maintainer_id, resource_ids))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_IN_DESKTOP_MAINTAINER, (resource_ids, desktop_maintainer_id))

    delete_desktop_maintainer_resource_info = {}
    for resource_id in resource_ids:
        delete_desktop_maintainer_resource_info = dict(
                                desktop_maintainer_id=desktop_maintainer_id,
                                resource_id=resource_id
                                )
        logger.info("delete_desktop_maintainer_resource_info == %s" % (delete_desktop_maintainer_resource_info))
        if not ctx.pg.base_delete(dbconst.TB_DESKTOP_MAINTAINER_RESOURCE, delete_desktop_maintainer_resource_info):
            logger.error("delete desktop maintainer resource [%s] to db failed" % (delete_desktop_maintainer_resource_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_DESKTOP_MAINTAINER_RESOURCE_FAILED,delete_desktop_maintainer_resource_info)

    return None

def send_desktop_maintainer_job(sender, desktop_maintainer_ids, action, extra=None):

    if not isinstance(desktop_maintainer_ids, list):
        desktop_maintainer_ids = [desktop_maintainer_ids]

    directive = {
        "sender": sender,
        "action": action,
        "desktop_maintainer_id": desktop_maintainer_ids,
    }
    if extra:
        directive.update(extra)

    ret= Job.submit_desktop_job(action, directive, desktop_maintainer_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def check_desktop_maintainer_resource(desktop_maintainer_id):

    ctx = context.instance()
    ret = ctx.pgm.get_desktop_maintainer_resources(desktop_maintainer_id=desktop_maintainer_id)
    if not ret:
        return None
    desktop_maintainer_resources = ret
    valid_desktop_ids = []
    for resource_id,desktop_maintainer_resource in desktop_maintainer_resources.items():
        desktop_ids = resource_id
        if desktop_ids:
            desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids)
            if not desktops:
                logger.error("desktop_resource %s no instance" % desktop_ids)
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_DESKTOP_MAINTAINER_NO_DESKTOP_INSTANCE, desktop_ids)
            for _,desktop in desktops.items():
                status = desktop["status"]
                if const.INST_STATUS_RUN == status:
                    if resource_id not in valid_desktop_ids:
                        valid_desktop_ids.append(resource_id)

    return valid_desktop_ids

def _check_private_ips(desktop_ips):
    active_ips = []
    for desktop_ip in desktop_ips:
        ret = is_port_open(desktop_ip, const.VDHOST_SERVER_DEFAULT_PORT)
        if ret:
            active_ips.append(desktop_ip)
    if len(active_ips) == 0:
        return None
    return active_ips

def run_shell_command(req):
    logger.info("run_shell_command req == %s" %(req))
    ctx = context.instance()
    desktop_ips = req.get("desktop_ips")
    if not desktop_ips:
        logger.error("desktop_ips is null.")
        return -1

    active_ips = _check_private_ips(desktop_ips)
    if active_ips is None:
        logger.error("active_ips size is 0.")
        return -1;

    desktop_id = req.get("desktop_id")
    hostnames = ctx.pgm.get_desktop_name(desktop_ids=[desktop_id])
    if not hostnames:
        logger.error("hostname is null.")
        return -1;
    hostname = hostnames[desktop_id]

    server_ip = active_ips[0]
    request_url = "http://%s:%s/api" % (server_ip, const.VDHOST_SERVER_DEFAULT_PORT)
    request = {
        "action": req.get("action"),
        "hostname": hostname
        }
    request_id = get_uuid(UUID_TYPE_VDHOST_REQUEST,
                          None,
                          long_format=True)
    request.update({"request_id": request_id})
    request.update(req["params"])

    logger.info("run_shell_command request: [ %s ]" % request)
    end_time = time.time() + const.REQUEST_VDHOST_SERVER_RUN_GUEST_SHELL_COMMAND_TIMEOUT
    while time.time() < end_time:
        try:
            rep = requests.post(request_url, data=json_dump(request))
            logger.info("post rep status: [ %d ], text:[ %s ]" % (rep.status_code, rep.text))
            if rep.status_code == 200:
                response = json_load(rep.text)
                if response:
                    ret_code = response["ret_code"]
                    if ret_code == 0:
                        return rep.text
            time.sleep(10)
        except Exception,e:
            logger.error("request vdhost server with exception: %s" % e)
            return -1
    return -1

def build_guest_shell_command(req):

    modify_keys = ["command"]
    dump_keys = ['']

    guest_shell_command = {}
    for modify_key in modify_keys:
        if modify_key not in req:
            continue

        value = req[modify_key]
        if modify_key in dump_keys:
            value = json_dump(value)

        guest_shell_command[modify_key] = value

    return guest_shell_command

def register_guest_shell_command(sender, req):

    ctx = context.instance()
    guest_shell_command_id = get_uuid(UUID_TYPE_GUEST_SHELL_COMMAND, ctx.checker)
    guest_shell_command_info = build_guest_shell_command(req)
    update_info = dict(
        guest_shell_command_id=guest_shell_command_id,
        guest_shell_command_name=const.GUEST_SHELL_COMMAND_NAME_OTHER_CUSTOM_CMD,
        guest_shell_command_type=const.GUEST_SHELL_COMMAND_TYPE_CUSTOM_CMD,
        status=const.GUEST_SHELL_COMMAND_STATUS_ACTIVE,
        create_time=get_current_time()
    )
    update_info.update(guest_shell_command_info)
    logger.info("register_guest_shell_command update_info == %s" %(update_info))
    # register guest_shell_command
    if not ctx.pg.insert(dbconst.TB_GUEST_SHELL_COMMAND, update_info):
        logger.error("insert newly register guest_shell_command for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return guest_shell_command_id

def register_guest_shell_command_resource(sender,guest_shell_command_id,resource_id):

    ctx = context.instance()
    update_info = dict(
        guest_shell_command_id=guest_shell_command_id,
        resource_id=resource_id,
        resource_type=const.GUEST_SHELL_COMMAND_RESOURCE_TYPE_DESKTOP,
        zone_id=sender["zone"],
        create_time=get_current_time()
    )
    logger.info("register_guest_shell_command_resource update_info == %s" %(update_info))
    # register guest_shell_command_resource
    if not ctx.pg.insert(dbconst.TB_GUEST_SHELL_COMMAND_RESOURCE, update_info):
        logger.error("insert newly register guest_shell_command_resource for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return guest_shell_command_id

def register_guest_shell_command_run_history(sender,guest_shell_command_id,resource_id):

    ctx = context.instance()
    guest_shell_command_run_history_id = get_uuid(UUID_TYPE_GUEST_SHELL_COMMAND_RUN_HISTORY, ctx.checker)
    update_info = dict(
        guest_shell_command_run_history_id=guest_shell_command_run_history_id,
        guest_shell_command_id=guest_shell_command_id,
        resource_id=resource_id,
        create_time=get_current_time(),
        update_time=get_current_time(),
    )

    logger.info("register_guest_shell_command_run_history update_info == %s" %(update_info))
    # register guest_shell_command_run_history
    if not ctx.pg.insert(dbconst.TB_GUEST_SHELL_COMMAND_RUN_HISTORY, update_info):
        logger.error("insert newly register guest_shell_command_run_history for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return guest_shell_command_run_history_id

def send_guest_shell_command_job(sender, guest_shell_command_ids, action, extra=None):

    if not isinstance(guest_shell_command_ids, list):
        guest_shell_command_ids = [guest_shell_command_ids]

    directive = {
        "sender": sender,
        "action": action,
        "guest_shell_command_id": guest_shell_command_ids,
    }
    if extra:
        directive.update(extra)

    ret = Job.submit_desktop_job(action, directive, guest_shell_command_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid


