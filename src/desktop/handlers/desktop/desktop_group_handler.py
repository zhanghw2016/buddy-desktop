
import context
from db.constants  import (
    TB_DESKTOP_GROUP,
    TB_DESKTOP_GROUP_DISK,
    TB_DESKTOP_GROUP_NETWORK,
    TB_DESKTOP_GROUP_USER,
    TB_DESKTOP_NIC,
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    PUBLIC_COLUMNS,
)
from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
    is_citrix_platform,
    check_global_admin_console,
    check_admin_console
)
from utils.misc import get_columns
import constants as const
import db.constants as dbconst
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg

import resource_control.desktop.desktop_group as DesktopGroup
import resource_control.desktop.image as Image
import resource_control.desktop.resource_permission as ResCheck
import resource_control.desktop.desktop as Desktop
import resource_control.desktop.disk as Disk
import resource_control.citrix.citrix as Citrix
import resource_control.user.apply_approve as ApplyApprove
import resource_control.permission as Permission
from utils.misc import explode_array
import resource_control.desktop.network as Network

def handle_describe_desktop_groups(req):

    ctx = context.instance()
    sender = req["sender"]

    # build filter conditions
    filter_conditions = build_filter_conditions(req, TB_DESKTOP_GROUP)
    desktop_image_id = req.get("desktop_image")
    if desktop_image_id:
        filter_conditions["desktop_image_id"] = desktop_image_id

    desktop_group_ids = req.get("desktop_groups")
    user_id = req.get("user")
    if user_id:
        desktop_group_ids = ctx.pgm.get_user_desktop_groups(user_id, desktop_group_ids)

    if desktop_group_ids:
        filter_conditions["desktop_group_id"] = desktop_group_ids
    
    session_type = req.get("session_type")
    if session_type:
        ret = ctx.pgm.get_desktop_images(session_type=session_type)
        if ret:
            image_ids = ret.keys()
        else:
            rep = {'total_count': 0} 
            return return_items(req, {}, "desktop_group", **rep)
        
        filter_conditions["desktop_image_id"] = image_ids

    check_desktop_dn_flag = req.get("check_desktop_dn",0)    
    # describe desktop group
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_GROUP]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_GROUP]
    else:
        display_columns = PUBLIC_COLUMNS[TB_DESKTOP_GROUP]
        
        if "zone" in filter_conditions:
            del filter_conditions["zone"]
            
        user_id = sender["owner"]
        ret = ctx.pgm.get_desktop_group_by_user(user_id, filter_conditions.get("desktop_group_id"))
        if ret:
            filter_conditions["desktop_group_id"] = ret.keys()
        else:
            rep = {'total_count': 0}
            return return_items(req, {}, "desktop_group", **rep)
        
    desktop_group_set = ctx.pg.get_by_filter(TB_DESKTOP_GROUP, filter_conditions, display_columns,
                                      sort_key = get_sort_key(TB_DESKTOP_GROUP, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )

    if desktop_group_set is None:
        logger.error("describe desktop group failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    # format desktop group
    DesktopGroup.format_desktop_groups(sender, desktop_group_set, req.get("verbose", 0),check_desktop_dn_flag)

    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_GROUP, filter_conditions)
    if total_count is None:
        logger.error("get desktop group count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count} 
    return return_items(req, desktop_group_set, "desktop_group", **rep)

def handle_create_desktop_group(req):

    sender = req["sender"]
    additional_params = {}
    ctx = context.instance()

    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_image", "cpu", "memory", 
                                             "desktop_group_type", "naming_rule", "instance_class", "networks"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_image_id = req["desktop_image"]
    naming_rule = req["naming_rule"]
    desktop_group_type = req["desktop_group_type"]
    instance_class = req["instance_class"]

    # check desktop dn
    desktop_dn = req.get("desktop_dn")
    if is_citrix_platform(ctx, sender["zone"]) and not desktop_dn:
        logger.error("citrix desktop group need dn" )
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_DESKTOP_GROUP_PARAM_NEED_OU))

    # build desktop group naming
    ret = DesktopGroup.check_desktop_group_naming_rule(sender["zone"], naming_rule)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # check image vaild
    ret = Image.check_desktop_image_vaild(desktop_image_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_image = ret[desktop_image_id]
    image_name = desktop_image["image_name"]
    req.update({"image_name": image_name})
    
    ret = DesktopGroup.check_desktop_group_attributes(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    # check desktop group type
    ret = DesktopGroup.build_desktop_group_type(desktop_group_type, req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # check disk config
    if "disk_size" in req:
        disk_sizes = explode_array(req["disk_size"], is_integer=True)
        disk_configs = []
        for disk_size in disk_sizes:
            
            ret = ctx.zone_checker.check_disk_size(sender["zone"], disk_size)
            if isinstance(ret, Error):
                return return_error(req, ret)

            ret = ctx.pgm.get_instance_class_disk_type(zone_deploy=ctx.zone_deploy, instance_class=instance_class)
            if not ret:
                logger.error("instance_class %s no found corresponding disk_type" % instance_class)
                return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND,
                                               ErrorMsg.ERR_MSG_INSTANCE_CLASS_NO_FOUND_CORRESPONDING_DISK_TYPE,instance_class))
            instance_class_disk_types = ret

            disk_type = 0
            for _, instance_class_disk_type in instance_class_disk_types.items():
                disk_type = instance_class_disk_type.get("disk_type")

            disk_config = {
                            "size": disk_size,
                            "disk_type": disk_type,
                            "disk_name": req.get("disk_name", "disk")
                            }
            disk_configs.append(disk_config)

        additional_params["disk_configs"] = disk_configs
        
    # check network config
    network_ids = req["networks"]
    ret = DesktopGroup.check_add_desktop_group_network(sender, network_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    additional_params["network_config"] = ret

    # check desktop group user
    if "users" in req and not is_citrix_platform(ctx, sender["zone"]):
        user_ids = req["users"]
        ret = DesktopGroup.check_desktop_group_user_vaild(user_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        users = ret
        
        additional_params["users"] = users
    
    # create desktop group
    ret = DesktopGroup.create_desktop_group(sender, req, additional_params)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop_group_id = ret
    
    job_uuid = None
    if is_citrix_platform(ctx, sender["zone"]):

        is_load = req.get("is_load", 0)
        if not is_load:
            ret = DesktopGroup.send_desktop_group_job(sender, desktop_group_id, const.JOB_ACTION_CREATE_DESKTOP_GROUP)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret

    # register resource permission
    Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_DESKTOP_GROUP, desktop_group_id, sender["zone"], dbconst.RES_SCOPE_DELETE)

    # return the desktop group id
    ret = {'desktop_group': desktop_group_id}
    return return_success(req, None, job_uuid, **ret)

def handle_modify_desktop_group_attributes(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group_id = req["desktop_group"]

    # need maintenance mode
    need_maint_columns = get_columns(req, ["cpu", "memory", "ivshmem_enable", "gpu", "gpu_class", "desktop_count", "desktop_group_name",
                                           'usbredir', 'clipboard', 'filetransfer', 'qxl_number', "is_create", "description", "desktop_dn"])
    
    check_status_keys = get_columns(req, ["cpu", "memory", "ivshmem_enable", "gpu", "gpu_class", "desktop_count",
                                           'usbredir', 'clipboard', 'filetransfer', 'qxl_number', "is_create", "desktop_dn"])
    
    desktop_group_status = None
    if check_status_keys:
        desktop_group_status = const.DG_STATUS_MAINT

    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, status=desktop_group_status)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]

    ret = DesktopGroup.check_desktop_group_attributes(sender, need_maint_columns)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopGroup.modify_desktop_group_attributes(sender, desktop_group, need_maint_columns)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_modify_desktop_group_image(req):

    ctx = context.instance()
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_group", "desktop_image_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group_id = req["desktop_group"]
    desktop_image_id = req["desktop_image_id"]

    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id,check_modify_image=True)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]

    ret = Image.check_desktop_image_vaild(desktop_image_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_image = ret[desktop_image_id]
    
    if desktop_group["desktop_image_id"] == desktop_image_id:
        return return_success(req, None)
    
    if not is_citrix_platform(ctx, sender["zone"]):
        ret = DesktopGroup.modify_desktop_group_image(sender, desktop_group, desktop_image)
        if isinstance(ret, Error):
            return return_error(req, ret)

        return return_success(req, None)
    else:
        
        job_uuid = None
        citrix_update = {"desktop_image": desktop_image_id}
        ret = DesktopGroup.send_desktop_group_job(sender, desktop_group_id, const.JOB_ACTION_UPDATE_CITRIX_IMAGE, citrix_update)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

        return return_success(req, None, job_uuid)

def handle_modify_desktop_group_desktop_count(req):
    
    ctx = context.instance()
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_group", "desktop_count"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group_id = req["desktop_group"]
    desktop_count = req["desktop_count"]

    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]
    
    job_uuid = None

    if not is_citrix_platform(ctx, sender["zone"]):
        
        desktop_group_type = desktop_group["desktop_group_type"]
        if desktop_group_type == const.DG_TYPE_RANDOM:
            
            ret = Desktop.register_desktop_group_desktops(sender, desktop_group, desktop_count=desktop_count)
            if isinstance(ret, Error):
                return return_error(req, ret)
            desktop_ids = ret

            if desktop_ids:
                # submit desktop job
                ret = Desktop.send_desktop_job(sender, desktop_ids, const.JOB_ACTION_CREATE_DESKTOPS)
                if isinstance(ret, Error):
                    return return_error(req, ret)
                job_uuid = ret
    
            ret = {"desktop": desktop_ids}
            return return_success(req, None, job_uuid, **ret)
  
    else:
        citrix_update = {"desktop_count": desktop_count}
        ret = DesktopGroup.send_desktop_group_job(sender, desktop_group_id, const.JOB_ACTION_ADD_CITRIX_COMPUTERS, citrix_update)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_delete_desktop_groups(req):
    
    ctx = context.instance()
    sender = req["sender"]

    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_groups"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group_ids = req["desktop_groups"]

    # check desktop group
    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_ids, check_desktop_status = True)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_groups = ret

    delete_desktop_groups = []
    # clear desktop group resource
    for desktop_group_id, desktop_group in desktop_groups.items():

        if is_citrix_platform(ctx, sender["zone"]):
            
            ret = Citrix.check_delete_citrix_desktop_groups(desktop_group)
            if isinstance(ret, Error):
                return return_error(req, ret)
            
            delete_desktop_groups.append(desktop_group_id)
        else:
            # delete desktop
            desktops = desktop_group["desktops"]
            if desktops:
                ret = Desktop.delete_desktops(sender, desktops, True)
                if isinstance(ret, Error):
                    return return_error(req, ret)

                if ret:
                    delete_desktop_groups.append(desktop_group_id)
    
            # clear avail disks
            disks = ctx.pgm.get_desktop_group_disk(desktop_group_id, status=const.DISK_STATUS_AVAIL)
            if disks:
                ret = Disk.delete_disks(disks)
                if isinstance(ret, Error):
                    return return_error(req, ret)
    
                if ret:
                    if desktop_group_id not in delete_desktop_groups:
                        delete_desktop_groups.append(desktop_group_id)
    
            if desktop_group_id in delete_desktop_groups:
                continue
    
            desktop_group = desktop_groups[desktop_group_id]
            ret = DesktopGroup.delete_desktop_group(desktop_group)
            if isinstance(ret, Error):
                return return_error(req, ret)

    # delete desktop group
    job_uuid = None
    if delete_desktop_groups:
        ret = DesktopGroup.send_desktop_group_job(sender, delete_desktop_groups, const.JOB_ACTION_DELETE_DESKTOP_GROUPS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

        # clear resource in apply group
        ApplyApprove.clean_resource_in_apply_group(delete_desktop_groups)

        # clear resource permisson
        Permission.clear_user_resource_scope(resource_ids=delete_desktop_groups)

    return return_success(req, None, job_uuid)

def handle_modify_desktop_group_status(req):
    
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_group", "status"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop_group_id = req["desktop_group"]
    status = req["status"]

    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, None)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]
    
    # check desktop group
    ret = DesktopGroup.modify_desktop_group_status(desktop_group, status)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_describe_desktop_group_disks(req):

    ctx = context.instance()
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ["desktop_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    filter_conditions = {}
    desktop_group_id = req["desktop_group"]
    if desktop_group_id:
        filter_conditions["desktop_group_id"] = desktop_group_id

    disk_config_ids = req.get("disk_config")
    if disk_config_ids:
        filter_conditions.update({'disk_config_id': disk_config_ids})

    # describe desktop group disk
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_GROUP_DISK]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_GROUP_DISK]
    else:
        display_columns = {}
    
    disk_config_set = ctx.pg.get_by_filter(TB_DESKTOP_GROUP_DISK, filter_conditions, display_columns)
    if disk_config_set is None:
        logger.error("get desktop group disk config failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # verbose
    DesktopGroup.format_desktop_group_disks(sender, disk_config_set, req)

    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_GROUP_DISK, filter_conditions)
    if total_count is None:
        logger.error("get desktop group disk config count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, disk_config_set, "disk_config", **rep)

def handle_create_desktop_group_disk(req):

    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop_group", "disk_size", "disk_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop_group_id = req["desktop_group"]
    size = req["disk_size"]
    disk_name = req["disk_name"]
    is_load = req.get("is_load")

    # check desktop group avail
    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]

    ret = Disk.check_desktop_disk_count(desktop_group_id=desktop_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # check disk name
    ret = DesktopGroup.check_disk_config_name(disk_name)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    instance_class = desktop_group["instance_class"]

    ret = ctx.pgm.get_instance_class_disk_type(zone_deploy=ctx.zone_deploy, instance_class=instance_class)
    if not ret:
        logger.error("instance_class %s no found corresponding disk_type" % instance_class)
        return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND,
                                       ErrorMsg.ERR_MSG_INSTANCE_CLASS_NO_FOUND_CORRESPONDING_DISK_TYPE,instance_class))
    instance_class_disk_types = ret

    disk_type = 0
    for _, instance_class_disk_type in instance_class_disk_types.items():
        disk_type = instance_class_disk_type.get("disk_type")

    disk = {
              "size": size,
              "disk_type": disk_type,
              "disk_name": disk_name
              }
    ret = DesktopGroup.create_disk_config(desktop_group, disk, is_load=is_load)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    disk_config_id = ret
    rep = {'disk_config': disk_config_id}
    job_uuid = None

    if is_citrix_platform(ctx, sender["zone"]) and not is_load:

        job_disks = DesktopGroup.build_citrix_disks(desktop_group_id, disk_config_id)
        if job_disks:
            ret = Disk.send_disk_job(sender, job_disks, const.JOB_ACTION_ATTACH_DISKS)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret
            
            rep["disks"] = job_disks

    return return_success(req, None, job_uuid, **rep)

