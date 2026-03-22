'''
Created on 2012-5-5

@author: yunify
'''
import traceback
from log.logger import logger

class SchedulerContext(object):

    def __init__(self):
        self.pg = None

        # pull server listening url
        self.pull_url = None

        # zone config
        self.zones = None
        self.zone_users = None
        self.zone_builder = None
        self.zone_checker = None
        self.zone_deploy = None

    def __getattr__(self, attr):
        # get conf short cut
        try:
            pass
        except:
            logger.error('getattr error: %s', traceback.format_exc())
            pass
        return None

g_scheduler_ctx = SchedulerContext()

def instance():
    ''' get context '''
    global g_scheduler_ctx
    return g_scheduler_ctx
