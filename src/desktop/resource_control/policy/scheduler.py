'''
Created on 2015-01-09

@author: yunify
'''
import ast
import traceback
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error

import constants as const

from resource_control.permission import(
    check_user_resource_permission,
)
from db.constants import (
    TB_SCHEDULER_TASK,
    TB_SCHEDULER_TASK_HISTORY,
    TB_SCHEDULER_TASK_RESOURCE,
    TB_DESKTOP_GROUP,
    TB_SNAPSHOT_GROUP,
    RESTYPE_DESKTOP_GROUP,
    RESTYPE_DELIVERY_GROUP,
    TB_DELIVERY_GROUP)
from utils.id_tool import get_uuid, UUID_TYPE_VDI_SCHEDULER_TASK, get_resource_type
from utils.misc import get_current_time

import context
from constants import (
    REQ_TYPE_START_SCHEDULER_TASK,
    REQ_TYPE_STOP_SCHEDULER_TASK,
    REQ_TYPE_RENEW_SCHEDULER,
    REQ_TYPE_EXECUTE_SCHEDULER_TASK,
    SCHETASK_TYPE_MODIFY_DG_COUNT,
    SCHEDULER_TASK_NEED_PARSE,
    SCHETASK_TYPE_UPDATE_DESKTOP_IMAGE,
    SCHETASK_TYPE_AUTO_SNAPSHOT)
from base_client import ReqLetter
from constants import VDI_SCHEDULER_SERVER_PORT
from utils.json import json_dump, json_load
from log.logger import logger
from common import (
    is_global_admin_user,
    is_citrix_platform
)
from db.constants import(
    RES_SCOPE_READONLY,
)
TIMEOUT = 10

def check_scheduler_task_vaild(scheduler_task_id, status=None, check_trans_status=True):

    ctx = context.instance()
    scheduler_tasks = ctx.pgm.get_scheduler_tasks(scheduler_task_id)
    if not scheduler_tasks:
        logger.error("scheduler task [%s] no found" % scheduler_task_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, scheduler_task_id)
    
    scheduler_task = scheduler_tasks[scheduler_task_id]
    
    if status and status != scheduler_task["status"]:
        logger.error("scheduler task [%s] status %s dismatch" % (scheduler_task_id, status))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_SCHEDULER_TASK_STATUS_DISMATCH, (scheduler_task_id, status))

    if check_trans_status and scheduler_task["transition_status"]:
        logger.error("scheduler task [%s] in trans status %s" % (scheduler_task_id, scheduler_task["transition_status"]))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_SCHEDULER_TASK_STILL_EXECUTING, (scheduler_task_id))

    return scheduler_task

def format_scheduler_tasks(scheduler_task_set, verbose=0):

    ctx = context.instance()
    if not scheduler_task_set or not verbose:
        return None
    
    for scheduler_task_id, scheduler_task in scheduler_task_set.items():
        task_resource_set = ctx.pgm.get_scheduler_task_resource(scheduler_task_id)
        if not task_resource_set:
            scheduler_task["resources"] = []
        else:
            scheduler_task["resources"] = task_resource_set.values()
    
    return scheduler_task_set

def check_schduler_task_type(task_type):
    
    if task_type not in const.SCHEDULER_TASK_TYPES:
        logger.error('no found scheduler task resource type %s' % task_type)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_TASK_TYPE_NO_SUPPORTED, task_type)

    return None

