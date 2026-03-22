import constants as const
import db.constants as dbconst
from log.logger import logger
from utils.misc import rLock
from utils.thread_local import set_msg_id
from utils.json import json_load
import traceback
from common import is_citrix_platform
import context
import dispatch_resource.desktop_instance as Instance
import dispatch_resource.desktop_nic as Nic
import dispatch_resource.desktop_disk as Disk
import dispatch_resource.desktop_image as Image
import dispatch_resource.desktop_network as Network
import dispatch_resource.desktop_common as DeskComm
import dispatch_resource.desktop_group as DesktopGroup
import dispatch_resource.desktop_citrix as Citrix
import dispatch_resource.desktop_snapshot as Snapshot
import dispatch_resource.terminal as Terminal
import dispatch_resource.software as Software
import dispatch_resource.file_share as FileShare
import dispatch_resource.component as Component
import resource_common as ResComm
from send_request import push_topic_job
from utils.net import get_hostname

def handle_job_create_desktop_group(job_id, job):
    
    ctx = context.instance()
    sender = job['directive']["sender"]
    desktop_group_ids= job['directive']['desktop_groups']
    desktop_group_id = desktop_group_ids[0]
    action = job['directive']['action']
    
    with rLock(desktop_group_id):
        ret = Citrix.create_citrix_desktop_group(sender, desktop_group_id)
        if ret < 0:
            DesktopGroup.delete_desktop_group(desktop_group_id)
            logger.error("job create desktop group fail %s, %s " % (job_id, desktop_group_id))
            return -1
        
    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
    if not desktop_group:
        logger.error("get desktop group fail %s" % desktop_group_id)
        return -1

    desktop_count = desktop_group["desktop_count"]
    if not desktop_count:
        return 0

    # create desktop task
    task_ids = []
    for _ in range(0, desktop_count):
        directive = {"desktop_group": desktop_group_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_group_id, directive)
        if not task_id:
            logger.error("Job[%s] start task fail %s" % (action, desktop_group_id))
            return -1
        task_ids.append(task_id)
    
    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_update_citrix_image(job_id, job):

    action = job['directive']['action']
    ctx = context.instance()
    sender = job['directive']["sender"]
    desktop_group_ids = job['directive']['desktop_groups']
    desktop_group_id = desktop_group_ids[0]
    citrix_update = job['directive']["citrix_update"]

    with rLock(desktop_group_id):
        desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
        if not desktop_group:
            logger.error("no found desktop group %s" % desktop_group_id)
            return -1
        
        desktop_image_id = citrix_update.get("desktop_image")
        if not desktop_image_id:
            return 0
    
        ret = Citrix.update_citrix_desktop_group_image(sender, desktop_group_id, desktop_image_id)
        if ret < 0:
            logger.error("update desktop image fail %s, %s, %s, %s" % (desktop_group_id, desktop_image_id, action, job_id))
            return -1
        
        return 0

def handle_job_add_citrix_computers(job_id, job):
    
    action = job['directive']['action']
    ctx = context.instance()
    sender = job['directive']["sender"]
    desktop_group_ids = job['directive']['desktop_groups']
    desktop_group_id = desktop_group_ids[0]
    citrix_update = job['directive']["citrix_update"]
    with rLock(desktop_group_id):
    
        desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
        if not desktop_group:
            logger.error("no found desktop group %s" % desktop_group_id)
            return -1

        task_ids = []
        desktop_count = citrix_update.get("desktop_count")
        if not desktop_count:
            return 0
    
        for _ in range(0, desktop_count):
            directive = {"desktop_group": desktop_group_id}
            task_type = const.TASK_ACTION_CREATE_COMPUTER
            task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_group_id, directive, task_type)
            if not task_id:
                logger.error("Job[%s] start task fail %s" % (action, desktop_group_id))
                return -1
            task_ids.append(task_id)

        return ResComm.dispatch_resource_task(job_id, task_ids)

    return 0

def handle_job_apply_desktop_group(job_id, job):
    
    action = job['directive']['action']
    desktop_group_ids = job['directive']['desktop_groups']
    sender = job['directive']["sender"]
    desktop_group_id = desktop_group_ids[0]
    ret = DesktopGroup.check_desktop_group_update_resource(desktop_group_id)
    if not ret:
        DeskComm.set_desktop_group_apply(desktop_group_id, 0)
        return 0
    
    resources = ret
    resource_ids = resources.keys()
    with rLock(desktop_group_id):

        with ResComm.transition_status(dbconst.TB_DESKTOP_GROUP, desktop_group_id, const.STATUS_UPDATING):
            
            ret = DesktopGroup.check_apply_desktop_group_task(sender, resources)
            if ret == -1:
                logger.error("check apply desktop group fail %s" % (desktop_group_id))
                return -1
    
            (task_resource, check_desktops, check_disks) = ret
            # create desktop task
            task_ids = []
            for resource_id, task_type in task_resource.items():
                directive = {}
                if task_type in [const.TASK_ACTION_RESIZE_DISK, const.TASK_ACTION_DELETE_DISK]:
                    disk = check_disks.get(resource_id)
                    if not disk:
                        continue
                    directive["disk"] = resource_id
                else:
                    desktop = check_desktops.get(resource_id)
                    if not desktop:
                        continue
                    if "modify_config" in desktop:
                        directive["modify_config"] = desktop["modify_config"]
                    directive["desktop"] = resource_id
                
                if task_type == const.TASK_ACTION_RESET_DESKTOP:
                    directive["trans_status"] = const.INST_TRAN_STATUS_RESETTING
                elif task_type == const.TASK_ACTION_CREATE_DESKTOP:
                    directive["trans_status"] = const.INST_TRAN_STATUS_CREATING
    
                task_id = ResComm.new_desktop_task(sender, job_id, action, resource_id, directive, task_type)
                if not task_id:
                    logger.error("Job[%s] create task fail %s, %s" % (action, task_type, resource_id))
                    return -1
                task_ids.append(task_id)
    
            if not task_ids:
                logger.error("Job[%s] no task %s " % (action, resource_ids))
                return -1
            
            ret = ResComm.dispatch_resource_task(job_id, task_ids)
            if ret < 0:
                logger.error("dispatch task handle fail %s, %s " % (job_id, task_ids))
                return -1
    
            DeskComm.set_desktop_group_apply(desktop_group_id, 0)
        return 0

def handle_job_delete_desktop_groups(job_id, job):
    
    action = job['directive']['action']
    desktop_group_ids = job['directive']["desktop_groups"]
    sender = job['directive']["sender"]

    with rLock(desktop_group_ids):
        
        for desktop_group_id in desktop_group_ids:
            ret = DesktopGroup.task_delete_desktop_group(job_id, action, sender, desktop_group_id)
            if ret < 0:
                logger.error("delete desktop group fail %s" % desktop_group_id)
                return -1

            ret = DesktopGroup.delete_desktop_group(desktop_group_id)
            if ret < 0:
                logger.error("job delete desktop group fail %s " % (desktop_group_id))
                return -1
        
        return 0

