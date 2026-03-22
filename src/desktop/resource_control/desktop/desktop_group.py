
from utils.misc import filter_out_none
import constants as const
import db.constants as dbconst
from log.logger import logger
from utils.misc import get_current_time
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.id_tool import(
    UUID_TYPE_DESKTOP_GROUP,
    UUID_TYPE_DESKTOP_GROUP_DISK,
    UUID_TYPE_DESKTOP_GROUP_NETWORK,
    get_uuid,
    UUID_TYPE_DESKTOP,
    UUID_TYPE_DESKTOP_IMAGE
)

from common import (
    is_normal_user,
    is_normal_console,
    is_citrix_platform,
    check_normal_console,
    check_global_admin_console,
    check_admin_console,
    get_sort_key,
    get_reverse,
    check_resource_transition_status
)

import resource_control.desktop.network as Network
import resource_control.desktop.nic as Nic
import resource_control.desktop.disk as Disk
import resource_control.desktop.job as Job
import resource_control.desktop.desktop as Desktop
import resource_control.desktop.desktop_common as Desktopcomm
import resource_control.permission as Permission
import resource_control.policy.usb as UsbPlicy
import resource_control.policy.policy_group as PolicyGroup
import resource_control.zone.zone as Zone
from distutils.command.config import config

# desktop group common

def send_desktop_group_job(sender, desktop_group_ids, action, citrix_update=None):
    
    if not isinstance(desktop_group_ids, list):
        desktop_group_ids = [desktop_group_ids]
    
    directive = {
                "sender": sender,
                "action": action,
                "desktop_groups" : desktop_group_ids,
                }
    if citrix_update:
        directive["citrix_update"] = citrix_update

    ret = Job.submit_desktop_job(action, directive, desktop_group_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    
    return job_uuid

def check_desktop_group_user_vaild(user_ids, desktop_group_id=None, is_attach=False, is_detach=False, status=const.USER_STATUS_ACTIVE):

    ctx = context.instance()
    if not isinstance(user_ids, list):
        user_ids = [user_ids]
    
    users = ctx.pgm.get_desktop_users(user_ids)
    if not users:
        logger.error("no found user %s" % user_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, user_ids)
    
    desktop_group_user = {}
    if desktop_group_id:
        ret = ctx.pgm.get_desktop_group_users(desktop_group_id)
        if ret:
            desktop_group_user = ret

    for user_id in user_ids:
        user = users.get(user_id)
        if not user:
            logger.error("user %s not found or status disable" % user_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, user_id)
        
        if status:
            if user["status"] != status:
                logger.error("user %s status %s dismatch" % (user_id, status))
                return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_USER_STATUS_NO_ACTIVE, user_id)
            
            dg_user = desktop_group_user.get(user_id)
            if dg_user:
                if dg_user["status"] != status:
                    logger.error("user %s status %s dismatch" % (user_id, status))
                    return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_USER_STATUS_NO_ACTIVE, user_id)
        
        if is_attach and user_id in desktop_group_user:
            logger.error("user %s already in desktop group %s" % (user_id, desktop_group_user))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_GROUP_USER_EXISTED, (user_id, desktop_group_id))

        if is_detach and user_id not in desktop_group_user:
            logger.error("user %s no found in desktop group %s" % (user_id, desktop_group_user))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_GROUP_USER_NO_EXISTED, (user_id, desktop_group_id))

    return users

def check_desktop_group_vaild(desktop_group_ids, status=const.DG_STATUS_MAINT, check_desktop_status=False, desktop_group_type=None,check_modify_image=False):
    
    ctx = context.instance()
    
    if not isinstance(desktop_group_ids, list):
        desktop_group_ids = [desktop_group_ids]
    
    desktop_groups = {}
    for desktop_group_id in desktop_group_ids:
        desktop_group = ctx.pgm.get_desktop_group(desktop_group_id, extras=[dbconst.TB_DESKTOP])
        if not desktop_group:
            logger.error("desktop group [%s] no found" % desktop_group_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_group_id)
        
        if desktop_group_type and desktop_group["desktop_group_type"] != desktop_group_type:
            logger.error("desktop group %s type [%s][%s] dismatch" % (desktop_group_id, desktop_group["desktop_group_type"], desktop_group_type))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_GROUP_TYPE_DISMATCH, desktop_group_id)

        if check_modify_image:
            if desktop_group["desktop_group_type"] == const.DG_TYPE_STATIC and desktop_group["save_desk"] == const.DESKTOP_RULE_SAVE:
                logger.error("static desktop group [%s] choose save system disk cant update image" % (desktop_group_id))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_SAVE_DESKTOP_CANT_UPDATE_IMAGE, desktop_group_id)

        # check desktop grouup transition status
        ret = check_resource_transition_status({desktop_group_id: desktop_group})
        if isinstance(ret, Error):
            return ret

        # check desktop transition status
        desktops = desktop_group["desktops"]
        if check_desktop_status and desktops:
            ret = check_resource_transition_status(desktops)
            if isinstance(ret, Error):
                return ret
        
        if desktop_group["desktop_group_type"] != const.DG_TYPE_CITIRX:
            if status and desktop_group["status"] != status:
                logger.error("desktop group status dismatch %s %s" % (desktop_group["status"], status))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_DESKTOP_GROUP_STATUS_DISMATCH)
        
        desktop_groups[desktop_group_id] = desktop_group

    return desktop_groups

def set_desktop_group_apply(desktop_group_id, is_apply):

    # set desktop group is_apply flag
    ctx = context.instance()
    
    ret = ctx.pgm.get_desktop_group(desktop_group_id, extras=[])
    if not ret:
        logger.error("no found desktop group[%s] " % (desktop_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    desktop_group = ret
    if desktop_group["desktop_group_type"] == const.PLATFORM_TYPE_CITRIX:
        return desktop_group_id
    
    ctx = context.instance()
    update_info = {"is_apply": is_apply}
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_GROUP, {desktop_group_id: update_info}):
        logger.error("Failed to update desktop group[%s] to apply %s" % (desktop_group_id, is_apply))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return desktop_group_id

def set_desktop_need_update(desktop_ids, need_update):
    
    ctx = context.instance()
    desktop_update = {desktop_id: {"need_update": need_update} for desktop_id in desktop_ids}
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, desktop_update):
        logger.error("set desktop need update fail %s, %s" % (desktop_ids, need_update))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return desktop_ids

def format_desktop_group_platform(desktop_group):
    
    if not desktop_group:
        return None

    ctx = context.instance()
    filter_keys = ["managed_resource", "citrix_uuid", "allocation_type"]
    if desktop_group["desktop_group_type"] == const.DG_TYPE_CITIRX:
        filter_keys = ["usbredir", "clipboard", "filetransfer", "naming_count", "is_apply", "is_create"]
        image = desktop_group.get("image")
        if image:
            session_type = image.get("session_type")
            desktop_group["session_type"] = session_type
        
        desktop_group_id = desktop_group["desktop_group_id"]
        desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
        if not desktops:
            desktops = {}
        
        desktop_group["desktop_count"] = len(desktops)
        
    for filter_key in filter_keys:
        if filter_key not in desktop_group:
            continue
        del desktop_group[filter_key]

    return None

def desktop_group_stat(desktop_group_id):
    
    ctx = context.instance()
    
    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
    if not desktops:
        desktops = {}
    
    users = ctx.pgm.get_desktop_group_users(desktop_group_id)
    if not users:
        users = {}
    
    desktop_status = {}
    trans_count = 0
    running_count = 0
    stopped_count = 0

    for _, desktop in desktops.items():
        
        status = desktop["status"]
        transition_status = desktop["transition_status"]
        if transition_status:
            trans_count = trans_count + 1
            continue
        
        if status in [const.INST_STATUS_RUN]:
            running_count = running_count + 1
            continue
        
        else:
            stopped_count = stopped_count + 1
    
    desktop_status[const.INST_STATUS_TRANS] = trans_count
    desktop_status[const.INST_STATUS_RUN] = running_count
    desktop_status[const.INST_STATUS_STOP] = stopped_count
    
    user_desktop = {
        "desktop_stats": desktop_status,
        "user_count": len(users)
        }
    
    return user_desktop

