'''
Created on 2013-1-1

@author: yunify
'''

import time
import threading
import traceback
from contextlib import contextmanager
from log.logger import logger

class ShutdownManager(object):
    
    def __init__(self):
        # if program is shutting down
        self.shutting_down = False
        
        # synchronous message number in processing
        self.sync_msg_num = 0
        
        # asynchronous message number in processing
        self.async_msg_num = 0
        
        self.lock = threading.RLock()
    
    @contextmanager
    def on_async_message(self):
        ''' called when receiving a asynchronous message 
            Note: this message is normally handled by pull handler
        '''
        self._enter_async_message()
        try:
            yield
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())
        self._exit_async_message()
    
    @contextmanager
    def on_sync_message(self, to_sink=False):
        ''' called when receiving a synchronous message 
            @param to_sink - True if this message will be relayed to pull handler afterwards
            Note: this message is normally the input message, handled by service handler
        '''
        accept = self._enter_sync_message(to_sink)
        try:
            yield accept
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())
        if accept:
            self._exit_sync_message()

    def wait_for_shutdown(self):   
        logger.info("waiting for shutdown ...") 
        
        # gracefully shutdown
        self.set_shutting_down()
        count = 100
        while True:
            if self.can_shutdown():
                # wait until all reply has been sent out
                time.sleep(1)
                return
            time.sleep(1)
            count -= 1
            if count == 0:
                logger.critical("server can't shut down, please check")
                count = 100
            
    def is_shutting_down(self):
        return self.shutting_down

    def set_shutting_down(self):
        with self._lock():
            self.shutting_down = True
        return
    
    def can_shutdown(self):
        # since it may take time for message to be passed from service handler to pull handler
        # we have to wait to make sure there are really no processing messages
        endtime = time.time() + 2
        while endtime > time.time():
            with self._lock():
                if self.sync_msg_num != 0 or self.async_msg_num != 0:
                    logger.info("can't shut down now, waiting: sync[%d] async[%d]" % (self.sync_msg_num, self.async_msg_num))
                    from server.shutdown.helper import print_left_msgs
                    print_left_msgs()
                    return False
            time.sleep(0.1)
        
        logger.info("shutting down now ...")
        return True    
    
    def _enter_async_message(self):
        ''' called before handing an asynchronous message '''
        with self._lock():
            self.async_msg_num += 1
            logger.debug("enter async message: sync[%d] async[%d]" % (self.sync_msg_num, self.async_msg_num))
            return

    def _exit_async_message(self):
        ''' called after handing an asynchronous message '''
        with self._lock():
            self.async_msg_num -= 1
            logger.debug("exit async message: sync[%d] async[%d]" % (self.sync_msg_num, self.async_msg_num))
            return
    
    def _enter_sync_message(self, to_sink=False):
        ''' called before handling a portal message
            @param to_sink - true if this message is going to be relayed to pull server
            @return True to accept message or False to reject
         '''
        # if shutting down, then:
        #     1) block all new asynchronous messages
        #     2) if no asynchronous messages, block all new synchronous messages
        with self._lock():
            if not self.shutting_down:
                self.sync_msg_num += 1
                logger.debug("_enter_sync_message")
                logger.debug("accept sync message: sync[%d] async[%d]" % (self.sync_msg_num, self.async_msg_num))
                return True
            
            if not to_sink:
                if self.async_msg_num != 0:
                    self.sync_msg_num += 1
                    logger.debug("accept sync message: sync[%d] async[%d]" % (self.sync_msg_num, self.async_msg_num))
                    return True
                
            logger.debug("reject sync message: sync[%d] async[%d]" % (self.sync_msg_num, self.async_msg_num))
            return False
    
    def _exit_sync_message(self):
        with self._lock():
            self.sync_msg_num -= 1            
            logger.debug("exit sync message: sync[%d] async[%d]" % (self.sync_msg_num, self.async_msg_num))
            return
        
    @contextmanager
    def _lock(self):
        self.lock.acquire()
        try:
            yield
        except:
            logger.error("yield exits with exception: %s" % traceback.format_exc())
        self.lock.release()
        
g_shutdown_manager = None
def instance():
    ''' get shutdown manager instance '''
    global g_shutdown_manager
    if g_shutdown_manager == None:
        g_shutdown_manager = ShutdownManager()
    return g_shutdown_manager
