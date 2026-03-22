
from utils.json import json_load
from log.logger import logger
import context
import constants as const
from base_client import send_to_pull

def handle_desktop_job(req):

    ctx = context.instance()
    if 0 != send_to_pull(ctx.pull_url, {'req_type': const.REQ_TYPE_DESKTOP_JOB, 'job_id': req['job_id']}):
        return -1
    return 0

def handle_desktop_task(req):

    # dispatch job task
    ctx = context.instance()
    if 0 != send_to_pull(ctx.pull_url, {'req_type': const.REQ_TYPE_DESKTOP_TASK, 'task_id': req["task_id"]}):
        return -1

    return 0

def handle_desktop_zone_sync(req):

    # dispatch zone_sync
    ctx = context.instance()
    if 0 != send_to_pull(ctx.pull_url, {'req_type': const.REQ_TYPE_DESKTOP_ZONE_SYNC,"action": const.ZONE_SYNC_ACTION_SYNC_ZONE_INFO,'zone_id': req["zone_id"]}):
        return -1

    return 0

class ServiceHandler(object):

    def __init__(self):
        self.handle_map = {
            const.REQ_TYPE_DESKTOP_JOB: handle_desktop_job,
            const.REQ_TYPE_DESKTOP_TASK: handle_desktop_task,
            const.REQ_TYPE_DESKTOP_ZONE_SYNC: handle_desktop_zone_sync,
        }

    def handle(self, req_msg, title, **kargs):
        # decode to request object
        req = json_load(req_msg)
        if req == None or not isinstance(req, dict) or "req_type" not in req:
            logger.error("invalid request: %s" % req_msg)
            return

        # get message handler
        req_type = req["req_type"]
        if req_type not in self.handle_map:
            return

        # handle it directly
        self.handle_map[req_type](req)
        return 
        
        
        
