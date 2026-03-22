import context
from db.constants  import (
    TB_DESKTOP,
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    PUBLIC_COLUMNS,
    SUPPORTED_MONITOR_RESOURCE_TYPES,
    RESTYPE_DESKTOP,
    TB_DESKTOP_NIC,
    TB_RESOURCE_USER
)
import constants as const
from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
    check_global_admin_console,
    check_admin_console,
    is_citrix_platform,
    is_search_ip,
)
from utils.id_tool import (
    get_resource_type,
)
from utils.net import(
    is_valid_ip
)
from utils.json import json_dump
import random
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
from db.data_types import SearchWordType
import resource_control.desktop.desktop_group as DesktopGroup
import resource_control.desktop.desktop as Desktop
import resource_control.desktop.image as Image
import resource_control.desktop.resource_permission as ResCheck
import resource_control.desktop.disk as Disk
import resource_control.desktop.network as Network
import resource_control.desktop.nic as Nic
import resource_control.citrix.citrix as Citrix
from resource_control.guest.spice import create_spice_connect_files
from resource_control.guest.guest import get_spice_connection_number
from resource_control.guest.qdp import create_qdp_connect_files
from resource_control.policy.usb import delete_usb_policy
from utils.misc import get_columns
import resource_control.store_front.store_front as StoreFront
import resource_control.citrix.guest as CitrixGuest
from api.user.user import is_normal_console
import resource_control.tools.refresh_db as RefreshDB 

def get_apps_by_user(user_id,sf_applist):
    ctx = context.instance()
    existed_broker_app_ids = []
    user_id_groups = ctx.pgm.get_user_group(user_id)
    if user_id_groups:
        user_id_groups.append(user_id)
    else:
        user_id_groups=[user_id]
    ret = ctx.pgm.get_delivery_group_by_user(user_id_groups)
    if not ret:
        return None
    delivery_group_ids = ret
    for delivery_group_id in delivery_group_ids:
        broker_app = ctx.pgm.get_delivery_group_broker_apps(delivery_group_id)
        if broker_app:
            existed_broker_app_ids.extend(broker_app.keys())
    
    if  not existed_broker_app_ids: 
        return None              

    existed_broker_apps = ctx.pgm.get_broker_apps(existed_broker_app_ids)
    if  not existed_broker_apps: 
        return None            

    applist=[]
    for app in sf_applist:
        app_name=app["app_name"]
        zone_id=app["zone"]
        for _,existed_app in existed_broker_apps.items():       
            if existed_app["display_name"]==app_name and existed_app["zone"]==zone_id:
                applist.append(app)
            else:
                continue

    return applist

def filter_desktop_by_ip(search_word):

    ctx = context.instance()
    filter_conditions = {"search_word": SearchWordType(search_word)}
    nic_set = ctx.pg.base_get(TB_DESKTOP_NIC, filter_conditions, ['resource_id'])
    if nic_set is None:
        logger.error("describe desktop failed [%s]" % search_word)
        return None

    desktop_ids = [v['resource_id'] for v in nic_set]
    return desktop_ids

def filter_desktop_by_user(search_word):
    
    if not search_word:
        return None

    ctx = context.instance()
    filter_conditions = {"user_name": SearchWordType(search_word), "resource_type": "desktop"}
    desktop_set = ctx.pg.base_get(TB_RESOURCE_USER, filter_conditions, ['resource_id'])
    if desktop_set is None:
        logger.error("describe desktop failed [%s]" % search_word)
        return None

    desktop_ids = [v['resource_id'] for v in desktop_set]
    return desktop_ids

def filter_desktop_by_hostname(search_word):
    
    if not search_word:
        return None

    ctx = context.instance()
    filter_conditions = {"hostname": SearchWordType(search_word)}
    desktop_set = ctx.pg.base_get(TB_DESKTOP, filter_conditions, ['desktop_id'])
    if desktop_set is None:
        logger.error("describe desktop failed [%s]" % search_word)
        return None

    desktop_ids = [v['desktop_id'] for v in desktop_set]
    return desktop_ids

