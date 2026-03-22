from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
from utils.id_tool import(
    UUID_TYPE_TERMINAL,
    UUID_TYPE_TERMINAL_GROUP
)
import constants as const
from utils.id_tool import(
    get_uuid
)
import time
from utils.misc import get_current_time,exec_cmd
import api.user.user as APIUser
import os
import resource_control.desktop.job as Job
from utils.net import get_hostname

def send_desktop_terminal_job(sender, terminal_ids, action, extra=None):

    if not isinstance(terminal_ids, list):
        terminal_ids = [terminal_ids]

    directive = {
        "sender": sender,
        "action": action,
        "terminal_id": terminal_ids,
    }
    if extra:
        directive.update(extra)

    ret = Job.submit_desktop_job(action, directive, terminal_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

def modify_terminal_management_attributes(terminal_id, need_maint_columns):

    ctx = context.instance()
    terminals = ctx.pgm.get_terminals(terminal_ids=terminal_id)
    if not terminals:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, terminal_id)

    condition = {"terminal_id": terminal_id}
    if not ctx.pg.base_update(dbconst.TB_TERMINAL_MANAGEMENT,condition, need_maint_columns):
        logger.error("modify terminal update DB fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def check_terminal_vaild(terminal_ids=None, status=None):

    ctx = context.instance()
    if terminal_ids and not isinstance(terminal_ids, list):
        terminal_ids = [terminal_ids]

    if status and not isinstance(status, list):
        status = [status]

    terminals = {}
    terminals = ctx.pgm.get_terminals(terminal_ids=terminal_ids)

    if not terminals:
        logger.error("check terminal, no found terminal %s" % terminal_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, terminal_ids)

    else:
        if terminal_ids:
            for terminal_id in terminal_ids:
                if terminal_id not in terminals:
                    logger.error("check terminal, no found terminal %s" % terminal_id)
                    return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                                 ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, terminal_id)

    # check terminal status
    if status:
        for terminal_id, terminal in terminals.items():
            terminal_status = terminal["status"]
            if terminal_status not in status:
                logger.error("terminal %s status %s invaild " % (terminal_id, terminal_status))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_TERMINAL_STATUS_DISMATCH, (terminal_id, status))

    return terminals

def delete_terminal_managements(terminals):

    ctx = context.instance()
    for terminal_id, terminal in terminals.items():
        conditions = {"terminal_id": terminal_id}
        ctx.pg.base_delete(dbconst.TB_TERMINAL_MANAGEMENT, conditions)

    return None

def get_terminal_mac(terminal_ids):

    ctx = context.instance()

    terminals = ctx.pgm.get_terminals(terminal_ids=terminal_ids)
    if not terminals:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, terminal_ids)
    terminal_macs = []
    for terminal_id,terminal in terminals.items():
        terminal_mac = terminal["terminal_mac"]
        if terminal_mac not in terminal_macs:
            terminal_macs.append(terminal_mac)

    return terminal_macs


def register_terminal_group(sender, terminal_group_name, description=None):

    ctx = context.instance()
    new_terminal_group = {}
    terminal_group_id = get_uuid(UUID_TYPE_TERMINAL_GROUP, ctx.checker)
    terminal_group_info = dict(
        terminal_group_id=terminal_group_id,
        terminal_group_name=terminal_group_name,
        create_time=get_current_time(False),
        description=description if description else ''
    )
    new_terminal_group[terminal_group_id] = terminal_group_info
    if not ctx.pg.batch_insert(dbconst.TB_TERMINAL_GROUP, new_terminal_group):
        logger.error("insert newly created terminal group [%s] to db failed" % (new_terminal_group))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_TERMINAL_GROUP_FAILED)

    return terminal_group_id

def check_terminal_group_name(terminal_group_name):

    ctx = context.instance()
    ret = ctx.pgm.get_terminal_group_name()
    if not ret:
        return terminal_group_name

    if terminal_group_name.upper() in ret:
        logger.error("terminal group name already existd %s" % terminal_group_name)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_TERMINAL_GROUP_NAME_ALREADY_EXISTED, terminal_group_name)
    return terminal_group_name

