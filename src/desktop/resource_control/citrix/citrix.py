from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import constants as const
import db.constants as dbconst

from utils.id_tool import(
    UUID_TYPE_DESKTOP,
    UUID_TYPE_DESKTOP_DISK,
    get_uuid
)
from utils.misc import get_current_time
import resource_control.citrix.delivery_group as DeliveryGroup
import resource_control.desktop.disk as Disk
from api.citrix.citrix_common import check_citrix_update
import api.user.resource_user as ResUser

def check_delete_desktops(desktop):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    delivery_group_id = desktop["delivery_group_id"]
    if not delivery_group_id:
        return None

    delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_id)
    if not delivery_groups:
        return None
    else:
        logger.error("desktop in delivery group %s fail" % desktop_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_CITIRX_DESKTOP_IN_DELIVERY_GROUP, (desktop_id, delivery_group_id))

def modify_citrix_desktop_group(desktop_group, modify_config):
    
    citrix_update = {}
    desktop_image_id = modify_config.get("desktop_image_id")
    if desktop_image_id and desktop_image_id != desktop_group["desktop_image_id"]:   
        citrix_update["desktop_image"] = desktop_image_id
    
    desktop_count = modify_config.get("desktop_count")
    if desktop_count:
        citrix_update["desktop_count"] = desktop_count

    return citrix_update

def check_delete_citrix_desktop_groups(desktop_group):

    ctx = context.instance()
    
    desktop_group_name = desktop_group["desktop_group_name"]
    desktop_group_id = desktop_group["desktop_group_id"]
    zone_id = desktop_group["zone"]
    
    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
    if desktops:
        logger.error("catalog %s has desktop %s ,cant delete" % (desktop_group_name, desktops.keys()))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKTOP_GROUP_HAS_DESKTOP_RESOURCE, desktop_group_name)

    disks = ctx.pgm.get_disks(desktop_group_ids=desktop_group_id)
    if disks:
        logger.error("ddc no found computer catalog %s fail" % desktop_group_name)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKTOP_GROUP_HAS_DISK_RESOURCE, desktop_group_name)

    computers = ctx.res.resource_describe_computers(zone_id, catalog_name=desktop_group_name)
    if computers:
        logger.error("catalog %s has desktop,cant delete" % (desktop_group_name))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DESKTOP_GROUP_HAS_DESKTOP_RESOURCE_IN_DDC, desktop_group_name)

    return desktop_group_id

def build_load_computer_catalog(sender, catalog_set, req):
    
    ctx = context.instance()
    zone_id = sender["zone"]
    desktop_group_req = []
    required_params = ["desktop_image","cpu","memory","naming_rule","instance_class"]
    for _, catalog in catalog_set.items():
        
        req_info = {}
        
        provision_type = catalog.get("provision_type")
        if provision_type == const.PROVISION_TYPE_MANUAL:
            
            managed_resource = req.get("managed_resource")
            ret = ctx.zone_checker.check_managed_resource(zone_id, managed_resource, is_update=False)
            if isinstance(ret, Error):
                return ret

            req_info["managed_resource"] = managed_resource
            req_info["desktop_group_name"] = catalog["name"]
            req_info["provision_type"] = const.PROVISION_TYPE_MANUAL
        else:
            managed_resource = catalog["citrix_area"]
            ret = ctx.zone_checker.check_managed_resource(zone_id, managed_resource, is_update=True)
            if isinstance(ret, Error):
                return ret
            for param in required_params:
                if param not in catalog:
                    logger.error("load computer catalogs no found param %s" % param)
                    return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_LOAD_COMPUTER_CATALOG_NO_PARAM, param)
    
                req_info[param] = catalog[param]
            
            ret = ctx.zone_checker.check_cpu_memory_pairs(zone_id, req_info["cpu"], req_info["memory"], is_update=True)
            if isinstance(ret, Error):
                return ret
    
            req_info["managed_resource"] = managed_resource
            req_info["desktop_group_type"] = const.DG_TYPE_CITIRX
            req_info["desktop_group_name"] = catalog["name"]
            if catalog["gpu"]:
                req_info["gpu"] = catalog["gpu"]
                req_info["gpu_class"] = catalog.get("gpu_class", 0)
            
            req_info["desktop_dn"] = catalog["desktop_dn"]
    
            req_info["allocation_type"] = catalog["allocation_type"]
            if catalog["place_group_id"]:
                req_info["place_group_id"] = catalog["place_group_id"]
            
            if "disk_sizes" in catalog:
                req_info["disk_size"] = ",".join(catalog["disk_sizes"])
            
            req_info["networks"] = catalog["networks"]
            
            image_id = req_info["desktop_image"]
            ret = ctx.pgm.get_base_image(image_id)
            if not ret:
                return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_LOAD_COMPUTER_CATALOG_NO_FOUND_IMAGE, image_id)
            
            desktop_image_id = ret["desktop_image_id"]
            req_info["desktop_image"] = desktop_image_id
            req_info["provision_type"] = const.PROVISION_TYPE_MCS

        desktop_group_req.append(req_info)

    return desktop_group_req

