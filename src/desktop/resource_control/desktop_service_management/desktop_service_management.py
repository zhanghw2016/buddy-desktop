from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
from utils.misc import get_current_time
from utils.misc import exec_cmd
from common import is_citrix_platform

def get_current_valid_desktop_server_ip(server_ip):

    cmd = "cat /etc/hosts | grep 'vdi' | grep %s" %(server_ip)
    ret = exec_cmd("%s" % (cmd))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_current_localhost_ip():

    cmd = '''ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"'''
    ret = exec_cmd("%s" % (cmd))
    (_, output, _) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_desktop_server_master_version(pitrix_version):

    cmd = "echo %s | awk -F- '{print $2}'" %(pitrix_version)
    ret = exec_cmd("%s" %(cmd))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_desktop_server_minor_version(pitrix_version):

    cmd = "echo %s | awk -F- '{print $4}'" %(pitrix_version)
    ret = exec_cmd("%s" % (cmd))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_desktop_server_version(service_node_ip):

    ret = exec_cmd('ssh -o StrictHostKeyChecking=no root@%s "cat /pitrix/version"' %(service_node_ip))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        if output:
            pitrix_version = output
            master_version = get_desktop_server_master_version(pitrix_version)
            minor_version = get_desktop_server_minor_version(pitrix_version)
            desktop_server_version = "%s-%s" %(master_version,minor_version)
            if desktop_server_version:
                return desktop_server_version

    return None

