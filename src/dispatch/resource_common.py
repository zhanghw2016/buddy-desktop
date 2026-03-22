from contextlib import contextmanager
import traceback
import context
from utils.id_tool import(
    UUID_TYPE_DESKTOP_GROUP,
    UUID_TYPE_DESKTOP,
    UUID_TYPE_DESKTOP_IMAGE,
    UUID_TYPE_DESKTOP_DISK,
    UUID_TYPE_DESKTOP_NETWORK,
)
import db.constants as dbconst
from utils.misc import remove_file
import constants as const
from utils.id_tool import(
    UUID_TYPE_DESKTOP_TASK,
    get_uuid
)
import copy
from utils.json import json_dump
from utils.misc import get_current_time
from log.logger import logger
from utils.misc import rLock
from base_client import send_to_server, send_pull_task
import time
from constants import TASK_STATUS_WORKING, TASK_STATUS_PEND
import datetime

DISPATCH_TASKS_LOCK = "DispatchTasks"
@contextmanager
def transition_status(tb, keys, status, suppress_warning=False, noop=False):
    if noop:
        yield
        return

    ctx = context.instance()
    if isinstance(keys, list) or isinstance(keys, set):
        for key in keys:
            ctx.pg.update(tb, key, {'transition_status': status}, suppress_warning=suppress_warning)
    else:
        ctx.pg.update(tb, keys, {'transition_status': status}, suppress_warning=suppress_warning)

    try:
        yield
    except:
        logger.critical("yield exits with exception: %s" % traceback.format_exc())

    if isinstance(keys, list):
        for key in keys:
            ctx.pg.update(tb, key, {'transition_status': ""}, suppress_warning=suppress_warning)
    else:
        ctx.pg.update(tb, keys, {'transition_status': ""}, suppress_warning=suppress_warning)

def clear_resource_lock(resource_ids):
    
    ctx = context.instance()
    if not resource_ids:
        return None
    
    if not isinstance(resource_ids, list):
        resource_ids = [resource_ids]
    
    for resource_id in resource_ids:
        prefix = resource_id.split("-")[0]
        if prefix == UUID_TYPE_DESKTOP_GROUP:
            resource_type = dbconst.RESTYPE_DESKTOP_GROUP
        elif prefix == UUID_TYPE_DESKTOP:
            resource_type = dbconst.RESTYPE_DESKTOP
        elif prefix == UUID_TYPE_DESKTOP_DISK:
            resource_type = dbconst.RESTYPE_DESKTOP_DISK
        elif prefix == UUID_TYPE_DESKTOP_NETWORK:
            resource_type = dbconst.RESTYPE_DESKTOP_NETWORK
        elif prefix == UUID_TYPE_DESKTOP_IMAGE:
            resource_type = dbconst.RESTYPE_DESKTOP_IMAGE
        else:
            continue
            
        table = dbconst.RESOURCE_TYPE_TABLES[resource_type]
        resource = ctx.pg.get(table, resource_id)
        if resource:
            continue
        remove_file(const.PITRIX_LOCK_PATH % resource_id)
    
    return None

# task
def new_desktop_task(sender, job_id, action, resource_ids, directive, task_type=None):
    ctx = context.instance()
    if not isinstance(resource_ids, list):
        resource_ids = [resource_ids]
    
    if "owner" not in sender:
        sender["owner"] = const.GLOBAL_ADMIN_USER_ID

    if not task_type:
        task_type = const.DESKTOP_JOB_MAP_TASK[action]
    
    task_level = 0 if task_type not in const.DESKTOP_HEAVY_TASKS else 1
    directive["action"] = task_type
    directive["sender"] = sender
    task_uuid = get_uuid(UUID_TYPE_DESKTOP_TASK, ctx.checker)
    task_info = dict(
                     task_id=task_uuid,
                     status=const.TASK_STATUS_PEND,
                     task_type=task_type,
                     resource_ids=",".join(resource_ids),
                     directive=json_dump(directive),
                     create_time=get_current_time(),
                     job_id=job_id,
                     task_level = task_level,
                     owner = sender["owner"],
                     zone = sender["zone"]
                     )

    if not ctx.pg.insert(dbconst.TB_DESKTOP_TASK, task_info):
        logger.error("create new desktop task [%s] to db failed" % (task_uuid))
        return None
    return task_uuid

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

def get_working_tasks(task_level=0):

    ctx = context.instance()
    tasks = ctx.pgm.get_tasks(status=[const.TASK_STATUS_WORKING], task_level=task_level)
    if not tasks:
        return None

    return tasks.keys()

def get_dispatch_task_count(task_level=0):

    ctx = context.instance()
    max_count = ctx.batch_task_count
    if task_level:
        max_count = ctx.batch_heavy_task_count
    
    if not max_count:
        max_count = const.MAX_BATCH_TASK_COUNT

    with rLock(DISPATCH_TASKS_LOCK):

        working_tasks = get_working_tasks(task_level)
        if not working_tasks:
            return max_count

        if len(working_tasks) >= max_count:
            return 0

        return (max_count - len(working_tasks))