def check_citrix_disks(desktop, disk_config):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    disk_config_id = disk_config["disk_config_id"]
    ret = ctx.pgm.get_desktop_volume(desktop_id, disk_config_id)
    if ret:
        return None
    desktop_volumes = ret
    if not desktop_volumes:
        desktop_volumes = {}

    zone = desktop["zone"]
    instance_id = desktop["instance_id"]
    if not instance_id:
        return None

    ret = ctx.res.resource_describe_instances(zone, instance_id)
    if not ret:
        return None
    instance = ret[instance_id]

    volume_ids = instance.get("volume_ids")
    if not volume_ids:
        return None
    
    disk_volumes = ctx.pgm.get_desktop_volumes(desktop_id)
    if not disk_volumes:
        disk_volumes = {}
    
    ret = ctx.res.resource_describe_volumes(zone, volume_ids)
    if not ret:
        logger.error("no found volume %s" % volume_ids)
        return None
    volumes = ret
    
    check_size = disk_config["size"]
    
    new_disks = {}
    for volume_id, volume in volumes.items():
        
        if volume_id in desktop_volumes:
            continue
        
        if int(volume["size"]) != check_size:
            continue
        
        if volume_id in disk_volumes:
            continue
        
        volume_name = volume["volume_name"]
        if int(volume["size"]) == const.IDENTIFY_DISK_SIZE and const.IDENTIFY_DISK_NAME in volume_name:
            continue
        
        disk_id = get_uuid(UUID_TYPE_DESKTOP_DISK, ctx.checker)
        disk_info = dict(disk_id=disk_id,
                         volume_id=volume_id,
                         desktop_id = desktop_id,
                         desktop_name= desktop["hostname"],
                         disk_config_id= disk_config["disk_config_id"],
                         disk_type=volume["volume_type"],
                         desktop_group_id=desktop["desktop_group_id"],
                         desktop_group_name=desktop["desktop_group_name"],
                         size=volume["size"],
                         status=const.DISK_STATUS_INUSE,
                         need_update = 0,
                         disk_name = volume["volume_name"],
                         create_time=get_current_time(False),
                         status_time=get_current_time(False),
                         user_name = desktop["user_name"],
                         zone=desktop["zone"]
                        )
        new_disks[disk_id] = disk_info
    
    if not new_disks:
        return None
    
    # register desktop group
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_DISK, new_disks):
        logger.error("create disk insert new db fail %s" % new_disks)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    resource_users = ctx.pgm.get_resource_user(desktop_id)
    if not resource_users:
        resource_users = []
    
    if resource_users:
        for disk_id, _ in new_disks.items():
            ret = ResUser.add_user_to_resource(ctx, disk_id, resource_users)
            if isinstance(ret, Error):
                return ret

    return desktop_id

def update_desktop_disk(desktops, disk_config):
    
    desktop_ids = []
    for _, desktop in desktops.items():
        
        if desktop["transition_status"]:
            continue
        
        ret = check_citrix_disks(desktop, disk_config)
        if isinstance(ret, Error):
            return ret
        if ret:
            desktop_ids.append(ret)
   
    return desktop_ids