def modify_terminal_group(terminal_group_id, terminal_group_name, description):

    ctx = context.instance()
    ret = ctx.pgm.get_terminal_groups(terminal_group_ids=terminal_group_id)
    if not ret:
        logger.error("terminal group no found %s" % terminal_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_TERMINAL_GROUP_NO_FOUND, terminal_group_id)
    terminal_groups = ret

    terminal_group = terminal_groups[terminal_group_id]
    if terminal_group_name is None and description is None:
        return None
    else:
        if terminal_group_name == terminal_group["terminal_group_name"] and description == terminal_group["description"]:
            return None

    update_terminal_group = {}
    terminal_group_info = dict(
        terminal_group_name=terminal_group_name,
        description=description if description else '',
    )
    update_terminal_group[terminal_group_id] = terminal_group_info
    if not ctx.pg.batch_update(dbconst.TB_TERMINAL_GROUP, update_terminal_group):
        logger.error("modify terminal group update db fail %s" % update_terminal_group)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_TERMINAL_GROUP_FAILED)

    return None

def delete_terminal_groups(terminal_group_id):

    ctx = context.instance()
    ret = ctx.pgm.get_terminal_groups(terminal_group_ids=terminal_group_id)
    if not ret:
        logger.error("terminal group no found %s" % terminal_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_TERMINAL_GROUP_NO_FOUND, terminal_group_id)
    terminal_groups = ret

    # delete terminal_group and terminal_group_terminal db
    for terminal_group_id, _ in terminal_groups.items():
        if not ctx.pg.delete(dbconst.TB_TERMINAL_GROUP_TERMINAL, terminal_group_id):
            logger.error("delete terminal group resource %s fail" % terminal_group_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_TERMINAL_GROUP_RESOURCE_FAILED,terminal_group_id)

        if not ctx.pg.delete(dbconst.TB_TERMINAL_GROUP, terminal_group_id):
            logger.error("delete terminal group %s fail" % terminal_group_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_TERMINAL_GROUP_FAILED,terminal_group_id)

        terminals = ctx.pgm.get_terminals(terminal_group_id=terminal_group_id)
        if not terminals:
            continue
        for terminal_id, _ in terminals.items():
            update_terminal = {}
            terminal_info = dict(
                terminal_group_id=""
            )
            update_terminal[terminal_id] = terminal_info
            if not ctx.pg.batch_update(dbconst.TB_TERMINAL_MANAGEMENT, update_terminal):
                logger.error("modify terminal update db fail %s" % update_terminal)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_TERMINAL_FAILED,terminal_id)

    return None

def check_terminal_valid(sender, terminal_ids=None):

    ctx = context.instance()
    for terminal_id in terminal_ids:
        terminals = ctx.pgm.get_terminals(terminal_ids=terminal_id)
        if not terminals:
            logger.error("terminal %s no found" % terminal_id)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_TERMINAL_NO_FOUND, terminal_id)
    return None

