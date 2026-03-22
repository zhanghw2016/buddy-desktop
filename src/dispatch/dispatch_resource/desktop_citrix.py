
import context
import constants as const
from log.logger import logger
import db.constants as dbconst
import resource_common as ResComm
from utils.id_tool import(
    UUID_TYPE_DESKTOP,
    UUID_TYPE_DESKTOP_DISK,
    get_uuid
)
from common import (
    generate_disk_name,
    is_citrix_platform
)
from api.citrix.citrix_common import check_citrix_update
import time
import dispatch_resource.desktop_disk as Disk
import dispatch_resource.desktop_nic as Nic
from utils.misc import get_current_time
from dispatch_resource.desktop_common import get_desktop_ivshmem

def refresh_task_desktop_disk(resource_id, user_ids):
    
    ctx = context.instance()
    
    if not isinstance(user_ids, list):
        user_ids = [user_ids]
    
    existed_users = ctx.pgm.get_resource_user_ids(resource_id, user_ids=user_ids)
    if not existed_users:
        existed_users = {}
    
    existed_user = existed_users.get(resource_id, [])
    
    add_user = []
    for user_id in user_ids:
        if user_id in existed_user:
            continue
        
        add_user.append(user_id)
    
    resource_type = dbconst.RESTYPE_DESKTOP
    if resource_id.startswith(dbconst.RESTYPE_DESKTOP_DISK):
        resource_type = dbconst.RESTYPE_DESKTOP_DISK

    user_names = ctx.pgm.get_user_names(add_user)
    if not user_names:
        user_names = {}

    update_info = {}
    for user_id in add_user:
        user_name = user_names.get(user_id, "")
        update_info[user_id] = {
            "resource_id": resource_id,
            "resource_type": resource_type,
            "user_id": user_id,
            "user_name": user_name,
            "is_sync": 1
            }

    if update_info:
        if not ctx.pg.batch_insert(dbconst.TB_RESOURCE_USER, update_info):
            return -1

    return add_user

def register_citrix_disks(sender, disk_configs, desktop_id):

    ctx = context.instance()
    new_disks = {}
    
    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        logger.error("register citrix disk no found desktop %s" % desktop_id)
        return -1
    desktop = desktops[desktop_id]
    instance_id = desktop["instance_id"]
    if not instance_id:
        return 0
    desktop_id = desktop["desktop_id"]
    desktop_users = ctx.pgm.get_resource_user(desktop_id)
    if not desktop_users:
        desktop_users = []

    for _, disk_config in disk_configs.items():
        
        prefix_name = disk_config["disk_name"]
        disk_name = generate_disk_name(prefix_name)
        disk_id = get_uuid(UUID_TYPE_DESKTOP_DISK, ctx.checker)
    
        disk_info = dict(disk_id=disk_id,
                         volume_id='',
                         desktop_id = desktop_id,
                         desktop_name= desktop["hostname"],
                         disk_config_id=disk_config.get("disk_config_id", ""),
                         disk_type=disk_config["disk_type"],
                         desktop_group_id=desktop["desktop_group_id"],
                         desktop_group_name=desktop["desktop_group_name"],
                         size=disk_config["size"],
                         status=const.DISK_STATUS_ALLOC,
                         need_update = 0,
                         disk_name = disk_name,
                         create_time=get_current_time(False),
                         status_time=get_current_time(False),
                         zone=desktop["zone"]
                        )
        new_disks[disk_id] = disk_info
    
    # register desktop group
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_DISK, new_disks):
        logger.error("create disk insert new db fail %s" % new_disks)
        return -1
    
    if desktop_users:
        for disk_id, _ in new_disks.items():
            
            ret = refresh_task_desktop_disk(disk_id, desktop_users)
            if ret < 0:
                return -1

    disk_ids = new_disks.keys()
    disks = ctx.pgm.get_disks(disk_ids)
    if not disks:
        logger.error("citrix desktop no found disks %s" % disk_ids)
        return -1

    ret = Disk.create_volumes(sender, disks)
    if ret < 0:
        logger.error("Desktop create volume fail %s" % disk_ids)
        return -1

    ret = Disk.attach_volumes(sender, disks, instance_id)
    if ret < 0:
        return -1
        
    return 0

