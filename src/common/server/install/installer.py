'''
Created on 2014-12-7

@author: yunify
'''

import os
import signal
from log.logger import logger

g_restart_server_flag = ""
def get_restart_server_flag():
    global g_restart_server_flag
    if not g_restart_server_flag:
        # get module name
        from log.logger_name import get_logger_name
        server_name = get_logger_name() 
        if not server_name:
            logger.critical("get server name failed")
            return g_restart_server_flag

        g_restart_server_flag = "/pitrix/lib/%s.restart_server.flag" % server_name
    
    return g_restart_server_flag

def clear_restart_server_flag():
    flag_file = get_restart_server_flag()
    if os.path.exists(flag_file):
        os.unlink(flag_file)
        logger.info("restart server flag is cleared")
    return

g_shutting_down = False
def restart_server():
    # check if server shall restart to reinstall
    global g_shutting_down
    flag_file = get_restart_server_flag()
    if os.path.exists(flag_file):
        if not g_shutting_down:
            from utils.misc import get_program_pid
            logger.info("find restart server flag, restarting...")
            g_shutting_down = True
            os.kill(get_program_pid(), signal.SIGTERM)
    
    return 0