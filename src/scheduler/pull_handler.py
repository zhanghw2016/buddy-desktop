'''
Created on 2014-4-21

@author: yunify
'''
import time

from constants import REQ_TYPE_EXECUTE_SCHEDULER_TASK
from log.logger import logger
from server.shutdown.helper import handle_async_message
from utils.json import json_load

import context
from constants import REQ_TYPE_SCHED_EVENT
from constants import REQ_TYPE_DESKTOP_ZONE_SYNC
from threads import SchedItem

def handle_execute_scheduler_task(req):
    
    ctx = context.instance()
    scheduler_task_id = req['scheduler_task']

    scheduler_tasks = ctx.pgm.get_scheduler_tasks(scheduler_task_id)
    if not scheduler_tasks:
        logger.error('get scheduler task [%s] failed', scheduler_task_id)
        return -1

    scheduler_task = scheduler_tasks[scheduler_task_id]
    ret = ctx.scheduler_task_mgr.execute_scheduler_task(scheduler_task)
    if ret < 0:
        logger.error("execute scheduler task fail %s" % scheduler_task_id)
        return -1
    
    return 0

def handle_sched_event(req):

    ctx = context.instance()
    sched_item = SchedItem.load(req['sched_item'])
    ctx.scheduler_task_mgr.handle_sched_event(sched_item)

def handle_sched_sync_zone_info(req):

    zone_id = req.get("zone_id")
    if not zone_id:
        return 0

    ctx = context.instance()
    ctx.zone_builder.load_zone(zone_id)

    return 0

class PullServiceHandler(object):
    ''' long time service handler '''

    def handle(self, req_msg, title, **kargs):

        return handle_async_message(self._handle, req_msg)

    def _handle(self, req_msg):
        ''' no return'''

        # decode to request object
        req = json_load(req_msg)
        if req is None:
            logger.error("invalid request: %s" % req_msg)
            return

        if "req_type" not in req:
            logger.error("invalid request: %s" % req_msg)
            return

        start_time = time.time()

        req_type = req["req_type"]
        if req_type == REQ_TYPE_EXECUTE_SCHEDULER_TASK:
            handle_execute_scheduler_task(req)
        elif req_type == REQ_TYPE_SCHED_EVENT:
            handle_sched_event(req)
        elif req_type == REQ_TYPE_DESKTOP_ZONE_SYNC:
            handle_sched_sync_zone_info(req)
        else:
            logger.error('invalid request type [%s]', req)
            return

        exec_time = round(time.time() - start_time, 2)
        if exec_time > 120:
            logger.warn('slow [%s] request: %s', exec_time, req)
