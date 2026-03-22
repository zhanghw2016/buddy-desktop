'''
Created on 2012-5-2

@author: yunify
'''

import time
import threading
from server.proxy import context
from log.logger import logger
from base_client import send_to_pull
from common import REP_OK, KEY_ARG_TIMEOUT, REP_ERROR
from server.proxy.comm import send_message
from utils.json import json_load

g_sync_counter=0
g_sync_lock=threading.RLock()
class ServiceHandler(object):
    ''' handler '''
    
    def handle(self, req_msg, title, **kargs):
        ''' @return reply message '''
        global g_sync_counter, g_sync_lock
        ctx = context.instance()
               
        # for asynchronous message, relay to pull server and reply immediately
        # title must stand for request type when client sends this kind of message
        req_type = title
        if req_type in ctx.async_reqs:
            if 0 != send_to_pull(ctx.pull_url, json_load(req_msg), title):
                return REP_ERROR
            return REP_OK
        
        g_sync_lock.acquire()
        g_sync_counter += 1
        req_id = g_sync_counter
        g_sync_lock.release()

        # for synchronous message, send to backend directly
        # timeout is meaningful only for sync messages
        # for asynchronous messages, proxy only makes sure it can be replayed to backend
        timeout = kargs[KEY_ARG_TIMEOUT] if kargs.get(KEY_ARG_TIMEOUT) else 120      
        stime = time.time()
        logger.info("enter sync request: id[%d] req[%s] to[%d]" % (req_id, req_msg, timeout))     
        rep = send_message(req_msg, title, timeout=timeout)   
        etime = time.time()
        exec_time = etime - stime
        if exec_time < 3:
            logger.info("exit sync request: id[%d] rep[%s] tt[%.3f]s" % (req_id, rep, exec_time))  
        else:
            logger.warn("[LONG_TIME_REQ] exit sync request: id[%d] rep[%s] tt[%.3f]s" % (req_id, rep, exec_time))   
        return rep
            
