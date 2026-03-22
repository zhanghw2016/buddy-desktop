import constants as const
from log.logger import logger
import context
import db.constants as dbconst
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.misc import explode_array
from utils.global_conf import get_resource_limit_conf
from utils.json import json_dump, json_load

def get_resource_limit_network_type(zone_id):
    
    ctx = context.instance()

    resource_limit = ctx.pgm.get_zone_resource_limit(zone_id)
    if not resource_limit:
        return None

    network_type = resource_limit.get("network_type")
    if not network_type:
        return None
    
    network_type = json_load(network_type)
    
    if isinstance(network_type, list):
        network_type = network_type[0]
    
    network_type = int(network_type)

    return network_type

def get_resource_limit_router(zone_id=None):
    
    ctx = context.instance()
    
    if not zone_id:
        return None
    
    resource_limit = ctx.pgm.get_zone_resource_limit(zone_id)
    if not resource_limit:
        return None
    
    return resource_limit["router"]
    

def get_gpu_class_key(zone_id=None):
    
    ctx = context.instance()
    
    if not zone_id:
        return None

    resource_limit = ctx.pgm.get_zone_resource_limit(zone_id)
    if not resource_limit:
        return None

    ret = ctx.pgm.get_gpu_class_type(zone_id=zone_id)
    if not ret:
        return None
    
    gpus = []
    for _, gpu_class in ret.items():
        key_str = "%s|%s" % (gpu_class["gpu_class_key"], gpu_class["gpu_class"])
        gpus.append(key_str)

    return gpus

def get_default_resource_limit(zone_id=None):
    
    ctx = context.instance()
    
    resource_limit = {}
    default_resource_limit = {}
    ret = get_resource_limit_conf()
    if ret:
        resource_limit = ret

    # cpu
    cpu_cores = resource_limit.get("cpu_cores")
    if cpu_cores:
        cpu_cores = explode_array(cpu_cores, is_integer=True)
    else:
        cpu_cores = const.ZONE_DEFAULT_CPU_CORES
    default_resource_limit["cpu_cores"] = json_dump(cpu_cores)

    # memory size
    memory_size = resource_limit.get("memory_size")
    if memory_size:
        memory_size = explode_array(memory_size, is_integer=True)
    else:
        memory_size = const.ZONE_DEFAULT_MEMORY_SIZE
    default_resource_limit["memory_size"] = json_dump(memory_size)

    # cpu memory pairs
    cpu_memory_pairs = resource_limit.get("cpu_memory_pairs")
    if cpu_memory_pairs:
        cpu_memory_pairs = explode_array(cpu_memory_pairs)
    else:
        cpu_memory_pairs = const.ZONE_DEFAULT_CPU_MEMORY_PAIRS
    default_resource_limit["cpu_memory_pairs"] = json_dump(cpu_memory_pairs)

    # instance_class
    instance_class_list = []
    ret = ctx.pgm.get_instance_class_disk_type(zone_deploy=ctx.zone_deploy)
    if not ret:
        instance_class_list = const.SUPPORTED_INSTANCE_CLASSES
    else:
        instance_class_disk_types = ret
        for _, instance_class_disk_type in instance_class_disk_types.items():
            instance_class = instance_class_disk_type.get("instance_class")
            if instance_class not in instance_class_list:
                instance_class_list.append(instance_class)

    default_resource_limit["instance_class"] = json_dump(instance_class_list)

    # disk_size
    disk_size = resource_limit.get("disk_size")
    if disk_size:
        disk_size = explode_array(disk_size, is_integer=True)
    else:
        disk_size = const.ZONE_DEFAULT_DISK_SIZE
    default_resource_limit["disk_size"] = json_dump(disk_size)

    # supported_gpu
    supported_gpu = resource_limit.get("supported_gpu", 0)
    default_resource_limit["supported_gpu"] = supported_gpu

    # max_disk_count
    max_disk_count = resource_limit.get("max_disk_count")
    if max_disk_count:
        default_resource_limit["max_disk_count"] = int(max_disk_count)
    else:
        default_resource_limit["max_disk_count"] = const.ZONE_DEFAULT_MAX_DISK_COUNT
    
    # default_passwd
    default_resource_limit["default_passwd"] = resource_limit.get("default_passwd", const.ZONE_DEFAULT_DESKTOP_PASSWORD)
   
    # max_snapshot_count
    max_snapshot_count = resource_limit.get("max_snapshot_count")
    if max_snapshot_count:
        default_resource_limit["max_snapshot_count"] = int(max_snapshot_count)
    else:
        default_resource_limit["max_snapshot_count"] = const.ZONE_DEFAULT_MAX_SNAPSHOT_COUNT

    # max_chain_count
    max_chain_count = resource_limit.get("max_chain_count")
    if max_chain_count:
        default_resource_limit["max_chain_count"] = int(max_chain_count)
    else:
        default_resource_limit["max_chain_count"] = const.ZONE_DEFAULT_MAX_CHAIN_COUNT
    
    default_resource_limit["network_type"] = json_dump([const.NETWORK_TYPE_BASE])
    default_resource_limit["gpu_class_key"] = None
    
    if not zone_id:
        return default_resource_limit

    # network type
    default_resource_limit["network_type"] = get_resource_limit_network_type(zone_id)
    default_resource_limit["gpu_class_key"] = get_gpu_class_key(zone_id)

    return default_resource_limit