def parse_schduler_task_resource(task_type, resource_ids):

    if not resource_ids:
        return None
    
    resources = {}
    for resource_id in resource_ids:
        if task_type not in SCHEDULER_TASK_NEED_PARSE:
            resources[resource_id] = ""
            continue
        
        if task_type == SCHETASK_TYPE_MODIFY_DG_COUNT:
            resource_list = resource_id.split("|")
            if len(resource_list) != 2:
                logger.error('task modify desktop group count no desktop count %s' % resource_id)
                return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                             ErrorMsg.ERR_MSG_TASK_RESOURCE_NO_DESKTOP_COUNT, task_type)
            
            resources[resource_list[0]] = json_dump({"desktop_count": resource_list[1]})

        elif task_type == SCHETASK_TYPE_UPDATE_DESKTOP_IMAGE:
            resource_list = resource_id.split("|")
            if len(resource_list) != 2:
                logger.error('task update desktop group image no desktop image %s' % resource_id)
                return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                             ErrorMsg.ERR_MSG_TASK_RESOURCE_NO_DESKTOP_IMAGE, task_type)
            
            resources[resource_list[0]] = json_dump({"desktop_image": resource_list[1]})
        elif task_type == SCHETASK_TYPE_AUTO_SNAPSHOT:
            resource_list = resource_id.split("|")
            if len(resource_list) != 2:
                logger.error('task update auto snapshot no is_full parameter %s' % resource_id)
                return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                             ErrorMsg.ERR_MSG_TASK_RESOURCE_NO_IS_FULL_PARAMETER, task_type)

            resources[resource_list[0]] = json_dump({"is_full": resource_list[1]})

    return resources

def create_scheduler_task(sender, task_name, task_type, description, repeat, period, ymd, hhmm, term_time, resource_type=None):

    ctx = context.instance()

    if not resource_type:
        resource_type = const.SCHEDULER_TASK_RESOURCE_TYPES.get(task_type)
        if not resource_type:
            logger.error('no found scheduler task resource type %s' % task_type)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_SCHEDULER_TASK_RESOURCE_TYPE_DISMATCH, task_type)

    scheduler_task_id = get_uuid(UUID_TYPE_VDI_SCHEDULER_TASK, ctx.checker)
    new_scheduler_task = {
                        'owner': sender["owner"],
                        'scheduler_task_id': scheduler_task_id,
                        'task_name': task_name,
                        'task_type': task_type,
                        'description': description,
                        'repeat': repeat,
                        'period': period,
                        'ymd': ymd,
                        'hhmm': hhmm,
                        'term_time': term_time,
                        'zone': sender["zone"],
                        "create_time": get_current_time(),
                        "resource_type": resource_type
                        }

    if not ctx.pg.insert(TB_SCHEDULER_TASK, new_scheduler_task):
        logger.error('insert scheduler task [%s] fail', new_scheduler_task)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return scheduler_task_id

def active_task_changed(sender, scheduler_task_id, status=None):
    
    ctx = context.instance()
    scheduler_tasks = ctx.pgm.get_scheduler_tasks(scheduler_task_id)
    if not scheduler_tasks:
        logger.error("scheduler task [%s] no found" % scheduler_task_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, scheduler_task_id)
    
    scheduler_task = scheduler_tasks[scheduler_task_id]
    if not status:
        status = scheduler_task["status"]
    
    if status == const.SCHEDULER_TASK_STATUS_ACTIVE:
        ret = start_scheduler_task(sender, scheduler_task_id)
        if not ret:
            return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_START_SCHEDULER_TASK_FAIL, (scheduler_task_id))
        
    else:
        ret = stop_scheduler_task(sender, scheduler_task_id)
        if not ret:
            return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_STOP_SCHEDULER_TASK_FAIL, (scheduler_task_id))

    return ret
            
def parse_python_data(string):

    try:
        return ast.literal_eval(string)
    except:
        logger.error('parse python data[%s] failed: %s',
                string, traceback.format_exc())
        return None

