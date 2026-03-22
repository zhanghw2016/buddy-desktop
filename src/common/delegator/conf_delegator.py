'''
Created on 2014-5-28

@author: yunify
'''

import traceback
import threading
from contextlib import contextmanager
from log.logger import logger
from utils.global_conf import get_updater
from utils.misc import explode_array

class ConfWrapper():
    def __init__(self, conf, handlers):
        self.conf = conf
        self.handlers = handlers
        self._conf = {}
        
    def get(self, key, default=None):
        val = self.__getitem__(key)
        return val if val is not None else default
    
    def keys(self):
        return self.conf.keys()

    def iterkeys(self):
        return self.conf.iterkeys()

    def iteritems(self):
        return iter([(key, self.__getitem__(key)) for key in self.conf.iterkeys()])

    def __str__(self):
        return self.conf.__str__()

    def __setitem__(self, key, val):
        if isinstance(val, ConfWrapper):
            val = val.conf
        self.conf[key] = val

    def __getitem__(self, key):
        # return internal value
        if key in self._conf:
            return self._conf[key]
        
        # original key matched
        val = self.conf.get(key)
        if val is not None:
            if isinstance(val, dict):
                val = ConfWrapper(val, self.handlers)
            self._conf[key] = val
            return val
        
        # original key just has no value
        parts = key.split("#")
        if len(parts) == 1:
            self._conf[key] = val
            return val
        
        # special key with specific type
        vtype = parts[0]
        vkey = parts[1]
        val = self.conf.get(vkey)
        if val:
            if vtype in self.handlers:
                try:
                    val = self.handlers[vtype](val)
                except Exception, e:
                    logger.critical("global conf parse error for type [%s], %s" % (vtype, e))
                    logger.error("traceback: %s", traceback.format_exc())
                    
        self._conf[key] = val  # set back
        return val

    def __contains__(self, key):
        return key in self.conf

    def __iter__(self):
        return self.conf.__iter__()


class ConfDelegator():
    
    def __init__(self, name):
        self.lock = threading.RLock()
        self.name = name
        self.conf = None
        self.version = None
        self.handlers = {"A" : explode_array}
        
    def register(self, val_type, handler):
        self.handlers[val_type] = handler
        
    def get(self, key, default=None):
        val = self.__getitem__(key)
        return val if val is not None else default

    def __nonzero__(self):
        self._get_client()
        return True if self.conf else False

    def __str__(self):
        return self.conf.__str__()
        
    def __getitem__(self, key):
        client = self._get_client()
        return client.get(key) if client else None
    
    def __contains__(self, key):
        client = self._get_client()
        return key in client if client else False

    def _get_client(self):
        ''' get client '''      
          
        # lightweight check
        updater = get_updater()
        if self.conf:
            (conf, version) = updater.get_conf(self.name)
            if conf != None:
                # if not changed, use current object
                if version == self.version:
                    return self.conf    
            
        logger.info("detected a conf change: %s" % self.name)
        with self._lock():
            # double check
            (conf, version) = updater.get_conf(self.name)
            if conf == None:
                logger.error("can't get config")
                return None
            
            # if not changed, use current object
            if self.conf:
                # config changed?
                if version == self.version:
                    return self.conf     
                 
            self.version = version
            self.conf = ConfWrapper(conf, self.handlers)
            logger.info("%s conf has been switched" % self.name)
            return self.conf
        
    @contextmanager
    def _lock(self):
        self.lock.acquire()
        try:
            yield
        except:
            logger.error("yield exits with exception: %s" % traceback.format_exc())
        self.lock.release()
    