def get_citrix_computer_config(desktop_group):

    computer_config = {}
    desktop_keys = ["cpu", "memory", "instance_class", "gpu", "gpu_class", "ivshmem_enable", "desktop_dn", 
                    "desktop_group_id", "desktop_group_name", "desktop_group_type", "desktop_image_id", "image_name",
                    "save_disk", "save_desk", "zone"]
    for desktop_key in desktop_keys:
        if desktop_key not in desktop_group:
            continue
        computer_config[desktop_key] = desktop_group[desktop_key]
    return computer_config

def update_new_computer(sender, desktop):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    instance_name = desktop["hostname"]
    ret = ctx.res.resource_describe_computers(sender["zone"], machine_names=instance_name)
    if not ret:
        logger.error("describe computer fail %s, %s" % (instance_name, ret))
        return -1

    computer = ret[instance_name]
    instance_id = computer["hosted_machine_id"]
    mode = computer["mode"]
    update_info = {
                "instance_id": instance_id,
                "status": const.INST_STATUS_RUN,
                "desktop_mode": const.DESKTOP_GROUP_STATUS_MAINT if mode == 'True' else const.DESKTOP_GROUP_STATUS_NORMAL,
                "status_time": get_current_time(),
                "reg_state": computer["reg_state"],
                }
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: update_info}):
        logger.error("update desktop mode %s to desktop fail %s" % (desktop_id, update_info))
        return -1
    
    ret = Nic.refresh_desktop_nics(sender, desktop_id)
    if ret < 0:
        logger.error("refresh citrix desktop %s nic fail" % desktop_id)
        return -1

    return 0

def register_citrix_computer(desktop_group, instance_name):

    ctx = context.instance()

    ret = ctx.pgm.get_desktop_by_hostnames(instance_name)
    if ret:
        logger.error("instance name found in desktop %s" % instance_name)
        return -1

    ret = get_citrix_computer_config(desktop_group)
    if not ret:
        logger.error("get citrix compute config %s fail" % instance_name)
        return -1

    desktop_config = ret
    desktop_id = get_uuid(UUID_TYPE_DESKTOP, ctx.checker)
    desktop_info = dict(desktop_id=desktop_id,
                        status=const.INST_STATUS_PEND,
                        create_time=get_current_time(False),
                        status_time = get_current_time(False),
                        hostname = instance_name,
                        )
    desktop_info.update(desktop_config)
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP, {desktop_id: desktop_info}):
        logger.error("register citrix computer insert db fail %s" % desktop_info)
        return -1

    return desktop_id

def task_wait_citrix_desktop_done(sender, desktop_id, job_id):
    
    ctx = context.instance()
    with ResComm.transition_status(dbconst.TB_DESKTOP, desktop_id, const.SNAPSHOT_TRAN_STATUS_CREATING):
        ret = ctx.res.resource_wait_job_done(sender["zone"], job_id, const.PLATFORM_TYPE_CITRIX)
        if not ret:
            logger.error("resource wait job done fail %s, %s" % (desktop_id, job_id)) 
            return -1
    
        return 0

def get_citrix_desktop_group(desktop_group_id):
    
    ctx = context.instance()
    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
    if not desktop_group:
        return None

    return desktop_group

def get_citrix_image(sender, desktop_image_id):

    ctx = context.instance()
    ret = ctx.pgm.get_desktop_images(desktop_image_id)
    if not ret:
        logger.error("citrix no found desktop image %s" % desktop_image_id)
        return -1

    desktop_image = ret[desktop_image_id]
    image_id = desktop_image["image_id"]
    ret = ctx.res.resource_describe_images(sender["zone"], image_id)
    if not ret:
        logger.error("resource image no found %s" % image_id) 
        return -1

    images = ret
    image = images.get(image_id)
    if not image:
        logger.error("resource image no found %s" % image_id)
        return -1

    if image["status"] != const.IMG_STATUS_AVL:
        logger.error("image %s status dismatch %s" % (image_id, image["status"]))
        return -1
    
    return desktop_image

def get_citrix_network(sender, desktop_group):

    ctx = context.instance()
    desktop_group_id = desktop_group["desktop_group_id"]
    network_configs= ctx.pgm.get_desktop_group_network(desktop_group_id)
    if not network_configs:
        logger.error("no config citrix group network %s" % desktop_group["desktop_group_id"])
        return None
    
    network_ids = network_configs.keys()
    ret = ctx.res.resource_describe_networks(sender["zone"], network_ids)
    if not ret:
        logger.error("no found network resource %s" % network_ids)
        return None
    res_networks = ret
    
    for network_id in network_ids:
        if network_id not in res_networks:
            logger.error("no found network resource %s " % network_id)
            return None
        
        res_network = res_networks[network_id]
        if "router" not in res_network:
            logger.error("router no found network resource %s " % network_id)
            return None
    
    networks = {}
    base_networks = ctx.pgm.get_networks(network_ids, const.NETWORK_TYPE_BASE)
    if base_networks:
        networks["base_networks"] = base_networks.keys()
    
    managed_networks = ctx.pgm.get_networks(network_ids, const.NETWORK_TYPE_MANAGED)
    if managed_networks:
        networks["pri_networks"] = managed_networks.keys()
    
    return networks