def handle_describe_normal_desktops(req):

    ctx = context.instance()
    sender = req["sender"]

    rep = {}
    if not is_normal_console(sender):
        rep = {'total_count':0} 
        return return_items(req, None, "desktop", **rep)
    
    owner = sender["owner"]

    # get desktop group set
    filter_conditions = build_filter_conditions(req, TB_DESKTOP)
    desktop_ids = req.get("desktops", [])

    if is_search_ip(req.get('search_word')):

        search_word = req['search_word']
        filtered_desktop_ids = filter_desktop_by_ip(search_word)
        if not filtered_desktop_ids:
            rep = {'total_count':0} 
            return return_items(req, None, "desktop", **rep)
        
        desktop_ids.extend(filtered_desktop_ids)
        
        del filter_conditions['search_word']

    user_desktops = ctx.pgm.get_resource_by_user(owner, desktop_ids)
    if not user_desktops:
        user_desktops = {}
    
    desktop_ids = user_desktops.get(owner)
    if not desktop_ids:
        filter_conditions["desktop_id"] = None
    else:
        filter_conditions["desktop_id"] = desktop_ids

    if "zone" in filter_conditions:
        del filter_conditions["zone"]
    
    ret = StoreFront.check_sf_cookies(req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    sf_cookies = None
    sf_info = None
    if ret:
        sf_cookies, sf_info = ret
    
    # check resource permission
    display_columns = PUBLIC_COLUMNS[TB_DESKTOP]
    desktop_set = ctx.pg.get_by_filter(TB_DESKTOP, filter_conditions, display_columns,
                                      sort_key = get_sort_key(TB_DESKTOP, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if desktop_set is None:
        logger.error("describe desktop group failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                      ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    Desktop.format_normal_desktops(sender, desktop_set)
    
    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP, filter_conditions)
    if total_count is None:
        logger.error("describe desktop total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    ret = StoreFront.get_sf_desktops(owner, desktop_set, sf_cookies, req)
    if ret is not None:
        unassign_desktop, randset_desktop, appset_list = ret
        if unassign_desktop:
            rep["sf_unassign"] = unassign_desktop
            total_count = total_count + len(unassign_desktop)

        if randset_desktop:
            rep["sf_random"] = randset_desktop
            total_count = total_count + len(randset_desktop)

        if appset_list:
            app_list=get_apps_by_user(owner,appset_list)
            rep["sf_app"] = app_list
            if app_list:
                logger.debug("sf_app count %s" %len(app_list))
    if sf_cookies:
        rep["sf_cookies"] = json_dump(sf_cookies)
    
    rep['total_count'] = total_count
    if sf_info:
        rep["sf_message"] = json_dump(sf_info)    
    return return_items(req, desktop_set, "desktop", **rep)

def handle_describe_desktops(req):

    ctx = context.instance()
    sender = req["sender"]

    # get desktop group set
    filter_conditions = build_filter_conditions(req, TB_DESKTOP)

    desktop_group_id = req.get("desktop_group")
    if desktop_group_id:
        filter_conditions["desktop_group_id"] = desktop_group_id
    
    desktop_ids = req.get("desktops")
    if desktop_ids:
        filter_conditions["desktop_id"] = desktop_ids
    
    delivery_group_id = req.get("delivery_group_id")
    if delivery_group_id:
        filter_conditions["delivery_group_id"] = delivery_group_id

    no_delivery_group = req.get("no_delivery_group")
    if no_delivery_group:
        filter_conditions["delivery_group_id"] = ''

    search_word = req.get('search_word', "")
    if is_search_ip(search_word):

        filtered_desktop_ids = filter_desktop_by_ip(search_word)
        if not filtered_desktop_ids:
            rep = {'total_count':0} 
            return return_items(req, None, "desktop", **rep)

        filter_conditions.update({'desktop_id': filtered_desktop_ids})
        del filter_conditions['search_word']
    
    elif search_word:
        filter_desktops = []
        filtered_user_ids = filter_desktop_by_user(search_word)
        if filtered_user_ids:
            filter_desktops.extend(filtered_user_ids)

        filtered_desktop_ids = filter_desktop_by_hostname(search_word)
        if filtered_desktop_ids:
            filter_desktops.extend(filtered_desktop_ids)
        
        if filter_desktops:
            filter_conditions.update({'desktop_id': filter_desktops})
            del filter_conditions['search_word']
        else:
            rep = {'total_count':0} 
            return return_items(req, None, "desktop", **rep)

    # check resource permission
    rep = {}
    # filter admin user desktop group id
    desktop_image_ids = req.get("desktop_image")
    if desktop_image_ids:
        filter_conditions.update({'desktop_image_id': desktop_image_ids})

    user_id = req.get("user")
    if user_id:
        ret = ctx.pgm.get_resource_by_user(user_id)
        if not ret:
            rep = {'total_count':0} 
            return return_items(req, None, "desktop", **rep)
        
        user_desktops = ret.get(user_id, [])
        if user_desktops:
            filter_conditions["desktop_id"] = user_desktops

    # global admin user can see all resources
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP]
    else:
        display_columns = PUBLIC_COLUMNS[TB_DESKTOP]

    desktop_set = ctx.pg.get_by_filter(TB_DESKTOP, filter_conditions, display_columns,
                                      sort_key = get_sort_key(TB_DESKTOP, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if desktop_set is None:
        logger.error("describe desktop group failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                      ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
        
    verbose = req.get("verbose", 0)
    with_monitor = req.get("with_monitor", 0)
    Desktop.format_desktops(sender, desktop_set, verbose, with_monitor)

    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP, filter_conditions)
    if total_count is None:
        logger.error("describe desktop total count fail")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep['total_count'] = total_count

    return return_items(req, desktop_set, "desktop", **rep)

def handle_create_desktop(req):

    ctx = context.instance()
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["hostname", "desktop_image", "cpu", "memory", "instance_class"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    instance_class = req["instance_class"]
    user_id = req.get("user")

    # chech hostname
    hostname = req["hostname"]
    ret = Desktop.check_desktop_hostname(hostname)
    if isinstance(ret, Error):
        return return_error(req, ret)
    hostname = ret

    # check image vaild
    desktop_image_id = req["desktop_image"]
    ret = Image.check_desktop_image_vaild(desktop_image_id, const.IMG_STATUS_AVL, True)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_image = ret[desktop_image_id]

    # register desktops
    ret = Desktop.register_desktop(sender, req, desktop_image, hostname)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_id = ret

    if user_id:
        ret = Desktop.attach_user_to_dekstop(desktop_id, user_id)
        if isinstance(ret, Error):
            return return_error(req, ret)

    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        logger.error("desktop [%s] no found" % desktop_id)
        return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND,
                                       ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_id))
    desktop = desktops[desktop_id]

    # handle disk
    disk_ids = req.get("disks", [])
    if disk_ids:
        ret = Disk.check_desktop_disk_avail(disk_ids, const.DISK_STATUS_AVAIL, True)
        if isinstance(ret, Error):
            return return_error(req, ret)

    disk_size = req.get("disk_size")
    if disk_size:
        instance_class = req["instance_class"]

        ret = ctx.pgm.get_instance_class_disk_type(zone_deploy=ctx.zone_deploy, instance_class=instance_class)
        if not ret:
            logger.error("instance_class %s no found corresponding disk_type" % instance_class)
            return return_error(req, Error(ErrorCodes.RESOURCE_NOT_FOUND,
                                           ErrorMsg.ERR_MSG_INSTANCE_CLASS_NO_FOUND_CORRESPONDING_DISK_TYPE, instance_class))
        instance_class_disk_types = ret

        disk_type = 0
        for _, instance_class_disk_type in instance_class_disk_types.items():
            disk_type = instance_class_disk_type.get("disk_type")

        disk_config = {
            "size": disk_size,
            "disk_type": disk_type,
            "disk_name": req.get("disk_name")
        }

        ret = Disk.create_disks(disk_config, desktop_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
        if ret:
            disk_ids.extend(ret)
    
    if disk_ids:
        ret = Disk.attach_disk_to_dekstop(desktop, disk_ids)
        if isinstance(ret, Error):
            return return_error(req, ret)

    # network
    network_id = req.get("network_id")
    if network_id:
        
        private_ip = None
        network_list = network_id.split("|")
        network_id = network_list[0]
        if len(network_list) > 1:
            private_ip =  network_list[1]
        
        ret = Nic.alloc_desktop_nics(desktop, network_id, private_ip)
        if isinstance(ret, Error):
            return return_error(req, ret)

    # submit desktop job
    ret = Desktop.send_desktop_job(sender, desktop_id, const.JOB_ACTION_CREATE_DESKTOPS)
    if isinstance(ret, Error):
        return return_error(req, ret)
    job_uuid = ret

    ret = {"desktop": desktop_id}
    return return_success(req, None, job_uuid, **ret)

def handle_modify_desktop_attributes(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_id = req["desktop"]
    
    # need maintenance mode
    need_maint_columns = get_columns(req, ["cpu", "memory","ivshmem", "gpu", 'qxl_number', 
                                           "usbredir", "clipboard", "filetransfer", "no_sync", "description"])

    description = need_maint_columns.get("description")
    if description is not None:
        ret = Desktop.modify_desktop_description(desktop_id, description)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        del need_maint_columns["description"]

    if is_normal_console(sender):
        qxl_number = need_maint_columns.get("qxl_number")
        if qxl_number in const.SUPPORTED_QXL_NUMBER:
            ret = Desktop.check_desktop_vaild(desktop_id, status=const.INST_STATUS_STOP)
            if isinstance(ret, Error):
                return return_error(req, ret)
            desktop = ret[desktop_id]
            ret = Desktop.modify_desktop_attributes(desktop, need_maint_columns)
            if isinstance(ret, Error):
                return return_error(req, ret)

            modify_desktop = ret
            job_uuid = None
            # submit desktop job
            if modify_desktop:
                ret = Desktop.send_desktop_job(sender, desktop_id, const.JOB_ACTION_MODIFY_DESKTOP_ATTRIBUTES)
                if isinstance(ret, Error):
                    return return_error(req, ret)
                job_uuid = ret

            return return_success(req, None, job_uuid)
        return return_success(req, {})
    
    modify_desktop = None
    if need_maint_columns:

        ret = Desktop.check_desktop_vaild(desktop_id, status=const.INST_STATUS_STOP)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop = ret[desktop_id]

        # check desktop group vaild
        desktop_group_id = desktop["desktop_group_id"]
        if desktop_group_id:
            ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, None)
            if isinstance(ret, Error):
                return return_error(req, ret)

        ret = Desktop.modify_desktop_attributes(desktop, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

        modify_desktop = ret

    job_uuid = None
    # submit desktop job
    if modify_desktop:
        ret = Desktop.send_desktop_job(sender, desktop_id, const.JOB_ACTION_MODIFY_DESKTOP_ATTRIBUTES)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_delete_desktops(req):
    
    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktops"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_ids = req["desktops"]
    save_disk = req.get("save_disk", 1)

    ret = Desktop.check_desktop_vaild(desktop_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktops = ret

    for desktop_id, desktop in desktops.items():
        
        # update desktop group info
        desktop_group_id = desktop["desktop_group_id"]
        if not desktop_group_id:
            continue

        # check desktop group status
        ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, None)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_group = ret[desktop_group_id]

        if is_citrix_platform(ctx, sender["zone"]):
            ret = Citrix.check_delete_desktops(desktop)
            if isinstance(ret, Error):
                return return_error(req, ret)
        
        # set user status
        desktop_group_type = desktop_group["desktop_group_type"]
        if desktop_group_type == const.DG_TYPE_RANDOM:
            continue
        
        if not is_citrix_platform(ctx, sender["zone"]):
            user_ids = ctx.pgm.get_resource_user(desktop_id)
            if not user_ids:
                user_ids = []
            ret = DesktopGroup.set_desktop_group_user_status(desktop_group_id, user_ids, const.USER_STATUS_DISABLED)
            if isinstance(ret, Error):
                return return_error(req, ret)

    # delete desktop
    ignore_save = False
    if save_disk == 0:
        ignore_save = True
    ret = Desktop.delete_desktops(sender, desktops, ignore_save)
    if isinstance(ret, Error):
        return return_error(req, ret)

    delete_desktop = ret

    job_uuid = None
    if delete_desktop:
        # submit desktop job
        ret = Desktop.send_desktop_job(sender, delete_desktop, const.JOB_ACTION_DELETE_DESKTOPS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

        if not is_citrix_platform(ctx, sender["zone"]):
            delete_usb_policy(object_ids=delete_desktop)

    return return_success(req, None, job_uuid)

def handle_restart_desktops(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktops", "desktop_group"], True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_ids = req.get("desktops")
    desktop_group_id = req.get("desktop_group")

    restart_desktop = []
    if desktop_group_id:

        # check desktop group vaild
        ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_group = ret[desktop_group_id]

        # check and free random desktop
        ret = Desktop.refresh_random_desktop_count(desktop_group)
        if isinstance(ret, Error):
            return return_error(req, ret)

        # check desktop vaild
        ret = Desktop.check_desktop_vaild(desktop_group_id=desktop_group_id, status=const.INST_STATUS_RUN)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktops = ret
        
        if desktops:
            ret = Desktop.restart_desktops(sender, desktops)
            if isinstance(ret, Error):
                return return_error(req, ret)

            restart_desktop = ret
    else:

        ret = Desktop.check_desktop_vaild(desktop_ids, status = const.INST_STATUS_RUN)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktops = ret

        ret = Desktop.restart_desktops(sender, desktops)
        if isinstance(ret, Error):
            return return_error(req, ret)

        restart_desktop = ret

    # submit desktop job
    job_uuid = None
    if restart_desktop:
        ret = Desktop.send_desktop_job(sender, restart_desktop, const.JOB_ACTION_RESTART_DESKTOPS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_start_desktops(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktops", "desktop_group"], True)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_ids = req.get("desktops")
    desktop_group_id = req.get("desktop_group")

    start_desktop = []
    if desktop_group_id:

        # check desktop group vaild
        ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)

        # check desktop vaild
        ret = Desktop.check_desktop_vaild(desktop_group_id=desktop_group_id, status=const.INST_STATUS_STOP)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktops = ret
        
        if desktops:
            # start desktops
            ret = Desktop.start_desktops(desktops)
            if isinstance(ret, Error):
                return return_error(req, ret)

            start_desktop = ret
    else:

        ret = Desktop.check_desktop_vaild(desktop_ids, None, const.INST_STATUS_STOP)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktops = ret

        ret = Desktop.start_desktops(desktops)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        start_desktop = ret

    # submit desktop job
    job_uuid = None
    if start_desktop:
        ret = Desktop.send_desktop_job(sender, start_desktop, const.JOB_ACTION_START_DESKTOPS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_stop_desktops(req):
    
    sender = req["sender"]
    ctx = context.instance()
    ret = ResCheck.check_request_param(req, ["desktops", "desktop_group"], True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_ids = req.get("desktops")
    desktop_group_id = req.get("desktop_group")

    stop_desktop = []
    if desktop_group_id:

        # check desktop group vaild
        ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktop_group = ret[desktop_group_id]
        
        # get run status desktop
        ret = Desktop.check_desktop_vaild(desktop_group_id=desktop_group_id, status=const.INST_STATUS_RUN)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktops = ret
    
        if desktops:
            desktop_ids = desktops.keys()

            # check and free random desktop
            ret = Desktop.refresh_random_desktop_count(desktop_group)
            if isinstance(ret, Error):
                return return_error(req, ret)
            
            desktops = ctx.pgm.get_desktops(desktop_ids)
            
            ret = Desktop.stop_desktops(sender, desktops)
            if isinstance(ret, Error):
                return return_error(req, ret)

            stop_desktop = ret
    else:

        ret = Desktop.check_desktop_vaild(desktop_ids, None, const.INST_STATUS_RUN)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktops = ret

        ret = Desktop.stop_desktops(sender, desktops)
        if isinstance(ret, Error):
            return return_error(req, ret)

        stop_desktop = ret

    # submit desktop job
    job_uuid = None
    if stop_desktop:
        ret = Desktop.send_desktop_job(sender, stop_desktop, const.JOB_ACTION_STOP_DESKTOPS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_reset_desktops(req):
    
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ["desktops", "desktop_group"], True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_ids = req.get("desktops")
    desktop_group_id = req.get("desktop_group")
    reset_desktop = []

    if desktop_group_id:
        # check desktop group vaild
        ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id)
        if isinstance(ret, Error):
            return return_error(req, ret)

        desktop_group = ret[desktop_group_id]
        # get reset desktop
        ret = Desktop.check_desktop_vaild(desktop_group_id=desktop_group_id, status=const.INST_STATUS_STOP)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktops = ret
        
        if desktops:
            desktops = ret
            desktop_ids = desktops.keys()
            # check and free random desktop
            ret = Desktop.refresh_random_desktop_count(desktop_group, desktop_ids)
            if isinstance(ret, Error):
                return return_error(req, ret)
            ret = Desktop.reset_desktops(desktops)
            if isinstance(ret, Error):
                return return_error(req, ret)
            reset_desktop = ret
    else:
        ret = Desktop.check_desktop_vaild(desktop_ids, None, const.INST_STATUS_STOP)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktops = ret
        ret = Desktop.reset_desktops(desktops)
        if isinstance(ret, Error):
            return return_error(req, ret)
        reset_desktop = ret

    # submit desktop job
    job_uuid = None
    if reset_desktop:
        ret = Desktop.send_desktop_job(sender, reset_desktop, const.JOB_ACTION_RESET_DESKTOPS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_attach_user_to_desktop(req):
    
    ret = ResCheck.check_request_param(req, ["desktop", "user_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_id = req["desktop"]
    user_ids = req["user_ids"]

    ret = Desktop.check_desktop_vaild(desktop_id, None, None, False)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = Desktop.check_attach_user_to_desktop(desktop_id, user_ids)
    if ret:
        user_ids = ret

    ret = Desktop.attach_user_to_dekstop(desktop_id, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_detach_user_from_desktop(req):
    
    ret = ResCheck.check_request_param(req, ["desktop_id", "user_ids"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_id = req["desktop_id"]
    user_ids = req["user_ids"]

    ret = Desktop.check_desktop_vaild(desktop_id, None, None, False)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop = ret[desktop_id]

    desktop_group_id = desktop["desktop_group_id"]
    if desktop_group_id:
        logger.error("desktop has desktop group dont detach %s" % desktop_id)
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_DESKTOP_HAS_DESKTOP_GROUP, (desktop_id, desktop_group_id)))
        
    ret = Desktop.detach_user_from_dekstop(desktop_id, user_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_set_desktop_monitor(req):
    """ set desktop monitor
    """
    ret = ResCheck.check_request_param(req, ["desktops", "monitor"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_ids = req["desktops"]
    monitor = req["monitor"]

    ret = Desktop.set_desktop_monitor(desktop_ids, monitor)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_set_desktop_auto_login(req):
    """ set desktop auto login
    """
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop", "auto_login"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_id = req["desktop"]
    auto_login = req["auto_login"]

    ret = Desktop.set_desktop_auto_login(sender, desktop_id, auto_login)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_modify_desktop_description(req):
    """ modify desktop description
    """

    ret = ResCheck.check_request_param(req, ["desktop"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_id = req["desktop"]
    description = req.get("description")

    ret = Desktop.modify_desktop_description(desktop_id, description)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_apply_random_desktop(req):
    
    sender = req["sender"]
    ctx = context.instance()
    
    ret = ResCheck.check_request_param(req, ["user", "desktop_group"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    user_id = req["user"]
    desktop_group_id = req["desktop_group"]
    
    ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, const.DG_STATUS_NORMAL, False, const.DG_TYPE_RANDOM)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = DesktopGroup.check_desktop_group_user_vaild(user_id, desktop_group_id, status=const.USER_STATUS_ACTIVE)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = ctx.pgm.get_free_random_desktops(desktop_group_id)
    if not ret:
        logger.error("desktop group[%s] no enough desktop[%s][%s]" % (desktop_group_id, ret, user_id))
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_NO_RESOURCE_SPECIFIED, desktop_group_id))

    random_desktop = ret
    desktop_ids = random_desktop.keys()
    desktop_index = random.randint(0, len(desktop_ids)-1)
    desktop_id = desktop_ids[desktop_index]

    desktop = random_desktop[desktop_id]

    ret = Desktop.attach_user_to_dekstop(desktop_id, user_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    job_uuid = None
    status = desktop["status"]
    if status == const.INST_STATUS_STOP:
        ret = Desktop.start_desktops(desktop)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        ret = Desktop.send_desktop_job(sender, desktop_id, const.JOB_ACTION_START_DESKTOPS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    ret = {'desktop': desktop_id}
    return return_success(req, None, job_uuid, **ret)

def handle_free_random_desktops(req):
    
    sender = req["sender"]
    ctx = context.instance()
    ret = ResCheck.check_request_param(req, ["desktops"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    desktop_ids = req["desktops"]

    ret = Desktop.check_desktop_vaild(desktop_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = ctx.pgm.get_group_by_desktop(desktop_ids)
    if not ret:
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_NO_RESOURCE_SPECIFIED))
    desktop_group_index = ret
    reset_desktop = []
    
    for desktop_group_id, desk_ids in desktop_group_index.items():
        # check desktop group vaild
        ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, const.DG_STATUS_NORMAL, desktop_group_type=const.DG_TYPE_RANDOM)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        ret = ctx.pgm.get_desktops(desk_ids)
        if ret:
            desktops = ret

            ret = Desktop.reset_desktops(desktops)
            if isinstance(ret, Error):
                return return_error(req, ret)
    
            reset_desktop.extend(ret)

    # submit desktop job
    job_uuid = None
    if reset_desktop:
        ret = Desktop.send_desktop_job(sender, reset_desktop, const.JOB_ACTION_RESET_DESKTOPS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_create_brokers(req):

    sender = req["sender"]
    ctx = context.instance()
    zone_id = sender["zone"]
    
    desktop_id = req.get("desktop")
    desktop_image_id = req.get("desktop_image")
    protocol_type = req.get("protocol_type", const.DESKTOP_CONNECT_PROTOCOL_SPICE)
    
    desktop = {}
    if desktop_id:
        
        ret = Desktop.check_desktop_vaild(desktop_id, None, const.INST_STATUS_RUN)
        if isinstance(ret, Error):
            return return_error(req, ret)
        desktops = ret
        desktop = desktops[desktop_id]
        
        if zone_id != desktop["zone"]:
            zone_id = desktop["zone"]
    
    sf_cookie=req.get("sf_cookie")
    if sf_cookie and is_citrix_platform(ctx, zone_id):
        ui_type=const.IMG_UI_TYPE_SF
        ret = ResCheck.check_request_param(req, ["ica_uri", "assign_state", "sf_cookie"])
        if isinstance(ret, Error):
            return return_error(req, ret)
        assign_state = req.get("assign_state")
        if assign_state=='0' or assign_state=='2':
            ret = ResCheck.check_request_param(req, ["assign_uri"])
            if isinstance(ret, Error):
                return return_error(req, ret)
        
        sf_sender = {"zone": zone_id, "owner": sender["owner"]}
        ret = StoreFront.create_store_front_broker(sf_sender, req)
        if isinstance(ret, Error):
            return return_error(req, ret)

        # update login record
        client_ip = req.get("client_ip", "127.0.0.1")
        CitrixGuest.create_desktop_login_record(sender["owner"], zone_id, desktop_id, client_ip, 1)

        ret = {'desktop_brokers': ret}
        return return_success(req, None, **ret)  
    else: 
        ui_type = None
        if protocol_type==const.DESKTOP_CONNECT_PROTOCOL_SPICE:
            ui_type = const.IMG_UI_TYPE_GUI
        elif protocol_type==const.DESKTOP_CONNECT_PROTOCOL_VNC:
            ui_type = const.IMG_UI_TYPE_TUI
        elif protocol_type==const.DESKTOP_CONNECT_PROTOCOL_QDP:
            ui_type = const.IMG_UI_TYPE_QDP
        else:
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                           ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "protocol_type"))
        desktop_brokers = {}

        if desktop_id and ui_type!=const.IMG_UI_TYPE_QDP:
            
            if desktop["desktop_image_id"]:
                ret = Image.check_desktop_image_ui_type(sender, desktop["desktop_image_id"])
                if isinstance(ret, Error):
                    return return_error(req, ret)
                ui_type = ret
            else:
                ui_type = const.IMG_UI_TYPE_TUI
            
            desktop_group_id = desktop["desktop_group_id"]
            
            if desktop_group_id:
                ret = DesktopGroup.check_desktop_group_vaild(desktop_group_id, const.DG_STATUS_NORMAL)
                if isinstance(ret, Error):
                    return return_error(req, ret)
            
            is_token = 1 if ui_type == const.IMG_UI_TYPE_TUI else 0

            instance_id = desktop["instance_id"]
            if instance_id:
                ret = Desktop.create_broker(sender, instance_id, is_token)
                if isinstance(ret, Error):
                    return return_error(req, ret)

                desktop_broker = ret
                desktop_broker["desktop_id"] = desktop_id
                desktop_broker["ui_type"] = ui_type
                desktop_broker["full_screen"] = req["full_screen"]
                if desktop_group_id:
                    desktop_broker["desktop_group_id"] = desktop_group_id
                
                vnc_proxy_ips = ctx.pgm.get_vnc_proxy_ip()
                if vnc_proxy_ips:
                    port = str(desktop_broker.get("broker_port", 0))
                    zone_id = zone_id
                    zone_proxy = vnc_proxy_ips.get(zone_id)
                    if zone_proxy:
                        proxy_ip = zone_proxy.get(port)
                        if proxy_ip and is_valid_ip(proxy_ip) and ui_type == const.IMG_UI_TYPE_TUI:
                            desktop_broker["broker_host"] = proxy_ip

                desktop_brokers[desktop_id] = desktop_broker

        elif desktop_id and ui_type==const.IMG_UI_TYPE_QDP:
            nics = ctx.pgm.get_nic_desktop(desktop_ids=[desktop_id])
            if not nics:
                logger.error("desktop have not nic")
                return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                               ErrorMsg.ERR_MSG_INSTANCE_CREATE_BROKER_FAILED))
            desktop_broker = {}
            desktop_broker["type"] = const.IMG_UI_TYPE_QDP
            private_ips = []
            for _, nic in nics.items():
                private_ips.append(nic["private_ip"])
            private_ip_size = len(private_ips)
            if private_ip_size == 1:
                desktop_broker["host"] = private_ips[0]
            elif private_ip_size > 1:
                private_ip = private_ips[0]
                for i in range(1, private_ip_size):
                    private_ip = "%s,%s" % (private_ip, private_ips[i])
                desktop_broker["host"] = private_ip
            else:
                return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                               ErrorMsg.ERR_MSG_INSTANCE_CREATE_BROKER_FAILED))
            desktop_broker["port"] = const.DESKTOP_CONNECTION_WITH_QDP_PORT
            desktop_broker["full_screen"] = req["full_screen"]
            desktop_brokers[desktop_id] = desktop_broker

        elif desktop_image_id:
            
            ret = Image.check_desktop_image_vaild(desktop_image_id, const.IMG_STATUS_EDITED)
            if isinstance(ret, Error):
                return return_error(req, ret)
            desktop_image = ret[desktop_image_id]
    
            ret = Image.check_desktop_image_ui_type(sender, desktop_image_id)
            if isinstance(ret, Error):
                return return_error(req, ret)
            ui_type = ret
            
            instance_id = desktop_image["instance_id"]
            ret = Desktop.create_broker(sender, instance_id)
            if isinstance(ret, Error):
                return return_error(req, ret)
    
            desktop_broker = ret
            desktop_broker["desktop_image_id"] = desktop_image_id
            desktop_broker["ui_type"] = ui_type
            desktop_broker["full_screen"] = req["full_screen"]
            desktop_broker["desktop_id"] = desktop_id
            desktop_brokers[desktop_image_id] = desktop_broker
    
    if ui_type == const.IMG_UI_TYPE_GUI:
        # check license
        ctx = context.instance()
        conn_number = get_spice_connection_number()
        if conn_number >= ctx.license["number"]:
            logger.error("can not create spice connect file, out of license number limit")
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, ErrorMsg.ERR_CODE_MSG_LICENSE_OUT_OF_LIMIT))

        ret = create_spice_connect_files(desktop_brokers)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = {'desktop_brokers': ret}
        return return_success(req, None, **ret)
    elif ui_type == const.IMG_UI_TYPE_QDP:
        ret = create_qdp_connect_files(desktop_brokers)
        if isinstance(ret, Error):
            return return_error(req, ret)

        ret = {'desktop_brokers': ret}
        return return_success(req, None, **ret)
    else:
        ret = {'desktop_brokers': ret}
        return return_success(req, None, **ret)

def handle_delete_brokers(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktops"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_ids = req["desktops"]
    ret = Desktop.check_desktop_vaild(desktop_ids, None, const.INST_STATUS_RUN)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktops = ret
    
    ret = Desktop.delete_brokers(sender, desktops)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_desktop_leave_networks(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktops", "network"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    desktop_ids = req["desktops"]
    network_id = req["network"]

    # check desktop vaild
    ret = Desktop.check_desktop_vaild(desktop_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    # check network vaild
    ret = Network.check_desktop_network_vaild(sender, network_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    network = ret[network_id]
    
    ret = Desktop.desktop_leave_network(desktop_ids, network)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    detach_desktop = ret
    job_uuid = None
    
    if detach_desktop:
        # submit desktop job
        ret = Desktop.send_desktop_job(sender, detach_desktop, const.JOB_ACTION_UPDATE_DESKTOP_NICS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_desktop_join_networks(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktops", "network"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_ids = req["desktops"]
    network_id = req["network"]

    # check desktop vaild
    ret = Desktop.check_desktop_vaild(desktop_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktops = ret

    # check network vaild
    ret = Network.check_desktop_network_vaild(sender, network_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    network = ret[network_id]

    ret = Desktop.desktop_join_network(desktops, network)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    join_desktop = ret
    job_uuid = None

    # submit desktop job
    if join_desktop:
        ret = Desktop.send_desktop_job(sender, join_desktop, const.JOB_ACTION_UPDATE_DESKTOP_NICS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_modify_desktop_ip(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["desktop", "network", "private_ip"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop_id = req["desktop"]
    network_id = req["network"]
    private_ip = req["private_ip"]

    # check desktop vaild
    ret = Desktop.check_desktop_vaild(desktop_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    desktop = ret[desktop_id]

    ret = Network.check_desktop_network_vaild(sender, network_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    network = ret[network_id]

    ret = Desktop.modify_desktop_ip(desktop, network, private_ip)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # submit desktop job
    ret = Desktop.send_desktop_job(sender, desktop_id, const.JOB_ACTION_UPDATE_DESKTOP_NICS)
    if isinstance(ret, Error):
        return return_error(req, ret)
    job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_get_desktop_monitor(req):
    
    sender = req["sender"]
    ctx = context.instance()
    resource_id = req["resource"]

    rt = get_resource_type(resource_id)
    
    if rt not in SUPPORTED_MONITOR_RESOURCE_TYPES:
        logger.error("no vpc network specified in request [%s]" % (req))
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                                       ErrorMsg.ERR_MSG_NO_RESOURCE_SPECIFIED))

    desktop_id = resource_id
    if rt == RESTYPE_DESKTOP:
        desktop_instance = ctx.pgm.get_desktop_instance(desktop_id)
        if not desktop_instance:
            rep = {resource_id: []}
            return return_success(req, None, **rep)

        resource_id = desktop_instance[desktop_id]
    
    meters = req.get("meters")
    step = req.get("step")
    start_time = req.get("start_time")
    end_time = req.get("end_time")
    
    ret = ctx.res.resource_get_monitoring_data(sender["zone"], resource_id, meters, step, start_time, end_time)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    meter_set = ret

    ret_rep = {
               "meter_set": meter_set,
               "resource_id": desktop_id
              }

    return return_success(req, None, **ret_rep) 

def handle_check_desktop_hostname(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["hostname", "name_type"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    hostname = req["hostname"]
    name_type = req["name_type"]
    
    is_repeat = 0
    if name_type == const.HOSTNAME_TYPE_DG:
        ret = DesktopGroup.check_desktop_group_naming_rule(sender["zone"], hostname)
        if isinstance(ret, Error):
            is_repeat  = 1
    elif name_type == const.HOSTNAME_TYPE_DESKTOP:
        ret = Desktop.check_desktop_hostname(hostname)
        if isinstance(ret, Error):
            is_repeat  = 1

    ret = {"is_repeat": is_repeat}
    return return_success(req, None, **ret)

def handle_download_log(req):
    """ download log
    """
    date = req["date"]
    ret = Desktop.download_pitrix_log(date)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = {'pitrix_log': ret}
    return return_success(req, None, **ret)

def handle_refresh_desktop_db(req):
    
    
    db_type = req["db_type"]
    
    if db_type not in const.REFRESH_DB_TYPES:
        logger.error("refresh desktop db type %s dismatch" % (db_type))
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                                       ErrorMsg.ERR_MSG_NO_RESOURCE_SPECIFIED))    
    
    refresh_count = 0
    if db_type == const.REFRESH_DESKTOP_DB_DESKTOP_OWNER:
        ret = RefreshDB.refresh_desktop_owner()
        if isinstance(ret, Error):
            return return_error(req, ret)

        refresh_count = ret if ret is not None else 0
    
    ret = {"refresh_count": refresh_count}

    return return_success(req, None, **ret)