def update_desktop_group_use_stat(desktop_group):

    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]
    free_count = 0
    total_count = 0

    use_stat = {
        "free_count": free_count,
        "total_count": total_count
        }

    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
    if not desktops:
        desktop_group["use_stat"] = use_stat
        return None
    
    total_count = len(desktops)
    for _, desktop in desktops.items():
        delivery_group_id = desktop["delivery_group_id"]
        if not delivery_group_id:
            free_count = free_count + 1
    
    use_stat["free_count"] = free_count
    use_stat["total_count"] = total_count
    
    desktop_group["use_stat"] = use_stat
    
    return None

def check_desktop_dn(desktops):
    
    ctx = context.instance()
    
    if not desktops:
        return None
    
    desktop_ou = {}
    for desktop_id, desktop in desktops.items():
        
        desktop_dn = desktop.get("desktop_dn")
        if not desktop_dn:
            continue
        
        dn_guid = desktop.get("dn_guid") 
        if dn_guid:
            continue
        
        desktop_ou[desktop_id] = desktop_dn
    
    if not desktop_ou:
        return None
    
    update_guid = {}
    ret = ctx.pgm.get_ou_guids(desktop_ou.values())
    if not ret:
        return None
    for desktop_id, ou_dn in desktop_ou.items():
        guid = ret.get(ou_dn)
        if not guid:
            continue
        
        update_guid[desktop_id] = {"dn_guid": guid}
    
    if update_guid:
        ctx.pg.batch_update(dbconst.TB_DESKTOP, update_guid)
        
    return

# describe desktop groups
def format_desktop_groups(sender, desktop_group_set, verbose = 0,check_desktop_dn_flag=0):

    ctx = context.instance()
    need_check_ou_list=[]
    for desktop_group_id, desktop_group in desktop_group_set.items():
        desktop_group_type = desktop_group["desktop_group_type"]
        if check_normal_console(sender):
            if desktop_group_type == const.DG_TYPE_RANDOM:
    
                transition_status = desktop_group["transition_status"]
                if transition_status:
                    desktop_group["free_desktop"] = 0
                else:
                    random_desktop = ctx.pgm.get_free_random_desktops(desktop_group_id)
                    desktop_group["free_desktop"] = len(random_desktop) if random_desktop else 0

            continue
    
        elif verbose:
            ret = ctx.pgm.get_desktop_group(desktop_group_id, extras=[dbconst.TB_DESKTOP_GROUP_NETWORK,
                                                                      dbconst.TB_DESKTOP_GROUP_USER,
                                                                      dbconst.TB_DESKTOP_GROUP_DISK,
                                                                      dbconst.TB_DESKTOP_IMAGE])
            if ret:
                group_disks = ctx.pgm.get_desktop_group_disk(desktop_group_id)
                if group_disks:
                    ret["group_disks"] = group_disks

                group_policys = ctx.pgm.get_resource_group_policy(desktop_group_id)
                if group_policys:
                    policy_groups = ctx.pgm.get_policy_groups(group_policys.values(), extras=[])
                    if policy_groups:
                        ret["group_policy"] = policy_groups.values()
                desktop_group_set[desktop_group_id] = ret

        else:
            desktop_image_id = desktop_group["desktop_image_id"]
            if desktop_image_id:
                desktop_image = ctx.pgm.get_desktop_image(desktop_image_id)
                if desktop_image:
                    desktop_group["image"] = desktop_image
           
        # format qingcloud/citrix desktop
        desktop_group = desktop_group_set[desktop_group_id]

        desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
        if desktops:
            desktop_group["desktop_ids"] = desktops.keys()
        
        check_desktop_dn(desktops)

        user_desktop = desktop_group_stat(desktop_group_id)
        desktop_group["user_desktop"] = user_desktop
        
        if is_citrix_platform(ctx, sender["zone"]):
            update_desktop_group_use_stat(desktop_group)
        
        if desktop_group.get("gpu"):
            gpu_class = desktop_group["gpu_class"]
            gpu_info = Zone.check_gpu_config(sender)
            if not gpu_info:
                gpu_info = []
            
            for gpu in gpu_info:
                if gpu_class == gpu["gpu_class"]:
                    desktop_group["gpu_info"] = gpu
                    break

        format_desktop_group_platform(desktop_group)
        if not is_citrix_platform(ctx, sender["zone"]):
            desktop_group["usb_policy"] = UsbPlicy.describe_usb_policy({"object_id": desktop_group_id})
        
        if check_desktop_dn_flag != 1:
            continue
        else :
            if is_citrix_platform(ctx, sender["zone"]):        
                need_check_ou_list.append(desktop_group["desktop_group_name"])
            else:
                ret = check_desktop_group_desktop_dn(sender["zone"], desktop_group.get("desktop_dn"), desktop_group, check_citrix=False)
                if isinstance(ret, Error):
                    desktop_group["check_invalid_status"] = const.DG_STATUS_DESKTOP_DN_INVAILD
                    
    if need_check_ou_list:
        need_check_citrix_deskotp_group_dn(need_check_ou_list,desktop_group_set,sender["zone"])
            
    return desktop_group_set

def need_check_citrix_deskotp_group_dn(need_check_deskotp_group_dn,desktop_group_set,zone):
    ctx = context.instance()
    ret = ctx.res.resource_describe_computer_catalogs(zone, need_check_deskotp_group_dn, verbose=1)
    logger.error("no found computer catalog %s" % ret)
    if not ret:
        logger.error("no found computer catalog ")
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    catalogs=ret
    
    for desktop_group in desktop_group_set.values():  
        ret = check_desktop_group_desktop_dn(zone, desktop_group.get("desktop_dn"))
        if isinstance(ret, Error):
            desktop_group["check_invalid_status"] = const.DG_STATUS_DESKTOP_DN_INVAILD            
            continue   
        if ret is None:
            continue
                                    
        desktop_group_name = desktop_group["desktop_group_name"]  
        desktop_dn = desktop_group["desktop_dn"]  
    
        catalog = catalogs.get(desktop_group_name)
        if not catalog:
            logger.error("no found computer catalog %s" % desktop_group_name)
            desktop_group["check_invalid_status"] = const.DG_STATUS_DESKTOP_DN_INVAILD
            continue
        _desktop_dn = catalog.get("desktop_dn")
        if _desktop_dn != desktop_dn:     
            logger.error("catalog %s desktop_dn is not same " % desktop_group_name)
            desktop_group["check_invalid_status"] = const.DG_STATUS_DESKTOP_DN_INVAILD
            continue    

# create desktop group
def build_desktop_group_type(desktop_group_type, req):

    if desktop_group_type == const.DG_TYPE_CITIRX:

        allocation_type = req.get("allocation_type")
        if desktop_group_type not in [const.DG_TYPE_CITIRX] or not allocation_type:
            logger.error("citrix platform desktop group type dismatch %s" % desktop_group_type)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_GROUP_TYPE_DISMATCH_PLATFORM, desktop_group_type)

        save_desk = const.DESKTOP_RULE_SAVE
        save_disk = req.get("save_disk")
        if allocation_type == const.CITRIX_DG_TYPE_STATIC:
            if not save_disk:
                save_disk = const.DESKTOP_RULE_SAVE
            save_desk = const.DESKTOP_RULE_SAVE
        else:
            save_disk = const.DESKTOP_RULE_NOSAVE
            save_desk = const.DESKTOP_RULE_NOSAVE

        req["save_desk"] = save_desk
        req["save_disk"] = save_disk
    else:
        if desktop_group_type not in [const.DG_TYPE_PERSONAL, const.DG_TYPE_RANDOM, const.DG_TYPE_STATIC]:
            logger.error("citrix platform desktop group type dismatch %s" % desktop_group_type)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_GROUP_TYPE_DISMATCH_PLATFORM, desktop_group_type)

        save_desk = req.get("save_desk")
        if desktop_group_type in [const.DG_TYPE_PERSONAL]:
            save_desk = const.DESKTOP_RULE_SAVE
        elif desktop_group_type in [const.DG_TYPE_RANDOM]:
            save_desk = const.DESKTOP_RULE_NOSAVE
        else:
            if not save_desk:
                save_desk = const.DESKTOP_RULE_NOSAVE
    
        req["save_desk"] = save_desk
        save_disk = req.get("save_disk")
        if desktop_group_type in [const.DG_TYPE_PERSONAL]:
            save_disk = const.DESKTOP_RULE_SAVE
        elif desktop_group_type in [const.DG_TYPE_RANDOM]:
            save_disk = const.DESKTOP_RULE_NOSAVE
        else:
            if not save_disk:
                save_disk = const.DESKTOP_RULE_NOSAVE

        req["save_disk"] = save_disk

    return None

