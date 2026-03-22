import constants as const
import db.constants as dbconst
from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.misc import get_current_time

def create_desktop_nic(desktop, network_id, private_ip):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]

    new_nic = ctx.res.resource_create_nics(desktop["zone"], network_id, desktop["hostname"], private_ips=private_ip)
    if not new_nic:
        logger.error("desktop alloc nic fail %s" % desktop_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_NETWORK_NO_NIC_AVAIL, (network_id))
    
    nic_id = new_nic[0]
    
    ret = ctx.res.resource_describe_nics(desktop["zone"], nic_id)
    if not ret:
        logger.error("check desktop alloc nic fail %s" % desktop_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_NETWORK_NO_NIC_AVAIL, (network_id))
    
    nic = ret[nic_id]
    nic_info = {
        "nic_id": nic_id,
        "instance_id": '',
        "network_id": nic["vxnet_id"],
        "network_name": nic["nic_name"],
        "resource_id": desktop_id,
        "resource_name": desktop["hostname"],
        "ip_network": "",
        "status": const.NIC_STATUS_AVAIL,
        "private_ip": nic["private_ip"],
        "desktop_group_id": desktop["desktop_group_id"],
        "desktop_group_name": desktop["desktop_group_name"],
        "network_type": nic["vxnet_type"],
        "create_time": get_current_time()
        }
    
    new_nics = {nic_id: nic_info}

    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_NIC, new_nics):
        logger.error("insert citrix desktop nic insert db fail %s" % new_nics)
        return -1
    
    return nic_info

def check_alloc_desktop_nic(desktop, network_id, private_ip=None):
    
    ctx = context.instance()
    desktop_group_id = desktop["desktop_group_id"]

    if desktop_group_id:
        # get network auto nic
        ret = ctx.pgm.get_desktop_group_network(desktop_group_id)
        if not ret or network_id not in ret:
            logger.error("desktop group %s no network config" % desktop_group_id)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_GROUP_NO_THIS_NETWORK, (desktop_group_id, network_id))

    avail_nics = ctx.pgm.get_network_nics(network_id, desktop_group_id=desktop_group_id, private_ips=private_ip, is_free=True, status=const.NIC_STATUS_AVAIL)
    if not avail_nics:
        return None
    
    nic_ids = avail_nics.keys()
    
    ret = ctx.res.resource_describe_nics(desktop["zone"], nic_ids)
    if not ret:
        return None
    
    nic_id = ret.keys()[0]
    
    return avail_nics[nic_id]

def alloc_desktop_nics(desktop, network_id, private_ip=None):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]

    ret = check_alloc_desktop_nic(desktop, network_id, private_ip)
    if isinstance(ret, Error):
        logger.error("alloc desktop nics fail %s" % desktop_id)
        return ret
    
    update_nic = ret
    if not update_nic:        
        ret = create_desktop_nic(desktop, network_id, private_ip)
        if isinstance(ret, Error):
            return ret
        update_nic = ret
        
    network_config_id = ""
    network_id = update_nic["network_id"]
    desktop_group_id = desktop["desktop_group_id"]
    if desktop_group_id:
        ret = ctx.pgm.get_desktop_group_network(desktop_group_id, None, network_id)
        network_config = ret
        if network_config:
            network_config_id = network_config.get(network_id)
    
    desktop_group_id = desktop["desktop_group_id"]
    desktop_group_name = desktop["desktop_group_name"]
    nic_id = update_nic["nic_id"]
    
    
    update_info = {
                            "resource_id": desktop_id,
                            "resource_name": desktop["hostname"],
                            "need_update": const.DESKTOP_NIC_ATTACH,
                            "status": const.NIC_STATUS_AVAIL,
                            "status_time": get_current_time(),
                            "desktop_group_id": desktop_group_id if desktop_group_id else '',
                            "desktop_group_name": desktop_group_name if desktop_group_name else '',
                            "network_config_id": network_config_id
                          }
    update_nic.update(update_info)
    
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_NIC, {nic_id: update_info}):
        logger.error("alloc desktop nic update db fail %s" % update_nic)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return desktop_id

def check_desktop_group_free_nics(sender, desktop_group_id, network_ids):

    ctx = context.instance()
    
    # get network range nic
    avail_nics = ctx.pgm.get_desktop_group_nics(desktop_group_id, network_id=network_ids, status=[const.NIC_STATUS_AVAIL])
    if not avail_nics:
        return None
    
    avail_nics = ctx.res.resource_describe_nics(sender["zone"], nic_ids=avail_nics.keys())
    if not avail_nics:
        return None
    
    return avail_nics

