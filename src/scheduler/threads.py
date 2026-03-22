'''
Created on 2014-4-20

@author: yunify
'''
from contextlib import contextmanager
from datetime import datetime
import heapq
import time
import threading
import traceback

from base_client import send_to_pull
from log.logger import logger
from utils.misc import get_current_time, exit_program

import context
from constants import REQ_TYPE_SCHED_EVENT

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

class SchedThread(threading.Thread):

    def __init__(self, shutdown_manager):

        super(SchedThread, self).__init__()
        self.lock = threading.RLock()
        self.heap = []  # heap structure
        self.count = 0
        self.stopped = False
        self.sdmgr = shutdown_manager

    def _run(self):
        while not self.stopped and not self.sdmgr.is_shutting_down():
            
            # loop until no scheduled event
            now = get_current_time()
            batch_count = 20
            #logger.error("%s, %s, %s" % (self.count, batch_count, self.heap))
            while self.count > 0 and batch_count > 0:
            
                sched_item = None
                with self._lock():
                    # double check
                    if self.count == 0:
                        break

                    sched_item = self.heap[0]
                    if sched_item.sched_time > now:
                        break

                    if 0 != self.handle_sched_task(sched_item):
                        break

                    # remove item
                    heapq.heappop(self.heap)

                    self.count -= 1

                batch_count -= 1

            time.sleep(1)

    def run(self):
        try:
            self._run()
        except Exception:
            logger.critical("Exit with exception: %s" % traceback.format_exc())
            exit_program(-1)
    
    def push(self, sched_item):
        with self._lock():
            
            heapq.heappush(self.heap, sched_item)
            self.count += 1
        return 0

    def push_all(self, sched_list):
        with self._lock():
            del self.heap

            self.heap = sched_list
            heapq.heapify(self.heap)
            self.count = len(sched_list)

        return 0

    def close(self):
        self.stopped = True

    @contextmanager
    def _lock(self):
        self.lock.acquire()
        try:
            yield
        except Exception:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())
        self.lock.release()

    def handle_sched_task(self, sched_item):
        
        ctx = context.instance()
        # to improve efficiency,
        # send to pull handler and handle this request concurrently
        return send_to_pull(ctx.pull_url, {

            'req_type': REQ_TYPE_SCHED_EVENT,
            'sched_item': sched_item.dump()
            })


class SchedItem(object):

    def __init__(self, sched_time, scheduler_task_id, update_time):

        self.sched_time = sched_time
        self.scheduler_task_id = scheduler_task_id
        self.update_time = update_time

    def __str__(self):
        return '<SchedItem sched_time:%s, scheduler_task_id:%s, update_time:%s>' % (
                self.sched_time, self.scheduler_task_id, self.update_time)

    def __eq__(self, other):
        return self.scheduler_id == other.scheduler_id and \
               self.update_time == other.update_time

    def __ne__(self, other):
        return self.scheduler_id != other.scheduler_id or \
               self.update_time != other.update_time

    def __gt__(self, other):
        return self.sched_time > other.sched_time

    def __ge__(self, other):
        return self.sched_time >= other.sched_time

    def __le__(self, other):
        return self.sched_time <= other.sched_time

    def __lt__(self, other):
        return self.sched_time < other.sched_time

    def dump(self):
    
        datas = [self.sched_time.strftime(TIME_FORMAT),
                self.scheduler_task_id,
                self.update_time.strftime(TIME_FORMAT)]

        return "\t".join(datas)

    @staticmethod
    def load(s):
    
        sched_time, scheduler_task_id, update_time = s.split("\t")
        sched_time = datetime.strptime(sched_time, TIME_FORMAT)
        update_time = datetime.strptime(update_time, TIME_FORMAT)
    
        return SchedItem(sched_time, scheduler_task_id, update_time)