def get_desktop_server_hostname(service_node_ip):
    ret = exec_cmd('ssh -o StrictHostKeyChecking=no root@%s "cat /etc/hostname"' %(service_node_ip))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_cache_master_ip():

    ret = exec_cmd("cat /opt/cache_master_ip_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_cache_node_id():

    ret = exec_cmd("cat /opt/cache_node_id_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_rdb_master_ip():

    ret = exec_cmd("cat /opt/rdb_master_ip_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_rdb_topslave_ip():

    ret = exec_cmd("cat /opt/rdb_topslave_ip_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_master_rdb_instance_id():

    ret = exec_cmd("cat /opt/master_rdb_instance_id_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_topslave_rdb_instance_id():

    ret = exec_cmd("cat /opt/topslave_rdb_instance_id_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def is_use_appcenter_cache_cluster():

    ret = exec_cmd("cat /opt/cache_cluster_id_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def is_use_appcenter_rdb_cluster():

    ret = exec_cmd("cat /opt/rdb_cluster_id_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_postgresql_host():

    ret = exec_cmd("cat /etc/hosts | grep pgpool | awk '{print $1}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_memcache_host():

    ret = exec_cmd("cat /etc/hosts | grep memcached_host | awk '{print $1}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_loadbalancer_id():

    ret = exec_cmd("cat /opt/loadbalancer_id_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_loadbalancer_ip():

    ret = exec_cmd("cat /opt/loadbalancer_ip_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_s2server_id():

    ret = exec_cmd("cat /opt/s2server_id_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_s2server_ip():

    ret = exec_cmd("cat /opt/s2server_ip_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_shared_target_id():

    ret = exec_cmd("cat /opt/shared_target_id_conf | awk '{print $2}'")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def modify_desktop_service_management_attributes(req):

    ctx = context.instance()
    sender = req["sender"]
    service_id = req.get("services")
    service_name = req.get("service_name")
    description = req.get("description")

    ret = ctx.pgm.get_desktop_service_managements(service_ids=service_id,service_node_type=const.MASTER_SERVICE_NODE_TYPE)
    if not ret:
        logger.error("desktop_service_management no found %s" % service_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, service_id)
    desktop_service_managements = ret
    desktop_service_management = desktop_service_managements.values()[0]

    if service_name is None and description is None:
        return None
    else:
        if service_name == desktop_service_management["service_name"] and description == desktop_service_management["description"]:
            return None

    service_type = desktop_service_management["service_type"]
    if service_type == const.CACHE_SERVICE_TYPE:
        if is_use_appcenter_cache_cluster():
            ret = ctx.res.resource_modify_cluster_attributes(sender["zone"],service_type,service_id,service_name,description)
            if not ret:
                logger.error("modify_cluster_attributes failed for [%s]" % service_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED, service_id)
        else:
            ret = ctx.res.resource_modify_cache_attributes(sender["zone"],service_type,service_id,service_name,description)
            if not ret:
                logger.error("modify_cache_attributes failed for [%s]" % service_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED, service_id)

    elif service_type == const.RDB_SERVICE_TYPE:
        if is_use_appcenter_rdb_cluster():
            ret = ctx.res.resource_modify_cluster_attributes(sender["zone"],service_type,service_id,service_name,description)
            if not ret:
                logger.error("modify_cluster_attributes failed for [%s]" % service_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED, service_id)
        else:
            ret = ctx.res.resource_modify_rdb_attributes(sender["zone"],service_type,service_id,service_name,description)
            if not ret:
                logger.error("modify_rdb_attributes failed for [%s]" % service_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED, service_id)

    elif service_type == const.S2SERVER_SERVICE_TYPE:
            ret = ctx.res.resource_modify_s2server_attributes(sender["zone"],service_type,service_id,service_name,description)
            if not ret:
                logger.error("modify_s2server_attributes failed for [%s]" % service_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED, service_id)

    elif service_type == const.LOADBALANCER_SERVICE_TYPE:
            ret = ctx.res.resource_modify_loadbalancer_attributes(sender["zone"],service_type,service_id,service_name,description)
            if not ret:
                logger.error("modify_loadbalancer_attributes failed for [%s]" % service_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED, service_id)

    conditions = dict(
        service_id=service_id
    )
    update_desktop_service_management_info = dict(
        service_name=service_name,
        description=description if description else ''
    )
    if not ctx.pg.base_update(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, conditions, update_desktop_service_management_info):
        logger.error("modify desktop service management for [%s] to db failed" % (update_desktop_service_management_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED)

    return None

def update_desktop_service_management(service_id,service_name,description,status):

    ctx = context.instance()
    conditions = dict(
        service_id=service_id
    )
    update_desktop_service_management_info = dict(
        service_name=service_name,
        description=description if description else '',
        status=status
    )
    if not ctx.pg.base_update(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, conditions,update_desktop_service_management_info):
        logger.error("modify desktop service management for [%s] to db failed" % (update_desktop_service_management_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED)

    return None

def check_desktop_service_managements(service_type):

    ctx = context.instance()
    ret = ctx.pgm.get_desktop_service_managements(service_type=service_type,service_node_type=const.MASTER_SERVICE_NODE_TYPE)
    if not ret:
        logger.error("desktop_service_management no found %s" % service_type)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, service_type)
    desktop_service_managements = ret
    desktop_service_management = desktop_service_managements.values()[0]
    service_id = desktop_service_management.get("service_id")
    return service_id

def update_ad_desktop_service_management(sender, host):

    ctx = context.instance()
    ret = ctx.res.resource_describe_nics_with_private_ip(sender["zone"], host)
    if not ret:
        logger.error("resource_describe_nics_with_private_ip failed for [%s]" % host)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, host)
    nic_sets = ret
    for _, nic_set in nic_sets.items():
        private_ip = nic_set.get("private_ip")
        if private_ip == host:
            instance_id = nic_set.get("instance_id")
            ret = ctx.res.resource_describe_instances(sender["zone"], instance_id)
            if not ret:
                logger.error("resource_describe_instances failed for [%s]" % instance_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, instance_id)
            instance_sets = ret
            for instance_id, instance_set in instance_sets.items():
                status = instance_set["status"]
                if status == const.INST_STATUS_RUN:
                    service_node_status = const.SERVICE_STATUS_ACTIVE
                else:
                    service_node_status = const.SERVICE_STATUS_INVAILD

                conditions = dict(
                    service_node_ip=host
                )
                update_desktop_service_management_info = dict(
                    service_node_status=service_node_status
                )
                if not ctx.pg.base_update(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, conditions,update_desktop_service_management_info):
                    logger.error("modify desktop service management for [%s] to db failed" % (update_desktop_service_management_info))
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED)

def register_ad_desktop_service_management(sender, host):

    ctx = context.instance()
    ret = ctx.res.resource_describe_nics_with_private_ip(sender["zone"], host)
    if not ret:
        logger.error("resource_describe_nics_with_private_ip failed for [%s]" % host)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, host)
    nic_sets = ret
    for _, nic_set in nic_sets.items():
        private_ip = nic_set.get("private_ip")
        if private_ip == host:
            instance_id = nic_set.get("instance_id")
            ret = ctx.res.resource_describe_instances(sender["zone"], instance_id)
            if not ret:
                logger.error("resource_describe_instances failed for [%s]" % instance_id)
                return None
            
            instance_sets = ret
            for instance_id, instance_set in instance_sets.items():
                status = instance_set["status"]
                if status == const.INST_STATUS_RUN:
                    service_node_status = const.SERVICE_STATUS_ACTIVE
                else:
                    service_node_status = const.SERVICE_STATUS_INVAILD
                service_node_id = instance_id
                service_node_ip = private_ip
                update_desktop_service_management_info = {}
                update_info = dict(
                    service_node_id=service_node_id,
                    service_id=const.AD_SERVICE_ID,
                    service_name=const.AD_SERVICE_NAME,
                    description="this is AD Server",
                    status=const.SERVICE_STATUS_ACTIVE,
                    service_version=const.AD_SERVICE_VERSION,
                    service_ip="",
                    service_node_status=service_node_status,
                    service_node_ip=service_node_ip,
                    service_node_type=const.MASTER_SERVICE_NODE_TYPE,
                    service_port=const.AD_SERVICE_PORT,
                    service_type=const.AD_SERVICE_TYPE,
                    create_time=get_current_time(),
                )
                update_desktop_service_management_info[service_node_id] = update_info
                # register desktop_service_management
                if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT,update_desktop_service_management_info):
                    logger.error("insert newly created desktop service management for [%s] to db failed" % (update_info))
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def register_rdb_desktop_service_management(sender, host):

    ctx = context.instance()
    ret = ctx.res.resource_describe_nics_with_private_ip(sender["zone"], host)
    if not ret:
        logger.error("resource_describe_nics_with_private_ip failed for [%s]" % host)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, host)
    nic_sets = ret
    for _, nic_set in nic_sets.items():
        private_ip = nic_set.get("private_ip")
        if private_ip == host:
            instance_id = nic_set.get("instance_id")
            ret = ctx.res.resource_describe_instances(sender["zone"], instance_id)
            if not ret:
                logger.error("resource_describe_instances failed for [%s]" % instance_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, instance_id)
            instance_sets = ret
            for instance_id, instance_set in instance_sets.items():
                instance_name = instance_set.get("instance_name")
                instance_name_list = instance_name.split(".")
                rdb_id = instance_name_list[0]
                rdb_instance_id = instance_name_list[1]
                ret = ctx.res.resource_describe_rdbs(sender["zone"], rdb_id)
                if not ret:
                    logger.error("describe_rdbs failed for [%s]" % rdb_id)
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, rdb_id)
                rdb_sets = ret
                for rdb_id, rdb_set in rdb_sets.items():
                    service_name = rdb_set.get("rdb_name")
                    description = rdb_set.get("description")
                    status = rdb_set.get("status")
                    service_node_id = rdb_instance_id
                    service_id = rdb_id

                    update_desktop_service_management_info = {}
                    update_info = dict(
                        service_node_id=service_node_id,
                        service_id=service_id,
                        service_name=service_name if service_name else '',
                        description=description if description else '',
                        status=status,
                        service_version=const.RDB_SERVICE_VERSION,
                        service_ip=host,
                        service_node_status=status,
                        service_node_ip=host,
                        service_node_type=const.MASTER_SERVICE_NODE_TYPE,
                        service_port=const.RDB_SERVICE_PORT,
                        service_type=const.RDB_SERVICE_TYPE,
                        service_management_type=const.DESKTOP_SERVICE_MANAGEMENT_TYPE,
                        create_time=get_current_time(),
                    )
                    update_desktop_service_management_info[service_node_id] = update_info
                    # register desktop_service_management
                    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT,update_desktop_service_management_info):
                        logger.error("insert newly created desktop service management for [%s] to db failed" % (update_info))
                        return Error(ErrorCodes.INTERNAL_ERROR,
                                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def register_cache_desktop_service_management(sender, host):

    ctx = context.instance()
    ret = ctx.res.resource_describe_nics_with_private_ip(sender["zone"], host)
    if not ret:
        logger.error("resource_describe_nics_with_private_ip failed for [%s]" % host)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, host)
    nic_sets = ret
    for _, nic_set in nic_sets.items():
        private_ip = nic_set.get("private_ip")
        if private_ip == host:
            instance_id = nic_set.get("instance_id")
            ret = ctx.res.resource_describe_instances(sender["zone"], instance_id)
            if not ret:
                logger.error("resource_describe_instances failed for [%s]" % instance_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, instance_id)
            instance_sets = ret
            for instance_id, instance_set in instance_sets.items():
                instance_name = instance_set.get("instance_name")
                instance_name_list = instance_name.split(".")
                cache_id = instance_name_list[0]
                cache_node_id = instance_name_list[1]

                ret = ctx.res.resource_describe_caches(sender["zone"], cache_id)
                if not ret:
                    logger.error("describe_caches failed for [%s]" % cache_id)
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, cache_id)
                cache_sets = ret
                for cache_id, cache_set in cache_sets.items():
                    service_name = cache_set.get("cache_name")
                    description = cache_set.get("description")
                    status = cache_set.get("status")
                    service_node_id = cache_node_id
                    service_id = cache_id

                    update_desktop_service_management_info = {}
                    update_info = dict(
                        service_node_id=service_node_id,
                        service_id=service_id,
                        service_name=service_name if service_name else '',
                        description=description if description else '',
                        status=status,
                        service_version=const.CACHE_SERVICE_VERSION,
                        service_ip=host,
                        service_node_status=status,
                        service_node_ip=host,
                        service_node_type=const.MASTER_SERVICE_NODE_TYPE,
                        service_port=const.CACHE_SERVICE_PORT,
                        service_type=const.CACHE_SERVICE_TYPE,
                        service_management_type=const.DESKTOP_SERVICE_MANAGEMENT_TYPE,
                        create_time=get_current_time(),
                    )
                    update_desktop_service_management_info[service_node_id] = update_info
                    # register desktop_service_management
                    if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT,update_desktop_service_management_info):
                        logger.error("insert newly created desktop service management for [%s] to db failed" % (update_info))
                        return Error(ErrorCodes.INTERNAL_ERROR,
                                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def register_loadbalancer_desktop_service_management(sender, loadbalancer_id,loadbalancer_ip):

    ctx = context.instance()
    ret = ctx.res.resource_describe_loadbalancers(sender["zone"], loadbalancer_id)
    if not ret:
        logger.error("describe_loadbalancers failed for [%s]" % loadbalancer_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, loadbalancer_id)
    loadbalancer_sets = ret

    for loadbalancer_id, loadbalancer_set in loadbalancer_sets.items():
        service_id = loadbalancer_id
        service_name = loadbalancer_set.get("loadbalancer_name")
        description = loadbalancer_set.get("description")
        status = loadbalancer_set.get("status")
        service_ip = loadbalancer_ip

        listeners = loadbalancer_set.get("listeners")
        for listener in listeners:
            listener_port = listener.get("listener_port")
            if 80 == listener_port:
                loadbalancer_listener_id = listener.get("loadbalancer_listener_id")
                # DescribeLoadBalancerBackends
                ret = ctx.res.resource_describe_loadbalancer_backends(sender["zone"], loadbalancer_listener_id)
                if not ret:
                    logger.error("resource_describe_loadbalancer_backends failed for [%s]" % loadbalancer_listener_id)
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, loadbalancer_listener_id)
                loadbalancer_backend_sets = ret
                for _, loadbalancer_backend_set in loadbalancer_backend_sets.items():
                    service_node_id = loadbalancer_backend_set.get("resource_id")
                    service_node_ip = loadbalancer_backend_set.get("private_ip")
                    ret = get_current_valid_desktop_server_ip(service_node_ip)
                    if not ret:
                        current_localhost_ip = get_current_localhost_ip()
                        if service_node_ip != current_localhost_ip:
                            logger.info("service_node_ip[%s] not equal current_localhost_ip[%s]" % (service_node_ip,current_localhost_ip))
                            continue
                    if service_node_id and service_node_ip:
                        update_desktop_service_management_info = {}
                        update_info = dict(
                            service_node_id=service_node_id,
                            service_id=service_id,
                            service_name=service_name if service_name else '',
                            description=description if description else '',
                            status=status,
                            service_version=const.LOADBALANCER_SERVICE_VERSION,
                            service_ip=service_ip,
                            service_node_status=status,
                            service_node_ip=service_node_ip,
                            service_node_type=const.MASTER_SERVICE_NODE_TYPE,
                            service_port=const.LOADBALANCER_SERVICE_PORT,
                            service_type=const.LOADBALANCER_SERVICE_TYPE,
                            service_management_type=const.DESKTOP_SERVICE_MANAGEMENT_TYPE,
                            create_time=get_current_time(),
                        )
                        update_desktop_service_management_info[service_node_id] = update_info
                        # register desktop_service_management
                        if not ctx.pg.batch_insert(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT,
                                                   update_desktop_service_management_info):
                            logger.error("insert newly created desktop service management for [%s] to db failed" % (
                                update_desktop_service_management_info))
                            return Error(ErrorCodes.INTERNAL_ERROR,
                                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def register_s2server_desktop_service_management(sender, s2server_id, s2server_ip,shared_target_id):

    ctx = context.instance()
    service_id = s2server_id
    service_node_id = shared_target_id
    service_ip = s2server_ip
    service_node_ip = s2server_ip

    #DescribeS2Servers
    ret = ctx.res.resource_describe_s2servers(sender["zone"], s2server_id)
    if not ret:
        logger.error("describe_s2servers failed for [%s]" % s2server_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, s2server_id)
    s2_server_sets = ret

    for _, s2_server_set in s2_server_sets.items():
        service_name = s2_server_set.get("s2_server_name")
        description = s2_server_set.get("description")
        status = s2_server_set.get("status")

        update_desktop_service_management_info = {}
        update_info = dict(
            service_node_id=service_node_id,
            service_id=service_id,
            service_name=service_name if service_name else '',
            description=description if description else '',
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
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return None

def register_cluster_rdb_desktop_service_management(sender, rdb_cluster_id,rdb_master_ip,rdb_topslave_ip,master_rdb_instance_id,topslave_rdb_instance_id):

    ctx = context.instance()

    service_nodes_master = {"service_id":rdb_cluster_id,"service_node_id": master_rdb_instance_id, "service_node_ip": rdb_master_ip, "service_ip": rdb_master_ip,"service_node_type":"master"}
    service_nodes_topslave = {"service_id":rdb_cluster_id,"service_node_id": topslave_rdb_instance_id, "service_node_ip": rdb_topslave_ip,"service_ip": rdb_master_ip,"service_node_type":"topslave"}
    service_nodes_list = [service_nodes_master,service_nodes_topslave]

    ret = ctx.res.resource_describe_clusters(sender["zone"], rdb_cluster_id)
    if not ret:
        logger.error("resource_describe_clusters failed for [%s]" % rdb_cluster_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, rdb_cluster_id)
    cluster_sets = ret

    for _, cluster_set in cluster_sets.items():
        service_name = cluster_set.get("name")
        description = cluster_set.get("description")
        status = cluster_set.get("status")
        if status == const.SERVICE_STATUS_ACTIVE:
            service_node_status = const.SERVICE_STATUS_ACTIVE
        else:
            service_node_status = const.SERVICE_STATUS_INVAILD

        for service_nodes in service_nodes_list:
            service_id = service_nodes.get("service_id")
            service_node_id = service_nodes.get("service_node_id")
            service_node_ip = service_nodes.get("service_node_ip")
            service_ip = service_nodes.get("service_ip")
            service_node_type = service_nodes.get("service_node_type")

            desktop_service_management = {}
            desktop_service_management["service_node_id"] = service_node_id
            desktop_service_management["service_id"] = service_id
            desktop_service_management["service_name"] = service_name
            desktop_service_management["description"] = description
            desktop_service_management["status"] = service_node_status
            desktop_service_management["service_version"] = const.RDB_SERVICE_VERSION
            desktop_service_management["service_ip"] = service_ip
            desktop_service_management["service_node_status"] = service_node_status
            desktop_service_management["service_node_ip"] = service_node_ip
            desktop_service_management["service_node_type"] = service_node_type
            desktop_service_management["service_port"] = const.RDB_SERVICE_PORT
            desktop_service_management["service_type"] = const.RDB_SERVICE_TYPE
            desktop_service_management["service_management_type"] = const.DESKTOP_SERVICE_MANAGEMENT_TYPE

            ret = ctx.pgm.get_desktop_service_managements(service_management_type=const.DESKTOP_SERVICE_MANAGEMENT_TYPE,service_type=const.RDB_SERVICE_TYPE, service_node_ids=service_node_id)
            if ret:
                logger.error("desktop service instances already existed %s" % service_node_id)
                return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_INSTANCE_ALREADY_EXISTED, service_node_id)

            # register desktop_service_management
            if not ctx.pg.insert(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, desktop_service_management):
                logger.error("insert newly created desktop service management for [%s] to db failed" % (desktop_service_management))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_DESKTOP_SERVICE_MANAGEMENT_FAILED)

def register_cluster_cache_desktop_service_management(sender, cache_cluster_id, cache_master_ip,cache_node_id):

    ctx = context.instance()

    service_nodes_master = {"service_id":cache_cluster_id,"service_node_id": cache_node_id, "service_node_ip": cache_master_ip, "service_ip": cache_master_ip,"service_node_type":"master"}
    service_nodes_list = [service_nodes_master]

    ret = ctx.res.resource_describe_clusters(sender["zone"], cache_cluster_id)
    if not ret:
        logger.error("resource_describe_clusters failed for [%s]" % cache_cluster_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, cache_cluster_id)
    cluster_sets = ret

    for _, cluster_set in cluster_sets.items():
        service_name = cluster_set.get("name")
        description = cluster_set.get("description")
        status = cluster_set.get("status")
        if status == const.SERVICE_STATUS_ACTIVE:
            service_node_status = const.SERVICE_STATUS_ACTIVE
        else:
            service_node_status = const.SERVICE_STATUS_INVAILD

        for service_nodes in service_nodes_list:
            service_id = service_nodes.get("service_id")
            service_node_id = service_nodes.get("service_node_id")
            service_node_ip = service_nodes.get("service_node_ip")
            service_ip = service_nodes.get("service_ip")
            service_node_type = service_nodes.get("service_node_type")

            desktop_service_management = {}
            desktop_service_management["service_node_id"] = service_node_id
            desktop_service_management["service_id"] = service_id
            desktop_service_management["service_name"] = service_name
            desktop_service_management["description"] = description
            desktop_service_management["status"] = service_node_status
            desktop_service_management["service_version"] = const.CACHE_SERVICE_VERSION
            desktop_service_management["service_ip"] = service_ip
            desktop_service_management["service_node_status"] = service_node_status
            desktop_service_management["service_node_ip"] = service_node_ip
            desktop_service_management["service_node_type"] = service_node_type
            desktop_service_management["service_port"] = const.CACHE_SERVICE_PORT
            desktop_service_management["service_type"] = const.CACHE_SERVICE_TYPE
            desktop_service_management["service_management_type"] = const.DESKTOP_SERVICE_MANAGEMENT_TYPE

            ret = ctx.pgm.get_desktop_service_managements(service_management_type=const.DESKTOP_SERVICE_MANAGEMENT_TYPE,service_type=const.CACHE_SERVICE_TYPE, service_node_ids=service_node_id)
            if ret:
                logger.error("desktop service instances already existed %s" % service_node_id)
                return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_INSTANCE_ALREADY_EXISTED, service_node_id)

            # register desktop_service_management
            if not ctx.pg.insert(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, desktop_service_management):
                logger.error("insert newly created desktop service management for [%s] to db failed" % (desktop_service_management))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_DESKTOP_SERVICE_MANAGEMENT_FAILED)

def sync_deskop_service_management(req):

    ctx = context.instance()
    sender = req["sender"]
    for service_type in const.SERVICE_TYPE_LIST:
        if const.AD_SERVICE_TYPE == service_type:
            continue
        if const.RDB_SERVICE_TYPE == service_type:
            if is_use_appcenter_rdb_cluster():
                logger.info("use appcenter rdb")
                ret = ctx.pgm.get_desktop_service_managements(service_type=service_type,service_node_type=const.MASTER_SERVICE_NODE_TYPE)
                if not ret:
                    rdb_cluster_id = is_use_appcenter_rdb_cluster()
                    if not rdb_cluster_id:
                        logger.error("rdb_cluster_id is None")
                        return None

                    rdb_master_ip = get_rdb_master_ip()
                    if not rdb_master_ip:
                        logger.error("rdb_master_ip is None")
                        return None

                    rdb_topslave_ip = get_rdb_topslave_ip()
                    if not rdb_topslave_ip:
                        logger.error("rdb_topslave_ip is None")
                        return None

                    master_rdb_instance_id = get_master_rdb_instance_id()
                    if not master_rdb_instance_id:
                        logger.error("master_rdb_instance_id is None")
                        return None

                    topslave_rdb_instance_id = get_topslave_rdb_instance_id()
                    if not topslave_rdb_instance_id:
                        logger.error("topslave_rdb_instance_id is None")
                        return None

                    ret = register_cluster_rdb_desktop_service_management(sender, rdb_cluster_id,rdb_master_ip,rdb_topslave_ip,master_rdb_instance_id,topslave_rdb_instance_id)
                    if isinstance(ret, Error):
                        return ret
                else:
                    ret = check_desktop_service_managements(service_type)
                    if isinstance(ret, Error):
                        return ret
                    service_id = ret

                    ret = ctx.res.resource_describe_clusters(sender["zone"], service_id)
                    if not ret:
                        logger.error("resource_describe_clusters failed for [%s]" % service_id)
                        return Error(ErrorCodes.INTERNAL_ERROR,
                                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, service_id)
                    cluster_sets = ret

                    for _, cluster_set in cluster_sets.items():
                        service_name = cluster_set.get("name")
                        description = cluster_set.get("description")
                        status = cluster_set.get("status")
                        if status == const.SERVICE_STATUS_ACTIVE:
                            service_node_status = const.SERVICE_STATUS_ACTIVE
                        else:
                            service_node_status = const.SERVICE_STATUS_INVAILD
                        ret = update_desktop_service_management(service_id, service_name, description, service_node_status)
                        if isinstance(ret, Error):
                            return ret

            else:
                logger.info("use iaas rdb")
                ret = ctx.pgm.get_desktop_service_managements(service_type=service_type,service_node_type=const.MASTER_SERVICE_NODE_TYPE)
                if not ret:
                    pgpool = get_postgresql_host()
                    if not pgpool:
                        logger.error("pgpool is None")
                        return None

                    ret = register_rdb_desktop_service_management(sender, pgpool)
                    if isinstance(ret, Error):
                        return ret
                else:
                    ret = check_desktop_service_managements(service_type)
                    if isinstance(ret, Error):
                        return ret
                    service_id = ret
                    ret = ctx.res.resource_describe_rdbs(sender["zone"],service_id)
                    if not ret:
                        logger.error("describe_rdbs failed for [%s]" % service_id)
                        return Error(ErrorCodes.INTERNAL_ERROR,
                                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, service_id)
                    rdb_sets = ret
                    for _,rdb_set in rdb_sets.items():
                        service_name = rdb_set.get("rdb_name")
                        description = rdb_set.get("description")
                        status = rdb_set.get("status")
                        if status == const.SERVICE_STATUS_ACTIVE:
                            service_node_status = const.SERVICE_STATUS_ACTIVE
                        else:
                            service_node_status = const.SERVICE_STATUS_INVAILD
                        ret = update_desktop_service_management(service_id, service_name, description, service_node_status)
                        if isinstance(ret, Error):
                            return ret

        elif const.CACHE_SERVICE_TYPE == service_type:
            if is_use_appcenter_cache_cluster():
                logger.info("use appcenter cache")
                ret = ctx.pgm.get_desktop_service_managements(service_type=service_type,service_node_type=const.MASTER_SERVICE_NODE_TYPE)
                if not ret:
                    cache_cluster_id = is_use_appcenter_cache_cluster()
                    if not cache_cluster_id:
                        logger.error("cache_cluster_id is None")
                        return None

                    cache_master_ip = get_cache_master_ip()
                    if not cache_master_ip:
                        logger.error("cache_master_ip is None")
                        return None

                    cache_node_id = get_cache_node_id()
                    if not cache_node_id:
                        logger.error("cache_node_id is None")
                        return None

                    ret = register_cluster_cache_desktop_service_management(sender, cache_cluster_id, cache_master_ip,cache_node_id)
                    if isinstance(ret, Error):
                        return ret
                else:
                    ret = check_desktop_service_managements(service_type)
                    if isinstance(ret, Error):
                        return ret
                    service_id = ret

                    ret = ctx.res.resource_describe_clusters(sender["zone"], service_id)
                    if not ret:
                        logger.error("resource_describe_clusters failed for [%s]" % service_id)
                        return Error(ErrorCodes.INTERNAL_ERROR,
                                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, service_id)
                    cluster_sets = ret

                    for _, cluster_set in cluster_sets.items():
                        service_name = cluster_set.get("name")
                        description = cluster_set.get("description")
                        status = cluster_set.get("status")
                        if status == const.SERVICE_STATUS_ACTIVE:
                            service_node_status = const.SERVICE_STATUS_ACTIVE
                        else:
                            service_node_status = const.SERVICE_STATUS_INVAILD
                        ret = update_desktop_service_management(service_id, service_name, description, service_node_status)
                        if isinstance(ret, Error):
                            return ret
            else:
                logger.info("use iaas cache")
                ret = ctx.pgm.get_desktop_service_managements(service_type=service_type,service_node_type=const.MASTER_SERVICE_NODE_TYPE)
                if not ret:
                    memcached_host = get_memcache_host()
                    if not memcached_host:
                        logger.error("memcached_host is None")
                        return None

                    ret = register_cache_desktop_service_management(sender, memcached_host)
                    if isinstance(ret, Error):
                        return ret
                else:
                    ret = check_desktop_service_managements(service_type)
                    if isinstance(ret, Error):
                        return ret
                    service_id = ret

                    ret = ctx.res.resource_describe_caches(sender["zone"], service_id)
                    if not ret:
                        logger.error("describe_caches failed for [%s]" % service_id)
                        return Error(ErrorCodes.INTERNAL_ERROR,
                                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, service_id)
                    cache_sets = ret
                    for _, cache_set in cache_sets.items():
                        service_name = cache_set.get("cache_name")
                        description = cache_set.get("description")
                        status = cache_set.get("status")
                        if status == const.SERVICE_STATUS_ACTIVE:
                            service_node_status = const.SERVICE_STATUS_ACTIVE
                        else:
                            service_node_status = const.SERVICE_STATUS_INVAILD
                        ret = update_desktop_service_management(service_id, service_name, description, service_node_status)
                        if isinstance(ret, Error):
                            return ret

        elif const.LOADBALANCER_SERVICE_TYPE == service_type:
            ret = ctx.pgm.get_desktop_service_managements(service_type=service_type,service_node_type=const.MASTER_SERVICE_NODE_TYPE)
            if not ret:
                loadbalancer_id = get_loadbalancer_id()
                loadbalancer_ip = get_loadbalancer_ip()
                if  loadbalancer_id and loadbalancer_ip:
                    ret = register_loadbalancer_desktop_service_management(sender, loadbalancer_id,loadbalancer_ip)
                    if isinstance(ret, Error):
                        return ret
            else:
                ret = check_desktop_service_managements(service_type)
                if isinstance(ret, Error):
                    return ret
                service_id = ret

                ret = ctx.res.resource_describe_loadbalancers(sender["zone"], service_id)
                if not ret:
                    logger.error("describe_loadbalancers failed for [%s]" % service_id)
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, service_id)
                loadbalancer_sets = ret
                for loadbalancer_id, loadbalancer_set in loadbalancer_sets.items():
                    service_name = loadbalancer_set.get("loadbalancer_name")
                    description = loadbalancer_set.get("description")
                    status = loadbalancer_set.get("status")
                    ret = update_desktop_service_management(service_id, service_name, description, status)
                    if isinstance(ret, Error):
                        return ret

                    ret = update_loadbalancer_desktop_service_management(sender)
                    if isinstance(ret, Error):
                        return ret

        elif const.AD_SERVICE_TYPE == service_type:
            ret = ctx.pgm.get_desktop_service_managements(service_type=service_type,service_node_type=const.MASTER_SERVICE_NODE_TYPE)
            if not ret:
                ret = ctx.pgm.get_auth_services()
                if not ret:
                    logger.info("no found auth service")
                    continue
                auth_services = ret
                for _, auth_service in auth_services.items():
                    host = auth_service.get("host")
                    ret = register_ad_desktop_service_management(sender, host)
                    if isinstance(ret, Error):
                        return ret

            else:
                exist_service_node_ip = []
                desktop_service_managements = ret
                for _, desktop_service_management in desktop_service_managements.items():
                    service_node_ip = desktop_service_management.get("service_node_ip")
                    if service_node_ip  not in exist_service_node_ip:
                        exist_service_node_ip.append(service_node_ip)

                ret = ctx.pgm.get_auth_services()
                if not ret:
                    logger.info("no found auth service")
                    continue
                auth_services = ret
                for _, auth_service in auth_services.items():
                    host = auth_service.get("host")
                    if host in exist_service_node_ip:
                        ret = update_ad_desktop_service_management(sender, host)
                        if isinstance(ret, Error):
                            return ret
                    else:
                        ret = register_ad_desktop_service_management(sender, host)
                        if isinstance(ret, Error):
                            return ret
    return None

def refresh_deskop_service_management(req):

    ret = sync_deskop_service_management(req)
    if isinstance(ret, Error):
        return ret

    return None

def filter_system_instances(sender, body=None):

    ctx = context.instance()

    offset = 0
    limit = const.MAX_LIMIT_PARAM
    if not body:
        body = {}

    body["offset"] = offset
    body["limit"] = limit

    ret = ctx.res.resource_describe_instances_by_search_word(sender["zone"], body)
    if not ret:
        return None

    # add private_ip
    private_ip = ''
    for _,instance in ret.items():
        vxnets = instance.get("vxnets")
        if vxnets:
            vxnet = vxnets[0]
            if vxnet:
                private_ip = vxnet.get("private_ip",'')
        instance["private_ip"] = private_ip

    return ret

def remove_desktop_service_instances(service_type,instance_ids):

    ctx = context.instance()

    ret = ctx.pgm.get_desktop_service_managements(service_type=service_type,service_node_ids=instance_ids)
    if not ret:
        logger.error("desktop service management instance no found %s" % instance_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_INSTANCE_NO_FOUND, instance_ids)
    desktop_service_managements = ret

    for service_node_id, _ in desktop_service_managements.items():

        if not ctx.pg.delete(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, service_node_id):
            logger.error("delete desktop service management instance %s fail" % service_node_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_DESKTOP_SERVICE_INSTANCE_FAILED, service_node_id)

    return None

def check_service_type_valid(sender,service_management_type,service_type):

    ctx = context.instance()
    if const.CITRIX_SERVICE_MANAGEMENT_TYPE == service_management_type:
        if not is_citrix_platform(ctx, sender["zone"]):
            logger.error("only citrix zone support load citrix service_type %s" % (service_type))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_ONLY_CITRIX_ZONE_SUPPORT_LOAD_CITRIX_SERVICE_TYPE,service_type)

        if service_type not in const.CITRIX_SERVICE_TYPE_LIST:
            logger.error("service type %s error" % service_type)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESKTOP_SERVICE_INSTANCE_SERVICE_TYPE_ERRORED, service_type)
    elif const.DESKTOP_SERVICE_MANAGEMENT_TYPE == service_management_type:
        if service_type not in const.DESKTOP_SERVICE_TYPE_LIST:
            logger.error("service type %s error" % service_type)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESKTOP_SERVICE_INSTANCE_SERVICE_TYPE_ERRORED, service_type)
    else:
        logger.error("service type %s error" % service_type)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESKTOP_SERVICE_INSTANCE_SERVICE_TYPE_ERRORED, service_type)

    return None

