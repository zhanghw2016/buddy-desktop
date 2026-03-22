'''
Created on 2019-09-26

@author: yunify
'''
import time
import error.error_msg as ErrorMsg
import error.error_code as ErrorCodes
from error.error import Error
from common import return_error
from utils.json import json_load
from utils.misc import format_params
from log.logger import logger
from server.shutdown.helper import handle_sync_message
import constants as const
from request.desktop_server_request import DesktopServerRequest
import handler.desktop_server_handler as DesktopServerHandler

class ServiceHandler(object):
    ''' service handler , responded immediately '''

    def __init__(self):

        self.handler_map = {
            const.REQUEST_DESKTOP_SERVER_MODIFY_TERMINAL_ATTRIBUTES: DesktopServerHandler.handle_modify_terminal_attributes,
            const.REQUEST_DESKTOP_SERVER_RESTART_TERMINALS: DesktopServerHandler.handle_restart_terminals,
            const.REQUEST_DESKTOP_SERVER_STOP_TERMINALS: DesktopServerHandler.handle_stop_terminals,
            const.REQUEST_DESKTOP_SERVER_ONLINE_UPGRADE_TERMINALS: DesktopServerHandler.handle_online_upgrade_terminals
        }

    def handle(self, req_msg, title, **kargs):
        # if program is shutting down, notify front end with special reply
        # title is request type
        return handle_sync_message(False, self._handle, req_msg)

    def _handle(self, req_msg):
        ''' @return reply message '''

        # decode to request object
        try:
            req = json_load(req_msg)
        except Exception, e:
            logger.exception(
                "req_msg [%s] is not json, [%s]" % (req_msg, e))
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR))

        # record receive request
        logger.info("request received [%s]" % format_params(req))
        start_time = time.time()

        # discard none type request
        if req is None or not isinstance(req, dict):
            logger.error(
                "illegal request, try it again [%s]" % format_params(req))
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                           ErrorMsg.ERR_MSG_ILLEGAL_REQUEST))

        # check request type
        if "type" not in req:
            logger.error("[type] should be provided in request [%s]" %
                         format_params(req))
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                           ErrorMsg.ERR_MSG_MISSING_PARAMETER, "type"))

        req_type = req.pop("type")
        if req_type != const.REQUEST_TYPE_DESKTOP_SERVER:
            logger.error("illegal type [%s]" % (req_type))
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                           ErrorMsg.ERR_MSG_ILLEGAL_REQUEST))

        # handle it
        if "action" not in req.keys():
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                           ErrorMsg.ERR_MSG_ILLEGAL_REQUEST))
        action = req['action']
        if action not in self.handler_map:
            logger.error(
                "sorry, we can't handle this request [%s]" % format_params(req))
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                           ErrorMsg.ERR_MSG_CAN_NOT_HANDLE_REQUEST))
        try:
            request = DesktopServerRequest(req).build_internal_request()
            logger.info("DesktopServerRequest request == %s" %(request))
            rep = self.handler_map[action](request)
        except Exception, e:
            logger.exception(
                "handle request [%s] failed, [%s]" % (format_params(req), e))
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR))

        # logging request
        end_time = time.time()
        elapsed_time = end_time - start_time
        if int(elapsed_time) >=const.LONG_HANDLE_TIME:
            logger.critical(
                "handled request [%s], exec_time is [%.3f]s" % (req, elapsed_time))
        else:
            logger.info("handled request [%s], exec_time is [%.3f]s" % (
                str(request), elapsed_time))
        return rep
