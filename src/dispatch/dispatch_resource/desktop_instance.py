
import context
from log.logger import logger
import constants as const
import db.constants as dbconst
from utils.misc import get_current_time
import dispatch_resource.desktop_disk as Disk
import dispatch_resource.desktop_nic as Nic
import dispatch_resource.desktop_image as Image
import dispatch_resource.desktop_domain as Domain
import dispatch_resource.desktop_common as DeskComm
from common import is_citrix_platform
from dispatch_resource.desktop_common import get_desktop_ivshmem
from api.user.resource_user import del_user_from_resource

def refresh_desktop_info(desktop, desktop_info):
    
    for desktop_key, desktop_value in desktop_info.items():
        
        if desktop_key not in desktop:
            continue
        
        desktop[desktop_key] = desktop_value

    return 0

def refresh_desktop_config(desktop, config):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    update_info = {}
    for desktop_key, desktop_value in config.items():
        
        if desktop_key not in desktop:
            continue
        
        if desktop[desktop_key] != desktop_value:
            update_info[desktop_key] = desktop_value
    
    if not update_info:
        return 0

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: update_info}):
        logger.error("check desktop update term desktop fail: %s" % (update_info))
        return -1

    return 0

def check_desktop_resource(sender, desktops):

    desktop_ids = desktops.keys()
    # check desktop image
    ret = Image.check_desktop_resource_image(sender, desktops)
    if ret < 0:
        logger.error("get desktop resource image fail %s" % desktop_ids)
        return -1

    # desktop nics
    ret = Nic.check_desktop_resource_nic(sender, desktops)
    if ret< 0:
        logger.error("get desktop resource nic fail %s" % desktop_ids)
        return -1

    # check disk
    ret = Disk.check_desktop_resource_disk(sender, desktops)
    if ret < 0:
        logger.error("get desktop resource disk fail %s" % desktop_ids)
        return -1

    return 0

def check_desktop_instance_attributes(desktop, instance):

    modify_key = ["cpu", "memory","ivshmem", "gpu", "usbredir", "clipboard", "filetransfer", "qxl_number"]
    config_info = {}

    for key in modify_key:
        
        if key == "ivshmem":
            ivshmem = get_desktop_ivshmem(desktop["zone"])
            if not ivshmem:
                continue
            if desktop["ivshmem_enable"]:
                if instance[key] != ivshmem:
                    config_info["ivshmem"] = ivshmem
            else:
                if instance[key] != "none":
                    config_info["ivshmem"] = "none"

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

