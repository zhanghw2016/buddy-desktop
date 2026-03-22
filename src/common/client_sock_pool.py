'''
Created on 2012-4-26

@author: yunify
'''

import zmq
import threading
from collections import deque
from log.logger import logger

class SockPoolKey(object):
    ''' request letter structure '''
    
    def __init__(self, url, stype):
        '''
        @param url - communication url
        @param stype - zmq socket type
        '''
        self.url = url
        self.stype = stype
        
    def __eq__(self, other):
        return other and self.url == other.url and self.stype == other.stype       
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.url, self.stype))

# Maximum client socks, during testing, approximately 100 zmq sockets will generate 1000 socket dispatch_handler
MAX_CLIENT_SOCK_NUM = 300

g_client_sock_num = 0
class ClientSockPool():
    ''' a simple ZMQ socket pool for multiplexing client sockets
    
    It is usually used in client endpoint, especially when this client needs to 
    connect to multiple peers concurrently
    It allocs sockets if not exists, and REQUIRES socket receiver to return or close socket 
    '''
    
    def __init__(self, ctx=None, cached=True):
        self.ctx = ctx or zmq.Context.instance()
        
        if hasattr(self.ctx, "MAX_SOCKETS"):
            self.ctx.MAX_SOCKETS = 65535
            
        self.lock = threading.RLock()
        self.sock_map = dict()
        
        # disable cache mode, cause this will hold zmq socks and raise "Too many open files" error
        # in case big concurrent requests are sent
        self.cached = True
        
    def alloc_sock(self, key):
        ''' allocate a socket, if there is free socket, reuse it 
        
        @param key must be a SockPoolKey instance
        '''

        if self.cached:
            self.lock.acquire()
            
            # create list
            if key not in self.sock_map:
                free_list = deque()
                self.sock_map[key] = free_list
            else:
                free_list = self.sock_map[key]
                
            # alloc from free list
            if len(free_list) != 0:
                sock = free_list.pop()
                self.lock.release()
                return sock
            
            self.lock.release()

        global g_client_sock_num
        logger.debug("g_client_sock_num == %s" %(g_client_sock_num))
        if g_client_sock_num >= MAX_CLIENT_SOCK_NUM:
            logger.critical("zmq connect to [%s] failed: sock full" % (key.url))
            return None

        # create new sock
        sock = self.ctx.socket(key.stype)
        try:
            sock.connect(key.url)
        except Exception, e:
            logger.error("zmq connect to [%s] failed: %s" % (key.url, e))
            self.close_sock(key, sock)
            return None
        
        g_client_sock_num += 1
        return sock
    
    def return_sock(self, key, sock):
        ''' return a socket into free list '''
        
        if self.cached:
            if key not in self.sock_map:
                return
            
            self.lock.acquire()
            
            free_list = self.sock_map[key]
            free_list.append(sock)
            
            self.lock.release()

            global g_client_sock_num
            if g_client_sock_num > 0:
                g_client_sock_num -= 1
        else:
            self.close_sock(key, sock)
        return
    
    def close_sock(self, key, sock):
        ''' close a specified sock '''
        
        if self.cached:
            if key not in self.sock_map:
                return
            
            self.lock.acquire()
            
            free_list = self.sock_map[key]
            try:
                free_list.remove(sock) 
            except ValueError:
                pass  
             
            self.lock.release()
            
        # close with linger = 0 to prevent program hang when exit
        sock.close(0)  
                
        global g_client_sock_num
        g_client_sock_num -= 1
        return
    
    def close_all_socks(self, key):
        ''' close sockets of the same key '''

        if self.cached:
            if key not in self.sock_map:
                return
            
            self.lock.acquire()
    
            free_list = self.sock_map[key]
            for sock in free_list:
                sock.close(0)
            del(self.sock_map[key])  
              
            self.lock.release()
        return
    
    def clear(self):
        ''' terminate object and close all open sockets '''
        if self.cached:
            self.lock.acquire()
            
            for key in self.sock_map:
                free_list = self.sock_map[key]
                for sock in free_list:
                    sock.close(0)
            self.sock_map = dict()
            
            self.lock.release()
        return
    
g_client_sock_pool = None
def instance():
    ''' get sock pool global instance 
    
    By default, it is safe and recommended to use a single/global instance of sock pool
    '''
    global g_client_sock_pool
    if g_client_sock_pool == None:
        g_client_sock_pool = ClientSockPool(cached=True)
    return g_client_sock_pool

__all__ = [ClientSockPool, SockPoolKey, instance]