def send_scheduler_request(req, timeout=TIMEOUT, retry=3):
    ''' send request to scheduler server '''
    ctx = context.instance()
    sender = req["sender"]
    zone_id = sender["zone"]
    zone = ctx.zones.get(zone_id)
    if not zone:
        logger.error("sender scheduler request no found zone in ctx.zones %s" % zone_id)
        return None
        
    desktop_connection = zone.desktop_connection
    scheduler_task_server = desktop_connection["host"]
    
    host, port = (scheduler_task_server, VDI_SCHEDULER_SERVER_PORT)

    letter = ReqLetter("tcp://127.0.0.1:%s" % (port), json_dump(req))

    cnt = 0
    while cnt < retry:
        rep = json_load(ctx.client.send(letter, timeout=timeout))
        if rep is None:
            logger.warn("send request to scheduler server [%s] timeout, [%s]" % (host, req))
            cnt += 1
            continue
        elif rep['ret_code'] != 0:
            logger.error("handle request failed on scheduler server [%s], \
                    req: [%s], resp: [%s]", host, req, rep)
        return rep

    logger.critical("send request to scheduler server [%s] timeout, [%s]" % (host, req))

def start_scheduler_task(sender, scheduler_task_id):

    req = {
            'req_type': REQ_TYPE_START_SCHEDULER_TASK,
            'scheduler_task': scheduler_task_id,
            "sender": sender
          }

    rep = send_scheduler_request(req)
    if not rep or rep['ret_code'] != 0:
        logger.error("start scheduler failed [%s]", req)
        return False

    return True

def stop_scheduler_task(sender, scheduler_task_id):

    req = {
            'req_type': REQ_TYPE_STOP_SCHEDULER_TASK,
            'scheduler_task': scheduler_task_id,
            "sender": sender
            }

    rep = send_scheduler_request(req)
    if not rep or rep['ret_code'] != 0:
        logger.error("stop scheduler failed [%s]", req)
        return False

    return True

def renew_scheduler_task(sender, scheduler_task_id):

    req = {
            'req_type': REQ_TYPE_RENEW_SCHEDULER,
            'scheduler_task': scheduler_task_id,
            "sender": sender
            }

    rep = send_scheduler_request(req)
    if not rep or rep['ret_code'] != 0:
        logger.error("renew scheduler failed [%s]", req)
        return False

    return True

def execute_scheduler_task(sender, scheduler_task_id):

    req = {
            'req_type': REQ_TYPE_EXECUTE_SCHEDULER_TASK,
            'scheduler_task': scheduler_task_id,
            "sender": sender
            }

    rep = send_scheduler_request(req)
    if not rep or rep['ret_code'] != 0:
        logger.error("execute scheduler task failed [%s]", req)
        return False

    return True

def check_desktop_scheduler_permission(sender, scheduler_ids, conditions=None, action_type=RES_SCOPE_READONLY):

    if isinstance(scheduler_ids, str):
        scheduler_ids = [scheduler_ids]       

    if is_global_admin_user(sender):
        if scheduler_ids and conditions is not None:
            conditions["scheduler_id"] = scheduler_ids
        return scheduler_ids
        
    ret = check_user_resource_permission(sender, TB_SCHEDULER_TASK, scheduler_ids)
    if isinstance(ret, Error):
        return ret
    
    access_scheduler = ret.keys()
    if scheduler_ids:
        if not access_scheduler:
            logger.error("describe user [%s] cant access resource [%s]." % (sender["owner"], scheduler_ids))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED, (sender["owner"], scheduler_ids))
        else:
            for scheduler_id in scheduler_ids:
                if scheduler_id in access_scheduler:
                    continue

                logger.error("describe user [%s] cant access resource [%s]." % (sender["owner"], scheduler_id))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED, (sender["owner"], scheduler_id))

    if conditions is not None:
        if not access_scheduler:
            conditions["scheduler_id"] = None
        else:
            conditions["scheduler_id"] = access_scheduler

    return access_scheduler

