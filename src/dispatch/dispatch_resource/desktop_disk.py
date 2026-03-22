
import context
import constants as const
from log.logger import logger
import db.constants as dbconst
from utils.misc import get_current_time
import dispatch_resource.desktop_common as DeskComm
from api.user.resource_user import del_user_from_resource

def check_disk_resource(sender, disks):
    
    ctx = context.instance()
    disk_ids = disks.keys()
    disk_volume = ctx.pgm.get_disk_volume(disk_ids)
    if not disk_volume:
        disk_volume = {}

    volume_ids = disk_volume.values()
    volumes = ctx.res.resource_describe_volumes(sender["zone"], volume_ids)
    if volumes is None:
        logger.error("no found resource volume %s" % volume_ids)
        return -1

    for _, disk in disks.items():
        volume_id = disk["volume_id"]
        if volume_id:
            volume = volumes.get(volume_id)
            if not volume:
                logger.error("no found volume %s" % volume)
                return -1
            
            disk_status = disk["status"]
            if disk_status == const.DISK_STATUS_ALLOC:
                disk_status = const.DISK_STATUS_AVAIL

            if volume["status"] != disk_status:
                logger.error("volume status dismatch %s, %s" % (volume["status"], disk["status"]))
                return -1
    
    return 0
    
# check desktop disk
def check_desktop_resource_disk(sender, desktops):
    
    ctx = context.instance()
    desktop_ids = desktops.keys()
    disks = ctx.pgm.get_disks(desktop_ids=desktop_ids)
    if not disks:
        return 0

    disk_ids = disks.keys()
    disk_volume = ctx.pgm.get_disk_volume(disk_ids)
    if not disk_volume:
        disk_volume = {}

    volume_ids = disk_volume.values()
    volumes = ctx.res.resource_describe_volumes(sender["zone"], volume_ids)
    if volumes is None:
        logger.error("no found resource volume %s" % volume_ids)
        return -1

    for disk_id, disk in disks.items():
        desktop_id = disk["desktop_id"]
        desktop = desktops[desktop_id]
        volume_id = disk["volume_id"]
        if volume_id:
            volume = volumes.get(volume_id)
            if not volume:
                logger.error("no found volume %s" % volume)
                return -1
            
            disk_status = disk["status"]
            if disk_status == const.DISK_STATUS_ALLOC:
                disk_status = const.DISK_STATUS_AVAIL
            if volume["status"] != disk_status:
                logger.error("volume %s status dismatch %s, %s" % (volume_id, volume["status"], disk["status"]))
                return -1

            if "volumes" not in desktop:
                desktop["volumes"] = [volume_id]
            else:
                desktop["volumes"].append(volume_id)

        if "disks" not in desktop:
            desktop["disks"] = {disk_id: disk}
        else:
            desktop["disks"].update({disk_id: disk})

    return 0

def check_disk_volume(sender, disk_ids, check_resize=False):
    
    ctx = context.instance()
    disks = ctx.pgm.get_disks(disk_ids)
    if not disks:
        logger.error("job no found disks %s" % disk_ids)
        return -1

    disk_volume = ctx.pgm.get_disk_volume(disk_ids)
    if not disk_volume:
        return disks

    volume_ids = disk_volume.values()
    ret = ctx.res.resource_describe_volumes(sender["zone"], volume_ids)
    if ret is None:
        logger.error("describe disk resource fail %s" % volume_ids)
        return -1
    volumes = ret

    delete_disk = []
    resize_disk = {}
    for disk_id, volume_id in disk_volume.items():
        volume = volumes.get(volume_id)
        if not volume or volume["status"] in [const.DISK_STATUS_CEASED, const.DISK_STATUS_DELETED]:
            delete_disk.append(disk_id)
            del disks[disk_id]
            continue
        
        trans_status = volume["transition_status"]
        if trans_status:
            logger.error("volume %s in trans status" % trans_status)
            return -1
        
        disk = disks[disk_id]
        disk_status = disk["status"]
        if disk_status == const.DISK_STATUS_ALLOC:
            disk_status = const.DISK_STATUS_AVAIL
        
        if disk_status != volume["status"]:
            logger.error("disk %s status %s no match volume status %s" % (disk_id, disk["status"], volume["status"]))
            return -1

        if check_resize:
            volume_size = volume["size"]
            disk_size = disk["size"]
            if disk_size > volume_size:
                resize_disk[disk_id] = {"need_update": const.DESKTOP_DISK_RESIZE}
            else:
                resize_disk[disk_id] = {"need_update": 0}
    
    if delete_disk:
        for disk_id in delete_disk:
            ctx.pg.delete(dbconst.TB_DESKTOP_DISK, disk_id)
        
    if resize_disk:
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, resize_disk):
            logger.error("update disk resize fail:%s, %s" % resize_disk)
            return -1
    
    return disks