def register_app_desktop_group(sender, req):
    
    ctx = context.instance()
    
    desktop_group_id = get_uuid(UUID_TYPE_DESKTOP_GROUP, ctx.checker)
    desktop_group_info = dict(
                              desktop_group_id = desktop_group_id,
                              desktop_group_name = req.get("desktop_group_name", ''),
                              desktop_group_type = const.DG_TYPE_CITIRX,
                              desktop_image_id = '',
                              provision_type = const.PROVISION_TYPE_MANUAL,
                              managed_resource = req["managed_resource"],
                              cpu = 0,
                              memory = 0,
                              allocation_type = const.CITRIX_DG_TYPE_RANDOM,
                              status = const.DG_STATUS_MAINT if not is_citrix_platform(ctx, sender["zone"]) else const.DG_STATUS_NORMAL,
                              create_time = get_current_time(),
                              status_time = get_current_time(),
                              is_apply = 0,
                              owner = sender["owner"],
                              zone = sender["zone"],
                              )

    # register desktop group
    if not ctx.pg.insert(dbconst.TB_DESKTOP_GROUP, desktop_group_info):
        logger.error("insert newly created desktop group for [%s] to db failed" % (desktop_group_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    ret = Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_DESKTOP_GROUP, desktop_group_id, zone_id=sender["zone"])
    if isinstance(ret, Error):
        return ret

    return desktop_group_id

def register_desktop_group(sender, req):
    
    ctx = context.instance()
    desktop_group_keys = ["desktop_group_type", 'cpu', 'memory', 'desktop_count', 'gpu', 'gpu_class', 'ivshmem_enable', 
                          'is_create', "save_desk", "save_disk", 'usbredir', 'clipboard', 'filetransfer', 'qxl_number',
                          'description', 'desktop_group_name', "instance_class", "naming_rule", "desktop_dn", "place_group_id", "cpu_model", "cpu_topology"]
    base_config = filter_out_none(req, desktop_group_keys)
    
    desktop_dn = base_config.get("desktop_dn")
    if desktop_dn:
        ret = ctx.pgm.get_ou_guid(desktop_dn)
        if ret:
            base_config["dn_guid"] = ret
    
    desktop_group_id = get_uuid(UUID_TYPE_DESKTOP_GROUP, ctx.checker)
    desktop_group_info = dict(
                              desktop_group_id = desktop_group_id,
                              desktop_group_name = req.get("desktop_group_name", ''),
                              desktop_image_id = req["desktop_image"],
                              image_name = req.get("image_name", ''),
                              qxl_number = req.get("qxl_number", 1),
                              status = const.DG_STATUS_MAINT if not is_citrix_platform(ctx, sender["zone"]) else const.DG_STATUS_NORMAL,
                              create_time = get_current_time(),
                              status_time = get_current_time(),
                              provision_type = req.get("provision_type", const.PROVISION_TYPE_MCS),
                              is_apply = 0,
                              owner = sender["owner"],
                              zone = sender["zone"],
                              )
    desktop_group_info.update(base_config)

    # register desktop group
    if not ctx.pg.insert(dbconst.TB_DESKTOP_GROUP, desktop_group_info):
        logger.error("insert newly created desktop group for [%s] to db failed" % (desktop_group_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    if is_citrix_platform(ctx, sender["zone"]):
        ret = update_citrix_desktop_group(sender, desktop_group_id, req)
        if isinstance(ret, Error):
            return ret

    ret = Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_DESKTOP_GROUP, desktop_group_id, zone_id=sender["zone"])
    if isinstance(ret, Error):
        return ret

    return desktop_group_id

def check_desktop_group_attributes(sender, need_maint_columns):
    
    # ivshmem
    ivshmem_enable = need_maint_columns.get("ivshmem_enable", 0)
    ret = check_desktop_group_ivshmem(sender["zone"], ivshmem_enable)
    if isinstance(ret, Error):
        return ret
    
    # desktop_dn
    desktop_dn = need_maint_columns.get("desktop_dn")
    ret = check_desktop_group_desktop_dn(sender["zone"], desktop_dn)
    if isinstance(ret, Error):
        return ret

    # check gpu
    gpu = need_maint_columns.get("gpu", 0)
    gpu_class = need_maint_columns.get("gpu_class", 0)
    if gpu:
        ret = Desktopcomm.check_desktop_group_gpus(sender, 1, gpu, gpu_class)
        if isinstance(ret, Error):
            return ret

    return None

def check_desktop_group_ivshmem(zone, ivshmem_enable):
    
    ctx = context.instance()

    ret = ctx.zone_checker.get_resource_limit(zone, "ivshmem")
    if ivshmem_enable and not ret:
        logger.error("no config ivshmem")
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_ILLEGAL_IVSHMEM_CONFIG)
    return ret

def check_desktop_group_desktop_dn(zone, desktop_dn, desktop_group=None, check_citrix=False):
    
    ctx = context.instance()
    if not desktop_dn:
        return None
    desktop_dn = desktop_dn.replace('DC=','dc=').replace('CN=','cn=').replace('OU=','ou=')
    ret = ctx.pgm.get_auth_zone(zone)
    if not ret:
        logger.error("no found zone %s auth service" % zone)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKTOP_DN_CONFIG)
    
    auth_service = ret
    auth_service_id = auth_service["auth_service_id"]
    
    if auth_service_id:
        auth_service = ctx.pgm.get_auth_service(auth_service_id)
        if not auth_service:
            return None
    
        if auth_service["auth_service_type"] == const.AUTH_TYPE_LOCAL:
            return None
    ret = ctx.pgm.get_desktop_ous(auth_service_id, desktop_dn)
    if not ret:
        logger.error("no found ou %s " % desktop_dn)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKTOP_DN_CONFIG)

    if not check_citrix or not desktop_group:
        return None
    
    if not is_citrix_platform(ctx, zone):
        return None

    desktop_group_name = desktop_group["desktop_group_name"]
    ret = ctx.res.resource_describe_computer_catalogs(zone, desktop_group_name, verbose=1)
    if not ret:
        logger.error("no found computer catalog %s" % desktop_group_name)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
    catalog = ret.get(desktop_group_name)
    if not catalog:
        return None

    _desktop_dn = catalog.get("desktop_dn")
    if _desktop_dn != desktop_dn:
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKTOP_DN_CONFIG)

    return None

def check_same_domain_zone(zone_id):
    
    ctx = context.instance()
    ret = ctx.pgm.get_zone_auth(zone_id)
    if not ret:
        return zone_id
    
    auth_service = ret
    domain = auth_service["domain"]
    
    ret = ctx.pgm.get_auth_service_by_domain(domain)
    if not ret:
        return zone_id
    
    auth_service_ids = ret.keys()
    
    ret = ctx.pgm.get_zone_by_auth_services(auth_service_ids)
    if not ret:
        return zone_id
    
    return ret.keys()

def check_desktop_group_naming_rule(zone_id, naming_rule):
    
    ctx = context.instance()

    if is_citrix_platform(ctx, zone_id):
        return None
    
    ret = check_same_domain_zone(zone_id)
    zone_ids = ret

    ret = ctx.pgm.get_desktop_group_naming_rule(zone_ids)
    if not ret:
        return None

    name_rules = ret
    if naming_rule.upper() in name_rules:
        logger.error("desktop group name rule %s has already existed" % naming_rule)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_NAMING_RULE_EXISTED, (naming_rule))
    return None

def check_desktop_group_name(zone_id, desktop_group_name):
    
    ctx = context.instance()

    ret = ctx.pgm.get_desktop_group_by_name(desktop_group_name, zone=zone_id)
    if ret:
        logger.error("desktop group name %s has already existed" % desktop_group_name)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKTOP_GROUP_NAMING_EXISTED, (desktop_group_name))
        
    return None