def check_desktop_instance(sender, desktop_ids):

    ctx = context.instance()
    if not desktop_ids:
        return {}
    
    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        logger.error("check desktop instance no found desktop %s" % desktop_ids)
        return -1
    
    # only check instance desktop
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instance:
        return desktops

    instance_ids = desktop_instance.values()
    # get instance resource
    res_instances = DeskComm.get_instances(sender, instance_ids)
    if res_instances is None:
        logger.error("resource describe instance return none %s" % instance_ids)
        return -1
    
    citrix_instances = {}
    if is_citrix_platform(ctx, sender["zone"]):
        machine_names = ctx.pgm.get_desktop_name(desktop_ids)
        if machine_names:       
            citrix_instances = ctx.res.resource_describe_computers(sender["zone"], machine_names=machine_names.values())
            if not citrix_instances:
                citrix_instances = {}
    
    term_desktop = []
    status_desktop = {}
    for desktop_id, desktop in desktops.items():
        
        if desktop_id not in desktop_instance:
            continue
        
        hostname = desktop["hostname"]
        instance_id = desktop_instance[desktop_id]
        # maybe instance has already be deleted
        instance = res_instances.get(instance_id)
        if not instance and hostname not in citrix_instances:

            term_desktop.append(desktop_id)
            continue
        # instance has trans status, cant handle
        trans_status = instance["transition_status"]
        if trans_status:
            logger.error("resource %s in trans status " % trans_status)
            return -1

        # sync desktop/instance status
        desktop = desktops[desktop_id]
        desk_status = desktop["status"]
        inst_status = instance["status"]
        if inst_status in [const.INST_STATUS_CEASED, const.INST_STATUS_TERM]:
            term_desktop.append(desktop_id)
            continue
                
        if desk_status != inst_status:
            if inst_status in [const.INST_STATUS_RUN]:
                status_desktop[desktop_id] = const.INST_STATUS_RUN
                desktop["status"] = const.INST_STATUS_RUN
            elif inst_status in [const.INST_STATUS_STOP, const.INST_STATUS_PEND, const.INST_STATUS_SUSP]:
                status_desktop[desktop_id] = const.INST_STATUS_STOP
                desktop["status"] = const.INST_STATUS_STOP

        # add desktop modify attribute
        need_update = desktop["need_update"]
        if need_update == const.DESKTOP_UPDATE_MODIFY:
            ret = check_desktop_instance_attributes(desktop, instance)
            if ret:
                desktop["modify_config"] = ret

    if term_desktop:
        update_info = {}
        for desktop_id in term_desktop:
            desktop_info = {"instance_id": '', "status": const.INST_STATUS_STOP}
            update_info[desktop_id] = desktop_info

        if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_info):
            logger.error("check desktop update term desktop fail: %s" % (update_info))
            return -1

    if status_desktop:
        update_info = {}
        for desktop_id, dsk_status in status_desktop.items():
            desktop_info = {"status": dsk_status}
            update_info[desktop_id] = desktop_info

        if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_info):
            logger.error("check desktop update desktop fail: %s" % (update_info))
            return -1

    return desktops

# create desktop
def check_create_desktops(sender, desktop_ids):

    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        logger.error("no found desktop %s" % desktop_ids)
        return -1
    
    create_desktop = {}
    for desktop_id, desktop in desktops.items():
        status = desktop["status"]
        if status != const.INST_STATUS_STOP:
            continue
        
        instance_id = desktop["instance_id"]
        if instance_id:
            continue

        create_desktop[desktop_id] = desktop
    
    ret = check_desktop_resource(sender, create_desktop)
    if ret == -1:
        logger.error("Check desktop [%s] resource Fail" % desktop_ids)
        return -1

    return create_desktop

def build_desktop_group_param(desktop):
    
    ctx = context.instance()
    desktop_group_id = desktop["desktop_group_id"]
    if not desktop_group_id:
        return None

    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id, extras=[])
    if not desktop_group:
        return None
    
    desktop_info = {}
    place_group_id = desktop_group["place_group_id"]
    if place_group_id:
        desktop_info["place_group_id"] = place_group_id

    cpu_model = desktop_group.get("cpu_model")
    if cpu_model:
        desktop_info["cpu_model"] = desktop_group["cpu_model"]
        
    cpu_topology = desktop_group.get("cpu_topology")
    if cpu_topology:
        desktop_info["cpu_topology"] = cpu_topology
    
    return desktop_info

def build_desktop_network(sender, desktop):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]

    nics = ctx.pgm.get_nic_desktop(desktop_id, status=const.NIC_STATUS_AVAIL)
    if nics:
        return None
    
    desktop_group_id = desktop["desktop_group_id"]
    select_network = []
    ret = ctx.pgm.get_desktop_group_network(desktop_group_id)
    if not ret:
        return select_network
    
    network_ids = ret.keys()
    for network_id in network_ids:
        
        ret = ctx.res.resource_describe_networks(sender["zone"], network_ids=network_id)
        if not ret:
            continue
        
        network = ret[network_id]
        
        available_ip_count = network.get("available_ip_count", 0)
        if available_ip_count:
            select_network.append(network_id)
            break

    return select_network

