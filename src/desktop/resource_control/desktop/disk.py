import constants as const
from log.logger import logger
from utils.misc import get_current_time
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.id_tool import(
    UUID_TYPE_DESKTOP_DISK,
    get_uuid
)
from db.constants import (
    TB_DESKTOP_DISK,
    TB_DESKTOP
)
import resource_control.desktop.job as Job
from constants import (
    REQ_TYPE_DESKTOP_JOB,
)
from common import (
    generate_disk_name,
    check_resource_transition_status
)
import api.user.resource_user as ResUser

# disk common
def send_disk_job(sender, disk_ids, action):

    if not isinstance(disk_ids, list):
        disk_ids = [disk_ids]

    directive = {
                "sender": sender,
                "action": action,
                "disks": disk_ids
                }
    ret= Job.submit_desktop_job(action, directive, disk_ids, REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def refresh_volume_info(volumes, disk_set, volume_disks):
    
    ctx = context.instance()
    update_disks = {}
    
    for disk_id, volume_id in volume_disks.items():
        
        volume = volumes.get(volume_id)
        if not volume:
            continue
        
        disk = disk_set.get(disk_id)
        if not disk:
            continue
        
        status = volume["status"]
        if status in [const.DISK_STATUS_DELETED, const.DISK_STATUS_CEASED]:
            if disk["status"] != const.DISK_STATUS_DELETED:
                update_disks[disk_id] = {"status": const.DISK_STATUS_DELETED, "volume_id": ''}

    if update_disks:
        ctx.pg.batch_update(TB_DESKTOP_DISK, update_disks)
    
    return None

def format_desktop_disks(sender, disk_set):
    
    ctx = context.instance()
    if not disk_set:
        return None
    
    disk_owners = ctx.pgm.get_resource_user_ids(disk_set.keys())
    if not disk_owners:
        return None
    
    volume_disks = {}
    
    for disk_id, disk in disk_set.items():
        volume_id = disk["volume_id"]
        volume_disks[disk_id] = volume_id
        user_ids = disk_owners.get(disk_id)
        if not user_ids:
            continue
        
        user_names = ctx.pgm.get_user_names(user_ids)
        if not user_names:
            user_names = {}
        
        disk["disk_owner"] = user_names

    if volume_disks:
        volume_ids = volume_disks.values()
        ret = ctx.res.resource_describe_volumes(sender["zone"], volume_ids, status=const.CHECK_VOL_STATUS)

        if ret:
            refresh_volume_info(ret, disk_set, volume_disks)
    
    return None

def check_desktop_disk_avail(disk_ids, status=None, check_trans_status=True):
    
    ctx = context.instance()
    
    if status and not isinstance(status, list):
        status = [status]
    
    if not disk_ids:
        logger.error("no disk ids %s" % disk_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, disk_ids)
    
    disks = ctx.pgm.get_disks(disk_ids)
    if not disks:
        logger.error("check dekstop disk avail, no found disk %s" % disk_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, disk_ids)
    
    if check_trans_status:
        ret = check_resource_transition_status(disks)
        if isinstance(ret, Error):
            return ret
    if status:
        for disk_id, disk in disks.items():
            if disk["status"] not in status:
                logger.error("disk %s status %s no match %s" % (disk_id, disk["status"], status))
                return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DISK_STATUS_DISMATCH, (disk_id, disk["status"], status))
    return disks

def check_disk_update_resize(config_id):
    
    ctx = context.instance()
    disks = ctx.pgm.get_disks(disk_config_ids=config_id)
    if not disks:
        return None

    update_disk = []
    for disk_id, disk in disks.items():
        volume_id = disk["volume_id"]
        if not volume_id:
            continue
        update_disk.append(disk_id)

    if not update_disk:
        return None

    update_info = {disk_id: {"need_update": const.DISK_CONF_UPDATE_RESIZE} for disk_id in update_disk}
    if not ctx.pg.batch_update(TB_DESKTOP, update_info):
        logger.error("desktop group resource not found")
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND)
    
    return None
            