def create_desktop_group(sender, req, additional_params={}):
    
    ctx = context.instance()
    desktop_group_type = req["desktop_group_type"]
    if desktop_group_type not in [const.DG_TYPE_RANDOM] and not is_citrix_platform(ctx, sender["zone"]):
        if "desktop_count" in req:
            del req["desktop_count"]
    
    ret = register_desktop_group(sender, req)
    if isinstance(ret, Error):
        return ret   
    desktop_group_id = ret

    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
    if not desktop_group:
        logger.error("desktop group resource not found %s " % desktop_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_group_id)

    # add disk config
    disk_configs = additional_params.get("disk_configs")
    if disk_configs:
        for disk_config in disk_configs:
            ret = create_disk_config(desktop_group, disk_config)
            if isinstance(ret, Error):
                return ret

    # add network config
    network_configs = additional_params.get("network_config")
    if network_configs:
        ret = add_desktop_group_network(desktop_group, network_configs)
        if isinstance(ret, Error):
            return ret

    security_group_id = req.get("security_group", "")
    if security_group_id:
        ret = PolicyGroup.add_resource_group_policy(sender, security_group_id, desktop_group_id, dbconst.RESTYPE_DESKTOP_GROUP, const.POLICY_TYPE_SECURITY)
        if isinstance(ret, Error):
            return ret

    # add user to desktop group
    if is_citrix_platform(ctx, sender["zone"]):
        return desktop_group_id
    
    users = additional_params.get("users", [])
    if users:
        ret = attach_user_to_dekstop_group(desktop_group, users)
        if isinstance(ret, Error):
            return ret

    is_create = req.get("is_create", 1)
    if is_create:
        if desktop_group_type in [const.DG_TYPE_RANDOM]:
            desktop_count = req.get("desktop_count", 0)
            if desktop_count > 0:
                set_desktop_group_apply(desktop_group_id, 1)
        else:
            if len(users) > 0:
                set_desktop_group_apply(desktop_group_id, 1)
    
    return desktop_group_id

# modify desktop group attributes
def modify_resource_desktop_group_name(desktop_group_id, desktop_group_name):

    ctx = context.instance()
    # desktop
    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
    if desktops:
        desktop_ids = desktops.keys()
        update_info = {desktop_id: {"desktop_group_name": desktop_group_name} for desktop_id in desktop_ids}
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_info):
            logger.error("update desktop group name to desktop fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    # disk
    disks = ctx.pgm.get_disks(desktop_group_ids=desktop_group_id)
    if disks:
        disk_ids = disks.keys()
        update_info = {disk_id: {"desktop_group_name": desktop_group_name} for disk_id in disk_ids}
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_info):
            logger.error("update desktop group name to disk fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    # nic
    nics = ctx.pgm.get_nics(desktop_group_id=desktop_group_id)
    if nics:
        nic_ids = nics.keys()
        update_info = {nic_id: {"desktop_group_name": desktop_group_name} for nic_id in nic_ids}
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_NIC, update_info):
            logger.error("update desktop group name to nic fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    update_info = {desktop_group_id: {"desktop_group_name": desktop_group_name}}
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_GROUP, update_info):
        logger.error("update desktop group name to desktop group fail %s" % update_info)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def modify_image_to_desktop(sender, desktop_group, desktop_image):

    ctx = context.instance()
    desktop_image_name = desktop_image["image_name"]
    desktop_image_id = desktop_image["desktop_image_id"]
    desktop_group_type = desktop_group["desktop_group_type"]
    desktop_group_id = desktop_group["desktop_group_id"]
    if is_citrix_platform(ctx, sender["zone"]):
        return None
    
    if desktop_group_type not in [const.DG_TYPE_RANDOM, const.DG_TYPE_STATIC]:
        return None
    
    # desktop
    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
    if not desktops:
        return None

    desktop_ids = desktops.keys()
    update_info = {desktop_id: {"image_name": desktop_image_name, "desktop_image_id": desktop_image_id} for desktop_id in desktop_ids}
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_info):
        logger.error("update desktop group name to desktop fail %s" % update_info)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    return None

def modify_desktop_group_image(sender, desktop_group, desktop_image):

    ctx = context.instance()
    
    if is_citrix_platform(ctx, sender["zone"]):
        return None
    
    desktop_image_id = desktop_image["desktop_image_id"]
    desktop_group_id = desktop_group["desktop_group_id"]   
    update_info = {"desktop_image_id": desktop_image_id, "image_name": desktop_image["image_name"]}
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_GROUP, {desktop_group_id: update_info}):
        logger.error("modify desktop group update fail %s" % desktop_group_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    ret = modify_image_to_desktop(sender, desktop_group, desktop_image)
    if isinstance(ret, Error):
        return ret
    return None

def update_citrix_desktop_group(sender, desktop_group_id, req):
    
    ctx = context.instance()
    zone_id = sender["zone"]
    managed_resource = req["managed_resource"]
    ret = ctx.zone_checker.check_managed_resource(zone_id, managed_resource)
    if isinstance(ret, Error):
        return ret
    
    allocation_type = req.get("allocation_type", const.CITRIX_ALLOC_TYPE_STATIC)
    if allocation_type not in const.SUPPORTED_CITIRX_ALLOC_TYPES:
        logger.error("allocation type unsupported %s" % allocation_type)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_CITIRX_ALLOC_TYPE_DISMATCH, allocation_type)
    
    update_info = {
                    "managed_resource": managed_resource,
                    "allocation_type": allocation_type,
                  }
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_GROUP, {desktop_group_id: update_info}):
        logger.error("update citrix desktop group %s fail" % update_info)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return desktop_group_id

def get_ivshmem_value(sender, ivshmem_enable):

    ctx = context.instance()
    zone_id = sender["zone"]
    
    ivshmem = ctx.zone_checker.get_resource_limit(zone_id, "ivshmem")
    if not ivshmem:
        return None
    
    ivshmem_value = None
    if ivshmem_enable == 0:
        ivshmem_value = "none"
    elif ivshmem_enable == 1:
        ivshmem_value = ivshmem
        
    if not ivshmem_value:
        return None
    
    return ivshmem_value
    
def modify_citrix_computer_catalog(sender, desktop_group, columns):

    ctx = context.instance()

    modify_keys = ["desktop_image_id", "cpu", "memory", "ivshmem_enable", "gpu", "gpu_class", "description", "desktop_dn"]

    desktop_group_name = desktop_group["desktop_group_name"]
    
    update_info = {}
    for modify_key, modify_value in columns.items():
        
        if modify_key not in modify_keys:
            continue
        
        if modify_value == desktop_group[modify_key]:
            continue
        
        if modify_key == "ivshmem_enable":
            ivshmem_value = get_ivshmem_value(sender, modify_value)
            modify_value = ivshmem_value if ivshmem_value else ''

        update_info[modify_key] = modify_value
    
    if not update_info:
        return None
    
    if "memory" in update_info and update_info["memory"]:
        update_info["memory"] = update_info["memory"]/1024
    
    ret = ctx.res.resource_modify_computer_catalog(sender["zone"], desktop_group_name, update_info)
    if not ret:
        logger.error("ddc modify computer catalog %s fail" % desktop_group_name)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def update_desktop_group_ivshmem_resource(desktop_group, columns):
    
    ctx = context.instance()
    
    if "ivshmem_enable" not in columns:
        return None
    ivshmem_enable = columns["ivshmem_enable"]
    
    desktops = desktop_group.get("desktops")
    if not desktops:
        return None

    desktop_ids = desktops.keys()
    
    update_info = {}
    for desktop_id in desktop_ids:
        update_info[desktop_id] = {"ivshmem_enable": ivshmem_enable}
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_info):
        logger.error("update desktop group ivshmem %s fail" % ivshmem_enable)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def modify_desktop_group_attributes(sender, desktop_group, columns):

    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]

    modify_keys = ["cpu", "memory", "ivshmem_enable", "gpu", "gpu_class", "desktop_count", "desktop_group_name",
                                           'usbredir', 'clipboard', 'filetransfer', 'qxl_number', "is_create", "description", "desktop_dn"]

    update_info = {}
    for modify_key, modify_value in columns.items():
        
        if modify_key not in modify_keys:
            continue
        
        if modify_value == desktop_group[modify_key]:
            continue

        update_info[modify_key] = modify_value
    
    if not update_info:
        return None
    
    compute_catalog = None
    if is_citrix_platform(ctx, sender["zone"]):
        ret = modify_citrix_computer_catalog(sender, desktop_group, columns)
        if isinstance(ret, Error):
            return ret
        
        compute_catalog = ctx.res.resource_describe_computer_catalogs(sender["zone"], desktop_group["desktop_group_name"], 1)
        if not compute_catalog:
            logger.error("no found compute catalog %s " % desktop_group["desktop_group_name"])
            return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_GROUP, {desktop_group_id: update_info}):
        logger.error("modify desktop group update fail %s" % desktop_group_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    if "desktop_dn" in update_info:
        conditions = {"desktop_group_id": desktop_group_id}
        ctx.pg.base_update(dbconst.TB_DESKTOP, conditions, {"desktop_dn": update_info["desktop_dn"]})
    
    ret = update_desktop_group_ivshmem_resource(desktop_group, columns)
    if isinstance(ret, Error):
        return ret

    return None

# delete desktop groups
def delete_desktop_group_config(desktop_group_id):
    
    ctx = context.instance()
    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
    if not desktop_group:
        return None
    
    #clear network resource
    network_configs = desktop_group.get("networks")
    if not network_configs:
        network_configs = {}
    
    for _, network_config in network_configs.items():
        ret = delete_network_config(network_config)
        if isinstance(ret, Error):
            return ret

    # clear disks resource
    disk_configs = desktop_group.get("disks")
    if disk_configs:
        ret = delete_disk_config(disk_configs.keys())
        if isinstance(ret, Error):
            return ret

    # clear user resource
    users = desktop_group.get("users")
    if users:
        for user_id, _ in users.items():
            conditions = dict(desktop_group_id=desktop_group_id, 
                              user_id=user_id)
    
            ctx.pg.base_delete(dbconst.TB_DESKTOP_GROUP_USER, conditions)

    return True

def delete_desktop_group(desktop_group):
    
    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]
    ret = delete_desktop_group_config(desktop_group_id)
    if isinstance(ret, Error):
        return ret

    ctx.pg.delete(dbconst.TB_DESKTOP_GROUP, desktop_group_id)
    ret = Permission.clear_user_resource_scope(desktop_group_id)
    if not ret:
        logger.error("clear desktop group resource scope fail %s" % desktop_group_id)

    return None

