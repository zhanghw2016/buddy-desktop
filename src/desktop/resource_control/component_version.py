from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
from utils.misc import get_current_time,exec_cmd
import resource_control.desktop.job as Job
import os
from common import (
    is_citrix_platform
)

def send_desktop_component_job(sender, component_ids, action, extra=None):

    if not isinstance(component_ids, list):
        component_ids = [component_ids]

    directive = {
        "sender": sender,
        "action": action,
        "component_id": component_ids,
    }
    if extra:
        directive.update(extra)

    ret = Job.submit_desktop_job(action, directive, component_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret
    return job_uuid

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

def update_component_version(sender, req):

    ctx = context.instance()
    component_id = req.get("component_id", "")
    component_versions = ctx.pgm.get_component_versions(component_ids=component_id)

    if component_versions is None or len(component_versions) == 0:
        update_info = dict(
            component_id = component_id,
            component_name = req.get("component_name", ""),
            version = req.get("version", ""),
            filename = req.get("filename", ""),
            upgrade_packet_md5 = req.get("upgrade_packet_md5", ""),
            upgrade_packet_size= req.get("upgrade_packet_size", ""),
            component_type = req.get("component_type", ""),
            description = req.get("description", ""),
            status=const.COMPONENT_STATUS_UPLOADING,
            need_upgrade=1,
            update_time = get_current_time(to_seconds=False),
            create_time=get_current_time(to_seconds=False)
        )
        if not ctx.pg.insert(dbconst.TB_COMPONENT_VERSION, update_info):
            logger.error("insert newly created component version for [%s] to db failed" % (update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    else:
        for component_id, _ in component_versions.items():
            condition = {"component_id": component_id}
            update_info = dict(
                component_name=req.get("component_name", ""),
                version=req.get("version", ""),
                filename=req.get("filename", ""),
                upgrade_packet_md5=req.get("upgrade_packet_md5", ""),
                upgrade_packet_size=req.get("upgrade_packet_size", ""),
                component_type=req.get("component_type", ""),
                description=req.get("description", ""),
                status=const.COMPONENT_STATUS_UPLOADING,
                need_upgrade=1,
                update_time=get_current_time(to_seconds=False)
            )
            if not ctx.pg.base_update(dbconst.TB_COMPONENT_VERSION, condition, update_info):
                logger.error("update component version for [%s] to db failed" % (update_info))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return component_id

def check_execute_component_upgrade(sender, component_ids):

    ctx = context.instance()
    ret = ctx.pgm.get_component_versions(component_ids=component_ids)
    if not ret:
        logger.error("component_versions no found %s" % component_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_COMPONET_NO_FOUND, component_ids)

    component_versions = ret

    return component_versions

def is_file_exist(component_upgrade_package_url):

    if not os.path.exists(component_upgrade_package_url):
        return False
    return True

def get_upgrade_hosts():

    ctx = context.instance()
    ret = ctx.pgm.get_desktop_service_managements(service_type=const.LOADBALANCER_SERVICE_TYPE)
    if not ret:
        return const.NUM_OF_DESKTOP_SERVER_2

    desktop_service_managements = ret
    service_node_name_list = const.NUM_OF_DESKTOP_SERVER_2
    for service_node_id, desktop_service_management in desktop_service_managements.items():
        service_node_name = desktop_service_management.get("service_node_name",'')
        if service_node_name:
            if service_node_name not in service_node_name_list:
                service_node_name_list.append(service_node_name)

    return service_node_name_list

def create_component_upgrade_package_root_dir(component_upgrade_package_root_dir):
    if not os.path.exists(component_upgrade_package_root_dir):
        os.system("mkdir -p %s && chmod -R 777 %s" %(component_upgrade_package_root_dir,component_upgrade_package_root_dir))
        return True
    return True

def format_component_version(sender, component_version_set,verbose):

    ctx = context.instance()

    if verbose:
        for component_id, component_version in component_version_set.items():

            filename = component_version["filename"]
            component_type = component_version["component_type"]

            if component_type == const.COMPONENT_TYPE_CLIENT:
                component_upgrade_package_url = "%s/%s" % (const.COMPONENT_TYPE_CLIENT_DIR, filename)
                component_upgrade_package_root_dir = "%s" % (const.COMPONENT_TYPE_CLIENT_DIR)

            elif component_type == const.COMPONENT_TYPE_TOOLS:
                component_upgrade_package_url = "%s/%s" % (const.COMPONENT_TYPE_TOOLS_DIR, filename)
                component_upgrade_package_root_dir = "%s" % (const.COMPONENT_TYPE_TOOLS_DIR)

            elif component_type == const.COMPONENT_TYPE_SERVER:
                component_upgrade_package_url = "%s/%s" % (const.COMPONENT_TYPE_SERVER_DIR, filename)
                component_upgrade_package_root_dir = "%s" % (const.COMPONENT_TYPE_SERVER_DIR)

            elif component_type == const.COMPONENT_TYPE_FILE_SHARE_TOOLS:
                component_upgrade_package_url = "%s/%s" % (const.COMPONENT_TYPE_FILE_SHARE_TOOLS_DIR, filename)
                component_upgrade_package_root_dir = "%s" % (const.COMPONENT_TYPE_FILE_SHARE_TOOLS_DIR)

            else:
                logger.error("invalid component_type %s" % (component_type))
                continue
            create_component_upgrade_package_root_dir(component_upgrade_package_root_dir)

            if is_file_exist(component_upgrade_package_url):
                component_upgrade_package_exist = 1
            else:
                component_upgrade_package_exist = 0

            component_version_set[component_id]["component_upgrade_package_url"] = component_upgrade_package_url
            component_version_set[component_id]["component_upgrade_package_exist"] = component_upgrade_package_exist
            #
            # if is_citrix_platform(ctx, sender["zone"]) and component_type == const.COMPONENT_TYPE_CLIENT:
            #     del component_version_set['compvn-default-client']

            if component_type == const.COMPONENT_TYPE_SERVER:
                upgrade_hosts = get_upgrade_hosts()
                component_version_set[component_id]["upgrade_hosts"] = upgrade_hosts

    return component_version_set

def update_component_status(component_ids,status=const.COMPONENT_STATUS_UPGRADING):

    ctx = context.instance()
    condition = {"component_id": component_ids}
    update_info = {"status": status,"need_upgrade":0}

    if not ctx.pg.base_update(dbconst.TB_COMPONENT_VERSION, condition, update_info):
        logger.error("update component version for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

