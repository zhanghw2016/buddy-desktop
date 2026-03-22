import time
import db.constants as dbconst
import constants as const
import traceback
import context
from log.logger import logger
from utils.json import json_load
import resource_common as ResComm
import dispatch_resource.desktop_instance as Instance
import dispatch_resource.desktop_nic as Nic
import dispatch_resource.desktop_disk as Disk
import dispatch_resource.desktop_network as Network
import dispatch_resource.desktop_image as Image
import dispatch_resource.desktop_domain as Domain
import dispatch_resource.desktop_snapshot as Snapshot
import dispatch_resource.desktop_security as Security
import dispatch_resource.desktop_citrix as Citrix
import dispatch_resource.desktop_workflow as Workflow
import dispatch_resource.desktop_common as DeskComm
import dispatch_resource.software as Software
import dispatch_resource.file_share as FileShare
import dispatch_resource.guest as Guest
import dispatch_resource.component as Component
from utils.misc import rLock
from send_request import (
    push_topic_job, 
    send_desktop_server_request,
    send_terminal_server_request
    )
from utils.id_tool import(
    UUID_TYPE_SECURITY_POLICY_SGRS,
)
from common import is_citrix_platform, check_citrix_action, check_citrix_random

def handle_task_create_computer(directive):

    ctx = context.instance()
    sender = directive["sender"]
    desktop_group_id = directive["desktop_group"]
    task_id = directive["task_id"]
    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
    if not desktop_group:
        return -1
    
    desktop_group_name = desktop_group["desktop_group_name"]
    ret = ctx.res.resource_create_instance(sender["zone"], None, desktop_group_name)
    if not ret:
        logger.error("citrix resource create instance fail %s" % desktop_group_name)
        return -1
    (instance_name, job_id) = ret
    ret = Citrix.register_citrix_computer(desktop_group, instance_name)
    if ret < 0:
        logger.error("citrix register citrix computer fail %s" % instance_name)
        return -1
    desktop_id = ret

    with rLock(desktop_id):
        
        ret = Citrix.task_wait_citrix_desktop_done(sender, desktop_id, job_id)
        if ret < 0:
            logger.error("wait citrix desktop job done fail %s" % job_id)
            return -1

        desktops = ctx.pgm.get_desktops(desktop_id)
        if not desktops:
            logger.error("get desktop fail %s" % desktop_id)
            return -1

        desktop = desktops[desktop_id]
        ret = Citrix.update_new_computer(sender, desktop)
        if ret < 0:
            return -1

        disk_configs = desktop_group["disks"]
        if disk_configs:
            ret = Citrix.register_citrix_disks(sender, disk_configs, desktop_id)
            if ret < 0:
                logger.error("register citrix disk fail %s" % disk_configs)
                return -1

        # security policy
        policy_group_id = Security.check_desktop_security_group(desktop_id)
        if policy_group_id:
            Security.set_desktop_to_policy_resource(sender, desktop_id, policy_group_id, const.APPLY_TYPE_APPLY)

        ret = Citrix.citrix_desktop_login(desktop)
        if ret < 0:
            logger.error("send citrix login fail %s" % desktop_id)
            return -1
    
    DeskComm.update_task_resource(task_id, desktop_id)
    
    return 0

def handle_task_update_desktop(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    desktop_id = directive["desktop"]

    with rLock(desktop_id):
        
        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Create Desktop no found Desktop %s" % desktop_id)
            return -1

        with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, const.INST_TRAN_STATUS_UPDATING):
            # check detach disk
            ret = Instance.task_update_desktop(sender, desktop)
            if ret < 0:
                logger.error("task update desktop fail %s" % desktop_id)
                return -1
        
    return 0

def handle_task_lease_desktop(directive):

    ctx = context.instance()
    sender = directive["sender"]
    desktop_id = directive["desktop"]
    trans_status = directive.get("trans_status")
    logger.error("handle_task_lease_desktop %s " % directive)
    if not trans_status:
        trans_status = const.INST_TRAN_STATUS_RESUMING

    with rLock(desktop_id):

        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Create Desktop no found Desktop %s" % desktop_id)
            return -1

        with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, trans_status):

            ret = ctx.res.resource_lease_desktop(sender["zone"], desktop["instance_id"])
            logger.error("resource_lease_desktop %s" % ret)
            if not ret:
                return -1
            
            desktop_info = {
                        "need_update": 0,
                        #"instance_id": '',
                        "status": const.INST_STATUS_RUN,
                        }

            if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: desktop_info}):
                logger.error("delete desktop update fail: %s" % desktop_info)
                return -1
            
    return 0

def handle_task_create_desktop(directive):

    ctx = context.instance()
    sender = directive["sender"]
    desktop_id = directive["desktop"]
    trans_status = directive.get("trans_status")

    if not trans_status:
        trans_status = const.INST_TRAN_STATUS_CREATING

    with rLock(desktop_id):

        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Create Desktop no found Desktop %s" % desktop_id)
            return -1

        with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, trans_status):

            ret = Instance.build_desktop_config(sender, desktop)
            if not ret:
                logger.error("Build desktop [%s] config Fail" % desktop_id)
                return -1
            desktop_config = ret

            # security policy
            policy_group_id = Security.check_desktop_security_group(desktop_id)
            if policy_group_id:
                security_group_id = ctx.pgm.get_base_policy(policy_group_id)
                desktop_config["security_group"] = security_group_id

            # create disk
            ret = Disk.create_desktop_disk(sender, desktop, desktop_config)
            if ret < 0:
                logger.error("task create desktop, create desktop disk fail %s" % desktop_id)
                return -1

            # create instance
            ret = Instance.task_create_desktop(sender, desktop, desktop_config)
            if ret < 0:
                logger.error("Task create desktop fail: %s [%s]" % (desktop_id, desktop_config))
                return -1

            if policy_group_id:
                Security.set_desktop_to_policy_resource(sender, desktop_id, policy_group_id)
            
            if "vxnets" in desktop_config:
                ret = Nic.refresh_desktop_nics(sender, desktop_id)
                if ret < 0:
                    logger.error("refresh desktop %s nic fail" % desktop_id)
                    return -1
            else:
                # attach nics
                ret = Nic.attach_desktop_nics(desktop)
                if ret < 0:
                    logger.error("Task create desktop, attach desktop nic fail %s" % desktop_id)
                    return -1

        Domain.desktop_domain(desktop)

    return 0

def handle_task_start_desktop(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    desktop_id = directive["desktop"]
    action = directive["action"]

    with rLock(desktop_id):
        
        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Start Desktop no found Desktop %s" % desktop_id)
            return -1

        with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, const.INST_TRAN_STATUS_STARTING):
            
            if check_citrix_random(ctx, sender["zone"], desktop):
                ret = Disk.reset_desktop_disk(sender, desktop)
                if ret < 0:
                    logger.error("delete desktop disk fail %s" % desktop_id)
                    return -1

            ret =  Instance.check_modify_desktop_attributes(sender, desktop, resume_status=False)
            if ret < 0:
                return -1

            ret = Instance.task_start_desktop(sender, desktop)
            if ret < 0:
                logger.error("Task start[%s] desktop fail" % (desktop_id))
                return -1
            
            if check_citrix_action(ctx, sender["zone"], desktop):
                ret = Citrix.sync_citrix_desktop_info(sender, desktop_id)
                if ret < 0:
                    logger.error("Task action[%s] update restart computer fail:%s " % (action, desktop_id))
                    return -1
            
            if check_citrix_random(ctx, sender["zone"], desktop):

                desktop = ctx.pgm.get_desktop(desktop_id)
                if not desktop:
                    logger.error("Start Desktop no found Desktop %s" % desktop_id)
                    return -1

                ret = Disk.reset_desktop_disk(sender, desktop, is_create=True)
                if ret < 0:
                    logger.error("delete desktop disk fail %s" % desktop_id)
                    return -1

    return 0

def handle_task_reset_desktop(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    desktop_id = directive["desktop"]
    trans_status = directive.get("trans_status", const.INST_TRAN_STATUS_RESETTING)
    
    with rLock(desktop_id):

        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Start Desktop no found Desktop %s" % desktop_id)
            return -1

        with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, trans_status):

            is_running = False
            if trans_status in [const.INST_TRAN_STATUS_RESETTING]:
                status = desktop["status"]
                if status == const.INST_STATUS_RUN:
                    is_running = True
            elif trans_status in [const.INST_TRAN_STATUS_RESTARTING]:
                is_running = True
            elif trans_status in [const.INST_TRAN_STATUS_STOPPING]:
                is_running = False
    
            ret = Instance.task_reset_desktop(sender, desktop, is_running)
            if ret < 0:
                logger.error("Task reset desktop fail:%s " % (desktop_id))
                return -1

    return 0

