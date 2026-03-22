from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import context

import time
import constants as const
from common import (
    check_resource_transition_status,
    is_citrix_platform
)
from schetask_common import (
    no_task_param,
    parse_python_data,
    return_none,
    update_task_resource_info,
    clear_task_resource_info
)

def task_check_desktop_group_resource(desktop_group_id):
    
    ctx = context.instance()

    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
    if not desktop_group:
        logger.error("scheTask no found desktop group resource %s " % desktop_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_group_id)
    
    # check desktop grouup transition status
    ret = check_resource_transition_status({desktop_group_id: desktop_group})
    if isinstance(ret, Error):
        return ret
    
    desktops = desktop_group["desktops"]
    if not desktops:
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_NO_DESKTOP_IN_DESKTOP_GROUP, desktop_group_id)

    ret = check_resource_transition_status(desktops)
    if isinstance(ret, Error):
        logger.error("scheTask desktop resource %s in trans status" % desktops.keys())
        return ret
    
    return desktop_group

def task_handle_desktop_groups(scheduler_task):

    ctx = context.instance()
    
    task_type = scheduler_task["task_type"]
    
    scheduler_task_id = scheduler_task["scheduler_task_id"]
    task_resources = ctx.pgm.get_scheduler_task_resource(scheduler_task_id)
    if not task_resources:
        return 0
    
    task_result = {}
    resource_job = {}
    dg_status = {}
    
    desktop_group_ids = task_resources.keys()

    for desktop_group_id in desktop_group_ids:
        
        task_result[desktop_group_id] = ''
        
        # check desktop group available
        ret = task_check_desktop_group_resource(desktop_group_id)
        if isinstance(ret, Error):
            
            message = {
                    "ret_code": ret.get_code(),
                    "message": ret.get_message()
                    }            
            task_result[desktop_group_id] = message
            continue
        
        desktop_group = ret
        zone = desktop_group["zone"]
        # check desktop group status
        status = desktop_group["status"]
        if status == const.DESKTOP_GROUP_STATUS_NORMAL and not is_citrix_platform(ctx, zone):
            ret = ctx.res.resource_modify_desktop_group_status(zone, desktop_group_id, const.DESKTOP_GROUP_STATUS_MAINT)
            if ret is None:
                message = return_none(desktop_group_id, const.ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES)
                task_result[desktop_group_id] = message
                continue
            
            task_result[desktop_group_id] = ret
            dg_status[desktop_group_id] = const.DESKTOP_GROUP_STATUS_NORMAL
        
        # handle task
        if task_type == const.SCHETASK_TYPE_RESTART_DG:
            
            job_id = ''
            ret = ctx.res.resource_restart_desktops(zone, desktop_group_id)
            if ret is None:
                message = return_none(desktop_group_id, const.ACTION_VDI_RESTART_DESKTOPS)
                task_result[desktop_group_id] = message
            else:
                task_result[desktop_group_id] = ret
                job_id = ret.get("job_id")
                if job_id:
                    resource_job[desktop_group_id] = job_id
            
            update_task_resource_info(scheduler_task_id, desktop_group_id, job_id, ret)
            
        elif task_type == const.SCHETASK_TYPE_START_DG:
            
            job_id = ''

            ret = ctx.res.resource_start_desktops(zone, desktop_group_id)
            if ret is None:
                message = return_none(desktop_group_id, const.ACTION_VDI_START_DESKTOPS)
                task_result[desktop_group_id] = message
            else:
                task_result[desktop_group_id] = ret
                job_id = ret.get("job_id")
                if job_id:
                    resource_job[desktop_group_id] = job_id
            
            update_task_resource_info(scheduler_task_id, desktop_group_id, job_id, ret)

        elif task_type == const.SCHETASK_TYPE_STOP_DG:
            job_id = ''

            ret = ctx.res.resource_stop_desktops(zone, desktop_group_id)
            if ret is None:
                message = return_none(desktop_group_id, const.ACTION_VDI_STOP_DESKTOPS)
                task_result[desktop_group_id] = message
            else:
                task_result[desktop_group_id] = ret
                job_id = ret.get("job_id")
                if job_id:
                    resource_job[desktop_group_id] = job_id

            update_task_resource_info(scheduler_task_id, desktop_group_id, job_id, ret)
        
        elif task_type == const.SCHETASK_TYPE_MODIFY_DG_COUNT:
            task_resource = task_resources[desktop_group_id]
            task_param = task_resource["task_param"]
            if not task_param:
                task_result[desktop_group_id] = no_task_param(scheduler_task_id, desktop_group_id)
                time.sleep(3)
                continue
    
            task_param = parse_python_data(task_param)
            desktop_count = task_param["desktop_count"]
            
            ret = ctx.res.resource_modify_desktop_group_attributes(zone, desktop_group_id, desktop_count=desktop_count)
            if ret is None:
                message = return_none(desktop_group_id, const.ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES)
                task_result[desktop_group_id] = message
            else:
                
                task_result[desktop_group_id] = ret
                ret = ctx.res.resource_apply_desktop_group(zone, desktop_group_id)
                if ret is None:
                    message = return_none(desktop_group_id, const.ACTION_VDI_APPLY_DESKTOP_GROUP)
                    task_result[desktop_group_id] = message
                else:
                    task_result[desktop_group_id] = ret
                    job_id = ret.get("job_id")
                    if job_id:
                        resource_job[desktop_group_id] = job_id
        
        elif task_type == const.SCHETASK_TYPE_UPDATE_DESKTOP_IMAGE:

            task_resource = task_resources[desktop_group_id]
            task_param = task_resource["task_param"]
            if not task_param:
                task_result[desktop_group_id] = no_task_param(scheduler_task_id, desktop_group_id)
                time.sleep(3)
                continue
            
            task_param = parse_python_data(task_param)
            desktop_image = task_param.get("desktop_image")
            if not desktop_image:
                task_result[desktop_group_id] = no_task_param(scheduler_task_id, desktop_group_id)
                time.sleep(3)
                continue
            
            ret = ctx.res.resource_modify_desktop_group_attributes(zone, desktop_group_id, desktop_image=desktop_image)
            if ret is None:
                message = return_none(desktop_group_id, const.ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES)
                task_result[desktop_group_id] = message
            else:
                
                task_result[desktop_group_id] = ret
                ret = ctx.res.resource_apply_desktop_group(zone, desktop_group_id)
                if ret is None:
                    message = return_none(desktop_group_id, const.ACTION_VDI_APPLY_DESKTOP_GROUP)
                    task_result[desktop_group_id] = message
                else:
                    task_result[desktop_group_id] = ret
                    job_id = ret.get("job_id")
                    if job_id:
                        resource_job[desktop_group_id] = job_id

        time.sleep(3)
    
    # wait task job
    if resource_job:
        job_ids = resource_job.values()
        ctx.res.resource_wait_desktop_jobs_done(zone, job_ids)

    # modify desktop group status
    if dg_status:
        for desktop_group_id, status in dg_status.items():
            ret =ctx.res.resource_modify_desktop_group_status(zone, desktop_group_id, status)
            if ret is None:
                message = return_none(desktop_group_id, const.ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES)
                task_result[desktop_group_id] = message
    
    # clear task resource info
    clear_task_resource_info(scheduler_task_id, desktop_group_ids)
    
    # return task result
    return task_result
