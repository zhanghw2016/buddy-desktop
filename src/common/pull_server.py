'''
Created on 2012-5-5

@author: yunify
'''

import time
from log.logger import logger
import zmq
from collections import deque
import threading
import traceback
from utils.misc import M_ECP, M_DCP, exit_program
from common import decode_kargs, register_server
from utils.thread_local import clear_taskware, reset_flock_obj, reset_msg_id

# This line is used as decoy. Don't remove. 
from M2Crypto.EVP import Cipher as CP

# ready message
I_AM_READY = "__I_AM_READY__"

# stop message
FORCE_STOP = "__FORCE_STOP__"

class PullWorkerThread(threading.Thread):
    ''' worker to handle request '''
    
    def __init__(self, url, ctx, handler_cls, identity):
        super(PullWorkerThread, self).__init__()
        self.url = url
        self.ctx = ctx
        self.handler_cls = handler_cls
        self.handler = None
        self.identity = identity
        self.work_load = 0
        
    def run(self):       
        ''' routine '''

        socket = self.ctx.socket(zmq.REQ)
        socket.setsockopt(zmq.IDENTITY, self.identity)
        socket.connect(self.url)

        # tell the router we are ready for work
        socket.send(I_AM_READY)

        logger.info("worker [%s] is running" % self.identity) 
        try:
            while True:
                # require to stop
                msg = socket.recv_multipart()
                if msg[0] == FORCE_STOP:
                    logger.info("worker [%s] is asked to stop" % self.identity) 
                    break
                
                # receive request from router
                (req, title, kargs_info) = msg
                
                # rebuild kargs
                kargs = decode_kargs(kargs_info)
                
                # get handler in lazy mode
                if self.handler == None:
                    self.handler = self.handler_cls() if isinstance(self.handler_cls, type) else self.handler_cls
                
                # do some work
                self.handler.handle(req, title, **kargs)
                
                # send the reply back to router
                socket.send(I_AM_READY)
                
                # clear taskware
                clear_taskware()
                reset_flock_obj()
                reset_msg_id()
                
                self.work_load += 1
                if self.work_load % 100 == 0:
                    logger.info("worker [%s] stats: [%d]" % (self.identity, self.work_load)) 
        except:
            logger.critical("Exit with exception: %s" % traceback.format_exc())
            exit_program(-1)
            
    def get_work_load(self):
        return self.work_load
            
