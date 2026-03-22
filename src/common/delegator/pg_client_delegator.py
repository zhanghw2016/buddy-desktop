'''
Created on 2014-5-28

@author: yunify
'''

import traceback
import threading
from contextlib import contextmanager
from log.logger import logger
from utils.global_conf import get_updater, is_conf_equal
from db.pg_client import PGClient
from db.pg_pool import PGAuth
from utils.misc import decode_string, explode_array
from utils.thread_local import set_taskware, get_taskware
from constants import (
    DEPLOY_TYPE_EXPRESS,
)
import context

class PGClientDelegator():
    '''
        a PG client proxy which would:
        1) detect config change and generate new pg client accordingly
        2) pg client shall be thread aware, and calls to this object will be delegated to actual pg client
    '''
    
    def __init__(self, db, taskware=False, minconn=0, maxconn=0):
        self.lock = threading.RLock()
        self.tkey = "pg_" + db
        self.db = db
        self.taskware = taskware
        self.pg = None
        self.conf = None
        self.version = None
        self.minconn = minconn if minconn > 0 else 1
        self.maxconn = maxconn
        
    def activate(self):
        # activate client, if this method is not called explicitly, 
        # client will be activated in lazy mode
        client = self._get_client()
        return 0 if client else -1
    
    def __getattr__(self, attr):
        if attr == "open":
            raise "open() method is not allowed to be called explicitly"
        client = self._get_client()
        return getattr(client, attr) if client else None
    
    def _get_client(self):
        ''' get pg client per thread '''
        
        if not self.taskware:
            return self._get_pg()
        
        client = get_taskware(self.tkey)
        if client:
            return client
        
        # get pg object once for one task
        client = self._get_pg()
        if client:
            set_taskware(self.tkey, client)
            return client
        return None
    
    def _get_pg(self):
        ''' get pg client object '''
        
        # lightweight check
        ctx = context.instance()
        updater = get_updater()
        if self.pg:
            if ctx.zone_deploy == DEPLOY_TYPE_EXPRESS:
                (conf, version) = updater.get_conf("postgresql")
            else:
                (conf, version) = updater.get_conf("postgresql_standard")
            if conf != None:
                # if not changed, use current object
                if version == self.version:
                    return self.pg    

        logger.info("detected a conf change: DB [%s]" % self.db)
        with self._lock():
            if ctx.zone_deploy == DEPLOY_TYPE_EXPRESS:
                (conf, version) = updater.get_conf("postgresql")
            else:
                (conf, version) = updater.get_conf("postgresql_standard")

            if conf == None:
                logger.error("connect to PostgreSQL failed: can't get config")
                return None
            conf = conf.get(self.db, conf)
            # if not changed, use current object
            if self.pg:
                # config changed?
                if version == self.version:
                    return self.pg     
                
                # content changed?
                if is_conf_equal(conf, self.conf):
                    self.version = version
                    return self.pg     
                
            # master/slave configure
            conf_m = conf.get("master", conf)        
            conf_s = conf.get("slave")        
                              
            # master db
            pg_host = explode_array(conf_m['host'].strip())
            pg_port = conf_m.get('port', None)
            pg_user = conf_m['user'].strip()
            pg_password = decode_string(conf_m['password'].strip())
            if self.maxconn and self.minconn:
                auth_m = PGAuth(pg_host, pg_user, pg_password, minconn=self.minconn, maxconn=self.maxconn, port=pg_port)
            else:
                auth_m = PGAuth(pg_host, pg_user, pg_password, port=pg_port)
                
            # slave db
            auth_s = None
            if conf_s:
                pg_host = explode_array(conf_s['host'].strip())
                pg_port = conf_s.get('port', None)
                pg_user = conf_s['user'].strip()
                pg_password = decode_string(conf_s['password'].strip())
                if self.maxconn and self.minconn:
                    auth_s = PGAuth(pg_host, pg_user, pg_password, minconn=self.minconn, maxconn=self.maxconn, port=pg_port)
                else:
                    auth_s = PGAuth(pg_host, pg_user, pg_password, port=pg_port)
            
            # connect to postgresql db
            pg = PGClient()
            if 0 != pg.open(self.db, auth_m, auth_s=auth_s):
                logger.error("connect to PostgreSQL [%s] failed" % (pg_host))
                return None
            
            # shallow copy all static attributes of old objects
            if self.pg:
                pg.delete_pre_trigger = self.pg.delete_pre_trigger
                pg.delete_triggers = self.pg.delete_triggers
                pg.update_pre_trigger = self.pg.delete_triggers
                pg.update_triggers = self.pg.update_triggers
                pg.insert_triggers = self.pg.insert_triggers
       
            self.version = version
            self.conf = conf
            self.pg = pg
            logger.info("DB [%s] has been switched" % self.db)
            return pg
    
    @contextmanager
    def _lock(self):
        self.lock.acquire()
        try:
            yield
        except:
            logger.error("yield exits with exception: %s" % traceback.format_exc())
        self.lock.release()
    