def get_per_task_timeout(task_level=0):
    
    ctx = context.instance()
    per_task_timeout = const.JOB_MIN_TIMEOUT
    interval = const.JOB_MIN_INTERVAL

    if task_level:
        per_task_timeout = const.JOB_MAX_TIMEOUT if not ctx.heavy_task_timeout else ctx.heavy_task_timeout
        interval = const.JOB_MAX_INTERVAL
    
    return (per_task_timeout, interval)

def get_base_task_timeout(task_ids, task_level=0):
    
    task_count = len(task_ids)
    (per_task_timeout, interval) = get_per_task_timeout(task_level)    
    timeout = per_task_timeout * task_count

    return (timeout, interval)

def update_task_timeout(task_ids, start_time, task_level=0):
    
    if not task_ids:
        return None
    
    (per_task_timeout, _) = get_per_task_timeout(task_level)  
    
    task_count = len(task_ids)
    status_tasks = get_resource_tasks(task_ids)
    if not status_tasks:
        return None      
    
    diff_time = time.time() - start_time
    succ_task = status_tasks.get(const.TASK_STATUS_SUCC)
    fail_task = status_tasks.get(const.TASK_STATUS_FAIL)
    done_task_count = len(succ_task) + len(fail_task)
    
    if not done_task_count:
        if diff_time > per_task_timeout * 9/10:
            per_task_timeout = per_task_timeout + diff_time/2
    else:
        per_task_time = diff_time/done_task_count
        if per_task_time > per_task_timeout:
            per_task_timeout = per_task_time

    timeout = per_task_timeout * (task_count - done_task_count + 1)

    return timeout

def refresh_zombie_task():
    
    ctx = context.instance()
    
    tasks = ctx.pgm.get_tasks(status=[const.TASK_STATUS_PEND, const.TASK_STATUS_WORKING])
    if not tasks:
        return None
    
    refresh_tasks = {}
    for task_id, task in tasks.items():
        create_time = task.get("create_time")
        current_time = get_current_time()
        detla_time = datetime.timedelta(seconds=const.JOB_MAX_TIMEOUT*12)
        # request is expires if current_time greater than expires
        if create_time < current_time - detla_time:
            refresh_tasks[task_id] = {"status": const.JOB_STATUS_TIMEOUT}
    
    if refresh_tasks:
        ctx.pg.batch_update(dbconst.TB_DESKTOP_TASK, refresh_tasks)
    
    return None

def do_resource_task(task_ids, task_level=0):

    action_task_ids = copy.deepcopy(task_ids)

    # get task timeout
    ret = get_base_task_timeout(action_task_ids, task_level)
    (timeout, interval) = ret
    
    start_time = time.time()
    end_time = time.time() + timeout
    while time.time() < end_time:
        # check task timeout
        ret = update_task_timeout(task_ids, start_time, task_level)
        if ret:
            timeout = ret
            end_time = time.time() + timeout
        
        # wait task done
        if not action_task_ids:
            status_tasks = get_resource_tasks(task_ids)
            if not status_tasks:
                logger.error("Dispatch Task[%s] get resource task fail" % task_ids)
                return -1

            work_task = status_tasks.get(TASK_STATUS_WORKING)
            pend_task = status_tasks.get(TASK_STATUS_PEND)
            if work_task or pend_task:
                time.sleep(interval)
                continue

            return 0

        # get current task count
        task_count = get_dispatch_task_count(task_level)
        if task_count <= 0:
            refresh_zombie_task()
            time.sleep(interval)
            continue

        # get tasks to send pull server
        pull_tasks = action_task_ids
        if len(action_task_ids) > task_count:
            pull_tasks = action_task_ids[0:task_count]

        for task_id in pull_tasks:
            task_req = {"task_id": task_id, "req_type": const.REQ_TYPE_DESKTOP_TASK}
            ret = send_to_server(const.LOCALHOST, const.DISPATCH_SERVER_PORT, task_req)
            action_task_ids.remove(task_id)
            logger.info("send task [%s] to dispatch server" % task_id)

        time.sleep(interval)
    
    logger.error("dispatch task timeout %s" % action_task_ids)
    return -1

def confirm_desktop_task(task_ids, task_level, retries=3):
    
    ctx = context.instance()
    
    curr_tasks = {}
    
    while retries > 0:
        tasks = ctx.pgm.get_tasks(task_ids, task_level=task_level)
        if not tasks:
            tasks = {}
        
        no_task = []
        for task_id in task_ids:
            if task_id not in tasks:
                no_task.append(task_id)
            else:
                if task_id not in curr_tasks:
                    curr_tasks[task_id] = tasks[task_id]

        if not no_task:
            return tasks
        
        retries -= 1
        time.sleep(0.2)
            
    return curr_tasks

