import constants as const
from log.logger import logger
from utils.misc import get_current_time
import context
from utils.json import json_dump
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.id_tool import(
    UUID_TYPE_DESKTOP_JOB,
    get_uuid
)

from db.constants import TB_DESKTOP_JOB
from base_client import send_to_server
import datetime

def refresh_zombie_job():
    
    ctx = context.instance()
    
    jobs = ctx.pgm.get_desktop_jobs(status=[const.JOB_STATUS_PEND, const.JOB_STATUS_WORKING])
    if not jobs:
        return None
    
    refresh_jobs = {}
    for job_id, job in jobs.items():
        create_time = job.get("create_time")
        current_time = get_current_time()
        detla_time = datetime.timedelta(seconds=const.JOB_MAX_TIMEOUT*12)
        # request is expires if current_time greater than expires
        if create_time < current_time - detla_time:
            refresh_jobs[job_id] = {"status": const.JOB_STATUS_TIMEOUT}
    
    if refresh_jobs:
        ctx.pg.batch_update(TB_DESKTOP_JOB, refresh_jobs)
    
    return None

def new_desktop_job(action, directive, resource_ids):

    ctx = context.instance()
    job_uuid = get_uuid(UUID_TYPE_DESKTOP_JOB, ctx.checker)
    
    if not isinstance(resource_ids, list):
        resource_ids = [resource_ids]
    
    sender = directive.get("sender")
    if not sender:
        sender = {}
    
    job_info = dict(
                    job_id = job_uuid,
                    status = const.JOB_STATUS_PEND,
                    job_action = action,
                    directive = json_dump(directive),
                    resource_ids = ",".join(resource_ids),
                    create_time = get_current_time(),
                    owner = sender.get("owner", ""),
                    zone = sender.get("zone", "")
                    )
    
    if not ctx.pg.batch_insert(TB_DESKTOP_JOB, {job_uuid: job_info}):
        logger.error("submit job [%s] to db failed" % (job_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return job_uuid

def submit_desktop_job(action, directive, resource_ids, req_type):

    ctx = context.instance()

    max_pending_jobs = ctx.max_pending_jobs
    if ctx.max_pending_jobs is None:
        max_pending_jobs = 20
    
    # do not send job if there are too much pending jobs
    pending_count = ctx.pg.get_count(TB_DESKTOP_JOB, {'status': const.JOB_STATUS_PEND})
    if pending_count >= max_pending_jobs:
        refresh_zombie_job()
        pending_count = ctx.pg.get_count(TB_DESKTOP_JOB, {'status': const.JOB_STATUS_PEND})
        if pending_count >= max_pending_jobs:
            logger.error("too much pending jobs [%s], disable new jobs" % pending_count)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_TOO_MUCH_PENDING_JOBS,pending_count)

    # create a new job
    ret = new_desktop_job(action, directive, resource_ids)
    if isinstance(ret, Error):
        return ret
    
    job_uuid = ret
    job_req = {"job_id": job_uuid, "req_type": req_type}
    
    ret = send_to_server(const.LOCALHOST, const.DISPATCH_SERVER_PORT, job_req)
    if isinstance(ret, Error):
        return ret

    return (job_uuid, ret)

def get_resource_tasks(task_ids):
    
    ctx = context.instance()
    status_tasks = {}
    tasks = ctx.pgm.get_tasks(task_ids)
    if not tasks:
        return None
    
    pend_task = []
    succ_task = []
    work_task = []
    fail_task = []
    for task_id, task in tasks.items():
        status = task["status"]
        if status == const.TASK_STATUS_FAIL:
            fail_task.append(task_id)
        elif status == const.TASK_STATUS_SUCC:
            succ_task.append(task_id)
        elif status == const.TASK_STATUS_PEND:
            pend_task.append(task_id)
        elif status == const.TASK_STATUS_WORKING:
            work_task.append(task_id)
            
    status_tasks[const.TASK_STATUS_FAIL] = fail_task
    status_tasks[const.TASK_STATUS_PEND] = pend_task
    status_tasks[const.TASK_STATUS_SUCC] = succ_task
    status_tasks[const.TASK_STATUS_WORKING] = work_task
    
    return status_tasks

def format_desktop_tasks(job_set):
    
    ctx = context.instance()
    
    for job_id, job in job_set.items():
        
        tasks = ctx.pgm.get_desktop_tasks(job_id)
        if not tasks:
            tasks = {}
            
        status_tasks = {}
        succ_task = []
        work_task = []
        fail_task = []
        for task_id, task in tasks.items():
            status = task["status"]
            if status == const.TASK_STATUS_FAIL:
                fail_task.append(task_id)
            elif status == const.TASK_STATUS_SUCC:
                succ_task.append(task_id)
            elif status == const.TASK_STATUS_WORKING:
                work_task.append(task_id)
        
        status_tasks["total_count"] = len(tasks)
        status_tasks["failed"] = len(fail_task)
        status_tasks["success"] = len(succ_task)
        status_tasks["working"] = len(work_task)
        
        job["task_stat"] = status_tasks
    
    return job_set
