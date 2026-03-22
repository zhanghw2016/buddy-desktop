'''
Created on 2012-5-6

@author: yunify
'''
from mc.constants import MC_EXPIRES_TIME
from log.logger import logger

class MCModel():
    ''' mc client for common request '''

    def __init__(self, mc):
        self.mc = mc
        
    def _get_complete_key(self, prefix, key):
        ''' get mc key '''
        return "%s.%s" % (prefix, key)
        
    def set(self, prefix, key, val, time=None):
        ''' set key-value pair '''
        if time is None and prefix not in MC_EXPIRES_TIME:
            logger.error("expires time not found for prefix [%s]" % prefix)
            return False
        time = MC_EXPIRES_TIME[prefix] if time is None else time
        return self.mc.set(self._get_complete_key(prefix, key), val, time)
    
    def get(self, prefix, key):
        ''' get key '''
        return self.mc.get(self._get_complete_key(prefix, key))
    
    def delete(self, prefix, key):
        ''' delete key '''
        return self.mc.delete(self._get_complete_key(prefix, key))
    
    def incr(self, prefix, key, delta=1):
        ''' incr value '''
        return self.mc.incr(self._get_complete_key(prefix, key), delta)
    
    def decr(self, prefix, key, delta=1):
        ''' decr value '''
        return self.mc.decr(self._get_complete_key(prefix, key), delta)
