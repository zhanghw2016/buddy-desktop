#!/usr/bin/env python
'''
Created on 2012-9-23

@author: yunify
'''
from log.logger_name import set_logger_name
set_logger_name("desktop_push")

import os
import sys
import time
import signal
import traceback
import threading
from optparse import OptionParser
from log.logger import logger
from utils.yaml_tool import yaml_load
from pull_server import PullServer
from constants import (SERVER_TYPE_PUSH_SERVER, 
                       PUSH_SERVER_PORT, 
                       )
from utils.net import get_listening_url, get_local_mgmt_ip
from utils.misc import exit_program, dump_program_stacks, dump_program_objects, \
                       initialize_program
import context
from service_handler import ServiceHandler
from topic_manager import TopicManager, SubscriberManager
from server.shutdown.helper import on_gracefully_shutdown
from websocket_server import WebSocketServer

class PushServer():
    ''' push server '''
    
    def __init__(self, conf):
        ''' constructor '''
        # initialization calls
        initialize_program()

        # threads handlers
        self.thrs = []

        # initialize context
        ctx = context.instance()
        ctx.conf = conf
        ctx.topic_mgr = TopicManager()
        ctx.subscriber_mgr = SubscriberManager()

    def _get_live_thr_cnt(self):
        ''' return the sum of threads that lives '''
        
        live_cnt = 0
        for thr in self.thrs:
            if thr.is_alive():
                live_cnt += 1

        return live_cnt

    def start(self):
        # start websocket server
        websocket_server = WebSocketServer()
        websocket_server.setDaemon(True)
        websocket_server.start()
        self.thrs.append(websocket_server)

        # start peer task to handle external requests
        handler = ServiceHandler()
        peer_server = PullServer(get_listening_url(SERVER_TYPE_PUSH_SERVER, listen_ip="0.0.0.0"), 1, handler)
        peer_thr = threading.Thread(target=peer_server.start, args=())
        peer_thr.setDaemon(True)
        peer_thr.start()
        self.thrs.append(peer_thr)
        
        # wait while servers are actually started
        time.sleep(1)
        logger.info("push_server is running now.")
        
        # 1) if KeyboardInterrupt, quit
        # 2) if one of the threads dead, quit           
        try:
            while self._get_live_thr_cnt() == len(self.thrs):
                time.sleep(1)
        except KeyboardInterrupt:
            print "interrupted, quit now"   
        exit_program(0)

def _get_opt_parser():
    ''' get option parser '''
    
    MSG_USAGE = "server [-c <conf_file>]" 
    opt_parser = OptionParser(MSG_USAGE)     
    
    opt_parser.add_option("-c", "--config", action="store", type="string", \
                         dest="conf_file", help='config file', default="") 

    return opt_parser

def main():
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
     
    signal.signal(signal.SIGTERM, on_gracefully_shutdown)  
    signal.signal(signal.SIGINT, on_gracefully_shutdown)  
    signal.signal(signal.SIGUSR1, dump_program_stacks)  
    signal.signal(signal.SIGUSR2, dump_program_objects)  
    
    # run the service
    server = PushServer(conf)
    try:
        server.start()
    except Exception:
        logger.error("Exit with exception: %s" % traceback.format_exc())
        exit_program(-1)
        
if __name__ == '__main__':
    main()