def load_delivery_group_computers(sender, delivery_group, computer_names=None):
    
    ctx = context.instance()
    
    delivery_group_id = delivery_group["delivery_group_id"]
    existed_desktops = ctx.pgm.get_desktops(delivery_group_id=delivery_group_id)
    if not existed_desktops:
        existed_desktops = {}
    
    delivery_group_name = delivery_group["delivery_group_name"]
    
    ret = DeliveryGroup.check_delivery_group_computers(sender, delivery_group_name, computer_names)
    if isinstance(ret, Error):
        return ret
    
    update_desktops = {}
    desktops = ret
    for desktop_id, desktop in desktops.items():
        if desktop_id in existed_desktops:
            continue
        
        update_desktops[desktop_id] = desktop
    
    if update_desktops:
        ret = DeliveryGroup.set_delivery_group_desktops(sender, delivery_group_id, update_desktops)
        if isinstance(ret, Error):
            return ret

    return update_desktops.keys()

def refresh_citrix_desktop_nics(sender, desktop_ids):
        
    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        logger.error("refresh citrix desktop nics, no found desktop %s " % desktop_ids)
        return None

    new_nics = {}
    delete_nics = []
    
    desktop_network_config = {}    
    # get desktop instance
    instances = {}
    desktop_instance = ctx.pgm.get_desktop_instance(desktop_ids)
    if desktop_instance:
        instance_ids = desktop_instance.values()
        instances = ctx.res.resource_describe_instances(sender["zone"], instance_ids)
        if not instances:
            instances = {}

    # get desktop nic
    desktop_nic = ctx.pgm.get_nic_desktop(desktop_ids)
    if desktop_nic:
        delete_nics.extend(desktop_nic.keys())

    for desktop_id in desktop_ids:
        desktop = desktops[desktop_id]   
        instance_id = desktop["instance_id"]
        desktop_group_id = desktop["desktop_group_id"]
    
        # get desktop network
        network_configs = desktop_network_config.get(desktop_group_id)
        if network_configs is None:
            network_configs = ctx.pgm.get_desktop_group_network(desktop_group_id)
            if not network_configs:
                network_configs = {}
            
            desktop_network_config[desktop_group_id] = network_configs
            
        network_ids = network_configs.keys()

        instance = instances.get(instance_id, {})
        vxnets = instance.get("vxnets")
        if not instance or not vxnets:
            continue
       
        for vxnet in vxnets:
            vxnet_id = vxnet["vxnet_id"]
            nic_id = vxnet["nic_id"]
            private_ip = vxnet["private_ip"]
            if vxnet_id not in network_ids or not private_ip:
                continue
    
            nic_info = {
                "nic_id": vxnet["nic_id"],
                "instance_id": instance_id,
                "network_id": vxnet["vxnet_id"],
                "network_name": vxnet["vxnet_name"],
                "resource_id": desktop_id,
                "resource_name": instance["instance_name"],
                "ip_network": "",
                "status": const.NIC_STATUS_INUSE,
                "private_ip": vxnet["private_ip"],
                "network_type": vxnet["vxnet_type"],
                "desktop_group_id": desktop["desktop_group_id"],
                "desktop_group_name": desktop["desktop_group_name"],
                "create_time": get_current_time()
                }
        
            new_nics[nic_id] = nic_info
    
    if new_nics:
        new_nic_ids = new_nics.keys()
        ret = ctx.pgm.get_nics(nic_ids=new_nic_ids)
        if ret:
            delete_nics.extend(ret.keys())
    
    if delete_nics:
        ctx.pg.base_delete(dbconst.TB_DESKTOP_NIC, {"nic_id": delete_nics})
    
    if new_nics:
        if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_NIC, new_nics):
            logger.error("insert citrix desktop nic insert db fail %s" % new_nics)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return 0