def build_desktop_config(sender, desktop):

    ctx = context.instance()
    zone = sender["zone"]
    desktop_id = desktop["desktop_id"]
    desktop_info = {}
    
    desktop_group = {}
    desktop_group_id = desktop["desktop_group_id"]
    if desktop_group_id:
        desktop_group = ctx.pgm.get_desktop_group(desktop_group_id, extras=[])
        if not desktop_group:
            desktop_group = {}
    
    default_passwd = ctx.zone_checker.get_resource_limit(zone, "default_passwd")
    if not default_passwd:
        default_passwd = const.LOGIN_PASSWD
    
    # image
    desktop_image_id = desktop["desktop_image_id"]
    desktop_image = ctx.pgm.get_desktop_image(desktop_image_id)
    if not desktop_image:
        return None
    desktop_info["image_id"] = desktop_image["image_id"]

    desktop_keys = ["cpu", "memory", "instance_class", "gpu", "gpu_class", 
                    "usbredir", "filetransfer", "clipboard", "qxl_number"]
    
    # build image
    for desktop_key in desktop_keys:
        if desktop_key not in desktop:
            logger.error("Build desktop config %s no found key %s" % (desktop_id, desktop_key))
            return None
        
        if desktop_key in desktop_group and desktop[desktop_key]!= desktop_group[desktop_key]:
            desktop_info[desktop_key] = desktop_group[desktop_key]
        else:
            desktop_info[desktop_key] = desktop[desktop_key]

    # graphics_protocol
    if desktop_image["ui_type"] == const.IMG_UI_TYPE_TUI:
        desktop_info["graphics_protocol"] = "vnc"
    elif desktop_image["ui_type"] == const.IMG_UI_TYPE_GUI:
        desktop_info["graphics_protocol"] = "spice"
    else:
        logger.error("desktop_image ui_type = %s, is invalid" % desktop_image["ui_type"])
        return None
    
    ivshmem_enable = desktop.get("ivshmem_enable", 0)
    if ivshmem_enable:
        desktop_info["ivshmem"] = get_desktop_ivshmem(zone)
   
    ret = build_desktop_group_param(desktop)
    if ret:
        desktop_info.update(ret)
    
    desktop_info['login_mode'] = const.LOGIN_MODE_PASSWD
    desktop_info["login_passwd"] = default_passwd
    if desktop_image.get("os_version").lower() == const.OS_VERSION_LINUX:
        zone_connection = ctx.pgm.get_zone_connection(zone)
        keypair = None
        if zone_connection:
            keypair = zone_connection.get("keypair")
        if keypair:
            del desktop_info["login_passwd"]
            desktop_info["login_mode"] = const.LOGIN_MODE_KEYPAIR
            desktop_info["login_keypair"] = keypair

    # hostname
    desktop_info["hostname"] = desktop["hostname"]
    desktop_info["instance_name"] = desktop["hostname"]

    volume_ids = ctx.pgm.get_desktop_volume(desktop_id)
    if volume_ids:
        desktop_info["volumes"] = volume_ids
    else:
        desktop_info["volumes"] = []
        
    network_ids = build_desktop_network(sender, desktop)
    if network_ids is not None:
        desktop_info["vxnets"] = network_ids
        
    return desktop_info
 
def task_create_desktop(sender, desktop, config):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]

    if hasattr(ctx, "usb3_bus"):
        usb3_bus = ctx.usb3_bus
        if usb3_bus:
            config["usb3_bus"] = usb3_bus

    ret = ctx.res.resource_create_instance(sender["zone"], config, desktop)
    if not ret:
        logger.error("resource run instance fail %s " % desktop_id)
        return -1
    instance_id = ret

    desktop_info = {
                    "hostname": desktop["hostname"],
                    "need_update": 0,
                    "instance_id": instance_id,
                    "status": const.INST_STATUS_RUN,
                    "status_time": get_current_time()
                    }

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: desktop_info}):
        logger.error("create desktop update fail: %s, %s" % (desktop_id, desktop_info))
        return -1
    
    refresh_desktop_info(desktop, desktop_info)
    refresh_desktop_config(desktop, config)
    
    if is_citrix_platform(ctx, sender["zone"]):
        ret = Disk.attach_desktop_disks(sender, desktop)
        if ret < 0:
            logger.error("citrix platform attach disk fail %s" % desktop["hostname"])
            return -1
    
    volume_ids = config.get("volumes")
    if not volume_ids:
        return 0

    ret = Disk.update_desktop_volume_status(volume_ids, const.DISK_STATUS_INUSE)
    if ret < 0:
        logger.error("Task create desktop, update disk status fail:%s" % (desktop_id))
        return -1

    return 0

