'''
Created on 2012-10-15

@author: yunify
'''
from log.logger import logger
from mc.mc_pool_client import PoolClient

class MCClient():
    ''' a thread-safe client for memcached '''
    
    SERVER_MAX_KEY_LENGTH = 250     # max key length
    DEAD_RETRY = 30                 # number of seconds before retrying a dead server.
    SOCKET_TIMEOUT = 3              # number of seconds before sockets timeout.
    
    def __init__(self, servers, 
                 debug=0,
                 server_max_key_length=SERVER_MAX_KEY_LENGTH,
                 dead_retry=DEAD_RETRY,
                 socket_timeout=SOCKET_TIMEOUT,
                 pool_size=100,
                 pool_timeout=10,
                 ):
        # init memcache client
        self.mc = PoolClient(
                pool_size=pool_size,
                pool_timeout=pool_timeout,
                servers=servers, 
                debug=debug, 
                server_max_key_length=server_max_key_length,
                dead_retry=dead_retry, 
                socket_timeout=socket_timeout)
        
    def set(self, key, val, time=60, min_compress_len=0):
        ''' set key-value 
            @param key: key must be str type. 
            @param time: a delta number of seconds which this value should expire,
                         default is 60s and time = 0 means cache forever.
            @return: True on success and False on failed.
        '''
        try:
            ret = self.mc.set(str(key), val, time, min_compress_len)
            if ret == 0:
                logger.error("mc-client set [%s,%s] failed" % (key, val))
                return False
        except Exception, e:
            logger.error("mc-client set failed: %s" % e)
            return False 
        return True
    
    def set_multi(self, mapping, time=60, key_prefix='', min_compress_len=0):        
        ''' multi-set key-value pairs
            @param mapping:  A dict of key/value pairs to set.
            @param time: a delta number of seconds which this value should expire,
                         default is 60s and time = 0 means cache forever.
            @param key_prefix: Optional string to prepend to each key 
                                when sending to memcache.
            @return: True on success and False on failed.
        '''   
        try:
            ret = self.mc.set_multi(mapping, time, key_prefix, min_compress_len)  
            if len(ret) != 0:
                logger.error("mc-client set_multi [%s] failed, failed items: [%s]" % (mapping, ret))
                return False
        except Exception, e:
            logger.error("mc-client set_multi failed: %s" % e)
            return False 
        return True
            
    def get(self, key):
        ''' get key 
            @param key: key must be str type. 
            @return: not None value if succeeded and None if failed.
        '''
        try:
            ret = self.mc.get(str(key))
        except Exception, e:
            logger.error("mc-client get failed: %s" % e)
            return None 
        return ret
        
    def get_multi(self, keys, key_prefix=''):
        ''' get key 
            @param keys: a list of keys you want to get. 
            @return: A dictionary of key/value pairs that were available if succeeded and None if failed.
                     If key_prefix was provided, the keys in the retured dictionary 
                     will not have it present.
        '''
        try:
            ret = self.mc.get_multi(keys, key_prefix)
        except Exception, e:
            logger.error("mc-client get_multi failed: %s" % e)
            return None 
        return ret
    
    def incr(self, key, delta=1):
        ''' incr value 
            @param key: key must be str type. 
            @param delta: Integer amount to increment by (should be zero or greater).
            @return: New value after incrementing or None if incrementing failed.
            Note: key must existed and its value must in non-negative integer 
                  before you can increment it.
        '''
        try:
            ret = self.mc.incr(str(key), delta)
            if ret is None or ret == 0:
                logger.error("mc-client incr [%s] failed" % (key))
                return None
        except Exception, e:
            logger.error("mc-client incr failed: %s" % e)
            return None
        return ret
    
    def decr(self, key, delta=1):
        ''' decr value 
            @param key: key must be str type. 
            @param delta: Integer amount to decrement by (should be zero or greater).
            @return: New value after decrementing or None if decrementing failed..
            Note: key must existed and its value must in non-negative integer 
                  before you can decrement it.
        '''
        try:
            ret = self.mc.decr(str(key), delta)
            # Note: sometimes ret = 0 means decr failed but we ignore it here.
            if ret is None:
                logger.error("mc-client decr [%s] failed" % (key))
                return None
        except Exception, e:
            logger.error("mc-client decr failed: %s" % e)
            return None 
        return ret 

    def add(self, key, val, time=60, min_compress_len=0):
        ''' add key-value, like set, but only stores in memcache if the key doesn't already exist.
            @param key: key must be str type. 
            @param time: a delta number of seconds which this value should expire,
                         default is 60s and time = 0 means cache forever.
            @return: True on success and False on failed.
        '''
        try:
            ret = self.mc.add(str(key), val, time, min_compress_len)
            if ret == 0:
                logger.error("mc-client add [%s,%s] failed" % (key, val))
                return False
        except Exception, e:
            logger.error("mc-client add failed: %s" % e)
            return False 
        return True
    
    def delete(self, key, time=0):
        ''' delete a key 
            @param key: key must be str type. 
            @param time: number of seconds any subsequent set / update commands
                         should fail. Defaults to None for no delay.
            @return: True on success and False on failed.
        '''
        try:
            ret = self.mc.delete(str(key), time)
            if ret == 0:
                logger.error("mc-client delete [%s] failed" % (key))
                return False
        except Exception, e:
            logger.error("mc-client delete failed: %s" % e)
            return False 
        return True      
        