# modify desktop group status

def modify_desktop_group_status(desktop_group, status):

    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]

    if desktop_group["status"] == status:
        return None

    row = {desktop_group_id: {"status": status}}

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_GROUP, row):
        logger.error("Failed to update desktop group[%s] status %s" % (desktop_group_id, status))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    return None

def build_disk_config_disks(sender, disk_config, req):
    
    ctx = context.instance()
    disk_config_id = disk_config["disk_config_id"]
    filter_conditions = {"disk_config_id": disk_config_id}

    if check_global_admin_console(sender):
        display_columns = dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_DESKTOP_DISK]
    elif check_admin_console(sender):
        display_columns = dbconst.CONSOLE_ADMIN_COLUMNS[dbconst.TB_DESKTOP_DISK]
    else:
        display_columns = {}

    disk_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_DISK, filter_conditions, display_columns,
                                      sort_key = get_sort_key(dbconst.TB_DESKTOP_DISK, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                      )
    if not disk_set:
        return None
    
    total_count = ctx.pg.get_count(dbconst.TB_DESKTOP_DISK, filter_conditions)
    if total_count is None:
        logger.error("get desktop group disk count failed [%s]" % req)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
    
    disk_config["disks"] = disk_set.values()
    disk_config["disk_total_count"] = total_count
    return disk_set

# describe desktop group disk
def format_desktop_group_disks(sender, desktop_group_disk_set, req):
    
    verbose = req.get("verbose", 0)
    if verbose == 0 or desktop_group_disk_set:
        return None

    for _, disk_config in desktop_group_disk_set.items():
        build_disk_config_disks(sender, disk_config, req)

    return desktop_group_disk_set

def check_disk_config_name(disk_name):

    ctx = context.instance()
    ret = ctx.pgm.get_disk_config(disk_name=disk_name)
    if ret:
        logger.error("check disk config name existed %s" % (disk_name))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DISK_CONFIG_NAME_ALREADY_EXISTED, disk_name)
    return None    

def build_citrix_disks(desktop_group_id, disk_config_id):
    
    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
    if not desktops:
        return None
    
    disk_configs = ctx.pgm.get_disk_config(disk_config_id)
    if not disk_configs:
        logger.error("no found disk config %s" % (disk_config_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, disk_config_id)
    
    job_disks = []
    disk_config = disk_configs[disk_config_id]
    for desktop_id, _ in desktops.items():

        ret = Disk.create_disks(disk_config, desktop_id)
        if isinstance(ret, Error):
            return ret
        if ret:
            job_disks.extend(ret)
        
    return job_disks

def create_disk_config(desktop_group, disk_config, is_load=0):

    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]

    disk_config_id = get_uuid(UUID_TYPE_DESKTOP_GROUP_DISK, ctx.checker)
    new_disk_config = dict(
                           disk_config_id = disk_config_id,
                           desktop_group_id = desktop_group_id,
                           desktop_group_name = desktop_group["desktop_group_name"],
                           disk_name = disk_config["disk_name"],
                           disk_type = disk_config["disk_type"],
                           size = disk_config["size"],
                           create_time = get_current_time(False),
                           status_time = get_current_time(False),
                        )

    # register disk config
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_GROUP_DISK, {disk_config_id: new_disk_config}):
        logger.error("insert newly created desktop group disk config for [%s] to db failed" % (new_disk_config))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    is_apply = 1
    if is_load:
        is_apply = 0
    
    ret = set_desktop_group_apply(desktop_group_id, is_apply)
    if isinstance(ret, Error):
        return ret

    return disk_config_id

