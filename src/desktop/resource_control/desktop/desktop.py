import constants as const
from log.logger import logger
from utils.misc import get_current_time, exec_cmd
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.id_tool import(
    UUID_TYPE_DESKTOP,
    get_uuid,
)
from db.constants import (
    TB_DESKTOP,
    TB_DESKTOP_DISK,
    TB_DESKTOP_GROUP,
)
from common import is_citrix_platform, check_resource_transition_status,\
    is_normal_console,get_target_host_list
import resource_control.desktop.nic as Nic
import resource_control.desktop.desktop_common as Desktopcomm
import resource_control.desktop.job as Job
import resource_control.desktop.disk as Disk
import resource_control.desktop.image as Image
import resource_control.guest.guest as Guest
import resource_control.policy.usb as UsbPlicy
import resource_control.user.apply_approve as ApplyApprove
import resource_control.citrix.guest as CitrixGuest
import os
import threading
import api.user.resource_user as ResUser
import db.constants as dbconst
from api.user.resource_user import del_user_from_resource
# common

def send_desktop_job(sender, desktop_ids, action, extra=None):
    logger.info("send_desktop_job action =%s" % (action))
    if not desktop_ids:
        return None

    if not isinstance(desktop_ids, list):
        desktop_ids = [desktop_ids]


    if action in [const.JOB_ACTION_START_DESKTOPS, const.JOB_ACTION_RESTART_DESKTOPS, const.JOB_ACTION_STOP_DESKTOPS]:
        ret = check_desktop_doing_job(desktop_ids)
        logger.info("check_desktop_doing_job ret =%s" %(ret))
        if isinstance(ret, Error):
            return ret

    directive = {
                "sender": sender,
                "action": action,
                "desktops": desktop_ids
                }
    if extra:
        directive.update(extra)
        
    ret= Job.submit_desktop_job(action, directive, desktop_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret

    return job_uuid

def check_desktop_vaild(desktop_ids=None, desktop_group_id=None, status=None, check_trans_status=True):

    ctx = context.instance()
    if desktop_ids and not isinstance(desktop_ids, list):
        desktop_ids = [desktop_ids]
    
    if status and not isinstance(status, list):
        status = [status]
    
    if not desktop_ids and not desktop_group_id:
        logger.error("check desktop no vaild resource")
        return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                     ErrorMsg.ERR_MSG_NO_RESOURCE_SPECIFIED)
    
    desktops = {}
    if not desktop_ids:
        desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id, status=status)
    else:
        desktops = ctx.pgm.get_desktops(desktop_ids)

    if not desktops:
        if desktop_ids:
            logger.error("check desktop, no found desktop %s" % desktop_ids)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_ids)
        else:
            return None
    else:
        if desktop_ids:
            for desktop_id in desktop_ids:
                if desktop_id not in desktops:
                    logger.error("check desktop,  no found desktop %s" % desktop_ids)
                    return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                                 ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_ids)

    # check desktop transition status
    if check_trans_status:

        ret = check_resource_transition_status(desktops)
        if isinstance(ret, Error):
            return ret
    
    # check desktop status
    if status:
        for desktop_id, desktop in desktops.items():
            desk_status = desktop["status"]
            if desk_status not in status:
                logger.error("desktop %s status %s invaild " % (desktop_id, desk_status))
                return Error(ErrorCodes.NEED_UPDATE_DESKTOP_STATUS,
                             ErrorMsg.ERR_MSG_DESKTOP_STAUTS_DISMATCH, (desktop_id, ",".join(status)))
    
    return desktops

def check_desktop_doing_job(desktop_ids):
    
    if isinstance(desktop_ids, list) and len(desktop_ids) == 1:
        desktop_id=desktop_ids[0]    
    else:
        return True
    ctx = context.instance()
    jobs = ctx.pgm.get_desktop_jobs(status=[const.JOB_STATUS_PEND, const.JOB_STATUS_WORKING],resource_ids=desktop_id)
    if jobs is not None:
        logger.error("resource [%s] have job, please try later" % desktop_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_IN_TRANSITION_STATUS, (desktop_id, "executing"))        
    return True

def refresh_desktop_update(desktop_ids, need_update):
    
    ctx = context.instance()
    if not isinstance(desktop_ids, list):
        desktop_ids = [desktop_ids]
    
    row = {desktop_id: {"need_update": need_update} for desktop_id in desktop_ids}
    if not ctx.pg.batch_update(TB_DESKTOP, row):
        logger.error("refresh desktop update db fail %s" % need_update)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def refresh_random_desktop_count(desktop_group, desktop_ids=None):

    ctx = context.instance()
    desktop_group_type = desktop_group["desktop_group_type"]
    if desktop_group_type != const.DG_TYPE_RANDOM:
        return None
    
    if not desktop_ids:
        desktops = desktop_group["desktops"]
        desktop_ids = desktops.keys()

    desktop_count = desktop_group["desktop_count"]
    if desktop_count >= len(desktop_ids):
        return None
    
    delete_desktop = []
    diff_count = len(desktop_ids) - desktop_count
    if diff_count >= len(desktop_ids):
        delete_desktop.extend(desktop_ids)
    else:
        delete_desktop = desktop_ids[0:diff_count]
    
    update_info = {desktop_id: {"need_update": const.DESKTOP_UPDATE_RESET} for desktop_id in delete_desktop}
    if not ctx.pg.batch_update(TB_DESKTOP, update_info):
        logger.error("refresh random desktop update db fail %s" % update_info)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

# describe desktops
def get_desktop_with_monitor(sender, desktop_ids):
    
    desktop_monitor = {}
    ctx = context.instance()
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        return desktop_monitor

    instance_ids = desktop_instance.values()
    instance_monitor = ctx.res.resource_describe_instances_with_monitors(sender["zone"], instance_ids)
    if not instance_monitor:
        return desktop_monitor
    
    for desktop_id, instance_id in desktop_instance.items():
        instance_data = instance_monitor.get(instance_id)
        if not instance_data:
            continue
        desktop_monitor[desktop_id] = instance_data
    return desktop_monitor

def format_desktop(desktop):
    
    ctx = context.instance()
    zone = desktop["zone"]
    
    filter_keys = ["desktop_mode", "assign_state", "reg_state", "delivery_group_id", "delivery_group_name"]
    if is_citrix_platform(ctx, zone):
        filter_keys = ["connect_status", "login_time", "logout_time", "connect_time", 
                       "usbredir", "clipboard", "no_sync"]

    for filter_key in filter_keys:
        if filter_key not in desktop:
            continue
        del desktop[filter_key]
    
    return desktop