def check_schduler_task_resource(scheduler_task, resource_ids, is_add=True):

    ctx = context.instance()
    scheduler_task_id = scheduler_task["scheduler_task_id"]
    resource_type = scheduler_task["resource_type"]
    if not resource_type:
        logger.error("schduler task %s no found resource type" % (scheduler_task_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_SCHEDULER_TASK_NO_RESOURCE_TYPE, scheduler_task_id)

    # check resource type
    for resource_id in resource_ids:
        res_type = get_resource_type(resource_id)
        if res_type != resource_type:
            logger.error("resource %s type dismatch scheduler task %s  %s" % (scheduler_task_id, resource_id, resource_type))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_RESOURCE_TYPE_DISMATCH, (scheduler_task_id, resource_id, resource_type))
    
    # check resource
    task_resource = ctx.pgm.get_scheduler_task_resource(scheduler_task_id)
    if not task_resource:
        task_resource = {}

    for resource_id in resource_ids:
        if is_add:
            if resource_id in task_resource:
                logger.error("resource %s already existed in scheduler task %s" % (resource_id, scheduler_task_id))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_RESOURCE_ALREADY_EXISTED_SCHEDULER_TASK, (scheduler_task_id, resource_id))
        else:
            if resource_id not in task_resource:
                logger.error("resource %s not in scheduler task %s" % (resource_id, scheduler_task_id))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_RESOURCE_NOT_IN_SCHEDULER_TASK, (scheduler_task_id, resource_id))

    return None

def add_resource_to_scheduler_task(scheduler_task_id, resources):

    ctx = context.instance()
    if not resources:
        return None
    
    resource_ids = resources.keys()
    scheduler_tasks = ctx.pgm.get_scheduler_tasks(scheduler_task_id)
    if not scheduler_tasks:
        logger.error("scheduler task [%s] no found" % scheduler_task_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, scheduler_task_id)
    
    scheduler_task = scheduler_tasks[scheduler_task_id]

    ret = check_schduler_task_resource(scheduler_task, resource_ids)
    if isinstance(ret, Error):
        return ret

    task_resource = {}
    for resource_id in resource_ids:
        
        task_type = scheduler_task["task_type"]   
        resource_info = {
                        "scheduler_task_id": scheduler_task_id,
                        "task_type": task_type,
                        "task_name": scheduler_task["task_name"],
                        "resource_id": resource_id,
                        "create_time": get_current_time(False),
                        "task_param": resources[resource_id] if resources[resource_id] else ''
                        }
        
        task_resource[resource_id] = resource_info

    if not ctx.pg.batch_insert(TB_SCHEDULER_TASK_RESOURCE, task_resource):
        logger.error("add resource to scheduler task [%s] failed", task_resource)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return resource_ids

def delete_resource_from_scheduler_task(scheduler_task_id, resource_ids=None):

    ctx = context.instance()
    if not resource_ids:
        ret = ctx.pgm.get_scheduler_task_resource(scheduler_task_id)
        if not ret:
            return None
        resource_ids = ret.keys()
    
    conditions = {
                 "scheduler_task_id": scheduler_task_id,
                 "resource_id": resource_ids
                 }
    ctx.pg.base_delete(TB_SCHEDULER_TASK_RESOURCE, conditions)
    return None