def init_resource_limit(zone_id):

    ctx = context.instance()
    ret = get_default_resource_limit()
    if isinstance(ret, Error):
        return ret
    zone_info = ret

    resource_limit = dict(
                      zone_id = zone_id,
                      )
    resource_limit.update(zone_info)
    
    if "gpu_class_key" in resource_limit:
        del resource_limit["gpu_class_key"]
    
    # register zone config
    if not ctx.pg.insert(dbconst.TB_ZONE_RESOURCE_LIMIT, resource_limit):
        logger.error("insert newly created zone resource limit for [%s] to db failed" % (resource_limit))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return resource_limit

def check_zone_network_modify(zone_id, network_type):
    
    ctx = context.instance()
    if network_type == const.NETWORK_TYPE_MANAGED:
        networks = ctx.pgm.get_desktop_networks(zone_id=zone_id)
        return 1 if not networks else 0
    else:
        desktop_groups = ctx.pgm.get_desktop_groups(zone_id=zone_id)
        if not desktop_groups:
            desktop_groups = {}
        
        desktops = ctx.pgm.get_desktops(zone=zone_id)
        if not desktops:
            desktops = {}
        
        if desktop_groups or desktops:
            return 0
        else:
            return 1

def format_resource_limit(zone_id, resource_limit=None):

    ctx = context.instance()

    if not resource_limit:
        ret = ctx.pgm.get_zone_resource_limit(zone_id)
        if not ret:
            return None
        
        resource_limit =ret
    
    resource_limit["cpu_cores"] = json_load(resource_limit["cpu_cores"])
    resource_limit["memory_size"] = json_load(resource_limit["memory_size"])
    resource_limit["cpu_memory_pairs"] = json_load(resource_limit["cpu_memory_pairs"])
    resource_limit["instance_class"] = json_load(resource_limit["instance_class"])
    resource_limit["disk_size"] = json_load(resource_limit["disk_size"])

    if "place_group" in resource_limit:
        resource_limit["place_group"] = json_load(resource_limit["place_group"])
    
    resource_limit["gpu_class_key"] = get_gpu_class_key(zone_id)
    resource_limit["network_type"] = get_resource_limit_network_type(zone_id)
    
    resource_limit["modify_network"] = check_zone_network_modify(zone_id, resource_limit["network_type"])

    return resource_limit

def convert_list_string_to_int(string_list):
    
    string_list = json_load(string_list)
    
    new_list = []
    for _string in string_list:
        if isinstance(_string, str):
            new_list.append(int(_string))
        
    return new_list
    
def build_resource_limit(resource_limit):
    
    new_resource_limit = {}
    
    # cpu
    cpu_cores = resource_limit.get("cpu_cores")
    if cpu_cores:
        cpu_cores = convert_list_string_to_int(cpu_cores)
        new_resource_limit["cpu_cores"] = json_dump(cpu_cores)

    # memory size
    memory_size = resource_limit.get("memory_size")
    if memory_size:
        memory_size = convert_list_string_to_int(memory_size)
        new_resource_limit["memory_size"] = json_dump(memory_size)

    # cpu memory pairs
    cpu_memory_pairs = resource_limit.get("cpu_memory_pairs")
    if cpu_memory_pairs:
        new_resource_limit["cpu_memory_pairs"] = cpu_memory_pairs

    # instance_class
    instance_class = resource_limit.get("instance_class")
    if instance_class:
        instance_class = convert_list_string_to_int(instance_class)
        new_resource_limit["instance_class"] = json_dump(instance_class)

    # disk_size
    disk_size = resource_limit.get("disk_size")
    if disk_size:
        disk_size = convert_list_string_to_int(disk_size)
        new_resource_limit["disk_size"] = json_dump(disk_size)

    # supported_gpu
    supported_gpu = resource_limit.get("supported_gpu")
    if supported_gpu is not None:
        new_resource_limit["supported_gpu"] = supported_gpu

    # place_group
    place_group = resource_limit.get("place_group", '')
    if place_group is not None:
        new_resource_limit["place_group"] = place_group

    # max_disk_count
    max_disk_count = resource_limit.get("max_disk_count")
    if max_disk_count:
        new_resource_limit["max_disk_count"] = int(max_disk_count)
    
    # default_passwd
    default_passwd = resource_limit.get("default_passwd")
    if default_passwd:
        new_resource_limit["default_passwd"] = default_passwd

    # ivshmem
    ivshmem = resource_limit.get("ivshmem")
    if ivshmem is not None:
        new_resource_limit["ivshmem"] = ivshmem
    
    # max_snapshot_count
    max_snapshot_count = resource_limit.get("max_snapshot_count")
    if max_snapshot_count:
        new_resource_limit["max_snapshot_count"] = int(max_snapshot_count)
        

    # max_chain_count
    max_chain_count = resource_limit.get("max_chain_count")
    if max_chain_count:
        new_resource_limit["max_chain_count"] = int(max_chain_count)

    # router
    router = resource_limit.get("router")
    if router:
        new_resource_limit["router"] = router

    return new_resource_limit
