from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import db.constants as dbconst
import constants as const
from utils.misc import exec_cmd,_exec_cmd
from utils.net import get_hostname
from common import get_target_host_list

def configure_vdi_portal_url_prefix(url_prefix_value,reset_url_prefix=0):

    ctx = context.instance()
    hostname = get_hostname()
    target_host = None
    target_host_list = []
    num_of_desktop_server = 0

    ret = ctx.pgm.get_desktop_service_managements(service_type=const.LOADBALANCER_SERVICE_TYPE)
    if ret:
        num_of_desktop_server = len(ret)

    if num_of_desktop_server == 2:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_2
    elif num_of_desktop_server == 4:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_4
    elif num_of_desktop_server == 6:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_6
    elif num_of_desktop_server == 8:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_8
    else:
        target_host_list = const.NUM_OF_DESKTOP_SERVER_2

    logger.info("target_host_list == %s" %(target_host_list))
    for target_host in target_host_list:
        logger.info("target_host == %s" %(target_host))
        if not reset_url_prefix:
            cmd = '''ssh -o StrictHostKeyChecking=no root@%s "/pitrix/conf/configure_vdi_portal.sh -f Y -u %s -c y" ''' %(target_host,url_prefix_value)
            logger.info("cmd == %s" % (cmd))
            exec_cmd(cmd)
        else:
            cmd = '''ssh -o StrictHostKeyChecking=no root@%s "/pitrix/conf/configure_vdi_portal.sh -f N -c y" ''' % (target_host)
            logger.info("cmd == %s" % (cmd))
            exec_cmd(cmd)

    return True

def check_system_custom(sender):
    ctx = context.instance()

    ret = ctx.pgm.get_system_custom_id(current_system_custom=1)
    if ret is None:
        system_custom_id = const.DEFAULT_SYSTEM_CUSTOM
    else:
        system_custom_id = ret

    return system_custom_id

def parse_modify_contents(modify_contents):
    logger.info("parse_modify_contents modify_contents == %s" %(modify_contents))
    if not modify_contents:
        return None

    need_modify_contents = {}
    for modify_content in modify_contents:
        modify_content_list = modify_content.split("|")
        logger.info("modify_content_list == %s" %(modify_content_list))
        if len(modify_content_list) != 4:
            logger.error('modify system custom config count missing number parameter %s' % modify_content)
            return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_SYSTEM_CUSTOM_CONFIG_COUNT, modify_content)
        need_modify_contents[modify_content_list[1]] = dict(
            module_type=modify_content_list[0],
            item_key=modify_content_list[1],
            item_value=modify_content_list[2],
            enable_module=modify_content_list[3]
        )

    return need_modify_contents

def apply_url_prefix(system_custom_id, item_key,item_value):

    ctx = context.instance()
    url_prefix_old_item_value = ctx.pgm.get_url_prefix_item_value(system_custom_ids=system_custom_id, item_key=item_key)
    url_prefix_new_item_value = item_value
    ret = True

    if url_prefix_old_item_value != url_prefix_new_item_value:
        if url_prefix_new_item_value:
            ret = configure_vdi_portal_url_prefix(url_prefix_value=url_prefix_new_item_value,reset_url_prefix=0)
        else:
            ret = configure_vdi_portal_url_prefix(url_prefix_value=url_prefix_new_item_value,reset_url_prefix=1)

    return ret

