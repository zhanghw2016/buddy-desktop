#!/usr/bin/env python
'''
Created on 2012-5-28

@author: yunify
'''
from log.logger_name import set_logger_name
set_logger_name("desktop_agent")

import os
import sys
import threading
import time
import traceback
import random
import signal
from optparse import OptionParser
from log.logger import logger
import context
from utils.yaml_tool import yaml_load
from db.pg_model import PGModel
from pull_server import PullServer
from agent_handler import PullServiceHandler
from constants import (
    CHK_TYPES,
    REQ_TYPE_CHECK,
)
from utils.misc import (
    exit_program,
    dump_program_stacks,
    dump_program_objects,
    initialize_program
)
from utils.thread_local import clear_taskware
from contextlib import contextmanager
from base_client import send_to_pull
from mc.mc_model import MCModel
from utils.global_conf import get_pg, get_mc
from db.constants import DB_VDI
from api.auth.auth_user import AuthUser
from api.zone.zone_builder import ZoneBuilder
from api.zone.zone_checker import ZoneChecker
from resource_adapter import ResourceAdapter

def extend_context():
    ''' extend basic dispatch_context with specific attributes '''
    ctx = context.instance()

    # checking interval
    ctx.chk_interval = {}

    # checking status, prevent duplicate checking
    ctx.is_checking = {}

    # checking lock, prevent duplicate checking
    ctx.chk_lock = {}

    # initialize
    for chk_type in CHK_TYPES:
        ctx.is_checking[chk_type] = False
        ctx.chk_lock[chk_type] = threading.Lock()

    @contextmanager
    def check(self, chk_type):
        ''' if this type is already in checking, do nothing and return is_checking status
            caller shall check "is_checking" status and return immediately if it is "true"
        '''
        lock = self.chk_lock[chk_type]

        lock.acquire()
        is_checking = self.is_checking[chk_type]
        if not is_checking:
            self.is_checking[chk_type] = True
        lock.release()

        yield is_checking

        lock.acquire()
        if not is_checking:
            self.is_checking[chk_type] = False
        lock.release()

    context.DesktopAgentContext.check = check

class ChkTriggerThread(threading.Thread):
    ''' worker to trigger check events '''

    def run(self):
        ctx = context.instance()

        # get initial ticks
        ticks = {}
        for chk_type in CHK_TYPES:
            if chk_type not in ctx.chk_interval.keys():
                logger.error("checking interval for [%s] is not set" % chk_type)
                return -1
            
            ticks[chk_type] = random.randint(1, 60)

        try:
            while True:
                # tick count
                for chk_type in ticks:

                    ticks[chk_type] = ticks[chk_type] - 1
                    if ticks[chk_type] <= 0:
                        ticks[chk_type] = ctx.chk_interval[chk_type]
                        # trigger only for valid interval
                        if ticks[chk_type] > 0:
                            # trigger event
                            send_to_pull(ctx.pull_url, {'req_type': REQ_TYPE_CHECK, 'params': {'type': chk_type}})
                clear_taskware()
                time.sleep(1)
        except:
            logger.critical("Exit with exception: %s" % traceback.format_exc())
            exit_program(-1)

class DesktopAgent(object):

    def __init__(self, conf):
        ''' constructor

        @param chk_interval - checking interval configuration
        '''
        # initialization calls
        initialize_program()
        
        ctx = context.instance()
        self.conf = conf

        # threads dispatch_handler
        self.thrs = []

        # extend dispatch_context
        extend_context()
        ctx.chk_interval = self.conf['chk_interval']
        
        # initialize dispatch_context
        ctx.pull_url = "inproc://pullserver_%d" % id(self)

    def _get_live_thr_cnt(self):
        ''' return the sum of threads that lives '''

        live_cnt = 0
        for thr in self.thrs:
            if thr.is_alive():
                live_cnt += 1

        return live_cnt

    def start(self):

        ctx = context.instance()
        logger.info("starting desktop agent ...")

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

        # connect to memcached
        ctx.mcclient = get_mc()
        if ctx.mcclient == None:
            logger.error("connect to memcached failed: can't connect")
            exit_program(-1)   
        ctx.mcm = MCModel(ctx.mcclient) 

        # start pull server to handle internal sink requests
        handler = PullServiceHandler()
        pull_server = PullServer(ctx.pull_url, 1, handler)
        pull_thr = threading.Thread(target=pull_server.start, args=())
        pull_thr.setDaemon(True)
        pull_thr.start()
        self.thrs.append(pull_thr)

        # start to trigger check events at specified time interval
        tri_thr = ChkTriggerThread()
        tri_thr.setDaemon(True)
        tri_thr.start()
        self.thrs.append(tri_thr)

        # wait while servers are actually started
        time.sleep(1)
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

    MSG_USAGE = "mgmt_bot [-c <conf_file>]"
    opt_parser = OptionParser(MSG_USAGE)

    opt_parser.add_option("-c", "--config", action="store", type="string", \
                         dest="conf_file", help='config file', default="")

    return opt_parser

def on_signal_term(a, b):
    logger.warn("signal term received, exiting...")
    exit_program(-1)

def main():
    ''' start up a vdi agent '''

    # parser options
    parser = _get_opt_parser()
    (options, _) = parser.parse_args(sys.argv)

    # get config if exists, but config has lower privilege than option parameters
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
    desktop_agent = DesktopAgent(conf)
    try:
        desktop_agent.start()
    except:
        logger.critical("Exit with exception: %s" % traceback.format_exc())
        exit_program(-1)

if __name__ == '__main__':
    main()
