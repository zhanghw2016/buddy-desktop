'''
Created on 2015-1-2

@author: yunify
'''
import context

import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg

from db.constants import (
    TB_SCHEDULER_TASK,
    TB_SCHEDULER_TASK_HISTORY,
    TB_DELIVERY_GROUP,
    GOLBAL_ADMIN_COLUMNS,
    DEFAULT_LIMIT,
    CONSOLE_ADMIN_COLUMNS,
    TB_DESKTOP_GROUP,
    TB_SNAPSHOT_GROUP,
    RESTYPE_DESKTOP_GROUP
)
import db.constants as dbconst
from utils.misc import get_columns
from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    check_global_admin_console,
    check_admin_console
)
from log.logger import logger
from utils.misc import get_current_time
from common import return_error, return_success, return_items
import resource_control.policy.scheduler as ScheTask
import resource_control.desktop.resource_permission as ResCheck
import resource_control.permission as Permission
import resource_control.desktop.image as Image
import resource_control.desktop.desktop as Desktop
import resource_control.desktop.desktop_group as DesktopGroup
import resource_control.policy.snapshot as Snapshot

def handle_describe_scheduler_tasks(req):

    sender = req["sender"]
    ctx = context.instance()

    # build filter
    filter_conditions = build_filter_conditions(req, TB_SCHEDULER_TASK)
    scheduler_task_ids = req.get("scheduler_tasks")
    if scheduler_task_ids:
        filter_conditions.update({'scheduler_task_id': scheduler_task_ids})
    
    resource_ids = req.get("resources")
    if resource_ids:
        filter_conditions.update({'resource_id': resource_ids})

    # global admin user can see all resources
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_SCHEDULER_TASK]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_SCHEDULER_TASK]
    else:
        display_columns = {}

    scheduler_task_set = ctx.pg.get_by_filter(TB_SCHEDULER_TASK, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_SCHEDULER_TASK, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )

    if scheduler_task_set is None:
        logger.error('describe scheduler task failed [%s]' % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    ScheTask.format_scheduler_tasks(scheduler_task_set, req.get("verbose", 0))

    # get total count
    total_count = ctx.pg.get_count(TB_SCHEDULER_TASK, filter_conditions)
    if total_count is None:
        logger.error('get scheduler task count failed [%s]' % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count': total_count}
    return return_items(req, scheduler_task_set, 'scheduler_task', **rep)

def handle_create_scheduler_task(req):

    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["task_type", "repeat", "hhmm"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    task_name = req.get('task_name', '')
    task_type = req["task_type"]
    description = req.get('description', '')
    term_time = req.get('term_time', '')
    resource_type = req.get("resource_type")

    repeat = req['repeat']
    if repeat != 0:
        period = req['period']
        ymd = ''
    else:
        period = ''
        ymd = req['ymd']
    hhmm = req.get('hhmm', '')
    
    ret = ScheTask.check_schduler_task_type(task_type)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    resource_ids = req.get("resources")
    ret = ScheTask.parse_schduler_task_resource(task_type, resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    resources = ret
    
    # create scheduler
    ret = ScheTask.create_scheduler_task(sender, task_name, task_type, description, repeat, period, ymd, hhmm, term_time, resource_type)
    if isinstance(ret, Error):
        return return_error(req, ret)
    scheduler_task_id = ret

    ret = ScheTask.add_resource_to_scheduler_task(scheduler_task_id, resources)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    # ensure scheduler started
    ret = ScheTask.active_task_changed(sender, scheduler_task_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # register resource permission
    Permission.register_user_resource_scope(sender["owner"], dbconst.RESTYPE_SCHEDULER_TASK, scheduler_task_id, sender["zone"], dbconst.RES_SCOPE_DELETE)

    resp = {'scheduler_task': scheduler_task_id}
    return return_success(req, None, **resp)

def handle_modify_scheduler_task_attributes(req):
    
    sender = req["sender"]
    # check request param
    ret = ResCheck.check_request_param(req, ["scheduler_task"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    scheduler_task_id = req['scheduler_task']

    need_maint_columns = get_columns(req, ['task_name', 'description', 'repeat', 'period', 'ymd', 'hhmm', "term_time"])
    description = need_maint_columns.get("description")
    task_name = need_maint_columns.get("task_name")
    if description is not None or task_name is not None:
        ret = ScheTask.modify_scheduler_task_attributes(scheduler_task_id, task_name, description)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
        if description is not None:
            del need_maint_columns["description"]
        if task_name is not None:
            del need_maint_columns["task_name"]
    
    if need_maint_columns:
        ret = ScheTask.check_scheduler_task_vaild(scheduler_task_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
        scheduler_task = ret
        # check if need renew in scheduler_server
        need_renew = False
        time_params = ('repeat', 'period', 'ymd', 'hhmm', 'term_time')
        if any(scheduler_task[p] != need_maint_columns[p] for p in time_params if p in need_maint_columns):
            need_renew = True
    
        # update db
        attrs = dict((k, need_maint_columns[k]) for k in ['repeat', 'period', 'ymd', 'hhmm', 'term_time'] if k in need_maint_columns)
        if need_renew:
            attrs['update_time'] = get_current_time()
        if 'repeat' in attrs:
            if attrs['repeat'] != 0:
                attrs['ymd'] = ''
            else:
                attrs['period'] = ''
        ret = ScheTask.update_scheduler_task(scheduler_task_id, attrs)
        if isinstance(ret, Error):
            return return_error(req, ret)
        # renew to scheduler server
        if need_renew:
            ret = ScheTask.renew_scheduler_task(sender, scheduler_task_id)
            if not ret:
                logger.error("renew scheduler task fail %s, %s" % (scheduler_task_id, ret))
                return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                               ErrorMsg.ERR_MSG_RENEW_SCHEDULER_TASK_FAIL, scheduler_task_id))

    rep = {"scheduler_task": scheduler_task_id}
    return return_success(req, None, **rep)

def handle_delete_scheduler_tasks(req):
    # check permission
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ["scheduler_tasks"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    scheduler_task_ids = req['scheduler_tasks']
    
    for scheduler_task_id in scheduler_task_ids:
        ret = ScheTask.check_scheduler_task_vaild(scheduler_task_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
        
    # update db
    ret = ScheTask.delete_scheduler_tasks(sender, scheduler_task_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # clear resource permission
    Permission.clear_user_resource_scope(resource_ids=scheduler_task_ids)
    rep = {"scheduler_tasks": scheduler_task_ids}
    return return_success(req, None, **rep)

def handle_describe_scheduler_task_history(req):

    ctx = context.instance()
    sender = req["sender"]
    scheduler_task_id = req.get('scheduler_task')

    filter_conditions = {}
    if scheduler_task_id:
        filter_conditions['scheduler_task_id'] = scheduler_task_id

    # global admin user can see all resources
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[TB_SCHEDULER_TASK_HISTORY]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[TB_SCHEDULER_TASK_HISTORY]
    else:
        display_columns = {}

    history_set = ctx.pg.get_by_filter(TB_SCHEDULER_TASK_HISTORY, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(TB_SCHEDULER_TASK_HISTORY, "create_time"),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )

    if history_set is None:
        logger.error('describe scheduler history failed [%s]' % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    # get total count
    total_count = ctx.pg.get_count(TB_SCHEDULER_TASK_HISTORY, filter_conditions)
    if total_count is None:
        logger.error('get scheduler history count failed [%s]' % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    rep = {'total_count': total_count}
    return return_items(req, history_set, 'scheduler_task_history', **rep)

def handle_add_resource_to_scheduler_task(req):
    
    ret = ResCheck.check_request_param(req, ["scheduler_task", "resources"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    scheduler_task_id = req['scheduler_task']
    resource_ids = req["resources"]

    ret = ScheTask.check_scheduler_task_vaild(scheduler_task_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    scheduler_task = ret

    ret = ScheTask.parse_schduler_task_resource(scheduler_task["task_type"], resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    resources = ret

    # add new tasks
    ret = ScheTask.add_resource_to_scheduler_task(scheduler_task_id, resources)
    if isinstance(ret, Error):
        return return_error(req, ret)

    rep = {"scheduler_task": scheduler_task_id}
    return return_success(req, None, **rep)

def handle_delete_resource_from_scheduler_task(req):
    
    # check permission
    ret = ResCheck.check_request_param(req, ["scheduler_task", "resources"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    scheduler_task_id = req['scheduler_task']
    resource_ids = req["resources"]

    ret = ScheTask.check_scheduler_task_vaild(scheduler_task_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    scheduler_task = ret

    ret = ScheTask.check_schduler_task_resource(scheduler_task, resource_ids, False)
    if isinstance(ret, Error):
        return return_error(req, ret)

    # add new tasks
    ret = ScheTask.delete_resource_from_scheduler_task(scheduler_task_id, resource_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    rep = {"scheduler_task": scheduler_task_id}
    return return_success(req, None, **rep)

def handle_set_scheduler_task_status(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["scheduler_tasks", "status"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    scheduler_task_ids = req['scheduler_tasks']
    status = req["status"]
    
    
    for scheduler_task_id in scheduler_task_ids:

        ret = ScheTask.check_scheduler_task_vaild(scheduler_task_id)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
        # update db
        ret = ScheTask.activate_desktop_scheduler_task(sender, scheduler_task_id, status)
        if isinstance(ret, Error):
            return return_error(req, ret)

    rep = {"scheduler_tasks": scheduler_task_ids}
    return return_success(req, None, **rep)

def handle_execute_scheduler_task(req):
    
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["scheduler_task"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    scheduler_task_id = req['scheduler_task']

    ret = ScheTask.check_scheduler_task_vaild(scheduler_task_id)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ScheTask.execute_scheduler_task(sender, scheduler_task_id)
    if not ret:
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_EXECUTE_SCHEDULER_TASK_FAIL, scheduler_task_id))

    rep = {"scheduler_task_id": scheduler_task_id}
    return return_success(req, None, **rep)

def handle_get_scheduler_task_resources(req):

    ctx = context.instance()
    sender = req["sender"]
    
    filter_conditions = {}
    ret = ResCheck.check_request_param(req, ["scheduler_task"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    resource_type = req.get("resource_type", RESTYPE_DESKTOP_GROUP)
    scheduler_task_id = req['scheduler_task']
    ret = ScheTask.check_scheduler_task_vaild(scheduler_task_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    scheduler_task = ret
    
    ret = ScheTask.build_scheduler_task_resource(sender, scheduler_task_id, scheduler_task["task_type"], resource_type)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    if not ret:
        rep = {'total_count': 0}
        return return_items(req, None, 'task_resource', **rep)

    (tb, resource_ids) = ret
    if not resource_ids:
        rep = {'total_count': 0}
        return return_items(req, None, 'task_resource', **rep)

    if tb == TB_DESKTOP_GROUP:
        filter_conditions["desktop_group_id"] = resource_ids
    elif tb == TB_SNAPSHOT_GROUP:
        filter_conditions["snapshot_group_id"] = resource_ids
    elif tb == TB_DELIVERY_GROUP:
        filter_conditions["delivery_group_id"] = resource_ids
    
    filter_conditions["zone"] = sender["zone"]
    
    if check_global_admin_console(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[tb]
    elif check_admin_console(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[tb]
    else:
        display_columns = {}

    resource_set = ctx.pg.get_by_filter(tb, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(tb, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", DEFAULT_LIMIT),
                                      )
    if resource_set is None:
        logger.error('describe desktop group failed [%s]' % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    
    if tb == TB_DELIVERY_GROUP:
        Desktop.format_delivery_group_desktop(resource_set, 1)
    elif tb == TB_DESKTOP_GROUP:
        DesktopGroup.format_desktop_groups(sender, resource_set, 1)
    elif tb == TB_SNAPSHOT_GROUP:
        Snapshot.format_snapshot_groups(sender, resource_set, 1)
        if_full = ScheTask.get_task_snapshot_type(scheduler_task_id)

    # get total count
    total_count = ctx.pg.get_count(tb, filter_conditions)
    if total_count is None:
        logger.error('get desktop group count failed [%s]' % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    if tb == TB_SNAPSHOT_GROUP:
        rep = {'total_count': total_count,'is_full':if_full}
    else:
        rep = {'total_count': total_count}
    return return_items(req, resource_set, 'task_resource', **rep)

def handle_modify_scheduler_resource_desktop_count(req):
    
    ret = ResCheck.check_request_param(req, ["scheduler_task", "resource", "desktop_count"])
    if isinstance(ret, Error):
        return return_error(req, ret)
        
    scheduler_task_id = req['scheduler_task']
    resource_id = req["resource"]
    desktop_count = req["desktop_count"]
    ret = ScheTask.check_scheduler_task_vaild(scheduler_task_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    scheduler_task = ret
    
    ret = ScheTask.modify_task_resource_desktop_count(scheduler_task, resource_id, desktop_count)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_modify_scheduler_resource_desktop_image(req):
    
    ret = ResCheck.check_request_param(req, ["scheduler_task", "resource", "desktop_image"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    scheduler_task_id = req['scheduler_task']
    resource_id = req["resource"]
    desktop_image = req["desktop_image"]
    ret = ScheTask.check_scheduler_task_vaild(scheduler_task_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    scheduler_task = ret

    # check image vaild
    ret = Image.check_desktop_image_vaild(desktop_image)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = ScheTask.modify_task_resource_desktop_image(scheduler_task, resource_id, desktop_image)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)