def handle_task_restart_desktop(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    desktop_id = directive["desktop"]
    action = directive["action"]
    
    with rLock(desktop_id):

        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Start Desktop no found Desktop %s" % desktop_id)
            return -1
    
        with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, const.INST_TRAN_STATUS_RESTARTING):

            if check_citrix_random(ctx, sender["zone"], desktop):
                
                ret = Instance.task_stop_desktop(sender, desktop)
                if ret < 0:
                    logger.error("delete desktop disk fail %s" % desktop_id)
                    return -1

                ret = Disk.reset_desktop_disk(sender, desktop)
                if ret < 0:
                    logger.error("delete desktop disk fail %s" % desktop_id)
                    return -1
            
                desktop = ctx.pgm.get_desktop(desktop_id)
                if not desktop:
                    logger.error("Start Desktop no found Desktop %s" % desktop_id)
                    return -1
            
            ret =  Instance.check_modify_desktop_attributes(sender, desktop, resume_status=False)
            if ret < 0:
                return -1

            inst_status = desktop["status"]
            if inst_status == const.INST_STATUS_RUN:
                ret = Instance.task_restart_desktop(sender, desktop)
                if ret < 0:
                    logger.error("Task action[%s] desktop fail:%s " % (action, desktop_id))
                    return -1
            elif inst_status == const.INST_STATUS_STOP:
                ret = Instance.task_start_desktop(sender, desktop)
                if ret < 0:
                    logger.error("Task action[%s] desktop fail:%s " % (action, desktop_id))
                    return -1
            
            if check_citrix_action(ctx, sender["zone"], desktop):
                ret = Citrix.sync_citrix_desktop_info(sender, desktop_id)
                if ret < 0:
                    logger.error("Task action[%s] update restart computer fail:%s " % (action, desktop_id))
                    return -1

            if check_citrix_random(ctx, sender["zone"], desktop):

                desktop = ctx.pgm.get_desktop(desktop_id)
                if not desktop:
                    logger.error("Start Desktop no found Desktop %s" % desktop_id)
                    return -1

                ret = Disk.reset_desktop_disk(sender, desktop, is_create=True)
                if ret < 0:
                    logger.error("delete desktop disk fail %s" % desktop_id)
                    return -1

    return 0

def handle_task_modify_desktop_attributes(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    action = directive["action"]
    desktop_id = directive["desktop"]
    modify_config = directive.get("modify_config")
    
    with rLock(desktop_id):

        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Modify Desktop no found Desktop %s" % desktop_id)
            return -1
        if modify_config:
            desktop["modify_config"] = modify_config
    
        with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, const.INST_TRAN_STATUS_UPDATING):
    
            ret = Instance.task_modify_desktop_attributes(sender, desktop)
            if ret < 0:
                logger.error("Task action[%s] desktop fail:%s " % (action, desktop_id))
                return -1
            
            ret = Instance.task_update_desktop(sender, desktop)
            if ret < 0:
                logger.error("modify desktop, update desktop fail %s" % desktop_id)
                return -1

    return 0

def handle_task_stop_desktop(directive):
    
    '''
    1. stop instance
    2. resize volume
    3. modify/resize instance attributes
    '''
    ctx = context.instance()
    sender = directive["sender"]
    desktop_id = directive["desktop"]
    expect_status = directive.get("expect_status")
    modify_config = directive.get("modify_config")

    with rLock(desktop_id):

        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Start Desktop no found Desktop %s" % desktop_id)
            return -1
        
        with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, const.INST_TRAN_STATUS_STOPPING):
    
            ret = Instance.task_stop_desktop(sender, desktop)
            if ret < 0:
                logger.error("task stop desktop fail: %s" % desktop_id)
                return -1
            
            if is_citrix_platform(ctx, sender["zone"]):
                ret = Citrix.sync_citrix_desktop_info(sender, desktop_id)
                if ret < 0:
                    logger.error("stop desktop update compute fail %s" % desktop_id)
                    return -1

                return 0
            
            # check desktop volume to resize
            ret = Disk.resize_desktop_disks(sender, desktop)
            if ret < 0:
                logger.error("resize desktop disk fail %s" % desktop_id)
                return -1

            desktop = ctx.pgm.get_desktop(desktop_id)
            if not desktop:
                logger.error("Start Desktop no found Desktop %s" % desktop_id)
                return -1
    
            if modify_config:
                desktop["modify_config"] = modify_config
            # check destop modify attributes
            ret = Instance.task_modify_desktop_attributes(sender, desktop)
            if ret < 0:
                logger.error("Task action desktop fail:%s " % (desktop_id))
                return -1
            
            if expect_status and expect_status == const.INST_STATUS_RUN:
                ret = Instance.task_start_desktop(sender, desktop)
                if ret < 0:
                    logger.error("Task start[%s] desktop fail:%s " % (desktop_id))
                    return -1
    return 0

def handle_task_delete_desktop(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    desktop_id = directive["desktop"]

    # delete desktop full_backup_chain if desktop full_backup_chain is exist
    ret = Snapshot.check_snapshot_ids_by_desktop_id(sender, desktop_id)
    if ret:
        snapshot_ids = ret
        ret = Snapshot.delete_desktop_full_backup_chain(sender, snapshot_ids)
        if ret < 0:
            logger.error("delete desktop_full_backup_chain fail %s" % (snapshot_ids))
            return -1
    
    with rLock(desktop_id):

        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Start Desktop no found Desktop %s" % desktop_id)
            return -1
    
        with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, const.INST_TRAN_STATUS_TERMINATING):

            ret = Instance.task_delete_instance(sender, desktop)
            if ret < 0:
                logger.error("task delete desktop fail[%s]" % desktop_id)
                return -1

            ret = Disk.delete_desktop_disks(sender, desktop)
            if ret < 0:
                logger.error("delete desktop disk fail %s" % desktop_id)
                return -1
    
        ret = Instance.clear_desktop_info(desktop)
        if ret < 0:
            logger.error("task delete desktop, delete desktop info fail %s " % desktop_id)
            return -1

    return 0

