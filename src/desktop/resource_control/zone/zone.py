import constants as const
from log.logger import logger
import context
import db.constants as dbconst
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.misc import get_current_time,_exec_cmd
from utils.net import is_port_open
import resource_control.zone.init_zone as InitZone
import resource_control.zone.resource_limit as ResourceLimit
from common import is_citrix_platform
from utils.json import json_dump, json_load
import api.user.user as APIUser
from base_client import send_to_server
from common import set_etc_host, clear_etc_host,get_target_host_list

def check_describe_desktop_zones(sender, zone_ids=None):

    ctx = context.instance()
    user_id = sender["owner"]
    
    if not APIUser.is_global_admin_user(sender):
        ret = ctx.pgm.get_user_zone(user_id, zone_ids)

        if not ret:
            return None
        
        return ret.keys()

    return []

def format_zone_user_role(sender, zones):
    
    ctx = context.instance()
    
    for zone_id, zone in zones.items():
        zone_user = ctx.pgm.get_zone_user(zone_id, sender["owner"])
        if not zone_user:
            continue
            
        zone["user_role"] = zone_user["role"]
        
    return None

def format_zone_stats(zone_id):
    
    ctx = context.instance()

    zone_stats = {}
    desktop_count = 0
    desktop_set = ctx.pgm.get_zone_desktops(zone_id)
    if desktop_set:
        desktop_count = len(desktop_set)
        
    zone_stats["desktop_count"] = desktop_count
    
    user_count = 0
    user_set = ctx.pgm.get_zone_users(zone_id)
    if user_set:
        user_count = len(user_set)
    
    zone_stats["user_count"] = user_count

    return zone_stats

def format_desktop_zones(sender, zones):

    ctx = context.instance()

    for zone_id, zone in zones.items():

        resource_limit = ResourceLimit.format_resource_limit(zone_id)
        if not resource_limit:
            resource_limit = {}

        zone["resource_limit"] = resource_limit

        if APIUser.is_normal_console(sender):
            
            zone_auth = ctx.pgm.get_zone_auth(zone_id, True)
            if not zone_auth:
                zone_auth = {}
            
            is_sync = zone_auth.get("is_sync", 0)
            modify_password = zone_auth.get("modify_password", is_sync)
            ret = ctx.pgm.get_auth_zone(zone_id)
            if not ret:
                ret = {}
            
            ret["is_sync"] = is_sync
            ret["modify_password"] = modify_password
            
            zone["zone_auth"] = ret
            continue

        resource_limit_range = ResourceLimit.get_default_resource_limit(zone_id)
        zone["resource_limit_range"] = ResourceLimit.format_resource_limit(zone_id, resource_limit_range)
        
        zone_conn = ctx.pgm.get_zone_connection(zone_id)
        if not zone_conn:
            zone_conn = {}
        zone["zone_connection"] = zone_conn
        zone_citrix_conn = ctx.pgm.get_zone_citrix_connection(zone_id)
        if not zone_citrix_conn:
            zone_citrix_conn = {}
        else:
            zone_citrix_conn["managed_resource"] = json_load(zone_citrix_conn["managed_resource"])
            if zone_citrix_conn["storefront_uri"] :
                if zone_citrix_conn["storefront_uri"][:2]=="[{":               
                    _uri=json_load(zone_citrix_conn["storefront_uri"]) 
                else:
                    _uri=zone_citrix_conn["storefront_uri"]
                if not isinstance(_uri ,list):
                    sf_data={}
                    sf_data["sf_uri"]=zone_citrix_conn["storefront_uri"]
                    sf_data["sf_port"]=zone_citrix_conn["storefront_port"]
                    sf_list=[sf_data]
                    zone_citrix_conn["storefront_uri"]=sf_list
                else:
                    zone_citrix_conn["storefront_uri"]=json_load(zone_citrix_conn["storefront_uri"]) 

            if zone_citrix_conn["netscaler_uri"] :
                if zone_citrix_conn["netscaler_uri"][:2]=="[{":               
                    _uri=json_load(zone_citrix_conn["netscaler_uri"])               
                else:
                    _uri=zone_citrix_conn["netscaler_uri"]
                if not isinstance(_uri,list):
                    ns_data={}
                    ns_data["ns_uri"]=zone_citrix_conn["netscaler_uri"]
                    ns_data["ns_port"]=zone_citrix_conn["netscaler_port"]
                    ns_list=[ns_data]
                    zone_citrix_conn["netscaler_uri"]=ns_list
                else:
                    zone_citrix_conn["netscaler_uri"]=json_load(zone_citrix_conn["netscaler_uri"])           
                
        zone["zone_citrix_connection"] = zone_citrix_conn
            
        zone_auth = ctx.pgm.get_zone_auth(zone_id, True)
        if not zone_auth:
            zone_auth = {}

        if APIUser.is_console_admin_user(sender):
            if "admin_password" in zone_auth:
                del zone_auth["admin_password"]

        zone["zone_auth"] = zone_auth
        zone["stats"] = format_zone_stats(zone_id)

    return zones


