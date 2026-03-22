#!/usr/bin/env python
'''
Created on 2012-5-2

@author: yunify
'''
from log.logger_name import set_logger_name
set_logger_name("server_proxy")

import os
import sys
import time
import threading
import signal
import traceback
from log.logger import logger
from base_server import BaseServer
from pull_server import PullServer
from optparse import OptionParser
from server.proxy import context
from server.proxy.service_handler import ServiceHandler
from server.proxy.pull_handler import PullServiceHandler
from utils.misc import exit_program, set_program_pid, dump_program_stacks, dump_program_objects
from utils.net import get_listening_url
from constants import SERVER_TYPE_SERVER_PROXY
from base_client import BaseClient
from utils.yaml_tool import yaml_load

class ServerProxy():
    ''' server proxy server'''
    
    def __init__(self, conf):
        ''' constructor '''
        
        self.conf = conf
        
        # threads dispatch_handler
        self.thrs = []
        
        # initialize dispatch_context
        ctx = context.instance()
        set_program_pid()
        ctx.pull_url = "inproc://pullserver_%d" % id(self)
        ctx.back_port = self.conf["back_port"]
        ctx.async_reqs = self.conf["async_reqs"]
        ctx.client = BaseClient(use_sock_pool=True)
        
    def _get_live_thr_cnt(self):
        ''' return the sum of threads that lives '''
        
        live_cnt = 0
        for thr in self.thrs:
            if thr.is_alive():
                live_cnt += 1
        
        return live_cnt
    
    def start(self):
        ctx = context.instance()

        # start peer task to handle requests from other bots
        handler = ServiceHandler()
        listen_ip = self.conf.get("listen_ip")
        peer_server = BaseServer(get_listening_url(SERVER_TYPE_SERVER_PROXY, self.conf["front_port"], listen_ip=listen_ip), 1, handler)
        peer_thr = threading.Thread(target=peer_server.start, args=())
        peer_thr.setDaemon(True)
        peer_thr.start()
        self.thrs.append(peer_thr)

        # start pull server to handle internal sink requests
        handler = PullServiceHandler()
        
        pull_server = PullServer(ctx.pull_url, 1, handler)
        pull_thr = threading.Thread(target=pull_server.start, args=())
        pull_thr.setDaemon(True)
        pull_thr.start()
        self.thrs.append(pull_thr)

        # wait while servers are actually started
        time.sleep(1)
        logger.info("server_proxy is running now.")
        
        # 1) if KeyboardInterrupt, quit
        # 2) if one of the threads dead, quit           
        try:
            while self._get_live_thr_cnt() == len(self.thrs):
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("interrupted, quit now")
        exit_program(-1)
        
def _get_opt_parser():
    ''' get option parser '''
    
    MSG_USAGE = "server_proxy [-c <conf_file>]" 
    opt_parser = OptionParser(MSG_USAGE)     
    
    opt_parser.add_option("-c", "--config", action="store", type="string", \
                         dest="conf_file", help='config file', default="") 

    return opt_parser

def on_signal_term(a, b):   
    logger.warn("signal term received, exiting...") 
    exit_program(-1)
    
def main():
    ''' start up a server and wait for request '''
    
    #import gc
    #gc.set_debug(gc.DEBUG_LEAK)
    
    signal.signal(signal.SIGTERM, on_signal_term)  
    signal.signal(signal.SIGINT, on_signal_term)  
    signal.signal(signal.SIGUSR1, dump_program_stacks)  
    signal.signal(signal.SIGUSR2, dump_program_objects)  

    # parser options
    parser = _get_opt_parser()    
    (options, _) = parser.parse_args(sys.argv)
    
    # get config
    conf = {}
    if options.conf_file != "":
        if not os.path.isfile(options.conf_file):
            logger.error("config file [%s] not exists" % options.conf_file)
            sys.exit(-1)
            
        with open(options.conf_file, "r") as fd:
            conf = yaml_load(fd)

    # run the service
    bot = ServerProxy(conf)
    try:
        bot.start()
    except:
        logger.critical("Exit with exception: %s" % traceback.format_exc())
        exit_program(-1)
        
if __name__ == '__main__':
    main()
    
