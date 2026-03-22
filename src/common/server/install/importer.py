'''
Created on 2014-12-7

@author: yunify
'''

import os
import sys
import threading
import __builtin__
from log.logger import logger
from log.logger_name import get_logger_name

'''
   Experimental: reload python modules, not stable yet
'''
class RollbackImporter:
    def __init__(self):
        "Creates an instance and installs as the global importer"
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = {}
        
    def _import(self, name, globals_=None, locals_=None, fromlist=[], level=-1):
        result = apply(self.realImport, (name, globals_, locals_, fromlist, level))
        if name not in self.newModules and hasattr(result, '__file__'):
            # record only pitrix modules
            path = os.path.abspath(result.__file__)
            if path.startswith("/pitrix"):
                self.newModules[name] = 1
                logger.info("--> importing %s from [%s]" % (fromlist, name))
        return result
        
    def uninstall(self):
        for modname in self.newModules.keys():
            # Force reload when modname next imported
            if modname in sys.modules:
                del(sys.modules[modname])
                logger.info("--> exporting [%s]" % modname)
        __builtin__.__import__ = self.realImport
        
g_importer = None
def set_importer():
    global g_importer
    g_importer = RollbackImporter()    
    return

g_reload_module_lock = threading.Lock()
def reload_module(server_name):
    global g_reload_module_lock
    
    # get module name
    server_name = get_logger_name() 
    if not server_name:
        logger.critical("get server name failed")
        return -1
    
    # check if only modules needs to be reinstalled
    flag_file = "/pitrix/lib/%s.update_module.flag" % server_name
    if os.path.exists(flag_file):
        global g_importer
        if not g_importer:
            logger.critical("get importer failed, must be initialized")
            return -1     
           
        g_reload_module_lock.acquire()
        # double check
        if os.path.exists(flag_file):
            logger.info("find update module flag, updating...")
            os.unlink(flag_file)
            g_importer.uninstall()
            set_importer()
            logger.info("find update module flag, updated")
        g_reload_module_lock.release()
    
    return 0