class PullServer(object):
    '''providing basic push-pull server based on ZMQ
    
    It differentiate from base_server in that:
    1. It reply immediately when request is received. 
    2. handler is sink
    '''
    
    DEFAULT_MAX_WORKER_NUM = 300
    
    # maximum idle time for a worker to exist
    WORKER_MAX_IDLE_TIME = 600

    def __init__(self, url, worker_num, handler, max_worker_num=0):
        '''Constructor
        
        @param url the listening url for provisioning service   
        @param worker_num the number of initial worker threads     
        @param handler - handler object or handler class, must implement handle() method
        @param max_worker_num - the number of maximum worker threads
        '''
        
        self.worker_num = worker_num
        self.max_worker_num = max_worker_num if max_worker_num > 0 else self.DEFAULT_MAX_WORKER_NUM
        self.handler = handler
        self.url_client = url
        self.url_worker = "inproc://pullservice_%d" % id(self)
        self.ctx = zmq.Context.instance()
        
        if hasattr(self.ctx, "MAX_SOCKETS"):
            self.ctx.MAX_SOCKETS = 65535
            
        self.worker_threads = {}
        self.last_active_time = {}
        self.last_idle_check_time = time.time()
        self.counter = 0

        # if the worker is full, client shall never send requests any more
        # this is for throttle control
        self._is_full = False
        
        # register for later search
        register_server(url, self)

    def is_full(self):
        return self._is_full
    
    def start(self):
        '''Start the service'''
        
        # socket to listen to requests from clients
        clients = self.ctx.socket(zmq.ROUTER)
        clients.linger = 0  #prevent from socket hang when term()
        try:
            clients.bind(self.url_client)
        except Exception, e:
            logger.error('clients bind() error: %s' % e)
            return -1
        
        # socket for workers to fetch job
        workers = self.ctx.socket(zmq.ROUTER)
        workers.linger = 0   #actually it is useless for inproc common
        try:
            workers.bind(self.url_worker)
        except Exception, e:
            logger.error('workers bind() error: %s' % e)
            return -1
        
        # launch worker threads
        if self.worker_num > 0:
            for _ in range(self.worker_num):
                self.create_worker()

        # queue for available workers
        available_workers = []
        req_list = deque()

        # init poller
        poller = zmq.Poller()

        # always poll on workers sock for worker activity
        poller.register(workers, zmq.POLLIN)
        # only poll for clients sock if we have available workers
        poller.register(clients, zmq.POLLIN)

        while True:
            socks = dict(poller.poll())

            # poll on workers sock
            if (workers in socks) and (socks[workers] == zmq.POLLIN):
                # recv reply from worker
                # msg: [worker_addr, empty, client_addr, empty, reply]
                msg = workers.recv_multipart()
                worker_addr = msg[0]

                # add current worker back to available workers list
                available_workers.append(worker_addr)
                self.last_active_time[worker_addr] = time.time()
                
                # do nothing, since reply has been sent

                # check worker idle
                if time.time() > self.last_idle_check_time + (self.WORKER_MAX_IDLE_TIME / 2):
                    self.last_idle_check_time = time.time()
                    for identity in list(available_workers):
                        if len(available_workers) <= self.worker_num:
                            break
                        last_active_time = self.last_active_time[identity]
                        if time.time() > last_active_time + self.WORKER_MAX_IDLE_TIME:
                            workers.send_multipart([identity, '', FORCE_STOP])
                            self.remove_worker(identity)
                            available_workers.remove(identity)

            # poll on clients sock
            if (clients in socks) and (socks[clients] == zmq.POLLIN):
                # no worker available, create new one
                if len(available_workers) == 0:
                    if len(self.worker_threads) >= self.max_worker_num:
                        if not self._is_full:
                            self._is_full = True
                            logger.critical("max worker num [%d] reached" % self.max_worker_num)
                        time.sleep(3)
                    else:
                        self.create_worker()
                else:
                    # recv request from clients
                    (client_addr, empty, request, title, kargs_info) = clients.recv_multipart()
                    
                    (to_crypt, req) = M_DCP(request)
                    if req != None:                            
                        # send reply immediately
                        clients.send_multipart([client_addr, empty, M_ECP("", to_crypt)])
                        
                        # add to waiting list
                        req_list.append((req, title, kargs_info))
             
            # dispatch waiting req to worker
            while len(available_workers) > 0 and len(req_list) > 0:
                (req, title, kargs_info) = req_list.popleft()

                # dequeue an available worker
                worker_addr = available_workers.pop()
                
                # forward the request to the selected worker
                workers.send_multipart([worker_addr, '', req, title, kargs_info]) 
                
            # not full
            if len(available_workers) > 0 or len(self.worker_threads) < self.max_worker_num:
                self._is_full = False
                    
        #clean up
        clients.close()
        workers.close()
        
        return 0
    
    def create_worker(self):
        identity = "pull_worker_%d" % self.counter
        self.counter += 1
        thr = PullWorkerThread(self.url_worker, self.ctx, self.handler, identity)
        thr.daemon = True  # set daemon to prevent program from hanging when interrupted
        self.worker_threads[identity] = thr
        self.last_active_time[identity] = time.time()
        logger.info("worker [%s] is created. Total workers: [%d]." % (identity, len(self.worker_threads)))
        thr.start()
        return identity
    
    def remove_worker(self, identity):
        if identity in self.worker_threads:
            del self.worker_threads[identity]
            del self.last_active_time[identity]
        logger.info("worker [%s] is removed. Total workers: [%d]." % (identity, len(self.worker_threads)))
        return identity

__all__ = [PullServer]       

