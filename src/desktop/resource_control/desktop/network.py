import constants as const
from log.logger import logger
import context
import db.constants as dbconst
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.net import(
    compare_ip,
    is_valid_ip,
    ip_in_network,
)
from common import is_citrix_platform
from utils.misc import get_current_time
from db.constants import TB_DESKTOP_NETWORK, TB_DESKTOP_GROUP_NETWORK, TB_DESKTOP_NIC
import resource_control.desktop.nic as Nic
import resource_control.zone.resource_limit as ResLimit

import resource_control.permission as Permission
import resource_control.desktop.job as Job
from constants import (
    REQ_TYPE_DESKTOP_JOB,
)

# common
def send_network_job(sender, network_ids, action):
    
    if not network_ids:
        return None
    
    if not isinstance(network_ids, list):
        network_ids = [network_ids]

    directive = {
                "sender": sender,
                "action": action,
                "networks": network_ids
                }
    ret = Job.submit_desktop_job(action, directive, network_ids, REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def check_ip_range(ip):
    
    ip_seq = int(ip.split('.')[-1])
    if ip_seq < 2 or ip_seq > 253:
        logger.error("illegal dhcp ip address [%s]" % (str(ip)))
        return False

    return True

def check_desktop_ip(ip_network, ip1, ip2=None):

    if not ip1:
        return False
    
    if not check_ip_range(ip1):
        return False
    
    if ip2 and not check_ip_range(ip1):
        return False
    
    if not is_valid_ip(ip1):
        return False

    if ip2 and not is_valid_ip(ip2):
        return False

    if not ip_in_network(ip1, ip_network):
        return False
    
    if ip2 and not ip_in_network(ip2, ip_network):
        return False

    if ip2 and compare_ip(ip1, ip2) > 0:
        return False
    
    if ip2:
        ip2_list = str(ip2).split('.')
        ip_seq = int(ip2_list[-1])
        if ip_seq >= 254:
            return False

    return True

def check_desktop_network_vaild(sender, network_ids):
    
    ctx = context.instance()
    
    if not isinstance(network_ids, list):
        network_ids = [network_ids]
    
    # get network
    networks = ctx.pgm.get_networks(network_ids)
    if not networks:
        networks = {}

    # check network type
    for network_id in network_ids:
        
        network = networks.get(network_id)
        if not network:
            logger.error("check vaild network, no found network %s" % network_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND, 
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, network_id)
        # check status
        status = network["status"]
        if status != const.NETWORK_STATUS_AVAIL:
            logger.error("network[%s] status[%s] invaild" % (network_id, status))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_NETWORK_STATUS_INVAILD, network_id)
        
        # check trans_status
        trans_status = network["transition_status"]
        if trans_status:
            logger.error("vxnet[%s] in trans status[%s]" % (network_id, trans_status))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_RESOURCE_IN_TRANSITION_STATUS, (network_id, trans_status))

    return networks

def check_managed_network_existed(router_id, ip_network):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_networks(ip_network=ip_network, network_type=const.NETWORK_TYPE_MANAGED, router_id=router_id)
    if ret:
        logger.error("network[%s] existed" % (ip_network))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_NETWORK_IN_USED, ip_network)

    return None

def register_managed_network(sender, router_id, ip_network, req):
    
    # check ip network
    ctx = context.instance()

    network_name = req.get("network_name", "network(%s)" % ip_network.split("/")[0])
    ret = ctx.res.resource_create_vxnets(sender["zone"], const.NETWORK_TYPE_MANAGED, network_name)
    if not ret:
        logger.error("resource create vxnet fail %s " % network_name)
        return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_CLOUD_RESOURCE_FAILED % network_name)
    network_id = ret
    network_update = {
                      "network_id":  network_id,
                      "ip_network": ip_network,
                      "network_name": network_name,
                      "network_type": const.NETWORK_TYPE_MANAGED,
                      'dyn_ip_start': '',
                      "dyn_ip_end": '',
                      "router_id": router_id,
                      "create_time":get_current_time(False),
                      "status_time":get_current_time(),
                      "status":const.NETWORK_STATUS_PEND,
                      "description": req.get("description", ''),
                      "zone" : sender["zone"]
                     }

    if not ctx.pg.batch_insert(TB_DESKTOP_NETWORK, {network_id: network_update}):
        logger.error("insert newly created desktop network for [%s] to db failed" % network_update)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    ret = Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_DESKTOP_NETWORK, network_id, zone_id=sender["zone"])
    if isinstance(ret, Error):
        return ret

    return network_id