# start desktop
def check_start_desktops(sender, desktops):
    '''
    1. start desktop
    2. create desktop
    '''
    desktop_ids = desktops.keys()
    ctx = context.instance()
    create_desktop = {}
    start_desktop = []
    for desktop_id, desktop in desktops.items():
        instance_id = desktop["instance_id"]
        if not instance_id and not is_citrix_platform(ctx, sender["zone"]):
            create_desktop[desktop_id] = desktop
            start_desktop.append(desktop_id)
            continue

        status = desktop["status"]
        if status == const.INST_STATUS_RUN:
            continue

        start_desktop.append(desktop_id)

    if create_desktop:
        ret = check_desktop_resource(sender, create_desktop)
        if ret < 0:
            logger.error("get desktop config fail %s" % desktop_ids)
            return -1
    
    return (start_desktop, create_desktop)
            
def task_start_desktop(sender, desktop):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]

    ret = ctx.res.resource_start_instances(sender["zone"], desktop)
    if not ret:
        logger.error("resource start instance fail %s" % desktop["instance_id"])
        return -1

    desktop_info = {
                    "need_update": 0,
                    "status": const.INST_STATUS_RUN,
                    "status_time": get_current_time()
                    }
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: desktop_info}):
        logger.error("create desktop update fail: %s" % desktop_info)
        return -1

    refresh_desktop_info(desktop, desktop_info)

    return 0

# reset desktop
def check_reset_desktops(desktops):
    
    '''
    1. reset desktops
    '''
    reset_desktop = {}
    for desktop_id, desktop in desktops.items():
        
        instance_id = desktop["instance_id"]
        if not instance_id:
            continue

        reset_desktop[desktop_id] = desktop

    return reset_desktop

def task_reset_desktop(sender, desktop, is_running=False):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]

    ret = task_delete_instance(sender, desktop)
    if ret < 0:
        logger.error("reset desktop, task delete desktop fail %s" % desktop_id)
        return -1

    ret = Disk.delete_desktop_disks(sender, desktop, True)
    if ret < 0:
        logger.error("reset desktop, task delete disk fail %s" % desktop_id)
        return -1
    
    # check desktop volume to resize
    ret = Disk.resize_desktop_disks(sender, desktop)
    if ret < 0:
        logger.error("reset desktop, task resize disk fail %s" % desktop_id)
        return -1

    if not is_running:
        return 0

    desktop = ctx.pgm.get_desktop(desktop_id)
    if not desktop:
        logger.error("Start Desktop no found Desktop %s" % desktop_id)
        return -1

    ret = build_desktop_config(sender, desktop)
    if ret < 0:
        logger.error("reset desktop, task build desktop fail %s" % desktop_id)
        return -1
    config = ret

    # create disk
    ret = Disk.create_desktop_disk(sender, desktop, config)
    if ret < 0:
        logger.error("task create desktop, create desktop disk fail %s" % desktop_id)
        return -1

    ret = task_create_desktop(sender, desktop, config)
    if ret == -1:
        logger.error("reset desktop, task create desktop fail %s" % desktop_id)
        return -1

    if "vxnets" in config:
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

# restart desktop