def get_disk_resource(disk_ids):
    
    ctx = context.instance()
    desktop_disk = ctx.pgm.get_disk_desktop(disk_ids)
    if not desktop_disk:
        return disk_ids
    
    resource_ids = []
    for desktop_id, _ids in desktop_disk.items():
        resource_ids.append(desktop_id)
        resource_ids.extend(_ids)

    return resource_ids

# create disk
def update_desktop_volume_status(volume_ids, status):

    ctx = context.instance()
    if not volume_ids:
        return 0
    
    conditions = {"volume_id": volume_ids}
    if not ctx.pg.base_update(dbconst.TB_DESKTOP_DISK, conditions, {"status": status}):
        logger.error("update disk status fail:%s, %s" % (volume_ids, status))
        return -1

    return 0

def update_desktop_disk_status(desktop, status):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    disks = desktop.get("disks")
    if disks is None:
        disks = ctx.pgm.get_disks(desktop_ids=desktop_id)
    
    if not disks:
        return 0

    disk_ids = disks.keys()

    update_info = {"status": status, "status_time": get_current_time()}
    
    update_disk = {disk_id: update_info for disk_id in disk_ids}
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_disk):
        logger.error("update disk status fail:%s" % (update_disk))
        return -1

    return 0

def check_desktop_create_disks(disk_ids):

    ctx = context.instance()

    disks = ctx.pgm.get_disks(disk_ids)
    if not disks:
        logger.error("no found create desktop disk %s" % disk_ids)
        return -1
    
    desktop_disk = {}
    for disk_id, disk in disks.items():
        
        volume_id = disk["volume_id"]
        if volume_id:
            continue
        
        desktop_id = disk["desktop_id"]
        if not desktop_id:
            continue

        status = disk["status"]
        if status not in [const.DISK_STATUS_ALLOC]:
            continue
        
        if desktop_id not in desktop_disk:
            desktop_disk[desktop_id] = {}

        desktop_disk[desktop_id].update({disk_id: disk})

    return desktop_disk

def create_volumes(sender, disks):

    ctx = context.instance()
    disk_volume = {}
    update_disk = {}
    
    for disk_id, disk in disks.items():
        size = disk["size"]
        disk_type = disk["disk_type"]
        disk_name = disk["disk_name"]
        
        volume_id = disk["volume_id"]
        if volume_id:
            continue
        
        ret = ctx.res.resource_create_volume(sender["zone"], size, disk_type, disk_name)
        if not ret:
            logger.error("Create Disk, resource handler fail %s, %s, %s" % (disk_id, disk_type, size))
            return -1
        volume_id = ret

        disk_info = {
                    "need_update": 0,
                    "volume_id": volume_id,
                    "status_time": get_current_time(),
                    }
        update_disk[disk_id] = disk_info
        disk_volume[disk_id] = volume_id
        
        DeskComm.refresh_resource_info(disk, disk_info)
    
    if update_disk:
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_disk):
            logger.error("create disk, update disk fail: %s, %s" % (disk_id, update_disk))
            return -1

    return disk_volume

