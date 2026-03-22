
import context
import constants as const
from log.logger import logger
import db.constants as dbconst
from utils.misc import get_current_time
import time

def check_desktop_resource_nic(sender, desktops):

    ctx = context.instance()
    desktop_ids = desktops.keys()
    nics = ctx.pgm.get_nic_desktop(desktop_ids)
    if not nics:
        return 0

    nic_ids = nics.keys()
    res_nics = ctx.res.resource_describe_nics(sender["zone"], nic_ids)
    if res_nics is None:
        logger.error("resource no found nics %s" % nic_ids)
        return -1
    
    if not res_nics:
        res_nics = {}

    desktop_nics = {}
    for nic_id, nic in nics.items():
        res_nic = res_nics.get(nic_id)
        if not res_nic:
            ctx.pg.delete(dbconst.TB_DESKTOP_NIC, nic_id)
            continue
        
        nic_status = nic["status"]
        if res_nic["status"] != nic_status:
            logger.error("resource nic %s status dismatch %s %s" % (nic_id, res_nic["status"], nic["status"]))
            return -1
        
        resource_id = nic["resource_id"]
        if resource_id not in desktops:
            continue
        if resource_id not in desktop_nics:
            desktop_nics[resource_id] = {nic_id: nic}
        else:
            desktop_nics[resource_id].update({nic_id: nic})
        
    for desktop_id, desk_nics in desktop_nics.items():
        desktop = desktops[desktop_id]
        desktop["nics"] = desk_nics
 
    return 0

# update desktop nic
def check_desktop_update_nic(sender, desktops):

    ctx = context.instance()
    desktop_ids = desktops.keys()
    # get attach nic
    nics = ctx.pgm.get_nic_desktop(desktop_ids, [const.DESKTOP_NIC_ATTACH, const.DESKTOP_NIC_DETACH])
    if not nics:
        logger.error("check desktop update nic, no found update nic %s" % desktop_ids)
        return 0
    
    nic_ids = nics.keys()
    # describe resource nics
    res_nics = ctx.res.resource_describe_nics(sender["zone"], nic_ids)
    if res_nics is None:
        logger.error("resource no found nics %s" % nic_ids)
        return -1
    
    if not res_nics:
        res_nics = {}
    
    clear_nic = {}
    desktop_nic = {}
    for nic_id, nic in nics.items():
        res_nic = res_nics.get(nic_id)
        if not res_nic:
            ctx.pg.delete(dbconst.TB_DESKTOP_NIC, nic_id)
            continue

        res_status = res_nic["status"]
        need_update = nic["need_update"]
        if need_update == const.DESKTOP_NIC_ATTACH:
            if res_status != const.NIC_STATUS_AVAIL:
                logger.error("resource nic %s status %s no match" % (nic_id, res_status))
                return -1
        elif need_update == const.DESKTOP_NIC_DETACH:
            if res_status != const.NIC_STATUS_INUSE:
                clear_nic[nic_id] = nic
                continue

        desktop_id = nic["resource_id"]
        if desktop_id not in desktop_nic:
            desktop_nic[desktop_id] = {}
        desktop_nic[desktop_id].update({nic_id: nic})
    
    for nic_id, _ in clear_nic.items():
        ret = clear_nic_info(nic_id)
        if ret < 0:
            return -1
    return desktop_nic

# attach nic
def attach_nics(sender, instance_id, nics):

    ctx = context.instance()
    nic_ids = nics.keys()

    ret = ctx.res.resource_describe_nics(sender["zone"], nic_ids)
    if not ret:
        logger.error("attach nic no found resource nic")
        return -1

    ret = ctx.res.resource_attach_nics(sender["zone"], instance_id, nic_ids)
    if not ret:
        logger.error("resource attach nic fail %s %s" % (instance_id, nic_ids))
        return -1

    update_info = {}
    for nic_id in nic_ids:
        nic_info = {
            "need_update": 0,
            "instance_id": instance_id,
            "status": const.NIC_STATUS_INUSE,
            "status_time": get_current_time()
            }
        update_info[nic_id] = nic_info
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_NIC, update_info):
        logger.error("attach nic update nic fail: %s" % update_info)
        return -1

    return 0           

