'''
Created on 2012-11-12

@author: yunify
'''

from utils.json import json_load
import traceback
from log.logger import logger

class PullServiceHandler(object):
    ''' long time service handler
    '''
    def __init__(self):
        self.handler = {
            }

    def handle(self, req, title, **kargs):

        req = json_load(req)

        try:
            req_type = req['req_type']

            # handle job directly
            ret = self.handler[req_type](req)
            if ret < 0:
                logger.error("handle fail [%s]" % (req))
        except:

            logger.critical("handle failed: [%s]" % (traceback.format_exc()))
            return

        return
