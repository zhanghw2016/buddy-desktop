'''
Created on 2015-1-1

@author: yunify
'''
import signal
import threading
import traceback
import time
import os
from contextlib import contextmanager
from datetime import datetime, timedelta
try:
    import cPickle as pickle
except:
    import pickle

from scheduler_task import handle_scheduler_task
import constants as const
from constants import (
        SCHEDULER_TASK_STATUS_ACTIVE, SCHEDULER_TASK_STATUS_EXECUTING,
        )
from db.constants import TB_SCHEDULER_TASK
from log.logger import logger
from utils.misc import exit_program, get_current_time

import context
from constants import (
        EXECUTE_TIMEOUT, 
)
from common import transition_status
from history_manager import HistoryManager
from threads import SchedItem, SchedThread
DUMP_FILE = "/tmp/.schedulers.dump"

def is_last_day_of_month(_datetime):
    return bool(_datetime.month != (_datetime + timedelta(1)).month)

def get_next_exectime(scheduler_task):

    scheduler_task_id = scheduler_task["scheduler_task_id"]
    repeat = scheduler_task['repeat']
    h, m = map(int, scheduler_task['hhmm'].split(':'))

    term_time = scheduler_task["term_time"].split(" ")[0]
    now = get_current_time()
    if term_time:
        _term_time = datetime.strptime(term_time, '%Y-%m-%d').replace(hour=h, minute=m, second=0)
        if now >= _term_time:
            return None
    
    # execute only once
    if repeat == 0:
        ymd = scheduler_task['ymd']
        if not ymd:
            logger.info("get next exectime, no ymd, no repeat %s" % scheduler_task_id)
            return None

        exectime = datetime.strptime(ymd, '%Y-%m-%d').replace(hour=h, minute=m, second=0)
        return exectime if exectime > now else None

    # execute repeatly
    period = scheduler_task['period']
    exectime = now.replace(hour=h, minute=m, second=0)

    if period in [const.SCHETASK_PERIOD_DAILY]:
        if exectime <= now:
            exectime += timedelta(days=1)

    elif period.startswith(const.SCHETASK_PERIOD_WEEKLY):
        max_days = 32
        days = map(int, period.split(':')[1].split(','))
        while (exectime.weekday() + 1) not in days or exectime <= now:
            exectime += timedelta(days=1)
            max_days -= 1
            if max_days <= 0:
                break
    else:
        return None

    return exectime