def dispatch_resource_task(job_id, task_ids, task_level=0):
    
    ctx = context.instance()
    if not task_ids:
        return 0

    # get tasks
    tasks = confirm_desktop_task(task_ids, task_level)
    if not tasks:
        logger.error("dispatch no found task %s" % task_ids)
        return 0

    logger.info("dispatch resource task %s , %s" % (job_id, task_ids))
    
    do_task_ids = tasks.keys()
    do_resource_task(do_task_ids, task_level)
    
    tasks = ctx.pgm.get_tasks(do_task_ids, [const.TASK_STATUS_FAIL,const.TASK_STATUS_PEND,const.TASK_STATUS_WORKING])
    if tasks:
        logger.error("dispatch task fail %s" % tasks.keys())
        return -1

    return 0

def set_job_working(job):

    ctx = context.instance()
    job_id = job["job_id"]
    status = job["status"]
    if status != const.JOB_STATUS_PEND:
        return -1
    if not ctx.pg.update(dbconst.TB_DESKTOP_JOB, job_id, {'status': const.JOB_STATUS_WORKING, 'status_time': get_current_time()}):
        return -1

    return 0

def job_fail(job_id):
    ctx = context.instance()
    logger.error("Job %s Fail." % job_id)
    if not ctx.pg.update(dbconst.TB_DESKTOP_JOB, job_id, {'status': const.JOB_STATUS_FAIL, 'status_time': get_current_time()}):
        return -1
    return 0

def job_ok(job_id):
    ctx = context.instance()
    logger.info("Job %s OK." % job_id)
    if not ctx.pg.update(dbconst.TB_DESKTOP_JOB, job_id, {'status': const.JOB_STATUS_SUCC, 'status_time': get_current_time()}):
        return -1
    return 0

def task_ok(task_id):
    ctx = context.instance()
    ctx.pg.update(dbconst.TB_DESKTOP_TASK, task_id, {'status': const.TASK_STATUS_SUCC, 'status_time': get_current_time()})
    return 0

def task_fail(task_id):
    ctx = context.instance()
    ctx.pg.update(dbconst.TB_DESKTOP_TASK, task_id, {'status': const.TASK_STATUS_FAIL, 'status_time': get_current_time()})
    return 0

def job_info(job_id):
    ctx = context.instance()
    job = ctx.pg.get(dbconst.TB_DESKTOP_JOB, job_id)
    if job is None:
        return None
    tasks = ctx.pg.base_get(dbconst.TB_DESKTOP_TASK, {"job_id": job_id}, limit=1000)
    if tasks is None:
        return None

    task_total = len(tasks);
    result = {"zone_id": job.get("zone"), 
              "user_id": job.get("owner"), 
              "job_id": job_id,
              "resource_ids": job.get("resource_ids"),
              "job_status": job.get("status"), 
              "job_action": job.get("job_action"), 
              "task_total": task_total,
              "create_time": job.get("create_time"),
              "status_time": job.get("status_time")}
    task_finished = 0;
    task_failed = 0;
    for task in tasks:
        if task.get("status") == const.TASK_STATUS_SUCC:
            task_finished = task_finished + 1
        if task.get("status") == const.TASK_STATUS_FAIL:
            task_failed = task_failed + 1
    result.update({"task_finished": task_finished})
    result.update({"task_failed": task_failed})
    return result

def task_info(task_id):
    ctx = context.instance()
    task = ctx.pg.get(dbconst.TB_DESKTOP_TASK, task_id)
    if task is None:
        return None
    
    job_id = task.get("job_id")
    if job_id is None:
        return None
    return job_info(job_id)

def send_internel_req(action, resource_ids):
    
    ctx = context.instance()
    if not isinstance(resource_ids, list):
        resource_ids = [resource_ids]
    
    internel_req = {
                "req_type": const.REQ_TYPE_DESKTOP_INTERNEL, 
                "action": action,
                "resources": resource_ids
                }
    ret = send_pull_task(ctx, internel_req)
    if not ret:
        logger.error("send pull task fail %s" % resource_ids)
        return -1
    
    return 0

def get_all_system_config(config_keys=[]):
    sysconfig = {}
    ctx = context.instance()
    try:
        result = ctx.pg.base_get(dbconst.TB_VDI_SYSTEM_CONFIG)
        if result is None:
            logger.error("get all system config from table failed")
            return None

        for item in result:
            if len(config_keys) == 0 or (item['config_key'] in config_keys):
                sysconfig[item['config_key']] = item['config_value']

        return sysconfig
    except Exception, e:
        logger.error("get all system config with Exception:%s" % e)
        return None

def update_apply_form_status(apply_id, status, resource_id=None):
    ctx = context.instance()
    update_info = {"status": status}
    if resource_id:
        update_info["resource_id"] = resource_id
    if status == const.APPLY_FORM_STATUS_CREATED:
        update_info["approve_advice"] = ""
    if not ctx.pg.base_update(dbconst.TB_APPLY, {"apply_id": apply_id}, update_info):
        logger.error("Failed to update TB_APPPLY [%s] status to %s" % (apply_id, status))
        return -1

    return 0
