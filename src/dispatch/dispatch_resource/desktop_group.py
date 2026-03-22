
import context
from log.logger import logger
import constants as const
import dispatch_resource.desktop_disk as Disk
import db.constants as dbconst
from utils.misc import get_current_time
import utils.id_tool as ResID
import resource_common as ResComm
import dispatch_resource.desktop_common as DeskComm
import dispatch_resource.desktop_citrix as Citrix
import dispatch_resource.desktop_instance as Instance
from common import is_citrix_platform

def check_group_resource_type(resources):
    
    desktops = {}
    disks = {}
    nics = {}
    for resource_id, resource in resources.items():
        prefix = resource_id.split("-")[0]
        if prefix == ResID.UUID_TYPE_DESKTOP:
            desktops[resource_id] = resource
        elif prefix == ResID.UUID_TYPE_DESKTOP_DISK:
            disks[resource_id] = resource
        elif ":" in prefix:
            nics[resource_id] = resource
        else:
            continue
    
    return (desktops, disks, nics)

# apply desktop group
def check_desktop_group_update_resource(desktop_group_id):

    ctx = context.instance()
    resources = {}
    # check update desktop
    need_update=[const.DESKTOP_UPDATE_DELETE,
                 const.DESKTOP_UPDATE_CREATE,
                 const.DESKTOP_UPDATE_MODIFY,
                 const.DESKTOP_UPDATE_RESET]
    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id, need_update=need_update)
    if not desktops:
        desktops = {}
    
    for desktop_id, desktop in desktops.items():
        need_update = desktop["need_update"]
        if not need_update:
            continue
    
        instance_id = desktop["instance_id"]
        if not instance_id:
            if need_update != const.DESKTOP_UPDATE_CREATE:
                continue
        
        status = desktop["status"]
        if need_update == const.DESKTOP_UPDATE_MODIFY:
            if status != const.INST_STATUS_STOP:
                continue
        
        resources[desktop_id] = desktop

    # check update disk
    need_update = [const.DESKTOP_DISK_RESIZE, 
                   const.DESKTOP_DISK_ATTACH, 
                   const.DESKTOP_DISK_DELETE]
    disks = ctx.pgm.get_disks(desktop_group_ids=desktop_group_id, need_update=need_update)
    if not disks:
        disks = {}
    
    for disk_id, disk in disks.items():
        need_update = disk["need_update"]
        if not need_update:
            continue
        
        status = disk["status"]
        if status not in [const.DISK_STATUS_ALLOC, const.DISK_STATUS_AVAIL]:
            continue

        resources[disk_id] = disk

    # check update disk
    need_update = [const.DESKTOP_NIC_ATTACH, 
                   const.DESKTOP_NIC_DETACH]
    nics = ctx.pgm.get_nics(desktop_group_id=desktop_group_id, need_update=need_update)
    if not nics:
        nics = {}
    
    nic_desktop = []
    for _, nic in nics.items():
        need_update = nic["need_update"]
        if not need_update:
            continue
        
        resource_id = nic["resource_id"]
        if resource_id not in resources:
            nic_desktop.append(resource_id)
    
    if nic_desktop:
        desktops = ctx.pgm.get_desktops(nic_desktop)
        if desktops:
            resources.update(desktops)
        
    return resources
    
def check_apply_desktop_group_task(sender, resources):
    '''
    1. delete desktop
    2. create desktop
    3. reset desktop
    4. modify desktop
    5. update desktop
    6. resize disk
    7. update nic
    '''
    task_resource = {}
    ret = check_group_resource_type(resources)
    (desktops, disks, nics) = ret

    desktop_ids = desktops.keys()
    if nics:
        for _, nic in nics.items():
            resource_id = nic["resource_id"]
            if resource_id in desktops:
                continue
            task_resource[resource_id] = const.TASK_ACTION_UPDATE_DESKTOP
            desktop_ids.append(resource_id)

    check_disks = {}
    if disks:
        for disk_id, disk in disks.items():
            desktop_id = disk["desktop_id"]
            need_update = disk["need_update"]
            if not desktop_id:
                if need_update == const.DESKTOP_DISK_RESIZE:
                    task_type = const.TASK_ACTION_RESIZE_DISK
                elif need_update == const.DESKTOP_DISK_DELETE:
                    task_type = const.TASK_ACTION_DELETE_DISK
                
                task_resource[disk_id] = task_type
                check_disks[disk_id] = disk
                continue
            else:
                if need_update == const.DESKTOP_DISK_ATTACH:
                    task_resource[desktop_id] = const.TASK_ACTION_UPDATE_DESKTOP
                    check_disks[disk_id] = disk
   
            if desktop_id not in desktop_ids:
                desktop_ids.append(desktop_id)

        if check_disks:
            ret = Disk.check_disk_resource(sender, check_disks)
            if ret < 0:
                logger.error("check disk resource fial %s" % check_disks)
                return -1

    ret = Instance.check_desktop_instance(sender, desktop_ids)
    if ret == -1:
        logger.error("check desktop instance fail %s" % desktop_ids)
        return -1
    check_desktops = ret

    # check desktop update flag
    for desktop_id, desktop in check_desktops.items():
        
        need_update = desktop["need_update"]
        status = desktop["status"]

        if need_update == const.DESKTOP_UPDATE_DELETE:
            task_resource[desktop_id] = const.TASK_ACTION_DELETE_DESKTOP
        elif need_update == const.DESKTOP_UPDATE_CREATE:
            task_resource[desktop_id] = const.TASK_ACTION_CREATE_DESKTOP
        elif need_update == const.DESKTOP_UPDATE_RESET:
            task_resource[desktop_id] = const.TASK_ACTION_RESET_DESKTOP
        elif need_update == const.DESKTOP_UPDATE_MODIFY:
            if status == const.INST_STATUS_STOP:
                task_resource[desktop_id] = const.TASK_ACTION_MODIFY_DESKTOP_ATTRIBUTES
        else:
            task_resource[desktop_id] = const.TASK_ACTION_UPDATE_DESKTOP
    
    return (task_resource, check_desktops, check_disks)