def format_desktop_images(desktop_set):
    
    ctx = context.instance()
    desktop_images = {}
    image_ids = []
    for desktop_id, desktop in desktop_set.items():
        desktop_image_id = desktop["desktop_image_id"]
        desktop_images[desktop_id] = desktop_image_id
        if desktop_image_id not in image_ids:
            image_ids.append(desktop_image_id)
    
    images = ctx.pgm.get_desktop_images(image_ids)
    if not images:
        return None
    
    Image.format_desktop_image(images)
    for desktop_id, desktop_image_id in desktop_images.items():
        desktop = desktop_set.get(desktop_id)
        image = images.get(desktop_image_id)
        if not image or not desktop:
            continue
        desktop["image"] = image

    return None

def check_citrix_is_lock(unassign, randset, user_id, zone_id):
    
    ctx = context.instance()
    
    new_unassign = []
    new_randset = []

    if unassign:
        for desktop in unassign:
            delivery_group_name = desktop.get("delivery_group_name")
            if not delivery_group_name:
                continue
            
            delivery_groups = ctx.pgm.get_delivery_group_by_name(delivery_group_name,zone_id)
            if not delivery_groups:
                continue

            delivery_group = delivery_groups[delivery_group_name]
            delivery_group_id = delivery_group["delivery_group_id"]
    
            ApplyApprove.refresh_desktop_apply_form(resource_group_ids=delivery_group_id)
            sender = {"owner": user_id, "zone": delivery_group["zone"]}

            apply_info = check_apply_desktop_is_lock(sender, resource_group_id=delivery_group_id)
            # update is_lock
            desktop["is_lock"] = apply_info.get("is_lock", 0)
            desktop["approve_groups"] = apply_info.get("approve_groups", {})
            desktop["delivery_group_id"] = delivery_group_id
            desktop["zone"] = zone_id
            if apply_info.get("apply_form"):
                desktop["apply_form"]  = apply_info.get("apply_form")

            new_unassign.append(desktop)
    
    if randset:
        
        for desktop in randset:
            delivery_group_name = desktop.get("delivery_group_name")
            if not delivery_group_name:
                continue
            
            delivery_groups = ctx.pgm.get_delivery_group_by_name(delivery_group_name,zone_id)
            if not delivery_groups:
                continue
            
            delivery_group = delivery_groups[delivery_group_name]
            delivery_group_id = delivery_group["delivery_group_id"]
            if delivery_group["desktop_hide_mode"] == 1:
                continue
            ApplyApprove.refresh_desktop_apply_form(resource_group_ids=delivery_group_id)
            sender = {"owner": user_id, "zone": delivery_group["zone"]}
            apply_info = check_apply_desktop_is_lock(sender, resource_group_id=delivery_group_id)
            # update is_lock
            desktop["is_lock"] = apply_info.get("is_lock", 0)
            desktop["approve_groups"] = apply_info.get("approve_groups", {})
            desktop["delivery_group_id"] = delivery_group_id
            desktop["zone"] = zone_id
            if apply_info.get("apply_form"):
                desktop["apply_form"]  = apply_info.get("apply_form")

            new_randset.append(desktop)
    
    return (new_unassign, new_randset)

def filter_citrix_random_desktop(sender, desktop_set):
    
    ctx = context.instance()
    if not is_normal_console(sender):
        return None
    
    for desktop_id, desktop in desktop_set.items():
        
        if not is_citrix_platform(ctx, desktop["zone"]):
            continue
        
        allocation_type = desktop.get("allocation_type")
        if allocation_type != const.CITRIX_ALLOC_TYPE_RANDOM:
            continue
        
        del desktop_set[desktop_id]

    return None

def check_apply_desktop_is_lock(sender, desktop=None, resource_group_id=None):
    
    ctx = context.instance()
    
    if desktop:
        sender["zone"] = desktop["zone"]
    
    zone_id = sender["zone"]
    owner = sender["owner"]
    
    apply_info = {"is_lock": 0}
    if not desktop and not resource_group_id:
        return apply_info
    
    if not resource_group_id:
        if is_citrix_platform(ctx, zone_id):
            resource_group_id = desktop["delivery_group_id"]
        else:
            resource_group_id = desktop["desktop_group_id"]

    ret = ctx.pgm.get_resource_group_apply_group(resource_group_id)
    if not ret:
        return apply_info

    apply_group_ids = ret
    
    user_ids = [owner]

    ret = ctx.pgm.get_user_group(owner)
    if ret:
        user_ids.extend(ret)
    
    approve_users = {}
    user_apply_group = []
    for apply_group_id in apply_group_ids:

        ret = ctx.pgm.get_apply_user(apply_group_id, user_ids=user_ids)
        if not ret:
            continue
        
        user_apply_group.append(apply_group_id)
        ret = ApplyApprove.get_approve_users(apply_group_id)
        if ret:
            approve_users.update(ret)
    
    if not user_apply_group:
        return apply_info
    
    apply_info["approve_groups"] = approve_users.values()
    apply_forms = ctx.pgm.get_apply_forms(resource_group_id=resource_group_id, status=const.APPLY_FORM_VAILD_STATUS, apply_user_id=owner)
    if not apply_forms:
        apply_info["is_lock"] = 1
        return apply_info

    apply_form = apply_forms.values()[0]
    apply_info["apply_form"] = apply_form
    status = apply_form["status"]
    apply_info["is_lock"] = 1 if status != const.APPLY_FORM_STATUS_EFFECTIVE else 0
    return apply_info