def check_restart_desktops(sender, desktops):
    
    '''
    1. restart desktop
    2. reset desktop
    3. stop->modify->start desktop
    '''
    reset_desktop = {}
    stop_desktop = {}
    task_desktop = {}

    for desktop_id, desktop in desktops.items():
        
        instance_id = desktop["instance_id"]
        if not instance_id:
            continue
        
        status = desktop["status"]
        if status != const.INST_STATUS_RUN:
            continue

        need_update = desktop["need_update"]
        if need_update == const.DESKTOP_UPDATE_RESET:
            reset_desktop[desktop_id] = desktop
        elif need_update == const.DESKTOP_UPDATE_MODIFY:
            stop_desktop[desktop_id] = desktop

        task_desktop[desktop_id] = desktop

    return (task_desktop, reset_desktop, stop_desktop)

def task_restart_desktop(sender, desktop):

    ctx = context.instance()
    
    desktop_id = desktop["desktop_id"]
    instance_id = desktop["instance_id"]
    if not instance_id:
        return 0

    ret = ctx.res.resource_restart_instances(sender["zone"], desktop)
    if not ret:
        logger.error("resource restart instance fail %s" % desktop["instance_id"])
        return -1

    desktop_info = {
                    "status": const.INST_STATUS_RUN,
                    "status_time": get_current_time()
                    }
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: desktop_info}):
        logger.error("restart desktop update fail: %s" % desktop_info)
        return -1

    return 0

# stop desktop

def set_desktop_update(desktop_id, update):
    
    ctx = context.instance()
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: {"need_update": update}}):
        logger.error("set desktop update desktop fail: %s, %s" % (desktop_id, update))
        return -1
    
    return 0

def check_stop_desktops(sender, desktops):
    
    '''
    1. stop-> modify desktop
    2. reset desktop
    '''

    reset_desktop = {}
    
    for desktop_id, desktop in desktops.items():
        
        need_update = desktop["need_update"]
        if need_update == const.DESKTOP_UPDATE_RESET:
            reset_desktop[desktop_id] = desktop

    if reset_desktop:
        ret = check_desktop_resource(sender, reset_desktop)
        if ret < 0:
            logger.error("get desktop config fail %s" % reset_desktop.keys())
            return -1

    return (desktops, reset_desktop)

def task_stop_desktop(sender, desktop):

    ctx = context.instance()
    
    desktop_id = desktop["desktop_id"]
    instance_id = desktop["instance_id"]
    
    if instance_id: 
        ret = ctx.res.resource_stop_instances(sender["zone"], desktop)
        if not ret:
            logger.error("stop desktop, resource stop instance fail %s" % instance_id)
            return -1

    desktop_info = {
                    "status": const.INST_STATUS_STOP,
                    "status_time": get_current_time()
                    }
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: desktop_info}):
        logger.error("stop desktop update fail: %s" % desktop_info)
        return -1
    
    return 0

# delete desktop
def clear_desktop_info(desktop):
    
    ctx = context.instance()
    
    desktop_id = desktop["desktop_id"]   
    ctx.pg.delete(dbconst.TB_DESKTOP, desktop_id)
    del_user_from_resource(ctx, desktop_id)

    disks = ctx.pgm.get_disks(desktop_ids=desktop_id)
    if disks:
        update_info = {
                       "need_update": 0,
                       "desktop_id": '',
                       "desktop_name": '',
                       'status': const.DISK_STATUS_AVAIL
                       }
        disk_ids = disks.keys()

        update_disk = {disk_id: update_info for disk_id in disk_ids}
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_DISK, update_disk):
            logger.error("refresh desktop disk update db fail %s" % update_disk)
            return -1
    
    nics = ctx.pgm.get_nic_desktop(desktop_id)
    if nics:
        nic_ids = nics.keys()
        ctx.pg.base_delete(dbconst.TB_DESKTOP_NIC, {"nic_id": nic_ids})

    return 0