def clear_network_config(desktop_group):

    ctx = context.instance()
    network_configs = desktop_group.get("networks")
    if not network_configs:
        return 0

    for network_config_id, _ in network_configs.items():
        nics = ctx.pgm.get_network_config_nics(network_config_id)
        if not nics:
            nics = {}

        update_nic = {}
        for nic_id, nic in nics.items():
            resource_id = nic["resource_id"]
            status = nic["status"]

            update_info = {
                            "is_occupied": 0,
                            "desktop_group_id": '',
                            "desktop_group_name": '',
                            "network_config_id": '',
                            "status_time": get_current_time()
                            }
            if resource_id:
                if status == const.NIC_STATUS_INUSE:
                    update_info["need_update"] = const.DESKTOP_NIC_DETACH
                else:
                    update_info["status"] = const.NIC_STATUS_AVAIL
                    update_info["resource_id"] = ''
                    update_info["resource_name"] = ''
            else:
                update_info["status"] = const.NIC_STATUS_AVAIL
                update_info["need_update"] = 0

            update_nic[nic_id] = update_info
        
        if update_nic:
            if not ctx.pg.batch_update(dbconst.TB_DESKTOP_NIC, update_nic):
                logger.error("update desktop nic fail %s" % update_nic)
                return -1
        ctx.pg.delete(dbconst.TB_DESKTOP_GROUP_NETWORK, network_config_id)

    return 0

def clear_disk_config(desktop_group):

    ctx = context.instance()
    disk_configs = desktop_group.get("disks")
    if not disk_configs:
        return 0
    
    disk_config_ids = disk_configs.keys()
    
    for disk_config_id in disk_config_ids:
        ctx.pg.delete(dbconst.TB_DESKTOP_GROUP_DISK, disk_config_id)
        
    ret = ctx.pgm.get_disks(disk_config_ids=disk_config_ids)
    if not ret:
        return 0
    disks = ret

    update_disk = {}
    for disk_id, _ in disks.items():
        update_disk[disk_id] = {
            "disk_config_id": ''
            }

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_disk):
        logger.error("Failed to update disk config[%s]" % update_disk)
        return -1

    return 0

def check_delete_desktop_group(sender, desktop_group_id):
        
    task_resource = {}

    ret = check_desktop_group_instance(sender, desktop_group_id)
    if ret < 0:
        logger.error("resource desktop instance fail %s " % desktop_group_id)
        return -1

    task_desktop = ret
    if task_desktop:
        task_resource[const.TASK_ACTION_DELETE_DESKTOP] = task_desktop

    ret = check_desktop_group_disk(sender, desktop_group_id)
    if ret < 0:
        logger.error("resource desktop instance fail %s " % desktop_group_id)
        return -1

    task_disk = ret
    if task_disk:
        task_resource[const.TASK_ACTION_DELETE_DISK] = task_disk
    
    return task_resource

def delete_desktop_group(desktop_group_id):

    ctx = context.instance()

    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
    if desktops:
        return 0
    
    disks = ctx.pgm.get_disks(desktop_group_ids=desktop_group_id)
    if disks:
        return 0

    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
    if not desktop_group:
        return 0
    
    ret = clear_network_config(desktop_group)
    if ret < 0:
        logger.error("clear delete desktop group network config fail %s" % desktop_group_id)
        return -1
    
    ret = clear_disk_config(desktop_group)
    if ret < 0:
        logger.error("clear delete desktop group disk config fail %s" % desktop_group_id)
        return -1

    users = desktop_group["users"]
    if users:
        for user_id, _ in users.items():
            conditions = dict(desktop_group_id=desktop_group_id, 
                              user_id=user_id)
    
            ctx.pg.base_delete(dbconst.TB_DESKTOP_GROUP_USER, conditions)
    
    ctx.pg.delete(dbconst.TB_DESKTOP_GROUP, desktop_group_id)
    ctx.pg.base_delete(dbconst.TB_ZONE_USER_SCOPE, {"resource_id": desktop_group_id})
        
    return 0