def refresh_zone_desktop_status(zone_id, desktops):
    
    ctx = context.instance()
    desktop_ids = desktops.keys()
    if not desktops:
        return None
    
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

    update_desktop = {}
    for desktop_id in desktop_ids:
        
        desktop = desktops[desktop_id]
        desktop_status = desktop["status"]
        transition_status = desktop["transition_status"]

        status_info = {}
        instance_id = desktop_instance.get(desktop_id)
        if not instance_id:
            if desktop_status != const.INST_STATUS_STOP:
                status_info["status"] = const.INST_STATUS_STOP
                update_desktop[desktop_id] = status_info

            continue

        instance = instances.get(instance_id)
        if not instance:
            if desktop_status != const.INST_STATUS_STOP:
                status_info["status"] = const.INST_STATUS_STOP
                update_desktop[desktop_id] = status_info
        
            continue
        
        if desktop_status != instance["status"]:
            status_info["status"] = instance["status"]
            update_desktop[desktop_id] = status_info
        
        if transition_status != instance["transition_status"]:
            status_info["transition_status"] = instance["transition_status"] if instance["transition_status"] else ''
            status_info["status"] = instance["status"]
            update_desktop[desktop_id] = status_info

    if not update_desktop:
        return None

    for desktop_id,update_desktop_item in update_desktop.items():
        condition = {"desktop_id": desktop_id}
        update_info = dict(
            status=update_desktop_item.get("status"),
            transition_status=update_desktop_item.get("transition_status",'')
        )
        if not ctx.pg.base_update(dbconst.TB_DESKTOP, condition, update_info):
            logger.error("update desktop for [%s] [%s] to db failed" % (condition,update_info))
            continue

    return update_desktop

def refresh_desktop_status(desktops):

    desktop_ids = desktops.keys()
    
    zone_desktops = {}
    
    for desktop_id, desktop in desktops.items():
        
        zone = desktop["zone"]
        if not zone:
            continue
        if zone not in zone_desktops:
            zone_desktops[zone] = []

        zone_desktops[zone].append(desktop_id)

    update_desktops = {}
    for zone_id, desktop_ids in zone_desktops.items():

        check_desktops = {}
        for desktop_id in desktop_ids:
            desktop = desktops.get(desktop_id)
            if not desktop:
                continue
            check_desktops[desktop_id] = desktop
        
        update_desktop = refresh_zone_desktop_status(zone_id, check_desktops)
        if update_desktop:
            update_desktops.update(update_desktop)
    
    return update_desktops
    
def format_desktop_policy_group(desktops):
    
    ctx = context.instance()
    desktop_ids = desktops.keys()
    
    ret = ctx.pgm.get_resource_policy(desktop_ids)
    if not ret:
        return None
    
    resource_policys = ret
    
    policy_groups = ctx.pgm.get_policy_groups(None, extras=[])
    if not policy_groups:
        policy_groups = {}
    
    for desktop_id, desktop in desktops.items():
        resource_policy = resource_policys.get(desktop_id)
        if not resource_policy:
            continue
        policy_group_id = resource_policy["policy_group_id"]
        policy_group = policy_groups.get(policy_group_id)
        if not policy_group:
            continue
        policy_group["is_lock"] = resource_policy["is_lock"]
        desktop["policy_group"] = policy_group

    return None

def format_normal_desktops(sender, desktop_set):
    
    ctx = context.instance()
    if not desktop_set:
        return None

    desktop_ids = desktop_set.keys()
    # get nic
    desktop_nics = ctx.pgm.get_desktop_nics(desktop_ids)
    if not desktop_nics:
        desktop_nics = {}
    
    desktop_images = ctx.pgm.get_desktop_images()
    if not desktop_images:
        desktop_images = {}
    
    ApplyApprove.refresh_desktop_apply_form(desktop_ids)   
    
    for desktop_id, desktop in desktop_set.items():
        format_desktop(desktop)
        
        zone_id = desktop["zone"]
        desktop_image_id = desktop["desktop_image_id"]
        # get image ui_type
        desktop_image = desktop_images.get(desktop_image_id)
        if desktop_image:
            desktop["ui_type"] = desktop_image["ui_type"]

        # get nics
        nics = desktop_nics.get(desktop_id)
        if nics:
            desktop["nics"] = nics
        
        desktop_group_id = desktop["desktop_group_id"]
        desktop_group = ctx.pgm.get_desktop_group(desktop_group_id, extras=[])
        if not desktop_group:
            desktop_group = {}
        
        if is_citrix_platform(ctx, zone_id):
            desktop["allocation_type"] = desktop_group.get("allocation_type", "")
        else:
            desktop["desktop_group_type"] = desktop_group.get("desktop_group_type", "")
        
        desktop["mode"] = desktop_group.get("status", const.DESKTOP_GROUP_STATUS_NORMAL)
        if is_citrix_platform(ctx, zone_id):
            
            apply_info = check_apply_desktop_is_lock(sender, desktop)
            # update is_lock
            desktop["is_lock"] = apply_info.get("is_lock", 0)
            desktop["approve_groups"] = apply_info.get("approve_groups", {})
            desktop["apply_form"]  = apply_info.get("apply_form", {})
    
        else:
            # update is_lock
            apply_info = check_apply_desktop_is_lock(sender, desktop)
            
            # update is_lock
            desktop["is_lock"] = apply_info.get("is_lock", 0)
            desktop["approve_groups"] = apply_info.get("approve_groups", {})
            desktop["apply_form"]  = apply_info.get("apply_form", {})

            # update user status in desktop group
            if desktop_group_id and sender["owner"]:
                desktop["owner_status"] = ctx.pgm.get_user_status_in_desktop_group(sender["owner"], desktop_group_id)

        trans_status = desktop["transition_status"]
        if trans_status:
            desktop["need_update"] = 0

    filter_citrix_random_desktop(sender, desktop_set)
    
    return desktop_set

