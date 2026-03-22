'''
Created on 2013-1-9

@author: yunify
'''

import time
import threading
import traceback
from log.logger import logger
from server.shutdown import manager
from common import REP_SHUTDOWN, REP_ERROR
from utils.misc import exit_program, format_timestamp

g_shutdown_hook = None
def set_shutdown_hook(hook):
    global g_shutdown_hook
    g_shutdown_hook = hook

def on_gracefully_shutdown(a=None, b=None):
    # already shutting down?   
    sdmgr = manager.instance()
    if sdmgr.is_shutting_down():
        return
    
    logger.warn("signal term received, exiting...") 
    sdmgr.wait_for_shutdown()
    
    global g_shutdown_hook
    if g_shutdown_hook:
        g_shutdown_hook()
        
    exit_program(-1)
    
g_sync_msg_lock = threading.RLock()
g_sync_msg_key = 0
g_sync_msg_left = {}
def handle_sync_message(to_sink, cb, *args):
    # if program is shutting down, notify frontend with special reply
    sdmgr = manager.instance()
    with sdmgr.on_sync_message(to_sink) as accept:
        if not accept:
            return REP_SHUTDOWN
        
        # keep record what messages are being handled
        global g_sync_msg_lock, g_sync_msg_key, g_sync_msg_left
        g_sync_msg_lock.acquire()
        g_sync_msg_key += 1
        key = g_sync_msg_key
        g_sync_msg_left[key] = (time.time(), cb, args)
        g_sync_msg_lock.release()
        
        try:
            return cb(*args) 
        except:
            logger.exception("handle sync message failed: %s" % (traceback.format_exc()))
            return REP_ERROR
        finally:
            g_sync_msg_lock.acquire()
            del g_sync_msg_left[key]
            g_sync_msg_lock.release()

g_async_msg_lock = threading.RLock()
g_async_msg_key = 0
g_async_msg_left = {}
def handle_async_message(cb, *args):
    # if program is shutting down, notify frontend with special reply
    sdmgr = manager.instance()
    with sdmgr.on_async_message():
        
        # keep record what messages are being handled
        global g_async_msg_lock, g_async_msg_key, g_async_msg_left
        g_async_msg_lock.acquire()
        g_async_msg_key += 1
        key = g_async_msg_key
        g_async_msg_left[key] = (time.time(), cb, args)
        g_async_msg_lock.release()
        
        try:
            cb(*args) 
        except:
            logger.critical("handle async message failed: %s" % (traceback.format_exc()))
            return
        finally:
            g_async_msg_lock.acquire()
            del g_async_msg_left[key]
            g_async_msg_lock.release()
            
def print_left_msgs():
    global g_sync_msg_left, g_async_msg_left
    
    s = "The left sync messages:\n"
    keys = sorted(g_sync_msg_left.keys())
    for key in keys:
        v = g_sync_msg_left.get(key)
        if not v:
            continue
        (ts, cb, args) = v
        s += "    %s: %s(%s)\n" % (format_timestamp(ts), cb.__name__, args)
    logger.info(s)
    
    s = "The left async messages:\n"
    keys = sorted(g_async_msg_left.keys())
    for key in keys:
        v = g_async_msg_left.get(key)
        if not v:
            continue
        (ts, cb, args) = v
        s += "    %s: %s(%s)\n" % (format_timestamp(ts), cb.__name__, args)
    logger.info(s)
    
    return 