def handle_job_create_desktops(job_id, job):
    
    ctx = context.instance()
    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]
    ret = Instance.check_create_desktops(sender, desktop_ids)
    if ret == -1:
        logger.error("Job check create desktop [%s] fail" % desktop_ids)
        return -1
    desktops = ret

    # create desktop task
    task_ids = []
    for desktop_id, _ in desktops.items():
        directive = {"desktop": desktop_id, "trans_status": const.INST_TRAN_STATUS_CREATING}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1

        task_ids.append(task_id)

    ret = ResComm.dispatch_resource_task(job_id, task_ids)
    if ret < 0:
        if is_citrix_platform(ctx, sender["zone"]):
            Citrix.check_citrix_desktop(desktops.keys())
    
    return ret

def handle_job_lease_desktops(job_id, job):
    
    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]

    # create desktop task
    task_ids = []
    for desktop_id in desktop_ids:
        directive = {"desktop": desktop_id, "trans_status": const.INST_TRAN_STATUS_RESUMING}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1

        task_ids.append(task_id)

    ret = ResComm.dispatch_resource_task(job_id, task_ids)
    if ret < 0:
        return -1
    
    return ret

def handle_job_start_desktops(job_id, job):
    
    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]
    
    ret = Instance.check_desktop_instance(sender, desktop_ids)
    if ret == -1:
        logger.error("check start desktop fail %s" % desktop_ids)
        return -1
    desktops = ret
    
    ret = Instance.check_start_desktops(sender, desktops)
    if ret == -1:
        logger.error("check desktop instance fail %s " % (desktop_ids))
        return -1
    (start_desktop, create_desktop) = ret

    # create desktop task
    task_ids = []
    for desktop_id in start_desktop:

        directive = {}
        task_type = const.TASK_ACTION_START_DESKTOP

        if desktop_id in create_desktop:
            directive["desktop"] = desktop_id
            directive["trans_status"] = const.INST_TRAN_STATUS_STARTING
            task_type = const.TASK_ACTION_CREATE_DESKTOP
        else:
            directive["desktop"] = desktop_id
        
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive, task_type)
        if not task_id:
            logger.error("Job[%s] start task fail %s" % (action, desktop_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_reset_desktops(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    trans_status = job['directive'].get("trans_status")
    sender = job['directive']["sender"]
    if not trans_status:
        trans_status = const.INST_TRAN_STATUS_RESETTING
        
    ret = Instance.check_desktop_instance(sender, desktop_ids)
    if ret == -1:
        logger.error("check start desktop fail %s" % desktop_ids)
        return -1
    desktops = ret

    ret = Instance.check_reset_desktops(desktops)
    if ret == -1:
        logger.error("job reset desktop fail %s" % desktop_ids)
        return -1
    
    reset_desktop = ret
    # create desktop task
    task_ids = []
    for desktop_id, _ in reset_desktop.items():

        directive = {"desktop": desktop_id, "trans_status": trans_status}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1

        task_ids.append(task_id)
    
    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_restart_desktops(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]

    ret = Instance.check_desktop_instance(sender, desktop_ids)
    if ret == -1:
        logger.error("check start desktop fail %s" % desktop_ids)
        return -1

    desktops = ret

    ret = Instance.check_restart_desktops(sender, desktops)
    if ret < 0:
        logger.error("check desktop instance fail %s " % (desktop_ids))
        return -1
    (task_desktop, reset_desktop, stop_desktop) = ret

    # create desktop task
    task_ids = []
    for desktop_id, _ in task_desktop.items():

        directive = {"desktop": desktop_id}
        task_type = const.TASK_ACTION_RESTART_DESKTOP

        if desktop_id in reset_desktop:
            directive = {"desktop": desktop_id, "trans_status": const.INST_TRAN_STATUS_RESTARTING}
            task_type = const.TASK_ACTION_RESET_DESKTOP

        elif desktop_id in stop_desktop:
            directive = {"desktop": desktop_id, "trans_status": const.INST_TRAN_STATUS_RESTARTING, "expect_status": const.INST_STATUS_RUN}
            st_desk = stop_desktop[desktop_id]
            if "modify_config" in st_desk:
                directive["modify_config"] = st_desk["modify_config"]

            task_type = const.TASK_ACTION_STOP_DESKTOP
        
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive, task_type)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_stop_desktops(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]


    ret = Instance.check_desktop_instance(sender, desktop_ids)
    if ret == -1:
        logger.error("check start desktop fail %s" % desktop_ids)
        return -1
    desktops = ret

    ret = Instance.check_stop_desktops(sender, desktops)
    if ret == -1:
        logger.error("check desktop instance fail %s " % (desktop_ids))
        return -1
    (stop_desktop, reset_desktop) = ret

    # create desktop task
    task_ids = []
    for desktop_id, desktop in stop_desktop.items():       
        directive = {"desktop": desktop_id}
        task_type= const.TASK_ACTION_STOP_DESKTOP

        if desktop_id in reset_desktop:
            task_type= const.TASK_ACTION_RESET_DESKTOP
            directive["trans_status"] = const.INST_TRAN_STATUS_STOPPING
        
        if "modify_config" in desktop:
            directive["modify_config"] = desktop["modify_config"]

        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive, task_type)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1
        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_delete_desktops(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]

    ret = Instance.check_desktop_instance(sender, desktop_ids)
    if ret < 0:
        logger.error("resource desktop instance fail %s " % desktop_ids)
        return -1
    
    desktops = ret

    # create desktop task
    task_ids = []
    for desktop_id, _ in desktops.items():
        directive = {"desktop": desktop_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1
        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_modify_desktop_attributes(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]

    ret = Instance.check_desktop_instance(sender, desktop_ids)
    if ret == -1:
        logger.error("check start desktop fail %s" % desktop_ids)
        return -1
    desktops = ret

    ret = Instance.check_desktop_modify_attributes(desktops)
    if ret == -1:
        logger.error("check modify desktop fail %s" % desktop_ids)
        return -1
    modify_desktops = ret

    # create desktop task
    task_ids = []
    for desktop_id, desktop in modify_desktops.items():
        directive = {"desktop": desktop_id,
                     "modify_config": desktop.get("modify_config")
                     }
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1
        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

# disk handler
def handle_job_attach_disks(job_id, job):
    
    action = job['directive']['action']
    disk_ids = job['directive']['disks']
    sender = job['directive']["sender"]
    
    ret = Disk.check_disk_volume(sender, disk_ids, True)
    if ret == -1:
        logger.error("check disk volume fail %s" % disk_ids)
        return -1
    disks = ret

    ret = Disk.check_desktop_attach_disks(disks)
    if not ret:
        logger.error("check desktop attach disks fail %s" % disk_ids)
        return -1
    desktop_disk = ret
    if not desktop_disk:
        return 0

    desktop_ids = desktop_disk.keys()
    ret = Instance.check_desktop_instance(sender, desktop_ids)
    if ret == -1:
        logger.error("job check create desktops fail %s" % desktop_ids)
        return -1
    desktops = ret

    # create desktop task
    task_ids = []
    for desktop_id, disks in desktop_disk.items():
        
        desktop = desktops.get(desktop_id)
        if not desktop:
            continue
        
        instance_id = desktop["instance_id"]
        if not instance_id:
            continue
        
        directive = {"desktop": desktop_id, "disks": disks.keys()}

        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1
        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_detach_disks(job_id, job):
    
    action = job['directive']['action']
    disk_ids = job['directive']['disks']
    sender = job['directive']["sender"]
    
    ret = Disk.check_disk_volume(sender, disk_ids)
    if ret == -1:
        logger.error("check disk resource fail %s" % disk_ids)
        return -1
    disks = ret

    ret = Disk.check_desktop_detach_disks(disks)
    if not ret:
        return 0
    desktop_disk = ret

    ret = Instance.check_desktop_instance(sender, desktop_disk.keys())
    if ret < 0:
        logger.error("check desktop instance fail %s" % desktop_disk.keys())
        return -1
    desktops = ret

    # create desktop task
    task_ids = []
    for desktop_id, disks in desktop_disk.items():
        
        desktop = desktops[desktop_id]
        if not desktop:
            continue
        directive = {"desktop": desktop_id, "disks": disks.keys()}

        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_resize_disks(job_id, job):

    action = job['directive']['action']
    disk_ids = job['directive']['disks']
    sender = job['directive']["sender"]

    ret = Disk.check_disk_volume(sender, disk_ids, True)
    if ret == -1:
        logger.error("check disk resource fail %s" % disk_ids)
        return -1
    disks = ret
    
    ret = Disk.check_desktop_resize_disks(disks)
    if not ret:
        return 0
    
    task_disk = ret
    # create desktop task
    task_ids = []
    for disk_id, _ in task_disk.items():
        directive = {"disk": disk_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, disk_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, disk_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_delete_disks(job_id, job):

    action = job['directive']['action']
    disk_ids = job['directive']['disks']
    sender = job['directive']["sender"]
            
    ret = Disk.check_disk_volume(sender, disk_ids)
    if ret == -1:
        logger.error("check  disk volume fail %s" % disk_ids)
        return -1
    
    disks = ret
    
    ret = Disk.check_desktop_delete_disks(disks)
    if not ret:
        return 0

    task_disk = ret
    tasks_ids = []
    # create desktop task
    for disk_id, _ in task_disk.items():
        directive = {"disk": disk_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, disk_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, disk_id))
            return -1
        tasks_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, tasks_ids)

################################# nic handler ##############################

def handle_job_update_desktop_nics(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]

    ret = Instance.check_desktop_instance(sender, desktop_ids)
    if ret < 0:
        logger.error("check desktop instance resource %s invaild" % desktop_ids)
        return -1
    desktops = ret
    
    ret = Nic.check_desktop_update_nic(sender, desktops)
    if ret < 0:
        logger.error("check update desktop nic fail %s " % (desktop_ids))
        return -1
    
    if not ret:
        return 0
    desktop_nic = ret

    # create desktop task
    task_ids = []
    for desktop_id, _ in desktop_nic.items():
        desktop = desktops.get(desktop_id)
        if not desktop:
            continue

        directive = {"desktop": desktop_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

################################# network handler ##############################

def handle_job_create_network(job_id, job):

    network_ids = job['directive']['networks']
    sender = job['directive']["sender"]       
    network_id = network_ids[0]

    with rLock(network_id):
        
        # only managed vxnet need to handle
        ret = Network.check_network_join_router(sender, network_id)
        if not ret:
            logger.error("check network join router fail %s" % (network_id))
            Network.clear_pend_network(network_id)
            return -1
        network = ret

        with ResComm.transition_status(dbconst.TB_DESKTOP_NETWORK, network_id, const.NETWORK_TRANS_STATUS_CREATING):

            ret = Network.network_join_router(sender, network)
            if ret < 0:
                logger.error("job create network %s, %s fail ." % (job_id, network))
                Network.clear_pend_network(network_id)
                return -1

            return 0

def handle_job_delete_networks(job_id, job):

    action = job['directive']['action']
    network_ids = job['directive']['networks']
    sender = job['directive']["sender"]

    ret = Network.check_delete_network(sender, network_ids)
    if ret < 0:
        logger.error("Job[%s] check delete network fail %s" % (action, network_ids))
        return -1

    task_network = ret
    # create desktop task
    task_ids = []
    for network_id, _ in task_network.items():

        directive = {"network": network_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, network_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, network_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

# image 
def handle_job_create_images(job_id, job):

    action = job['directive']['action']
    desktop_image_ids = job['directive']['desktop_images']
    sender = job['directive']["sender"]
        
    # check desktop image vaild
    ret = Image.check_create_desktop_image(sender, desktop_image_ids)
    if ret == -1:
        logger.error("Job Create Image, check image[%s] fail.")
        return -1
    
    desktop_images = ret
    
    # build save create image task
    task_ids = []
    for desktop_image_id, _ in desktop_images.items():
        directive = {"desktop_image": desktop_image_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_image_id, directive)
        if not task_id:
            logger.error("Job[%s] Action [%s], create new task fail %s" % (job_id, action, directive))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_save_images(job_id, job):

    action = job['directive']['action']
    desktop_image_ids = job['directive']['desktop_images']
    sender = job['directive']["sender"]

    # check desktop image vaild
    ret = Image.check_save_desktop_image(sender, desktop_image_ids)
    if ret == -1:
        logger.error("Job save Image, check image[%s] fail." % desktop_image_ids)
        return -1
    desktop_images = ret

    # build save image task
    task_ids = []
    for desktop_image_id, _ in desktop_images.items():

        directive = {"desktop_image": desktop_image_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_image_id, directive)
        if not task_id:
            logger.error("Job[%s] Action [%s], create new task fail %s" % (job_id, action, directive))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_delete_images(job_id, job):
    
    action = job['directive']['action']
    desktop_image_ids = job['directive']['desktop_images']
    sender = job['directive']["sender"]
    
    # create desktop task
    task_ids = []
    for desktop_image_id in desktop_image_ids:
        directive = {"desktop_image": desktop_image_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_image_id, directive)
        if not task_id:
            logger.error("Job[%s] Action [%s], create new task fail %s" % (job_id, action, directive))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_send_desktop_message(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    base64_message = job['directive']['base64_message']
    sender = job['directive']["sender"]

    # create desktop task
    task_ids = []
    for desktop_id in desktop_ids:
        directive = {"desktop": desktop_id, 
                     "base64_message": base64_message}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_send_desktop_notify(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    base64_notify = job['directive']['base64_notify']
    sender = job['directive']["sender"]

    # create desktop task
    task_ids = []
    for desktop_id in desktop_ids:
        directive = {"desktop": desktop_id, 
                     "base64_notify": base64_notify}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_login_desktop(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]
    username = job['directive']['username']
    password = job['directive']['password']
    domain = job['directive']['domain']

    # create desktop task
    task_ids = []
    for desktop_id in desktop_ids:
        directive = {"desktop": desktop_id,
                     "username":username,
                     "password": password,
                     "domain": domain}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_logoff_desktop(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]

    # create desktop task
    task_ids = []
    for desktop_id in desktop_ids:
        directive = {"desktop": desktop_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_add_desktiop_active_directory(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]
    username = job['directive']['username']
    password = job['directive']['password']
    domain = job['directive']['domain']
    ou = job['directive']['ou']

    # create desktop task
    task_ids = []
    for desktop_id in desktop_ids:
        directive = {"desktop": desktop_id,
                     "username":username,
                     "password": password,
                     "domain": domain,
                     "ou": ou}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_modify_guest_server_config(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    sender = job['directive']["sender"]
    guest_server_config = job['directive']['guest_server_config']

    # create desktop task
    task_ids = []
    for desktop_id in desktop_ids:
        directive = {
            "desktop": desktop_id,
            "guest_server_config":guest_server_config
            }
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_send_desktop_hot_keys(job_id, job):

    action = job['directive']['action']
    desktop_ids = job['directive']['desktops']
    keys = job['directive']['keys']
    timeout = job['directive']['timeout']
    time_step = job['directive']['time_step']
    sender = job['directive']["sender"]

    # create desktop task
    task_ids = []
    for desktop_id in desktop_ids:
        directive = {"desktop": desktop_id, "keys": keys, "timeout": timeout, "time_step": time_step}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_deal_desktop_apply_form(job_id, job):

    action = job['directive']['action']
    apply_id = job['directive']['apply_id']
    sender = job['directive'].pop("sender")
    directive = {"apply_id": apply_id}
    directive.update(job['directive'])
    
    # create desktop task
    task_id = ResComm.new_desktop_task(sender, job_id, action, apply_id, directive)

    return ResComm.dispatch_resource_task(job_id, [task_id])

def hanlde_job_create_desktop_snapshots(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    desktop_snapshot_ids = job['directive']['desktop_snapshots']
    sender = job['directive']["sender"]
    snapshot_name = job['directive']['snapshot_name']
    is_full = job['directive']['is_full']
    snapshot_group_snapshot_ids = job['directive']['snapshot_group_snapshot']

    # create snapshot task
    task_ids = []
    for desktop_snapshot_id in desktop_snapshot_ids:
        directive = {"desktop_snapshot": desktop_snapshot_id,"snapshot_name":snapshot_name,"is_full":is_full,"snapshot_group_snapshot":snapshot_group_snapshot_ids}

        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_snapshot_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_snapshot_ids))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids, 1)

def handle_job_apply_desktop_snapshots(job_id, job):

    action = job['directive']['action']
    sender = job['directive']["sender"]
    desktop_snapshot_ids = job['directive']['desktop_snapshots']
    snapshot_group_snapshot_ids = job['directive']['snapshot_group_snapshot']

    # apply snapshot task
    task_ids = []
    for desktop_snapshot_id in desktop_snapshot_ids:
        directive = {"desktop_snapshot": desktop_snapshot_id,"snapshot_group_snapshot":snapshot_group_snapshot_ids}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_snapshot_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_snapshot_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids, 1)

def handle_job_delete_desktop_snapshots(job_id, job):

    action = job['directive']['action']
    sender = job['directive']["sender"]
    desktop_snapshot_ids = job['directive']['desktop_snapshots']
    snapshot_group_snapshot_ids = job['directive']['snapshot_group_snapshot']

    # delete snapshot task
    task_ids = []
    for desktop_snapshot_id in desktop_snapshot_ids:
        directive = {"desktop_snapshot": desktop_snapshot_id, "snapshot_group_snapshot": snapshot_group_snapshot_ids}
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_snapshot_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_snapshot_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_capture_instance_from_desktop_snapshot(job_id, job):

    action = job['directive']['action']
    snapshot_ids = job['directive']['desktop_snapshots']
    sender = job['directive']["sender"]
    image_name = job['directive']['image_name']

    ret = Snapshot.check_capture_instance_from_desktop_snapshot(sender,snapshot_ids)
    if ret < 0:
        logger.error("check capture instance from desktop snapshot fail %s" % snapshot_ids)
        return -1
    snapshots = ret

    # create desktop task
    task_ids = []
    for snapshot_id, snapshot in snapshots.items():

        # Check if the snapshot resource is a instance type
        resource_id = snapshot["resource_id"]
        if not resource_id.startswith("i-"):
            logger.error("resource  must be instance when capture instance from desktop snapshot %s" % snapshot_ids)
            return -1

        directive = {"snapshot": snapshot_id,"image_name":image_name}
        task_id = ResComm.new_desktop_task(sender, job_id, action, snapshot_id, directive)
        if not task_id:
            logger.error("Job[%s] start task fail %s" % (action, snapshot_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids, 1)

def handle_job_create_disk_from_desktop_snapshot(job_id, job):

    action = job['directive']['action']
    snapshot_ids = job['directive']['desktop_snapshots']
    sender = job['directive']["sender"]
    disk_name = job['directive']['disk_name']

    ret = Snapshot.check_create_disk_from_desktop_snapshot(sender,snapshot_ids)
    if ret < 0:
        logger.error("check create disk from desktop snapshot fail %s" % snapshot_ids)
        return -1
    snapshots = ret

    # create desktop task
    task_ids = []
    for snapshot_id, snapshot in snapshots.items():

        # Check if the snapshot resource is a volume type
        resource_id = snapshot["resource_id"]
        if not resource_id.startswith("vol-"):
            logger.error("resource must be volume when create disk from desktop snapshot %s" % snapshot_ids)
            return -1

        directive = {"snapshot": snapshot_id,"disk_name":disk_name}
        task_id = ResComm.new_desktop_task(sender, job_id, action, snapshot_id, directive)
        if not task_id:
            logger.error("Job[%s] start task fail %s" % (action, snapshot_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids, 1)

def handle_job_apply_security_policys(job_id, job):
    
    sender = job['directive']["sender"]
    action = job['directive']['action']
    policy_group_ids = job['directive']['policy_groups']

    # create desktop task
    task_ids = []
    for policy_group_id in policy_group_ids:
        directive = {}
        directive["policy_group"] = policy_group_id

        task_id = ResComm.new_desktop_task(sender, job_id, action, policy_group_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, policy_group_id))
            return -1
        task_ids.append(task_id)

    if not task_ids:
        logger.error("Job[%s] no task %s " % (action, policy_group_id))
        return -1
    
    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_apply_security_ipsets(job_id, job):
    
    sender = job['directive']["sender"]
    action = job['directive']['action']
    security_ipset_ids = job['directive']['security_ipsets']

    # create desktop task
    task_ids = []
    for security_ipset_id in security_ipset_ids:
        directive = {}
        directive["security_ipset"] = security_ipset_id

        task_id = ResComm.new_desktop_task(sender, job_id, action, security_ipset_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, security_ipset_id))
            return -1
        task_ids.append(task_id)

    if not task_ids:
        logger.error("Job[%s] no task %s " % (action, security_ipset_id))
        return -1
    
    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_modify_terminal_management_attributes(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]
    terminal_ids = job['directive']['terminal_id']
    terminal_server_ip = job['directive']['terminal_server_ip']

    # create terminal task
    task_ids = []
    for terminal_id in terminal_ids:
        directive = {"terminal_id": terminal_id,"terminal_server_ip":terminal_server_ip}
        task_id = ResComm.new_desktop_task(sender, job_id, action, terminal_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, terminal_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_restart_terminals(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]
    terminal_ids = job['directive']['terminal_id']

    ret = Terminal.check_terminals(terminal_ids=terminal_ids)
    if ret < 0:
        logger.error("check terminals fail %s" %(terminal_ids))
        return -1
    terminals = ret

    # create terminal task
    task_ids = []
    for terminal_id,terminal in terminals.items():
        terminal_mac = terminal["terminal_mac"]
        directive = {"terminal_id": terminal_id,"terminal_mac":terminal_mac}
        task_id = ResComm.new_desktop_task(sender, job_id, action, terminal_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, terminal_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_stop_terminals(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]
    terminal_ids = job['directive']['terminal_id']

    ret = Terminal.check_terminals(terminal_ids=terminal_ids)
    if ret < 0:
        logger.error("check terminals fail %s" %(terminal_ids))
        return -1
    terminals = ret

    # create terminal task
    task_ids = []
    for terminal_id,terminal in terminals.items():
        terminal_mac = terminal["terminal_mac"]
        directive = {"terminal_id": terminal_id,"terminal_mac":terminal_mac}
        task_id = ResComm.new_desktop_task(sender, job_id, action, terminal_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, terminal_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_execute_workflow_job(job_id, job):
    
    sender = job['directive']["sender"]
    action = job['directive']['action']
    workflow_ids = job['directive']['workflows']
    ctx = context.instance()

    ret = ctx.pgm.get_workflows(workflow_ids, status=[const.WORKFLOW_STATUS_FAIL, const.WORKFLOW_STATUS_PENDING])
    if not ret:
        return 0
    workflows = ret

    task_ids = []
    for workflow_id, _ in workflows.items():

        directive = {"workflow_id": workflow_id}
        task_id = ResComm.new_desktop_task(sender, job_id, action, workflow_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, workflow_id))
            return -1

        task_ids.append(task_id)

    ret = ResComm.dispatch_resource_task(job_id, task_ids,1)
    if ret < 0:
        return -1
    
    return 0

def handle_job_upload_softwares(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]
    software_ids = job['directive']['software_id']

    ret = Software.check_softwares(software_ids=software_ids)
    if ret < 0:
        logger.error("check softwares fail %s" %(software_ids))
        return -1
    softwares = ret

    # create software task
    task_ids = []
    for software_id,software in softwares.items():
        software_name = software["software_name"]
        directive = {"software_id": software_id,"software_name":software_name}
        task_id = ResComm.new_desktop_task(sender, job_id, action, software_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, software_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_upload_file_shares(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]
    file_share_group_file_ids = job['directive']['file_share_group_file_id']
    create_method = job['directive']['create_method']

    ret = FileShare.check_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids)
    if ret < 0:
        logger.error("check file_share_group_files fail %s" %(file_share_group_file_ids))
        return -1
    file_share_group_files = ret

    # create file_share task
    task_ids = []
    for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]
        file_share_group_dn = file_share_group_file["file_share_group_dn"]
        directive = {
                        "file_share_group_file_id": file_share_group_file_id,
                        "file_share_group_file_name":file_share_group_file_name,
                        "file_share_group_dn":file_share_group_dn,
                        "create_method":create_method
                    }
        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_group_file_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_group_file_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids, 1)

def handle_job_download_file_shares(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]
    file_share_group_file_ids = job['directive']['file_share_group_file_id']
    create_method = job['directive']['create_method']

    ret = FileShare.check_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids)
    if ret < 0:
        logger.error("check file_share_group_files fail %s" %(file_share_group_file_ids))
        return -1
    file_share_group_files = ret

    # create file_share task
    task_ids = []
    for file_share_group_file_id,file_share_group_file in file_share_group_files.items():
        file_share_group_file_name = file_share_group_file["file_share_group_file_name"]
        file_share_group_dn = file_share_group_file["file_share_group_dn"]
        file_share_group_file_size = file_share_group_file["file_share_group_file_size"]
        directive = {
                        "file_share_group_file_id": file_share_group_file_id,
                        "file_share_group_file_name":file_share_group_file_name,
                        "file_share_group_dn":file_share_group_dn,
                        "create_method":create_method,
                        "file_share_group_file_size": file_share_group_file_size
                    }
        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_group_file_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_group_file_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids, 1)

def handle_job_change_file_in_file_share_group(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]

    file_share_group_file_ids = job['directive']['file_share_group_file_id']
    new_file_share_group_dn = job['directive']['new_file_share_group_dn']
    change_type = job['directive']['change_type']
    file_save_method = job['directive']['file_save_method']
    repeat_file_ids = job['directive']['repeat_file_ids']
    create_method = job['directive']['create_method']

    ret = FileShare.check_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids)
    if ret < 0:
        logger.error("check file_share_group_files fail %s" %(file_share_group_file_ids))
        return -1
    file_share_group_files = ret

    # create file_share task
    task_ids = []
    for file_share_group_file_id,file_share_group_file in file_share_group_files.items():

        directive = {
            "file_share_group_file_id":file_share_group_file_id,
            "file_share_group_file": file_share_group_file,
            "new_file_share_group_dn": new_file_share_group_dn,
            "change_type": change_type,
            "file_save_method": file_save_method,
            "repeat_file_ids": repeat_file_ids,
            "create_method": create_method
        }

        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_group_file_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_group_file_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_create_file_share_service(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]

    file_share_service_id = job['directive']['file_share_service_id']
    vnas_disk_size = job['directive']['vnas_disk_size']

    ret = FileShare.check_file_share_services(file_share_service_ids=file_share_service_id)
    if ret < 0:
        logger.error("check file_share_service fail %s" %(file_share_service_id))
        return -1
    file_share_services = ret

    # create file_share task
    task_ids = []
    for file_share_service_id,file_share_service in file_share_services.items():

        directive = {
            "file_share_service_id": file_share_service_id,
            "network_id": file_share_service["network_id"],
            "desktop_server_instance_id": file_share_service["desktop_server_instance_id"],
            "private_ip": file_share_service["private_ip"],
            "file_share_service_name": file_share_service["file_share_service_name"],
            "vnas_disk_size":vnas_disk_size,
            "vnas_id": file_share_service["vnas_id"],
            "limit_rate": file_share_service["limit_rate"],
            "limit_conn": file_share_service["limit_conn"],
            "fuser": file_share_service["fuser"],
            "fpw": file_share_service["fpw"]
        }

        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_service_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_service_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids, 1)