def format_desktops(sender, desktop_set, verbose=0, with_monitor=0):
    
    ctx = context.instance()
    if not desktop_set:
        return None

    desktop_ids = desktop_set.keys()
    desktop_monitor = {}
    if with_monitor:
        # get monitor
        ret = get_desktop_with_monitor(sender, desktop_ids)
        if ret:
            desktop_monitor = ret
    
    desktop_disks = {}
    desktop_nics = {}
    if verbose > 0:
        # get disk
        ret = ctx.pgm.get_desktop_disks(desktop_ids)
        if ret:
            desktop_disks = ret
        # get nic
        ret = ctx.pgm.get_desktop_nics(desktop_ids)
        if ret:
            desktop_nics = ret
        # get desktop image
        format_desktop_images(desktop_set)
    
    desktop_groups = {}
    ret = ctx.pgm.get_group_by_desktop(desktop_ids)
    if ret:
        desktop_group_ids = ret.keys()
        ret = ctx.pgm.get_desktop_groups(desktop_group_ids)
        if ret:
            desktop_groups = ret
       
    update_status = refresh_desktop_status(desktop_set)
    if not update_status:
        update_status = {}
    
    for desktop_id, desktop in desktop_set.items():
        format_desktop(desktop)
        
        if desktop_id in update_status:
            
            status = update_status[desktop_id].get("status")
            if status is not None:
                desktop["status"] = status
            
            transition_status = update_status[desktop_id].get("transition_status")
            if transition_status is not None:
                desktop["transition_status"] = transition_status

        # get monitor
        monitor = desktop_monitor.get(desktop_id)
        if monitor:
            desktop["monitor_data"] = monitor["monitor_data"]

        # get resource
        disks = desktop_disks.get(desktop_id)
        if disks:
            desktop["disks"] = disks
        
        desktop_users = {}
        desktop_owners = ctx.pgm.get_resource_users(desktop_id)
        if desktop_owners:
            desktop_owner = desktop_owners.get(desktop_id, [])
            for user in desktop_owner:
                user_id = user["user_id"]
                user_name = user["user_name"]
                desktop_users[user_id] = user_name
        
        desktop["desktop_owner"] = desktop_users
        # get nics
        nics = desktop_nics.get(desktop_id)
        if nics:
            desktop["nics"] = nics
        
        if is_citrix_platform(ctx, sender["zone"]):
            # get login record
            desktop["login_record"] = CitrixGuest.describe_desltop_login_record(desktop_id=desktop_id)
        else:
            # get guest info
            spice_info = Guest.describe_guest_connection_info(desktop_id)
            if spice_info:
                desktop["conn_status"] = spice_info

            # get usb policy
            desktop_group_id = desktop["desktop_group_id"]
            if desktop_group_id:
                usb_policy = UsbPlicy.describe_usb_policy({"object_id": desktop_group_id})
            else:
                usb_policy = UsbPlicy.describe_usb_policy({"object_id": desktop_id})
            if usb_policy:
                desktop["usb_policy"] = usb_policy
            # update user status in desktop group
            if desktop_group_id and desktop_users:
                desktop["owner_status"] = ctx.pgm.get_user_status_in_desktop_group(desktop_users.keys(), desktop_group_id)

        trans_status = desktop["transition_status"]
        if trans_status:
            desktop["need_update"] = 0

        desktop_group_id = desktop["desktop_group_id"]
        desktop_group = desktop_groups.get(desktop_group_id)
        if desktop_group:
            desktop["mode"] = desktop_group["status"]
            desktop["allocation_type"] = desktop_group["allocation_type"]
            desktop["provision_type"] = desktop_group.get("provision_type", 'MCS')

    filter_citrix_random_desktop(sender, desktop_set)
    format_desktop_policy_group(desktop_set)
    
    return desktop_set

# create desktops

def check_desktop_hostname(hostname):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_desktop_hostname()
    if not ret:
        return hostname

    if hostname.upper() in ret:
        logger.error("desktop hotname already existd %s" % hostname)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKOTP_HOSTNAME_ALREADY_EXISTED, hostname)
    return hostname

def get_desktop_config(sender, req):
    
    ctx = context.instance()
    desktop_config = {}
    required_params = ["cpu", "memory", "instance_class"]
    desktop_keys = ["cpu", "memory", "instance_class", "gpu", "gpu_class", "ivshmem_enable",
                    "usbredir", "clipboard", "filetransfer", "description", "desktop_dn", "qxl_number","cpu_model"]
    
    for desktop_key in desktop_keys:
        if desktop_key not in req:
            if desktop_key in required_params:
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
            continue
        
        if req[desktop_key] is None:
            continue
        
        desktop_config[desktop_key] = req[desktop_key]

    desktop_dn = desktop_config.get("desktop_dn")
    if desktop_dn:
        ret = ctx.pgm.get_ou_guid(desktop_dn)
        if ret:
            desktop_config["dn_guid"] = ret
    
    gpu = desktop_config.get("gpu", 0)
    if gpu:
        gpu_class = desktop_config.get("gpu_class", 0)
        ret = Desktopcomm.check_desktop_group_gpus(sender, 1, gpu, gpu_class)
        if isinstance(ret, Error):
            return ret

    return desktop_config

