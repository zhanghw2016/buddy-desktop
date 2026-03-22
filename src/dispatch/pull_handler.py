
from utils.json import json_load
from log.logger import logger
import constants as const
from dispatch_handler.job_handler import JobHandler
from dispatch_handler.task_handler import TaskHandler
from dispatch_handler.internel_handler import InternelHandler
from server.shutdown.helper import handle_async_message
import traceback
from dispatch_handler.zone_sync_handler import Zone_Sync_Handler

class PullServiceHandler(object):
    ''' long time service handler
    '''
    def __init__(self):
        self.job_handler = JobHandler()
        self.task_handler = TaskHandler()
        self.InternelHandler = InternelHandler()
        self.Zone_Sync_Handler = Zone_Sync_Handler()

    def handle(self, req_msg, title, **kargs):
        return handle_async_message(self._handle, req_msg)

    def _handle(self, req_msg):
        
        # decode to request object
        req = json_load(req_msg)
        if req == None or "req_type" not in req:
            logger.error("invalid request: %s" % req_msg)
            return

        req_type = req["req_type"]
        try:
            if req_type == const.REQ_TYPE_DESKTOP_JOB:
                job_id = req["job_id"]
                self.job_handler.handle(job_id)
    
            elif req_type == const.REQ_TYPE_DESKTOP_TASK:
                task_id = req["task_id"]
                self.task_handler.handle(task_id)
            
            elif req_type == const.REQ_TYPE_DESKTOP_INTERNEL:
                
                action = req.get("action")
                if not action:
                    logger.error("internel handle no found action %s" % req_msg)
                    return
                
                self.InternelHandler.handle(action, req)

            elif req_type == const.REQ_TYPE_DESKTOP_ZONE_SYNC:
                action = req.get("action")
                if not action:
                    logger.error("zone_sync handle no found action %s" % req_msg)
                    return
                self.Zone_Sync_Handler.handle(action, req)

            return
        except:

            logger.critical("handle failed: [%s]" % (traceback.format_exc()))
            return