# modify desktop group disk
def check_modify_disk_config_vaild(disk_config_id, size):
    
    ctx = context.instance()
    
    # check need_update
    disk_configs = ctx.pgm.get_disk_config(disk_config_id)
    if not disk_configs:
        logger.error("desktop group disk config no found [%s]" % (disk_config_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, disk_config_id)
    disk_config = disk_configs[disk_config_id]

    # check size
    disk_size = disk_config["size"]
    if size is not None and disk_size > size:
        logger.error("desktop group disk config no found [%s]" % (disk_config_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DISK_NEW_SIZE_SHOULD_LARGER_THAN_OLD_SIZE, (disk_size, size))       
    
    return disk_config

def modify_disk_config_attributes(sender, disk_config, size=None, disk_name=None):
    
    ctx = context.instance()
    disk_config_id = disk_config["disk_config_id"]
    
    if is_citrix_platform(ctx, sender["zone"]):
        size = None
    
    update_info = {
        "size": disk_config["size"] if not size else size,
        "disk_name": disk_config["disk_name"] if not disk_name else disk_name,
        "status_time": get_current_time()
        }

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_GROUP_DISK, {disk_config_id: update_info}):
        logger.error("Failed to update desktop group disk[%s] attributes %s" % (disk_config_id, update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    desktop_group_id = disk_config["desktop_group_id"]
    ret = set_desktop_group_apply(desktop_group_id, 1)
    if isinstance(ret, Error):
        return ret

    return None

# delete disk config
def check_delete_disk_config_vaild(disk_config_ids):
    
    ctx = context.instance()
    # get disk config
    disk_configs = ctx.pgm.get_disk_config(disk_config_ids)
    if not disk_configs:
        logger.error("desktop group disk config no found [%s]" % (disk_config_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, disk_config_ids)

    return disk_configs

def refresh_delete_disk_config(disk_config_ids):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_disks(disk_config_ids=disk_config_ids)
    if not ret:
        return None
    disks = ret

    update_disk = {}
    for disk_id, _ in disks.items():
        update_disk[disk_id] = {
            "disk_config_id": ''
            }

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_disk):
        logger.error("Failed to update disk config[%s]" % update_disk)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def delete_disk_config(disk_config_ids):

    ctx = context.instance()
    
    for disk_config_id in disk_config_ids:
        ctx.pg.delete(dbconst.TB_DESKTOP_GROUP_DISK, disk_config_id)
        
    ret = refresh_delete_disk_config(disk_config_ids)
    if isinstance(ret, Error):
        return ret

    return None

# describe desktop group network config
def format_desktop_group_networks(sender, desktop_group_network_set):

    ctx = context.instance()
    
    if is_normal_console(sender) or is_normal_user(sender):
        return None
    
    for network_config_id, network_config in desktop_group_network_set.items():

        network_id = network_config["network_id"]
        networks = ctx.pgm.get_networks(network_id)
        if not networks:
            continue
        
        network = networks.get(network_id)
        network_config["network"] = network
        nics = ctx.pgm.get_network_config_nics(network_config_id)
        if nics:
            network_config["nics"] = nics
        
    return desktop_group_network_set

# create desktop group network config
def _check_network_config_iprange(network, start_ip, end_ip):
    
    network_id = network["network_id"]

    ip_network = network["ip_network"]
    dyn_ip_start = network["dyn_ip_start"]
    dyn_ip_end = network["dyn_ip_end"]
    
    ret = Network.check_desktop_ip(ip_network, dyn_ip_start, start_ip)
    if not ret:
        logger.error("check network range fail %s" % (network_id, start_ip, end_ip))
        return Error(ErrorCodes.PERMISSION_DENIED, 
                     ErrorMsg.ERR_MSG_ILLEGAL_DYN_IP_START_SHOULD_SMALLER_THAT_IP_END, (dyn_ip_start, start_ip))
    
    ret = Network.check_desktop_ip(ip_network, start_ip, end_ip)
    if not ret:
        logger.error("check network range fail %s" % (network_id, start_ip, end_ip))
        return Error(ErrorCodes.PERMISSION_DENIED, 
                     ErrorMsg.ERR_MSG_ILLEGAL_DYN_IP_START_SHOULD_SMALLER_THAT_IP_END, (start_ip, end_ip))
    
    ret = Network.check_desktop_ip(ip_network, end_ip, dyn_ip_end)
    if not ret:
        logger.error("check network range fail %s" % (network_id, start_ip, end_ip))
        return Error(ErrorCodes.PERMISSION_DENIED, 
                     ErrorMsg.ERR_MSG_ILLEGAL_DYN_IP_START_SHOULD_SMALLER_THAT_IP_END, (end_ip, dyn_ip_end))
    
    return None


def check_add_desktop_group_network(sender, network_ids, desktop_group = None):
    
    ctx = context.instance()
    zone_id = sender["zone"]

    if desktop_group:
        zone_id = desktop_group["zone"]
        desktop_group_id = desktop_group["desktop_group_id"]
        ret = ctx.pgm.get_desktop_group_network(desktop_group_id, network_id=network_ids)
        if ret:
            logger.error("desktop network existed in desktop group %s" % ret.keys())
            return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                         ErrorMsg.ERR_MSG_NETWORK_ALREADY_EXISTED, ret.keys())
        
    
    desktop_networks = ctx.pgm.get_desktop_networks(network_ids)
    if not desktop_networks:
        logger.error("no found desktop network %s" % network_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, network_ids)
    
    for _, network in desktop_networks.items():
        network_type = network["network_type"]
        
        ret = ctx.zone_checker.check_network_type(zone_id, network_type)
        if isinstance(ret, Error):
            return ret

    return desktop_networks

def add_desktop_group_network(desktop_group, networks):

    ctx = context.instance()
    
    logger.error("networks %s" % networks)
    
    desktop_group_id = desktop_group["desktop_group_id"]
    new_network_config = {}
    
    for network_id, network in networks.items():
    
        network_config_id = get_uuid(UUID_TYPE_DESKTOP_GROUP_NETWORK, ctx.checker)
        network_info = dict(
                            network_config_id = network_config_id,
                            desktop_group_id=desktop_group_id,
                            desktop_group_name=desktop_group["desktop_group_name"],
                            network_id = network_id,
                            create_time=get_current_time(False),
                            status_time=get_current_time(False),
                            network_type = network["network_type"],
                            start_ip = '',
                            end_ip = '',
                            )

        new_network_config[network_config_id] = network_info

    # add new network config
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_GROUP_NETWORK, new_network_config):
        logger.error("insert newly created netowrk config [%s] to db failed" % (new_network_config))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    if desktop_group["desktop_group_type"] == const.DG_TYPE_CITIRX:
        return new_network_config.keys()
    
    ret = set_desktop_group_apply(desktop_group_id, 1)
    if isinstance(ret, Error):
        return ret

    return new_network_config.keys()

# modify desktop group network config
def check_modify_network_config_vaild(sender, network_config_id):
    
    ctx = context.instance()
    
    # get network config
    network_configs = ctx.pgm.get_network_config(network_config_id)
    if not network_configs:
        logger.error("network config no found %s" % network_config_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, network_config_id)

    network_config = network_configs[network_config_id]

    # check network
    network_id = network_config["network_id"]
    ret = Network.check_desktop_network_vaild(sender, network_id)
    if isinstance(ret, Error):
        return ret

    return network_config

def modify_network_config(network_config):
    pass

# delete desktop group network config

def check_delete_network_config_vaild(network_config_ids):
    
    ctx = context.instance()
    
    # get network config
    network_configs = ctx.pgm.get_network_config(network_config_ids)
    if not network_configs:
        logger.error("delete network config no found %s" % network_config_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, network_config_ids)
    
    for network_config_id in network_config_ids:
        
        if network_config_id not in network_configs:
            logger.error("delete network config no found %s" % network_config_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, network_config_id)
    
    nics = ctx.pgm.get_network_config_nics(network_config_ids)
    if not nics:
        return network_configs
    
    for nic_id, nic in nics.items():
        transition_status = nic["transition_status"]
        if transition_status:
            logger.error("resource %s has trans status %s" % (nic_id, transition_status))
            return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_IN_TRANSITION_STATUS, network_config_ids)

    return network_configs
        
def delete_network_config(network_config):

    ctx = context.instance()
    network_config_id = network_config["network_config_id"]
    nics = ctx.pgm.get_network_config_nics(network_config_id)
    if not nics:
        nics = {}

    for nic_id, nic in nics.items():
        resource_id = nic["resource_id"]
        status = nic["status"]
        update_info = {
                        "network_config_id": '',
                        "is_occupied": 0,
                        "status_time": get_current_time()
                      }
        if resource_id and status == const.NIC_STATUS_INUSE:
            update_info["need_update"] = const.DESKTOP_NIC_DETACH

        else:
            update_info["desktop_group_id"] = ''
            update_info["desktop_group_name"] =  ''
            update_info["need_update"] = 0
            update_info["status"] = const.NIC_STATUS_AVAIL
            update_info["resource_id"] = ''
            update_info["resource_name"] = ''

        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_NIC, {nic_id:update_info}):
            logger.error("update desktop nic fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    ctx.pg.delete(dbconst.TB_DESKTOP_GROUP_NETWORK, network_config_id)

    desktop_group_id = network_config["desktop_group_id"]
    ret = set_desktop_group_apply(desktop_group_id, 1)
    if isinstance(ret, Error):
        return ret

    return None

# attach user to desktop group
def attach_user_to_dekstop_group(desktop_group, users, need_desktop=1):
    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]
    # create user private info

    update_user = {}
    for user_id, user in users.items():
        update_info = {"desktop_group_id": desktop_group_id,
                       "desktop_group_name": desktop_group["desktop_group_name"],
                       "user_id": user_id,
                       "user_name": user["user_name"],
                       "real_name": user["real_name"],
                       "need_desktop": need_desktop,
                       "status": const.USER_STATUS_ACTIVE,
                       "create_time": get_current_time(False),
                       }

        update_user[user_id] = update_info

    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_GROUP_USER, update_user):
        logger.error("attach user to desktop group insert db fail %s" % update_user)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return users

def detach_desktop_from_desktop_group(desktop_group_id, user_ids):
    
    ctx = context.instance()
    update_desktop = {}
    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id, owner=user_ids)
    if desktops:
        for desktop_id, desktop in desktops.items():
            need_update = desktop["need_update"]
            if need_update == const.DESKTOP_UPDATE_DELETE:
                continue

            update_desktop[desktop_id] = {
                                          "desktop_group_id": '',
                                          "desktop_group_name": '',
                                          "desktop_group_type": '',
                                          "auto_login": 0
                                         }

        if update_desktop:
            if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_desktop):
                logger.error("detach user from desktop group, update desktop fail %s" % update_desktop)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    update_disk = {}
    disks = ctx.pgm.get_disks(desktop_group_ids=desktop_group_id, user_ids=user_ids)
    if disks:
        for disk_id, disk in disks.items():
            need_update = disk["need_update"]
            if need_update == const.DESKTOP_DISK_DELETE:
                continue
            update_disk[disk_id] = {
                                    "desktop_group_id": '',
                                    "desktop_group_name": '',
                                    }
        if update_disk:
            if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_disk):
                logger.error("detach user from desktop group, update disk fail %s" % update_disk)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