def register_desktop(sender, req, desktop_image, hostname=None):

    ctx = context.instance()
    ret = get_desktop_config(sender, req)
    if isinstance(ret, Error):
        return ret
    desktop_config = ret

    desktop_id = get_uuid(UUID_TYPE_DESKTOP, ctx.checker)
    desktop_info = dict(desktop_id=desktop_id,
                        desktop_image_id=desktop_image["desktop_image_id"],
                        image_name=desktop_image["image_name"],
                        status=const.INST_STATUS_STOP,
                        instance_class = desktop_config["instance_class"],
                        cpu = desktop_config["cpu"],
                        memory = desktop_config["memory"],
                        gpu = desktop_config.get("gpu", 0),
                        gpu_class = desktop_config.get("gpu_class", 0),
                        ivshmem_enable = desktop_config.get("ivshmem_enable", 0),
                        usbredir=desktop_config.get("usbredir", 1),
                        clipboard=desktop_config.get("clipboard", 1),
                        filetransfer=desktop_config.get("filetransfer", 1),
                        qxl_number=desktop_config.get("qxl_number", 1),
                        create_time=get_current_time(False),
                        status_time = get_current_time(False),
                        hostname = hostname if hostname else '',
                        desktop_dn = desktop_config.get("desktop_dn", ''),
                        dn_guid = desktop_config.get("dn_guid", ''),
                        cpu_model=desktop_config.get("cpu_model", ''),
                        zone=sender["zone"],
                        )
    if not ctx.pg.batch_insert(TB_DESKTOP, {desktop_id: desktop_info}):
        logger.error("insert newly created desktop [%s] to db failed" % (desktop_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return desktop_id

# modify desktop attribute
def modify_desktop_attributes(desktop, maint_columns):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    instance_id = desktop["instance_id"]

    desktop_info = {}
    modify_key = ["description"]
    update_key = ["cpu", "memory", "ivshmem", "gpu", "usbredir", "clipboard", "filetransfer", "qxl_number", "no_sync"]

    need_update = False
    for maint_key, maint_value in maint_columns.items():
        if maint_key not in modify_key and maint_key not in update_key:
            continue

        if maint_value == desktop[maint_key]:
            continue

        if maint_key in update_key and instance_id:
            need_update = True

        desktop_info[maint_key] = maint_value

    if not desktop_info:
        return None

    if not ctx.pg.batch_update(TB_DESKTOP, {desktop_id: desktop_info}):
        logger.error("modify desktop attributes update db fail %s" % desktop_info)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    if need_update:
        ret = refresh_desktop_update(desktop_id, const.DESKTOP_UPDATE_MODIFY)
        if isinstance(ret, Error):
            return ret

        return desktop_id

    return None

# delete desktops
def delete_desktop_disk_info(desktop_ids):

    ctx = context.instance()

    desktops = ctx.pgm.get_desktops(desktop_ids, has_disk=True)
    if not desktops:
        return None
    
    delete_disk = []
    update_disk = {}
    for _, desktop in desktops.items():
        
        instance_id = desktop["instance_id"]
        if instance_id:
            continue
        
        save_disk = desktop["save_disk"]
        disks = desktop.get("disks")
        if not disks:
            continue
        
        for disk in disks:
            disk_id = disk["disk_id"]
            volume_id = disk["volume_id"]
            if save_disk == const.DISK_RULE_NOSAVE:
                if volume_id:
                    update_disk[disk_id] = {
                        "desktop_id": disk["desktop_id"],
                        "desktop_name": disk["desktop_name"],
                        "status": disk["status"],
                        "need_update": const.DESKTOP_DISK_DELETE,
                        }
                else:
                    delete_disk.append(disk_id)
            else:
                update_disk[disk_id] = {
                        "desktop_id": '',
                        "desktop_name": '',
                        "status": const.DISK_STATUS_AVAIL,
                        "need_update": disk["need_update"],
                        }
    
    if update_disk:
        if not ctx.pg.batch_update(TB_DESKTOP_DISK, update_disk):
            logger.error("update desktop disk fail %s" % update_disk)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    if delete_disk:
        for disk_id in delete_disk:
            ctx.pg.delete(TB_DESKTOP_DISK, disk_id)
        
    return update_disk

def update_delete_desktop_disk(desktop_ids):
    
    ctx = context.instance()
    disks = ctx.pgm.get_disks(desktop_ids=desktop_ids)
    if not disks:
        return None
    
    disk_ids = disks.keys()
    update_info = {
                   "need_update": 0,
                   "desktop_id": '',
                   "desktop_name": '',
                   'status': const.DISK_STATUS_AVAIL
                   }
        
    update_disk = {disk_id: update_info for disk_id in disk_ids}
    if not ctx.pg.batch_update(TB_DESKTOP_DISK, update_disk):
        logger.error("refresh desktop disk update db fail %s" % update_disk)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def delete_desktops(sender, desktops, ignore_save=False, user_ids=None):

    ctx = context.instance()
    desktop_ids = desktops.keys()
    
    if user_ids:
        ret = ctx.pgm.get_resource_user_ids(desktop_ids)
        if not ret:
            return None

    upate_desktop = []
    # if desktop has instance, need to send job
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if desktop_instance:
        upate_desktop.extend(desktop_instance.keys())
    
    # delete disk, if disk has volume, send job to handle
    ret = Disk.delete_desktop_disks(desktops, ignore_save)
    if isinstance(ret, Error):
        return ret
    if ret:
        for desktop_id in ret:
            if desktop_id not in upate_desktop:
                upate_desktop.append(desktop_id)
    
    # delete guest connect info record
    ret = Guest.delete_guest_connection_info(desktop_ids)
    if ret < 0:
        logger.error("clean desktop spice connection info failed")

    if upate_desktop:
        ret = refresh_desktop_update(upate_desktop, const.DESKTOP_UPDATE_DELETE)
        if isinstance(ret, Error):
            return ret
    
    delete_desktop = []
    for desktop_id in desktop_ids:
        if desktop_id in upate_desktop:
            continue
        
        ctx.pg.delete(TB_DESKTOP, desktop_id)
        del_user_from_resource(ctx, desktop_id)
        
        delete_desktop.append(desktop_id)
    
    if delete_desktop:
        ret = update_delete_desktop_disk(delete_desktop)
        if isinstance(ret, Error):
            return ret

    return upate_desktop

def check_attach_user_to_desktop(desktop_id, user_ids):
    
    ctx = context.instance()
    
    desktop_users = ctx.pgm.get_resource_user_ids(desktop_id, user_ids=user_ids)
    if not desktop_users:
        return None
    
    desktop_user = desktop_users.get(desktop_id)
    if not desktop_user:
        return None
    
    attach_user = []
    for user_id in user_ids:
        if user_id in desktop_user:
            continue
        attach_user.append(user_id)

    return attach_user

# attach user to desktop
def attach_user_to_dekstop(desktop_id, user_ids):
    
    ctx = context.instance()
    
    if not user_ids:
        return None
    
    if not isinstance(user_ids, list):
        user_ids = [user_ids]
    
    users = ctx.pgm.get_desktop_users(user_ids)
    if not users:
        return None
    
    ret = ResUser.attach_user_to_desktop_resource(ctx, desktop_id, user_ids)
    if isinstance(ret, Error):
        return ret

    return None

# detach user from desktop
def detach_user_from_dekstop(desktop_id, user_ids=None):

    ctx = context.instance()
    if not user_ids:
        ret = ctx.pgm.get_resource_user(desktop_id)
        if not ret:
            return None
        
        user_ids = ret
        
    ret = ResUser.detach_user_from_desktop_resource(ctx, desktop_id, user_ids)
    if isinstance(ret, Error):
        return ret
    update_info = {"auto_login": 0}
    rows = {desktop_id: update_info}
    if not ctx.pg.batch_update(TB_DESKTOP, rows):
        logger.error("detach user from desktop update db fail %s" % rows)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

# restart desktop
def restart_desktops(sender, desktops):

    ctx = context.instance()

    desktop_ids = desktops.keys()
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        desktop_instance = {}

    random_desktop = []
    reset_desktop = []
    restart_desktop = []

    for desktop_id, desktop in desktops.items():
        
        desktop_group_type = desktop["desktop_group_type"]
        
        if desktop_id not in desktop_instance:
            continue

        restart_desktop.append(desktop_id)
        
        if desktop_group_type == const.DG_TYPE_RANDOM:
            random_desktop.append(desktop_id)

        need_update = desktop["need_update"]
        if need_update == const.DESKTOP_UPDATE_DELETE:
            continue

        save_desk = desktop["save_desk"]
        if save_desk == const.DESKTOP_RULE_NOSAVE and not is_citrix_platform(ctx, sender["zone"]):
            reset_desktop.append(desktop_id)
    
    if random_desktop:
        for desktop_id in random_desktop:
            ret = detach_user_from_dekstop(desktop_id)
            if isinstance(ret, Error):
                return ret

    if reset_desktop:
        ret = refresh_desktop_update(reset_desktop, const.DESKTOP_UPDATE_RESET)
        if isinstance(ret, Error):
            return ret

    return restart_desktop

# start desktop
def start_desktops(desktops):
    
    if not desktops:
        return None
    
    start_desktop = []
    for desktop_id, _ in desktops.items():
        start_desktop.append(desktop_id)

    return start_desktop

# stop desktops
def stop_desktops(sender, desktops):

    ctx = context.instance()
    if not desktops:
        return None

    desktop_ids = desktops.keys()
    random_desktop = []
    reset_desktop = []
    stop_desktop = []
    
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        desktop_instance = {}

    for desktop_id, desktop in desktops.items():

        desktop_group_type = desktop["desktop_group_type"]
        if desktop_id not in desktop_instance:
            continue
        stop_desktop.append(desktop_id)
        
        if desktop_group_type == const.DG_TYPE_RANDOM:
            random_desktop.append(desktop_id)
        
        if not is_citrix_platform(ctx, sender["zone"]):
            need_update = desktop["need_update"]
            if need_update == const.DESKTOP_UPDATE_DELETE:
                continue
    
            save_desk = desktop["save_desk"]
            if save_desk == const.DESKTOP_RULE_NOSAVE:
                reset_desktop.append(desktop_id)
    
    if random_desktop:
        for desktop_id in random_desktop:
            ret = detach_user_from_dekstop(desktop_id)
            if isinstance(ret, Error):
                return ret

    if reset_desktop:
        ret = refresh_desktop_update(reset_desktop, const.DESKTOP_UPDATE_RESET)
        if isinstance(ret, Error):
            return ret

    return stop_desktop

# reset desktops

def reset_desktops(desktops):
    
    ctx = context.instance()

    desktop_ids = desktops.keys()
    random_desktop = []
    reset_desktop = []
    
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        desktop_instance = {}
    
    for desktop_id, desktop in desktops.items():
        desktop_group_type = desktop["desktop_group_type"]

        if desktop_id not in desktop_instance:
            continue
        reset_desktop.append(desktop_id)
        
        if desktop_group_type == const.DG_TYPE_RANDOM:
            random_desktop.append(desktop_id)

        need_update = desktop["need_update"]
        if need_update == const.DESKTOP_UPDATE_DELETE:
            continue
    
    if random_desktop:
        for desktop_id in random_desktop:
            ret = detach_user_from_dekstop(desktop_id)
            if isinstance(ret, Error):
                return ret
    
    if reset_desktop:
        ret = refresh_desktop_update(reset_desktop, const.DESKTOP_UPDATE_RESET)
        if isinstance(ret, Error):
            return ret

    return reset_desktop

# set desktop monitor
def set_desktop_monitor(desktop_ids, monitor):
    
    ctx = context.instance()
    update_info = {desktop_id: {"need_monitor": monitor} for desktop_id in desktop_ids}
    if not ctx.pg.batch_update(TB_DESKTOP, update_info):
        logger.error("set desktop monitor update db fail %s" % desktop_ids)        
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def set_desktop_auto_login(sender, desktop_id, auto_login):
    
    ctx = context.instance()
    user_id = sender["owner"]
    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        logger.error("resource describe instance no found %s" % desktop_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, desktop_id)
    
    desktop = desktops[desktop_id]
    user_desktops =ctx.pgm.get_resource_by_user(user_id)
    if not user_desktops:
        return None
    
    user_desktop = user_desktops[user_id]
    
    update_desktop = {}
    desktops = ctx.pgm.get_desktops(user_desktop)
    for desk_id, desktop in desktops.items():
        if desktop_id == desk_id:
            update_desktop[desk_id] = {"auto_login": auto_login}
            continue
        
        curr_auto_login = desktop["auto_login"]
        if auto_login and curr_auto_login:
            update_desktop[desk_id] = {"auto_login": 0}
    
    if not update_desktop:
        return None

    if not ctx.pg.batch_update(TB_DESKTOP, update_desktop):
        logger.error("set desktop auto login update db fail %s" % update_desktop)        
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED) 
    return None

def modify_desktop_description(desktop_id, description):

    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        logger.error("resource describe instance no found %s" % desktop_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, desktop_id)
    
    if not ctx.pg.batch_update(TB_DESKTOP, {desktop_id: {"description": description}}):
        logger.error("moodify desktop description update db fail %s" % desktop_id)        
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

# create broker
def create_broker(sender, instance_id, is_token=0):
    
    ctx = context.instance()
    ret = ctx.res.resource_describe_instances(sender["zone"], instance_id)
    if not ret:
        logger.error("resource describe instance no found %s" % instance_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, instance_id)

    instance = ret[instance_id]
    ret = ctx.res.resource_create_brokers(sender["zone"], instance_id, is_token)
    if not ret:
        logger.error("resource instance create broker fail %s" % instance_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_INSTANCE_CREATE_BROKER_FAILED, instance_id)
    brokers = ret
    
    broker = brokers[0]
    broker["graphics_passwd"] = instance.get("graphics_passwd", '')
    broker["usb_redirect"] = instance.get("usb_redirect", 1)
    broker["copy_paste"] = instance.get("copy_paste", 1)
    broker["file_draw"] = instance.get("file_draw", 1)
    
    return broker

# delete broker
def delete_brokers(sender, desktops):

    ctx = context.instance()
    if not desktops:
        return None

    desktop_ids = desktops.keys()
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        desktop_instance = {}

    break_instance = []
    random_desktop = []
    for desktop_id, desktop in desktops.items():
        desktop_group_type = desktop["desktop_group_type"]
        if desktop_group_type == const.DG_TYPE_RANDOM:
            random_desktop.append(desktop_id)
        
        if desktop_id not in desktop_instance:
            continue
        instance_id = desktop["instance_id"]
        break_instance.append(instance_id)
 
    if random_desktop:
        for desktop_id in random_desktop:
            ret = detach_user_from_dekstop(desktop_id)
            if isinstance(ret, Error):
                return ret
    
    if break_instance:
        ret = ctx.res.resource_delete_brokers(sender["zone"], break_instance)
        if ret is None:
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, instance_id)
    return None

