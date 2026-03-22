from log.logger import logger
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
import context
from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success
)
import db.constants as dbconst
import api.user.user as APIUser
import constants as const
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    PUBLIC_COLUMNS,
    DEFAULT_LIMIT,
)
import resource_control.desktop.resource_permission as ResCheck
import resource_control.component_version as ComponentVersion

def handle_describe_component_version(req):

    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_COMPONENT_VERSION)
    component_id = req.get("components")
    if component_id:
        filter_conditions["component_id"] = component_id

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_COMPONENT_VERSION]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_COMPONENT_VERSION]
    else:
        display_columns = PUBLIC_COLUMNS[dbconst.TB_COMPONENT_VERSION]

    component_version_set = ctx.pg.get_by_filter(dbconst.TB_COMPONENT_VERSION, filter_conditions, display_columns,
                                  sort_key = get_sort_key(dbconst.TB_COMPONENT_VERSION, req.get("sort_key")),
                                  reverse = get_reverse(req.get("reverse")),
                                  offset = req.get("offset", 0),
                                  limit = req.get("limit", DEFAULT_LIMIT),
                                  )

    if component_version_set is None:
        logger.error("describe component version failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # format component_version_set
    ComponentVersion.format_component_version(sender, component_version_set,verbose=1)

    # get total count
    total_count = len(component_version_set)
    if total_count is None:
        logger.error("get component version count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count}
    return return_items(req, component_version_set, "component_version", **rep)

def handle_update_component_version(req):

    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["component_id","component_name", "version", "filename","upgrade_packet_md5","upgrade_packet_size"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ComponentVersion.update_component_version(sender, req)
    if isinstance(ret, Error):
        return return_error(req, ret)
    component_ids = ret

    # # send component job
    job_uuid = None
    if component_ids:
        ret = ComponentVersion.send_desktop_component_job(sender, component_ids,const.JOB_ACTION_UPDATE_COMPONENT)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret

    return return_success(req, None, job_uuid)

def handle_execute_component_upgrade(req):

    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["component_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    component_ids = req.get("component_id")
    upgrade_hosts = req.get("upgrade_hosts",['vdi0','vdi1'])
    ret = ComponentVersion.check_execute_component_upgrade(sender, component_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    component_versions = ret

    job_uuid = None
    for component_id,component_version in component_versions.items():
        component_type = component_version.get("component_type")
        if component_type == const.COMPONENT_TYPE_CLIENT:

            # get url_prefix
            url_prefix=''
            system_custom_configs=ctx.pgm.get_system_custom_configs(system_custom_ids='redefine_system_custom',item_key='url_prefix')
            for item_key,system_custom_config in system_custom_configs.items():
                url_prefix = system_custom_config.get("item_value",'')

            terminal_ids=[]
            terminals = ctx.pgm.get_terminals(status=const.TERMINAL_STATUS_ACTIVE)
            if terminals:
                for terminal_id,terminal in terminals.items():
                    terminal_server_ip = terminal.get("terminal_server_ip")
                    if terminal_id not in terminal_ids:
                        terminal_ids.append(terminal_id)

                upgrade_packet_name = component_version.get("filename")
                upgrade_packet_md5 = component_version.get("upgrade_packet_md5")
                if url_prefix:
                    upgrade_packet_path = "http://%s/%s/softwares/mnt/nasdata/linux_client/%s" % (terminal_server_ip,url_prefix,upgrade_packet_name)
                else:
                    upgrade_packet_path = "http://%s/softwares/mnt/nasdata/linux_client/%s" % (terminal_server_ip,upgrade_packet_name)

                extra = {"upgrade_packet_name": upgrade_packet_name,
                         "upgrade_packet_path": upgrade_packet_path,
                         "upgrade_packet_md5": upgrade_packet_md5
                         }

                ret = ComponentVersion.update_component_status(component_ids, status=const.COMPONENT_STATUS_UPGRADING)
                if isinstance(ret, Error):
                    return return_error(req, ret)

                ret = ComponentVersion.send_desktop_terminal_job(sender, terminal_ids, const.JOB_ACTION_EXECUTE_CLIENT_COMPONENT_UPGRADE,extra)
                if isinstance(ret, Error):
                    return return_error(req, ret)
                job_uuid = ret

        elif component_type == const.COMPONENT_TYPE_SERVER:

            ret = ComponentVersion.update_component_status(component_ids,status=const.COMPONENT_STATUS_UPGRADING)
            if isinstance(ret, Error):
                return return_error(req, ret)

            extra = {"upgrade_hosts": upgrade_hosts}
            ret = ComponentVersion.send_desktop_component_job(sender, component_ids,const.JOB_ACTION_EXECUTE_SERVER_COMPONENT_UPGRADE,extra)
            if isinstance(ret, Error):
                return return_error(req, ret)
            job_uuid = ret
        else:
            logger.info("tools component %s not support upgrade" % (component_id))

    return return_success(req, None, job_uuid)