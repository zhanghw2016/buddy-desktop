'''
Created on 2017-3-8

@author: yunify
'''
from log.logger import logger
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from common import (
    return_success, return_error, return_items
)
from resource_control.user.system_config import (
        get_all_system_config,
        set_system_config,
)
from common import is_admin_user, is_global_admin_user, build_filter_conditions, get_sort_key, get_reverse
import context
import constants as const
import db.constants as dbconst
from utils.json import json_load

def handle_describe_system_config(req):
    ''' describe system config ''' 
    if not is_admin_user(req['sender']):
        logger.error("only global admin can modify system config.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    ret = get_all_system_config()
    if isinstance(ret, Error):
        return return_error(req, ret)

    system_config = ret
    keys = req.get("keys")
    if keys:
        for k in system_config.keys():
            if k not in keys:
                system_config.pop(k)

    rep = {'vdi_system_config_set': system_config}
    rep.update({'total_count': 1})

    return return_success(req, rep)

def handle_modify_system_config(req):
    ''' modify system config '''
    if not is_global_admin_user(req['sender']):
        logger.error("only global admin can modify system config.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    sysconf = json_load(req.get('config_items', ''))
    if sysconf is None:
        logger.error("sysconf is invalid.")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, 'config_items'))

    for key in sysconf.keys():
        if key not in const.VDI_SUPPORT_SYSTEM_CONFIG_ITEMS:
            continue

        ret = set_system_config(key, sysconf[key])
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_describe_base_system_config(req):
    ''' describe qingcloud access key config ''' 
    access_key_config = get_all_system_config(const.VDI_BASE_CONFIG_ITEMS)
    if isinstance(access_key_config, Error):
        return return_error(req, access_key_config)

    rep = {'base_system_config_set': [access_key_config]}
    rep.update({'total_count': 1})

    return return_success(req, rep)


def handle_describe_desktop_system_logs(req):
    ''' describe system logs '''
    ctx = context.instance()

    # check must parameters
    filter_conditions = build_filter_conditions(req, dbconst.TB_VDI_SYSTEM_LOG)
    if "system_log_ids" in req:
        filter_conditions.update({'system_log_id':req["system_log_ids"]})

    if not is_global_admin_user(req['sender']):
        filter_conditions.update({'user_id': req['sender']['owner']})

    display_columns = dbconst.PUBLIC_COLUMNS[dbconst.TB_VDI_SYSTEM_LOG]
    
    system_log_set = ctx.pg.get_by_filter(dbconst.TB_VDI_SYSTEM_LOG, filter_conditions, display_columns, 
                                    sort_key = get_sort_key(dbconst.TB_VDI_SYSTEM_LOG, req.get("sort_key")),
                                    reverse = get_reverse(req.get("reverse")),
                                    offset = req.get("offset", 0),
                                    limit = req.get("limit", dbconst.DEFAULT_LIMIT),
                                    )
    if system_log_set is None:
        logger.error("describe system log failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_VDI_SYSTEM_LOG, filter_conditions)
    if total_count is None:
        logger.error("get system log count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    rep = {'total_count':total_count}

    return return_items(req, system_log_set, "system_log", **rep)

def handle_modify_approvalnotice_config(req):
    ''' modify approvalnotice config '''
    if not is_global_admin_user(req['sender']):
        logger.error("only global admin can modify system config.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))
    
    sysconf = {}
    sysconf['approval_notice'] = req.get('approval_notice', '')
    sysconf['approval_notice_title'] = req.get('approval_notice_title', '')

    for key in sysconf.keys():
        ret = set_system_config(key, sysconf[key])
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, sysconf)

def handle_describe_approvalnotice_config(req):
    ''' describe approvalnotice server config ''' 
    approvalnotice_config = get_all_system_config(const.VDI_APPROVALNOTICE_CONFIG_ITEMS)
    if isinstance(approvalnotice_config, Error):
        return return_error(req, approvalnotice_config)
    if approvalnotice_config is None :
        approvalnotice_config = {}

    rep = {'approvalnotice_config_set': [approvalnotice_config]}
    rep.update({'total_count': 1})

    return return_success(req, rep)