# create desktop group desktop
def alloc_desktop_hostname(desktop_group, desktop_ids):

    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]

    update_desktop = {}

    hostname_list = []        
    desktop_hostname = ctx.pgm.get_desktop_group_hostname(desktop_group_id)
    if desktop_hostname:
        hostname_list.extend(desktop_hostname.values())

    naming_count = desktop_group["naming_count"]
    naming_rule = desktop_group.get("naming_rule")
    for desktop_id in desktop_ids:
        if not naming_rule:
            desktop_hostname[desktop_id] = desktop_id
            continue
        
        if desktop_id in desktop_hostname:
            continue

        while True:
            naming_count = naming_count + 1
            hostname = "%s-%s" % (naming_rule, str(naming_count).zfill(3))
            if hostname in hostname_list:
                continue

            hostname_list.append(hostname)
            desktop_hostname[desktop_id] = hostname
            update_desktop[desktop_id] = {"hostname": hostname}
            break

    ret = check_desktop_in_domain(desktop_group["zone"], hostname)
    if isinstance(ret, Error):
        return ret
    
    if not ctx.pg.batch_update(TB_DESKTOP_GROUP, {desktop_group_id: {"naming_count": naming_count}} ):
        logger.error("Failed to update desktop [%s] hostname" % update_desktop.keys())
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    # update desktop hostname
    if update_desktop:
        if not ctx.pg.batch_update(TB_DESKTOP, update_desktop):
            logger.error("Failed to update desktop [%s] hostname" % update_desktop.keys())
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return desktop_hostname