def task_delete_instance(sender, desktop, save_nic=False):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    instance_id = desktop["instance_id"]
    hostname = desktop["hostname"]
    
    computer = None
    if is_citrix_platform(ctx, sender["zone"]) and not instance_id:
        ret = ctx.res.resource_describe_computers(sender["zone"], machine_names=[hostname])
        if ret:
            computer = ret.get(hostname)
    
    if instance_id or computer:
        ret = ctx.res.resource_terminate_instances(sender["zone"], desktop)
        if not ret:
            logger.error("resource terminate instance fail %s" % instance_id)
            return -1
    
        desktop_info = {
                        "need_update": 0,
                        "instance_id": '',
                        "status": const.INST_STATUS_STOP,
                        "status_time": get_current_time()
                        }

        if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: desktop_info}):
            logger.error("delete desktop update fail: %s" % desktop_info)
            return -1
    
        refresh_desktop_info(desktop, desktop_info)

        ret = Domain.desktop_leave_domain(sender, desktop)
        if ret < 0:
            logger.error("delete desktop domain %s fail" % (desktop_id))

    ret = Disk.update_desktop_disk_status(desktop, const.DISK_STATUS_ALLOC)
    if ret < 0:
        logger.error("Task create desktop, update disk status fail:%s" % (desktop_id))
        return -1
    
    nics = ctx.pgm.get_nic_desktop(desktop_id)
    if nics:
        nic_ids = nics.keys()
        if not save_nic:
            ctx.pg.base_delete(dbconst.TB_DESKTOP_NIC, {"nic_id": nic_ids})
        else:
            update_info = {}
            for nic_id in nic_ids:
                update_info[nic_id] = {"status": const.NIC_STATUS_AVAIL}
            
            ctx.pg.batch_update(dbconst.TB_DESKTOP_NIC, update_info)
    return 0

# modify desktop
def check_desktop_modify_attributes(desktops):

    modify_desktop = {}
    for desktop_id, desktop in desktops.items():
        
        if "modify_config" not in desktop:
            continue
        
        instance_id = desktop["instance_id"]
        if not instance_id:
            continue
        
        status = desktop["status"]
        if status != const.INST_STATUS_STOP:
            continue
        
        modify_desktop[desktop_id] = desktop
        
    return modify_desktop


def check_need_modify_desektop_attributes(desktop):
    
    ctx = context.instance()
    desktop_group_id = desktop["desktop_group_id"]
    if not desktop_group_id:
        return 0
    
    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id, extras=[])
    if not desktop_group:
        return 0
   
    modify_key = ["ivshmem", "gpu", "usbredir", "clipboard", "filetransfer"]
    resize_key = ["cpu", "memory"]
    modify_info = {}
    resize_info = {}
    for key in modify_key:
        if key not in desktop or key not in desktop_group:
            continue
        
        if desktop[key] != desktop_group[key]:
            modify_info[key] = desktop_group[key]
    
    for key in resize_key:
        if key not in desktop or key not in desktop_group:
            continue
        
        if desktop[key] != desktop_group[key]:
            resize_info[key] = desktop_group[key]
    
    modify_desktop = {}
    if modify_info:
        modify_desktop["modify"] = modify_info
    
    if resize_info:
        modify_desktop["resize"] = resize_info
    
    return modify_desktop

def check_modify_desktop_attributes(sender, desktop, resume_status=True):
    
    ctx = context.instance()
    instance_id = desktop["instance_id"]
    desktop_id = desktop["desktop_id"]
    
    if is_citrix_platform(ctx, desktop["zone"]):
        return 0
    
    modify_desktop = check_need_modify_desektop_attributes(desktop)
    if not modify_desktop:
        return 0

    modify_info = modify_desktop.get("modify")
    resize_info = modify_desktop.get("resize")
    desktop_status = desktop["status"]
    
    
    if desktop_status == const.INST_STATUS_RUN:
        ret = task_stop_desktop(sender, desktop)
        if ret < 0:
            return -1
        
        desktop["status"] = const.INST_STATUS_STOP
    logger.info("resource_modify_instance_attributes  modify_info == %s" %(modify_info))
    if modify_info:
        ret = ctx.res.resource_modify_instance_attributes(sender["zone"], instance_id, modify_info)
        if not ret:
            logger.error("modify instance attributes fail %s" % instance_id)
            return -1
        
    if resize_info:
        
        if "cpu" not in resize_info:
            resize_info["cpu"] = desktop["cpu"]
        
        if "memory" not in resize_info:
            resize_info["memory"] = desktop["memory"]
             
        ret = ctx.res.resource_resize_instances(sender["zone"], instance_id, resize_info)
        if not ret:
            logger.error("resize instance attributes fail %s" % instance_id)
            return -1

        update_info = {desktop_id: resize_info}
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_info):
            logger.error("modify desktop update fail: %s" % update_info)
            return -1
    
    if resume_status and desktop_status == const.INST_STATUS_RUN:
        ret = task_start_desktop(sender, desktop)
        if ret < 0:
            return -1
        desktop["status"] = const.INST_STATUS_RUN
        
    return 0

