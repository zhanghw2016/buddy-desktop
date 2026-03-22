'''
Created on 2018-5-15

@author: yunify
'''

import traceback
import error.error_msg as ErrorMsg
import error.error_code as ErrorCodes
from error.error import Error
from common import return_error
from utils.json import json_load
from log.logger import logger
from constants import (
    REQUEST_PULL_ACTION_SYNC_ZONE_INFO
)
import handler.terminal_pull_handler as TerminalPullHandler


class PullServiceHandler(object):
    ''' pull service handler , long time job '''

    def __init__(self):
        self.handler = {
            REQUEST_PULL_ACTION_SYNC_ZONE_INFO: TerminalPullHandler.handle_sync_zone_info
        }

    def handle(self, req, title, **kargs):

        try:
            req = json_load(req)

            # handle it
            if "action" not in req:
                return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                        ErrorMsg.ERR_MSG_ILLEGAL_REQUEST))

            action = req['action']
            if action not in self.handler.keys():
                return_error(req, Error(ErrorCodes.INVALID_REQUEST_METHOD,
                                        ErrorMsg.ERR_CODE_MSG_INVALID_REQUEST_METHOD))

            ret = self.handler[action](req)
            if ret < 0:
                logger.error("handle fail [%s]" % (req))
        except:
            logger.critical("handle failed: [%s]" % (traceback.format_exc()))
            return

        return
