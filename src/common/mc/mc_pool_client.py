'''
Created on 2014-9-24

@author: yunify
'''
import Queue
import memcache
from log.logger import logger

# Don't inherit client from threading.local so that we can reuse clients in
# different threads
memcache.Client = type('Client', (object,), dict(memcache.Client.__dict__))

# Client.__init__ references local, so need to replace that, too
class Local(object): pass
memcache.local = Local

class PoolClient(object):
    '''Pool of memcache clients that has the same API as memcache.Client'''

    def __init__(self, pool_size, pool_timeout, *args, **kwargs):
        self.pool_timeout = pool_timeout
        self.queue = Queue.Queue()
        for _i in range(pool_size):
            self.queue.put(memcache.Client(*args, **kwargs))

    def __getattr__(self, name):
        return lambda *args, **kw: self._call_client_method(name, *args, **kw)

    def _call_client_method(self, name, *args, **kwargs):
        try:
            client = self.queue.get(timeout=self.pool_timeout)
        except Queue.Empty:
            logger.critical('PoolClient queue is empty')
            return None

        try:
            return getattr(client, name)(*args, **kwargs)
        finally:
            self.queue.put(client)
