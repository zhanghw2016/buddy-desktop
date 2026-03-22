
import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    TB_DESKTOP_NETWORK,
)
from common import (
    build_filter_conditions,
    check_global_admin_console,
    check_admin_console,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success
)
import constants as const
import db.constants as dbconst
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.permission as Permission
import resource_control.desktop.resource_permission as ResCheck
import resource_control.desktop.network as Network
import resource_control.zone.resource_limit as ResLimit
from utils.misc import get_columns

def handle_describe_desktop_networks(req):

    ctx = context.instance()
    sender = req["sender"]

    # get desktop group volume set
    filter_conditions = build_filter_conditions(req, TB_DESKTOP_NETWORK)

    network_ids = req.get("networks")
    if network_ids:
        filter_conditions["network_id"] = network_ids

    network_type = ResLimit.get_resource_limit_network_type(sender["zone"])
    if network_type:
        filter_conditions["network_type"] = network_type
        if network_type == const.NETWORK_TYPE_BASE:
            if "zone" in filter_conditions:
                del filter_conditions["zone"]
            ret = ctx.res.resource_describe_networks(sender["zone"], network_ids=network_ids, network_type=const.NETWORK_TYPE_BASE)
            if not ret:
                rep = {'total_count': 0} 
                return return_items(req, None, "desktop_network", **rep)
            filter_conditions["network_id"] = ret.keys()
    else:
        rep = {'total_count': 0} 
        return return_items(req, None, "desktop_network", **rep)

    # global admin user can see all resources
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_NETWORK]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_NETWORK]
    else:
        display_columns = {}

    network_set = ctx.pg.get_by_filter(TB_DESKTOP_NETWORK, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_DESKTOP_NETWORK, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if network_set is None:
        logger.error("describe desktop network failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    Network.format_desktop_network(sender, network_set)

    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_NETWORK, filter_conditions)
    if total_count is None:
        logger.error("get desktop group network count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, network_set, "desktop_network", **rep)

def handle_create_desktop_network(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["ip_network"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    ip_network = req["ip_network"]

    ret = Network.check_router_id(sender["zone"], const.NETWORK_TYPE_MANAGED, get_router=True)
    if isinstance(ret, Error):
        return ret
    router_id = ret
    ret = Network.check_managed_network_existed(router_id, ip_network)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Network.check_ip_network(sender,router_id,ip_network)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Network.register_managed_network(sender, router_id, ip_network, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    network_id = ret

    # submit desktop job
    ret = Network.send_network_job(sender, network_id, const.JOB_ACTION_CREATE_NETWORK)
    if isinstance(ret, Error):
        return return_error(req, ret)
    job_uuid = ret

    # register resource permission
    Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_DESKTOP_NETWORK, network_id, sender["zone"], dbconst.RES_SCOPE_DELETE)

    ret = {"network": network_id}
    return return_success(req, None, job_uuid, **ret)

def handle_modify_desktop_network_attributes(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["network"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    network_id = req["network"]

    ret = Network.check_desktop_network_vaild(sender, network_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    network = ret[network_id]

    columns = get_columns(req, ["network_name", "description"])
    if columns:

        ret = Network.modify_desktop_network_attributes(sender, network, columns)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_delete_desktop_networks(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["networks"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    network_ids = req["networks"]

    # check vxnet permission
    ret = Network.check_desktop_network_vaild(sender, network_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    networks = ret

    ret = Network.delete_desktop_networks(sender, networks)
    if isinstance(ret, Error):
        return return_error(req, ret)

    network_ids = ret
    job_uuid = None

    # submit desktop job
    if network_ids:
        ret = Network.send_network_job(sender, network_ids, const.JOB_ACTION_DELETE_NETWORKS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    # clear resource permission
    Permission.clear_user_resource_scope(resource_ids=network_ids)

    return return_success(req, None, job_uuid)

def handle_describe_system_networks(req):
    
    sender = req["sender"]
    ctx = context.instance()
    zone_id = sender["zone"]

    if not check_global_admin_console(sender):
        rep = {'total_count': 0} 
        return return_items(req, None, "system_network", **rep)
    
    ret = Network.check_zone_network(zone_id)
    if isinstance(ret, Error):
        rep = {'total_count': 0} 
        return return_items(req, None, "system_network", **rep)
    network_info = ret
    network_type = network_info["network_type"]

    excluded_networks = []
    networks = ctx.pgm.get_networks(network_type=network_type)
    if networks:
        excluded_networks = networks.keys()
    
    vxnets = {}
    if network_type == const.NETWORK_TYPE_MANAGED:
        ret = Network.get_resource_managed_network(zone_id, network_info)
        if isinstance(ret, Error):
            return return_error(req, ret)
        vxnets = ret

    else:
        ret = ctx.res.resource_describe_networks(sender["zone"], None, const.NETWORK_TYPE_BASE)
        if ret:
            vxnets = ret
    
    system_networks = Network.format_system_networks(vxnets, excluded_networks)

    rep = {'total_count': len(system_networks)} 
    return return_items(req, system_networks, "system_network", **rep)

def handle_load_system_network(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["network"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    network_id = req["network"]

    if not check_global_admin_console(sender):
        logger.error("only global admin user can load system network %s" % network_id)
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_PRIVILEGE_ACCESS_DENIED))

    network_name = req.get("network_name")

    # check resource network
    ret = Network.check_load_system_network(sender, network_id, network_name)
    if isinstance(ret, Error):
        return return_error(req, ret)
    network = ret

    # register network
    ret = Network.register_system_network(sender, network)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, None)

def handle_describe_desktop_routers(req):
 
    sender = req["sender"]
    ctx = context.instance()

    desktop_routers = {}
    router_ids = req.get("routers")
    if not check_global_admin_console(sender):
        rep = {'total_count': 0}
        return return_items(req, None, "desktop_routers", **rep)

    total_count = 0
    ret = ctx.res.resource_describe_routers(sender["zone"], router_ids)
    if ret:
        total_count = len(ret)
        desktop_routers = ret

    rep = {'total_count': total_count}
    return return_items(req, desktop_routers, "desktop_routers", **rep)

