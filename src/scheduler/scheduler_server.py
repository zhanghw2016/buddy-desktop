#!/usr/bin/env python
'''
Created on 2015-1-1

@author: yunify
'''
from log.logger_name import set_logger_name
set_logger_name("desktop_scheduler")

import os
import signal
import sys
import time
import traceback
import threading
from optparse import OptionParser
from db.pg_model import PGModel
from base_client import BaseClient
from base_server import BaseServer
from pull_server import PullServer
from db.constants import DB_VDI
from log.logger import logger
from server.shutdown import manager as ShutdownManager
from server.shutdown.helper import on_gracefully_shutdown
from constants import SERVER_TYPE_VDI_SCHEDULER_SERVER
from utils.id_tool import UUIDPGChecker
from utils.net import get_listening_url
from utils.misc import (exit_program, set_program_pid, initialization_calls,
        dump_program_stacks, dump_program_objects)
from utils.yaml_tool import yaml_load
from utils.global_conf import get_pg
import context
from service_handler import ServiceHandler
from pull_handler import PullServiceHandler
from scheduler_manager import SchedulerTaskManager
from resource_adapter import ResourceAdapter
from api.auth.auth_user import AuthUser
from api.zone.zone_builder import ZoneBuilder
from api.zone.zone_checker import ZoneChecker

class SchedulerServer():
    ''' scheduler server '''

    def __init__(self, conf):
        ''' constructor '''

        initialization_calls()

        self.conf = conf

        # threads dispatch_handler
        self.thrs = []

        # initialize dispatch_context
        set_program_pid()

        self.server_type = SERVER_TYPE_VDI_SCHEDULER_SERVER

        ctx = context.instance()
        ctx.pull_url = "inproc://pullserver_%d" % id(self)

        # shared base client
        ctx.client = BaseClient(use_sock_pool=True)

    def _get_live_thr_cnt(self):
        ''' return the sum of threads that lives '''

        return len([thr for thr in self.thrs if thr.is_alive()])

    def start(self):

        ctx = context.instance()
        logger.info("starting scheduler server ...")

        # initial zone config
        logger.info("initial zone config ...")
        ctx.zone_builder = ZoneBuilder(ctx)
        ret = ctx.zone_builder.init_zone_config()
        if ret < 0:
            logger.error("load desktop config fail")
            exit_program(-1)

        # connect to zone db
        logger.info("connect to postgresql db...")
        ctx.pg = get_pg(DB_VDI, maxconn=200)
        if ctx.pg is None:
            logger.error("connect to desktop database failed: can't connect")
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

        # managers
        ctx.sdmgr = ShutdownManager.instance()
        ctx.scheduler_task_mgr = SchedulerTaskManager()

        # start peer task to handle external requests
        handler = ServiceHandler()
        peer_server = BaseServer(get_listening_url(self.server_type), 1, handler)
        peer_thr = threading.Thread(target=peer_server.start, args=())
        peer_thr.setDaemon(True)
        peer_thr.start()
        self.thrs.append(peer_thr)

        # start pull server to handle internal sink requests
        handler = PullServiceHandler()
        pull_server = PullServer(ctx.pull_url, 1, handler, max_worker_num=500)
        pull_thr = threading.Thread(target=pull_server.start, args=())
        pull_thr.setDaemon(True)
        pull_thr.start()
        self.thrs.append(pull_thr)

        # wait while servers are actually started
        time.sleep(2)
        logger.info("scheduler_server is running now.")

        # 1) if KeyboardInterrupt, quit
        # 2) if one of the threads dead, quit
        try:
            while self._get_live_thr_cnt() == len(self.thrs):
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("interrupted, quit now")
        exit_program(0)

def _get_opt_parser():
    ''' get option parser '''

    MSG_USAGE = "server [-c <conf_file>]"
    opt_parser = OptionParser(MSG_USAGE)

    opt_parser.add_option("-c", "--config", action="store", type="string",
                         dest="conf_file", help='config file', default="")
    return opt_parser

def on_signal_term(a, b):

    logger.warn("signal term received, exiting...")
    ctx = context.instance()
    if ctx.scheduler_task_mgr:
        ctx.scheduler_task_mgr.prepare_shutdown()

    on_gracefully_shutdown(a, b)

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

    signal.signal(signal.SIGTERM, on_signal_term)
    signal.signal(signal.SIGINT, on_signal_term)
    signal.signal(signal.SIGUSR1, dump_program_stacks)
    signal.signal(signal.SIGUSR2, dump_program_objects)

    # run the service
    server = SchedulerServer(conf)
    try:
        server.start()
    except Exception:
        logger.critical("Exit with exception: %s" % traceback.format_exc())
        exit_program(-1)

if __name__ == '__main__':
    main()