def task_modify_desktop_attributes(sender, desktop):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]

    need_update = desktop["need_update"]
    if need_update != const.DESKTOP_UPDATE_MODIFY:
        return 0
    
    status = desktop["status"]
    if status != const.INST_STATUS_STOP:
        return 0
    
    instance_id = desktop["instance_id"]

    modify_config = desktop.get("modify_config")
    if not modify_config:
        return 0
    
    modify_key = ["ivshmem", "gpu", "usbredir", "clipboard", "filetransfer", "qxl_number"]
    resize_key = ["cpu", "memory"]
    modify_info = {}
    resize_info = {}
    for key, value in modify_config.items():
        if key in modify_key:
            modify_info[key] = value
        
        if key in resize_key:
            resize_info[key] = value
    
    if modify_info:
        ret = ctx.res.resource_modify_instance_attributes(sender["zone"], instance_id, modify_info)
        if not ret:
            logger.error("modify instance attributes fail %s" % instance_id)
            return -1
        
    if resize_info:
        ret = ctx.res.resource_resize_instances(sender["zone"], instance_id, resize_info)
        if not ret:
            logger.error("resize instance attributes fail %s" % instance_id)
            return -1
    
    update_info = {desktop_id: {"need_update": 0}}
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_info):
        logger.error("modify desktop update fail: %s" % update_info)
        return -1

    return 0

def _send_desktop_hot_keys(sender, desktop_id, keys, timeout, time_step):
    
    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        return -1
    
    desktop = desktops[desktop_id]
    
    instance_id = desktop["instance_id"]
    if not instance_id:
        return -1
    
    ret = ctx.res.resource_send_desktop_hot_keys(sender["zone"], instance_id, keys, timeout, time_step)
    if not ret:
        return -1
    
    return 0

def _send_desktop_message(sender, desktop_id, base64_message):

    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        return -1
    
    desktop = desktops[desktop_id]
    
    instance_id = desktop["instance_id"]
    if not instance_id:
        return -1
    
    ret = ctx.res.resource_send_desktop_message(sender["zone"], instance_id, base64_message)
    if not ret:
        return -1
    
    return 0

def task_update_desktop(sender, desktop):
    
    desktop_id = desktop["desktop_id"]
    instance_id = desktop["instance_id"]
    if not instance_id:
        return 0

    ret = Disk.detach_desktop_disks(sender, desktop)
    if ret < 0:
        logger.error("Task update desktop, detach disk fail [%s]" % (desktop_id))
        return -1

    ret = Disk.attach_desktop_disks(sender, desktop)
    if ret < 0:
        logger.error("Task update desktop, attach disk fail [%s]" % (desktop_id))
        return -1
    
    ret = Disk.delete_desktop_disks(sender, desktop)
    if ret < 0:
        logger.error("Task update desktop, attach disk fail [%s]" % (desktop_id))
        return -1
    
    ret = Disk.resize_desktop_disks(sender, desktop)
    if ret < 0:
        logger.error("Task update desktop, attach disk fail [%s]" % (desktop_id))
        return -1

    ret = Nic.apply_desktop_nics(desktop)
    if ret < 0:
        logger.error("Task update desktop, attach/detach nic fail [%s]" % (desktop_id))
        return -1

    return 0