def check_disk_update_delete(config_id, delete_volume):
    
    ctx = context.instance()
    if not delete_volume:
        return None
    disks = ctx.pgm.get_disks(disk_config_ids=config_id)
    if not disks:
        return None

    update_disk = []
    delete_disk = []
    for disk_id, disk in disks.items():
        volume_id = disk["volume_id"]
        if not volume_id:
            delete_disk.append(disk_id)
            continue
        update_disk.append(disk_id)
    
    if delete_disk:
        for disk_id in delete_disk:
            ctx.pg.delete(TB_DESKTOP_DISK, disk_id)
        
    if not update_disk:
        return None

    update_info = {disk_id: {"need_update": const.DISK_CONF_UPDATE_DELETE} for disk_id in update_disk}
    if not ctx.pg.batch_update(TB_DESKTOP, update_info):
        logger.error("desktop group resource not found")
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND)

    return None

def create_disks(disk_config, desktop_ids):

    ctx = context.instance()
    
    if not isinstance(desktop_ids, list):
        desktop_ids = [desktop_ids]

    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        desktops = {}
    
    new_disks = {}
    update_disk_owner = {}
    for desktop_id in desktop_ids:
        
        desktop = desktops.get(desktop_id)
        if not desktop:
            continue
        
        ret = check_desktop_disk_count(desktop_id)
        if isinstance(ret, Error):
            continue
            
        instance_id = desktop["instance_id"]
        need_update = const.DESKTOP_DISK_ATTACH
        if not instance_id:
            need_update = 0
        
        desktop_users = ctx.pgm.get_resource_user(desktop_id)
        if not desktop_users:
            desktop_users = []
    
        prefix_name = disk_config["disk_name"]
        disk_name = generate_disk_name(prefix_name)
        disk_id = get_uuid(UUID_TYPE_DESKTOP_DISK, ctx.checker)
        disk_info = dict(disk_id=disk_id,
                         volume_id='',
                         desktop_id = desktop_id,
                         desktop_name= desktop["hostname"],
                         disk_config_id=disk_config.get("disk_config_id", ""),
                         disk_type=disk_config["disk_type"],
                         desktop_group_id=desktop["desktop_group_id"],
                         desktop_group_name=desktop["desktop_group_name"],
                         size=disk_config["size"],
                         status=const.DISK_STATUS_ALLOC,
                         need_update = need_update,
                         disk_name = disk_name,
                         create_time=get_current_time(False),
                         status_time=get_current_time(False),
                         zone=desktop["zone"]
                        )
        new_disks[disk_id] = disk_info
        
        update_disk_owner[disk_id] = desktop_users
    
    if new_disks:
        # register desktop group
        if not ctx.pg.batch_insert(TB_DESKTOP_DISK, new_disks):
            logger.error("create disk insert new db fail %s" % new_disks)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    if update_disk_owner:
        for disk_id, user_ids in update_disk_owner.items():
            
            ret = ResUser.add_user_to_resource(ctx, disk_id, user_ids)
            if isinstance(ret, Error):
                return ret
    
    return new_disks.keys()

# delete disk

def delete_disks(disks):

    ctx = context.instance()
    if not disks:
        return None
    
    delete_disk = []
    update_disk = {}
    for disk_id, disk in disks.items():
        
        volume_id = disk["volume_id"]        
        if not volume_id:
            delete_disk.append(disk_id)
            continue
        
        update_disk[disk_id] = {"need_update": const.DESKTOP_DISK_DELETE}

    if delete_disk:
        for disk_id in delete_disk:
            ctx.pg.delete(TB_DESKTOP_DISK, disk_id)
    
    if update_disk:
        if not ctx.pg.batch_update(TB_DESKTOP_DISK, update_disk):
            logger.error("delete disk, update disk info fail %s" % (update_disk))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return update_disk.keys()