def handle_modify_desktop_group_disk(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["disk_config"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    disk_config_id = req["disk_config"]

    # check disk config vaild
    size = req.get("size")
    ret = DesktopGroup.check_modify_disk_config_vaild(disk_config_id, size)
    if isinstance(ret, Error):
        return return_error(req, ret)
    disk_config = ret
    
    desktop_group_id = disk_config["desktop_group_id"]

    # check disk name
    disk_name = req.get("disk_name")
    if disk_name:
        ret = DesktopGroup.check_disk_config_name(disk_name)
        if isinstance(ret, Error):
            return return_error(req, ret)

    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    # modify disk config
    ret = DesktopGroup.modify_disk_config_attributes(sender, disk_config, size, disk_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_delete_desktop_group_disks(req):
    
    ret = ResCheck.check_request_param(req, ["disk_configs"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    disk_config_ids = req.get("disk_configs")
    ret = DesktopGroup.check_delete_disk_config_vaild(disk_config_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    disk_configs = ret

    for _, disk_config in disk_configs.items():

        desktop_group_id = disk_config["desktop_group_id"]

        ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)

    ret = DesktopGroup.delete_disk_config(disk_config_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_describe_desktop_group_networks(req):

    ctx = context.instance()
    sender = req["sender"]
    
    filter_conditions= {}
    desktop_group_id = req.get("desktop_group")
    if desktop_group_id:
        filter_conditions["desktop_group_id"] = desktop_group_id

    network_config_ids = req.get("network_config")
    if network_config_ids:
        filter_conditions.update({'network_config_id':network_config_ids})
    
    network_type = req.get("network_type")
    if network_type:
        filter_conditions.update({'network_type':network_type})
    
    # describe desktop group network
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_GROUP_NETWORK]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_GROUP_NETWORK]
    else:
        display_columns = {}

    network_config_set = ctx.pg.get_by_filter(TB_DESKTOP_GROUP_NETWORK, filter_conditions, display_columns,
                                              sort_key = get_sort_key(TB_DESKTOP_GROUP_NETWORK, req.get("sort_key")),
                                              reverse = get_reverse(req.get("reverse")),
                                              offset = req.get("offset", 0),
                                              limit = req.get("limit", DEFAULT_LIMIT),
                                              )
    if network_config_set is None:
        logger.error("describe desktop group network failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    ret = DesktopGroup.format_desktop_group_networks(sender, network_config_set)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_GROUP_NETWORK, filter_conditions)
    if total_count is None:
        logger.error("get desktop group network count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, network_config_set, "network_config", **rep)

def handle_create_desktop_group_network(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop_group", "network"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group_id = req["desktop_group"]
    network_id = req["network"]

    # check desktop group vaild
    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]
    
    
    ret = Network.check_desktop_network_vaild(sender, network_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    networks = ret

    # create network config
    ret = DesktopGroup.add_desktop_group_network(desktop_group, networks)
    if isinstance(ret, Error):
        return return_error(req, ret)
    network_config_id = ret

    ret = {'network_config': network_config_id}
    return return_success(req, None, **ret)

def handle_modify_desktop_group_network(req):
    
    sender = req["sender"]
    
    ret = ResCheck.check_request_param(req, ["network_config"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    network_config_id = req["network_config"]

    # check network config
    ret = DesktopGroup.check_modify_network_config_vaild(sender, network_config_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    network_config = ret

    desktop_group_id = network_config["desktop_group_id"]

    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = DesktopGroup.modify_network_config(network_config)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_delete_desktop_group_networks(req):
    
    ret = ResCheck.check_request_param(req, ["network_configs"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    network_config_ids = req["network_configs"]

    # check network config
    ret = DesktopGroup.check_delete_network_config_vaild(network_config_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    network_configs = ret

    for _, network_config in network_configs.items():
        desktop_group_id = network_config["desktop_group_id"]

        ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    for _, network_config in network_configs.items():
        ret = DesktopGroup.delete_network_config(network_config)
        if isinstance(ret, Error):
            logger.error("delete network config fail [%s]" % desktop_group_id)
            return return_error(req, ret)

    return return_success(req, None)

def handle_describe_desktop_group_users(req):

    ctx = context.instance()
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ["desktop_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    filter_conditions = build_filter_conditions(req, TB_DESKTOP_GROUP_USER)
    desktop_group_id = req["desktop_group"]
    if desktop_group_id:
        filter_conditions["desktop_group_id"] = desktop_group_id

    user_ids = req.get("users")
    if user_ids:
        filter_conditions.update({'user_id':user_ids})

    # describe desktop group
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_GROUP_USER]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_GROUP_USER]
    else:
        display_columns = {}

    user_set = ctx.pg.get_by_filter(TB_DESKTOP_GROUP_USER, filter_conditions, display_columns,
                                      sort_key = get_sort_key(TB_DESKTOP_GROUP_USER, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if user_set is None:
        logger.error("describe desktop group users failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_GROUP_USER, filter_conditions)
    if total_count is None:
        logger.error("get desktop group user count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, user_set, "desktop_group_user", **rep)

def handle_attach_user_to_desktop_group(req):
    
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ["users", "desktop_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    user_ids = req["users"]
    desktop_group_id = req["desktop_group"]

    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, None)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]    

    ret = DesktopGroup.check_desktop_group_user_vaild(user_ids, desktop_group_id, True)
    if isinstance(ret, Error):
        return return_error(req, ret)
    users = ret
    ret = DesktopGroup.attach_user_to_dekstop_group(desktop_group, users)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    job_uuid = None
    desktop_group_type = desktop_group["desktop_group_type"]
    if desktop_group_type != const.DG_TYPE_RANDOM:
        ret = Desktop.register_desktop_group_desktops(sender, desktop_group, user_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
        desktop_ids = ret
    
        is_create = desktop_group["is_create"]
        is_apply = desktop_group["is_apply"]
        # submit desktop job
        if is_create and not is_apply:
            ret = Desktop.send_desktop_job(sender, desktop_ids, const.JOB_ACTION_CREATE_DESKTOPS)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_detach_user_from_desktop_group(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop_group", "users"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    user_ids = req["users"]
    desktop_group_id = req["desktop_group"]

    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, None)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]

    ret = DesktopGroup.check_desktop_group_user_vaild(user_ids, desktop_group_id, False, True, None)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopGroup.detach_user_from_dekstop_group(sender, desktop_group, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    delete_desktop = ret

    job_uuid = None
    if delete_desktop:
        ret = Desktop.send_desktop_job(sender, delete_desktop, const.JOB_ACTION_DELETE_DESKTOPS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_set_desktop_group_user_status(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop_group", "users", "status"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    user_ids = req["users"]
    status = req["status"]
    desktop_group_id = req["desktop_group"]

    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, None)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]
    
    job_uuid = None
    if status == const.USER_STATUS_ACTIVE:
        ret = DesktopGroup.active_desktop_group_users(desktop_group_id, user_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        desktop_user = ret
        if desktop_user:
            ret = Desktop.register_desktop_group_desktops(sender, desktop_group, desktop_user)
            if isinstance(ret, Error):
                return return_error(req, ret)
    
            desktop_ids = ret
            is_create = desktop_group["is_create"]
            # submit desktop job
            if is_create:
                ret = Desktop.send_desktop_job(sender, desktop_ids, const.JOB_ACTION_CREATE_DESKTOPS)
                if isinstance(ret, Error):
                    return return_error(req, ret)
                job_uuid = ret
    
    else:
        ret = DesktopGroup.disable_desktop_group_users(sender, desktop_group, user_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

        desktop_ids = ret
        # submit desktop job
        if desktop_ids and desktop_group["desktop_group_type"] == const.DG_TYPE_RANDOM:
            ret = Desktop.send_desktop_job(sender, desktop_ids, const.JOB_ACTION_DELETE_DESKTOPS)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_apply_desktop_group(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["desktop_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group_id = req["desktop_group"]

    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, check_desktop_status=True)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_group = ret[desktop_group_id]
    
    if not desktop_group["is_apply"]:
        return return_success(req, None, None)
    
    apply_desktop = []
    apply_disk = []
    # check current desktop
    desktops = desktop_group["desktops"]
    if desktops:
        desktop_ids = desktops.keys()
            
        # apply desktop group nic
        ret = DesktopGroup.apply_desktop_group_nic(sender, desktop_group, desktop_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        if ret:
            apply_desktop.extend(ret)

        # apply desktop group disk
        ret = DesktopGroup.apply_desktop_group_disk(desktop_group, desktop_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        if ret:
            apply_desktop.extend(ret)

        # apply desktop 
        ret = DesktopGroup.apply_modify_desktop_attributes(desktop_group, desktop_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)
        if ret:
            apply_desktop.extend(ret)
   
    # apply new desktop
    ret = DesktopGroup.apply_new_desktops(sender, desktop_group)
    if isinstance(ret, Error):
        return return_error(req, ret)
    if ret:
        apply_desktop.extend(ret)
    
    # apply desktop group disk
    ret = DesktopGroup.apply_desktop_group_avail_disk(desktop_group)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    if ret:
        apply_disk.extend(ret)
    
    job_uuid = None

    if apply_desktop or apply_disk:
       
        ret = DesktopGroup.send_desktop_group_job(sender, desktop_group_id, const.JOB_ACTION_APPLY_DESKTOP_GROUP)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret
    else:
        ret = DesktopGroup.set_desktop_group_apply(desktop_group_id, 0)
        if isinstance(ret, Error):
            return return_error(req, ret)

    # return the group id
    return return_success(req, None, job_uuid)

def handle_describe_desktop_ips(req):

    ''' describe desktop group ips'''

    ctx = context.instance()
    sender = req["sender"]
    
    filter_conditions = build_filter_conditions(req, TB_DESKTOP_NIC)
    desktop_group_id = req.get("desktop_group")
    desktop_id = req.get("desktop")
    network_id = req.get("network")
    private_ips = req.get("private_ips")
    if private_ips:
        filter_conditions["private_ip"] = private_ips
    if network_id:
        filter_conditions["network_id"] = network_id
    
    is_free = req.get("is_free", 0)
    if desktop_group_id or desktop_id: 
        ret = DesktopGroup.get_desktop_ip_resource(filter_conditions, desktop_group_id, desktop_id, is_free, network_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    # global admin user can see all resources
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_NIC]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_NIC]
    else:
        display_columns = {}

    nic_set = ctx.pg.get_by_filter(TB_DESKTOP_NIC, filter_conditions, display_columns,
                                      sort_key = get_sort_key(TB_DESKTOP_NIC, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT)
                                      )
    if nic_set is None:
        logger.error("describe desktop group ip failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    DesktopGroup.format_desktop_ips(nic_set)
    
    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_NIC, filter_conditions)
    if total_count is None:
        logger.error("get desktop group ip count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, nic_set, "desktop_ip", **rep)