def create_desktop_disk(sender, desktop, desktop_config):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    
    disks = desktop.get("disks")
    if disks is None:
        disks = ctx.pgm.get_disks(desktop_ids=desktop_id)
    
    if not disks:
        return 0

    disk_ids = disks.keys()
    # create new disk
    ret = create_volumes(sender, disks)
    if ret < 0:
        logger.error("Desktop create volume fail %s" % disk_ids)
        return -1
    disk_volume = ret

    volume_ids = disk_volume.values()
    if "volumes" in desktop_config:
        desktop_config["volumes"].extend(volume_ids)
    else:
        desktop_config["volumes"] = volume_ids

    return 0

# delete disks
def check_desktop_delete_disks(disks):

    ctx = context.instance()
    clear_disk = []
    task_disk = {}

    for disk_id, disk in disks.items():
        status = disk["status"]
        if status not in [const.DISK_STATUS_ALLOC, const.DISK_STATUS_AVAIL]:
            continue

        volume_id = disk["volume_id"]
        if not volume_id:
            clear_disk.append(volume_id)
            continue

        task_disk[disk_id] = disk

    if clear_disk:
        for disk_id in clear_disk:
            ctx.pg.delete(dbconst.TB_DESKTOP_DISK, disk_id)
        
    return task_disk

def check_delete_volume_status(zone, volume_ids):
    
    ctx = context.instance()
    ret = ctx.res.resource_describe_volumes(zone, volume_ids)
    if not ret:
        logger.error("check delete volume status, no describe volume %s" % volume_ids)
        return -1
    
    delete_volume = []
    volumes = ret
    for volume_id, volume in volumes.items():
        status = volume["status"]
        if status in [const.DISK_STATUS_CEASED, const.DISK_STATUS_DELETED]:
            continue
        
        delete_volume.append(volume_id)
    
    if delete_volume:
        ret = ctx.res.resource_delete_volumes(zone, delete_volume)
        if ret is None:
            logger.error("Delete Disk, delete volume %s fail" % volume_id)
            return -1
    
    return 0

def delete_volumes(sender, disks):

    ctx = context.instance()
   
    volume_ids = []
    for disk_id, disk in disks.items():
        volume_id = disk["volume_id"]
        if not volume_id:
            continue
        status = disk["status"]
        if status not in [const.DISK_STATUS_ALLOC, const.DISK_STATUS_AVAIL]:
            continue
        volume_ids.append(volume_id)
    
    if not volume_ids:
        return 0

    ret = ctx.res.resource_delete_volumes(sender["zone"], volume_ids)
    if ret is None:
        if check_delete_volume_status(sender["zone"], volume_ids) < 0:
            logger.error("Delete Disk, delete volume %s fail" % volume_id)
            return -1

    update_info = {}
    for disk_id, disk in disks.items():
        volume_id = disk["volume_id"]
        if volume_id not in volume_ids:
            continue
        disk_info = {
                    "need_update": 0,
                    "volume_id": '',
                    "status_time": get_current_time()
                    }
        update_info[disk_id] = disk_info

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_info):
        logger.error("delete disk, update disk fail: %s" % update_info)
        return -1
    return 0

def delete_desktop_disks(sender, desktop, is_save=False):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]

    disks = ctx.pgm.get_disks(desktop_ids=desktop_id)
    if not disks:
        return 0
    delete_disk = {}
    for disk_id, disk in disks.items():
        
        if disk["need_update"] == const.DESKTOP_DISK_DELETE:
            delete_disk[disk_id] = disk

    if not delete_disk:
        return 0
    
    disk_ids = delete_disk.keys()
    ret = delete_volumes(sender, delete_disk)
    if ret < 0:
        logger.error("delete desktop disks %s fail" % delete_disk)
        return -1
    
    if is_save:
        return 0

    for disk_id in disk_ids:
        ctx.pg.delete(dbconst.TB_DESKTOP_DISK, disk_id)
        del_user_from_resource(ctx, disk_id)
        
    return 0