def build_desktop_group_nic(sender, network_id, nic_ids, network_config_id):
   
    ctx = context.instance()
    update_nic = {}
    
    ret = ctx.pgm.get_desktop_networks(network_id)
    if not ret:
        return None
    
    network = ret[network_id]
    
    nics = ctx.res.resource_describe_nics(sender["zone"], nic_ids)
    if not nics:
        return None

    for nic_id, nic in nics.items():
        
        private_ip = nic.get("private_ip")
        if not private_ip:
            continue

        nic_info = {
                    "nic_id": nic_id,
                    "nic_name": nic.get("nic_name", ''),
                    "network_name": network["network_name"],
                    "instance_id": '',
                    "network_id": network["network_id"],
                    "ip_network": network["ip_network"],
                    "private_ip": private_ip,
                    "network_type": network["network_type"],
                    "network_config_id": network_config_id,
                    "status": const.NIC_STATUS_AVAIL,
                    "create_time": get_current_time(False),
                    "status_time": get_current_time(False)
                    }
        update_nic[nic_id] = nic_info
        
    return update_nic
    
def register_desktop_group_nic(sender, network_configs, nic_count):
    
    ctx = context.instance()   
    alloc_nics = {}
    
    for network_id, network_config_id in network_configs.items():
        
        need_nic_count = nic_count - len(alloc_nics)
        if need_nic_count <= 0:
            break
        
        available_ip_count = 0
        ret = ctx.res.resource_describe_networks(sender["zone"], network_ids=network_id)
        if ret:
            network = ret[network_id]
            available_ip_count = network.get("available_ip_count", 0)

        alloc_nic_count = available_ip_count
        if alloc_nic_count > need_nic_count:
            alloc_nic_count = need_nic_count
        
        if not available_ip_count:
            continue

        nic_ids = ctx.res.resource_create_nics(sender["zone"], network_id, network_config_id, need_nic_count)
        if not nic_ids:
            continue
        
        ret = build_desktop_group_nic(sender, network_id, nic_ids, network_config_id)
        if isinstance(ret, Error):
            return ret

        alloc_nics.update(ret)

    if alloc_nics:
        if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_NIC, alloc_nics):
            logger.error("create new nic fail %s" % alloc_nics)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return alloc_nics

def alloc_desktop_nic(desktop_ids, nic_ids, network_configs, desktop_group):
    
    ctx = context.instance()
    if not desktop_ids:
        return None
    
    if not nic_ids:
        return None
    
    desktop_group_id = desktop_group["desktop_group_id"]
    
    desktop_name = ctx.pgm.get_desktop_name(desktop_ids)
    if not desktop_name:
        desktop_name = {}

    desktop_instances = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instances:
        desktop_instances = {}

    nics = ctx.pgm.get_nics(nic_ids, is_free=True)
    if not nics:
        nics = {}
    nic_ids = nics.keys()
    
    update_nic = {}
    desktop_nic = {}

    for desktop_id in desktop_ids:
        
        if not nic_ids:
            break
        
        hostname = desktop_name.get(desktop_id, desktop_id)

        need_update = const.DESKTOP_NIC_ATTACH
        if desktop_id not in desktop_instances:
            need_update = 0
        
        nic_id = nic_ids.pop(0)

        nic = nics[nic_id]
        network_id = nic["network_id"]
        network_config_id = nic["network_config_id"]
        if not network_config_id:
            network_config_id = network_configs.get(network_id, "")
        
        desktop_nic[desktop_id] = nic_id
        update_nic[nic_id] = {
                                "resource_id": desktop_id,
                                "resource_name": hostname,
                                "desktop_group_id": desktop_group_id,
                                "desktop_group_name": desktop_group["desktop_group_name"],
                                "need_update": need_update,
                                "network_config_id": network_config_id,
                                "status": const.NIC_STATUS_AVAIL,
                                "status_time": get_current_time()
                              }

    if update_nic:
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP_NIC, update_nic):
            logger.error("alloc desktop nic update db fail %s" % update_nic)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return desktop_nic


def alloc_desktop_group_nics(sender,desktop_group, desktop_ids, network_type=None):

    ctx = context.instance()
    
    desktop_group_id = desktop_group["desktop_group_id"]

    # get network auto nic
    ret = ctx.pgm.get_desktop_group_network(desktop_group_id, network_type)
    if not ret:
        return None

    network_configs = ret
    network_ids = network_configs.keys()

    nics = check_desktop_group_free_nics(sender,desktop_group_id, network_ids)
    if not nics:
        nics = {}
    
    nic_ids = nics.keys()
    free_nic_count = len(nics)
    
    desktop_instances = ctx.pgm.get_desktop_instance(desktop_ids)
    if not desktop_instances:
        desktop_instances = {}
    need_nic_count = len(desktop_instances)

    if free_nic_count < need_nic_count:
        
        nic_count = need_nic_count - free_nic_count
        ret = register_desktop_group_nic(sender, network_configs, nic_count)
        if ret:
            nics.update(ret)
            nic_ids = nics.keys()

    desktop_nic = {}
    
    if not nic_ids:
        return None
    
    if desktop_instances:
        _desktop_ids = desktop_instances.keys()
        ret = alloc_desktop_nic(_desktop_ids, nic_ids, network_configs, desktop_group)
        if isinstance(ret, Error):
            return ret
        
        if ret:
            desktop_nic.update(ret)
    
    other_desktop_ids = []
    for desktop_id in desktop_ids:
        if desktop_id in desktop_instances:
            continue
        other_desktop_ids.append(desktop_id)
    
    ret = alloc_desktop_nic(other_desktop_ids, nic_ids, network_configs, desktop_group)
    if isinstance(ret, Error):
        return ret

    if ret:
        desktop_nic.update(ret)

    return desktop_nic