def load_desktop_service_instances(sender,service_management_type,service_type,instance_ids):

    ctx = context.instance()
    ret = ctx.res.resource_describe_instances(sender["zone"], instance_ids)
    if not ret:
        logger.error("describe instance iaas request return fail %s" % instance_ids)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, instance_ids)
    instances = ret
    service_nodes = {}
    service_nodes_list = []
    service_ip = " "

    for instance_id in instance_ids:
        instance = instances[instance_id]
        service_node_id = instance_id
        status = instance["status"]
        if status == const.INST_STATUS_RUN:
            service_node_status = const.SERVICE_STATUS_ACTIVE
        else:
            service_node_status = const.SERVICE_STATUS_INVAILD

        vxnets = instance.get("vxnets")
        if vxnets:
            for vxnet in vxnets:
                service_node_ip = vxnet.get("private_ip")
        else:
            service_node_ip = ""

        if const.RDB_SERVICE_TYPE == service_type:
            instance_name = instance.get("instance_name")
            instance_name_list = instance_name.split(".")
            count = len(instance_name_list)
            if count < 2:
                logger.error("instance_id %s is not %s" % (instance_id, service_type))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_INSTANCE_IS_NOT_SERVICE_TYPE, (instance_id, service_type))
            rdb_id = instance_name_list[0]
            rdb_instance_id = instance_name_list[1]

            ret = ctx.res.resource_describe_rdbs(sender["zone"], rdb_id)
            if not ret:
                logger.error("describe_rdbs failed for [%s]" % rdb_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, rdb_id)
            rdb_sets = ret
            for rdb_id, rdb_set in rdb_sets.items():
                service_name = rdb_set.get("rdb_name")
            service_node_id = rdb_instance_id
            service_id = rdb_id
            service_nodes = {"service_node_id": service_node_id, "service_node_ip": service_node_ip,"service_ip": service_ip}
            service_nodes_list.append(service_nodes)

        elif const.CACHE_SERVICE_TYPE == service_type:
            instance_name = instance.get("instance_name")
            instance_name_list = instance_name.split(".")
            count = len(instance_name_list)
            if count < 2:
                logger.error("instance_id %s is not %s" % (instance_id,service_type))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_INSTANCE_IS_NOT_SERVICE_TYPE, (instance_id,service_type))
            cache_id = instance_name_list[0]
            cache_node_id = instance_name_list[1]

            ret = ctx.res.resource_describe_caches(sender["zone"], cache_id)
            if not ret:
                logger.error("describe_caches failed for [%s]" % cache_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, cache_id)
            cache_sets = ret
            for cache_id, cache_set in cache_sets.items():
                service_name = cache_set.get("cache_name")
            service_node_id = cache_node_id
            service_id = cache_id

            service_nodes = {"service_node_id": service_node_id, "service_node_ip": service_node_ip,"service_ip": service_ip}
            service_nodes_list.append(service_nodes)

        elif const.S2SERVER_SERVICE_TYPE == service_type:
            instance_name = instance.get("instance_name")
            s2server_id = instance_name

            ret = ctx.res.resource_describe_s2servers(sender["zone"], s2server_id)
            if not ret:
                logger.error("describe_s2servers failed for [%s]" % s2server_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, s2server_id)
            s2_server_sets = ret
            for s2_server_id, s2_server_set in s2_server_sets.items():
                service_name = s2_server_set.get("s2_server_name")
                shared_targets = s2_server_set.get("shared_targets")
                service_node_id = shared_targets.keys()[0]
                service_id = s2_server_id
                service_nodes = {"service_node_id": service_node_id, "service_node_ip": service_node_ip,"service_ip": service_ip}
                service_nodes_list.append(service_nodes)

        elif const.LOADBALANCER_SERVICE_TYPE == service_type:
            instance_name = instance.get("instance_name")
            loadbalancer_id = instance_name

            ret = ctx.res.resource_describe_loadbalancers(sender["zone"], loadbalancer_id)
            if not ret:
                logger.error("describe_loadbalancers failed for [%s]" % loadbalancer_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, loadbalancer_id)
            loadbalancer_sets = ret
            for loadbalancer_id, loadbalancer_set in loadbalancer_sets.items():
                service_id = loadbalancer_id
                service_name = loadbalancer_set.get("loadbalancer_name")
                vxnets = loadbalancer_set.get("vxnet")
                if vxnets:
                    service_ip = vxnets.get("private_ip")
                else:
                    service_ip = ""

                listeners = loadbalancer_set.get("listeners")
                loadbalancer_listener_id = listeners[0].get("loadbalancer_listener_id")

                # DescribeLoadBalancerBackends
                ret = ctx.res.resource_describe_loadbalancer_backends(sender["zone"], loadbalancer_listener_id)
                if not ret:
                    logger.error("resource_describe_loadbalancer_backends failed for [%s]" % loadbalancer_listener_id)
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_DESKTOP_SERVICE_MANAGEMENT_NO_FOUND, loadbalancer_listener_id)
                loadbalancer_backend_sets = ret

                for _, loadbalancer_backend_set in loadbalancer_backend_sets.items():
                    service_node_id = loadbalancer_backend_set.get("resource_id")
                    service_node_ip = loadbalancer_backend_set.get("private_ip")
                    service_nodes = {"service_node_id":service_node_id,"service_node_ip":service_node_ip,"service_ip":service_ip}
                    service_nodes_list.append(service_nodes)

        else:
            service_nodes = {"service_node_id": service_node_id, "service_node_ip": service_node_ip,"service_ip": service_ip}
            service_nodes_list.append(service_nodes)

        if const.DDC_SERVICE_TYPE == service_type:
            service_id = const.DDC_SERVICE_ID
            service_name = const.DDC_SERVICE_NAME
            service_version = const.DDC_SERVICE_VERSION
            service_port = const.DDC_SERVICE_PORT

        elif const.STORE_FRONT_SERVICE_TYPE == service_type:
            service_id = const.STORE_FRONT_SERVICE_ID
            service_name = const.STORE_FRONT_SERVICE_NAME
            service_version = const.STORE_FRONT_SERVICE_VERSION
            service_port = const.STORE_FRONT_SERVICE_PORT

        elif const.CITRIX_DATABASE_SERVICE_TYPE == service_type:
            service_id = const.CITRIX_DATABASE_SERVICE_ID
            service_name = const.CITRIX_DATABASE_SERVICE_NAME
            service_version = const.CITRIX_DATABASE_SERVICE_VERSION
            service_port = const.CITRIX_DATABASE_SERVICE_PORT

        elif const.RDB_SERVICE_TYPE == service_type:
            service_version = const.RDB_SERVICE_VERSION
            service_port = const.RDB_SERVICE_PORT

        elif const.CACHE_SERVICE_TYPE == service_type:
            service_version = const.CACHE_SERVICE_VERSION
            service_port = const.CACHE_SERVICE_PORT

        elif const.AD_SERVICE_TYPE == service_type:
            service_id = const.AD_SERVICE_ID
            service_name = const.AD_SERVICE_NAME
            service_version = const.AD_SERVICE_VERSION
            service_port = const.AD_SERVICE_PORT

        elif const.S2SERVER_SERVICE_TYPE == service_type:
            service_version = const.S2SERVER_SERVICE_VERSION
            service_port = const.S2SERVER_SERVICE_PORT

        elif const.LOADBALANCER_SERVICE_TYPE == service_type:
            service_version = const.LOADBALANCER_SERVICE_VERSION
            service_port = const.LOADBALANCER_SERVICE_PORT

        else:
            logger.error("service type %s don't support" % service_type)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESKTOP_SERVICE_INSTANCE_SERVICE_TYPE_ERRORED, service_type)

        for service_nodes in service_nodes_list:
            service_node_id = service_nodes.get("service_node_id")
            service_node_ip = service_nodes.get("service_node_ip")
            service_ip = service_nodes.get("service_ip")

            desktop_service_management = {}
            desktop_service_management["service_node_id"] = service_node_id
            desktop_service_management["service_id"] = service_id
            desktop_service_management["service_name"] = service_name
            desktop_service_management["description"] = ""
            desktop_service_management["status"] = service_node_status
            desktop_service_management["service_version"] = service_version
            desktop_service_management["service_ip"] = service_ip
            desktop_service_management["service_node_status"] = service_node_status
            desktop_service_management["service_node_ip"] = service_node_ip
            desktop_service_management["service_node_type"] = const.MASTER_SERVICE_NODE_TYPE
            desktop_service_management["service_port"] = service_port
            desktop_service_management["service_type"] = service_type
            desktop_service_management["service_management_type"] = service_management_type
            if const.CITRIX_SERVICE_MANAGEMENT_TYPE == service_management_type:
                desktop_service_management["zone_id"] = sender["zone"]

            ret = ctx.pgm.get_desktop_service_managements(service_management_type=service_management_type,service_node_ids=service_node_id,service_ids=service_id)
            if ret:
                logger.error("desktop service instances already existed %s" % service_node_id)
                return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                             ErrorMsg.ERR_MSG_DESKTOP_SERVICE_INSTANCE_ALREADY_EXISTED, service_node_id)

            # register desktop_service_management
            if not ctx.pg.insert(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, desktop_service_management):
                logger.error("insert newly created desktop service management for [%s] to db failed" % (desktop_service_management))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CREATE_DESKTOP_SERVICE_MANAGEMENT_FAILED)

    return instance_ids

