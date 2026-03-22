from log.logger import logger
from error.error import Error
import context
import time
import constants as const
from common import (
    check_resource_transition_status
)
from schetask_common import (
    return_none,
    update_task_resource_info,
    clear_task_resource_info
)

import ast
import traceback

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

def task_check_delivery_group_resource(delivery_group_id):
    
    ctx = context.instance()

    delivery_group = ctx.pgm.get_delivery_groups(delivery_group_id)
    if not delivery_group:
        return None
    
    desktops = ctx.pgm.get_desktops(delivery_group_id=delivery_group_id)
    if not desktops:
        return None

    ret = check_resource_transition_status(desktops)
    if isinstance(ret, Error):
        logger.error("scheTask desktop resource %s in trans status" % desktops.keys())
        return ret
    
    return desktops

def task_handle_delivery_groups(scheduler_task):

    ctx = context.instance()
    task_type = scheduler_task["task_type"]

    scheduler_task_id = scheduler_task["scheduler_task_id"]
    task_resources = ctx.pgm.get_scheduler_task_resource(scheduler_task_id)
    if not task_resources:
        return 0
    
    task_result = {}
    resource_job = {}
    
    delivery_group_ids = task_resources.keys()
    for delivery_group_id in delivery_group_ids:
        
        task_result[delivery_group_id] = ""
        
        # check desktop group available
        ret = task_check_delivery_group_resource(delivery_group_id)
        if isinstance(ret, Error):
            
            message = {
                    "ret_code": ret.get_code(),
                    "message": ret.get_message()
                    }            
            task_result[delivery_group_id] = message
            continue
        
        if not ret:
            continue
        
        desktops = ret
        zone = scheduler_task["zone"]
       
        # handle task
        if task_type == const.SCHETASK_TYPE_RESTART_DG:
            
            job_id = ''
            ret = ctx.res.resource_restart_desktops(zone, desktop_ids=desktops.keys())
            if ret is None:
                message = return_none(delivery_group_id, const.ACTION_VDI_RESTART_DESKTOPS)
                task_result[delivery_group_id] = message
            else:
                task_result[delivery_group_id] = ret
                job_id = ret.get("job_id")
                if job_id:
                    resource_job[delivery_group_id] = job_id
            
            update_task_resource_info(scheduler_task_id, delivery_group_id, job_id, ret)
            
        elif task_type == const.SCHETASK_TYPE_START_DG:
            
            job_id = ''

            ret = ctx.res.resource_start_desktops(zone, desktop_ids=desktops.keys())
            if ret is None:
                message = return_none(delivery_group_id, const.ACTION_VDI_START_DESKTOPS)
                task_result[delivery_group_id] = message
            else:
                task_result[delivery_group_id] = ret
                job_id = ret.get("job_id")
                if job_id:
                    resource_job[delivery_group_id] = job_id
            
            update_task_resource_info(scheduler_task_id, delivery_group_id, job_id, ret)

        elif task_type == const.SCHETASK_TYPE_STOP_DG:
            job_id = ''

            ret = ctx.res.resource_stop_desktops(zone, desktop_ids=desktops.keys())
            if ret is None:
                message = return_none(delivery_group_id, const.ACTION_VDI_STOP_DESKTOPS)
                task_result[delivery_group_id] = message
            else:
                task_result[delivery_group_id] = ret
                job_id = ret.get("job_id")
                if job_id:
                    resource_job[delivery_group_id] = job_id

            update_task_resource_info(scheduler_task_id, delivery_group_id, job_id, ret)

        time.sleep(3)
    
    # wait task job
    if resource_job:
        job_ids = resource_job.values()
        ctx.res.resource_wait_desktop_jobs_done(zone, job_ids)
    
    # clear task resource info
    clear_task_resource_info(scheduler_task_id, delivery_group_ids)
    
    # return task result
    return task_result
