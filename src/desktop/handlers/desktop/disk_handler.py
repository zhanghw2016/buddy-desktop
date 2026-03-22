
import context
from db.constants  import (
    TB_DESKTOP_DISK,
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
)
from common import (
    build_filter_conditions,
    is_global_admin_user,
    is_console_admin_user,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
    is_normal_console
)
import constants as const
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.desktop.resource_permission as ResCheck
import resource_control.desktop.desktop as Desktop
import resource_control.desktop.disk as Disk

from utils.misc import get_columns

def handle_describe_desktop_disks(req):

    ctx = context.instance()
    sender = req["sender"]

    # get desktop group set
    filter_conditions = build_filter_conditions(req, TB_DESKTOP_DISK)
   
    disk_config_id = req.get("disk_config")
    if disk_config_id:
        filter_conditions.update({'disk_config_id': disk_config_id})
    
    desktop_group_id = req.get("desktop_group")
    desktop_id = req.get("desktop")
    if desktop_group_id:
        filter_conditions["desktop_group_id"] = desktop_group_id
    if desktop_id:
        filter_conditions["desktop_id"] = desktop_id
    
    disk_ids = req.get("disks")
    if disk_ids:
        filter_conditions["disk_id"] = disk_ids

    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_DISK]
    elif is_console_admin_user(sender) and not is_normal_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_DISK]
    else:
        display_columns = {}

    disk_set = ctx.pg.get_by_filter(TB_DESKTOP_DISK, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_DESKTOP_DISK, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )

    if disk_set is None:
        logger.error("describe desktop volume failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    Disk.format_desktop_disks(sender, disk_set)
    
    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_DISK, filter_conditions)
    if total_count is None:
        logger.error("get desktop volume count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, disk_set, "disk", **rep)

def handle_create_desktop_disks(req):

    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktops", "size", "disk_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    size = req["size"]
    disk_name = req["disk_name"]
    desktop_ids = req["desktops"]

    # check
    ret = Desktop.check_desktop_vaild(desktop_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktops = ret
    new_disks = []
    
    job_disks = []

    ret = Disk.check_desktop_disk_count(desktop_ids=desktop_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)    

    for desktop_id, desktop in desktops.items():
        instance_class = desktop["instance_class"]

        ret = ctx.pgm.get_instance_class_disk_type(zone_deploy=ctx.zone_deploy, instance_class=instance_class)
        if not ret:
            logger.error("instance_class %s no found corresponding disk_type" % instance_class)
            return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND,
                                           ErrorMsg.ERR_MSG_INSTANCE_CLASS_NO_FOUND_CORRESPONDING_DISK_TYPE, instance_class))
        instance_class_disk_types = ret

        disk_type = 0
        for _, instance_class_disk_type in instance_class_disk_types.items():
            disk_type = instance_class_disk_type.get("disk_type")

        disk_config = {
                         "size": size,
                         "disk_name": disk_name,
                         "disk_type": disk_type,
                         "description": req.get("description", '')
                         }

        ret = Disk.create_disks(disk_config, desktop_id)
        if isinstance(ret, Error):
            return return_error(req, ret)

        disk_id = ret[0]
        new_disks.append(disk_id)
        # if desktop has instance, send job to create
        instance_id = desktop["instance_id"]
        if instance_id and disk_id:
            job_disks.append(disk_id)

    # submit desktop job
    job_uuid = None
    if job_disks:
        ret = Disk.send_disk_job(sender, job_disks, const.JOB_ACTION_ATTACH_DISKS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    ret = {'disks': new_disks}
    return return_success(req, None, job_uuid, **ret)

def handle_delete_desktop_disks(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["disks"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    disk_ids = req["disks"]

    ret = Disk.check_desktop_disk_avail(disk_ids, [const.DISK_STATUS_ALLOC, const.DISK_STATUS_AVAIL, const.DISK_STATUS_DELETED])
    if isinstance(ret, Error):
        return return_error(req, ret)
    disks = ret
    
    ret = Disk.delete_disks(disks)
    if isinstance(ret, Error):
        return return_error(req, ret)

    job_disk = ret
    job_uuid = None
    # submit desktop job
    if job_disk:
        ret = Disk.send_disk_job(sender, job_disk, const.JOB_ACTION_DELETE_DISKS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_attach_disk_to_desktop(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["disks"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    disk_ids = req["disks"]
    desktop_id = req["desktop"]

    ret = Disk.check_desktop_disk_avail(disk_ids, const.DISK_STATUS_AVAIL)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = Disk.check_desktop_disk_count(desktop_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # check desktop vaild
    ret = Desktop.check_desktop_vaild(desktop_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop = ret[desktop_id]

    ret = Disk.attach_disk_to_dekstop(desktop, disk_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    job_uuid = None
    job_disk = ret
    # submit desktop job
    if job_disk:
        ret = Disk.send_disk_job(sender, job_disk, const.JOB_ACTION_ATTACH_DISKS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_detach_disk_from_desktop(req):
    
    sender = req["sender"]
    ctx = context.instance()
    ret = ResCheck.check_request_param(req, ["disks"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    disk_ids = req["disks"]

    ret = Disk.check_desktop_disk_avail(disk_ids, [const.DISK_STATUS_ALLOC, const.DISK_STATUS_INUSE])
    if isinstance(ret, Error):
        return return_error(req, ret)
   
    desktop_disk = ctx.pgm.get_disk_desktops(disk_ids)
    if not desktop_disk:
        logger.error("disk %s no attach in desktop" % disk_ids)
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_DISK_NO_ATTACH_IN_DESKTOP, disk_ids))
    desktop_ids = desktop_disk.keys()

    # check desktop vaild
    ret = Desktop.check_desktop_vaild(desktop_ids, status=const.INST_STATUS_STOP)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktops = ret
    
    job_disk = []
    for desktop_id, disks in desktop_disk.items():
        desktop = desktops[desktop_id]

        ret = Disk.detach_disk_from_desktop(desktop, disks)
        if isinstance(ret, Error):
            return return_error(req, ret)

        if ret:
            job_disk.extend(ret)
    
    job_uuid = None
    # submit desktop job
    if job_disk:
        ret = Disk.send_disk_job(sender, job_disk, const.JOB_ACTION_DETACH_DISKS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_resize_desktop_disks(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["disks"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    disk_ids = req["disks"]
    size = req["size"]

    ret = Disk.check_desktop_disk_avail(disk_ids, const.DISK_STATUS_AVAIL)
    if isinstance(ret, Error):
        return return_error(req, ret)
    disks = ret
    
    ret = Disk.resize_disks(disks, size)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    job_disk = ret
    job_uuid = None
    # submit desktop job
    if job_disk:
        ret = Disk.send_disk_job(sender, job_disk, const.JOB_ACTION_RESIZE_DISKS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_modify_desktop_disk_attributes(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["disk"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    disk_id = req["disk"]
    
    ret = Disk.check_desktop_disk_avail(disk_id, None, False)
    if isinstance(ret, Error):
        return return_error(req, ret)
    disk = ret[disk_id]
    
    columns = get_columns(req, ["disk_name", "description"])
    if columns:
        ret = Disk.modify_disk_attributes(sender, disk, columns)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    return return_success(req, None)