def attach_desktop_nics(desktop, nics = None):
    
    ctx = context.instance()
    sender = {"zone": desktop["zone"]}
    desktop_id = desktop["desktop_id"]
    
    instance_id = desktop["instance_id"]
    if not instance_id:
        return 0
    
    if not nics:
        nics = ctx.pgm.get_nic_desktop(desktop_id, status=[const.NIC_STATUS_AVAIL])
        if not nics:
            return 0

    ret = attach_nics(sender, instance_id, nics)
    if ret < 0:
        logger.error("attach nic fail %s, %s" % (desktop_id, nics.keys()))
        return -1

    return 0
# detach nic 

def clear_nic_info(nic_id, is_save=False):

    ctx = context.instance()
    nic_info = {}
    if is_save:
        nic_info["status"] = const.NIC_STATUS_AVAIL
        nic_info["instance_id"] = ''
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_NIC, {nic_id: nic_info}):
            logger.error("check attach nic update nic fail: %s" % nic_info)
            return -1
    else:
        ctx.pg.delete(dbconst.TB_DESKTOP_NIC, nic_id)

    return 0

def clear_resource_nic(sender, resource_id):

    ctx = context.instance()
    
    nics = ctx.pgm.get_nic_desktop(resource_id)
    if not nics:
        return None
    
    nic_ids = nics.keys()
    resource_nics = ctx.res.resource_describe_nics(sender["zone"], nic_ids, status=const.NIC_STATUS_AVAIL)
    if not resource_nics:
        resource_nics = {}
    
    if resource_nics:
        ret = ctx.res.resource_delete_nics(sender["zone"], resource_nics.keys())
        if not ret:
            logger.error("clear resource nics fail %s" % resource_nics.keys())
            return -1

    for nic_id in nic_ids:
        ctx.pg.delete(dbconst.TB_DESKTOP_NIC, nic_id)

    return 0

def detach_nics(sender, nics, is_save=False):

    ctx = context.instance()
    nic_ids = nics.keys()

    #check nic_ids is or not exist
    resource_nics = ctx.res.resource_describe_nics(sender["zone"], nic_ids)
    if resource_nics is None:
        logger.error("detach nic, no found resource nics")
        return -1
    
    if not resource_nics:
        resource_nics = {}

    for nic_id, _ in nics.items():
        if nic_id in resource_nics:
            continue
        ctx.pg.delete(dbconst.TB_DESKTOP_NIC, nic_id)
        nic_ids.remove(nic_id)
    
    if not nic_ids:
        return 0
    
    ret = ctx.res.resource_detach_nics(sender["zone"], nic_ids)
    if not ret:
        logger.error("resource detach nic fail %s" % nic_ids)
        return -1
    
    avail_nics = ctx.res.resource_describe_nics(sender["zone"], nic_ids, status=[const.NIC_STATUS_AVAIL])
    if not avail_nics:
        avail_nics = {}

    if not is_save and avail_nics:

        ret = ctx.res.resource_delete_nics(sender["zone"], avail_nics.keys())
        if not ret:
            logger.error("delete nic fail %s" % avail_nics.keys())
            return -1
    
    for nic_id in avail_nics.keys():
        ret = clear_nic_info(nic_id, is_save)
        if ret < 0:
            logger.error("clear nic info fail %s" % nic_id)
            return -1    

    return 0