def load_desktop_group_computers(sender, desktop_group, computer_names=None):
    
    ctx = context.instance()
    
    existed_desktop = []
    desktops = desktop_group["desktops"]
    for _, desktop in desktops.items():
        hostname = desktop["hostname"]
        existed_desktop.append(hostname)
    
    desktop_ids = []
    
    desktop_group_name = desktop_group["desktop_group_name"]
    ret = ctx.res.resource_describe_computers(sender["zone"], desktop_group_name, computer_names)
    if not ret:
        return None
    
    computers = ret
    for computer_name, computer in computers.items():
        if computer_name in existed_desktop:
            continue
        
        user_name = computer["assign_user"]
        user_ids = []
        if user_name:
            user_names = user_name.split(",")
            for _name in user_names:
                user_id = ctx.pgm.get_user_id_by_user_name(user_name, zone_id=sender["zone"])
                if user_id:
                    user_ids.append(user_id)

        mode = computer["mode"]
        desktop_config = build_computer_info(desktop_group)
        status = const.CITRIX_STATUS_MAP.get(computer["power_state"], "")
        if not status:
            instances = ctx.res.resource_describe_instances(sender["zone"], computer["hosted_machine_id"])
            if not instances:
                status = const.INST_STATUS_STOP
            else:
                instance = instances.get(computer["hosted_machine_id"])
                status = instance["status"]
            
        desktop_id = get_uuid(UUID_TYPE_DESKTOP, ctx.checker)
        desktop_info = dict(desktop_id=desktop_id,
                            status = status,
                            desktop_mode = const.DESKTOP_GROUP_STATUS_MAINT if mode == 'True' else const.DESKTOP_GROUP_STATUS_NORMAL,
                            reg_state = computer["reg_state"],
                            instance_id = computer["hosted_machine_id"],
                            create_time=get_current_time(False),
                            status_time = get_current_time(False),
                            hostname = computer_name,
                            )
        desktop_info.update(desktop_config)
        if not ctx.pg.batch_insert(dbconst.TB_DESKTOP, {desktop_id: desktop_info}):
            logger.error("register citrix computer insert db fail %s" % desktop_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
        if user_ids:
            ret = ResUser.add_user_to_resource(ctx, desktop_id, user_ids)
            if isinstance(ret, Error):
                return ret
        desktop_ids.append(desktop_id)

    if desktop_ids:
        ret = refresh_citrix_desktop_nics(sender, desktop_ids)
        if isinstance(ret, Error):
            return ret

    return desktop_ids
    
def build_computer_info(desktop_group):

    computer_config = {}
    desktop_keys = ["cpu", "memory", "instance_class", "gpu", "gpu_class", "ivshmem", "desktop_dn", 
                    "desktop_group_id", "desktop_group_name", "desktop_group_type", "desktop_image_id", "image_name", "save_disk", "save_desk",
                    "zone"]
    for desktop_key in desktop_keys:
        if desktop_key not in desktop_group:
            continue
        computer_config[desktop_key] = desktop_group[desktop_key]
    
    return computer_config

def refresh_citrix_disks(sender, desktop_group_name):
    
    ctx = context.instance()
    ret = ctx.pgm.get_desktop_group_by_name(desktop_group_name, extras=[dbconst.TB_DESKTOP_GROUP_DISK, dbconst.TB_DESKTOP], zone=sender["zone"])
    if not ret:
        return None
    desktop_group = ret

    disk_configs = desktop_group["disks"]
    if not disk_configs:
        return None
    
    desktops = desktop_group["desktops"]
    if not desktops:
        return None
    
    for _, disk_config in disk_configs.items():
        ret = update_desktop_disk(desktops, disk_config)
        if isinstance(ret, Error):
            return ret

    return None

def refresh_citrix_ivshmem(sender, desktop_group_name):
    
    ctx = context.instance()
    zone_id = sender["zone"]

    ivshmem = ctx.zone_checker.get_resource_limit(zone_id, "ivshmem")
    if not ivshmem:
        return None

    ret = ctx.pgm.get_desktop_group_by_name(desktop_group_name, extras=[dbconst.TB_DESKTOP], zone=zone_id)
    if not ret:
        return None
    desktop_group = ret

    desktops = desktop_group["desktops"]
    if not desktops:
        return None
    
    desktop_ids = desktops.keys()
    
    desktop_instances = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instances:
        return None
    
    instance_ids = desktop_instances.values()
    
    instance_set = ctx.res.resource_describe_instances(zone_id, instance_ids, status=[const.INST_STATUS_STOP])
    if instance_set is None:
        return None
    
    for desktop_id, instance_id in desktop_instances.items():
        
        update_instance = {}
        instance = instance_set.get(instance_id)
        if not instance:
            continue
        
        desktop = desktops.get(desktop_id)
        if not desktop:
            continue
        
        ivshmem_enable = desktop.get("ivshmem_enable", 0)

        extra = instance.get("extra")
        if not extra:
            continue
        
        inst_ivshmem = extra.get("ivshmem", "")
        if not ivshmem_enable:
            if not inst_ivshmem:
                continue
            else:
                update_instance["ivshmem"] = "none"
        else:
            if not inst_ivshmem:
                update_instance["ivshmem"] = ivshmem
            elif inst_ivshmem != ivshmem:
                update_instance["ivshmem"] = ivshmem
    
        ret = ctx.res.resource_modify_instance_attributes(zone_id, instance_id, update_instance)
        if not ret:
            logger.error("update instance %s ivhsmem fail " % instance_id)
                
    return None

def refresh_citrix_desktops(sender, hostnames=None, desktop_group_name=None, delivery_group_name=None):
    
    ctx = context.instance()
    zone_id = sender["zone"]
    ret = ctx.res.resource_describe_computers(sender["zone"], desktop_group_name, hostnames, delivery_group_name)
    if not ret:
        return None

    computers = ret
    computer_names = computers.keys()
    
    desktops = ctx.pgm.get_desktop_by_hostnames(computer_names, zone_id=zone_id)
    if not desktops:
        logger.error("refresh citrix desktop %s, no found desktop by hostname" % (computer_names))
        return None
    
    refresh_desktop = []
    desktop_ids = []
    for hostname, computer in computers.items():
        desktop = desktops.get(hostname)
        if not desktop:
            continue

        desktop_id = desktop["desktop_id"]
        refresh_desktop.append(desktop_id)
        if desktop["transition_status"]:
            continue
        
        check_citrix_update(ctx, desktop, computer)
        desktop_ids.append(desktop_id)
    
    if refresh_desktop:
        ret = refresh_citrix_desktop_nics(sender, refresh_desktop)
        if isinstance(ret, Error):
            return ret

    return desktop_ids

def format_computers(ret_computers):
    
    computes = {}
    for computer_name, computer in ret_computers.items():
        compute_info = {}
        compute_info["hostname"] = computer["hosted_machine_name"]
        compute_info["reg_state"] = computer["reg_state"]
        compute_info["owner"] = computer["assign_user"]
        compute_info["delivery_group_name"] = computer["delivery_group_name"]
        
        computes[computer_name] = compute_info
    
    return computes

def create_citrix_disks(desktop_group_id):

    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_group_ids=desktop_group_id)
    if not desktops:
        return None
    
    desktop_ids = desktops.keys()
    
    update_desktops = []
    
    disk_config = ctx.pgm.get_disk_config(desktop_group_id=desktop_group_id)
    if not disk_config:
        return None
    
    job_disks = []
    for config_id, config in disk_config.items():
        desktop_disk = ctx.pgm.get_desktop_disk(desktop_ids, disk_config_ids=config_id)
        if not desktop_disk:
            desktop_disk = {}
        
        disk_desktop = []
        for desktop_id, desktop in desktops.items():
            
            transition_status = desktop["transition_status"]
            if transition_status:
                continue

            if desktop_id in desktop_disk:
                continue
            
            disk_desktop.append(desktop_id)
            update_desktops.append(desktop_id)
        
        if disk_desktop:
            ret = Disk.create_disks(config, disk_desktop)
            if isinstance(ret, Error):
                return ret
            
            job_disks.extend(ret)
        
    return (job_disks, update_desktops)
