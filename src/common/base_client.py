'''
Created on 2012-4-21

@author: yunify
'''

import zmq
import client_sock_pool as spool
from utils.misc import M_ECP, M_DCP
from log.logger import logger
from common import encode_kargs, get_server
from utils.net import get_hostname, get_mgmt_net_ip, is_valid_ip, is_port_open
from utils.json import json_dump, json_load

class ReqLetter(object):
    ''' request letter structure '''
    
    def __init__(self, url="", content="", title=""):
        '''
        @param url - communication url
        @param msg - request message
        '''
        self.url = url
        self.content = content   
        self.title = title    
        
    def __str__(self):
        return "%s__|__%s__|__%s" % (self.url, self.content, self.title)
    
    @staticmethod
    def load(s):
        items = s.split("__|__")
        if len(items) != 3:
            return None
        
        return ReqLetter(items[0], items[1], items[2])
    
    def get_host_port(self):
        if not self.url.startswith("tcp://"):
            return (None, None)
        parts = self.url[6:].split(":")
        return (parts[0], parts[1])

class BaseClient(object):
    ''' Basic sock to send request message based on ZMQ '''
    
    def __init__(self, use_sock_pool=False):
        ''' Constructor 
        
        @param sock_pool - the specified zmq socket pool to multiplex sockets
        '''
        # since bot's ZMQ connection is a mesh network, don't use sock cache, use short connection instead
        self.sock_pool = spool.instance() if use_sock_pool else spool.ClientSockPool(cached=False)
    
    def send(self, letter, retry=0, timeout=30, to_crypt=True, check_port=False):
        ''' send request message and get reply
        
        @param letter - the ReqLetter object including peer url and data
        @param retry - the retry number, 0 means no retry
        @param timeout - how long in seconds before one try of request times out, 0 means wait forever
        @return reply message or None if failed
        '''
        
        poll = zmq.Poller()
        pool_key = spool.SockPoolKey(letter.url, zmq.REQ)
        
        # throttle control for local server
        server = get_server(letter.url)
        if server and server.is_full():
            logger.error("send ZMQ message to [%s] failed due to server full: [%s]" % (letter.url, letter.content))
            return None
        
        if check_port:
            (_host, _port) = letter.get_host_port()
            if _host and _port and not is_port_open(_host, _port):
                logger.error("send ZMQ message to [%s] failed due to server closed: [%s]" % (letter.url, letter.content))
                return None
                            
        sock = None
        retries_left = 1 if retry <= 0 else retry + 1
        while retries_left:
            # Fetch a sock from pool
            sock = self.sock_pool.alloc_sock(pool_key)
            if sock != None:
                poll.register(sock, zmq.POLLIN)
                
                # send request message
                sock.send_multipart([M_ECP(letter.content, to_crypt), letter.title, encode_kargs(timeout)])
                
                # poll to get reply with timeout
                socks = dict(poll.poll(None if timeout <= 0 else (timeout * 1000)))
                if socks.get(sock) == zmq.POLLIN:
                    reply = sock.recv()
                    self.sock_pool.return_sock(pool_key, sock)  # return sock to pool
                    (_, rep) = M_DCP(reply)
                    return rep
            
                # no reply this time, destroy sock and retry
                poll.unregister(sock)
                self.sock_pool.close_sock(pool_key, sock)
                sock = None
                
            retries_left -= 1
            if retries_left == 0:
                break
                   
        if sock:
            self.sock_pool.return_sock(pool_key, sock)  # return sock to pool
             
        logger.error("send ZMQ message to [%s] failed: [%s]" % (letter.url, letter.content))
        return None
    
def send_to_local(port, msg, title="", retry=0, timeout=30, ignore_reply=False):
    ''' send request to local service '''
    return send_to_server(get_hostname(), port, msg, title, retry, timeout,
                          to_crypt=False, use_sock_pool=True, ignore_reply=ignore_reply)

def send_to_pull(pull_url, msg, title="", retry=0, timeout=30):
    ''' send request to pull service '''
    try:
        client = BaseClient(use_sock_pool=True)
        letter = ReqLetter(pull_url, json_dump(msg), title)
        if None == client.send(letter, retry=retry, timeout=timeout, to_crypt=False):
            return -1
    except Exception, e:
        logger.error("send req [%s] to pull failed: [%s]" % (msg, e))
        return -1
    return 0
 
def send_to_server(host, port, msg, title="", retry=0, timeout=30, to_crypt=True, use_sock_pool=False, ignore_reply=False):
    ''' send request to remote service '''
    try:
        client = BaseClient(use_sock_pool=use_sock_pool)
        ip = host if is_valid_ip(host) else get_mgmt_net_ip(host)
        letter = ReqLetter("tcp://%s:%s" % (ip, port), json_dump(msg), title)
        rep = client.send(letter, retry=retry, timeout=timeout, to_crypt=to_crypt)
        if ignore_reply:
            return None
        return None if rep == None else json_load(rep)
    except Exception, e:
        logger.error("send msg [%s] to server [%s:%s] failed: [%s]" % (msg, host, port, e))
        return None

def send_pull_task(ctx, req):
    ''' send pull task '''
    return send_to_pull(ctx.pull_url, req, timeout=1) == 0