def register_desktop_group_desktops(sender, desktop_group, user_ids=None, desktop_count=1):

    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]
    
    # get desktop image
    desktop_image_id = desktop_group["desktop_image_id"]
    ret = ctx.pgm.get_desktop_images(desktop_image_id)
    if not ret:
        logger.error("desktop group image %s invaild" % desktop_image_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKTOP_GROUP_IMAGE_INVAILD, desktop_image_id)
    desktop_image = ret[desktop_image_id]

    update_desktops = {}

    desktop_group_type = desktop_group["desktop_group_type"]

    if desktop_group_type == const.DG_TYPE_RANDOM:
        if not desktop_count:
            return None

        for _ in range(desktop_count):
            ret = register_desktop(sender, desktop_group, desktop_image)
            if isinstance(ret, Error):
                return ret

            desktop_id = ret
            desktop_info = dict(
                                desktop_group_id=desktop_group_id,
                                desktop_group_name=desktop_group["desktop_group_name"],
                                desktop_group_type = desktop_group["desktop_group_type"],
                                save_disk = desktop_group["save_disk"],
                                save_desk = desktop_group["save_desk"]
                                )
            update_desktops[desktop_id] = desktop_info
    else:
        if not user_ids:
            return None
        
        users = ctx.pgm.get_desktop_users(user_ids)
        if not users:
            return None
        
        # create desktop for users
        for user_id in user_ids:
            
            ret = register_desktop(sender, desktop_group, desktop_image)
            if isinstance(ret, Error):
                return ret

            desktop_id = ret

            desktop_info = dict(
                                desktop_group_id=desktop_group_id,
                                desktop_group_name=desktop_group["desktop_group_name"],
                                desktop_group_type = desktop_group["desktop_group_type"],
                                save_disk = desktop_group["save_disk"],
                                save_desk = desktop_group["save_desk"],                          
                                )
            update_desktops[desktop_id] = desktop_info
            
            ret = ResUser.add_user_to_resource(ctx, desktop_id, user_id)
            if isinstance(ret, Error):
                return ret
    
    if update_desktops:
        if not ctx.pg.batch_update(TB_DESKTOP, update_desktops):
            logger.error("update desktop user db fail %s " % update_desktops)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    desktop_ids = update_desktops.keys()
    if not desktop_ids:
        return None

    # alloc hostname to desktop
    ret = alloc_desktop_hostname(desktop_group, desktop_ids)
    if isinstance(ret, Error):
        return ret

    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        return None

    # alloc nic to desktop
    ret = Nic.alloc_desktop_group_nics(sender,desktop_group, desktop_ids)
    if isinstance(ret, Error):
        return ret
    
    # alloc disk to desktop
    disk_config = ctx.pgm.get_disk_config(desktop_group_id=desktop_group_id)
    if disk_config:
        for _, disk_config in disk_config.items():
            ret = Disk.create_disks(disk_config, desktops.keys())
            if isinstance(ret, Error):
                return ret
    
    return desktop_ids

def desktop_leave_network(desktop_ids, network):

    ctx = context.instance()
    network_id = network["network_id"]

    ret = Nic.desktop_detach_nics(desktop_ids, network_id)
    if isinstance(ret, Error):
        return ret

    update_nics = ctx.pgm.get_desktop_nics(desktop_ids, const.DESKTOP_NIC_DETACH)
    if not update_nics:
        return None

    return update_nics.keys()

def desktop_join_network(desktops, network):

    ctx = context.instance()
    desktop_ids = desktops.keys()
    network_id = network["network_id"]
    network_type = network["network_type"]
    
    # desktop cant in the same network type network
    ret = ctx.pgm.get_desktop_nics(desktop_ids, network_type=network_type)
    if ret:
        logger.error("desktop %s has already the same type network %s " % (desktop_ids, network_type))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_IN_THE_SAME_NETWORK, (desktop_ids, network_type))
    
    update_desktop = []
    for desktop_id, desktop in desktops.items():
        ret = Nic.alloc_desktop_nics(desktop, network_id)
        if isinstance(ret, Error):
            return ret
        
        if not ret:
            break
        
        update_desktop.append(desktop_id)

    return update_desktop

