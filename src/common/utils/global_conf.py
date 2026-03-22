
import os
import time
import threading
import traceback
from contextlib import contextmanager
from log.logger import logger
from utils.yaml_tool import yaml_load
from utils.misc import get_file_mtime

from constants import (
    DEPLOY_TYPE_EXPRESS,
)
import context


CONF_HOME = '/pitrix/conf/desktop/'
GLOBAL_CONF_HOME = '/pitrix/conf/global/'

CONF_DESKTOP_YAML = 'desktop.yaml'
CONF_ZONE_CONFIG_YAML = 'zone_config.yaml'
CONF_RESOURCE_LIMIT_YAML = 'resource_limit.yaml'

def _get_conf(conf_file):
    if not os.path.exists(conf_file):
        return None
    
    try:
        with open(conf_file, "r") as fd:
            conf = yaml_load(fd)
    except:
        return None

    return conf

def is_conf_equal(a, b):
    if isinstance(a, dict):
        if not isinstance(b, dict):
            return False
        for key in a.iterkeys():
            if key not in b:
                return False
            if not is_conf_equal(a[key], b[key]):
                return False
        return True
    
    if isinstance(a, list):
        if not isinstance(b, list):
            return False
        if len(a) != len(b):
            return False
        for i in xrange(len(a)):
            if not is_conf_equal(a[i], b[i]):
                return False
        return True
        
    return a == b

class GlobalConfUpdater(threading.Thread):
    ''' updater to update global conf if there is any updates '''
    
    def __init__(self):
        super(GlobalConfUpdater, self).__init__()
        
        self.lock = threading.RLock()
        self.conf = {
            "postgresql": (None, None),
            "server": (None, None),
        }
    
    def run(self):
        from server.install.installer import restart_server, clear_restart_server_flag
        
        # restart server flag shall be cleaned when server is started
        clear_restart_server_flag()
    
        while True:
            try: 
                for key in self.conf.iterkeys():
                    self._load(key)
                
                # do restart server check
                restart_server()
                
                time.sleep(1)
            except Exception, e:
                logger.critical("updating global conf failed: %s" % e)
                time.sleep(1)
     
    def get_conf(self, key):
        (conf, version) = self.conf.get(key, (None, None))
        if conf:
            return (conf, version)
        
        # this may happen when updater is not fully started
        # in this case have to force loading
        self._load(key)
        return self.conf.get(key, (None, None))
    
    def _load(self, key):
        with self._lock():
            conf_file = self._get_conf_file(key)
            (old_conf, old_version) = self.conf.get(key, (None, None))
            new_version = get_file_mtime(conf_file)
            
            # not changed
            if old_conf and new_version == old_version:
                return 0
        
            # get new conf
            new_conf = _get_conf(conf_file)
            if not new_conf:
                return -1
            
            self.conf[key] = (new_conf, new_version)
            return 0
    
    def _get_conf_file(self, key):
        return GLOBAL_CONF_HOME + key + ".yaml"
    
    @contextmanager
    def _lock(self):
        self.lock.acquire()
        try:
            yield
        except:
            logger.error("yield exits with exception: %s" % traceback.format_exc())
        self.lock.release()
    
g_global_conf_updater = None
def get_updater():
    ''' get global conf updater '''
    global g_global_conf_updater
    if not g_global_conf_updater:
        g_global_conf_updater = GlobalConfUpdater()
        g_global_conf_updater.setDaemon(True)
        g_global_conf_updater.start()
    return g_global_conf_updater

g_ssh_port = None
def get_ssh_port():

    global g_ssh_port
    if g_ssh_port is None:
        g_ssh_port = int(_get_conf(CONF_HOME + CONF_DESKTOP_YAML)['ssh_port'])
        
    return g_ssh_port

#############################################################
#                        DESKTOP
#############################################################
g_desktop_conf = None
def get_desktop_conf():
    global g_desktop_conf
    if g_desktop_conf is None:
        g_desktop_conf = _get_conf(CONF_HOME + CONF_DESKTOP_YAML)
    return g_desktop_conf

g_zone_conf = None
def get_zone_conf():
    global g_zone_conf
    if g_zone_conf is None:
        g_zone_conf = _get_conf(CONF_HOME + CONF_ZONE_CONFIG_YAML)
    return g_zone_conf

g_resource_limit_conf = None
def get_resource_limit_conf():
    global g_resource_limit_conf
    if g_resource_limit_conf is None:
        g_resource_limit_conf = _get_conf(CONF_HOME + CONF_RESOURCE_LIMIT_YAML)
    return g_resource_limit_conf

#############################################################
#                        POSTGRESQL
#############################################################
g_postgresql_conf = None
def get_postgresql_conf():
    ctx = context.instance()
    global g_postgresql_conf
    if g_postgresql_conf is None:
        if ctx.zone_deploy == DEPLOY_TYPE_EXPRESS:
            g_postgresql_conf = _get_conf(GLOBAL_CONF_HOME + "postgresql.yaml")
        else:
            g_postgresql_conf = _get_conf(GLOBAL_CONF_HOME + "postgresql_standard.yaml")
    return g_postgresql_conf

g_pg_delegator = {}
def get_pg(db_name, minconn=0, maxconn=0):
    global g_pg_delegator
    if not g_pg_delegator or db_name not in g_pg_delegator:
        from delegator.pg_client_delegator import PGClientDelegator
        g_pg_delegator[db_name] = PGClientDelegator(db_name, minconn=minconn, maxconn=maxconn)
    return g_pg_delegator[db_name]

#############################################################
#                        MEMCACHE
#############################################################
g_mc_conf = None
def get_mc_conf():
    global g_mc_conf
    ctx = context.instance()
    if g_mc_conf == None:
        if ctx.zone_deploy == DEPLOY_TYPE_EXPRESS:
            g_mc_conf = _get_conf(GLOBAL_CONF_HOME + "memcached.yaml")
        else:
            g_mc_conf = _get_conf(GLOBAL_CONF_HOME + "memcached_standard.yaml")
    
    return g_mc_conf

def get_mc(conf=None):
    if conf == None:
        conf = get_mc_conf()
        if conf == None:
            logger.error("connect to memcached failed: can't get config")
            return None
        
    # connect to memcached
    from mc.mc_client import MCClient
    mc_hosts = conf['mc_hosts'].strip().split(";")
    mc = MCClient(mc_hosts)
    return mc