# detach user from desktop group
def detach_user_from_dekstop_group(sender, desktop_group, user_ids):

    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]
    if not isinstance(user_ids, list):
        user_ids = [user_ids]

    # update user desktop
    user_desktops = ctx.pgm.get_user_desktops(desktop_group_id, user_ids)
    if not user_desktops:
        user_desktops = {}

    save_desk = desktop_group["save_desk"]
    delete_desktop = []
    
    if save_desk == const.DESKTOP_RULE_NOSAVE and user_desktops:
        check_desktops = []
        
        for user_id, dekstop_ids in user_desktops.items():
            check_desktops.extend(dekstop_ids)

        desktops = ctx.pgm.get_desktops(check_desktops)
        if desktops:
            ret = Desktop.delete_desktops(sender, desktops, user_ids=user_ids)
            if isinstance(ret, Error):
                return ret
            delete_desktop = ret
    
    for user_id in user_ids:
        conditions = dict(desktop_group_id=desktop_group_id, 
                          user_id=user_id)

        ctx.pg.base_delete(dbconst.TB_DESKTOP_GROUP_USER, conditions)
    
    ret = detach_desktop_from_desktop_group(desktop_group_id, user_ids)
    if isinstance(ret, Error):
        return ret

    return delete_desktop

# set desktop group user status
def active_desktop_group_users(desktop_group_id, user_ids):

    ctx = context.instance()
    user_desktop = ctx.pgm.get_user_desktop(desktop_group_id, user_ids)
    if not user_desktop:
        user_desktop = {}
    
    desktop_user = []
    # create user private info
    for user_id in user_ids:
        desktop_id = user_desktop.get(user_id)
        conditions = {
            "desktop_group_id": desktop_group_id,
            "user_id": user_id
            }
        update_info = {
            "status": const.USER_STATUS_ACTIVE
            }
        if not desktop_id:
            desktop_user.append(user_id)
            update_info["need_desktop"] = 1

        if not ctx.pg.base_update(dbconst.TB_DESKTOP_GROUP_USER, conditions, update_info):
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return desktop_user

def set_desktop_group_user_status(desktop_group_id, user_ids, status):

    ctx = context.instance()
    if not user_ids:
        return None
    
    if not isinstance(user_ids, list):
        user_ids = [user_ids]

    for user_id in user_ids:
        conditions = {
            "desktop_group_id": desktop_group_id,
            "user_id": user_id
            }
        update_info = {
            "status": status
            }
        desktop_group_user_set = ctx.pg.base_get(dbconst.TB_DESKTOP_GROUP_USER, conditions)
        if not desktop_group_user_set:
            continue
        if not ctx.pg.base_update(dbconst.TB_DESKTOP_GROUP_USER, conditions, update_info):
            logger.error("set desktop group user status update db fail %s, %s" % (conditions, update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def disable_desktop_group_users(sender, desktop_group, user_ids):
    
    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]
    save_desk = desktop_group["save_desk"]
    
    user_desktops = ctx.pgm.get_user_desktops(desktop_group_id, user_ids)
    if not user_desktops:
        user_desktops = {}

    delete_desktop = []
    for user_id in user_ids:
        
        desktop_ids = user_desktops.get(user_id)
        desktops = {}
        if desktop_ids:
            desktops = ctx.pgm.get_desktops(desktop_ids)
            if not desktops:
                desktops = {}
        
        if desktops and save_desk == const.DESKTOP_RULE_NOSAVE:
            ret = Desktop.delete_desktops(sender, desktops, user_ids=user_id)
            if isinstance(ret, Error):
                return ret
            if ret:
                delete_desktop.extend(ret)
    
        conditions = {
                     "desktop_group_id": desktop_group_id,
                     "user_id": user_id
                     }
        update_info = {
                      "status": const.USER_STATUS_DISABLED
                      }
        if not ctx.pg.base_update(dbconst.TB_DESKTOP_GROUP_USER, conditions, update_info):
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return delete_desktop

# apply desktop group
def set_stop_desktop_status(desktop_ids, clear_instance=False):
    
    ctx = context.instance()
    
    update_info = {}
    for desktop_id in desktop_ids:
        update_info[desktop_id] = {"status": const.INST_STATUS_STOP}
        if clear_instance:
            update_info[desktop_id]["instance_id"] = ''
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_info):
        logger.error("desktop group resource not found")
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def apply_modify_desktop_attributes(desktop_group, desktop_ids):

    ctx = context.instance()   
    
    if not desktop_ids:
        return None
    modify_keys = ['usbredir', 'clipboard', 'filetransfer', 'qxl_number']
    
    apply_desktop = []
    desktops = desktop_group["desktops"]

    for desktop_id in desktop_ids:
        
        desktop = desktops.get(desktop_id)
        if not desktop:
            continue
        
        status = desktop["status"]
        update_info = {}
        instance_id = desktop["instance_id"]

        # update desktop group resource
        for modify_key in modify_keys:

            if desktop[modify_key] == desktop_group[modify_key]:
                continue
            
            update_info[modify_key] = desktop_group[modify_key]
            
            if not instance_id:
                continue

            update_info["need_update"] = const.DESKTOP_UPDATE_MODIFY
            if status == const.INST_STATUS_STOP and desktop_id not in apply_desktop:
                apply_desktop.append(desktop_id)
                
        if not update_info:
            continue

        if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: update_info}):
            logger.error("apply modify desktop, update desktop fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)   
    return apply_desktop

def check_desktop_group_user(desktop_group_id):
    
    ctx = context.instance()
    # check user desktop
    desktop_user = ctx.pgm.get_desktop_group_users(desktop_group_id, need_desktop=1, status=const.USER_STATUS_ACTIVE)
    if not desktop_user:
        return None
    user_ids = desktop_user.keys()
    
    user_desktop = ctx.pgm.get_user_desktop(desktop_group_id, user_ids)
    if not user_desktop:
        return user_ids
    
    for user_id, _ in user_desktop.items():
        
        if user_id in user_ids:
            user_ids.remove(user_id)
        
    return user_ids

def apply_new_desktops(sender, desktop_group):

    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]
    dg_type = desktop_group["desktop_group_type"]
    create_desktop = []
    is_create = desktop_group["is_create"]

    # check create new desktop
    if dg_type == const.DG_TYPE_RANDOM:
        return None

    ret = check_desktop_group_user(desktop_group_id)
    if not ret:
        return None
    user_ids = ret
    # create desktops
    ret = Desktop.register_desktop_group_desktops(sender, desktop_group, user_ids)
    if isinstance(ret, Error):
        return ret
    if ret:
        create_desktop.extend(ret)
    
    condition = {"desktop_group_id": desktop_group_id, "user_id": user_ids}
    if not ctx.pg.base_update(dbconst.TB_DESKTOP_GROUP_USER, condition, {"need_desktop": 0}):
        logger.error("set desktop need update fail %s" % (condition))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    if not create_desktop or not is_create:
        return None
    
    if create_desktop:
        ret = set_desktop_need_update(create_desktop, const.DESKTOP_UPDATE_CREATE)
        if isinstance(ret, Error):
            return ret

    return create_desktop

def apply_desktop_group_disk(desktop_group, desktop_ids):
    
    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]
    disk_config = ctx.pgm.get_disk_config(desktop_group_id=desktop_group_id)
    if not disk_config:
        return None
    
    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        return None

    for config_id, config in disk_config.items():
        desktop_disk = ctx.pgm.get_desktop_disk(desktop_ids, disk_config_ids=config_id)
        if not desktop_disk:
            desktop_disk = {}

        desktop_disks = ctx.pgm.get_desktop_disks(desktop_ids)
        if not desktop_disks:
            desktop_disks = {}

        disk_desktops = []
        for desktop_id, _ in desktops.items():
            if desktop_id in desktop_disk:
                continue
            
            curr_disks = desktop_disks.get(desktop_id)
            
            if curr_disks and len(curr_disks) >= const.DESKTOP_MAX_DISK_COUNT:
                continue
            
            disk_desktops.append(desktop_id)
        
        if disk_desktops:
            ret = Disk.create_disks(config, disk_desktops)
            if isinstance(ret, Error):
                return ret
    
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        return None

    desktop_disk = ctx.pgm.get_desktop_disk(desktop_instance.keys(), [const.DESKTOP_DISK_ATTACH])
    if not desktop_disk:
        desktop_disk = {}
    
    return desktop_disk.keys()