class SchedulerTaskManager(object):

    _active = False
    lock_num = 300 # lock num in the lock group
    mgr_executings = {} # executing tasks in this manager
    mgr_scheduler_tasks = {} # schedulers in this manager
    def __init__(self):
        # lock group, to reduce conflict
        self.locks = []
        for _ in xrange(self.lock_num):
            self.locks.append(threading.RLock())

        self.history_mgr = HistoryManager()

        ctx = context.instance()
        self.sched_thr = SchedThread(ctx.sdmgr)
        self.sched_thr.setDaemon(True)
        self.sched_thr.start()

        # load scheduler data and push to sched thread
        if 0 != self.load():
            logger.error('load schedulers fail')
            exit_program(-1)

        self._active = True

    def is_active(self):
        return self._active
    
    def update_execute_time(self, scheduler_task_id, execute_time=None):
        
        ctx = context.instance()
        update_info = {}
        if execute_time:
            update_info["execute_time"] = execute_time
            update_info["status"] = const.SCHEDULER_TASK_STATUS_ACTIVE
        else:
            update_info["execute_time"] = None
            update_info["status"] = const.SCHEDULER_TASK_STATUS_INACTIVE
        
        if not ctx.pg.update(TB_SCHEDULER_TASK, scheduler_task_id, update_info):
            logger.error("update scheduler task [%s] execute [%s] failed", scheduler_task_id, update_info)
            return -1

        return 0
    
    def prepare_shutdown(self):
        # if server is inactive, will not accept new execute request
        self._active = False

        # wait for all executing scripts complete
        timeout = time.time() + EXECUTE_TIMEOUT + 10 # wait a little longer
        while len(self.mgr_executings) > 0:
            logger.warn('wait executing scripts [%s]', len(self.mgr_executings))
            time.sleep(1)
            if time.time() > timeout:
                break

        self.dump()

    def _is_obsolete_scheduler(self, sched_item):
    
        scheduler_task_id = sched_item.scheduler_task_id
        if scheduler_task_id not in self.mgr_scheduler_tasks:
            return True

        marked_updatetime = self.mgr_scheduler_tasks[scheduler_task_id]['update_time']
        return bool(marked_updatetime != sched_item.update_time)
    
    def execute_sched_task(self, scheduler_task_id, sched_item):

        ctx = context.instance()
        
        if self._is_obsolete_scheduler(sched_item):
            logger.info('ignore obsolete scheduler [%s]', sched_item)
            return 0
        # get
        scheduler_tasks = ctx.pgm.get_scheduler_tasks(scheduler_task_id)
        if not scheduler_tasks:
            logger.info('scheduler task[%s] should be deleted', scheduler_task_id)
            self.stop_scheduler_task(scheduler_task_id)
            return 0
        try:
            # execute
            scheduler_task = scheduler_tasks[scheduler_task_id]
            
            t = threading.Thread(target=self.execute_scheduler_task, args=(scheduler_task,))
            t.start()
            t.join(EXECUTE_TIMEOUT * 2)
    
            # push to sched thread if repeatable, otherwise stop it.
            if scheduler_task['repeat'] != 0:
                sched_time = get_next_exectime(scheduler_task)
                if sched_time:
                    sched_item.sched_time = sched_time
                    self.sched_thr.push(sched_item)
                self.update_execute_time(scheduler_task_id, sched_time)
            else:
                self.stop_scheduler_task(scheduler_task_id)
                
        except:
            logger.critical('yield exists when executing scheduler task [%s]: %s',(scheduler_task_id, traceback.format_exc()))
            sched_item.sched_time += 600 # retry after 10 min
            self.sched_thr.push(sched_item)

    def handle_sched_event(self, sched_item):

        # push back if not active(maybe is preparing to shutdown)
        if not self._active:
            self.sched_thr.push(sched_item)

        scheduler_task_id = sched_item.scheduler_task_id
        with self._lock(scheduler_task_id):
            self.execute_sched_task(scheduler_task_id, sched_item)

    def start_scheduler_task(self, scheduler_task_id, renew=False):

        ctx = context.instance()
        with self._lock(scheduler_task_id):
            if scheduler_task_id in self.mgr_scheduler_tasks and not renew:
                return True

            scheduler_tasks = ctx.pgm.get_scheduler_tasks(scheduler_task_id)
            if not scheduler_tasks:
                logger.error('get scheduler task[%s] failed', scheduler_task_id)
                return False
            scheduler_task = scheduler_tasks[scheduler_task_id]

            update_time = get_current_time(False)
            sched_time = get_next_exectime(scheduler_task)

            if sched_time:
                sched_item = SchedItem(sched_time, scheduler_task_id, update_time)
                
                self.sched_thr.push(sched_item)
                self.mgr_scheduler_tasks[scheduler_task_id] = {'update_time': update_time}
                self.dump()
                
                self.update_execute_time(scheduler_task_id, sched_time)
            else:
                self.update_execute_time(scheduler_task_id)

            return True

    def stop_scheduler_task(self, scheduler_task_id):
    
        with self._lock(scheduler_task_id):

            if scheduler_task_id in self.mgr_scheduler_tasks:
                del self.mgr_scheduler_tasks[scheduler_task_id]
                self.dump()
                self.update_execute_time(scheduler_task_id)

            logger.info('scheduler task [%s] is stopped', scheduler_task_id)

            return True

    def execute_scheduler_task(self, scheduler_task):

        ctx = context.instance()

        scheduler_task_id = scheduler_task['scheduler_task_id']
        if scheduler_task_id in self.mgr_executings:
            logger.error('scheduler task is still executing: %s', scheduler_task_id)
            return -1
    
        try:
            # check status
            if scheduler_task['status'] != SCHEDULER_TASK_STATUS_ACTIVE:
                logger.error('scheduler task [%s] is not active, reject execution', scheduler_task_id)
                return -1

            with transition_status(ctx, TB_SCHEDULER_TASK, scheduler_task_id, SCHEDULER_TASK_STATUS_EXECUTING):
                task_result = handle_scheduler_task(scheduler_task)

                if task_result:
                    self.history_mgr.save_scheduler_task_history(scheduler_task, task_result)
            
                return 0

        except:
            logger.critical('error occurred when executing scheduler task[%s]: %s', scheduler_task_id, traceback.format_exc())
            return None

        finally:
            if scheduler_task_id in self.mgr_executings:
                del self.mgr_executings[scheduler_task_id]

            logger.info('execute scheduler task [%s] complete', scheduler_task_id)

    def terminate_scheduler_task(self, scheduerl_task_id):
    
        try:
            with self._lock(scheduerl_task_id):
                if scheduerl_task_id in self.mgr_executings:
    
                    process = self.mgr_executings.pop(scheduerl_task_id)
                    os.kill(process.pid, signal.SIGKILL)
                    os.waitpid(-1, os.WNOHANG)
                return True
        except:
            logger.error('terminate scheduler task[%s] failed: %s', scheduerl_task_id, traceback.format_exc())
            return False

    @contextmanager
    def _lock(self, key):
    
        value = 0
        for char in key:
            value += ord(char)
        lock = self.locks[value % self.lock_num]
        lock.acquire()
        try:
            yield
        except Exception:
            logger.critical("yield exits with exception: %s", traceback.format_exc())
        lock.release()

    def dump(self, sche_item=None):
        # dump scheduler list
        d = os.path.dirname(DUMP_FILE)
        if not os.path.exists(d):
            os.makedirs(d)
        try:
            with open(DUMP_FILE, 'w') as fp:
                data = {
                        'mgr_scheduler_tasks': self.mgr_scheduler_tasks,
                        'sched_list': self.sched_thr.heap
                        }
                pickle.dump(data, fp)
            logger.info('dump [%s] scheduler items', len(self.sched_thr.heap))
        except Exception, e:
            logger.error('dump scheduler to dump file failed. [%s]', e)

    def load(self):

        if not os.path.exists(DUMP_FILE):
            logger.info('dump file [%s] not existed', DUMP_FILE)
            return 0
    
        try:
            with open(DUMP_FILE, 'r') as fp:
                ret = pickle.load(fp)
            # push to scheduler thread
            sched_list = ret['sched_list']
            self.sched_thr.push_all(sched_list)
            # set mgr_scheduler
            self.mgr_scheduler_tasks = ret['mgr_scheduler_tasks']
            logger.info('load [%s] schedulers from dump file', len(sched_list))
    
            return 0
        except Exception, e:
            logger.error('load scheduler tasks from dump file failed: [%s]', e)
            return -1