# resize disk
def check_desktop_resize_disks(disks):

    task_disk = {}
    for disk_id, disk in disks.items():
        
        volume_id = disk["volume_id"]
        if not volume_id:
            continue
        
        status = disk["status"]
        if status not in [const.DISK_STATUS_AVAIL, const.DISK_STATUS_ALLOC]:
            continue
        
        disk = disks[disk_id]
        need_update = disk["need_update"]
        if need_update != const.DESKTOP_DISK_RESIZE:
            continue
        task_disk[disk_id] = disk
    
    return task_disk

def resize_volumes(sender, disks):
    
    ctx = context.instance()
   
    update_disk = {}
    size_volume = {}
    for disk_id, disk in disks.items():
        
        status = disk["status"]
        if status == const.DISK_STATUS_INUSE:
            continue
        
        volume_id = disk["volume_id"]
        if not volume_id:
            continue
        
        size = disk["size"]
        if str(size) not in size_volume:
            size_volume[str(size)] = []
        size_volume[str(size)].append(volume_id)
    
    if not size_volume:
        return 0
        
    for size, volume_ids in size_volume.items():
        ret = ctx.res.resource_resize_volumes(sender["zone"], volume_ids, size)
        if not ret:
            logger.error("resource resize volume fail %s" % volume_ids)
            return -1
        disk_info = {
                    "need_update": 0,
                    "status_time": get_current_time(),
                    }
        update_disk[disk_id] = disk_info
    
    if update_disk:
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_disk):
            logger.error("check resize disk update disk fail: %s" % update_disk)
            return -1
    
    return 0

def resize_desktop_disks(sender, desktop, disk_ids=None):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    
    disks = ctx.pgm.get_disks(disk_ids, desktop_ids=desktop_id)
    if not disks:
        return 0

    resize_disk = {}
    for disk_id, disk in disks.items():
        need_update = disk["need_update"]
        if need_update != const.DESKTOP_DISK_RESIZE:
            continue
        resize_disk[disk_id] = disk

    if not resize_disk:
        return 0

    ret = detach_desktop_disks(sender, desktop, resize_disk.keys(), False)
    if ret < 0:
        logger.error("detach disk from desktop disk fail %s, %s" % (desktop_id, disk_ids))
        return -1

    ret = resize_volumes(sender, resize_disk)
    if ret < 0:
        logger.error("resize disk fail %s" % disk_ids)
        return -1
    
    if desktop:
        ret = attach_desktop_disks(sender, desktop)
        if ret < 0:
            logger.error("attach disk to desktop fail %s, %s" % (desktop_id, disk_ids))
            return -1

    return 0

# attach disk
def check_desktop_attach_disks(disks):
    
    desktop_disk = {}
    for disk_id, disk in disks.items():
        status = disk["status"]
        if status not in [const.DISK_STATUS_ALLOC]:
            continue
        desktop_id = disk["desktop_id"]
        if not desktop_id:
            continue
        if desktop_id not in desktop_disk:
            desktop_disk[desktop_id] = {}
        desktop_disk[desktop_id].update({disk_id: disk})
        
    return desktop_disk

def attach_volumes(sender, disks, instance_id):
    
    ctx = context.instance()
    new_disk = {}
    disk_volume = {}
    for disk_id, disk in disks.items():
        volume_id = disk["volume_id"]
        if not volume_id:
            new_disk[disk_id] = disk
            continue

        status = disk["status"]
        if status not in [const.DISK_STATUS_ALLOC, const.DISK_STATUS_AVAIL]:
            continue
        disk_volume[disk_id] = volume_id

    if new_disk:
        ret = create_volumes(sender, new_disk)
        if ret == -1:
            logger.error("attach volume, create new disk fail %s" % new_disk)
            return -1

        if ret:
            disk_volume.update(ret)
    
    if not disk_volume:
        return 0
    
    volume_ids = disk_volume.values()
    ret = ctx.res.resource_attach_volumes(sender["zone"], volume_ids, instance_id)
    if ret < 0:
        logger.error("Attach Volume, resource attach volume fail %s, %s" % (volume_ids, instance_id))
        return -1

    update_info = {}
    for disk_id, volume_id in disk_volume.items():

        disk_info = {
                    "need_update": 0,
                    "volume_id": volume_id,
                    "status": const.DISK_STATUS_INUSE,
                    "status_time": get_current_time(),
                    }
        update_info[disk_id] = disk_info

        disk = disks.get(disk_id)
        DeskComm.refresh_resource_info(disk, disk_info)        

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_info):
        logger.error("attach disk update disk fail: %s, %s" % (disk_id, update_info))
        return -1

    return 0