def task_delete_desktop_group(job_id, action, sender, desktop_group_id):
    
    ctx = context.instance()
    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
    if not desktop_group:
        logger.error("delete desktop group no found resource %s" % desktop_group_id)
        return -1

    with ResComm.transition_status(dbconst.TB_DESKTOP_GROUP, desktop_group_id, const.STATUS_DELETING):

        if is_citrix_platform(ctx, sender["zone"]):
            ret = Citrix.task_delete_citrix_desktop_group(sender, desktop_group)
            if ret < 0:
                logger.error("task delete citrix desktop group fail %s" % desktop_group_id)
                return -1
            
            return 0

        ret = check_delete_desktop_group(sender, desktop_group_id)
        if ret < 0:
            logger.error("check delete desktop group fail %s" % desktop_group_id)
            return -1

        task_resource = ret
        task_ids = []
        # create desktop task
        for task_type, resources in task_resource.items():

            if task_type == const.TASK_ACTION_DELETE_DESKTOP:
                for resource_id in resources:
                    directive = {"desktop": resource_id}
        
                    task_id = ResComm.new_desktop_task(sender, job_id, action, resource_id, directive, task_type)
                    if not task_id:
                        logger.error("Job[%s] create task fail %s, %s" % (action, task_type, resource_id))
                        return -1
                    task_ids.append(task_id)

            elif task_type == const.TASK_ACTION_DELETE_DISK:
                for resource_id in resources:
                    directive = {"disk": resource_id}
        
                    task_id = ResComm.new_desktop_task(sender, job_id, action, resource_id, directive, task_type)
                    if not task_id:
                        logger.error("Job[%s] create task fail %s, %s" % (action, task_type, resource_id))
                        return -1
                    task_ids.append(task_id)
        
        if not task_ids:
            logger.error("Job[%s] no task %s " % (action, desktop_group_id))
            return -1
        
        ret = ResComm.dispatch_resource_task(job_id, task_ids)
        if ret < 0:
            logger.error("dispatch task handle fail %s %s " % (job_id, task_ids))
            return -1
        
        return 0

def check_desktop_group_instance(sender, desktop_group_id):

    ctx = context.instance()
    
    delete_desktop = []
    task_desktop = []
    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
    if not desktops:
        return 0
    desktop_ids = desktops.keys()

    # only check instance desktop
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        desktop_instance = {}

    for desktop_id in desktop_ids:
        if desktop_id in desktop_instance:
            continue

        desktop = desktops.get(desktop_id)
        if not desktop:
            logger.error("delete desktop group no found desktop %s" % desktop_id)
            return -1

        ret = Instance.clear_desktop_info(desktop)
        if ret < 0:
            logger.error("clear desktop info %s" % desktop_id)
            return -1

    if not desktop_instance:
        return 0

    instance_ids = desktop_instance.values()
    # get instance resource
    res_instances = DeskComm.get_instances(sender, instance_ids)
    if res_instances is None:
        logger.error("resource describe instance return none %s" % instance_ids)
        return -1

    for desktop_id, desktop in desktops.items():

        instance_id = desktop_instance.get(desktop_id)
        if not instance_id:
            continue

        instance = res_instances.get(instance_id)
        if not instance or instance["status"] in [const.INST_STATUS_CEASED, const.INST_STATUS_TERM]:
            delete_desktop.append(desktop)
            continue
    
        # instance has trans status, cant handle
        trans_status = instance["transition_status"]
        if trans_status:
            logger.error("resource %s in trans status " % trans_status)
            return -1
        
        task_desktop.append(desktop_id)
    
    if delete_desktop:
        for desktop in delete_desktop:
            ret = Instance.clear_desktop_info(desktop)
            if ret < 0:
                logger.error("clear desktop info %s" % desktop["desktop_id"])
                return -1

    return task_desktop

def check_desktop_group_disk(sender, desktop_group_id):
    
    ctx = context.instance()
    disks = ctx.pgm.get_disks(desktop_group_ids=desktop_group_id, status=[const.DISK_STATUS_AVAIL])
    if not disks:
        return 0
    
    disk_ids = disks.keys()
    disk_volume = ctx.pgm.get_disk_volume(disk_ids)
    if not disk_volume:
        for disk_id in disk_ids:
            ctx.pg.delete(dbconst.TB_DESKTOP_DISK, disk_id)

    volume_ids = disk_volume.values()
    ret = ctx.res.resource_describe_volumes(sender["zone"], volume_ids)
    if ret is None:
        logger.error("describe disk resource fail %s" % volume_ids)
        return -1
    volumes = ret

    task_disk = []
    for disk_id, volume_id in disk_volume.items():
        volume = volumes.get(volume_id)
        if not volume or volume["status"] in [const.DISK_STATUS_CEASED, const.DISK_STATUS_DELETED]:
            ctx.pg.delete(dbconst.TB_DESKTOP_DISK, disk_id)
            continue
        
        trans_status = volume["transition_status"]
        if trans_status:
            logger.error("volume %s in trans status" % trans_status)
            return -1
        
        task_disk.append(disk_id)
    
    return task_disk
