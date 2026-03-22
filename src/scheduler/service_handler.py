'''
Created on 2015-1-1

@author: yunify
'''

from constants import (
    REQ_TYPE_START_SCHEDULER_TASK,
    REQ_TYPE_STOP_SCHEDULER_TASK,
    REQ_TYPE_RENEW_SCHEDULER,
    REQ_TYPE_EXECUTE_SCHEDULER_TASK,
    REQ_TYPE_DESKTOP_ZONE_SYNC
)
from base_client import send_to_pull
from log.logger import logger
from server.shutdown.helper import handle_sync_message
from utils.json import json_load, json_dump
import context

def handle_start_scheduler_task(req):

    ctx = context.instance()
    if 'scheduler_task' not in req:
        logger.error('missing scheduler_task in [%s]', req)
        return -1

    scheduler_task_id = req['scheduler_task']

    if not ctx.scheduler_task_mgr.start_scheduler_task(scheduler_task_id):
        logger.error('start scheduler task[%s] failed', scheduler_task_id)
        return -1

    logger.info('start scheduler task %s', scheduler_task_id)

    return 0

def handle_stop_scheduler_task(req):

    if 'scheduler_task' not in req:
        logger.error('missing scheduler in [%s]', req)
        return -1

    scheduler_task_id = req['scheduler_task']

    ctx = context.instance()

    if not ctx.scheduler_task_mgr.stop_scheduler_task(scheduler_task_id):
        logger.error('stop scheduler task [%s] failed', scheduler_task_id)
        return -1

    logger.info('stop scheduler task %s', scheduler_task_id)
    return 0

def handle_renew_scheduler_task(req):

    if 'scheduler_task' not in req:
        logger.error('missing scheduler task in [%s]', req)
        return -1

    scheduler_task_id = req['scheduler_task']

    ctx = context.instance()
    if not ctx.scheduler_task_mgr.start_scheduler_task(scheduler_task_id, renew=True):
        logger.error('renew scheduler task[%s] failed', scheduler_task_id)
        return -1

    logger.info('renew scheduler task %s', scheduler_task_id)

    return 0

def handle_run_scheduler_task(req):

    if 'scheduler_task' not in req:
        logger.error('missing scheduler task in [%s]', req)
        return -1

    ctx = context.instance()
    if not ctx.scheduler_task_mgr.is_active():
        logger.error('scheduler manager is not active')
        return -1

    req = {'req_type': REQ_TYPE_EXECUTE_SCHEDULER_TASK,
           'scheduler_task': req['scheduler_task']}

    if 0 != send_to_pull(ctx.pull_url, req):
        logger.error('send request [%s] to pull failed', req)
        return -1

    logger.info('run scheduler task %s', req['scheduler_task'])
    return 0

def handle_scheduler_sync_zone_info(req):

    # scheduler zone_sync
    ctx = context.instance()
    req = {'req_type': REQ_TYPE_DESKTOP_ZONE_SYNC,'zone_id': req["zone_id"]}

    if 0 != send_to_pull(ctx.pull_url, req):
        logger.error('send request [%s] to pull failed', req)
        return -1

    return 0

class ServiceHandler(object):
    ''' peer service handler '''

    def __init__(self):
        self.handle_map = {
                REQ_TYPE_START_SCHEDULER_TASK: handle_start_scheduler_task,
                REQ_TYPE_STOP_SCHEDULER_TASK: handle_stop_scheduler_task,
                REQ_TYPE_RENEW_SCHEDULER: handle_renew_scheduler_task,
                REQ_TYPE_EXECUTE_SCHEDULER_TASK: handle_run_scheduler_task,
                REQ_TYPE_DESKTOP_ZONE_SYNC: handle_scheduler_sync_zone_info,
                }

    def handle(self, req_msg, title, **kargs):
        # if program is shutting down, notify frontend with special reply
        # title is request type
        return handle_sync_message(False, self._handle, req_msg)

    def _handle(self, req_msg):
        ''' @return reply message '''
        # decode to request object
        req = json_load(req_msg)
        if not req or "req_type" not in req:
            logger.error("invalid request: %s" % req_msg)
            return self._reply_err()

        # get message handler
        req_type = req["req_type"]
        if req_type not in self.handle_map:
            logger.error("invalid request: %s" % req_msg)
            return self.return_error()

        # handle it
        ret = self.handle_map[req_type](req)
        if ret < 0:
            logger.error("handle request failed: %s" % req_msg)
            return self.return_error()

        return self.return_ok()

    def return_ok(self):
    
        rep = {'ret_code': 0}
        return json_dump(rep)

    def return_error(self):
    
        return {'ret_code': -1}