def format_normal_user_desktop_zones(sender, zones):

    ctx = context.instance()

    for zone_id, zone in zones.items():

        zone_auth = ctx.pgm.get_zone_auth(zone_id, True)
        if not zone_auth:
            zone_auth = {}

        is_sync = zone_auth.get("is_sync", 0)
        modify_password = zone_auth.get("modify_password", is_sync)
        ret = ctx.pgm.get_auth_zone(zone_id)
        if not ret:
            ret = {}

        ret["is_sync"] = is_sync
        ret["modify_password"] = modify_password

        zone["zone_auth"] = ret

    return zones

def check_create_desktop_zone_name(zone_name):

    ctx = context.instance()
    ret = ctx.pgm.get_zone_name()
    if not ret:
        return zone_name

    if zone_name.upper() in ret:
        logger.error("zone_name %s already existed" % zone_name)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_ZONE_NAME_ALREADY_EXISTED, zone_name)
    return zone_name

def check_create_desktop_zone(zone_id):

    ctx = context.instance()
    ret = ctx.pgm.get_zone(zone_id)
    if ret:
        logger.error("zone %s already existed" % (zone_id))
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_ZONE_ALREADY_EXISTED, zone_id)
    return ret

def check_desktop_zone_vaild(zone_id):
    
    ctx = context.instance()
    ret = ctx.pgm.get_zone(zone_id)
    if not ret:
        logger.error("zone %s no found" % (zone_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)
    return ret

def check_delete_desktop_zone(zone_ids):
    
    ctx = context.instance()
    ret = ctx.pgm.get_zones(zone_ids, status=False)
    if not ret:
        logger.error("zone %s no found" % (zone_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_ids)

    ret = check_zone_resources(zone_ids)
    if ret:
        logger.error("zone %s has resource, cant delete" % ret)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_ZONE_HAS_RESOURCE_CANT_DELETE, ret.keys())

    return ret

def create_desktop_zone(zone_id, req):

    ctx = context.instance()
    platform = req.get("platform", const.PLATFORM_TYPE_QINGCLOUD)
    zone_deploy = ctx.zone_deploy
    zone_info = dict(
                      zone_id = zone_id,
                      zone_name = req["zone_name"] if req.get("zone_name") else zone_id,
                      platform = platform,
                      zone_deploy = zone_deploy if zone_deploy else const.DEPLOY_TYPE_STANDARD,
                      status = const.ZONE_STATUS_INVAILD,
                      create_time = get_current_time(),
                      status_time = get_current_time(),
                      description = req.get("description", "")
                      )

    # register zone 
    if not ctx.pg.insert(dbconst.TB_DESKTOP_ZONE, zone_info):
        logger.error("insert newly created zone for [%s] to db failed" % (zone_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    ret = InitZone.init_desktop_zone(zone_id)
    if isinstance(ret, Error):
        delete_desktop_zones(zone_id)
        return ret
    
    ctx.zone_builder.load_zone(zone_id)

    zone_sync_to_other_server(zone_id)

    return zone_id

def modify_desktop_zone_attributes(zone_id, need_maint_columns):

    ctx = context.instance()
    zone_name = need_maint_columns.get("zone_name","")
    if zone_name:
        ret = ctx.pgm.get_zones(zone_name=zone_name)
        if ret:
            zones = ret
            for new_zone_id,_ in zones.items():
                if new_zone_id != zone_id:
                    logger.error("zone_name %s exist" % zone_name)
                    return Error(ErrorCodes.PERMISSION_DENIED,
                                 ErrorMsg.ERR_MSG_ZONE_NAME_ALREADY_EXISTED, zone_name)

    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_ZONE, {zone_id: need_maint_columns}):
        logger.error("modify desktop zone update f DB fail %s" % zone_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def detach_auth_service_form_zone(zone_id):
    
    ctx = context.instance()
    zone_auth = ctx.pgm.get_zone_auth(zone_id)
    if not zone_auth:
        return None
    
    auth_service_id = zone_auth["auth_service_id"]
    from resource_control.auth.auth_service import remove_auth_service_from_zones
    ret = remove_auth_service_from_zones(auth_service_id, zone_id)
    if isinstance(ret, Error):
        return ret
    
    return None
    
def delete_desktop_zones(zone_ids):
    
    ctx = context.instance()
    
    if not isinstance(zone_ids, list):
        zone_ids = [zone_ids]
    
    for zone_id in zone_ids:
        
        zone = ctx.pgm.get_zone(zone_id, ignore_zone=True)
        if not zone:
            continue
        
        auth_zone = zone.get("auth_zone")
        if auth_zone:
            ret = detach_auth_service_form_zone(zone_id)
            if isinstance(ret, Error):
                return ret
        
        connection = zone.get("connection")
        if connection:
            ctx.pg.delete(dbconst.TB_ZONE_CONNECTION, zone_id)

        citrix_connection = zone.get("citrix_connection")
        if citrix_connection:
            ctx.pg.delete(dbconst.TB_ZONE_CITRIX_CONNECTION, zone_id)

        resource_limit = zone.get("resource_limit")
        if resource_limit:
            ctx.pg.delete(dbconst.TB_ZONE_RESOURCE_LIMIT, zone_id)
        
        zone_id = zone.get("zone_id")
        if zone_id:
            ctx.pg.delete(dbconst.TB_DESKTOP_ZONE, zone_id)

            # delete desktop_image default system image
            ret = ctx.pgm.get_default_image(zone_id)
            if ret:
                default_images = ret
                default_image_ids = {}
                for desktop_image_id, image in default_images.items():
                    image_id = image["image_id"]
                    default_image_ids[desktop_image_id] = image_id

                for desktop_image_id in default_image_ids:
                    ctx.pg.delete(dbconst.TB_DESKTOP_IMAGE, desktop_image_id)

    ctx.zone_builder.load_zone(zone_ids)

    zone_sync_to_other_server(zone_ids)

    return None

def check_modify_desktop_zone_resource_limit(req):
    
    modify_keys = ["instance_class", "disk_size", "cpu_cores", "memory_size", "cpu_memory_pairs", "place_group", "network_type",
                   "supported_gpu", "max_disk_count", "default_passwd", "ivshmem","max_snapshot_count","router","gpu_class_key","max_gpu_count"]
    dump_keys = ["instance_class","disk_size", "cpu_cores", "memory_size", "cpu_memory_pairs", "place_group"]
    
    need_maint_columns = {}
    for modify_key in modify_keys:
        if modify_key not in req:
            continue
        
        value = req[modify_key]
        if modify_key in dump_keys:
            value = json_dump(value)
        
        need_maint_columns[modify_key] = value
    
    return need_maint_columns

def update_gpu_class_key(zone_id, gpu_class_key):
    
    ctx = context.instance()
    
    conditions = {}
    conditions["zone_id"] = zone_id

    ctx.pg.base_delete(dbconst.TB_GPU_CLASS_TYPE, conditions)
    
    update_infos = {}
    for gpu_key in gpu_class_key:
        _list = gpu_key.split("|")
        if len(_list) < 2:
            continue 
        gpu_key = _list[0]
        gpu_class = _list[1]
        
        update_infos[gpu_key] = {
            "gpu_class_key": gpu_key,
            "gpu_class": int(gpu_class),
            "zone_id": zone_id
            }

    if not ctx.pg.batch_insert(dbconst.TB_GPU_CLASS_TYPE, update_infos):
        logger.error("modify desktop zone update f DB fail %s" % zone_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def update_network_type(zone_id, network_type):
    
    ctx = context.instance()
    ret = ctx.pgm.get_zone_resource_limit(zone_id)
    if not ret:
        return None
    
    _type = ret.get("network_type")
    if _type:
        ret = ctx.pgm.get_desktop_networks(zone_id=zone_id)
        if ret:
            logger.error("zone %s has network, cant set network type" % zone_id)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_ZONE_HAS_NETWORK_CANT_SET_TYPE, zone_id)
    
    if not isinstance(network_type, list):
        network_type = [int(network_type)]
        
    network_type = json_dump(network_type)
    
    if not ctx.pg.base_update(dbconst.TB_ZONE_RESOURCE_LIMIT, {"zone_id": zone_id},{"network_type": network_type}):
        logger.error("modify desktop zone update f DB fail %s" % zone_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def modify_desktop_zone_resource_limit(zone_id, need_maint_columns):
   
    ctx = context.instance()
    
    update_info = ResourceLimit.build_resource_limit(need_maint_columns)
    if update_info:
        if not ctx.pg.batch_update(dbconst.TB_ZONE_RESOURCE_LIMIT, {zone_id: update_info}):
            logger.error("modify zone connection update DB fail %s" % zone_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    if "gpu_class_key" in need_maint_columns:
        ret = update_gpu_class_key(zone_id, need_maint_columns["gpu_class_key"])
        if isinstance(ret, Error):
            return ret
    
    if "network_type" in need_maint_columns:
        ret = update_network_type(zone_id, need_maint_columns["network_type"])
        if isinstance(ret, Error):
            return ret

    ctx.zone_builder.load_zone(zone_id)
    zone_sync_to_other_server(zone_id)

    return None

def check_zone_resources(zone_ids):
    
    zone_resources = {}
    for zone_id in zone_ids:
        
        ret = check_zone_resource(zone_id)
        if not ret:
            continue
        zone_resources[zone_id] = ret
    
    return zone_resources

def check_zone_resource(zone_id):

    ctx = context.instance()
    check_tb = [dbconst.TB_DESKTOP, dbconst.TB_DESKTOP_IMAGE, dbconst.TB_DESKTOP_NETWORK,
                dbconst.TB_DESKTOP_DISK, dbconst.TB_DESKTOP_GROUP]

    resources = {}
    for tb in check_tb:

        conditions = {"zone": zone_id}
        if tb in [dbconst.TB_DESKTOP_IMAGE]:
            conditions["is_default"] = 0
        
        if tb in [dbconst.TB_DESKTOP_NETWORK]:
            conditions["network_type"] = const.NETWORK_TYPE_MANAGED
        
        resource = ctx.pg.base_get(tb, conditions)
        if resource:
            if tb == dbconst.TB_DESKTOP_IMAGE:
                for res in resource:
                    zone = res.get("zone")
                    image_type = res.get("image_type")
                    owner = res.get("owner")
                    if zone_id == zone and const.IMG_TYPE_SYSTEM == image_type and "system" == owner:
                        continue
                    else:
                        resources[tb] = resource
            else:
                resources[tb] = resource

    return resources

def check_modify_desktop_zone_citrix_connection(zone_id, req):

    ctx = context.instance()
    zone_citrix_connection = ctx.pgm.get_zone_citrix_connection(zone_id)
    if not zone_citrix_connection:
        logger.error("no found zone citrix connection %s" % zone_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    modify_keys = ["host", "managed_resource", "port", "protocol", "http_socket_timeout", "storefront_uri","netscaler_uri","support_netscaler","support_citrix_pms"]
    need_maint_columns = {}
    for key in modify_keys:
        # if key not in req or not req[key]:
        if key not in req:
            continue
        
        # if req[key] == zone_citrix_connection.get(key):
        #     continue
        
        if not req[key] and key not in ["support_netscaler","support_citrix_pms"]:
            continue

        need_maint_columns[key] = req[key]

    return need_maint_columns

def reset_zone_connection_host(zone_id, need_maint_columns):
    
    ctx = context.instance()

    host = need_maint_columns.get("host")
    if host:
        logger.error("host %s connection" % host)
        # clear_etc_host(host)

    ret = ctx.pgm.get_zone_connection(zone_id)
    if not ret:
        logger.error("no found zone %s connection" % zone_id)
        return None

    zone_host = ret["host"]
    zone_host_ip = ret["host_ip"]

    set_etc_host(zone_host_ip, zone_host)

    return None

def set_zone_connection_host(zone_id, zone_conn):
    
    ctx = context.instance()

    host = zone_conn.get("host")
    host_ip = zone_conn.get("host_ip")
    ret = ctx.pgm.get_zone_connection(zone_id)
    if not ret:
        logger.error("no found zone connection %s" % zone_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)

    zone_host = ret["host"]
    zone_host_ip = ret["host_ip"]
    if zone_host and zone_host != host:
        clear_etc_host(zone_host)

    if not host_ip:
        if zone_host and zone_host_ip:
            clear_etc_host(zone_host)
        return None

    set_etc_host(host_ip, host)

    return None

def set_zone_keypair(zone_id, keypair):
    
    ctx = context.instance()

    conds = {"zone_id": zone_id}
    need_maint_columns = {"keypair": keypair}

    ret = ctx.pgm.get_zone_connection(zone_id)
    if not ret:
        logger.error("no found zone %s connection" % zone_id)
        return None

    return ctx.pg.base_update(dbconst.TB_ZONE_CONNECTION, conds, need_maint_columns)

def check_modify_desktop_zone_connection(zone_id, req):

    ctx = context.instance()
    
    zone_connection = ctx.pgm.get_zone_connection(zone_id)
    if not zone_connection:
        logger.error("no found zone connection %s" % zone_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)

    has_resource = 1
    ret = check_zone_resource(zone_id)
    if not ret:
        has_resource = 0

    modify_keys = ["base_zone_id", "account_user_id", "zone_access_key_id", "zone_secret_access_key",
                   "host", "host_ip", "port", "protocol", "http_socket_timeout"]
    
    need_maint_columns = {}
    if has_resource:
        if req.get("port"):
            need_maint_columns["port"] = req["port"]
        if req.get("protocol"):
            need_maint_columns["protocol"] = req["protocol"]
        if req.get("http_socket_timeout"):
            need_maint_columns["http_socket_timeout"] = req["http_socket_timeout"]
        if req.get("host"):
            need_maint_columns["host"] = req["host"]
        if req.get("host_ip"):
            need_maint_columns["host_ip"] = req["host_ip"]       
    else:
        for key in modify_keys:
            if key not in req or not req[key]:
                continue
            
            # if req[key] == zone_connection.get(key):
            #     continue
            
            if key == "zone_access_key_id":
                need_maint_columns["access_key_id"] = req[key]
                continue
            
            if key == "zone_secret_access_key":
                need_maint_columns["secret_access_key"] = req[key]
                continue
                
            need_maint_columns[key] = req[key]

    return need_maint_columns
   
def modify_desktop_zone_connection(zone_id, need_maint_columns):

    ctx = context.instance()
    
    ret = ctx.pgm.get_zone_connection(zone_id)
    if not ret:
        logger.error("no found zone connection %s" % zone_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, zone_id)
    zone_connection = ret

    base_zone_id = need_maint_columns.get("base_zone_id")   
    if not base_zone_id:
        base_zone_id = zone_connection["base_zone_id"]
    
    need_maint_columns["status"] = const.ZONE_STATUS_INVAILD
    zone_connection.update(need_maint_columns)
    ret = ctx.zone_builder.get_base_zone(base_zone_id, zone_connection)
    if isinstance(ret, Error):
        return ret
    if ret:
        if base_zone_id != ret["zone_id"]:
            logger.error("base zone %s no match" % (base_zone_id))
            return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_ZONE_CONFIG_ERROR, base_zone_id)

        zone_status = const.ZONE_STATUS_ACTIVE
        need_maint_columns["base_zone_name"] = ret.get("zone_name", "")
        need_maint_columns["status"] = zone_status

    account_user_id = zone_connection.get("account_user_id")
    ret = ctx.zone_builder.check_account_user_id(base_zone_id, zone_connection)
    if not ret:
        logger.error("account_user_id %s is not admin user" % (account_user_id))
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_ZONE_CONFIG_ACCOUNT_USER_ID_IS_NOT_ADMIN_USER, account_user_id)
    
    if not ctx.pg.batch_update(dbconst.TB_ZONE_CONNECTION, {zone_id: need_maint_columns}):
        logger.error("modify zone connection update DB fail %s" % zone_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    ret = ctx.zone_builder.update_zone_status(zone_id)
    if isinstance(ret, Error):
        return ret

    ctx.zone_builder.load_zone(zone_id)
    zone_sync_to_other_server(zone_id)

    return zone_id

def check_citrix_connection_status(host, port):
    
    status = const.ZONE_STATUS_ACTIVE
    if not is_port_open(host, port):
        status = const.ZONE_STATUS_INVAILD

    return status

def modify_desktop_zone_citrix_connection(zone_id, need_maint_columns):

    ctx = context.instance()
    
    host = need_maint_columns["host"]
    port = need_maint_columns["port"]
    need_maint_columns["status"] = check_citrix_connection_status(host, port)
    
    if "managed_resource" in need_maint_columns:
        need_maint_columns["managed_resource"] = json_dump(need_maint_columns["managed_resource"])
    
    if not ctx.pg.batch_update(dbconst.TB_ZONE_CITRIX_CONNECTION, {zone_id: need_maint_columns}):
        logger.error("modify zone connection update DB fail %s" % zone_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    ret = ctx.zone_builder.update_zone_status(zone_id)
    if isinstance(ret, Error):
        return ret

    ctx.zone_builder.load_zone(zone_id)
    ctx.zone_builder.refresh_zone_builder()
    zone_sync_to_other_server(zone_id)

    return zone_id

def zone_sync_to_other_server(zone_id):

    zone_sync_req = {
        "req_type": const.REQ_TYPE_DESKTOP_ZONE_SYNC,
        "action": const.ZONE_SYNC_ACTION_SYNC_ZONE_INFO,
        "zone_id": zone_id
    }

    ret = send_to_server(const.LOCALHOST, const.DISPATCH_SERVER_PORT, zone_sync_req,timeout=3)
    if isinstance(ret, Error):
        return ret

    ret = send_to_server(const.LOCALHOST, const.VDI_SCHEDULER_SERVER_PORT, zone_sync_req,timeout=3)
    if isinstance(ret, Error):
        return ret

    ret = send_to_server(const.LOCALHOST, const.VDI_TERMINAL_PULL_SERVER_PORT, zone_sync_req,timeout=3)
    if isinstance(ret, Error):
        return ret

def check_desktop_zone_citrix_connection_host(host=None,ignore_zone=None):

    ctx = context.instance()
    ret = ctx.pgm.get_zone_citrix_connection_by_host(host=host,ignore_zone=ignore_zone,status=const.ZONE_STATUS_ACTIVE)
    if ret:
        logger.error("zone_citrix_connection host %s already existed" % host)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_ZONE_CITRIX_CONNECTION_HOST_ALREADY_EXISTED, host)

    return None

def check_gpu_config(sender):
    
    ctx = context.instance()
    
    ret = ctx.res.resource_describe_gpus(sender["zone"])
    if not ret:
        return None
    
    resource_gpus = ret
    
    gpus = {}
    gpu_count = {}
    for resource_gpu in resource_gpus:
        gpu_device_name = resource_gpu.get("gpu_device_name")
        if not gpu_device_name:
            continue
        gpu_class = resource_gpu["gpu_class"]
        
        if gpu_device_name not in gpu_count:
            gpu_count[gpu_device_name] = 0
            
        gpu_count[gpu_device_name] = gpu_count[gpu_device_name] + 1
        
        if str(gpu_class) in gpus:
            continue
        gpus[str(gpu_class)] = gpu_device_name

    gpu_infos = []
    for gpu_class, gpu_device_name in gpus.items():
        gpu_info = {}
        gpu_info["gpu_class"] = int(gpu_class)
        gpu_info["gpu_device_name"] = gpu_device_name
        gpu_info["count"] = gpu_count[gpu_device_name]
        gpu_infos.append(gpu_info)
    
    return gpu_infos

def init_zone_info(sender, zone_set):

    ctx = context.instance()
    zone_ids= zone_set.keys()

    for zone_id in zone_ids:
        zone = ctx.pgm.get_zone(zone_id, extras=[])
        if not zone:
            return None

        if zone["status"] != const.ZONE_STATUS_ACTIVE:
            return None

        # refresh_zone_builder
        ctx.zone_builder.load_zone(zone_id)
        ctx.zone_builder.refresh_zone_builder()
        zone_sync_to_other_server(zone_id)

def refresh_other_desktop_server_host_zone_info():

    ctx = context.instance()
    target_hosts = get_target_host_list(ctx)
    logger.debug("target_hosts == %s" % (target_hosts))
    rep = False
    for desktop_server_host in target_hosts:
        export_pythonpath_cmd = 'export PYTHONPATH="/pitrix/lib/pitrix-desktop-tools/apiserver:/pitrix/lib/pitrix-desktop-tools/common:${PYTHONPATH}"'
        cli_cmd = "/pitrix/lib/pitrix-desktop-tools/cli/bin/describe-desktop-zones"
        cmd = "%s && %s" %(export_pythonpath_cmd,cli_cmd)
        logger.debug("cmd == %s" %(cmd))
        ret = _exec_cmd(cmd=cmd, remote_host=desktop_server_host, ssh_port=22,timeout=3)
        if ret != None and ret[0] == 0:
            rep = True
        else:
            rep = False
            return rep

    return rep