def modify_system_custom_config(sender,system_custom_id,need_modify_contents):

    ctx = context.instance()
    # update system_custom_config
    for item_key, system_custom_config in need_modify_contents.items():

        module_type = system_custom_config.get("module_type")
        item_value = system_custom_config.get("item_value","")
        enable_module = system_custom_config.get("enable_module")

        if item_key == const.URL_PREFIX and ctx.zone_deploy == const.DEPLOY_TYPE_STANDARD:
            ret = apply_url_prefix(system_custom_id, item_key,item_value)
            if not ret:
                continue

        if item_key == const.URL_PREFIX and ctx.zone_deploy == const.DEPLOY_TYPE_EXPRESS:
            continue

        conditions = dict(
            system_custom_id=system_custom_id,
            module_type=module_type,
            item_key=item_key
        )

        update_system_custom_config_info = dict(
            item_value=item_value,
            enable_module=enable_module
        )

        if not ctx.pg.base_update(dbconst.TB_SYSTEM_CUSTOM_CONFIG, conditions, update_system_custom_config_info):
            logger.error("modify system custom config for [%s] to db failed" % (update_system_custom_config_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_MODIFY_SYSTEM_CUSTOM_CONFIG_FAILED)

    return None

def parse_reset_system_custom_config(module_type,item_key):

    ctx = context.instance()
    if not module_type:
        return None

    need_reset_system_custom_configs = None
    ret = ctx.pgm.get_system_custom_configs(system_custom_ids=const.DEFAULT_SYSTEM_CUSTOM,module_type=module_type,item_key=item_key)
    if not ret:
        return None
    need_reset_system_custom_configs = ret

    return need_reset_system_custom_configs

def reset_system_custom_configs(system_custom_id,need_reset_system_custom_configs):

    ctx = context.instance()
    zone_deploy = ctx.zone_deploy

    # update system_custom_config
    for item_key, system_custom_config in need_reset_system_custom_configs.items():
        module_type = system_custom_config.get("module_type")
        item_value = system_custom_config.get("item_value","")
        enable_module = system_custom_config.get("enable_module")

        if item_key == const.URL_PREFIX and ctx.zone_deploy == const.DEPLOY_TYPE_STANDARD:
            ret = apply_url_prefix(system_custom_id, item_key,item_value)

        if item_key == const.URL_PREFIX and ctx.zone_deploy == const.DEPLOY_TYPE_EXPRESS:
            item_value = ''

        conditions = dict(
            system_custom_id=system_custom_id,
            module_type=module_type,
            item_key=item_key
        )
        update_system_custom_config_info = dict(
            item_value=item_value,
            enable_module=enable_module
        )

        if not ctx.pg.base_update(dbconst.TB_SYSTEM_CUSTOM_CONFIG, conditions, update_system_custom_config_info):
            logger.error("modify system custom config for [%s] to db failed" % (update_system_custom_config_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_MODIFY_SYSTEM_CUSTOM_CONFIG_FAILED)

    return None

def format_system_customs(sender, system_custom_set, req):

    ctx = context.instance()
    module_type = req.get("module_type",None)
    for system_custom_id, _ in system_custom_set.items():

        # get system_custom_configs
        system_custom_configs = ctx.pgm.get_system_custom_configs(system_custom_ids=system_custom_id,module_type=module_type)
        if system_custom_configs:
            system_custom_set[system_custom_id]["system_custom_configs"] = system_custom_configs

    return system_custom_set

def refresh_ctx_system_custom_set(sender):

    ctx = context.instance()
    system_custom_set = {
                            'redefine_system_custom':
                                {
                                    'is_default': 0,
                                    'current_system_custom': 1,
                                    'system_custom_id': 'redefine_system_custom'
                                }
    }

    # format system_custom_set
    format_system_customs(sender, system_custom_set, {})
    ctx.system_custom_set = system_custom_set

def refresh_other_desktop_server_host_system_custom_configs_info():

    ctx = context.instance()
    target_hosts = get_target_host_list(ctx)
    current_hostname = get_hostname()
    if current_hostname in target_hosts:
        target_hosts.remove(current_hostname)

    rep = False
    for desktop_server_host in target_hosts:
        logger.info("desktop_server_host== %s" % (desktop_server_host))
        export_pythonpath_cmd = 'export PYTHONPATH="/pitrix/lib/pitrix-desktop-tools/apiserver:/pitrix/lib/pitrix-desktop-tools/common:${PYTHONPATH}"'
        cli_cmd = "/pitrix/lib/pitrix-desktop-tools/cli/bin/describe-system-custom-configs --force_refresh=1"
        cmd = "%s && %s" % (export_pythonpath_cmd, cli_cmd)
        logger.info("cmd == %s" % (cmd))
        ret = _exec_cmd(cmd=cmd, remote_host=desktop_server_host, ssh_port=22, timeout=3)
        if ret != None and ret[0] == 0:
            rep = True
        else:
            rep = False
            return rep

    return rep