def apply_desktop_group_avail_disk(desktop_group):
    
    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]
    disk_config = ctx.pgm.get_disk_config(desktop_group_id=desktop_group_id)
    if not disk_config:
        return None
    
    update_disk = {}
    apply_disk = []
    for config_id, config in disk_config.items():
        disks = ctx.pgm.get_disks(disk_config_ids=config_id)
        if not disks:
            continue
        
        config_size = config["size"]
        for disk_id, disk in disks.items():
            if disk["size"] >= config_size:
                continue
            status = disk["status"]
            volume_id = disk["volume_id"]
            update_info = {"size": config_size}
            if volume_id:
                update_info["need_update"] = const.DESKTOP_DISK_RESIZE
            
            update_disk[disk_id] = update_info
            if status in [const.DISK_STATUS_AVAIL]:
                apply_disk.append(disk_id)

    if update_disk:
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_disk):
            logger.error("apply desktop group update db fail %s" % update_disk)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return apply_disk

def apply_free_random_desktop(sender, desktop_group, desktop_ids):

    # check desktop count and delete the free random desktop
    ctx = context.instance()
    dg_type = desktop_group["desktop_group_type"]
    if dg_type != const.DG_TYPE_RANDOM:
        return None

    desktop_group_id = desktop_group["desktop_group_id"]

    desktop_count = desktop_group["desktop_count"]
    curr_desktop_count = len(desktop_ids)
    # only delete desktop that exceed the desktop count
    if curr_desktop_count <= desktop_count:
        return None

    delete_desktop = []
    delete_count = curr_desktop_count - desktop_count
    free_desktop = ctx.pgm.get_free_random_desktops(desktop_group_id)
    if not free_desktop:
        return None

    if len(free_desktop) > delete_count:
        delete_desktop = free_desktop.keys()[0:delete_count]
    else:
        delete_desktop = free_desktop.keys()
    
    desktops = ctx.pgm.get_desktops(delete_desktop)
    if desktops:    
        ret = Desktop.delete_desktops(sender, desktops)
        if isinstance(ret, Error):
            return ret

    delete_desktop = ret
    if delete_desktop:
        for desktop_id in delete_desktop:
            if desktop_id in desktop_ids:
                desktop_ids.remove(desktop_id)

    return delete_desktop

def apply_desktop_group_nic(sender, desktop_group, desktop_ids):

    ctx = context.instance()
    
    if not desktop_ids:
        return None
    
    alloc_desktops = []
    for network_type in const.SUPPORT_NETWORK_TYPES:
        
        ret = ctx.zone_checker.check_network_type(sender["zone"], network_type)
        if isinstance(ret, Error):
            continue

        # get desktop current nic
        desktop_nics = ctx.pgm.get_desktop_nics(desktop_ids, network_type=network_type)
        if not desktop_nics:
            desktop_nics = {}

        # check desktop nics
        alloc_desktop = []
        for desktop_id in desktop_ids:
            desk_nics = desktop_nics.get(desktop_id)
            if not desk_nics:
                alloc_desktop.append(desktop_id)
                continue

            for nic in desk_nics:
                need_update = nic["need_update"]
                if need_update == const.DESKTOP_NIC_DETACH:
                    if desktop_id in alloc_desktop:
                        continue
                    alloc_desktop.append(desktop_id)
        
        if not alloc_desktop:
            continue
        
        alloc_desktops.extend(alloc_desktop)

        # alloc new nic
        ret = Nic.alloc_desktop_group_nics(sender,desktop_group, alloc_desktop, network_type)
        if isinstance(ret, Error):
            return ret

    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        return None
    
    desktop_nics = []
    detach_nics = ctx.pgm.get_desktop_nics(desktop_instance.keys(), [const.DESKTOP_NIC_DETACH], status=const.NIC_STATUS_INUSE)
    if detach_nics:
        desktop_nics.extend(detach_nics.keys())
    
    if alloc_desktops:
        desktop_nics.extend(alloc_desktops)

    return desktop_nics

def get_desktop_group_ipresource(desktop_group_id, is_free=0, include_networks=None):
    
    ctx = context.instance()
    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id, extras=[dbconst.TB_DESKTOP_GROUP_NETWORK])
    if not desktop_group:
        return None
    
    private_ips = []
    conditions = {}
    network_ids = []
    networks = desktop_group["networks"]
    for _, network in networks.items():
        network_id = network["network_id"]
        start_ip = network["start_ip"]
        if start_ip:
            conditions["desktop_group_id"] = desktop_group_id
            continue
        
        if include_networks and network_id not in include_networks:
            continue

        network_ids.append(network_id)
    
    if network_ids:
        conditions["network_id"] = network_ids
    
    if not conditions:
        return None
    
    nic_set = ctx.pg.base_get(dbconst.TB_DESKTOP_NIC, conditions, is_and=False)
    for nic in nic_set:
        private_ip = nic["private_ip"]
        resource_id = nic["resource_id"]
        status = nic["status"]
        if status in [const.NIC_STATUS_INUSE]:
            if not nic["desktop_group_id"]:
                continue
    
            if nic["desktop_group_id"] and nic["desktop_group_id"] != desktop_group_id:
                continue

        if is_free and resource_id:
            continue
        
        private_ips.append(private_ip)
    
    return private_ips

def get_desktop_ip_resource(filter_conditions, desktop_group_id=None, desktop_id=None, is_free=0, network_ids=None):
    
    if network_ids and not isinstance(network_ids, list):
        network_ids = [network_ids]
    
    ctx = context.instance()   
    if is_free:
        if desktop_id:
            desktops = ctx.pgm.get_desktops(desktop_id)
            if desktops:
                desktop = desktops[desktop_id]
                if desktop["desktop_group_id"]:
                    desktop_group_id = desktop["desktop_group_id"]
                else:
                    filter_conditions["status"] = const.NIC_STATUS_AVAIL
                    return
            else:
                filter_conditions["resource_id"] = None

        if desktop_group_id:
            private_ips = get_desktop_group_ipresource(desktop_group_id, is_free, network_ids)
            if not private_ips:
                filter_conditions["private_ip"] = None 
            else:
                filter_conditions["private_ip"] = private_ips 
    else:
        if desktop_id:
            filter_conditions["resource_id"] = desktop_id
        else:
            private_ips = get_desktop_group_ipresource(desktop_group_id, is_free, network_ids)
            if not private_ips:
                filter_conditions["private_ip"] = None 
            else:
                filter_conditions["private_ip"] = private_ips 

    return None

def format_desktop_ips(nic_set):

    if not nic_set:
        return None
    ctx = context.instance()
    
    desktop_ids = []
    image_ids = []
    for _, nic in nic_set.items():
        network_type = nic["network_type"]
        if network_type == const.NETWORK_TYPE_MANAGED:
            continue
        
        resource_id = nic["resource_id"]
        if resource_id.startswith(UUID_TYPE_DESKTOP):
            desktop_ids.append(resource_id)
        elif resource_id.startswith(UUID_TYPE_DESKTOP_IMAGE):
            image_ids.append(resource_id)
    
    desktops = {}
    if desktop_ids:
        desktops = ctx.pgm.get_desktops(desktop_ids)
        if not desktops:
            desktops = {}
    
    images = {}
    if image_ids:
        images = ctx.pgm.get_desktop_images(image_ids)
        if not images:
            images = {}
    
    for _, nic in nic_set.items():
        resource_id = nic["resource_id"]
        if resource_id.startswith(UUID_TYPE_DESKTOP):
            desktop = desktops.get(resource_id)
            if desktop:
                nic["zone"] = desktop["zone"]
        elif resource_id.startswith(UUID_TYPE_DESKTOP_IMAGE):
            image = images.get(resource_id)
            if image:
                nic["zone"] = image["zone"]
            
    return nic_set
    