def check_terminal_group(sender, terminal_group_ids=None):

    ctx = context.instance()
    if terminal_group_ids and not isinstance(terminal_group_ids, list):
        terminal_group_ids = [terminal_group_ids]

    for terminal_group_id in terminal_group_ids:
        terminal_groups = ctx.pgm.get_terminal_groups(terminal_group_ids=terminal_group_id)
        if not terminal_groups:
            logger.error("terminal groups %s no found" % (terminal_group_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_TERMINAL_GROUP_NO_FOUND, terminal_group_id)
    return None

def add_terminal_to_terminal_group(terminal_group_id, terminal_ids):

    ctx = context.instance()
    existed_terminal_ids = []
    ret = ctx.pgm.get_terminal_group_terminals(terminal_group_id=terminal_group_id, terminal_ids=terminal_ids)
    if ret:
        terminal_group_terminals = ret
        for terminal_id,_ in terminal_group_terminals.items():
            existed_terminal_ids.append(terminal_id)
        logger.error("add terminal to terminal_group %s, terminal %s existed" % (terminal_group_id, existed_terminal_ids))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_TERMINAL_ALREAY_EXISTED_TERMINAL_GROUP, (existed_terminal_ids, terminal_group_id))

    new_terminal_group_terminal_info = {}
    for terminal_id in terminal_ids:

        #update terminal_management db terminal_group_id value
        update_terminal = {}
        terminal_info = dict(
            terminal_group_id=terminal_group_id
        )
        update_terminal[terminal_id] = terminal_info
        if not ctx.pg.batch_update(dbconst.TB_TERMINAL_MANAGEMENT, update_terminal):
            logger.error("modify terminal update db fail %s" % update_terminal)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_MODIFY_TERMINAL_FAILED, terminal_id)

        # update terminal_group_terminal db
        terminal_group_terminal_info = dict(
                            terminal_group_id=terminal_group_id,
                            terminal_id = terminal_id,
                            create_time=get_current_time(False)
                         )
        new_terminal_group_terminal_info[terminal_id] = terminal_group_terminal_info

    if not ctx.pg.batch_insert(dbconst.TB_TERMINAL_GROUP_TERMINAL, new_terminal_group_terminal_info):
        logger.error("insert newly created terminal_group terminal [%s] to db failed" % (terminal_group_terminal_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_ADD_TERMINAL_GROUP_TERMINAL_FAILED)

    return None

def delete_terminal_from_terminal_group(terminal_group_id, terminal_ids):

    ctx = context.instance()
    ret = ctx.pgm.get_terminal_group_terminals(terminal_group_id=terminal_group_id, terminal_ids=terminal_ids)
    if not ret:
        logger.error("delete terminal from terminal_group %s, terminal %s not exist" % (terminal_group_id, terminal_ids))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_TERMINAL_NOT_IN_TERMINAL_GROUP, (terminal_ids, terminal_group_id))

    delete_terminal_group_terminal_info = {}
    for terminal_id in terminal_ids:
        delete_terminal_group_terminal_info = dict(
                                terminal_group_id=terminal_group_id,
                                terminal_id=terminal_id
                                )
        if not ctx.pg.base_delete(dbconst.TB_TERMINAL_GROUP_TERMINAL, delete_terminal_group_terminal_info):
            logger.error("delete terminal_group terminal [%s] to db failed" % (terminal_id))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_TERMINAL_GROUP_TERMINAL_FAILED,terminal_id)

        update_terminal = {}
        terminal_info = dict(
            terminal_group_id=""
        )
        update_terminal[terminal_id] = terminal_info
        if not ctx.pg.batch_update(dbconst.TB_TERMINAL_MANAGEMENT, update_terminal):
            logger.error("modify terminal update db fail %s" % update_terminal)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_MODIFY_TERMINAL_FAILED,terminal_id)


    return None

def format_terminal_groups(sender, terminal_group_set, verbose=0):

    ctx = context.instance()
    for terminal_group_id, _ in terminal_group_set.items():
        if verbose:
            ret = ctx.pgm.get_terminal_group_terminal_detail(terminal_group_id)
            if ret:
                terminal_group_set[terminal_group_id] = ret

        # get terminal_group terminal_total_count
        ret = ctx.pgm.get_terminal_group_terminals(terminal_group_id=terminal_group_id)
        if ret is None:
            terminal_total_count = 0
        else:
            terminal_total_count = len(ret)
        terminal_group_set[terminal_group_id]["terminal_total_count"] = terminal_total_count

        # get terminal_group terminal_online_count
        ret = ctx.pgm.get_terminals(terminal_group_id=terminal_group_id,status=const.TERMINAL_STATUS_ACTIVE)
        if ret is None:
            terminal_online_count = 0
        else:
            terminal_online_count = len(ret)
        terminal_group_set[terminal_group_id]["terminal_online_count"] = terminal_online_count

    return terminal_group_set

def format_terminal_management(sender, terminal_management_set, filter_joined_terminal_group=0):

    ctx = context.instance()
    for terminal_id, _ in terminal_management_set.items():
        if filter_joined_terminal_group:
            ret = ctx.pgm.get_terminal_group_terminals(terminal_ids=terminal_id)
            if ret:
                del terminal_management_set[terminal_id]

    return terminal_management_set

