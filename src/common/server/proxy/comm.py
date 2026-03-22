'''
Created on 2013-1-2

@author: yunify
'''

import os
import threading
import time
import traceback
from contextlib import contextmanager
from base_client import ReqLetter
from server.proxy import context
from log.logger import logger
from utils.misc import exec_cmd
from common import REP_SHUTDOWN, REP_ERROR

g_backend_lock = threading.RLock()

@contextmanager
def _backend_lock():
    global g_backend_lock
    g_backend_lock.acquire()
    try:
        yield
    except:
        logger.critical("yield exits with exception: %s" % traceback.format_exc())
    g_backend_lock.release()
    
g_backend_pid = None
def _get_backend_pid(port, force=False):
    global g_backend_pid
    if not force and g_backend_pid != None:
        return g_backend_pid
    
    with _backend_lock():   
        g_backend_pid = None
        ret = exec_cmd("netstat -tlnp | grep '127.0.0.1:%s ' | awk '{print $NF}' | awk -F'/' '{print $1}'" % port)
        if ret != None and ret[1] != "":
            g_backend_pid = ret[1]
    
    return g_backend_pid

def _is_backend_listening(port):
    pid = _get_backend_pid(port)
    if pid != None:
        if os.path.exists("/proc/" + pid):
            return True
    
    # backend may be restarting, need to wait until port is listening
    pid = _get_backend_pid(port, True)
    if pid != None:
        return True
            
    return False

def send_message(req_msg, title, timeout):
    ''' send message to backend and wait for reply '''
    
    ctx = context.instance()
    letter = ReqLetter("tcp://127.0.0.1:%s" % (ctx.back_port), req_msg, title)
    
    # send message to backend:
    # 1) if backend is normal, then client shall get response after message is processed by backend handler
    # 2) if backend is shutting down, then :
    #    - if message is synchronous, client will get normal response
    #    - if message is asynchronous, client will get SHUTDOWN response, and we will wait here
    # 3) if backend is restarting, client will hang and will get response when backend gets up
    starttime = time.time()
    while time.time() < starttime + timeout:        
        # send message only when backend is listening, otherwise message may be lost
        if not _is_backend_listening(ctx.back_port):
            logger.info("handle request: backend server is starting: [%s]" % (req_msg))  
            time.sleep(3)
            continue
        old_pid = _get_backend_pid(ctx.back_port)
            
        rep = ctx.client.send(letter, timeout=timeout, to_crypt=False)
        
        # error occurred, reply with error
        if rep == None:
            # if timeout, normally it means backend is restarting while sending message
            new_pid = _get_backend_pid(ctx.back_port, True)
            if old_pid != new_pid:
                logger.info("handle request failed: backend server is starting: [%s], retry..." % (req_msg))  
                continue
            break
        
        # backend getting down, wait a little while
        if rep == REP_SHUTDOWN:     
            logger.info("handle request: backend server is shutting down: [%s]" % (req_msg))  
            
            # wait until backend is started
            endtime = starttime + (timeout if timeout < 180 else 180)
            while time.time() < endtime:
                new_pid = _get_backend_pid(ctx.back_port, True)
                if old_pid != new_pid:
                    break
                time.sleep(3)
            continue
        
        # normal result
        return rep
    
    logger.error("something error: request [%s], title [%s], timeout [%s]",
                 req_msg, title, timeout)
    return REP_ERROR