def handle_job_load_file_share_service(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]

    file_share_service_id = job['directive']['file_share_service_id']
    vnas_disk_size = job['directive']['vnas_disk_size']

    ret = FileShare.check_file_share_services(file_share_service_ids=file_share_service_id)
    if ret < 0:
        logger.error("check file_share_service fail %s" %(file_share_service_id))
        return -1
    file_share_services = ret

    # create file_share task
    task_ids = []
    for file_share_service_id,file_share_service in file_share_services.items():

        directive = {
            "file_share_service_id": file_share_service_id,
            "network_id": file_share_service["network_id"],
            "desktop_server_instance_id": file_share_service["desktop_server_instance_id"],
            "file_share_service_name": file_share_service["file_share_service_name"],
            "vnas_disk_size":vnas_disk_size,
            "vnas_id": file_share_service["vnas_id"],
            "limit_rate": file_share_service["limit_rate"],
            "limit_conn": file_share_service["limit_conn"],
            "fuser": file_share_service["fuser"],
            "fpw": file_share_service["fpw"]
        }

        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_service_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_service_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids, 1)

def handle_job_delete_file_share_service(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]

    file_share_service_id = job['directive']['file_share_service_id']
    create_method = job['directive']['create_method']

    ret = FileShare.check_file_share_services(file_share_service_ids=file_share_service_id)
    if ret < 0:
        logger.error("check file_share_service fail %s" %(file_share_service_id))
        return -1
    file_share_services = ret

    # create file_share task
    task_ids = []
    for file_share_service_id,file_share_service in file_share_services.items():

        directive = {
            "file_share_service_id": file_share_service_id,
            "file_share_service_instance_id": file_share_service["file_share_service_instance_id"],
            "create_method":create_method
        }

        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_service_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_service_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_refresh_file_share_service(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]

    file_share_service_id = job['directive']['file_share_service_id']
    create_method = job['directive']['create_method']

    ret = FileShare.check_file_share_services(file_share_service_ids=file_share_service_id)
    if ret < 0:
        logger.error("check file_share_service fail %s" %(file_share_service_id))
        return -1
    file_share_services = ret

    # create file_share task
    task_ids = []
    for file_share_service_id, _ in file_share_services.items():

        directive = {
            "file_share_service_id": file_share_service_id,
            "create_method":create_method
        }

        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_service_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_service_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids, 1)