# modify desktop network attributes

def refresh_desktop_network_name(network_id, network_name):

    ctx = context.instance()

    conditions = {"network_id": network_id}
    update_info = {"network_name": network_name}
    # update desktop group
    ctx.pg.base_update(TB_DESKTOP_GROUP_NETWORK, conditions, update_info)

    # update desktop
    ctx.pg.base_update(TB_DESKTOP_NIC, conditions, update_info)

    return None

def modify_desktop_network_attributes(sender, network, columns):

    ctx = context.instance()

    network_id = network["network_id"]
    network_name = columns.get("network_name")
    description = columns.get("description")
    network_type = network["network_type"]

    res_networks = ctx.res.resource_describe_networks(sender["zone"], network_id)
    if not res_networks:
        logger.error("modify network attribute, get resource network fail %s " % network_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, network_id)

    update_info = {}
    
    if network_name and network["network_name"] != network_name:      
        update_info["network_name"] = network_name
    
    if description is not None and network["description"] != description:
        update_info["description"] = description
    
    if not update_info:
        return None

    # update network info
    if not ctx.pg.batch_update(TB_DESKTOP_NETWORK, {network_id: update_info}):
        logger.error("Failed to update desktop network[%s] " % (network_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    if "description" in update_info or "network_name" in update_info:
        
        if network_type == const.NETWORK_TYPE_MANAGED:    
            ret = ctx.res.resource_modify_vxnet_attributes(sender["zone"], network_id, network_name, description)
            if not ret:
                logger.error("Failed to update desktop network[%s] " % (network_id))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, network_id)

    # refresh network name
    if "network_name" in update_info:
        ret = refresh_desktop_network_name(network_id, update_info["network_name"])
        if isinstance(ret, Error):
            return ret

    return None

def refresh_network_nic_resource(sender, network_id):

    ctx = context.instance()

    nics = ctx.pgm.get_network_nics(network_id, status=[const.NIC_STATUS_AVAIL])
    if not nics:
        return None

    nic_ids = nics.keys()
    resource_nics = ctx.res.resource_describe_nics(sender["zone"], nic_ids, is_owner=False)
    if resource_nics is None:
        logger.error("resource nics no found")
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    if not resource_nics:
        resource_nics = {}

    delete_nics = []
    del_resource_nics = []
    
    for nic_id in nic_ids:
        
        resource_nic = resource_nics.get(nic_id)
        
        if not resource_nic:
            delete_nics.append(nic_id)
            continue
        
        del_resource_nics.append(nic_id)

    if delete_nics:
        ctx.pg.base_delete(TB_DESKTOP_NIC, {"nic_id": delete_nics})
    
    if del_resource_nics:
        resource_nics = ctx.res.resource_describe_nics(sender["zone"], nic_ids,status=[const.NIC_STATUS_AVAIL])
        if not resource_nics:
            return None
        
        ret = ctx.res.resource_delete_nics(sender["zone"], resource_nics.keys())
        if not ret:
            return None
        ctx.pg.base_delete(TB_DESKTOP_NIC, {"nic_id": resource_nics.keys()})
        
    return None

def check_network_resource(network):
    ctx = context.instance()
    network_id = network["network_id"]
    
    ret = ctx.pgm.get_network_nics(network_id, status=const.NIC_STATUS_INUSE)
    if ret:
        logger.error("nic in used cant delete")
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_NETWORK_HAS_RESOURCE_IN_USED, (network["network_name"]))
    
    network_configs = ctx.pgm.get_network_config(network_id=network_id)
    if network_configs:
        desktop_group_names = []
        for _, network_config in network_configs.items():
            desktop_group_name = network_config["desktop_group_name"]
            desktop_group_names.append(desktop_group_name)
        
        logger.error("check network %s in use %s " % (network_id, network_configs.keys()))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_NETWORK_HAS_RESOURCE_IN_USED, (network["network_name"]))

    ret = ctx.res.resource_describe_nics(network["zone"], network_id=network_id, is_owner=False)
    if ret:
        logger.error("check network %s in use" % (network_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_NETWORK_HAS_RESOURCE_IN_USED, (network["network_name"]))
    
    return None

def delete_network_nics(network):
    
    ctx = context.instance()
    network_id = network["network_id"]
    zone_id = network["zone"]

    nics = ctx.pgm.get_network_nics(network_id)
    if not nics:
        return None

    nic_ids = nics.keys()
    resource_nics = ctx.res.resource_describe_nics(zone_id, nic_ids)
    if resource_nics is None:
        return None
    
    delete_nics = []
    delete_res_nics = []
    for nic_id, _ in nics.items():
        resource_nic = resource_nics.get(nic_id)
        if not resource_nic:
            delete_nics.append(nic_id)
            continue
        
        if resource_nic["status"] != const.NIC_STATUS_AVAIL:
            continue
        
        delete_nics.append(nic_id)
        delete_res_nics.append(nic_id)
    
    if delete_res_nics:
        ret = ctx.res.resource_describe_nics(zone_id, delete_res_nics)
        if ret is None:
            logger.error("resource nics no found")
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                            ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
        
        if ret:
            ret = ctx.res.resource_delete_nics(zone_id, ret.keys())
            logger.error("resource nics no found")
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                            ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    if delete_nics:
        ctx.pg.base_delete(TB_DESKTOP_NIC, {"nic_id": delete_nics})
    
    return None

# delete desktop network
def delete_desktop_networks(sender, networks):

    ctx = context.instance()
    network_ids = networks.keys()
    
    # check network nic in-use
    for network_id, network in networks.items():
        refresh_network_nic_resource(sender, network_id)
        
        ret = check_network_resource(network)
        if isinstance(ret, Error):
            return ret

    resource_networks = ctx.res.resource_describe_networks(sender["zone"], network_ids)
    if resource_networks is None:
        return None

    # delete network
    router_network = []
    for network_id, network in networks.items():
        
        delete_network_nics(network)
        
        network_type = network["network_type"]
        if network_type == const.NETWORK_TYPE_MANAGED:
            router_network.append(network_id)
        else:
            ctx.pg.delete(TB_DESKTOP_NETWORK, network_id)
            Permission.clear_user_resource_scope(network_id)

    return router_network

# format system network

def format_system_networks(networks, excluded_networks=[]):
    
    if not networks:
        return {}
    
    system_network = {}
    for _, network in networks.items():
        network_id = network["vxnet_id"]
        if network_id in excluded_networks:
            continue
        
        network_info = {
            "network_id": network_id,
            "network_name": network["vxnet_name"],
            "network_type": network["vxnet_type"],
            "description": network["description"],
            }

        router = network.get("router")
        if not router:
            network_info["manager_ip"] = network.get("manager_ip")
            network_info["ip_network"] = network.get("ip_network")
            network_info["dyn_ip_end"] = network.get("dyn_ip_end")
            network_info["dyn_ip_start"] = network.get("dyn_ip_start")
        else:
            network_info["manager_ip"] = router["manager_ip"]
            network_info["ip_network"] = router["ip_network"]
            network_info["dyn_ip_end"] = router["dyn_ip_end"]
            network_info["dyn_ip_start"] = router["dyn_ip_start"]
        
        if "manager_ip" not in network_info:
            continue
        
        system_network[network_id] = network_info
        
    return system_network

# load system network

def get_resource_network(sender, network_id,network_type=None):
    
    ctx = context.instance()
    ret = ctx.res.resource_describe_networks(sender["zone"], network_id,network_type)
    if not ret:
        logger.error("system network %s no found" % network_id)
        return None

    network = ret[network_id]
    router = network.get("router")
    if not router:
        logger.error("system network %s no router" % network_id)
        return None
    
    for router_key, router_value in router.items():
        if router_key in network:
            continue
        network[router_key] = router_value
        
    return network

def check_load_system_network(sender, network_id, network_name=None):

    ctx = context.instance()

    # check network existed
    ret = ctx.pgm.get_networks(network_id)
    if ret:
        logger.error("network %s already existed " % (network_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_NETWORK_ALREADY_EXISTED , network_id)
    # get system network
    ret = get_resource_network(sender, network_id)
    if not ret:
        logger.error("network %s dont existed" % network_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_BASE_NETWORK_NOT_EXISTED ,network_id)
    network = ret
    ip_network = network["ip_network"]
    network["network_id"] = network_id

    if not network_name:
        network_name = "SN(%s)" % ip_network.split("/")[0]
        network["network_name"] = network_name
    else:
        network["network_name"] = network_name

    if is_citrix_platform(ctx, sender["zone"]):
        return network
    
    return network

def register_system_network(sender, network):

    ctx = context.instance()
    network_update = {}
    
    network_id = network["network_id"]

    network_update[network_id] = dict(
                                      network_id = network_id,
                                      ip_network = network["ip_network"],
                                      network_name = network.get("network_name", ''),
                                      network_type = const.NETWORK_TYPE_BASE,
                                      dyn_ip_start = network.get("dyn_ip_start", ""),
                                      dyn_ip_end = network.get("dyn_ip_end", ''),
                                      manager_ip = network.get("manager_ip", ''),
                                      router_id = network.get("router_id", ''),
                                      create_time=get_current_time(False),
                                      status_time=get_current_time(),
                                      status=const.NETWORK_STATUS_AVAIL,
                                      zone = sender["zone"],
                                  )

    if not ctx.pg.batch_insert(TB_DESKTOP_NETWORK, network_update):
        logger.error("insert newly created desktop vxnet for [%s] to db failed" % network_update)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return network_id

def format_desktop_network(sender, network_set):
    
    ctx = context.instance()
    
    for network_id, network in network_set.items():
        
        refresh_network_nic_resource(sender, network_id)
        
        ret = ctx.pgm.get_network_nics(network_id)
        if not ret:
            ret = {}
        
        network["nics"] = ret.values()
    
    return None

def check_router_id(zone_id, network_type, get_router=False):

    ctx = context.instance()
    ret = ctx.pgm.get_zone_resource_limit(zone_id=zone_id)
    if not ret:
        logger.error("get zone  %s resource_limit fail, no found zone resource limit" % (zone_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)
    resource_limit = ret

    network_types = resource_limit["network_type"]
    router = resource_limit.get("router")

    if str(network_type) in network_types:
        if network_type == const.NETWORK_TYPE_MANAGED:
            if get_router and router:
                return router

        return True
    else:
        logger.error("check network type %s fail" % network_type)
        return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                     ErrorMsg.ERR_MSG_UNSUPPORTED_NETWORK_TYPE, network_type)

def check_ip_network(sender,router_id,ip_network):

    ctx = context.instance()
    ret = ctx.res.resource_describe_routers(sender["zone"], router_ids=router_id)
    if not ret:
        logger.error("resource %s no found" % router_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND % router_id)
    routers = ret
    for _,router in routers.items():
        vpc_network = router.get("vpc_network")
        if ip_network.split("/")[0] == vpc_network.split("/")[0]:
            logger.error("duplicate IP network %s in router [%s]" %(ip_network,router_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_NETWORK_HAS_RESOURCE_USED_IN_ROUTER, (ip_network, router_id))

    return None
        
def check_zone_network(zone_id):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_zone(zone_id, extras=[])
    if not ret:
        logger.error("no found zone %s" % (zone_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)
    zone = ret

    if zone["status"] != const.ZONE_STATUS_ACTIVE:
        logger.error("zone status not active %s" % (zone_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_ZONE_STATUS_INVAILD, zone_id)
    
    network_info = {}
    
    network_type = ResLimit.get_resource_limit_network_type(zone_id)
    if not network_type:
        network_type = const.NETWORK_TYPE_BASE
    
    network_info["network_type"] = network_type

    if network_type == const.NETWORK_TYPE_MANAGED:
        router_id = ResLimit.get_resource_limit_router(zone_id)
        if not router_id:
            logger.error("zone network need router %s" % (zone_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_ZONE_NETWORK_NEED_ROUTER, zone_id)
    
        network_info["router_id"] = router_id

    return network_info

def get_resource_managed_network(zone_id, network_info):
    
    ctx = context.instance()
    router_id = network_info.get("router_id")
    if not router_id:
        logger.error("zone network no found router %s" % (zone_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_ZONE_NETWORK_NEED_ROUTER, zone_id)

    ret = ctx.res.resource_describe_managed_networks(zone_id, router_id)
    if not ret:
        return None
    
    return ret
    