def check_terminal_group_valid(terminal_ids):

    ctx = context.instance()
    if terminal_ids and not isinstance(terminal_ids, list):
        terminal_ids = [terminal_ids]
    terminal_group_ids = []

    for terminal_id in terminal_ids:
        terminal_group_terminals = ctx.pgm.get_terminal_group_terminals(terminal_ids=terminal_id)
        if not terminal_group_terminals:
            continue
        for terminal_id,terminal_group_terminal in terminal_group_terminals.items():
            terminal_group_id = terminal_group_terminal.get("terminal_group_id")
            if terminal_group_id not in terminal_group_ids:
                terminal_group_ids.append(terminal_group_id)

    return terminal_group_ids

def check_master_backup_ips(sender,instance_id=None):

    ctx = context.instance()
    vdi_ip = []
    body = {}
    offset = 0
    limit = const.MAX_LIMIT_PARAM

    body["offset"] = offset
    body["limit"] = limit
    body["search_word"] = instance_id

    ret = ctx.res.resource_describe_instances_by_search_word(sender["zone"], body)
    if ret:
        # add private_ip and eip_addr
        for _, instance in ret.items():
            vxnets = instance.get("vxnets")
            if vxnets:
                vxnet = vxnets[0]
                if vxnet:
                    private_ip = vxnet.get("private_ip", '')
                    if private_ip not in vdi_ip:
                        vdi_ip.append(private_ip)

            eip = instance.get("eip")
            if eip:
                eip_addr = eip.get("eip_addr")
                if eip_addr not in vdi_ip:
                    vdi_ip.append(eip_addr)

    return vdi_ip