def handle_job_modify_file_share_service(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]

    file_share_service_id = job['directive']['file_share_service_id']
    limit_rate = job['directive']['limit_rate']
    limit_conn = job['directive']['limit_conn']

    ret = FileShare.check_file_share_services(file_share_service_ids=file_share_service_id)
    if ret < 0:
        logger.error("check file_share_service fail %s" %(file_share_service_id))
        return -1
    file_share_services = ret

    # create file_share task
    task_ids = []
    for file_share_service_id, _ in file_share_services.items():

        directive = {
            "file_share_service_id": file_share_service_id,
            "limit_rate":limit_rate,
            "limit_conn":limit_conn
        }

        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_service_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_service_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_delete_file_share_group_files(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]

    file_share_group_file_ids = job['directive']['file_share_group_file_id']
    create_method = job['directive']['create_method']

    ret = FileShare.check_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids)
    if ret < 0:
        logger.error("check file_share_group_files fail %s" %(file_share_group_file_ids))
        return -1
    file_share_group_files = ret

    # create file_share task
    task_ids = []
    for file_share_group_file_id,_ in file_share_group_files.items():

        directive = {
            "file_share_group_file_id": file_share_group_file_id,
            "create_method": create_method
        }

        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_group_file_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_group_file_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_restore_file_share_recycles(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]

    file_share_group_file_ids = job['directive']['file_share_group_file_id']
    create_method = job['directive']['create_method']

    ret = FileShare.check_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids)
    if ret < 0:
        logger.error("check file_share_group_files fail %s" %(file_share_group_file_ids))
        return -1
    file_share_group_files = ret

    # create file_share task
    task_ids = []
    for file_share_group_file_id,_ in file_share_group_files.items():

        directive = {
            "file_share_group_file_id": file_share_group_file_id,
            "create_method": create_method
        }

        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_group_file_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_group_file_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_delete_permanently_file_share_recycles(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]

    file_share_group_file_ids = job['directive']['file_share_group_file_id']
    create_method = job['directive']['create_method']

    ret = FileShare.check_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids)
    if ret < 0:
        logger.error("check file_share_group_files fail %s" %(file_share_group_file_ids))
        return -1
    file_share_group_files = ret

    # create file_share task
    task_ids = []
    for file_share_group_file_id,_ in file_share_group_files.items():

        directive = {
            "file_share_group_file_id": file_share_group_file_id,
            "create_method": create_method
        }

        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_group_file_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_group_file_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_empty_file_share_recycles(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]

    file_share_group_file_ids = job['directive']['file_share_group_file_id']
    create_method = job['directive']['create_method']

    ret = FileShare.check_file_share_group_files(file_share_group_file_ids=file_share_group_file_ids)
    if ret < 0:
        logger.error("check file_share_group_files fail %s" %(file_share_group_file_ids))
        return -1
    file_share_group_files = ret

    # create file_share task
    task_ids = []
    for file_share_group_file_id,_ in file_share_group_files.items():

        directive = {
            "file_share_group_file_id": file_share_group_file_id,
            "create_method": create_method
        }

        task_id = ResComm.new_desktop_task(sender, job_id, action, file_share_group_file_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, file_share_group_file_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_update_component(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]
    component_ids = job['directive']['component_id']

    ret = Component.check_component_versions(component_ids=component_ids)
    if ret < 0:
        logger.error("check component_versions fail %s" %(component_ids))
        return -1
    component_versions = ret

    # create component task
    task_ids = []
    for component_id,component_version in component_versions.items():
        filename = component_version["filename"]
        component_type = component_version["component_type"]
        directive = {"component_id": component_id,"filename":filename,"component_type":component_type}
        task_id = ResComm.new_desktop_task(sender, job_id, action, component_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, component_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_execute_server_component_upgrade(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]
    component_ids = job['directive']['component_id']
    upgrade_hosts = job['directive']['upgrade_hosts']
    ctx = context.instance()
    zone_deploy = ctx.zone_deploy
    localhost_hostname = get_hostname()

    ret = Component.check_component_versions(component_ids=component_ids)
    if ret < 0:
        logger.error("check component_versions fail %s" %(component_ids))
        return -1
    component_versions = ret
    for component_id,component_version in component_versions.items():
        filename = component_version["filename"]
        component_type = component_version["component_type"]

    if const.DEPLOY_TYPE_STANDARD == zone_deploy:
        if localhost_hostname in upgrade_hosts:
            # create task to upgrade vdi host but current localhost
            task_ids = []
            for target_host in upgrade_hosts:
                if localhost_hostname == target_host:
                    continue
                directive = {"component_id": component_id,"filename":filename,"component_type":component_type,"target_host":target_host}
                task_id = ResComm.new_desktop_task(sender, job_id, action, component_id, directive)
                if not task_id:
                    logger.error("Job[%s] create task fail %s" % (action, component_id))
                    return -1

                task_ids.append(task_id)

            ResComm.dispatch_resource_task(job_id, task_ids)

            # create task to upgrade current localhost
            task_ids = []
            target_host = localhost_hostname
            directive = {"component_id": component_id,"filename":filename,"component_type":component_type,"target_host":target_host}
            task_id = ResComm.new_desktop_task(sender, job_id, action, component_id, directive)
            if not task_id:
                logger.error("Job[%s] create task fail %s" % (action, component_id))
                return -1

            task_ids.append(task_id)
            return ResComm.dispatch_resource_task(job_id, task_ids)
        else:
            task_ids = []
            for target_host in upgrade_hosts:
                directive = {"component_id": component_id, "filename": filename, "component_type": component_type,"target_host": target_host}
                task_id = ResComm.new_desktop_task(sender, job_id, action, component_id, directive)
                if not task_id:
                    logger.error("Job[%s] create task fail %s" % (action, component_id))
                    return -1

                task_ids.append(task_id)

            return ResComm.dispatch_resource_task(job_id, task_ids)

    else:
        # create task to firstbox upgrade vdi host
        task_ids = []
        target_host = 'vdi0'
        directive = {"component_id": component_id, "filename": filename, "component_type": component_type,"target_host": target_host}
        task_id = ResComm.new_desktop_task(sender, job_id, action, component_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, component_id))
            return -1

        task_ids.append(task_id)

        return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_execute_client_component_upgrade(job_id, job):

    directive = job['directive']
    action = job['directive']['action']
    sender = job['directive']["sender"]
    terminal_ids = job['directive']['terminal_id']
    upgrade_packet_name = job['directive']['upgrade_packet_name']
    upgrade_packet_path = job['directive']['upgrade_packet_path']
    upgrade_packet_md5 = job['directive']['upgrade_packet_md5']

    ret = Terminal.check_terminals(terminal_ids=terminal_ids)
    if ret < 0:
        logger.error("check terminals fail %s" %(terminal_ids))
        return -1
    terminals = ret

    # create terminal task
    task_ids = []
    for terminal_id,terminal in terminals.items():
        terminal_mac = terminal["terminal_mac"]
        directive = {"terminal_id": terminal_id,
                     "terminal_mac":terminal_mac,
                     "upgrade_packet_name":upgrade_packet_name,
                     "upgrade_packet_path":upgrade_packet_path,
                     "upgrade_packet_md5":upgrade_packet_md5
                     }
        task_id = ResComm.new_desktop_task(sender, job_id, action, terminal_id, directive)

        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, terminal_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_apply_desktop_maintainer(job_id, job):

    action = job['directive']['action']
    sender = job['directive']["sender"]
    desktop_maintainer_id = job['directive']['desktop_maintainer_id']
    desktop_ids = job['directive']['desktops']
    network_value = job['directive']['network_value']
    registry_value = job['directive']['registry_value']

    if desktop_ids and not isinstance(desktop_ids,list):
        desktop_ids = [desktop_ids]

    # create desktop task
    task_ids = []
    for desktop_id in desktop_ids:
        directive = {
                     "desktop_maintainer_id": desktop_maintainer_id,
                     "desktop": desktop_id,
                     "network_value":network_value,
                     "registry_value": registry_value,
                    }
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def handle_job_run_guest_shell_command(job_id, job):

    action = job['directive']['action']
    sender = job['directive']["sender"]
    guest_shell_command_id = job['directive']['guest_shell_command_id']
    desktop_ids = job['directive']['desktops']
    command = job['directive']['command']

    if desktop_ids and not isinstance(desktop_ids,list):
        desktop_ids = [desktop_ids]

    # create desktop task
    task_ids = []
    for desktop_id in desktop_ids:
        directive = {
                     "guest_shell_command_id":guest_shell_command_id,
                     "desktop": desktop_id,
                     "command":command,
                    }
        task_id = ResComm.new_desktop_task(sender, job_id, action, desktop_id, directive)
        if not task_id:
            logger.error("Job[%s] create task fail %s" % (action, desktop_id))
            return -1

        task_ids.append(task_id)

    return ResComm.dispatch_resource_task(job_id, task_ids)

def send_to_push_server(job_id):
    if job_id is None:
        return None

    data = ResComm.job_info(job_id)
    return push_topic_job(data)

class JobHandler():
    ''' desktop dispatch server - job handler '''

    def __init__(self):
        self.handler = {
            # desktop group
            const.JOB_ACTION_CREATE_DESKTOP_GROUP: handle_job_create_desktop_group,
            const.JOB_ACTION_DELETE_DESKTOP_GROUPS: handle_job_delete_desktop_groups,
            const.JOB_ACTION_APPLY_DESKTOP_GROUP: handle_job_apply_desktop_group,
            const.JOB_ACTION_ADD_CITRIX_COMPUTERS: handle_job_add_citrix_computers,
            const.JOB_ACTION_UPDATE_CITRIX_IMAGE: handle_job_update_citrix_image,

            # desktop
            const.JOB_ACTION_LEASE_DESKTOPS: handle_job_lease_desktops,
            const.JOB_ACTION_CREATE_DESKTOPS: handle_job_create_desktops,
            const.JOB_ACTION_DELETE_DESKTOPS: handle_job_delete_desktops,
            const.JOB_ACTION_START_DESKTOPS: handle_job_start_desktops,
            const.JOB_ACTION_RESTART_DESKTOPS: handle_job_restart_desktops,
            const.JOB_ACTION_STOP_DESKTOPS: handle_job_stop_desktops,
            const.JOB_ACTION_RESET_DESKTOPS: handle_job_reset_desktops,
            const.JOB_ACTION_MODIFY_DESKTOP_ATTRIBUTES: handle_job_modify_desktop_attributes,
            
            # disk
            const.JOB_ACTION_DELETE_DISKS: handle_job_delete_disks,
            const.JOB_ACTION_ATTACH_DISKS: handle_job_attach_disks,
            const.JOB_ACTION_DETACH_DISKS: handle_job_detach_disks,
            const.JOB_ACTION_RESIZE_DISKS: handle_job_resize_disks,
            
            # image
            const.JOB_ACTION_CREATE_IMAGES: handle_job_create_images,
            const.JOB_ACTION_SAVE_IMAGES: handle_job_save_images,
            const.JOB_ACTION_DELETE_IMAGES: handle_job_delete_images,
            
            # nic
            const.JOB_ACTION_UPDATE_DESKTOP_NICS: handle_job_update_desktop_nics,

            # network
            const.JOB_ACTION_CREATE_NETWORK: handle_job_create_network,
            const.JOB_ACTION_DELETE_NETWORKS: handle_job_delete_networks,
            
            # vdi
            const.JOB_ACTION_SEND_DESKTOP_HOT_KEYS: handle_job_send_desktop_hot_keys,
            const.JOB_ACTION_SEND_DESKTOP_MESSAGE: handle_job_send_desktop_message,
            const.JOB_ACTION_SEND_DESKTOP_NOTIFY: handle_job_send_desktop_notify,
            const.JOB_ACTION_VDI_LOGIN_DESKTOP: handle_job_login_desktop,
            const.JOB_ACTION_VDI_LOGOFF_DESKTOP: handle_job_logoff_desktop,
            const.JOB_ACTION_VDI_ADD_DESKTOP_ACTIVE_DIRECTORY: handle_job_add_desktiop_active_directory,
            const.JOB_ACTION_VDI_MODIFY_GUEST_SERVER_CONFIG: handle_job_modify_guest_server_config,
            
            # apply and approve
            const.JOB_ACTION_VDI_DEAL_DESKTOP_APPLY_FORM: handle_job_deal_desktop_apply_form,
            
            # snapshot
            const.JOB_ACTION_CREATE_DESKTOP_SNAPSHOTS: hanlde_job_create_desktop_snapshots,
            const.JOB_ACTION_DELETE_DESKTOP_SNAPSHOTS: handle_job_delete_desktop_snapshots,
            const.JOB_ACTION_APPLY_DESKTOP_SNAPSHOTS: handle_job_apply_desktop_snapshots,
            const.JOB_ACTION_CAPTURE_INSTANCE_FROM_DESKTOP_SNAPSHOT: handle_job_capture_instance_from_desktop_snapshot,
            const.JOB_ACTION_CREATE_DISK_FROM_DESKTOP_SNAPSHOT: handle_job_create_disk_from_desktop_snapshot,
            
            # security policy
            const.JOB_ACTION_APPLY_SECURITY_POLICYS: handle_job_apply_security_policys,
            const.JOB_ACTION_APPLY_SECURITY_IPSETS: handle_job_apply_security_ipsets,

            # terminal
            const.JOB_ACTION_MODIFY_TERMINAL_MANAGEMENT_ATTRIBUTTES: handle_job_modify_terminal_management_attributes,
            const.JOB_ACTION_RESTART_TREMINALS: handle_job_restart_terminals,
            const.JOB_ACTION_STOP_TREMINALS: handle_job_stop_terminals,
            
            # workflow
            const.JOB_ACTION_EXECUTE_WORKFLOWS: handle_job_execute_workflow_job,

            # software
            const.JOB_ACTION_UPLOAD_SOFTWARES: handle_job_upload_softwares,

            # file_share
            const.JOB_ACTION_UPLOAD_FILE_SHARES: handle_job_upload_file_shares,
            const.JOB_ACTION_DOWNLOAD_FILE_SHARES: handle_job_download_file_shares,
            const.JOB_ACTION_CHANGE_FILE_IN_FILE_SHARE_GROUP: handle_job_change_file_in_file_share_group,
            const.JOB_ACTION_CREATE_FILE_SHARE_SERVICE: handle_job_create_file_share_service,
            const.JOB_ACTION_LOAD_FILE_SHARE_SERVICE: handle_job_load_file_share_service,
            const.JOB_ACTION_DELETE_FILE_SHARE_SERVICE: handle_job_delete_file_share_service,
            const.JOB_ACTION_REFRESH_FILE_SHARE_SERVICE: handle_job_refresh_file_share_service,
            const.JOB_ACTION_MODIFY_FILE_SHARE_SERVICE: handle_job_modify_file_share_service,
            const.JOB_ACTION_DELETE_FILE_SHARE_GROUP_FILES: handle_job_delete_file_share_group_files,
            const.JOB_ACTION_RESTORE_FILE_SHARE_RECYCLES: handle_job_restore_file_share_recycles,
            const.JOB_ACTION_DELETE_PERMANENTLY_FILE_SHARE_RECYCLES: handle_job_delete_permanently_file_share_recycles,
            const.JOB_ACTION_EMPTY_FILE_SHARE_RECYCLES: handle_job_empty_file_share_recycles,

            # component
            const.JOB_ACTION_UPDATE_COMPONENT: handle_job_update_component,
            const.JOB_ACTION_EXECUTE_SERVER_COMPONENT_UPGRADE: handle_job_execute_server_component_upgrade,
            const.JOB_ACTION_EXECUTE_CLIENT_COMPONENT_UPGRADE: handle_job_execute_client_component_upgrade,

            # desktop_maintainer
            const.JOB_ACTION_APPLY_DESKTOP_MAINTAINER: handle_job_apply_desktop_maintainer,

            # guest_shell_command
            const.JOB_ACTION_RUN_GUEST_SHELL_COMMAND: handle_job_run_guest_shell_command,
        }

    def handle(self, job_id):

        ctx = context.instance()
        job = ctx.pg.get(dbconst.TB_DESKTOP_JOB, job_id)
        if job == None:
            logger.error("invalid job_id [%s]" % job_id)
            return

        set_msg_id(job_id)

        # dispatch job by action
        job['directive'] = json_load(job['directive'])
        
        if ResComm.set_job_working(job) < 0:
            return

        try:
            action = job['directive']['action']
            if action in self.handler:
                # handle job directly
                ret = self.handler[action](job_id, job)
                if ret < 0:
                    ResComm.job_fail(job_id)
                else:
                    ResComm.job_ok(job_id)
            else:
                logger.error("no found job handler %s" % action)
                ResComm.job_fail(job_id)
            if action in const.JOB_ACTION_LIST_NEED_TO_PUSH_SERVER:
                send_to_push_server(job_id)
            return
        except:
            logger.critical("handle job [%s] failed: [%s]" % (job_id, traceback.format_exc()))
            ResComm.job_fail(job_id)
            if action in const.JOB_ACTION_LIST_NEED_TO_PUSH_SERVER:
                send_to_push_server(job_id)
            return