# disk
def handle_task_attach_disks(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    desktop_id = directive["desktop"]
    disk_ids = directive["disks"]
        
    with rLock(desktop_id):

        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Start Desktop no found Desktop %s" % desktop_id)
            return -1
        
        with ResComm.transition_status(dbconst.TB_DESKTOP_DISK, disk_ids, const.DISK_TRAN_STATUS_ATTACHING):

            ret = Disk.resize_desktop_disks(sender, desktop, disk_ids)
            if ret < 0:
                logger.error("task resize disk fail[%s]" % disk_ids)
                return -1
        
            ret = Disk.attach_desktop_disks(sender, desktop, disk_ids)
            if ret < 0:
                logger.error("task attach disk fail[%s]" % disk_ids)
                return -1

    return 0

def handle_task_detach_disks(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    desktop_id = directive["desktop"]
    disk_ids = directive["disks"]

    with rLock(desktop_id):

        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Start Desktop no found Desktop %s" % desktop_id)
            return -1

        with ResComm.transition_status(dbconst.TB_DESKTOP_DISK, disk_ids, const.DISK_TRAN_STATUS_DETACHING):
    
            ret = Disk.detach_desktop_disks(sender, desktop, disk_ids)
            if ret < 0:
                logger.error("task detach disk fail[%s]" % disk_ids)
                return -1
    
            ret = Disk.resize_desktop_disks(sender, desktop, disk_ids)
            if ret < 0:
                logger.error("task resize disk fail[%s]" % disk_ids)
                return -1

    return 0

def handle_task_resize_disk(directive):

    ctx = context.instance()
    sender = directive["sender"]
    disk_id = directive["disk"]

    with rLock(disk_id):
        
        disks = ctx.pgm.get_disks(disk_id)
        if not disks:
            return -1
        
        with ResComm.transition_status(dbconst.TB_DESKTOP_DISK, disk_id, const.DISK_TRAN_STATUS_RESIZING):
            ret = Disk.resize_volumes(sender, disks)
            if ret < 0:
                logger.error("task resize disk fail[%s]" % disk_id)
                return -1

    return 0

def handle_task_delete_disk(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    disk_id = directive["disk"]

    with rLock(disk_id):
        
        disks = ctx.pgm.get_disks(disk_id)
        if not disks:
            return -1
    
        with ResComm.transition_status(dbconst.TB_DESKTOP_DISK, disk_id, const.DISK_TRAN_STATUS_DELETING):
    
            ret = Disk.delete_volumes(sender, disks)
            if ret < 0:
                logger.error("task delete disk fail[%s]" % disk_id)
                return -1
        
        ctx.pg.delete(dbconst.TB_DESKTOP_DISK, disk_id)
        from api.user.resource_user import del_user_from_resource
        del_user_from_resource(ctx, disk_id)
        
    return 0

# task nic
def handle_task_update_desktop_nic(directive):
    
    ctx = context.instance()
    desktop_id = directive["desktop"]
    
    with rLock(desktop_id):

        desktop = ctx.pgm.get_desktop(desktop_id)
        if not desktop:
            logger.error("Start Desktop no found Desktop %s" % desktop_id)
            return -1

        with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, const.STATUS_UPDATING):
    
            ret = Nic.apply_desktop_nics(desktop)
            if ret < 0:
                logger.error("Task update desktop, attach/detach nic fail [%s]" % (desktop_id))
                return -1

    return 0

def handle_task_delete_network(directive):
    
    sender = directive["sender"]
    ctx = context.instance()
    network_id = directive["network"]
    
    with rLock(network_id):

        networks = ctx.pgm.get_networks(network_id, const.NETWORK_TYPE_MANAGED)
        if not networks:
            logger.error("check delete network, get network fail %s " % network_id)
            return -1
        
        network = networks[network_id]
        with ResComm.transition_status(dbconst.TB_DESKTOP_NETWORK, network_id, const.STATUS_DELETING):
           
            ret = Network.delete_managed_network(sender, network)
            if ret < 0:
                logger.error("delete managed network fail %s " % network_id)
                return -1
        
        ctx.pg.delete(dbconst.TB_DESKTOP_NETWORK, network_id)
        ctx.pg.base_delete(dbconst.TB_ZONE_USER_SCOPE, {"resource_id": network_id})
    
    return 0

def handle_task_create_image(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    desktop_image_id = directive["desktop_image"]
    
    with rLock(desktop_image_id):
    
        desktop_images = ctx.pgm.get_desktop_images(desktop_image_id)
        if not desktop_images:
            logger.error("check desktop image[%s] fail." % desktop_image_id)
            return -1
        
        desktop_image = desktop_images[desktop_image_id]
        with ResComm.transition_status(dbconst.TB_DESKTOP_IMAGE, desktop_image_id, const.IMG_TRAN_STATUS_CREATING):
            
            image_ret = 0
            ret = Image.create_desktop_image(sender, desktop_image)
            if ret < 0:
                logger.error("task create image fail: %s" % (desktop_image_id))
                image_ret = ret
    
            if image_ret == 0:
                ret = Citrix.refresh_image_nics(sender, desktop_image_id)
                if ret < 0:
                    logger.error("refresh citrix desktop %s nic fail" % desktop_image_id)
                    return -1
                return 0
                
        Image.clear_desktop_image_info(desktop_image_id)

    return -1

def handle_task_save_image(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    desktop_image_id = directive["desktop_image"]
    
    with rLock(desktop_image_id):
    
        desktop_images = ctx.pgm.get_desktop_images(desktop_image_id)
        if not desktop_images:
            logger.error("check desktop image[%s] fail." % desktop_image_id)
            return -1
        desktop_image = desktop_images[desktop_image_id]
        with ResComm.transition_status(dbconst.TB_DESKTOP_IMAGE, desktop_image_id, const.IMG_TRAN_STATUS_SAVING):
    
            ret = Image.save_desktop_image(sender, desktop_image)
            if ret < 0:
                logger.error("task save image fail: %s" % (desktop_image_id))
                return -1
           
            ret = ctx.res.resource_terminate_instances(sender["zone"], desktop_image, const.PLATFORM_TYPE_QINGCLOUD)
            if not ret:
                logger.error("delete desktop image instance fail %s" % desktop_image["instance_id"])
                return -1
            
            sender = {"zone": desktop_image["zone"]}
            Nic.clear_resource_nic(sender, desktop_image_id)
    
            update_info = {
                            "instance_id": '',
                            "inst_status": '',
                            "cpu": 0,
                            "memory": 0,
                            "instance_class": 0
                          }
            ret = Image.update_desktop_image(desktop_image_id, update_info)
            if ret < 0:
                logger.error("update desktop_image fail %s" % desktop_image_id)
                return -1 

            return 0
        
def handle_task_delete_image(directive):
    
    ctx = context.instance()
    sender = directive["sender"]
    desktop_image_id = directive["desktop_image"]
    
    with rLock(desktop_image_id):
    
        desktop_images = ctx.pgm.get_desktop_images(desktop_image_id)
        if not desktop_images:
            logger.error("check desktop image[%s] fail." % desktop_image_id)
            return -1
        desktop_image = desktop_images[desktop_image_id]

        with ResComm.transition_status(dbconst.TB_DESKTOP_IMAGE, desktop_image_id, const.IMG_TRAN_STATUS_DELETING):
    
            ret = Image.delete_desktop_image(sender, desktop_image)
            if ret < 0:
                logger.error("task delete image fail: %s" % (desktop_image_id))
                ctx.pg.delete(dbconst.TB_DESKTOP_IMAGE, desktop_image_id)
                ctx.pg.base_delete(dbconst.TB_ZONE_USER_SCOPE, {"resource_id": desktop_image_id})
                return -1
    
        ctx.pg.delete(dbconst.TB_DESKTOP_IMAGE, desktop_image_id)
        ctx.pg.base_delete(dbconst.TB_ZONE_USER_SCOPE, {"resource_id": desktop_image_id})

    return 0

def handle_task_send_desktop_hot_keys(directive):
    
    sender = directive["sender"]
    desktop_id = directive["desktop"]
    
    keys = directive["keys"]
    timeout = directive["timeout"]
    time_step = directive["time_step"]
    
    ret = Instance._send_desktop_hot_keys(sender, desktop_id, keys, timeout, time_step)
    if ret < 0:
        return -1
    
    return 0

def handle_task_send_desktop_message(directive):
    
    sender = directive["sender"]
    desktop_id = directive["desktop"]
    base64_message = directive["base64_message"]
    
    ret = Instance._send_desktop_message(sender, desktop_id, base64_message)
    if ret < 0:
        return -1
    
    return 0

def handle_task_send_desktop_notify(directive):
    ctx = context.instance()
    desktop_id = directive["desktop"]
    base64_notify = directive['base64_notify']
    
    ips = [] 
    nics = ctx.pgm.get_nics(desktop_ids = [desktop_id])
    if not nics:
        logger.error("desktop [%s] have no nics.")
        return -1
    for _,nic in nics.items():
        ips.append(nic["private_ip"])

    req = {
        "action": const.REQUEST_VDHOST_SERVER_NOTIFY,
        "desktop_id": desktop_id,
        "desktop_ips": ips,
        "params":{
            "base64_notify": base64_notify
            }
        }
    return Guest.send_desktop_notify(req)

def handle_task_login_desktop(directive): 
    ctx = context.instance()
    desktop_id = directive["desktop"]
    username = directive["username"]
    password = directive['password']
    domain = directive['domain']
    
    ips = [] 
    nics = ctx.pgm.get_nics(desktop_ids = [desktop_id])
    if not nics:
        logger.error("desktop [%s] have no nics.")
        return -1
    for _,nic in nics.items():
        ips.append(nic["private_ip"])

    req = {
        "action": const.REQUEST_VDHOST_SERVER_LOGIN,
        "desktop_id": desktop_id,
        "desktop_ips": ips,
        "params":{
            "username": username,
            "password": password,
            "domain": domain
            }
        }
    return Guest.desktop_login(req)

def handle_task_logoff_desktop(directive): 
    ctx = context.instance()
    desktop_id = directive["desktop"]
    
    ips = [] 
    nics = ctx.pgm.get_nics(desktop_ids = [desktop_id])
    if not nics:
        logger.error("desktop [%s] have no nics.")
        return -1
    for _,nic in nics.items():
        ips.append(nic["private_ip"])

    req = {
        "action": const.REQUEST_VDHOST_SERVER_LOGOFF,
        "desktop_id": desktop_id,
        "desktop_ips": ips,
        "params":{}
        }
    return Guest.logoff(req)

def handle_task_add_desktiop_active_directory(directive):
    ctx = context.instance()
    desktop_id = directive["desktop"]
    username = directive["username"]
    password = directive['password']
    domain = directive['domain']
    ou = directive['ou']

    ips = [] 
    nics = ctx.pgm.get_nics(desktop_ids = [desktop_id])
    if not nics:
        logger.error("desktop [%s] have no nics.")
        return -1
    for _,nic in nics.items():
        ips.append(nic["private_ip"])
    req = {
        "action": const.REQUEST_VDHOST_SERVER_ADD_AD,
        "desktop_id": desktop_id,
        "desktop_ips": ips,
        "params":{
            "username": username,
            "password": password,
            "domain": domain,
            "ou": ou
            }
        }
    return Guest.add_active_directory(req)

def handle_task_modify_guest_server_config(directive):
    ctx = context.instance()
    desktop_id = directive["desktop"]
    guest_server_config = directive["guest_server_config"]

    ips = [] 
    nics = ctx.pgm.get_nics(desktop_ids = [desktop_id])
    if not nics:
        logger.error("desktop [%s] have no nics.")
        return -1
    for _,nic in nics.items():
        ips.append(nic["private_ip"])
    req = {
        "action": const.REQUEST_VDHOST_SERVER_MODIFY_SERVER_CONFIG,
        "desktop_id": desktop_id,
        "desktop_ips": ips,
        "params":{
            "guest_server_config": guest_server_config
            }
        }
    return Guest.modify_server_config(req)

def handle_task_deal_desktop_apply_form(directive):
    create_type = directive["create_type"]
    apply_id = directive["apply_id"]
    job_id = None
    job = None
    if create_type == const.APPLY_DESKTOP_TYPE_APPEND:
        req = {"type": "internal",
                   "params": {
                       "action": const.ACTION_VDI_ATTACH_USER_TO_DESKTOP_GROUP,
                       'desktop_group': directive['desktop_group'],
                       'users': directive["users"],
                       "zone": directive["zone"]
                       }
                   }
        ret = send_desktop_server_request(req)
        if ret is None or ret.get("ret_code", -1)!=0:
            logger.error("send desktop request action ACTION_VDI_ATTACH_USER_TO_DESKTOP_GROUP error.")
            ResComm.update_apply_form_status(apply_id, const.APPLY_FORM_STATUS_CREATED)
            return -1
        job_id = ret.get("job_id")
            
    elif create_type == const.APPLY_DESKTOP_TYPE_CREATE:
        logger.info("unsupport create single desktop")
    else:
        logger.error("create_type error.")
        ResComm.update_apply_form_status(apply_id, const.APPLY_FORM_STATUS_CREATED)
        return -1
    
    end_time = time.time() + 600

    while time.time() < end_time:

        req = {
            "type":"internal",
            "params":{
                "action": const.ACTION_VDI_DESCRIBE_DESKTOP_JOBS,
                "jobs": [job_id],
                "zone": directive["zone"]
            },
        }
        ret = send_desktop_server_request(req)
        if ret is None or ret.get("ret_code", -1) != 0:
            logger.error("wait job timeout.[%s][%s]" % (ret, job_id))
            return -1

        job_set = ret["desktop_job_set"]
        if not job_set:
            logger.error("describe jobs none.[%s][%s]" % (ret, job_id))
            return -1

        job = job_set[0]
        status = job["status"]

        if status in [const.JOB_STATUS_PEND, const.JOB_STATUS_WORKING]:
            time.sleep(5)
            continue

        if status in [const.JOB_STATUS_SUCC]:
            break
        else:
            break
    
    if create_type == const.APPLY_DESKTOP_TYPE_CREATE:
        desktop_id = job["resource_ids"]
        usb_policy = None
        if directive.get("usbredir", -1) == 1:
            if directive.get("usb_policy"):
                usb_policy = directive["usb_policy"]
            else:
                usb_policy = const.USB_POLICY_DEFAULT_ENABLE
        else:
            usb_policy = const.USB_POLICY_DEFAULT_DISABLE

        for policy in usb_policy:
            req = {
                "type":"internal",
                "params":{
                    "action": const.ACTION_VDI_CREATE_USB_PROLICY,
                    "zone": directive["zone"],
                    "object_id": desktop_id,
                    "allow": policy["allow"],
                    "class_id": policy["class_id"],
                    "vendor_id": policy["vendor_id"],
                    "priority": policy["priority"],
                    "product_id": policy["product_id"],
                    "policy_type": policy["policy_type"],
                },
            }
            ret = send_desktop_server_request(req)
            if ret is None or ret.get("ret_code", -1) != 0:
                logger.error("create usb policy error")
                req = {
                    "type":"internal",
                    "params":{
                        "action": const.ACTION_VDI_DELETE_DESKTOPS,
                        "zone": directive["zone"],
                        "desktops": [desktop_id]
                        }
                }
                ret = send_desktop_server_request(req)
                if ret is None or ret.get("ret_code", -1) != 0:
                    logger.error("wait job timeout.[%s][%s]" % (ret, job_id))

                ResComm.update_apply_form_status(apply_id, const.APPLY_FORM_STATUS_CREATED)
                return -1

    ResComm.update_apply_form_status(apply_id, const.APPLY_FORM_STATUS_PASSED, resource_id=job["resource_ids"])
    return 0

def hanlde_task_create_desktop_snapshot(directive):

    sender = directive["sender"]
    desktop_snapshot_id = directive["desktop_snapshot"]
    snapshot_name = directive["snapshot_name"]
    is_full = directive["is_full"]
    snapshot_group_snapshot_id = directive["snapshot_group_snapshot"]
    snapshot_group_id = None

    # check resource_ids
    ret = Snapshot.check_snapshot_resource_ids(sender, desktop_snapshot_id)
    if ret < 0:
        logger.error("get snapshot resource_ids fail %s" % (desktop_snapshot_id))
        return -1
    resource_ids = ret

    # check is_full
    ret = Snapshot.check_snapshot_is_full(sender, desktop_snapshot_id,resource_ids,is_full)
    if ret < 0:
        logger.error("get snapshot is_full fail %s" % (desktop_snapshot_id))
        return -1
    (is_full, oldest_full_backup_chain) = ret

    if snapshot_group_snapshot_id:
        # update snapshot_group_snapshot db
        res_snapshot = {"status": "pending","transition_status":"creating"}
        ret = Snapshot.update_snapshot_group_snapshot(sender, res_snapshot,snapshot_group_snapshot_id)
        if ret < 0:
            logger.error("update snapshot group snapshot fail %s" %(snapshot_group_snapshot_id))
            return -1

        snapshot_group_id = Snapshot.get_snapshot_group_id(snapshot_group_snapshot_ids=snapshot_group_snapshot_id)
        if snapshot_group_id:
            # update snapshot_group db
            res_snapshot = {"status": "backuping"}
            ret = Snapshot.update_snapshot_group(sender, res_snapshot,snapshot_group_id)
            if ret < 0:
                logger.error("update snapshot group fail %s" %(snapshot_group_id))
                return -1

    # CreateSnapshots
    ret = Snapshot.task_create_desktop_snapshot(sender, resource_ids, snapshot_name, is_full)
    if ret < 0:
        logger.error("task create desktop snapshot fail %s " %(resource_ids))
        return -1
    (snapshot_ids, job_id) = ret
    
    if isinstance(job_id,list):
        job_id = job_id[0]

    # task register_desktop_snapshots
    for snapshot_id in snapshot_ids:
        ret = Snapshot.task_register_desktop_snapshots(sender, desktop_snapshot_id,snapshot_id,snapshot_group_snapshot_id)
        if ret < 0:
            logger.error("task register desktop snapshot fail %s" %(snapshot_id))
            return -1

    with rLock(snapshot_ids):

        ret = Snapshot.task_wait_create_desktop_snapshot_done(sender, snapshot_ids, job_id,snapshot_group_snapshot_id)
        if ret < 0:
            logger.error("task wait create desktop snapshot done fail %s" % (snapshot_ids))
            ret = Snapshot.delete_desktop_snapshots(sender, snapshot_ids)
            if ret < 0:
                logger.error("delete desktop snapshot db fail %s" % snapshot_ids)
                return -1

            if snapshot_group_id:
                # update snapshot_group db
                res_snapshot = {"status": "normal"}
                ret = Snapshot.update_snapshot_group(sender, res_snapshot, snapshot_group_id)
                if ret < 0:
                    logger.error("update snapshot group fail %s" % (snapshot_group_id))
                    return -1

                # update snapshot_group_snapshot db
                res_snapshot = {"status": "available", "transition_status": ""}
                ret = Snapshot.update_snapshot_group_snapshot(sender, res_snapshot, snapshot_group_snapshot_id)
                if ret < 0:
                    logger.error("update snapshot group snapshot fail %s" % (snapshot_group_snapshot_id))
                    return -1

            return -1

        # delete oldest full_backup_chain if oldest_full_backup_chain is exist
        ret = Snapshot.delete_oldest_full_backup_chain(sender,oldest_full_backup_chain)
        if ret < 0:
            logger.error("delete oldest_full_backup_chain fail %s" % (oldest_full_backup_chain))
            return -1

    return 0

def handle_task_apply_desktop_snapshot(directive):

    sender = directive["sender"]
    desktop_snapshot_id = directive["desktop_snapshot"]
    snapshot_group_snapshot_id = directive["snapshot_group_snapshot"]
    snapshot_group_id = None
    # # check snapshot_ids
    ret = Snapshot.check_snapshot_ids(sender, desktop_snapshot_id)
    if ret < 0:
        logger.error("get desktop snapshot snapshot_ids fail %s" % (desktop_snapshot_id))
        return -1
    snapshot_ids = ret

    if snapshot_group_snapshot_id:
        # update snapshot_group_snapshot db
        res_snapshot = {"status": "available","transition_status":"applying"}
        ret = Snapshot.update_snapshot_group_snapshot(sender, res_snapshot,snapshot_group_snapshot_id)
        if ret < 0:
            logger.error("update snapshot group snapshot fail %s" %(snapshot_group_snapshot_id))
            return -1

        snapshot_group_id = Snapshot.get_snapshot_group_id(snapshot_group_snapshot_ids=snapshot_group_snapshot_id)
        if snapshot_group_id:
            # update snapshot_group db
            res_snapshot = {"status": "rollback"}
            ret = Snapshot.update_snapshot_group(sender, res_snapshot,snapshot_group_id)
            if ret < 0:
                logger.error("update snapshot group fail %s" %(snapshot_group_id))
                return -1
    time.sleep(5)

    with rLock(snapshot_ids):

        ret = Snapshot.task_wait_apply_desktop_snapshot_done(sender, snapshot_ids,snapshot_group_snapshot_id)
        if ret < 0:
            logger.error("task wait apply desktop snapshot done fail %s" % (snapshot_ids))

            if snapshot_group_id:
                # update snapshot_group db
                res_snapshot = {"status": "normal"}
                ret = Snapshot.update_snapshot_group(sender, res_snapshot, snapshot_group_id)
                if ret < 0:
                    logger.error("update snapshot group fail %s" % (snapshot_group_id))
                    return -1

                # update snapshot_group_snapshot db
                res_snapshot = {"status": "available", "transition_status": ""}
                ret = Snapshot.update_snapshot_group_snapshot(sender, res_snapshot, snapshot_group_snapshot_id)
                if ret < 0:
                    logger.error("update snapshot group snapshot fail %s" % (snapshot_group_snapshot_id))
                    return -1

            return -1

    return 0

def handle_task_delete_desktop_snapshot(directive):

    sender = directive["sender"]
    desktop_snapshot_id = directive["desktop_snapshot"]
    snapshot_group_snapshot_id = directive["snapshot_group_snapshot"]

    # # check snapshot_ids
    ret = Snapshot.check_snapshot_ids(sender, desktop_snapshot_id)
    if ret < 0:
        logger.error("get desktop snapshot snapshot_ids fail %s" % (desktop_snapshot_id))
        return -1
    snapshot_ids = ret

    if snapshot_group_snapshot_id:
        # update snapshot_group_snapshot db
        res_snapshot = {"status": "available","transition_status":"deleting"}
        ret = Snapshot.update_snapshot_group_snapshot(sender, res_snapshot,snapshot_group_snapshot_id)
        if ret < 0:
            logger.error("update snapshot group snapshot fail %s" %(snapshot_group_snapshot_id))
            return -1

    with rLock(snapshot_ids):

        ret = Snapshot.task_wait_delete_desktop_snapshot_done(sender, snapshot_ids,snapshot_group_snapshot_id)
        if ret < 0:
            logger.error("task wait delete desktop snapshot done fail %s" % (snapshot_ids))
            return -1

    return 0

def handle_task_capture_instance_from_desktop_snapshot(directive):

    sender = directive["sender"]
    snapshot_id = directive["snapshot"]
    image_name = directive["image_name"]

    with rLock(snapshot_id):

        with ResComm.transition_status(dbconst.TB_DESKTOP_SNAPSHOT, snapshot_id, const.INST_TRAN_STATUS_STARTING):
            ret = Snapshot.task_capture_instance_from_desktop_snapshot(sender, snapshot_id,image_name)
            if ret < 0:
                logger.error("Task start[%s] desktop fail:%s " % (snapshot_id))
                return -1

    return 0

def handle_task_create_disk_from_desktop_snapshot(directive):

    sender = directive["sender"]
    snapshot_id = directive["snapshot"]
    disk_name = directive["disk_name"]

    with rLock(snapshot_id):

        with ResComm.transition_status(dbconst.TB_DESKTOP_SNAPSHOT, snapshot_id, const.INST_TRAN_STATUS_STARTING):
            ret = Snapshot.task_create_disk_from_desktop_snapshot(sender, snapshot_id,disk_name)
            if ret < 0:
                logger.error("Task start[%s] desktop fail:%s " % (snapshot_id))
                return -1

    return 0

def handle_task_apply_security_policy(directive):
    
    sender = directive["sender"]
    policy_group_id = directive["policy_group"]
    with rLock(policy_group_id):
        if policy_group_id.startswith(UUID_TYPE_SECURITY_POLICY_SGRS):
            with ResComm.transition_status(dbconst.TB_SECURITY_POLICY, policy_group_id, const.STATUS_UPDATING):

                ret = Security.task_apply_security_rule_set(sender, policy_group_id)
                if ret < 0:
                    logger.error("Task apply desktop security fail:%s " % (policy_group_id))
                    return -1
        else:
            with ResComm.transition_status(dbconst.TB_POLICY_GROUP, policy_group_id, const.STATUS_UPDATING):
    
                ret = Security.task_apply_security_policy(sender, policy_group_id)
                if ret < 0:
                    logger.error("Task apply desktop security fail:%s " % (policy_group_id))
                    return -1

    return 0

def handle_task_apply_security_ipset(directive):
    
    sender = directive["sender"]
    security_ipset_id = directive["security_ipset"]
    
    with rLock(security_ipset_id):

        with ResComm.transition_status(dbconst.TB_SECURITY_IPSET, security_ipset_id, const.STATUS_UPDATING):

            ret = Security.task_apply_security_ipset(sender, security_ipset_id)
            if ret < 0:
                logger.error("Task apply desktop security ipset fail:%s " % (security_ipset_id))
                return -1

    return 0

def handle_task_modify_terminal_management_attributes(directive):

    terminal_id = directive["terminal_id"]
    terminal_server_ip = directive['terminal_server_ip']

    req = {
        "action": const.REQUEST_DESKTOP_SERVER_MODIFY_TERMINAL_ATTRIBUTES,
        "terminal_id": terminal_id,
        "params": {
            "terminal_server_ip": terminal_server_ip
        }
    }
    rep = send_terminal_server_request(req)
    if rep is None:
        return -1
    ret = rep["ret_code"]
    if ret != 0:
        return -1

    return 0

def handle_task_restart_terminals(directive):

    terminal_id = directive["terminal_id"]
    terminal_mac = directive['terminal_mac']

    req = {
        "action": const.REQUEST_DESKTOP_SERVER_RESTART_TERMINALS,
        "terminal_id": terminal_id,
        "params": {
            "terminal_mac": terminal_mac
        }
    }
    rep = send_terminal_server_request(req)
    if rep is None:
        return -1
    ret = rep["ret_code"]
    if ret != 0:
        return -1

    return 0

def handle_task_stop_terminals(directive):

    terminal_id = directive["terminal_id"]
    terminal_mac = directive['terminal_mac']

    req = {
        "action": const.REQUEST_DESKTOP_SERVER_STOP_TERMINALS,
        "terminal_id": terminal_id,
        "params": {
            "terminal_mac": terminal_mac
        }
    }
    rep = send_terminal_server_request(req)
    if rep is None:
        return -1
    ret = rep["ret_code"]
    if ret != 0:
        return -1

    return 0

def handle_task_execute_workflow(directive):
    
    sender = directive["sender"]
    workflow_id = directive["workflow_id"]

    with rLock(workflow_id):

        with ResComm.transition_status(dbconst.TB_WORKFLOW, workflow_id, const.STATUS_EXECUTING):

            ret = Workflow.task_execute_workflow(sender, workflow_id)
            if ret < 0:
                logger.error("Task execute workflow fail:%s " % (workflow_id))
                return -1

    return 0

def handle_task_upload_softwares(directive):

    sender = directive["sender"]
    software_id = directive["software_id"]
    software_name = directive["software_name"]

    with rLock(software_id):

        with ResComm.transition_status(dbconst.TB_SOFTWARE_INFO, software_id, const.SOFTWARE_STATUS_UPLOADING):
            ret = Software.task_upload_softwares(sender, software_id,software_name)
            if ret < 0:
                logger.error("Task upload software fail:%s " % (software_id))
                return -1

    return 0

def handle_task_upload_file_shares(directive):

    sender = directive["sender"]
    file_share_group_file_id = directive["file_share_group_file_id"]
    file_share_group_file_name = directive["file_share_group_file_name"]
    file_share_group_dn = directive["file_share_group_dn"]
    create_method = directive["create_method"]

    with rLock(file_share_group_file_id):

        with ResComm.transition_status(dbconst.TB_FILE_SHARE_GROUP_FILE, file_share_group_file_id, const.FILE_SHARE_STATUS_UPLOADING):

            if const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED == create_method:
                ret = FileShare.task_created_file_share_service_upload_file_shares(sender, file_share_group_file_id,file_share_group_file_name,file_share_group_dn)
                if ret < 0:
                    logger.error("task_created_file_share_service_upload_file_shares fail:%s " % (file_share_group_file_id))
                    ret = FileShare.delete_file_share_group_file_dn(file_share_group_file_id)
                    if ret < 0:
                        logger.error("delete_file_share_group_file_dn fail %s" % (file_share_group_file_id))
                        return -1
                    return -1

            elif const.FILE_SHARE_SERVICE_CREATE_METHOD_LOADED == create_method:
                ret = FileShare.task_loaded_file_share_service_upload_file_shares(sender, file_share_group_file_id,file_share_group_file_name,file_share_group_dn)
                if ret < 0:
                    logger.error("task_loaded_file_share_service_upload_file_shares fail:%s " % (file_share_group_file_id))
                    ret = FileShare.delete_file_share_group_file_dn(file_share_group_file_id)
                    if ret < 0:
                        logger.error("delete_file_share_group_file_dn fail %s" % (file_share_group_file_id))
                        return -1
                    return -1

            else:
                logger.error("handle_task_upload_file_shares invalid create_method %s" % (create_method))
                return -1

    return 0

def handle_task_download_file_shares(directive):

    sender = directive["sender"]
    file_share_group_file_id = directive["file_share_group_file_id"]
    file_share_group_file_name = directive["file_share_group_file_name"]
    file_share_group_dn = directive["file_share_group_dn"]
    create_method = directive["create_method"]
    file_share_group_file_size = directive["file_share_group_file_size"]

    with rLock(file_share_group_file_id):

        with ResComm.transition_status(dbconst.TB_FILE_SHARE_GROUP_FILE, file_share_group_file_id, const.FILE_SHARE_STATUS_DOWNLOADING):

            if const.FILE_SHARE_SERVICE_CREATE_METHOD_LOADED == create_method:
                ret = FileShare.task_loaded_file_share_service_download_file_shares(sender, file_share_group_file_id,file_share_group_file_name,file_share_group_dn,file_share_group_file_size)
                if ret < 0:
                    logger.error("task_loaded_file_share_service_download_file_shares fail:%s " % (file_share_group_file_id))
                    return -1
            else:
                logger.error("handle_task_download_file_shares invalid create_method %s" % (create_method))
                return -1

    return 0

def handle_task_change_file_in_file_share_group(directive):

    sender = directive["sender"]
    file_share_group_file_id = directive["file_share_group_file_id"]
    file_share_group_file = directive["file_share_group_file"]
    new_file_share_group_dn = directive["new_file_share_group_dn"]
    change_type = directive["change_type"]
    file_save_method = directive["file_save_method"]
    repeat_file_ids = directive["repeat_file_ids"]
    create_method = directive["create_method"]

    if change_type == const.FILE_SHARE_CHANGE_TYPE_MOVE:
        with rLock(file_share_group_file_id):

            with ResComm.transition_status(dbconst.TB_FILE_SHARE_GROUP_FILE, file_share_group_file_id, const.FILE_SHARE_STATUS_MOVING):

                ret = FileShare.task_change_file_in_loaded_file_share_service_group(sender, file_share_group_file_id,file_share_group_file,new_file_share_group_dn,change_type,file_save_method,repeat_file_ids)
                if ret < 0:
                    logger.error("task_change_file_in_loaded_file_share_service_group move file %s fail" % (file_share_group_file_id))
                    return -1

            # Delete file records in source file share if change_type is move
            ret = FileShare.delete_file_share_group_file_dn(file_share_group_file_id)
            if ret < 0:
                logger.error("delete_file_share_group_file fail %s " %(file_share_group_file_id))
                return -1

    elif change_type == const.FILE_SHARE_CHANGE_TYPE_COPY:
        with rLock(file_share_group_file_id):

            with ResComm.transition_status(dbconst.TB_FILE_SHARE_GROUP_FILE, file_share_group_file_id, const.FILE_SHARE_STATUS_COPYING):
                if const.FILE_SHARE_SERVICE_CREATE_METHOD_CREATED == create_method:
                    ret = FileShare.task_change_file_in_loaded_file_share_service_group(sender, file_share_group_file_id,file_share_group_file,new_file_share_group_dn,change_type,file_save_method,repeat_file_ids)
                    if ret < 0:
                        logger.error("task_change_file_in_loaded_file_share_service_group copy file %s fail" % (file_share_group_file_id))
                        return -1
                elif const.FILE_SHARE_SERVICE_CREATE_METHOD_LOADED == create_method:
                    logger.error("loaded file share service not support copy file action")
                    return -1
                else:
                    logger.error("handle_task_change_file_in_file_share_group invalid create_method %s" % (create_method))
                    return -1

    else:
        logger.error("change_type %s is invalid" %(change_type))
        return -1

    return 0

def handle_task_create_file_share_service(directive):

    ctx = context.instance()
    sender = directive["sender"]
    file_share_service_id = directive["file_share_service_id"]
    network_id = directive["network_id"]
    desktop_server_instance_id = directive["desktop_server_instance_id"]
    private_ip = directive["private_ip"]
    file_share_service_name = directive["file_share_service_name"]
    vnas_disk_size = directive["vnas_disk_size"]
    vnas_id = directive["vnas_id"]
    limit_rate = directive["limit_rate"]
    limit_conn = directive["limit_conn"]
    fuser = directive["fuser"]
    fpw = directive["fpw"]

    with rLock(file_share_service_id):
        if ctx.zone_deploy == const.DEPLOY_TYPE_STANDARD:
            ret = FileShare.task_wait_create_file_share_service_done(sender,
                                                                     file_share_service_id,
                                                                     network_id,
                                                                     desktop_server_instance_id,
                                                                     private_ip,
                                                                     file_share_service_name,
                                                                     vnas_disk_size,
                                                                     vnas_id,
                                                                     limit_rate,
                                                                     limit_conn,
                                                                     fuser,
                                                                     fpw)
            if ret < 0:
                logger.error("task wait create file share service done fail %s" % (file_share_service_id))
                ret = FileShare.delete_file_share_service(file_share_service_id)
                if ret < 0:
                    logger.error("delete_file_share_service fail %s" % (file_share_service_id))
                    return -1
                return -1
        elif ctx.zone_deploy == const.DEPLOY_TYPE_EXPRESS:
            ret = FileShare.task_wait_express_create_file_share_service_done(sender,
                                                                             file_share_service_id,
                                                                             network_id,
                                                                             desktop_server_instance_id,
                                                                             private_ip,
                                                                             file_share_service_name,
                                                                             vnas_disk_size,
                                                                             vnas_id,
                                                                             limit_rate,
                                                                             limit_conn,
                                                                             fuser,
                                                                             fpw)
            if ret < 0:
                logger.error("task wait express create file share service done fail %s" % (file_share_service_id))
                ret = FileShare.delete_file_share_service(file_share_service_id)
                if ret < 0:
                    logger.error("delete_file_share_service fail %s" % (file_share_service_id))
                    return -1
                return -1
        else:
            logger.error("invalid deploy zone_deploy [%s]" %(ctx.zone_deploy))
            return -1

        FileShare.active_file_share_service_status(file_share_service_id)

    return 0

def handle_task_load_file_share_service(directive):

    ctx = context.instance()
    sender = directive["sender"]
    file_share_service_id = directive["file_share_service_id"]
    network_id = directive["network_id"]
    desktop_server_instance_id = directive["desktop_server_instance_id"]
    file_share_service_name = directive["file_share_service_name"]
    vnas_disk_size = directive["vnas_disk_size"]
    vnas_id = directive["vnas_id"]
    limit_rate = directive["limit_rate"]
    limit_conn = directive["limit_conn"]
    fuser = directive["fuser"]
    fpw = directive["fpw"]
    private_ip = directive.get("private_ip")

    with rLock(file_share_service_id):
        if ctx.zone_deploy == const.DEPLOY_TYPE_STANDARD:
            ret = FileShare.task_wait_load_file_share_service_done(sender,
                                                                 file_share_service_id,
                                                                 network_id,
                                                                 desktop_server_instance_id,
                                                                 file_share_service_name,
                                                                 vnas_disk_size,
                                                                 vnas_id,
                                                                 limit_rate,
                                                                 limit_conn,
                                                                 fuser,
                                                                 fpw)
            if ret < 0:
                logger.error("task wait load file share service done fail %s" % (file_share_service_id))
                ret = FileShare.delete_file_share_service(file_share_service_id)
                if ret < 0:
                    logger.error("delete_file_share_service fail %s" % (file_share_service_id))
                    return -1
                return -1
        elif ctx.zone_deploy == const.DEPLOY_TYPE_EXPRESS:
            ret = FileShare.task_wait_express_load_file_share_service_done(sender,
                                                                         file_share_service_id,
                                                                         network_id,
                                                                         desktop_server_instance_id,
                                                                         private_ip,
                                                                         file_share_service_name,
                                                                         vnas_disk_size,
                                                                         vnas_id,
                                                                         limit_rate,
                                                                         limit_conn,
                                                                         fuser,
                                                                         fpw)
            if ret < 0:
                logger.error("task wait express load file share service done fail %s" % (file_share_service_id))
                ret = FileShare.delete_file_share_service(file_share_service_id)
                if ret < 0:
                    logger.error("delete_file_share_service fail %s" % (file_share_service_id))
                    return -1
                return -1
        else:
            logger.error("invalid deploy zone_deploy [%s]" %(ctx.zone_deploy))
            return -1

        FileShare.active_file_share_service_status(file_share_service_id)

    return 0

def handle_task_delete_file_share_service(directive):

    sender = directive["sender"]
    file_share_service_id = directive["file_share_service_id"]
    file_share_service_instance_id = directive["file_share_service_instance_id"]
    create_method = directive["create_method"]

    with rLock(file_share_service_id):

        ret = FileShare.task_wait_delete_file_share_service_done(sender,file_share_service_id,file_share_service_instance_id,create_method)
        if ret < 0:
            logger.error("task wait delete file share service done fail %s" % (file_share_service_id))

        FileShare.delete_file_share_service(file_share_service_id)

    return 0

def handle_task_refresh_file_share_service(directive):

    sender = directive["sender"]
    file_share_service_id = directive["file_share_service_id"]
    create_method = directive["create_method"]

    with rLock(file_share_service_id):

        ret = FileShare.task_wait_refresh_file_share_service_done(sender,file_share_service_id,create_method)
        if ret < 0:
            logger.error("task wait refresh file share service done fail %s" % (file_share_service_id))
            return -1

    return 0

def handle_task_modify_file_share_service(directive):

    sender = directive["sender"]
    file_share_service_id = directive["file_share_service_id"]
    limit_rate = directive["limit_rate"]
    limit_conn = directive["limit_conn"]

    with rLock(file_share_service_id):

        ret = FileShare.task_wait_modify_file_share_service_done(sender,file_share_service_id,limit_rate,limit_conn)
        if ret < 0:
            logger.error("task wait modify file share service done fail %s" % (file_share_service_id))
            return -1

    return 0

def handle_task_delete_file_share_group_files(directive):

    sender = directive["sender"]
    file_share_group_file_id = directive["file_share_group_file_id"]

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if not ret:
        return 0

    with rLock(file_share_group_file_id):

        with ResComm.transition_status(dbconst.TB_FILE_SHARE_GROUP_FILE, file_share_group_file_id, const.FILE_SHARE_STATUS_DELETING):

            ret = FileShare.task_delete_loaded_file_share_service_files(sender, file_share_group_file_id)
            if ret < 0:
                logger.error("task_delete_loaded_file_share_service_files %s fail" % (file_share_group_file_id))
                # Delete file record in the recycle bin
                # FileShare.delete_file_share_group_file_record(file_share_group_file_id)
                return -1

        FileShare.delete_file_share_group_file_record(file_share_group_file_id)

    return 0

def handle_task_restore_file_share_recycles(directive):

    sender = directive["sender"]
    file_share_group_file_id = directive["file_share_group_file_id"]

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if not ret:
        return 0

    with rLock(file_share_group_file_id):

        with ResComm.transition_status(dbconst.TB_FILE_SHARE_GROUP_FILE, file_share_group_file_id, const.FILE_SHARE_STATUS_RESTORING):

            ret = FileShare.task_restore_loaded_file_share_service_recycles(sender, file_share_group_file_id)
            if ret < 0:
                logger.error("task_restore_loaded_file_share_service_recycles %s fail" % (file_share_group_file_id))
                return -1

        # Delete file record in the recycle bin
        FileShare.delete_file_share_group_file_record(file_share_group_file_id)

    return 0

def handle_task_delete_permanently_file_share_recycles(directive):

    sender = directive["sender"]
    file_share_group_file_id = directive["file_share_group_file_id"]

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if not ret:
        return 0

    with rLock(file_share_group_file_id):

        with ResComm.transition_status(dbconst.TB_FILE_SHARE_GROUP_FILE, file_share_group_file_id, const.FILE_SHARE_STATUS_DELETING):

            ret = FileShare.task_delete_permanently_loaded_file_share_service_recycles(sender, file_share_group_file_id)
            if ret < 0:
                logger.error("task_delete_permanently_loaded_file_share_service_recycles %s fail" % (file_share_group_file_id))
                # Delete file record in the recycle bin
                FileShare.delete_file_share_group_file_record(file_share_group_file_id)
                return -1

        # Delete file record in the recycle bin
        FileShare.delete_file_share_group_file_record(file_share_group_file_id)

    return 0

def handle_task_empty_file_share_recycles(directive):

    sender = directive["sender"]
    file_share_group_file_id = directive["file_share_group_file_id"]

    ctx = context.instance()
    ret = ctx.pgm.get_file_share_group_files(file_share_group_file_ids=file_share_group_file_id)
    if not ret:
        return 0

    with rLock(file_share_group_file_id):

        with ResComm.transition_status(dbconst.TB_FILE_SHARE_GROUP_FILE, file_share_group_file_id, const.FILE_SHARE_STATUS_DELETING):

            ret = FileShare.task_empty_loaded_file_share_service_recycles(sender, file_share_group_file_id)
            if ret < 0:
                logger.error("task_empty_loaded_file_share_service_recycles %s fail" % (file_share_group_file_id))
                # Delete file record in the recycle bin
                FileShare.delete_file_share_group_file_record(file_share_group_file_id)
                return -1

        # Delete file record in the recycle bin
        FileShare.delete_file_share_group_file_record(file_share_group_file_id)

    return 0

def handle_task_update_component(directive):

    sender = directive["sender"]
    component_id = directive["component_id"]
    filename = directive["filename"]
    component_type = directive["component_type"]

    with rLock(component_id):

        with ResComm.transition_status(dbconst.TB_COMPONENT_VERSION, component_id, const.COMPONENT_STATUS_UPLOADING):
            ret = Component.task_update_components(sender, component_id,filename,component_type)
            if ret < 0:
                logger.error("Task update components fail:%s " % (component_id))
                Component.update_component_status(component_ids=component_id, status=const.COMPONENT_STATUS_NORMAL)
                return -1

            Component.update_component_status(component_ids=component_id, status=const.COMPONENT_STATUS_NORMAL)

            if component_type == const.COMPONENT_TYPE_FILE_SHARE_TOOLS:
                Component.refresh_component_type_file_share_tools_info(component_id)

            if component_type == const.COMPONENT_TYPE_TOOLS:
                Component.refresh_component_type_tools_info(component_id)
    return 0

def handle_task_execute_server_component_upgrade(directive):

    sender = directive["sender"]
    component_id = directive["component_id"]
    filename = directive["filename"]
    component_type = directive["component_type"]
    target_host = directive["target_host"]

    with rLock(component_id):

        with ResComm.transition_status(dbconst.TB_COMPONENT_VERSION, component_id, const.COMPONENT_STATUS_UPGRADING):
            ret = Component.task_execute_server_component_upgrade(sender, component_id,filename,component_type,target_host)
            if ret < 0:
                logger.error("Task execute_component_upgrade fail:%s " % (component_id))

                # reset component status normal
                Component.update_component_status(component_ids=component_id, status=const.COMPONENT_STATUS_NORMAL)
                return -1

            Component.update_component_status(component_ids=component_id, status=const.COMPONENT_STATUS_NORMAL)
            Component.update_loadbalancer_desktop_service_management(sender)

    return 0

def handle_task_execute_client_component_upgrade(directive):

    sender = directive["sender"]
    terminal_id = directive["terminal_id"]
    terminal_mac = directive['terminal_mac']
    upgrade_packet_name = directive['upgrade_packet_name']
    upgrade_packet_path = directive['upgrade_packet_path']
    upgrade_packet_md5 = directive['upgrade_packet_md5']

    component_id = 'compvn-default-client'
    req = {
        "action": const.REQUEST_DESKTOP_SERVER_ONLINE_UPGRADE_TERMINALS,
        "terminal_id": terminal_id,
        "params": {
            "terminal_mac": terminal_mac,
            "upgrade_packet_name": upgrade_packet_name,
            "upgrade_packet_path": upgrade_packet_path,
            "upgrade_packet_md5": upgrade_packet_md5
        }
    }

    with rLock(component_id):

        with ResComm.transition_status(dbconst.TB_COMPONENT_VERSION, component_id, const.COMPONENT_STATUS_UPGRADING):
            ret = Component.task_execute_client_component_upgrade(sender,req)
            if ret < 0:
                logger.error("Task execute_client_component_upgrade fail:%s " % (component_id))

                # reset component status normal
                Component.update_component_status(component_ids=component_id, status=const.COMPONENT_STATUS_NORMAL)
                return -1

            Component.update_component_status(component_ids=component_id, status=const.COMPONENT_STATUS_NORMAL)

    return 0

def handle_task_apply_desktop_maintainer(directive):

    ctx = context.instance()
    desktop_maintainer_id = directive["desktop_maintainer_id"]
    desktop_id = directive["desktop"]
    network_value = directive["network_value"]
    registry_value = directive["registry_value"]

    ips = []
    nics = ctx.pgm.get_nics(desktop_ids = [desktop_id])
    if not nics:
        logger.error("desktop [%s] have no nics.")
        return -1
    for _,nic in nics.items():
        ips.append(nic["private_ip"])

    # demo
    # req =
    #     {
    #         "action": "apply_desktop_maintainer",
    #         "desktop_id": "desktop-z5gue6cn",
    #         "desktop_ips": ["10.11.13.114"],
    #         "json_detail": {
    #             "network": 1,
    #             "registry": ["HKEY_CURRENT_USER\\Control Panel\\Desktop",
    #                          "HKEY_CURRENT_USER\\Control Panel\\Desktop1",
    #                          "HKEY_CURRENT_USER\\Control Panel\\Desktop2",
    #                          ]
    #         }
    #     }
    # network_value = 1
    # registry_value = ["HKEY_CURRENT_USER\\Control Panel\\Desktop"]

    req = {
        # "action": const.REQUEST_VDHOST_SERVER_STATUS,
        "action": const.REQUEST_VDHOST_SERVER_APPLY_DESKTOP_MAINTAINER,
        "desktop_id": desktop_id,
        "desktop_ips": ips,
        "json_detail":{
            "network": network_value,
            "registry":registry_value,
            }
        }
    logger.info("req == %s" %(req))

    with rLock(desktop_maintainer_id):

        with ResComm.transition_status(dbconst.TB_DESKTOP_MAINTAINER, desktop_maintainer_id, const.DESKTOP_MAINTAINER_STATUS_APPLYING):
            ret = Guest.apply_desktop_maintainer(req)
            if ret < 0:
                logger.error("Task apply_desktop_maintainer fail:%s " % (desktop_maintainer_id))
                return -1

    return 0

def handle_task_run_guest_shell_command(directive):

    ctx = context.instance()
    guest_shell_command_id = directive["guest_shell_command_id"]
    desktop_id = directive["desktop"]
    command = directive["command"]

    ips = []
    nics = ctx.pgm.get_nics(desktop_ids = [desktop_id])
    if not nics:
        logger.error("desktop [%s] have no nics.")
        return -1
    for _,nic in nics.items():
        ips.append(nic["private_ip"])
    req = {
        # "action": const.REQUEST_VDHOST_SERVER_STATUS,
        "action": const.REQUEST_VDHOST_SERVER_RUN_GUEST_SHELL_COMMAND,
        "desktop_id": desktop_id,
        "desktop_ips": ips,
        "params":{
            "command": command,
            }
        }
    logger.info("req == %s" %(req))

    with rLock(guest_shell_command_id):

        with ResComm.transition_status(dbconst.TB_GUEST_SHELL_COMMAND, guest_shell_command_id, const.GUEST_SHELL_COMMAND_STATUS_EXCUTING):
            ret = Guest.run_guest_shell_command(req)
            if ret < 0:
                logger.error("Task run_guest_shell_command fail:%s " % (guest_shell_command_id))
                return -1
            Guest.update_guest_shell_command(guest_shell_command_id=guest_shell_command_id, command_response=ret)

    return 0

def send_to_push_server(task_id):
    if task_id is None:
        return None

    data = ResComm.task_info(task_id)
    if data.get("job_action", "") in const.JOB_ACTION_LIST_NEED_TO_PUSH_SERVER:
        return push_topic_job(data)

class TaskHandler():
    ''' Job Task Handler '''

    def __init__(self):
        self.handler = {
            # desktop group
           
            # desktop
            const.TASK_ACTION_UPDATE_DESKTOP: handle_task_update_desktop,
            const.TASK_ACTION_LEASE_DESKTOP: handle_task_lease_desktop,
            const.TASK_ACTION_CREATE_DESKTOP: handle_task_create_desktop,
            const.TASK_ACTION_DELETE_DESKTOP: handle_task_delete_desktop,
            const.TASK_ACTION_START_DESKTOP: handle_task_start_desktop,
            const.TASK_ACTION_RESTART_DESKTOP: handle_task_restart_desktop,
            const.TASK_ACTION_STOP_DESKTOP: handle_task_stop_desktop,
            const.TASK_ACTION_RESET_DESKTOP: handle_task_reset_desktop,
            const.TASK_ACTION_MODIFY_DESKTOP_ATTRIBUTES: handle_task_modify_desktop_attributes,

            # disk
            const.TASK_ACTION_DELETE_DISK: handle_task_delete_disk,
            const.TASK_ACTION_ATTACH_DISKS: handle_task_attach_disks,
            const.TASK_ACTION_DETACH_DISKS: handle_task_detach_disks,
            const.TASK_ACTION_RESIZE_DISK: handle_task_resize_disk,

            # image
            const.TASK_ACTION_CREATE_IMAGE: handle_task_create_image,
            const.TASK_ACTION_SAVE_IMAGE: handle_task_save_image,
            const.TASK_ACTION_DELETE_IMAGE: handle_task_delete_image,

            # network
            const.TASK_ACTION_UPDATE_DESKTOP_NIC: handle_task_update_desktop_nic,
            const.TASK_ACTION_DELETE_NETWORK: handle_task_delete_network,

            # vdi
            const.TASK_ACTION_SEND_DESKTOP_MESSAGE: handle_task_send_desktop_message,
            const.TASK_ACTION_SEND_DESKTOP_HOT_KEYS: handle_task_send_desktop_hot_keys,
            const.TASK_ACTION_SEND_DESKTOP_NOTIFY: handle_task_send_desktop_notify,
            const.TASK_ACTION_VDI_LOGIN_DESKTOP: handle_task_login_desktop,
            const.TASK_ACTION_VDI_LOGOFF_DESKTOP: handle_task_logoff_desktop,
            const.TASK_ACTION_VDI_ADD_DESKTOP_ACTIVE_DIRECTORY: handle_task_add_desktiop_active_directory,
            const.TASK_ACTION_VDI_MODIFY_GUEST_SERVER_CONFIG: handle_task_modify_guest_server_config,
            
            # apply and approve
            const.TASK_ACTION_VDI_DEAL_DESKTOP_APPLY_FORM: handle_task_deal_desktop_apply_form,
            
            # snapshot
            const.TASK_ACTION_CREATE_DESKTOP_SNAPSHOT: hanlde_task_create_desktop_snapshot,
            const.TASK_ACTION_DELETE_DESKTOP_SNAPSHOT: handle_task_delete_desktop_snapshot,
            const.TASK_ACTION_APPLY_DESKTOP_SNAPSHOT: handle_task_apply_desktop_snapshot,
            const.TASK_ACTION_CAPTURE_INSTANCE_FROM_DESKTOP_SNAPSHOT: handle_task_capture_instance_from_desktop_snapshot,
            const.TASK_ACTION_CREATE_DISK_FROM_DESKTOP_SNAPSHOT: handle_task_create_disk_from_desktop_snapshot,
            
            const.TASK_ACTION_CREATE_COMPUTER: handle_task_create_computer,
            const.TASK_ACTION_APPLY_SECURITY_POLICY: handle_task_apply_security_policy,
            const.TASK_ACTION_APPLY_SECURITY_IPSET: handle_task_apply_security_ipset,

            # terminal
            const.TASK_ACTION_MODIFY_TERMINAL_MAMAGEMENT_ATTRIBUTES: handle_task_modify_terminal_management_attributes,
            const.TASK_ACTION_RESTART_TERMINALS: handle_task_restart_terminals,
            const.TASK_ACTION_STOP_TERMINALS: handle_task_stop_terminals,

            # workflow
            const.TASK_ACTION_EXECUTE_WORKFLOW: handle_task_execute_workflow,

            # softwares
            const.TASK_ACTION_UPLOAD_SOFTWARES: handle_task_upload_softwares,

            # file_share
            const.TASK_ACTION_UPLOAD_FILE_SHARES: handle_task_upload_file_shares,
            const.TASK_ACTION_DOWNLOAD_FILE_SHARES: handle_task_download_file_shares,
            const.TASK_ACTION_CHANGE_FILE_IN_FILE_SHARE_GROUP: handle_task_change_file_in_file_share_group,
            const.TASK_ACTION_CREATE_FILE_SHARE_SERVICE: handle_task_create_file_share_service,
            const.TASK_ACTION_LOAD_FILE_SHARE_SERVICE: handle_task_load_file_share_service,
            const.TASK_ACTION_DELETE_FILE_SHARE_SERVICE: handle_task_delete_file_share_service,
            const.TASK_ACTION_REFRESH_FILE_SHARE_SERVICE: handle_task_refresh_file_share_service,
            const.TASK_ACTION_MODIFY_FILE_SHARE_SERVICE: handle_task_modify_file_share_service,
            const.TASK_ACTION_DELETE_FILE_SHARE_GROUP_FILES: handle_task_delete_file_share_group_files,
            const.TASK_ACTION_RESTORE_FILE_SHARE_RECYCLES: handle_task_restore_file_share_recycles,
            const.TASK_ACTION_DELETE_PERMANENTLY_FILE_SHARE_RECYCLES: handle_task_delete_permanently_file_share_recycles,
            const.TASK_ACTION_EMPTY_FILE_SHARE_RECYCLES: handle_task_empty_file_share_recycles,

            # components
            const.TASK_ACTION_UPDATE_COMPONENT: handle_task_update_component,
            const.TASK_ACTION_EXECUTE_SERVER_COMPONENT_UPGRADE: handle_task_execute_server_component_upgrade,
            const.TASK_ACTION_EXECUTE_CLIENT_COMPONENT_UPGRADE: handle_task_execute_client_component_upgrade,

            # desktop_maintainer
            const.TASK_ACTION_APPLY_DESKTOP_MAINTAINER: handle_task_apply_desktop_maintainer,

            # guest_shell_command
            const.TASK_ACTION_RUN_GUEST_SHELL_COMMAND: handle_task_run_guest_shell_command,
        }
   
    def handle(self, task_id):
        'return'''

        ctx = context.instance()
        task = ctx.pg.get(dbconst.TB_DESKTOP_TASK, task_id)
        if task == None:
            logger.error("invalid task_id: [%s]" % (task_id))
            return

        directive = json_load(task['directive'])
        action = directive['action']
        directive['task_id'] = task_id
        # update job status to "working"
        if not ctx.pg.update(dbconst.TB_DESKTOP_TASK, task_id, {'status': const.TASK_STATUS_WORKING}):
            logger.error("update task_id [%s] failed" % task_id)
            return

        try:
            if action in self.handler:
                # handle directly
                ret = self.handler[action](directive)
                if ret < 0:
                    ResComm.task_fail(task_id)
                else:
                    ResComm.task_ok(task_id)

            else:
                ResComm.task_fail(task_id)

            send_to_push_server(task_id)
            return
        except:
            logger.critical("handle request [%s] failed: [%s] [%s] [%s]" % (action, task['job_id'], task['task_id'], traceback.format_exc()))
            ResComm.task_fail(task_id)
            send_to_push_server(task_id)
            return

