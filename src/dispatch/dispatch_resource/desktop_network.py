
import context
import constants as const
from log.logger import logger
import db.constants as dbconst
from utils.misc import get_current_time

def clear_pend_network(network_id):
    
    ctx = context.instance()
    networks = ctx.pgm.get_networks(network_id)
    if not networks:
        return 0

    network = networks[network_id]
    
    status = network["status"]
    if status == const.NETWORK_STATUS_PEND:
        ctx.pg.delete(dbconst.TB_DESKTOP_NETWORK, network_id)
    
    return 0

# create network

def check_network_join_router(sender, network_id):

    ctx = context.instance()
    networks = ctx.pgm.get_networks(network_id)
    if not networks:
        logger.error("check network join router no found network %s" % network_id)
        return None
    network = networks[network_id]
    
    ret = ctx.res.resource_describe_networks(sender["zone"], network_id, const.NETWORK_TYPE_MANAGED)
    if not ret:
        logger.error("check network join router, no found resource network %s" % network_id)
        return None

    vxnet = ret[network_id]
    router = vxnet.get("router")
    if router:
        logger.error("check network join router, network already join vxnet %s, %s" % (network_id, router))
        return None

    return network

def network_join_router(sender, network):

    ctx = context.instance()
    
    network_id = network["network_id"]
    ip_network = network["ip_network"]
    router_id = network["router_id"]
    
    if not network_id or not ip_network or not router_id:
        logger.error("network join router no resource %s, %s, %s" % (network_id, router_id, ip_network))
        return -1

    ret = ctx.res.resource_join_router(sender["zone"], network_id, router_id, ip_network)
    if not ret:
        logger.error("resource network join router fail. network [%s], router [%s], ip network [%s]" % (network_id, router_id, ip_network))
        return -1

    ret = ctx.res.resource_describe_networks(sender["zone"], network_id, const.NETWORK_TYPE_MANAGED)
    if not ret:
        logger.error("network join router, describe network fail %s" % network_id)
        return -1

    vxnet = ret[network_id]
    router = vxnet.get("router")
    if not router:
        logger.error("network join router, network %s no found router" % network_id)
        return -1

    update_network = {
                     "status": const.NETWORK_STATUS_AVAIL,
                     "status_time": get_current_time()
                     }

    if not network["dyn_ip_start"]:
        network["dyn_ip_start"] = router["dyn_ip_start"]
        update_network["dyn_ip_start"] = router["dyn_ip_start"]
    
    if not network["dyn_ip_end"]:
        network["dyn_ip_end"] = router["dyn_ip_end"]
        update_network["dyn_ip_end"] = router["dyn_ip_end"]
    
    if not network["manager_ip"]:
        network["manager_ip"] = router["manager_ip"]
        update_network["manager_ip"] = router["manager_ip"]

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_NETWORK, {network_id: update_network}):
        logger.error("update new network fail %s" % update_network)
        return -1

    return 0

# delete networks
def check_delete_network(sender, network_ids):
    
    ctx = context.instance()
    networks = ctx.pgm.get_networks(network_ids, const.NETWORK_TYPE_MANAGED)
    if not networks:
        logger.error("check delete network, get network fail %s " % network_ids)
        return -1

    res_networks = ctx.res.resource_describe_networks(sender["zone"], network_ids)
    if not res_networks:
        res_networks = {}
    
    task_network = {}
    delete_network = []
    for network_id in network_ids:
        network = networks.get(network_id)
        if not network:
            logger.error("check delete network, no found network %s " % network_id)
            return -1

        res_network = res_networks.get(network_id)
        if not res_network:
            delete_network.append(network_id)
            continue

        res_nics = ctx.res.resource_describe_nics(sender["zone"], network_id=network_id, is_owner=False)
        if res_nics:
            logger.error("check delete network %s, has resource nic %s " % (network_id, res_nics.keys()))
            return -1

        task_network[network_id] = network

    for network_id in delete_network:
        ctx.pg.delete(dbconst.TB_DESKTOP_NETWORK, network_id)

    return task_network

def delete_managed_network(sender, network):
    
    ctx = context.instance()

    vxnet_id = network["network_id"]
    router_id = network["router_id"]
    ret = ctx.res.resource_leave_router(sender["zone"], router_id, vxnet_id)
    if not ret:
        logger.error("delete network, leave router fail %s %s " % (router_id, vxnet_id))
        return -1

    ret = ctx.res.resource_delete_vxnets(sender["zone"], vxnet_id)
    if not ret:
        logger.error("delete network, delete vxnet fail %s " % (vxnet_id))
        return -1

    return 0

    