def get_master_vdi_ip(local_hostname):

    ret = exec_cmd("cat /etc/hosts | grep %s | awk '{print $1}'" %(local_hostname))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_backup_vdi_ip(target_hostname):

    ret = exec_cmd("cat /etc/hosts | grep %s | awk '{print $1}'" %(target_hostname))
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def describe_master_backup_ips(sender):

    ctx = context.instance()
    zone_deploy = ctx.zone_deploy
    master_vdi_ip = []
    backup_vdi_ip = []
    backup_vdi2_ip = []
    backup_vdi3_ip = []
    backup_vdi4_ip = []
    backup_vdi5_ip = []
    backup_vdi6_ip = []
    backup_vdi7_ip = []

    if zone_deploy == const.DEPLOY_TYPE_STANDARD:
        desktop_service_managements = ctx.pgm.get_desktop_service_managements(service_type=const.LOADBALANCER_SERVICE_TYPE)
        if desktop_service_managements:
            service_node_ids = desktop_service_managements.keys()
            count = len(service_node_ids)
            if count == 2:
                master_vdi_ip = ctx.pgm.get_desktop_service_management_service_node_ip(service_type=const.LOADBALANCER_SERVICE_TYPE,service_node_name='vdi0')
                backup_vdi_ip = ctx.pgm.get_desktop_service_management_service_node_ip(service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi1')

            elif count == 4:
                master_vdi_ip = ctx.pgm.get_desktop_service_management_service_node_ip(service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi0')
                backup_vdi_ip = ctx.pgm.get_desktop_service_management_service_node_ip(service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi1')
                backup_vdi2_ip = ctx.pgm.get_desktop_service_management_service_node_ip(service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi2')
                backup_vdi3_ip = ctx.pgm.get_desktop_service_management_service_node_ip(service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi3')
            elif count == 6:
                master_vdi_ip = ctx.pgm.get_desktop_service_management_service_node_ip(
                    service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi0')
                backup_vdi_ip = ctx.pgm.get_desktop_service_management_service_node_ip(
                    service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi1')
                backup_vdi2_ip = ctx.pgm.get_desktop_service_management_service_node_ip(
                    service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi2')
                backup_vdi3_ip = ctx.pgm.get_desktop_service_management_service_node_ip(
                    service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi3')
                backup_vdi4_ip = ctx.pgm.get_desktop_service_management_service_node_ip(service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi4')
                backup_vdi5_ip = ctx.pgm.get_desktop_service_management_service_node_ip(service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi5')
            elif count == 8:
                master_vdi_ip = ctx.pgm.get_desktop_service_management_service_node_ip(
                    service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi0')
                backup_vdi_ip = ctx.pgm.get_desktop_service_management_service_node_ip(
                    service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi1')
                backup_vdi2_ip = ctx.pgm.get_desktop_service_management_service_node_ip(
                    service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi2')
                backup_vdi3_ip = ctx.pgm.get_desktop_service_management_service_node_ip(
                    service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi3')
                backup_vdi4_ip = ctx.pgm.get_desktop_service_management_service_node_ip(service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi4')
                backup_vdi5_ip = ctx.pgm.get_desktop_service_management_service_node_ip(service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi5')
                backup_vdi6_ip = ctx.pgm.get_desktop_service_management_service_node_ip(
                    service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi6')
                backup_vdi7_ip = ctx.pgm.get_desktop_service_management_service_node_ip(
                    service_type=const.LOADBALANCER_SERVICE_TYPE, service_node_name='vdi7')
            else:
                logger.error("desktop_service_managements loadbalancer service_node_ids count == %d is valid" %(count))

    elif zone_deploy == const.DEPLOY_TYPE_EXPRESS:
        local_hostname = get_hostname()
        if local_hostname.endswith(const.DESKTOP_SERVER_HOSTNAME_0):
            target_hostname = local_hostname.replace(const.DESKTOP_SERVER_HOSTNAME_0, const.DESKTOP_SERVER_HOSTNAME_1)

        if local_hostname.endswith(const.DESKTOP_SERVER_HOSTNAME_1):
            target_hostname = local_hostname.replace(const.DESKTOP_SERVER_HOSTNAME_1, const.DESKTOP_SERVER_HOSTNAME_0)

        ret = get_master_vdi_ip(local_hostname)
        if ret not in master_vdi_ip:
            master_vdi_ip.append(ret)

        ret = get_backup_vdi_ip(target_hostname)
        if ret not in backup_vdi_ip:
            backup_vdi_ip.append(ret)

    else:
        logger.error("invalid zone_deploy %s" % (zone_deploy))

    return (master_vdi_ip,backup_vdi_ip,backup_vdi2_ip,backup_vdi3_ip,backup_vdi4_ip,backup_vdi5_ip,backup_vdi6_ip,backup_vdi7_ip)

def get_cb0server_host():

    ret = exec_cmd("cat /pitrix/conf/desktop/cbserver_host | grep cb0")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def get_cb1server_host():

    ret = exec_cmd("cat /pitrix/conf/desktop/cbserver_host | grep cb1")
    (_,output,_) = ret
    if ret != None and ret[0] == 0:
        return output
    return None

def describe_cbserver_hosts(sender):

    ctx = context.instance()
    zone_deploy = ctx.zone_deploy
    cb0server_host = ''
    cb1server_host = ''

    if zone_deploy == const.DEPLOY_TYPE_STANDARD:
        system_custom_configs = ctx.pgm.get_system_custom_configs(system_custom_ids="redefine_system_custom",item_key="cbserver_host")
        if system_custom_configs:
            for _,system_custom_config in system_custom_configs.items():
                item_value = system_custom_config.get("item_value","")
                item_value_list = item_value.split(";")
                for cbserver_host_value in item_value_list:
                    if "cb0" in cbserver_host_value:
                        cb0server_host = cbserver_host_value
                    if "cb1" in cbserver_host_value:
                        cb1server_host = cbserver_host_value

    elif zone_deploy == const.DEPLOY_TYPE_EXPRESS:
        ret = get_cb0server_host()
        if ret:
            if ret not in cb0server_host:
                cb0server_host = ret

        ret = get_cb1server_host()
        if ret:
            if ret not in cb1server_host:
                cb1server_host = ret
    else:
        logger.error("invalid zone_deploy %s" % (zone_deploy))

    return (cb0server_host,cb1server_host)