def citrix_build_catalog_config(sender, desktop_group):
    
    catalog = {}
    desktop_group_name = desktop_group["desktop_group_name"]

    provision_type = desktop_group.get("provision_type")
    if not provision_type:
        provision_type = const.PROVISION_TYPE_MCS
        
    catalog["provision_type"] = provision_type
    
    if provision_type == const.PROVISION_TYPE_MCS:

        ret = get_citrix_image(sender, desktop_group["desktop_image_id"])
        if ret < 0:
            logger.error("get citrix image fail %s" % desktop_group_name)
            return -1
        desktop_image = ret
        image_id = desktop_image["image_id"]
        catalog["base_image"] = image_id
        catalog["session_type"] = desktop_image.get("session_type", "SingleSession")

        save_desk = desktop_group["save_desk"]
        catalog["persist_user_changes"] = const.CITRIX_DATA_TYPE_LOCAL if save_desk==const.DESKTOP_RULE_SAVE else const.CITRIX_DATA_TYPE_DISCARD

        networks = get_citrix_network(sender, desktop_group)
        if not networks:
            logger.error("get citrix network fail %s" % desktop_group_name)
            return -1
    
        catalog.update(networks)
    else:
        catalog["session_type"] = const.OS_SESSION_TYPE_MULTI
        catalog["persist_user_changes"] = const.CITRIX_DATA_TYPE_LOCAL

    catalog["allocation_type"] = desktop_group["allocation_type"]
    catalog["catalog_name"] = desktop_group["desktop_group_name"]
    catalog["hosting_unit"] = desktop_group["managed_resource"]
    
    
    catalog["desktop_dn"] = desktop_group["desktop_dn"]
    catalog["cpu"] = desktop_group["cpu"]
    catalog["memory"] = desktop_group["memory"]/1024
    catalog["instance_class"] = desktop_group["instance_class"]
    ivshmem_enable = desktop_group.get("ivshmem_enable")
    ivshmem = get_desktop_ivshmem(sender["zone"])
    if ivshmem_enable and ivshmem:
        catalog["ivshmem"] = ivshmem

    catalog["description"] = desktop_group["description"]
    catalog["name_regular_pre"] = desktop_group["naming_rule"]
    catalog["gpu"] = desktop_group["gpu"]
    catalog["gpu_class"] = desktop_group["gpu_class"]

    return catalog

def task_create_citrix_desktop_group(sender, desktop_group):
    
    ctx = context.instance()
    desktop_group_name = desktop_group["desktop_group_name"]
    desktop_group_id = desktop_group["desktop_group_id"]
    ret = ctx.res.resource_describe_computer_catalogs(sender["zone"], desktop_group_name)
    if ret:
        logger.error("computer catalog %s already existed in ddc" % desktop_group_name)
        return -1

    ret = citrix_build_catalog_config(sender, desktop_group)
    if ret < 0:
        logger.error("build citrix catalog config fail %s" % desktop_group_name)
        return -1
    catalog_config = ret

    ret = ctx.res.resource_create_computer_catalog(sender["zone"], catalog_config)
    if not ret:
        logger.error("create resource computer catalog fail %s" % desktop_group_name)
        return -1
    
    ret = ctx.res.resource_describe_computer_catalogs(sender["zone"], desktop_group_name)
    if not ret:
        logger.error("describe resource computer catalog fail %s, %s" % (desktop_group_name, ret))
        return -1
    
    catalog = ret.get(desktop_group_name)
    if not catalog:
        logger.error("describe compute catalog fail %s, %s" % (desktop_group_name, ret))
        return -1

    uuid = catalog["uuid"]
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_GROUP, {desktop_group_id: {"citrix_uuid": uuid}}):
        logger.error("update desktop group name %s to desktop fail %s" % (desktop_group_name, uuid))
        return -1

    return 0

