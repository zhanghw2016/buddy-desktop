from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import db.constants as dbconst
import ast
import traceback
from utils.json import json_dump
import context


def no_task_param(scheduler_task_id, resource_id):

    logger.error("schetask %s no specify task param [%s]" % (scheduler_task_id, resource_id))
    return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                 ErrorMsg.ERR_MSG_SCHETASK_NO_TASK_PARAM, (scheduler_task_id, resource_id))
    
def no_task_resource(scheduler_task_id):

    logger.error("scheTask no task resource [%s]" % (scheduler_task_id))
    return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                 ErrorMsg.ERR_MSG_SCHETASK_NO_TASK_RESOURCE, (scheduler_task_id))
    
def desktop_no_instance(desktop_id):

    logger.error("scheTask no task resource [%s]" % (desktop_id))
    return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                 ErrorMsg.ERR_MSG_DESKTOP_NO_INSTANCE_RESOURCE, (desktop_id))
    
def disk_no_volume(disk_id):

    logger.error("scheTask no task resource [%s]" % (disk_id))
    return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                 ErrorMsg.ERR_MSG_DISK_NO_VOLUME_RESOURCE, (disk_id))
    
def parse_python_data(string):
    try:
        return ast.literal_eval(string)
    except:
        logger.error('parse python data[%s] failed: %s',
                string, traceback.format_exc())
        return None

def return_none(resource_id, action):
    
    ret = {
            "ret_code": 5000,
            "message": "resource %s action %s API return none" % (resource_id, action)
            }

    return ret

def update_task_resource_info(scheduler_task_id, resource_id, job_id, ret_info):

    ctx = context.instance()
    
    if not job_id:
        job_id = ''
    
    conditions = {"scheduler_task_id": scheduler_task_id, "resource_id": resource_id}
    update_info = {"job_id": job_id}
    
    if ret_info:
        update_info["task_msg"] = json_dump(ret_info)

    if not ctx.pg.base_update(dbconst.TB_SCHEDULER_TASK_RESOURCE, conditions, update_info):
        logger.error("update desktop group info %s fail" % update_info)
        return -1
    
    return 0

def clear_task_resource_info(scheduler_task_id, resource_ids):

    ctx = context.instance()
    conditions = {"scheduler_task_id": scheduler_task_id, "resource_id": resource_ids}
    update_info = {"job_id": '', "task_msg": ''}

    if not ctx.pg.base_update(dbconst.TB_SCHEDULER_TASK_RESOURCE, conditions, update_info):
        logger.error("update desktop group info %s fail" % update_info)
        return -1
    
    return 0