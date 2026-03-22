'''
Created on 2012-5-2

@author: yunify
'''

import time
import threading
from server.proxy.comm import send_message
from log.logger import logger

g_async_counter=0
g_async_lock=threading.RLock()
class PullServiceHandler(object):
    ''' handler '''
    
    def handle(self, req_msg, title, **kargs):
        ''' @return no reply message '''
        global g_async_counter, g_async_lock
        
        g_async_lock.acquire()
        g_async_counter += 1
        req_id = g_async_counter
        g_async_lock.release()

        stime = time.time()  
        logger.info("enter async request: id[%d] req[%s]" % (req_id, req_msg)) 
        rep = send_message(req_msg, title, timeout=30)  
        etime = time.time()
        exec_time = etime - stime
        logger.info("exit async request: id[%d] rep[%s] tt[%.3f]s" % (req_id, rep, exec_time))   
        return