def create_citrix_desktop_group(sender, desktop_group_id):

    with ResComm.transition_status(dbconst.TB_DESKTOP_GROUP, desktop_group_id, const.STATUS_CREATING):
        
        ret = get_citrix_desktop_group(desktop_group_id)
        if not ret:
            logger.error("create desktop group get citrix fail %s" % (desktop_group_id))
            return -1
        desktop_group = ret

        ret = task_create_citrix_desktop_group(sender, desktop_group)
        if ret < 0:
            logger.error("task create citrix desktop group fail %s" % (desktop_group_id))
            return -1

        return 0

def task_delete_citrix_desktop_group(sender, desktop_group):

    ctx = context.instance()

    desktop_group_name = desktop_group["desktop_group_name"]
    ret = ctx.res.resource_describe_computer_catalogs(sender["zone"], desktop_group_name)
    if ret is None:
        logger.error("describe computer catalog fail %s" % desktop_group_name)
        return -1

    if not ret:
        return 0

    ret = ctx.res.resource_delete_computer_catalog(sender["zone"], desktop_group_name)
    if not ret:
        logger.error("delete computer catalog fail %s" % desktop_group_name)
        return -1

    return 0
        
def update_citrix_desktop_group_image(sender, desktop_group_id, desktop_image_id):
    
    ctx = context.instance()
    with ResComm.transition_status(dbconst.TB_DESKTOP_GROUP, desktop_group_id, const.STATUS_UPDATING):
        
        desktop_images = ctx.pgm.get_desktop_images(desktop_image_id)
        if not desktop_images:
            logger.error("no found desktop image %s" % desktop_image_id)
            return -1

        desktop_image = desktop_images[desktop_image_id]
        ret = task_update_citrix_desktop_group_image(sender, desktop_group_id, desktop_image)
        if ret < 0:
            logger.error("desktop group update image fail %s" % ( desktop_group_id))
            return -1
        
        ret = update_desktop_group_image(desktop_group_id, desktop_image)
        if ret < 0:
            logger.error("update desktop group image fail %s" % desktop_group_id)
            return -1

    return 0

def update_desktop_group_image(desktop_group_id, desktop_image):
    
    ctx = context.instance()
    update_info = {}
    update_info["desktop_image_id"] = desktop_image["desktop_image_id"]
    update_info["image_name"] = desktop_image["image_name"]

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_GROUP, {desktop_group_id: update_info}):
        logger.error("update desktop group image %s fail" % update_info)
        return -1
    
    return 0

def task_update_citrix_desktop_group_image(sender, desktop_group_id, desktop_image):
    
    ctx = context.instance()
    ret = get_citrix_desktop_group(desktop_group_id)
    if not ret:
        logger.error("create desktop group get citrix fail %s" % (desktop_group_id))
        return -1
    desktop_group = ret
   
    catalog_name = desktop_group["desktop_group_name"]
    hosting_unit = desktop_group["managed_resource"]
    
    ret = ctx.res.resource_describe_computer_catalogs(sender["zone"], catalog_name)
    if not ret:
        logger.error("computer catalog %s no found" % catalog_name)
        return -1

    ret = ctx.res.resource_update_catalog_master_image(sender["zone"], catalog_name, hosting_unit, desktop_image["image_id"])
    if not ret:
        logger.error("update resource computer catalog image fail %s" % catalog_name)
        return -1
    
    return 0

def check_citrix_desktop(desktop_ids):
    
    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        return 0
    
    for desktop_id, desktop in desktops.items():
        instance_id = desktop["instance_id"]
        if instance_id:
            continue
        
        desktop_group_id = desktop["desktop_group_id"]
        ctx.pg.delete(dbconst.TB_DESKTOP, desktop_id)
        
        desktop_users = ctx.pgm.get_resource_user(desktop_id)
        if not desktop_users:
            continue

        conditions = dict(desktop_group_id=desktop_group_id, 
                          user_id=desktop_users)
        ctx.pg.base_delete(dbconst.TB_DESKTOP_GROUP_USER, conditions)
    return 0

def citrix_desktop_login(desktop):
    
    ctx = context.instance()
    if not is_citrix_platform(ctx, desktop["zone"]):
        logger.error("no citrix platform, cant wait desktop login")
        return -1
    
    desktop_id = desktop["desktop_id"]
    ret = ResComm.send_internel_req(const.INTERNEL_ACTION_WAIT_CITRIX_LOGIN, desktop_id)
    
    return ret

def update_desktop_reg_state(desktop_id):
    
    ctx = context.instance()
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: {"reg_state": 1}}):
        logger.error("update desktop reg state %s fail" % desktop_id)
        return -1

    return 0

