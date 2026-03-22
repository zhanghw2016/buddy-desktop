'''
Created on 2012-10-17

@author: yunify
'''

import context
from mc.constants import MC_KEY_PREFIX_SERVER_STATUS, MC_EXPIRES_TIME
from constants import (
    VDI_MEMCACHE_KEY_AUTH_SERVER,
    VDI_MEMCACHE_KEY_POSTGRESQL, 
    VDI_MEMCACHE_KEY_QINGCLOUD_SERVER, 
    VDI_MEMCACHE_KEY_CITRIX_SERVER,
    VDI_MEMCACHE_VALUE_UNKNOWN,
    VDI_MEMCACHE_VALUE_RUNNINT,
    VDI_MEMCACHE_VALUE_TERMINATED,
    TOPIC_MONITOR_SUB_TYPE_SERVER_STATUS_STOP,
    ALL_SUBSCRIBERS,
    TOPIC_MONITOR_SUB_TYPE_SERVER,
    PLATFORM_TYPE_CITRIX,
)
from utils.global_conf import get_postgresql_conf
from utils.net import is_port_open
from error.error import Error
from utils.misc import get_current_time,_exec_cmd,exec_cmd
from send_request import push_topic_monitor
from log.logger import logger
import db.constants as dbconst
import constants as const
from common import get_target_host_list

def check_postgresql_status():

    ctx = context.instance()
    pg_conf = get_postgresql_conf().get('vdi', {})
    host = pg_conf.get('host', '')
    if not host:
        ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                    VDI_MEMCACHE_KEY_POSTGRESQL, 
                    VDI_MEMCACHE_VALUE_UNKNOWN, 
                    MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])
    port = pg_conf.get('port', 5432)
    if is_port_open(host, port):
        ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                    VDI_MEMCACHE_KEY_POSTGRESQL, 
                    VDI_MEMCACHE_VALUE_RUNNINT, 
                    MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])
    else:
        ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                    VDI_MEMCACHE_KEY_POSTGRESQL, 
                    VDI_MEMCACHE_VALUE_TERMINATED, 
                    MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])
        #push message
        data = {"service_name": "postgresql",
               "service_status": TOPIC_MONITOR_SUB_TYPE_SERVER_STATUS_STOP,
               "current_time": get_current_time()
        }
        push_topic_monitor(ALL_SUBSCRIBERS, TOPIC_MONITOR_SUB_TYPE_SERVER, data)

def check_qingcloud_service_status():

    ctx = context.instance()
    zones = ctx.zones
    for zone_id, zone in zones.items():

        zone_info = zone.connection
        host = zone_info["host"] if zone_info else None
        if not host:
            ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                        VDI_MEMCACHE_KEY_QINGCLOUD_SERVER, 
                        VDI_MEMCACHE_VALUE_UNKNOWN, 
                        MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])
        
        port = zone_info["port"] if zone_info else None
        if port is None or (port <= 0 or port > 65535):
            ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                        VDI_MEMCACHE_KEY_QINGCLOUD_SERVER, 
                        VDI_MEMCACHE_VALUE_UNKNOWN, 
                        MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])

        if is_port_open(host, port):
            ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                        VDI_MEMCACHE_KEY_QINGCLOUD_SERVER, 
                        VDI_MEMCACHE_VALUE_RUNNINT, 
                        MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])
        else:
            ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                        VDI_MEMCACHE_KEY_QINGCLOUD_SERVER, 
                        VDI_MEMCACHE_VALUE_TERMINATED, 
                        MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])
            #push message
            data = {"service_name": "iaas_api_server",
                    "service_status": TOPIC_MONITOR_SUB_TYPE_SERVER_STATUS_STOP,
                    "current_time": get_current_time()
                    }
            push_topic_monitor(ALL_SUBSCRIBERS, TOPIC_MONITOR_SUB_TYPE_SERVER, data)

def check_citrix_service_status():

    ctx = context.instance()
       
    zones = ctx.zones
    for zone_id, zone in zones.items():
        
        if zone.platform != PLATFORM_TYPE_CITRIX:
            continue
        
        zone_info = zone.citrix_connection
        host = zone_info["host"] if zone_info else None
        if not host:
            ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                        VDI_MEMCACHE_KEY_CITRIX_SERVER, 
                        VDI_MEMCACHE_VALUE_UNKNOWN, 
                        MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])

        port = zone_info["port"] if zone_info else None
        if port is None or (port <= 0 or port > 65535):
            ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                        VDI_MEMCACHE_KEY_CITRIX_SERVER, 
                        VDI_MEMCACHE_VALUE_UNKNOWN, 
                        MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])
        if is_port_open(host, port):
            ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                        VDI_MEMCACHE_KEY_CITRIX_SERVER, 
                        VDI_MEMCACHE_VALUE_RUNNINT, 
                        MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])
        else:
            ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                        VDI_MEMCACHE_KEY_CITRIX_SERVER, 
                        VDI_MEMCACHE_VALUE_TERMINATED, 
                        MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])
            #push message
            data = {"service_name": "citrix_api_server",
                    "service_status": TOPIC_MONITOR_SUB_TYPE_SERVER_STATUS_STOP,
                    "current_time": get_current_time()
                    }
            push_topic_monitor(ALL_SUBSCRIBERS, TOPIC_MONITOR_SUB_TYPE_SERVER, data)