def modify_desktop_ip(desktop, network, private_ip):

    ctx = context.instance()
    network_id = network["network_id"]
    desktop_id = desktop["desktop_id"]
    
    ret = ctx.pgm.get_desktop_nics(desktop_id, network_id=network_id)
    if not ret:
        return None
    
    ret = Nic.desktop_detach_nics(desktop_id, network_id)
    if isinstance(ret, Error):
        return ret
    
    attach_desktop = ret
    
    ret = Nic.alloc_desktop_nics(desktop, network_id, private_ip)
    if isinstance(ret, Error):
        return ret
    
    detach_desktop = ret
    
    if detach_desktop or attach_desktop:
        return desktop_id
    
    return None

def format_citrix_desktop(desktops):
    
    ctx = context.instance()
    if not desktops:
        return []
    
    format_desktop_policy_group(desktops)
    desktop_ids = desktops.keys()
    desktop_nics = {}
    ret = ctx.pgm.get_desktop_nics(desktop_ids)
    if ret:
        desktop_nics = ret
    
    filter_key = ["need_update", "connect_time", "connect_status", "filetransfer",
                  "in_domain", "clipboard", "no_sync", "login_time", "logout_time", "usbredir", "need_monitor", "auto_login"]
    for desktop_id, desktop in desktops.items():
        
        for key, _ in desktop.items():
            if key in filter_key:
                del desktop[key]
        
        desktop["nics"] = desktop_nics.get(desktop_id, [])
        
    return desktops.values()

def format_delivery_group_desktop(delivery_group_set, verbose):
    
    ctx = context.instance()
    for delivery_group_id, delivery_group in delivery_group_set.items():
        desktops = ctx.pgm.get_desktops(delivery_group_id=delivery_group_id, has_disk=True)
        if not desktops:
            desktops = {}
        
        if verbose:
            delivery_group["desktops"] = format_citrix_desktop(desktops)
        
        delivery_group["desktop_count"] = len(desktops)
        
        users = ctx.pgm.get_delivery_group_user(delivery_group_id)
        if not users:
            users = {}
        
        if verbose:
            ret = ctx.pgm.get_user_and_user_group_names(users.keys())
            if ret:
                for user_id, user in users.items():
                    name= ret.get(user_id, '')
                    if name !="":
                        user["user_name"]=name   
                    else:
                        user["user_name"]=user["user_name"]+"[-userdel]"
            delivery_group["users"] = users.values()
        delivery_group["user_count"] = len(users)

        group_policys = ctx.pgm.get_resource_group_policy(delivery_group_id)
        if group_policys:
            policy_groups = ctx.pgm.get_policy_groups(group_policys.values(), extras=[])
            if policy_groups:
                delivery_group["group_policy"] = policy_groups.values()

    return None

def get_desktop_id(hostname):
    ''' get desktop id by hostname '''
    ctx = context.instance()  
    columns = ["desktop_id", "hostname"]
    # get desktop_id from db
    try:
        result = ctx.pg.base_get(TB_DESKTOP, {}, columns)
        if not result:
            logger.error("get desktop [%s] failed" % hostname)
            return None
    except Exception,e:
        logger.error("get desktop id with Exception:%s" % e)
        return None
    
    for item in result:
        for key in item.keys():
            if key == "hostname" and item[key].upper() == hostname:
                desktop_id = item["desktop_id"]
                return desktop_id
                
    return None

def _clean_download_log_file(file_name, base_path=const.DOWNLOAD_LOG_DIR):

    for dirpath, _, filenames in os.walk(base_path):
        if file_name in filenames:
            file_path = os.path.join(dirpath, file_name)
            os.remove(file_path)

    return None

def pack_pitrix_log(filename,target_host_list,date):

    for target_host in target_host_list:
        cmd = ('rm -fr %s /tmp/%s' % (target_host,target_host))
        logger.info("cmd == %s" % (cmd))
        exec_cmd(cmd)

        cmd = ('mkdir -p %s /tmp/%s' % (target_host,target_host))
        logger.info("cmd == %s" % (cmd))
        exec_cmd(cmd)

        cmd = ('scp -r root@%s:/pitrix/log/*wf  %s' % (target_host,target_host))
        logger.info("cmd == %s" % (cmd))
        exec_cmd(cmd)

        files = os.listdir("./%s" %(target_host))
        for f in files:
            #  grep -r "2019-04-09" ./vdi0/desktop_server.log.wf > /tmp/vdi0/desktop_server.log.wf
            os.system("grep -r %s ./%s/%s  > /tmp/%s/%s" %(date,target_host,f,target_host,f))

    cmd = ('tar czvf pitrix_log.tar.gz /tmp/*vdi[0-9]')
    logger.info("cmd == %s" % (cmd))
    exec_cmd(cmd)

    cmd = ('cp -fr pitrix_log.tar.gz %s' %(filename))
    logger.info("cmd == %s" % (cmd))
    exec_cmd(cmd)

def _pack_download_log_file(filename,date):

    ctx = context.instance()
    target_host_list = get_target_host_list(ctx)
    logger.info("get_target_host_list target_host_list == %s" %(target_host_list))
    if target_host_list:
        #Create a child thread to perform the operation of packing the log
        t = threading.Thread(target=pack_pitrix_log,args=(filename,target_host_list,date,))
        t.start()
        t.join()

def download_pitrix_log(date):

    if not os.path.isdir(const.DOWNLOAD_LOG_DIR):
        os.system("mkdir -p %s" % const.DOWNLOAD_LOG_DIR)
        os.system("chmod 777 %s" % const.DOWNLOAD_LOG_DIR)

    # clean old download log file
    download_log_name = "pitrix_log.%s.tar.gz" %(date)
    _clean_download_log_file(download_log_name, const.DOWNLOAD_LOG_DIR)

    pitrix_logs = {}
    pitrix_logs["download_log_file_uri"] = "%s/%s" % (const.DOWNLOAD_LOG_BASE_URI, download_log_name)
    filename = "%s/%s" %(const.DOWNLOAD_LOG_DIR,download_log_name)
    _pack_download_log_file(filename,date)
    return pitrix_logs


def check_desktop_in_domain(zone, hostname):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_zone_auth(zone)
    if not ret:
        return None
    
    auth_service = ret
    if auth_service["auth_service_type"] == const.AUTH_TYPE_LOCAL:
        return None
    
    auth_service_id = auth_service["auth_service_id"]
    
    ret = ctx.auth.get_auth_computes(auth_service_id, compute_names=[hostname])
    if ret:
        logger.error("desktop name %s in domain" % (hostname))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKTOP_NAME_ALREADY_EXISTED_IN_DOMAIN, (hostname))
    
    return None