def wait_citrix_desktop_login(desktop, timeout=const.CITRIX_WAIT_LOGIN_TIMEOUT, interval=const.CITRIX_WAIT_LOGIN_INTERVAL):
    
    ctx = context.instance()
    hostname = desktop["hostname"]
    desktop_id = desktop["desktop_id"]
    end_time = time.time() + timeout

    while time.time() < end_time:
        
        ret = ctx.res.resource_describe_computers(desktop["zone"], machine_names=hostname)
        if not ret:
            logger.error("wait citrix desktop login %s fail " % hostname)
            return -1
        
        computer = ret.get(hostname)
        if not computer:
            logger.error("wait login no found compute %s" % hostname)
            return -1

        if int(computer["reg_state"]) == 1:
            ret = update_desktop_reg_state(desktop_id)
            if ret < 0:
                logger.error("update desktop assign status fail %s" % computer["reg_state"])
                return -1

            return 0

        time.sleep(interval)

    return 0

def refresh_image_nics(sender, desktop_image_id):
    
    ctx = context.instance()
    
    desktop_images = ctx.pgm.get_desktop_images(desktop_image_id)
    if not desktop_images:
        return 0
    
    desktop_image = desktop_images[desktop_image_id]   
    instance_id = desktop_image["instance_id"]

    new_nics = {}
        
    # get desktop instance
    instances = ctx.res.resource_describe_instances(sender["zone"], instance_id)
    if not instances:
        instances = {}

    instance = instances.get(instance_id, {})
    vxnets = instance.get("vxnets")
    if not instance or not vxnets:
        return 0
   
    for vxnet in vxnets:
        vxnet_id = vxnet["vxnet_id"]
        nic_id = vxnet["nic_id"]
        private_ip = vxnet["private_ip"]
        if vxnet_id != desktop_image["network_id"] or not private_ip:
            continue

        nic_info = {
            "nic_id": vxnet["nic_id"],
            "instance_id": instance_id,
            "network_id": vxnet["vxnet_id"],
            "network_name": vxnet["vxnet_name"],
            "resource_id": desktop_image_id,
            "resource_name": instance["instance_name"],
            "ip_network": "",
            "status": const.NIC_STATUS_INUSE,
            "private_ip": vxnet["private_ip"],
            "network_type": vxnet["vxnet_type"],
            "create_time": get_current_time()
            }
    
        new_nics[nic_id] = nic_info
    if new_nics:
        if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_NIC, new_nics):
            logger.error("insert citrix desktop nic insert db fail %s" % new_nics)
            return -1
    
    return 0

def update_citrix_image(sender, desktop_id):
    
    ctx = context.instance()

    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        return -1
    
    desktop = desktops[desktop_id]
    instance_id = desktop["instance_id"]
    if not instance_id:
        return 0
    
    desktop_group_id = desktop["desktop_group_id"]
    
    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id, extras=[])
    if not desktop_group:
        return 0
    
    if desktop_group["desktop_image_id"] == desktop["desktop_image_id"]:
        return 0
    
    ret = ctx.res.resource_describe_instances(sender["zone"], instance_id)
    if not ret:
        return 0
    
    instance = ret[instance_id]
    image = instance["image"]
    image_id = image["image_id"]
    
    desktop_image = ctx.pgm.get_base_image(image_id)
    if not desktop_image:
        return None
    
    desktop_image_id = desktop_image["desktop_image_id"]
    if desktop_image_id != desktop_group["desktop_image_id"]:
        return None
    
    update_image = {
        "desktop_image_id": desktop_image_id,
        "image_name": desktop_image["image_name"]
        }

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: update_image}):
        logger.error("update desktop mode %s to desktop fail %s" % (desktop_id, update_image))
        return -1
    
    return 0

def sync_citrix_desktop_info(sender, desktop_id):

    ctx = context.instance()
    if ctx.pass_citrix_pm:
        return 0
    
    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        logger.error("sync citrix desktop no found desktop %s" % desktop_id)
        return -1

    desktop = desktops[desktop_id]
    instance_name = desktop["hostname"]
    ret = ctx.res.resource_describe_computers(sender["zone"], machine_names=instance_name)
    if not ret:
        logger.error("describe computer fail %s, %s" % (instance_name, ret))
        return -1

    computer = ret[instance_name]

    check_citrix_update(ctx, desktop, computer)

    #update image
    update_citrix_image(sender, desktop_id)
    # update nic
    Nic.refresh_desktop_nics(sender, desktop_id)

    return 0

    