def check_auth_service_status():
    ctx = context.instance()
    ctx.mcm.set(MC_KEY_PREFIX_SERVER_STATUS, 
                VDI_MEMCACHE_KEY_AUTH_SERVER, 
                VDI_MEMCACHE_VALUE_RUNNINT, 
                MC_EXPIRES_TIME[MC_KEY_PREFIX_SERVER_STATUS])

def get_vnas_server_id():
    cmd = " cat /opt/s2server_id_conf | awk '{print $2}'"
    ret = exec_cmd(cmd=cmd)
    (_, output, _) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_vnas_server_private_ip():
    cmd = "cat /etc/fstab  | grep /mnt/nas | awk '{print $1}' | awk -F: '{print $1}'"
    ret = exec_cmd(cmd=cmd)
    (_, output, _) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def check_vnas_server():
    ctx = context.instance()
    target_hosts = get_target_host_list(ctx)

    for desktop_server_host in target_hosts:
        cmd = "netstat -anp |grep 2049 | grep ESTABLISHED"
        if is_port_open(host=desktop_server_host, port=22):
            ret = _exec_cmd(cmd=cmd, remote_host=desktop_server_host, ssh_port=22)
            (_, output, _) = ret
            logger.debug("output == %s" % (output))
            if not output:
                return False
    return True

def check_vnas_server_status():
    ctx = context.instance()
    if ctx.zone_deploy == const.DEPLOY_TYPE_EXPRESS:
        return None

    ret = get_vnas_server_id()
    if not ret:
        vnas_id = const.S2SERVER_DEFAULT_ID
    else:
        vnas_id = ret

    ret = get_vnas_server_private_ip()
    if not ret:
        vnas_private_ip = ''
    else:
        vnas_private_ip = ret

    ret = check_vnas_server()
    if not ret:
        status = const.SERVICE_STATUS_INVAILD
    else:
        status = const.SERVICE_STATUS_ACTIVE

    ret = ctx.pgm.get_desktop_service_managements(service_version='NAS1.0')
    if not ret:
        register_desktop_server_manangement_vnas(vnas_id, vnas_private_ip, status)
    else:
        vnas_id = ret.keys()[0]
        update_desktop_server_manangement_vnas(vnas_id, vnas_private_ip, status)

    return None

def register_desktop_server_manangement_vnas(vnas_id,vnas_private_ip,status):

    ctx = context.instance()
    #delete s2server in desktop_server_manangement
    conditions = {"service_type": const.S2SERVER_SERVICE_TYPE}
    ctx.pg.base_delete(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, conditions)

    service_id = vnas_id
    service_node_id = vnas_id
    service_ip = vnas_private_ip if vnas_private_ip else ''
    service_node_ip = vnas_private_ip if vnas_private_ip else ''
    status = status
    update_desktop_service_management_info = {}
    update_info = dict(
        service_node_id=service_node_id,
        service_id=service_id,
        service_name=const.S2SERVER_NAME,
        description= '',
        status=status,
        service_version=const.S2SERVER_SERVICE_VERSION,
        service_ip=service_ip,
        service_node_status=status,
        service_node_ip=service_node_ip,
        service_node_type=const.MASTER_SERVICE_NODE_TYPE,
        service_port=const.S2SERVER_SERVICE_PORT,
        service_type=const.S2SERVER_SERVICE_TYPE,
        service_management_type=const.DESKTOP_SERVICE_MANAGEMENT_TYPE,
        create_time=get_current_time(),
    )
    update_desktop_service_management_info[service_node_id] = update_info
    # register desktop_service_management
    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, update_desktop_service_management_info):
        logger.error("insert newly created desktop service management for [%s] to db failed" % (update_desktop_service_management_info))
        return -1

    return 0

def update_desktop_server_manangement_vnas(vnas_id,vnas_private_ip,status):

    ctx = context.instance()

    service_id = vnas_id
    service_node_id = vnas_id
    service_ip = vnas_private_ip if vnas_private_ip else ''
    service_node_ip = vnas_private_ip if vnas_private_ip else ''
    status = status
    update_desktop_service_management_info = {}
    update_info = dict(
        service_node_id=service_node_id,
        service_id=service_id,
        status=status,
        service_ip=service_ip,
        service_node_status=status,
        service_node_ip=service_node_ip,
        create_time=get_current_time(),
    )
    update_desktop_service_management_info[service_node_id] = update_info
    # update desktop_service_management
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, update_desktop_service_management_info):
        logger.error("update desktop service management for [%s] to db failed" % (update_desktop_service_management_info))
        return -1

    return 0

