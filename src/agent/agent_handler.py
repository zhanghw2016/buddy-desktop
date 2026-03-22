'''
Created on 2012-5-2

@author: yunify
'''
import traceback
from log.logger import logger
from utils.json import json_load
from constants import (
    REQ_TYPE_CHECK,
    CHK_TYPE_POSTGRESQL,
    CHK_TYPE_QINGCLOUD_SERVER,
    CHK_TYPE_CITRIX_SERVER,
    CHK_TYPE_AUTH_SERVER,
    CHK_TYPE_VNAS_SERVER,
    CLEAN_DESKTOP_CONNECTION_FILE,
    CHK_TYPE_LICENSE,
    CHK_TYPE_SYNC_ZONE_INFO,
    PUSH_SYSLOG,
    CHK_TYPE_CLEAN_UP_LOG,
    REFRESH_DESKTOP_INSTANCE
)
import context
from inspector.service_status import (check_postgresql_status,
                                      check_qingcloud_service_status,
                                      check_auth_service_status,
                                      check_citrix_service_status,
                                      check_vnas_server_status
                                      )
from inspector.clean_connection_file import clean_desktop_connection_file
from inspector.license import check_license
from inspector.sync_zone_info import check_sync_zone_info
from inspector.push_syslog import push_syslogs
from inspector.clean_up_log import check_clean_up_log
from inspector.refresh_desktop_status import refresh_desktop_status

def debug():
    return

def handle_check_postgresql_status():
    ''' check postgresql '''
    check_postgresql_status()

def handle_check_qingcloud_service_status():
    ''' check qingcloud service '''
    check_qingcloud_service_status()

def handle_check_citrix_service_status():
    ''' check citrix service '''
    check_citrix_service_status()

def handle_check_auth_service_status():
    ''' check auth service '''
    check_auth_service_status()

def handle_check_vnas_server_status():
    ''' check vnas server '''
    check_vnas_server_status()

def handle_clean_desktop_connection_file():
    ''' clean spice connection files '''
    clean_desktop_connection_file()

def handle_check_license():
    ''' check license '''
    check_license()

def handle_check_sync_zone_info():
    check_sync_zone_info()

def handle_check_clearn_up_log():
    check_clean_up_log()

def handle_push_syslogs():
    push_syslogs()
    
def handle_refresh_desktop_status():
    
    refresh_desktop_status()

g_module_handlers = []
def _register_extensions():
    ''' find in extensions and load module handler dynamically '''
    
    global g_module_handlers
    exts = []
    for ext in exts:
        handler = ext["test"]
        if handler:
            g_module_handlers.append(handler())
        
def _dispatch_module(chk_type):
    ''' a general request dispatcher '''
    
    global g_module_handlers
    for handler in g_module_handlers:
        if chk_type not in handler.handle_map:
            continue
        return handler.handle(chk_type)
    
    return

def handle_check(req):
    ''' handle check event '''

    params = {}
    if "params" in req:
        params = req["params"]

    
    handle_map = {
        CHK_TYPE_CITRIX_SERVER: handle_check_citrix_service_status,
        CHK_TYPE_POSTGRESQL: handle_check_postgresql_status,
        CHK_TYPE_QINGCLOUD_SERVER: handle_check_qingcloud_service_status,
        CHK_TYPE_AUTH_SERVER: handle_check_auth_service_status,
        CHK_TYPE_VNAS_SERVER: handle_check_vnas_server_status,
        CLEAN_DESKTOP_CONNECTION_FILE: handle_clean_desktop_connection_file,
        CHK_TYPE_LICENSE: handle_check_license,
        CHK_TYPE_SYNC_ZONE_INFO: handle_check_sync_zone_info,
        PUSH_SYSLOG: handle_push_syslogs,
        CHK_TYPE_CLEAN_UP_LOG: handle_check_clearn_up_log,
        REFRESH_DESKTOP_INSTANCE: handle_refresh_desktop_status
    }

    if "type" not in params:
        logger.error("invalid request")
        return
    chk_type = params["type"]

    # dispatch
    ctx = context.instance()
    with ctx.check(chk_type) as is_checking:
        # don't check twice at a time
        if is_checking:
            logger.warn("duplicate checking [%s]" % chk_type)
            return

        try:
            if chk_type in handle_map:
                return handle_map[chk_type]()
            else:
                return _dispatch_module(chk_type)
        except:
            logger.critical("handle [%s] failed: %s" % (req, traceback.format_exc()))
            return

    return

class PullServiceHandler(object):
    ''' long time service handler
    '''

    def __init__(self):
        self.handle_map = {
            REQ_TYPE_CHECK : handle_check
        }
        
        _register_extensions()

    def handle(self, req_msg, title, **kargs):
        try:
            return self._handle(req_msg)
        except:
            logger.critical("handle [%s] failed: %s" % (req_msg, traceback.format_exc()))
            return

    def _handle(self, req_msg):
        ''' no return'''
        # decode to request object
        req = json_load(req_msg)
        if req == None:
            logger.error("invalid request: %s" % req_msg)
            return

        if "req_type" not in req:
            logger.error("invalid request: %s" % req_msg)
            return

        # get message handler
        req_type = req["req_type"]
        if req_type not in self.handle_map:
            logger.error("invalid request: %s" % req_msg)
            return

        # handle it
        self.handle_map[req_type](req)