def detach_desktop_nics(desktop, is_save=False, stop_desktop=False, nics = None):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    
    sender = {"zone": desktop["zone"]}
    
    instance_id = desktop["instance_id"]
    if not instance_id:
        return 0
    
    if not nics:
        nics = ctx.pgm.get_nic_desktop(desktop_id, status=[const.NIC_STATUS_INUSE])
        if not nics:
            return 0

    status = desktop["status"]
    if status == const.INST_STATUS_RUN:
        import dispatch_resource.desktop_instance as Instance
        ret = Instance.task_stop_desktop(sender, desktop)
        if ret < 0:
            logger.error("stop desktop fail %s" % desktop_id)
            return -1

    ret = detach_nics(sender, nics, is_save)
    if ret < 0:
        logger.error("detach nic fail %s, %s " % (desktop_id, nics.keys()))
        return -1
    
    if status == const.INST_STATUS_RUN and not stop_desktop:
        from dispatch_resource.desktop_instance import task_start_desktop
        ret = task_start_desktop(sender, desktop)
        if ret < 0:
            logger.error("start desktop fail %s" % desktop_id)
            return -1
    
    return 0

def refresh_desktop_nics(sender, desktop_id):
    
    ctx = context.instance()
    
    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        return 0
    
    desktop = desktops[desktop_id]   
    instance_id = desktop["instance_id"]
    desktop_group_id = desktop["desktop_group_id"]

    new_nics = {}
    delete_nics = []
    # get desktop network
    network_configs = ctx.pgm.get_desktop_group_network(desktop_group_id)
    if not network_configs:
        network_configs = {}
    network_ids = network_configs.keys()
    
    # get desktop nic
    desktop_nic = ctx.pgm.get_nic_desktop(desktop_id)
    if desktop_nic:
        delete_nics.extend(desktop_nic.keys())

    retries = 3
    while True:

        # get desktop instance
        instances = ctx.res.resource_describe_instances(sender["zone"], instance_id)
        if not instances:
            instances = {}

        instance = instances.get(instance_id, {})
        vxnets = instance.get("vxnets")
        if vxnets:
            for vxnet in vxnets:
                vxnet_id = vxnet["vxnet_id"]
                private_ip = vxnet["private_ip"]
                logger.info("vxnet_id == %s private_ip == %s" % (vxnet_id,private_ip))
                if vxnet_id in network_ids and private_ip:
                    retries = 0
                    break
        logger.info("retries == %s" % (retries))
        if retries == 0:
            break

        retries -= 1
        time.sleep(30)
        
    # get desktop instance
    instances = ctx.res.resource_describe_instances(sender["zone"], instance_id)
    if not instances:
        instances = {}

    instance = instances.get(instance_id, {})
    vxnets = instance.get("vxnets")
    if not instance or not vxnets:
        if delete_nics:
            ctx.pg.base_delete(dbconst.TB_DESKTOP_NIC, {"nic_id": delete_nics})
        return 0
   
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
            "desktop_group_id": desktop["desktop_group_id"],
            "desktop_group_name": desktop["desktop_group_name"],
            "network_config_id": network_configs.get(vxnet["vxnet_id"], ''),
            "network_type": vxnet["vxnet_type"],
            "create_time": get_current_time()
            }
    
        new_nics[nic_id] = nic_info
    
    if delete_nics:
        ctx.pg.base_delete(dbconst.TB_DESKTOP_NIC, {"nic_id": delete_nics})
    
    if new_nics:
        if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_NIC, new_nics):
            logger.error("insert citrix desktop nic insert db fail %s" % new_nics)
            return -1
    
    return 0

def apply_desktop_nics(desktop):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]

    de_nics = ctx.pgm.get_nic_desktop(desktop_id, const.DESKTOP_NIC_DETACH)
    if de_nics:
        ret = detach_desktop_nics(desktop, nics = de_nics)
        if ret < 0:
            return ret
        
    at_nics = ctx.pgm.get_nic_desktop(desktop_id, const.DESKTOP_NIC_ATTACH)
    if at_nics:
        ret = attach_desktop_nics(desktop, nics = at_nics)
        if ret < 0:
            return ret
    
    return 0