def get_target_host_name_by_target_host_ip(target_host_ip):
    ctx = context.instance()
    ret = ctx.pgm.get_desktop_service_managements(service_node_ips=target_host_ip)
    if not ret:
        return None

    desktop_service_managements = ret
    for service_node_id,desktop_service_management in desktop_service_managements.items():
        service_node_name = desktop_service_management.get("service_node_name")
        return service_node_name

    return None

def refresh_etc_hosts():

    ctx = context.instance()
    ret = ctx.pgm.get_desktop_service_managements(service_type=const.LOADBALANCER_SERVICE_TYPE)
    if not ret:
        return None

    desktop_service_managements = ret
    service_node_ip_list = []
    for service_node_id,desktop_service_management in desktop_service_managements.items():
        service_node_ip = desktop_service_management.get("service_node_ip")
        if service_node_ip not in service_node_ip_list:
            service_node_ip_list.append(service_node_ip)

    for service_node_ip in service_node_ip_list:
        for target_host_ip in service_node_ip_list:
            target_host_name = get_target_host_name_by_target_host_ip(target_host_ip)
            cmd = '''ssh -o StrictHostKeyChecking=no root@%s "sed -i 's/.*%s/%s %s/g' /etc/hosts"''' % (service_node_ip,target_host_name,target_host_ip,target_host_name)
            exec_cmd(cmd)

