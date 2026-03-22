import context
from db.constants  import (
    TB_DESKTOP_JOB,
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    TB_DESKTOP_TASK
)
from common import (
    check_global_admin_console,
    check_admin_console,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    is_normal_console
)
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
from common import (
    build_filter_conditions
)
import resource_control.desktop.job as Job

def handle_describe_desktop_jobs(req):

    ctx = context.instance()
    sender = req["sender"]

    # get desktop group set
    filter_conditions = build_filter_conditions(req, TB_DESKTOP_JOB)
    job_ids = req.get("jobs")
    if job_ids:
        filter_conditions.update({'job_id': job_ids})

    # global admin user can see all resources
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_JOB]
    elif check_admin_console(sender) and not is_normal_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_JOB]
    else:
        display_columns = {}

    job_set = ctx.pg.get_by_filter(TB_DESKTOP_JOB, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_DESKTOP_JOB, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if job_set is None:
        logger.error("describe desktop job failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    Job.format_desktop_tasks(job_set)
    
    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_JOB, filter_conditions)
    if total_count is None:
        logger.error("get desktop job count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, job_set, "desktop_job", **rep)

def handle_describe_desktop_tasks(req):

    ctx = context.instance()
    sender = req["sender"]

    # get desktop group set
    filter_conditions = build_filter_conditions(req, TB_DESKTOP_JOB)
    job_ids = req.get("jobs")
    if job_ids:
        filter_conditions.update({'job_id': job_ids})

    task_ids = req.get("tasks")
    if task_ids:
        filter_conditions.update({'task_id': task_ids})

    # global admin user can see all resources
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_DESKTOP_TASK]
    elif check_admin_console(sender) and not is_normal_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_DESKTOP_TASK]
    else:
        display_columns = {}

    task_set = ctx.pg.get_by_filter(TB_DESKTOP_TASK, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_DESKTOP_TASK, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if task_set is None:
        logger.error("describe desktop job failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(TB_DESKTOP_TASK, filter_conditions)
    if total_count is None:
        logger.error("get desktop job count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, task_set, "desktop_task", **rep)
