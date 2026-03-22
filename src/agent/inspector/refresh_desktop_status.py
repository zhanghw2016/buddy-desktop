
import context
from log.logger import logger
import constants as const
import db.constants as dbconst
from utils.misc import get_current_time

def check_desktop_task_status(desktop_id):
    
    ctx = context.instance()
    ret = ctx.pgm.get_tasks(resource_ids = desktop_id, status=[const.TASK_STATUS_WORKING, const.TASK_STATUS_PEND])
    if ret:
        return False
    return True

def refresh_zone_desktop_status(zone_id, desktops):
    
    ctx = context.instance()
    if not desktops:
        return None
    desktop_ids = desktops.keys()

    desktop_instance = {}
    for desktop_id, desktop in desktops.items():
        
        instance_id = desktop["instance_id"]
        if not instance_id:
            continue
        
        desktop_instance[desktop_id] = instance_id
    
    instance_ids = desktop_instance.values()
    instances = {}
    
    if instance_ids:
        instances = ctx.res.resource_describe_instances(zone_id, instance_ids)
        if instances is None:
            logger.error("refresh no found instance")
            return None

    update_desktop = {}
    for desktop_id, instance_id in desktop_instance.items():
        
        desktop = desktops[desktop_id]
        desktop_status = desktop["status"]
        transition_status = desktop["transition_status"]

        status_info = {}
        instance = instances.get(instance_id)
        if not instance:
            continue
        
        if instance["transition_status"]:
            continue

        if transition_status:
            ret = check_desktop_task_status(desktop_id)
            if not ret:
                continue

        if desktop_status != instance["status"]:
            status_info["transition_status"] = ''
            status_info["status"] = instance["status"]
            update_desktop[desktop_id] = status_info
        
        if transition_status != instance["transition_status"]:
            status_info["transition_status"] = instance["transition_status"] if instance["transition_status"] else ''
            status_info["status"] = instance["status"]
            update_desktop[desktop_id] = status_info

    if not update_desktop:
        logger.info("refresh desktop count %s, update count %s" % (len(instance_ids), 0))
        return None
    
    update_infos = {}
    
    for desktop_id, update_desktop_item in update_desktop.items():
        update_info = dict(
            status=update_desktop_item.get("status"),
            transition_status=update_desktop_item.get("transition_status", ''),
            status_time = get_current_time()
        )
        
        update_infos[desktop_id] = update_info

    ctx.pg.batch_update(dbconst.TB_DESKTOP, update_infos)
    
    logger.info("refresh desktop count %s, update count %s" % (len(instance_ids), len(update_desktop)))
    
    return None

def refresh_desktop_status():

    ctx = context.instance()
    if not ctx.zones:
        logger.error("refresh desktop no found zone")
        return None

    zone_ids = ctx.zones.keys()
    
    for zone_id in zone_ids:

        ret = ctx.pgm.get_all_desktops(zone_id)
        if not ret:
            continue
        
        desktops = ret
        
        refresh_zone_desktop_status(zone_id, desktops)
        
    return None