def attach_desktop_disks(sender, desktop, disk_ids=None):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    
    disks = ctx.pgm.get_disks(disk_ids, desktop_ids=desktop_id)
    if not disks:
        return 0

    attach_disk = {}
    for disk_id, disk in disks.items():
        status = disk["status"]
        if status == const.DISK_STATUS_INUSE:
            continue
        
        if len(attach_disk) >= const.DESKTOP_MAX_DISK_COUNT:
            continue
        attach_disk[disk_id] = disk
    
    if not attach_disk:
        return 0

    desktop_id = desktop["desktop_id"]
    instance_id = desktop["instance_id"]
    if not instance_id:
        return 0
       
    ret = attach_volumes(sender, attach_disk, instance_id)
    if ret < 0:
        logger.error("attach volume fail %s" % desktop_id)
        return -1

    return 0

# detack disk

def clear_disk_desktop_info(disk_ids):

    ctx = context.instance()
    update_info = {"desktop_id": '', "desktop_name": '', "status": const.DISK_STATUS_AVAIL}
    update_disk = {disk_id: update_info for disk_id in disk_ids}
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_disk):
        logger.error("check detach disk update disk fail: %s" % update_disk)
        return -1
    
    return 0

def check_desktop_detach_disks(disks):

    desktop_disk = {}
    for disk_id, disk in disks.items():
        
        volume_id = disk["volume_id"]
        if not volume_id:
            continue
        status = disk["status"]
        if status not in [const.DISK_STATUS_INUSE]:
            continue
        desktop_id = disk["desktop_id"]
        if not desktop_id:
            continue

        if desktop_id not in desktop_disk:
            desktop_disk[desktop_id] = {}
        desktop_disk[desktop_id].update({disk_id: disk})
        
    return desktop_disk

def check_detach_volume(sender, volume_ids, instance_id):
    
    ctx = context.instance()
    detach_volume = []
    
    ret = ctx.res.resource_describe_volumes(sender["zone"], volume_ids)
    if not ret:
        logger.error("detach volume, describe volume fail %s" % volume_ids)
        return -1

    for vol_id, volume in ret.items():
        if volume["status"] == const.DISK_STATUS_INUSE:
            detach_volume.append(vol_id)
        
    if detach_volume:
        ret = ctx.res.resource_detach_volumes(sender["zone"], detach_volume, instance_id)
        if not ret:
            return -1
    
    ret = ctx.res.resource_describe_volumes(sender["zone"], volume_ids)
    if not ret:
        logger.error("detach volume, describe volume fail %s" % volume_ids)
        return -1
    
    inuse_volume = []
    for vol_id, volume in ret.items():
        if volume["status"] == const.DISK_STATUS_INUSE:
            inuse_volume.append(vol_id)

    return inuse_volume

def detach_volumes(sender, disks, instance_id):
    
    ctx = context.instance()
    disk_volume = {}
    for disk_id, disk in disks.items():
        status = disk["status"]
        if status != const.DISK_STATUS_INUSE:
            continue
        volume_id = disk["volume_id"]
        if not volume_id:
            continue

        disk_volume[disk_id] = volume_id
    
    if not disk_volume:
        return 0
    
    inuse_volume = []
    volume_ids = disk_volume.values()
    ret = ctx.res.resource_detach_volumes(sender["zone"], volume_ids, instance_id)
    if not ret:
        ret = check_detach_volume(sender, volume_ids, instance_id)
        if ret == -1:
            return -1
        
        inuse_volume = ret

    update_info = {}
    for disk_id, volume_id in disk_volume.items():
        
        if volume_id in inuse_volume:
            continue

        disk_info = {
                    "status": const.DISK_STATUS_ALLOC,
                    "status_time": get_current_time(),
                    }
        update_info[disk_id] = disk_info
    
    if update_info:
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_info):
            logger.error("check detach disk update disk fail: %s" % update_info)
            return -1
    
    return 0