def modify_scheduler_task_attributes(scheduler_task_id, task_name, description):
    
    ctx = context.instance()
    update_info = {}
    if description is not None:
        update_info["description"] = description
    if task_name is not None:
        update_info["task_name"] = task_name
    
    if not update_info:
        return None
        
    if not ctx.pg.update(TB_SCHEDULER_TASK, scheduler_task_id, update_info):
        logger.error("update scheduler task [%s] attrs [%s] failed", (scheduler_task_id, update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
    if task_name:
        conditions = {'scheduler_task_id': scheduler_task_id}
        cols = {
                'task_name': task_name,
                }
        if ctx.pg.base_update(TB_SCHEDULER_TASK, conditions, cols) == -1:
            logger.error('refresh scheduler task name [%s] fail', scheduler_task_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def update_scheduler_task(scheduler_task_id, attrs):
    
    if not scheduler_task_id or not attrs:
        return None
    
    ctx = context.instance()
    if not ctx.pg.batch_update(TB_SCHEDULER_TASK, {scheduler_task_id: attrs}):
        logger.error("update scheduler task [%s] attrs [%s] failed", (scheduler_task_id, attrs))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def delete_scheduler_tasks(sender, scheduler_task_ids):

    ctx = context.instance()
    for scheduler_task_id in scheduler_task_ids:
        
        ret = stop_scheduler_task(sender, scheduler_task_id)
        if not ret:
            return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_STOP_SCHEDULER_TASK_FAIL, (scheduler_task_id))
        
        ret = delete_resource_from_scheduler_task(scheduler_task_id)
        if isinstance(ret, Error):
            return ret

        ctx.pg.delete(TB_SCHEDULER_TASK, scheduler_task_id)
        condition = {'scheduler_task_id': scheduler_task_id}
        ctx.pg.base_delete(TB_SCHEDULER_TASK_HISTORY, condition)

    return None

def activate_desktop_scheduler_task(sender, scheduler_task_id, status):

    ctx = context.instance()
    
    ret = active_task_changed(sender, scheduler_task_id, status)
    if isinstance(ret, Error):
        return ret

    conditions = {'scheduler_task_id': scheduler_task_id}
    cols = {
            'status': status,
            'status_time': get_current_time(),
            "update_time": get_current_time()
            }

    if ctx.pg.base_update(TB_SCHEDULER_TASK, conditions, cols) == -1:
        logger.error('activate scheduler task [%s] fail', scheduler_task_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def get_scheduler_desktop_group(scheduler_id, scheduler_task_id=None):
    ctx = context.instance()

    tasks = ctx.pgm.get_scheduler_task(scheduler_id=scheduler_id)
    if not tasks:
        return None
    
    desktop_group_ids = []
    for _, task in tasks.items():
        task_param = task["task_param"]
       
        task_id = task["scheduler_task_id"]
        if scheduler_task_id and scheduler_task_id == task_id:
            continue
        
        task_param = parse_python_data(task_param)
        if not task_param:
            continue
        
        resources = task_param["resources"]
        if not resources:
            continue
        
        desktop_group_ids.extend(resources)
    
    return desktop_group_ids

def get_task_desktop_group_resource(sender, scheduler_task_id, task_type):
    
    zone_id = sender["zone"]
    ctx = context.instance()
    task_resource = ctx.pgm.get_scheduler_task_resource(scheduler_task_id)
    if not task_resource:
        task_resource = {}
    
    desktop_group_type = None
    if task_type == const.SCHETASK_TYPE_MODIFY_DG_COUNT:
        desktop_group_type = const.DG_TYPE_RANDOM

    if not is_citrix_platform(ctx, sender["zone"]):
        if task_type == const.SCHETASK_TYPE_UPDATE_DESKTOP_IMAGE:
            desktop_group_type = [const.DG_TYPE_RANDOM,const.DG_TYPE_STATIC]
        
    desktop_groups = ctx.pgm.get_desktop_groups(desktop_group_type=desktop_group_type, zone_id=zone_id)
    if not desktop_groups:
        return None
    
    check_resource = []
    for desktop_group_id, _ in desktop_groups.items():
        if desktop_group_id in task_resource:
            continue
        check_resource.append(desktop_group_id)
    
    return check_resource

def get_task_delivery_group_resource(sender, scheduler_task_id):
    
    ctx = context.instance()
    task_resource = ctx.pgm.get_scheduler_task_resource(scheduler_task_id)
    if not task_resource:
        task_resource = {}
       
    delivery_groups = ctx.pgm.get_delivery_groups(zone_id=sender["zone"])
    if not delivery_groups:
        return None
    
    check_resource = []
    for delivery_group_id, _ in delivery_groups.items():
        if delivery_group_id in task_resource:
            continue
        check_resource.append(delivery_group_id)
    
    return check_resource

def get_task_snapshot_resource(sender, scheduler_task_id):
    
    ctx = context.instance()
    task_resource = ctx.pgm.get_scheduler_task_resource(scheduler_task_id)
    if not task_resource:
        task_resource = {}

    snapshot_group_ids = None
    snapshot_groups = ctx.pgm.get_snapshot_groups(snapshot_group_ids=snapshot_group_ids, zone_id=sender["zone"])
    if not snapshot_groups:
        return None
    
    check_resource = []
    for snapshot_group_id, _ in snapshot_groups.items():
        if snapshot_group_id in task_resource:
            continue
        check_resource.append(snapshot_group_id)
    
    return check_resource


def get_task_snapshot_type(scheduler_task_id):

    ctx = context.instance()
    is_full = 0
    task_resource = ctx.pgm.get_scheduler_task_resource(scheduler_task_id)
    if not task_resource:
        task_resource = {}

    for _,task_resources in task_resource.items():
        task_param = task_resources.get("task_param")
        if "1" in task_param:
            is_full = 1
        else:
            is_full = 0

    return is_full

def build_scheduler_task_resource(sender, scheduler_task_id, task_type, resource_type=None):
        
    if task_type in const.SCHEDULER_TASK_DG_TYPES:
        
        if resource_type == RESTYPE_DESKTOP_GROUP:
            resource_ids = get_task_desktop_group_resource(sender, scheduler_task_id, task_type)
            return (TB_DESKTOP_GROUP, resource_ids)
        elif resource_type == RESTYPE_DELIVERY_GROUP:
            resource_ids = get_task_delivery_group_resource(sender, scheduler_task_id)
            return (TB_DELIVERY_GROUP, resource_ids)
        
    elif task_type in [const.SCHETASK_TYPE_AUTO_SNAPSHOT]:
        resource_ids = get_task_snapshot_resource(sender, scheduler_task_id)
        return (TB_SNAPSHOT_GROUP, resource_ids)
    
    return None

def modify_task_resource_desktop_count(scheduler_task, resource_id, desktop_count):
    
    ctx = context.instance()
    scheduler_task_id = scheduler_task["scheduler_task_id"]
    ret = ctx.pgm.get_scheduler_task_resource(scheduler_task_id, resource_id)
    if not ret:
        logger.error('resource %s no found in scheduler task %s' % (resource_id, scheduler_task_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_IN_SCHEDULER_TASK, (resource_id, scheduler_task_id))
    
    task_type = scheduler_task["task_type"]
    if task_type != const.SCHETASK_TYPE_MODIFY_DG_COUNT:
        logger.error('scheduler task type %s dismatch %s' % (task_type, scheduler_task_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_IN_SCHEDULER_TASK, (resource_id, scheduler_task_id))    
    conditions = {}
    conditions["scheduler_task_id"] = scheduler_task_id
    conditions["resource_id"] = resource_id
    task_param = json_dump({"desktop_count": desktop_count})
    if not ctx.pg.base_update(TB_SCHEDULER_TASK_RESOURCE, conditions, {"task_param": task_param}):
        logger.error("modify desktop group update fail %s" % conditions)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def modify_task_resource_desktop_image(scheduler_task, resource_id, desktop_image):
    
    ctx = context.instance()
    scheduler_task_id = scheduler_task["scheduler_task_id"]
    ret = ctx.pgm.get_scheduler_task_resource(scheduler_task_id, resource_id)
    if not ret:
        logger.error('resource %s no found in scheduler task %s' % (resource_id, scheduler_task_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_IN_SCHEDULER_TASK, (resource_id, scheduler_task_id))
    
    task_type = scheduler_task["task_type"]
    if task_type != const.SCHETASK_TYPE_UPDATE_DESKTOP_IMAGE:
        logger.error('scheduler task type %s dismatch %s' % (task_type, scheduler_task_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_IN_SCHEDULER_TASK, (resource_id, scheduler_task_id))    
    conditions = {}
    conditions["scheduler_task_id"] = scheduler_task_id
    conditions["resource_id"] = resource_id
    task_param = json_dump({"desktop_image": desktop_image})
    if not ctx.pg.base_update(TB_SCHEDULER_TASK_RESOURCE, conditions, {"task_param": task_param}):
        logger.error("modify desktop group update fail %s" % conditions)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None