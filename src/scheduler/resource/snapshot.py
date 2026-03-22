
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import context
import constants as const
from schetask_common import (
    no_task_resource,
    desktop_no_instance,
    disk_no_volume,
    no_task_param,
    parse_python_data,
    return_none,
    update_task_resource_info,
    clear_task_resource_info
)
from utils.id_tool import(
    UUID_TYPE_DESKTOP,
    UUID_TYPE_DESKTOP_DISK
)
import time
from common import check_resource_transition_status

def task_check_snapshot_group_resource(snapshot_group_id):

    ctx = context.instance()

    snapshot_group = ctx.pgm.get_snapshot_groups(snapshot_group_ids=snapshot_group_id)
    if not snapshot_group:
        logger.error("scheTask no found snapshot group resource %s " %(snapshot_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, snapshot_group_id)
    snapshot_resource = ctx.pgm.get_snapshot_group_resources(snapshot_group_id=snapshot_group_id)
    if not snapshot_resource:
        logger.error("scheTask no found snapshot resource %s " %(snapshot_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, snapshot_group_id)

    # check snapshot grouup transition status
    ret = check_resource_transition_status(snapshot_group)
    if isinstance(ret, Error):
        return ret

    return snapshot_group

def task_handle_auto_snapshot(scheduler_task):
    ctx = context.instance()

    task_type = scheduler_task["task_type"]
    scheduler_task_id = scheduler_task["scheduler_task_id"]
    task_resources = ctx.pgm.get_scheduler_task_resource(scheduler_task_id)
    if not task_resources:
        return 0

    task_result = {}
    resource_job = {}
    snapshot_group_ids = task_resources.keys()

    for snapshot_group_id in snapshot_group_ids:
        task_result[snapshot_group_id] = ''

        # check snapshot group available
        ret = task_check_snapshot_group_resource(snapshot_group_id)
        if isinstance(ret, Error):
            message = {
                "ret_code": ret.get_code(),
                "message": ret.get_message()
            }
            task_result[snapshot_group_id] = message
            continue

        snapshot_groups = ret
        for _,snapshot_group in snapshot_groups.items():
            zone = snapshot_group["zone"]

        # handle task
        if task_type == const.SCHETASK_TYPE_AUTO_SNAPSHOT:
            job_id = ''
            task_resource = task_resources[snapshot_group_id]
            task_param = task_resource["task_param"]
            if not task_param:
                task_result[snapshot_group_id] = no_task_param(scheduler_task_id, snapshot_group_id)
                time.sleep(3)
                continue

            task_param = parse_python_data(task_param)
            is_full = task_param["is_full"]
            ret = ctx.res.resource_create_desktop_snapshots(zone, snapshot_group_id,is_full=is_full)
            if ret is None:
                message = return_none(snapshot_group_id, const.ACTION_VDI_CREATE_DESKTOP_SNAPSHOTS)
                task_result[snapshot_group_id] = message
            else:
                task_result[snapshot_group_id] = ret
                job_id = ret.get("job_id")
                if job_id:
                    resource_job[snapshot_group_id] = job_id
            ret = update_task_resource_info(scheduler_task_id, snapshot_group_id, job_id, ret)

        time.sleep(3)

    # wait task job
    if resource_job:
        job_ids = resource_job.values()
        ctx.res.resource_wait_desktop_jobs_done(zone, job_ids)

    # clear task resource info
    ret = clear_task_resource_info(scheduler_task_id, snapshot_group_ids)

    # return task result
    return task_result
        
        
        
    