def detach_desktop_disks(sender, desktop, disk_ids=None, is_detach=True, is_force=False):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    disks = ctx.pgm.get_disks(disk_ids, desktop_ids=desktop_id)
    if not disks:
        return 0
    
    detach_disk = {}
    for disk_id, disk in disks.items():
        
        if is_force:
            detach_disk[disk_id] = disk
            continue
        
        if disk["need_update"] != const.DESKTOP_DISK_DETACH:
            continue
        
        detach_disk[disk_id] = disk
    
    if not detach_disk:
        return 0
    desktop_id = desktop["desktop_id"]
    instance_id = desktop["instance_id"]
    if not instance_id:
        return 0

    disk_ids = detach_disk.keys()
    ret = detach_volumes(sender, detach_disk, instance_id)
    if ret < 0:
        logger.error("detach desktop %s disk fail %s" % (desktop_id, disk_ids))
        return -1

    update_info = {}
    for disk_id, _ in detach_disk.items():
        disk_info = {}
        if is_detach:
            disk_info["status"] = const.DISK_STATUS_AVAIL
            disk_info["status_time"] = get_current_time()
            disk_info["desktop_id"] = ''
            disk_info["desktop_name"] = ''
            disk_info["need_update"] = 0
        else:
            disk_info["status"] = const.DISK_STATUS_ALLOC
            disk_info["status_time"] = get_current_time()
            disk_info["need_update"] = const.DESKTOP_DISK_ATTACH
        
        update_info[disk_id] = disk_info

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_info):
        logger.error("update detach disk fail: %s" % update_info)
        return -1
    
    return 0

def reset_desktop_disk(sender, desktop, disk_ids=None, is_create=False):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    save_disk = desktop.get("save_disk", const.DISK_RULE_NOSAVE)
    if save_disk != const.DISK_RULE_NOSAVE:
        return 0

    disks = ctx.pgm.get_disks(disk_ids, desktop_ids=desktop_id)
    if not disks:
        return 0

    clear_disk = {}
    create_disk = {}
    for disk_id, disk in disks.items():
        volume_id = disk["volume_id"]
        if volume_id:
            clear_disk[disk_id] = disk
        else:
            create_disk[disk_id] = disk
    
    if clear_disk and not is_create:

        ret = detach_desktop_disks(sender, desktop, clear_disk.keys(), is_detach=False, is_force=True)
        if ret < 0:
            logger.error("task detach disk fail[%s]" % disk_ids)
            return -1
        
        clear_disk_ids = clear_disk.keys()
        clear_disk = ctx.pgm.get_disks(clear_disk_ids)
        if not clear_disk:
            clear_disk = {}

        ret = delete_volumes(sender, clear_disk)
        if ret < 0:
            logger.error("delete desktop disks %s fail" % clear_disk.keys())
            return -1

    if create_disk and is_create:
        ret = create_volumes(sender, create_disk)
        if ret < 0:
            logger.error("Desktop create volume fail %s" % disk_ids)
            return -1
        disk_volume = ret

        ret = attach_desktop_disks(sender, desktop)
        if ret < 0:
            logger.error("citrix platform attach disk fail %s" % desktop["hostname"])
            return -1
    
        volume_ids = disk_volume.values()
        ret = update_desktop_volume_status(volume_ids, const.DISK_STATUS_INUSE)
        if ret < 0:
            logger.error("Task reset desktop, update disk status fail:%s" % (desktop_id))
            return -1
    return 0
    