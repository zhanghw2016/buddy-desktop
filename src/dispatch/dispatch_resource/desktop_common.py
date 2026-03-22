import context
import db.constants as dbconst
from utils.id_tool import get_resource_type
import constants as const
from log.logger import logger

def set_desktop_group_apply(desktop_group_id, is_apply):

    # set desktop group is_apply flag
    ctx = context.instance()
    update_info = {"is_apply": is_apply}
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_GROUP, {desktop_group_id: update_info}):
        logger.error("Failed to update desktop group[%s] to apply %s" % (desktop_group_id, is_apply))
        return -1

    return 0

def get_instances(sender, instance_ids, status=None):

    ctx = context.instance()
    instances ={}
    if not instance_ids:
        return instances
    
    instance_set = ctx.res.resource_describe_instances(sender["zone"], instance_ids, status)
    if instance_set is None:
        return None
    # build instance
    for instance_id, instance in instance_set.items():
        instance_info = {}
        instance_info['cpu'] = instance["vcpus_current"]
        instance_info['memory'] = instance["memory_current"]
        instance_info["volume_ids"] = instance.get("volume_ids","")
        instance_info["status"] = instance["status"]
        instance_info["graphics_passwd"] = instance["graphics_passwd"]
        instance_info["transition_status"] = instance["transition_status"]
        instance_info['host_machine'] = instance["host_machine"]
        if "image" in instance:
            image = instance["image"]
            instance_info['image_id'] = image["image_id"]

        if "extra" in instance:
            extra = instance["extra"]
            ivshmem = extra.get("ivshmem", "")
            instance_info['ivshmem'] = ivshmem if ivshmem else ''
            instance_info["gpu"] = extra["gpu"]
            instance_info["qxl_number"] = extra.get("qxl_number", 1)
            usbredir = extra.get("usbredir", None)
            if usbredir is not None:
                instance_info['usbredir'] = usbredir

            clipboard = extra.get("clipboard", None)
            if clipboard is not None:
                instance_info["clipboard"] = clipboard

            filetransfer = extra.get("filetransfer", None)
            if filetransfer is not None:
                instance_info['filetransfer'] = filetransfer
        
        instances[instance_id] = instance_info
    
    return instances

def get_desktop_resource(desktop_ids, resource_type=[const.RES_DESKTOP, const.RES_DISK, const.RES_NIC]):

    ctx = context.instance()
    resource_ids = []
    if not desktop_ids:
        logger.error("get desktop resource no found desktop ids [%s]" % desktop_ids)
        return None
    
    if not isinstance(desktop_ids, list):
        desktop_ids = [desktop_ids]

    resource_ids.extend(desktop_ids)
    # disk
    if const.RES_DISK in resource_type:
        disks = ctx.pgm.get_disks(desktop_ids=desktop_ids)
        if disks:
            resource_ids.extend(disks.keys())

    return resource_ids

def get_resource_instance(resource_id):

    ctx = context.instance()
    
    ret = get_resource_type(resource_id)
    if ret == dbconst.RESTYPE_DESKTOP:
        desktops = ctx.pgm.get_desktops(resource_id)
        if not desktops:
            return None
        
        desktop = desktops[resource_id]
        instance_id = desktop["instance_id"]
        if not instance_id:
            return None
        
        return instance_id
    elif ret == dbconst.RESTYPE_DESKTOP_IMAGE:
        desktop_images = ctx.pgm.get_desktop_images(resource_id)
        if not desktop_images:
            return None
        
        desktop_image = desktop_images[resource_id]
        instance_id = desktop_image["instance_id"]
        if not instance_id:
            return None
        
        return instance_id
    
    return None

def check_desktop_instance_config(desktop, instance):

    check_key = ["cpu", "memory","ivshmem", "gpu",
                 "usbredir", "clipboard", "filetransfer", "qxl_number"]
        
    config_info = {}

    for key in check_key:
        if key not in instance or key not in desktop:
            continue

        if instance[key] == desktop[key]:
            continue
        
        if key in ["cpu", "memory"]:
            config_info["cpu"] = desktop["cpu"]
            config_info["memory"] = desktop["memory"]
        else:
            config_info[key] = desktop[key]

    return config_info

def refresh_resource_info(resource, resource_info):
    
    if not resource_info or not resource:
        return None
    
    for k, v in resource_info.items():
        if k not in resource:
            resource[k] = v
            continue
        resource[k] = v
    
    return None

def get_desktop_ivshmem(zone):
    
    ctx = context.instance()
    ivshmem = ctx.zone_checker.get_resource_limit(zone, "ivshmem")
    if ivshmem is None:
        logger.error("get ivshmem fail")
        return None
    
    return ivshmem
    
def update_task_resource(task_id, resource_ids):
    
    ctx = context.instance()
    if not isinstance(resource_ids, list):
        resource_ids = [resource_ids]
    
    update_info = {
        "resource_ids": ",".join(resource_ids)
    }
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_TASK, {task_id: update_info}):
        logger.error("update desktop task resource %s to desktop fail %s" % (task_id, update_info))
        return -1
    