def delete_desktop_disks(desktops, ignore_save_disk=False):
    
    ctx = context.instance()
    desktop_ids = desktops.keys()

    desktop_disk = ctx.pgm.get_desktop_disk(desktop_ids)
    if not desktop_disk:
        return None
    
    update_desktop = []
    for desktop_id, desktop in desktops.items():
        
        desktop_group_type = desktop["desktop_group_type"]
        if desktop_group_type == const.DG_TYPE_RANDOM:
            ignore_save_disk = True

        if not ignore_save_disk:
            continue

        disk_ids = desktop_disk.get(desktop_id)
        disks = ctx.pgm.get_disks(disk_ids)
        if not disks:
            continue

        ret = delete_disks(disks)
        if isinstance(ret, Error):
            return ret
        if ret:
            update_desktop.append(desktop_id)

    return update_desktop

def check_desktop_disk_count(desktop_ids=None, desktop_group_id=None):
    
    ctx = context.instance()
    
    if desktop_ids:
        
        if not isinstance(desktop_ids, list):
            desktop_ids = [desktop_ids]
        
        ret = ctx.pgm.get_desktop_disks(desktop_ids)
        if not ret:
            return None
        
        for desktop_id in desktop_ids:
            if desktop_id not in ret:
                continue
            
            desktop_disks = ret.get(desktop_id)
            if len(desktop_disks) >= const.DESKTOP_MAX_DISK_COUNT:
                logger.error("desktop disk exceed max disk count %s" % desktop_id)
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_DISK_COUNT_EXCEEDS_MAXIMUM_LIMIT, const.DESKTOP_MAX_DISK_COUNT)
        
    if desktop_group_id:
        ret = ctx.pgm.get_disk_config(desktop_group_id=desktop_group_id)
        if not ret:
            return None
        
        if len(ret) >= const.DESKTOP_MAX_DISK_COUNT:
            logger.error("desktop disk exceed max disk count %s" % desktop_group_id)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DISK_COUNT_EXCEEDS_MAXIMUM_LIMIT, const.DESKTOP_MAX_DISK_COUNT)
    
    return None

# attach disk to desktop
def attach_disk_to_dekstop(desktop, disk_ids):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    instance_id = desktop["instance_id"]

    update_disk = {}
    # update volume desktop info
    for disk_id in disk_ids:
        
        update_info = {
                       "desktop_id": desktop_id,
                       "desktop_name": desktop["hostname"],
                       "desktop_group_id": desktop["desktop_group_id"],
                       "desktop_group_name": desktop["desktop_group_name"],
                       "status_time": get_current_time(),
                       "status": const.DISK_STATUS_ALLOC,
                       }

        if instance_id:
            update_info["need_update"] = const.DESKTOP_DISK_ATTACH

        update_disk[disk_id] = update_info

    if not ctx.pg.batch_update(TB_DESKTOP_DISK, update_disk):
        logger.error("update attach disk fail %s" % update_disk)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    desktop_users = ctx.pgm.get_resource_user(desktop_id)
    if desktop_users:
        for disk_id, _ in update_disk.items():
            ret = ResUser.add_user_to_resource(ctx, disk_id, desktop_users)
            if isinstance(ret, Error):
                return ret

    if instance_id:
        return disk_ids

    return None