def update_loadbalancer_desktop_service_management(sender):

    ctx = context.instance()
    ret = ctx.pgm.get_desktop_service_managements(service_type=const.LOADBALANCER_SERVICE_TYPE)
    if not ret:
        return None

    desktop_service_managements = ret
    for service_node_id,desktop_service_management in desktop_service_managements.items():
        service_id = desktop_service_management.get("service_id")
        # get service_node_ip
        body = {}
        body["offset"] = 0
        body["limit"] = 1
        body["search_word"] = service_node_id
        ret = ctx.res.resource_describe_instances_by_search_word(sender["zone"], body)
        if not ret:
            continue
        private_ip = ''
        for _, instance in ret.items():
            vxnets = instance.get("vxnets")
            if vxnets:
                vxnet = vxnets[0]
                if vxnet:
                    private_ip = vxnet.get("private_ip", '')
            service_node_ip = private_ip
            if not service_node_ip:
                service_node_ip = desktop_service_management.get("service_node_ip")

            # get service_node_name
            ret = get_desktop_server_hostname(service_node_ip)
            if ret:
                service_node_name = ret
                # get service_node_version
                ret = get_desktop_server_version(service_node_ip)
                if ret:
                    service_node_version = ret
                    conditions = dict(
                        service_id=service_id,
                        service_node_id=service_node_id
                    )
                    update_desktop_service_management_info = dict(
                        service_node_ip=service_node_ip,
                        service_node_name=service_node_name,
                        service_node_version=service_node_version
                    )
                    logger.info("update_desktop_service_management_info == %s" % (update_desktop_service_management_info))
                    if not ctx.pg.base_update(dbconst.TB_DESKTOP_SERVICE_MANAGEMENT, conditions,update_desktop_service_management_info):
                        logger.error("modify desktop service management for [%s] to db failed" % (update_desktop_service_management_info))
                        return Error(ErrorCodes.INTERNAL_ERROR,
                                     ErrorMsg.ERR_MSG_MODIFY_DESKTOP_SERVICE_MANAGEMENT_FAILED)

    # refresh_etc_hosts
    # refresh_etc_hosts()

    return None