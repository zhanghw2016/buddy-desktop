'''
Created on 2018-5-15

@author: yunify
'''
import threading
import threadpool
import traceback
import error.error_msg as ErrorMsg
import error.error_code as ErrorCodes
from error.error import Error
from common import return_error
from utils.json import json_load
from utils.misc import format_params
from log.logger import logger
import constants as const
from request.terminal_agent_request import TerminalAgentRequest
import handler.terminal_agent_handler as TerminalAgentHandler
from response.response_handler import send_response_to_terminal

class TerminalAgentSocketHandler(object):
    ''' socket service handler '''
    handler = {
        # handle request
        const.REQUEST_SPICE_AGENT_PING: TerminalAgentHandler.handle_ping,
        const.REQUEST_SPICE_AGENT_REGISTER: TerminalAgentHandler.handle_register,
        const.REQUEST_SPICE_AGENT_UNREGISTER: TerminalAgentHandler.handle_unregister,
        const.REQUEST_SPICE_AGENT_SPICE_CONNECTED: TerminalAgentHandler.handle_spice_connected,
        const.REQUEST_SPICE_AGENT_SPICE_DISCONNECTED: TerminalAgentHandler.handle_spice_disconnected,

        # handle response
        const.RESPONSE_TERMINAL_SERVER_MODIFY_TERMINAL: TerminalAgentHandler.handle_modify_terminal_response,
        const.RESPONSE_TERMINAL_SERVER_RESTART_TERMINAL: TerminalAgentHandler.handle_restart_terminal_response,
        const.RESPONSE_TERMINAL_SERVER_STOP_TERMINAL: TerminalAgentHandler.handle_stop_terminal_response,
        const.RESPONSE_VDAGENT_SERVER_ONLINE_UPGRADE_TERMINAL: TerminalAgentHandler.handle_online_upgrade_terminal_response
        }

    @classmethod
    def handle(cls, req):
        try:
            # check request type
            logger.info("handle socket req: [%s]" % req)
            if "type" not in req:
                logger.error("[type] should be provided in request [%s]" %
                             format_params(req))
                rep = return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                              ErrorMsg.ERR_MSG_MISSING_PARAMETER, "type"))
                if send_response_to_terminal(req["server"], req["sock"], rep) < 0:
                    logger.error("send res_str [%s] error" % rep)
                return

            req_type = req.pop("type")
            if req_type != const.REQUEST_TYPE_SPICE_AGENT:
                logger.error("illegal type [%s]" % (req_type))
                rep = return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                              ErrorMsg.ERR_MSG_ILLEGAL_REQUEST))
                if send_response_to_terminal(req["server"], req["sock"], rep) < 0:
                    logger.error("send res_str [%s] error" % rep)
                return

            request = TerminalAgentRequest(req).build_internal_request()
            if request is None:
                rep = return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                              ErrorMsg.ERR_MSG_ILLEGAL_REQUEST))
                if send_response_to_terminal(req["server"], req["sock"], rep) < 0:
                    logger.error("send res_str [%s] error" % rep)
                return

            # check request type
            if "action" not in request.keys():
                rep = return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                              ErrorMsg.ERR_MSG_ILLEGAL_REQUEST))
                if send_response_to_terminal(req["server"], req["sock"], rep) < 0:
                    logger.error("send res_str [%s] error" % rep)
                return
            # handle
            action = request['action']
            if action not in cls.handler.keys():
                rep = return_error(req, Error(ErrorCodes.INVALID_REQUEST_METHOD,
                                              ErrorMsg.ERR_CODE_MSG_INVALID_REQUEST_METHOD))
                if send_response_to_terminal(req["server"], req["sock"], rep) < 0:
                    logger.error("send res_str [%s] error" % rep)
                return

            if action.endswith(const.IS_VDAGENT_RESPONSE):
                ret = cls.handler[action](request)
                if ret < 0:
                    logger.error("handle action [%s] with response: [%s] error" % (action, request))
            else:
                rep = cls.handler[action](request)
                if send_response_to_terminal(req["server"], req["sock"], rep) < 0:
                    logger.error("send res_str [%s] error" % rep)
            return
        except:
            logger.critical("handle failed: [%s]" % (traceback.format_exc()))
            rep = return_error(req, Error(ErrorCodes.INTERNAL_ERROR))
            if send_response_to_terminal(req["server"], req["sock"], rep) < 0:
                logger.error("send res_str [%s] error" % rep)
            return


class TerminalAgentServiceHandler:
    def __init__(self, thread_num = 10):
        self.pool = threadpool.ThreadPool(thread_num) 
        self.lock = threading.Lock()

    def handle(self, server, sock, req, **kargs):
        self.lock.acquire()
        try:
            if server is None or sock is None or req is None:
                logger.error("paramters [server socket req] is None")
                self.lock.release()
                return -1

            req = json_load(req)
            req.update({"server": server})
            req.update({"sock": sock})
            requests = threadpool.makeRequests(TerminalAgentSocketHandler.handle, [req])
            [self.pool.putRequest(request) for request in requests]
            self.pool.wait()
            self.lock.release()
            return 0
        except:
            logger.critical("handle failed: [%s]" % (traceback.format_exc()))
            self.lock.release()
            return -1
