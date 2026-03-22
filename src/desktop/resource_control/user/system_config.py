'''
Created on 2012-10-17

@author: yunify
'''
import context
from db.constants import (
    TB_VDI_SYSTEM_CONFIG,
    TB_VDI_SYSTEM_LOG,
)
from utils.misc import get_current_time
from utils.id_tool import UUID_TYPE_VDI_SYSTEM_LOG, get_uuid
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from log.logger import logger

def get_all_system_config(config_keys=[]):

    sysconfig = {}
    ctx = context.instance()
    try:
        result = ctx.pg.base_get(TB_VDI_SYSTEM_CONFIG)
        if result is None:
            logger.error("get all system config from table [%s] failed" % TB_VDI_SYSTEM_CONFIG)
            return Error(ErrorCodes.DESCRIBE_SYSTEM_CONDIF_ERROR,
                         ErrorMsg.ERR_MSG_DESCRIBE_SYSTEM_CONDIF_ERROR)

        for item in result:
            if len(config_keys) == 0 or (item['config_key'] in config_keys):
                sysconfig[item['config_key']] = item['config_value']

        return sysconfig
    except Exception, e:
        logger.error("get all system config with Exception:%s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                     ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def system_config_key_exists(config_key):
    ''' get system config '''
    ctx = context.instance()
    try:
        result = ctx.pg.base_get(TB_VDI_SYSTEM_CONFIG, {'config_key': config_key})
        if result == None or len(result) == 0:
            return False

        return True
    except Exception, e:
        logger.error("get system config with Exception:%s" % e)
        return False

def set_system_config(config_key, config_value):
    ''' set system config '''
    try:
        # modify
        ctx = context.instance()
        ret = system_config_key_exists(config_key)
        if ret:
            if ctx.pg.base_update(TB_VDI_SYSTEM_CONFIG, {'config_key': config_key}, {'config_value': config_value}) < 0:
                logger.error("modify system config item with error, [key: %s, value: %s]." % (config_key, config_value))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_SYSTEM_CONDIF_ERROR)
        else:
            if ctx.pg.insert(TB_VDI_SYSTEM_CONFIG, {'config_key': config_key, 'config_value': config_value}) < 0:
                logger.error("add system config item with error, [config_key: %s, value: %s]." % (config_key, config_value))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_MODIFY_SYSTEM_CONDIF_ERROR)
        return config_key
    except Exception, e:
        logger.error("modify system config with Exception:%s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                     ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def delete_system_config_key(config_key):
    try:
        ctx = context.instance()
        if ctx.pg.base_delete(TB_VDI_SYSTEM_CONFIG, {'config_key': config_key}) < 0:
            return False
        return True
    except Exception, e:
        logger.error("delete system config key with Exception:%s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                     ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def get_sysconfig_auth_type():
    ctx = context.instance()
    auth_type = ctx.pgm.get_system_config('auth_type')
    if isinstance(auth_type, Error):
        return None

    return auth_type

def add_system_log(log):
    ctx = context.instance()
    
    curtime = get_current_time(to_seconds=False)
    log_id = get_uuid(UUID_TYPE_VDI_SYSTEM_LOG, 
                      ctx.checker, 
                      long_format=True)
    log['create_time'] = curtime
    log['system_log_id'] = log_id
    
    try:
        if not ctx.pg.insert(TB_VDI_SYSTEM_LOG, log):
            logger.error("add log [%s] failed." % (log))
            return Error(ErrorCodes.ADD_SYSTEM_LOG_ERROR,
                         ErrorMsg.ERR_MSG_ADD_SYSTEM_LOG_ERROR)

        return log_id
    except Exception,e:
        logger.error("add system log with Exception: %s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)
    
