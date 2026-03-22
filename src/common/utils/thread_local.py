'''
Created on 2012-6-21

@author: yunify
'''

import time
import threading
from M2Crypto.EVP import Cipher as CP

# thread local object
g_thr_local = threading.local()

def current_timestamp():
    ''' current timestamp in microseconds '''
    return int(time.time() * 1e6)

def get_msg_timestamp():
    ''' get message timestamp of current thread  '''
    if not hasattr(g_thr_local, "msg_timestamp"):
        g_thr_local.msg_timestamp = current_timestamp()
    return g_thr_local.msg_timestamp

def reset_msg_timestamp():
    ''' reset message timestamp of current thread  '''
    g_thr_local.msg_timestamp = current_timestamp()
    
def set_msg_timestamp(timestamp):
    ''' set message timestamp of current thread '''
    g_thr_local.msg_timestamp = timestamp
 
def get_msg_id():
    ''' get message id of current thread  '''
    if not hasattr(g_thr_local, "msg_id"):
        g_thr_local.msg_id = ""
    return g_thr_local.msg_id

def reset_msg_id():
    ''' reset message id of current thread  '''
    g_thr_local.msg_id = ""
    
def set_msg_id(msg_id):
    ''' set message id of current thread '''
    g_thr_local.msg_id = msg_id
    
def get_trigger_resource():
    ''' get resource info of trigger event  '''
    if not hasattr(g_thr_local, "trigger_resource"):
        g_thr_local.trigger_resource = None
    # get once and remove it
    resource = g_thr_local.trigger_resource
    g_thr_local.trigger_resource = None
    return resource

def set_trigger_resource(resource_info):
    ''' set resource info of trigger event '''
    g_thr_local.trigger_resource = resource_info
    
def is_pg_proxied(db):
    ''' if pg pool allow proxy mode  '''
    if hasattr(g_thr_local, "pg_proxy") and db in g_thr_local.pg_proxy:
        return g_thr_local.pg_proxy[db]
    return True

def enable_pg_proxy(db):
    ''' set pg to use proxy mode, that is to allow read/write separation '''
    if not hasattr(g_thr_local, "pg_proxy"):
        g_thr_local.pg_proxy = {}
    g_thr_local.pg_proxy[db] = True
    
def disable_pg_proxy(db):
    ''' disable proxy mode, that is to disallow read/write separation, all sql operations will go to rw pool '''
    if not hasattr(g_thr_local, "pg_proxy"):
        g_thr_local.pg_proxy = {}
    g_thr_local.pg_proxy[db] = False
    
'''
    All taskware objects will be cleared when task is done
'''
def get_taskware(key):
    if hasattr(g_thr_local, "taskware") and key in g_thr_local.taskware:
        return g_thr_local.taskware[key]
    return None

def clear_taskware():
    if hasattr(g_thr_local, "taskware"):
        g_thr_local.taskware = {}
    return
    
def set_taskware(key, val):
    if not hasattr(g_thr_local, "taskware"):
        g_thr_local.taskware = {}
    g_thr_local.taskware[key] = val
    
'''
    file lock object
    it is used for FileLock to be remote-calling-aware and 
    to prevent dead lock
'''
def get_flock_obj():
    if not hasattr(g_thr_local, "flock_obj"):
        return (set(), None)
    return g_thr_local.flock_obj

def reset_flock_obj():
    g_thr_local.flock_obj = (set(), None)
    
def set_flock_obj(name, host):
    g_thr_local.flock_obj = (name, host)

def get_flock_name():
    if not hasattr(g_thr_local, "flock_name"):
        return set()
    return g_thr_local.flock_name

def set_flock_name(name):
    if not hasattr(g_thr_local, "flock_name"):
        g_thr_local.flock_name = set()
    g_thr_local.flock_name.add(name.encode("ascii"))

def clear_flock_name(name):
    if not hasattr(g_thr_local, "flock_name"):
        return
    if name in g_thr_local.flock_name:
        g_thr_local.flock_name.remove(name)
    return

def reset_flock_name():
    g_thr_local.flock_name = set()


class BaseThreadProcessor(object):
    def __init__(self, func=None, *args):
        ''' 
        @key process: None for failed
        '''
        if not callable(func):
            raise Exception("not callable function [%s]", func)
        self.func = func
        self.args = args
        self._cur_timeout = None
        
        # None for failed
        self.process = None
        self.thread = None
    
    def terminate(self):
        raise NotImplementedError
    
    def run(self, timeout=10):
        ''' the strict=False be able to use that the function "be not Daemon" '''
        def target():
            self.process = None
            self.process = self.func(*self.args)
            
        thread = threading.Thread(target=target)
        self.thread = thread
        thread.start()
        if timeout:
            self._cur_timeout = timeout
            thread.join(int(timeout))
            if thread.is_alive():
                self.terminate()
                thread.join()
            return self.process
