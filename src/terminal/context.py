'''
Created on 2012-5-5

@author: yunify
'''

from utils.global_conf import get_desktop_conf
from constants import DESKTOP_SERVER_ATTR
g_desktop_conf = None
from log.logger import logger
import resource.terminal as Terminal
import constants as const

class TerminalContext():
    ''' thread context for vdi server 
    '''
    def __init__(self):
        # postgresql
        self.pg = None
        self.pgm = None

        # program pid
        self.pid = None

        # uuid check
        self.checker = None
        
        # memcache client
        self.mcclient = None
        self.mcm = None

        # resources
        self.resources = None

        self.zone_builder = None
        self.zone_checker = None
        self.zones = None
        self.zone_users = None
        self.zone_deploy = None

        # server conf
        self.server_conf = {}
        
        # third auth object
        self.auth = None

        # conf
        self.conf = None

        # terminal agent, key:terminal_mac, value: sender
        self.terminals = {}

        # send agent request, key: request_id, value: response
        self.terminal_request = {}

        # client
        self.client = None

    def __getattr__(self, attr):
        # get conf short cut
        global g_desktop_conf
        try:
                        
            if attr in DESKTOP_SERVER_ATTR:
                desktop_conf = get_desktop_conf()
                if not desktop_conf:
                    return None
                return desktop_conf.get(attr)

        except: 
            pass
        
        return None

    def socket_close_callback(self, sock):
        logger.info("call close socket callback")
        try:
            for sender in self.terminals.values():
                if sender is not None and sender.get("sock") == sock:
                    terminal_mac = sender.get("terminal_mac")
                    logger.info("find terminal_mac [%s]" % terminal_mac)
                    if terminal_mac:
                        self.terminals.pop(terminal_mac)
                        logger.info("Socket close refresh terminal status to be inactive")
                        Terminal.update_terminal_management_status(sender,terminal_mac=terminal_mac,status = const.TERMINAL_STATUS_INACTIVE)
                    break
        except Exception,e:
            logger.error("call close socket callback exception: %s" % e)
        
g_terminal_ctx = TerminalContext()
def instance():
    ''' get terminal server context '''
    global g_terminal_ctx
    return g_terminal_ctx
