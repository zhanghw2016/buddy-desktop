#!/usr/bin/env python

import os
import signal
import sys
import time
import threading
import traceback

from log.logger_name import set_logger_name
set_logger_name("dispatch_server")

import context
from base_client import BaseClient
from db.pg_model import PGModel
from db.constants import DB_VDI
from constants import SERVER_TYPE_DISPATCH_SERVER
from log.logger import logger
from base_server import BaseServer
from pull_server import PullServer
from optparse import OptionParser
from utils.net import get_listening_url
from utils.yaml_tool import yaml_load
from service_handler import ServiceHandler
from pull_handler import PullServiceHandler
from utils.misc import exit_program, dump_program_stacks, dump_program_objects, initialize_program
from server.shutdown.helper import on_gracefully_shutdown
from utils.id_tool import UUIDPGChecker
from utils.global_conf import get_pg
from resource_adapter import ResourceAdapter
from api.zone.zone_builder import ZoneBuilder
from api.auth.auth_user import AuthUser
from api.zone.zone_checker import ZoneChecker

class DispatchService():
    ''' dispatch server '''

    def __init__(self, conf):
        ''' constructor '''

        # initialization calls
        initialize_program()

        self.conf = conf

        # threads dispatch_handler
        self.thrs = []

        # initialize dispatch_context
        ctx = context.instance()
        ctx.pull_url = "inproc://pullserver_%d" % id(self)

        # shared base client
        ctx.client = BaseClient(use_sock_pool = True)

    def _get_live_thr_cnt(self):
        ''' return the sum of threads that lives '''

        live_cnt = 0
        for thr in self.thrs:
            if thr.is_alive():
                live_cnt += 1
        
        return live_cnt

    def start(self):

        ctx = context.instance()
        logger.info("starting dispatch server ...")

        # initial zone config
        logger.info("initial zone config ...")
        ctx.zone_builder = ZoneBuilder(ctx)
        ret = ctx.zone_builder.init_zone_config()
        if ret < 0:
            logger.error("load desktop config fail")
            exit_program(-1)

        # since vdi is the centrol point, its connect pool shall be large enough
        logger.info("connect to postgresql db...")
        ctx.pg = get_pg(DB_VDI, maxconn=200)
        if ctx.pg is None:
            logger.error("connect to PostgreSQL failed: can't connect")
            exit_program(-1)
        ctx.pgm = PGModel(ctx.pg)

        # uuid check
        ctx.checker = UUIDPGChecker(ctx.pg)
    
        # initial zone
        logger.info("initial zone ...")
        ctx.zone_builder.load_zone()
        ctx.zone_builder.refresh_zone_builder()
        ctx.zone_checker = ZoneChecker(ctx)

        # init resource_adapter
        ctx.res = ResourceAdapter(ctx)
        ret = ctx.res.init_resource_adapter()
        if ret < 0:
            logger.error("init resource adapater fail")
            exit_program(-1)

        # auth
        ctx.auth = AuthUser(ctx)
        if not ctx.auth:
            logger.error("init auth service fail")
            exit_program(-1)

        # start peer task to handle requests from clients
        logger.info("starting service handler ...")
        handler = ServiceHandler()
        peer_server = BaseServer(get_listening_url(SERVER_TYPE_DISPATCH_SERVER), 1, handler)
        peer_thr = threading.Thread(target=peer_server.start, args=())
        peer_thr.setDaemon(True)
        peer_thr.start()
        self.thrs.append(peer_thr)
        ctx.peer_server = peer_server
        
        # start pull server to handle internal sink requests
        logger.info("starting pull service handler ...")
        handler = PullServiceHandler()
        pull_server = PullServer(ctx.pull_url, 1, handler)
        pull_thr = threading.Thread(target=pull_server.start, args=())
        pull_thr.setDaemon(True)
        pull_thr.start()
        self.thrs.append(pull_thr)

        # wait while servers are actually started
        time.sleep(1)
        logger.info("dispatch server is running now.")
        
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

    MSG_USAGE = "dispatch_server [-c <conf_file>]"
    opt_parser = OptionParser(MSG_USAGE)

    opt_parser.add_option("-c", "--config", action="store", type="string",
                          dest="conf_file", help='config file', default="")

    return opt_parser

def main():
    ''' start up a server and wait for request '''
    reload(sys)
    sys.setdefaultencoding('utf-8')

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

    # receive signal and handler it properly
    signal.signal(signal.SIGTERM, on_gracefully_shutdown)
    signal.signal(signal.SIGINT, on_gracefully_shutdown)
    signal.signal(signal.SIGUSR1, dump_program_stacks)
    signal.signal(signal.SIGUSR2, dump_program_objects)

    # run the service
    ds = DispatchService(conf)
    try:
        ds.start()
    except Exception:
        logger.error("Exit with exception: %s" % traceback.format_exc())
        exit_program(-1)

if __name__ == '__main__':
    main()