def desktop_detach_nics(desktop_ids, network_id):

    ctx = context.instance()
    
    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        desktops = {}
    
    update_desktop = []
    update_nics = []
    delete_nics = []
    delete_resource_nics = []
    for desktop_id in desktop_ids:
        
        desktop = desktops.get(desktop_id)
        if not desktop:
            continue
        
        nics = ctx.pgm.get_nic_desktop(desktop_ids, network_id=network_id)
        if not nics:
            continue
        
        nic_ids = nics.keys()
        ret = ctx.res.resource_describe_nics(desktop["zone"], nic_ids)
        if ret is None:
            continue
        
        resource_nics = ret
        
        for nic_id, _ in nics.items():
            if nic_id not in resource_nics:
                delete_nics.append(nic_id)
                continue

            resource_nic = resource_nics[nic_id]
            if resource_nic["status"] == const.NIC_STATUS_AVAIL:
                delete_resource_nics.append(nic_id)
                delete_nics.append(nic_id)
                continue
            
            update_nics.append(nic_id)

            if desktop_id not in update_desktop:
                update_desktop.append(desktop_id)
    
        if delete_resource_nics:
            ret = ctx.res.resource_delete_nics(desktop["zone"], delete_resource_nics)
            if ret is None:
                return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
            
        if delete_nics:
            ctx.pg.base_delete(dbconst.TB_DESKTOP_NIC, {"nic_id": delete_nics})
        
        if update_nics:
            update_info = {
                            "need_update": const.DESKTOP_NIC_DETACH,
                            "status_time": get_current_time()
                              }

            ctx.pg.base_update(dbconst.TB_DESKTOP_NIC, {"nic_id":update_nics}, update_info)
    
    return update_desktop

def attach_nic_to_desktop(desktop, resource_nic, network, nic=None):
    
    ctx = context.instance()
    
    desktop_id = desktop["desktop_id"]
    nic_id = resource_nic["nic_id"]
    network_id = resource_nic["vxnet_id"]
    
    if not nic:
        nic_info = {
                    "nic_id": nic_id,
                    "nic_name": resource_nic.get("nic_name", ''),
                    "network_name": network["network_name"],
                    "instance_id": desktop["instance_id"],
                    "resource_id": desktop_id,
                    "network_id": network_id,
                    "ip_network": network["ip_network"],
                    "private_ip": resource_nic["private_ip"],
                    "network_type": network["network_type"],
                    "need_update": const.DESKTOP_NIC_ATTACH,
                    "status": const.NIC_STATUS_AVAIL,
                    "create_time": get_current_time(False),
                    "status_time": get_current_time(False)
                    }
        
        if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_NIC, {nic_id: nic_info}):
            logger.error("create new nic fail %s" % nic_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    else:
        
        update_nic = {
            "status": nic["status"],
            "create_time": get_current_time(False),
            "status_time": get_current_time(False)
            }
        
        if nic["status"] == const.NIC_STATUS_AVAIL:
            update_nic["need_update"] = const.DESKTOP_NIC_ATTACH
        
        if not ctx.pg.update(dbconst.TB_DESKTOP_NIC, nic_id, update_nic):
            logger.error("release resource nic failed for [%s]" % nic_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return nic_id

def detach_nic_from_desktop(desktop, nic, resource_nic = None):
    
    ctx = context.instance()
    nic_id = nic["nic_id"]
    if not resource_nic:
        ret = ctx.res.resource_describe_nics(desktop["zone"], nic_id)
        if not ret:
            resource_nic = {}
        resource_nic = ret[nic_id]
    
    if resource_nic["status"] == const.NIC_STATUS_AVAIL:
        
        ret = ctx.res.resource_delete_nics(desktop["zone"], nic_id)
        if not ret:
            logger.error("delete nic %s failed " % nic_id)
            return None
        ctx.pg.delete(dbconst.TB_DESKTOP_NIC, nic_id)
    
    elif resource_nic["status"] == const.NIC_STATUS_INUSE:
        update_info = {
            "need_update": const.DESKTOP_NIC_DETACH
            }
        ctx.pg.update(dbconst.TB_DESKTOP_NIC, nic_id, update_info)

    return nic_id