# detach disk from desktop
def detach_disk_from_desktop(desktop, disks):

    ctx = context.instance()
    instance_id = desktop["instance_id"]
    job_disk = []
    zone = desktop["zone"]
    volume_ids = []
    for disk in disks:
        volume_id = disk["volume_id"]
        volume_ids.append(volume_id)

    volumes = ctx.res.resource_describe_volumes(zone, volume_ids)
    if not volumes:
        volumes = {}
    
    for disk in disks:
        disk_id = disk["disk_id"]
        status = disk["status"]
        volume_id = disk["volume_id"]
        
        volume = {}
        if volume_id and volume_id in volumes:
            volume = volumes[volume_id]

        update_info = {}
        volume_status = volume.get("status")
        
        if not instance_id or not volume_id or status in [const.DISK_STATUS_ALLOC, const.DISK_STATUS_AVAIL]:
            update_info["desktop_id"] = ""
            update_info["desktop_name"] = ""
            update_info["status"] = const.DISK_STATUS_AVAIL
            update_info["status_time"] = get_current_time()
            update_info["need_update"] = 0
        elif not volume or volume_status in [const.DISK_STATUS_DELETED, const.DISK_STATUS_CEASED, const.DISK_STATUS_AVAIL]:
            
            desk_disk_status = const.DISK_STATUS_AVAIL
            if volume_status in [const.DISK_STATUS_DELETED, const.DISK_STATUS_CEASED]:
                desk_disk_status = const.DISK_STATUS_ALLOC
            
            update_info["desktop_id"] = ""
            update_info["desktop_name"] = ""
            update_info["status"] = desk_disk_status
            update_info["status_time"] = get_current_time()
            update_info["need_update"] = 0

        else:
            update_info["need_update"] = const.DESKTOP_DISK_DETACH
            job_disk.append(disk_id)
        
        if update_info:
            if not ctx.pg.batch_update(TB_DESKTOP_DISK, {disk_id: update_info}):
                logger.error("update detach disk fail %s" % update_info)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return job_disk

# resize disk
def resize_disks(disks, size):
    
    update_disk = {}
    ctx = context.instance()

    job_disk = []
    for disk_id, disk in disks.items():
        disk_size = disk["size"]
        if disk_size > size:
            logger.error("disk %s 's new size %s GB should larger than the old size %s GB" % (disk_id, disk_size, size))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DISK_NEW_SIZE_SHOULD_LARGER_THAN_OLD_SIZE, (disk_id, disk_size, size))

        if disk_size == size:
            continue

        update_info = {
                        "size": size
                      }

        volume_id = disk["volume_id"]
        if volume_id:
            update_info["need_update"] = const.DESKTOP_DISK_RESIZE
            job_disk.append(disk_id)
        else:
            update_info["need_update"] = disk["need_update"]

        update_disk[disk_id] = update_info

    if update_disk:
        if not ctx.pg.batch_update(TB_DESKTOP_DISK, update_disk):
            logger.error("update resize disk fail " % update_disk)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return job_disk

# modify disk

def modify_disk_attributes(sender, disk, columns):
    
    ctx = context.instance()
    disk_id = disk["disk_id"]
    volume_id = disk["volume_id"]
    if volume_id:
        ret = ctx.res.resource_describe_volumes(sender["zone"], volume_id)
        if ret is None:
            logger.error("iaas describe volume is none %s" % volume_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, disk_id)
        
        volume = ret.get(volume_id)
        if volume:
            body = {}
            if "disk_name" in columns:
                body["volume_name"] = columns["disk_name"]
            if "description" in columns:
                body["description"] = columns["description"]
            if not body:
                logger.error("no found modify volume attribute %s" % volume_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, volume_id)
            
            ret = ctx.res.resource_modify_volume_attributes(sender["zone"], volume_id, body)
            if not ret:
                logger.error("iaas describe volume is none %s" % disk_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, disk_id)

    if not ctx.pg.batch_update(TB_DESKTOP_DISK, {disk_id: columns}):
        logger.error("update disk attributes fail %s " % disk_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def refresh_desktop_disk_owner(desktop_ids):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_desktops(desktop_ids)
    if not ret:
        return None
    
    desktop_disks = ctx.pgm.get_desktop_disks(desktop_ids)
    if not desktop_disks:
        return None
    
    for desktop_id, _ in ret.items():
        
        desktop_users = ctx.pgm.get_resource_user(desktop_id)
        if not desktop_users:
            continue
        
        disks = desktop_disks.get(desktop_id)
        if not disks:
            continue
        
        for disk in disks:
            disk_id = disk["disk_id"]
            ret = ResUser.add_user_to_resource(ctx, disk_id, desktop_users)
            if isinstance(ret, Error):
                return ret
    
    return None

