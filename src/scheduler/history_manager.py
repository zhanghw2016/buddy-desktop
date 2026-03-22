'''
Created on 2014-4-15

@author: yunify
'''
import threading
import traceback
import time
from db.constants import TB_SCHEDULER_TASK_HISTORY
from db.data_types import TimeStampType
from log.logger import logger
from utils.id_tool import get_uuid, UUID_TYPE_VDI_SCHEDULER_TASK_HISTORY
from utils.misc import get_current_time
import context
from utils.json import json_dump

class ClearThread(threading.Thread):

    INTERVAL = 3600 * 24
    MAX_HISTORY_LEN = 50
    EXPIRE_THRESHOLD = 3600 * 24 * 7

    def __init(self):
        super(ClearThread, self).__init__()

    def run(self):
        try:
            time.sleep(10)
            while True:
                self.clear_expired_history()
                time.sleep(self.INTERVAL)
        except:
            logger.critical('Exit with exception: %s', traceback.format_exc())

    def clear_expired_history(self):
        ''' If the length of an scheduler's history is greater than `MAX_HISTORY_LEN`,
            clear the old ones.
        '''
        ctx = context.instance()
        sql = 'select scheduler_task_id, count(scheduler_history_id) as cnt from %s \
               group by scheduler_task_id having count(scheduler_history_id) > %s' % \
               (TB_SCHEDULER_TASK_HISTORY, self.MAX_HISTORY_LEN)
        
        entries = ctx.pg.execute_sql(sql)
        if entries is None:
            logger.error('get scheduler history count failed when clear expired history [%s]', sql)
            return

        for entry in entries:
            self.delete_old_histories(entry['scheduler_task_id'])

    def delete_old_histories(self, scheduler_task_id):
    
        ctx = context.instance()
        # get the timestamp
        histories = ctx.pg.get_by_filter(TB_SCHEDULER_TASK_HISTORY,
                                         {'scheduler_task_id': scheduler_task_id},
                                         sort_key='create_time', reverse=True,
                                         limit=self.MAX_HISTORY_LEN)
        if not histories:
            logger.error('get scheduler task history failed')
            return
    
        time_point = histories.values()[-1]['create_time'].strftime('%Y-%m-%d %H:%M:%S')
        # delete histories that older than `time_point`
        condition = {
                    'scheduler_task_id': scheduler_task_id,
                    'create_time': TimeStampType([None, time_point]),
                    }
        rows = ctx.pg.get_all(TB_SCHEDULER_TASK_HISTORY, condition, sort_key='create_time')
        if not rows:
            return
    
        history_ids = [r['scheduler_history_id'] for r in rows]
        # delete from db
        ctx.pg.base_delete(TB_SCHEDULER_TASK_HISTORY, {'scheduler_history_id': history_ids})

class HistoryManager(object):

    def __init__(self):
        self.clear_thr = ClearThread()
        self.clear_thr.setDaemon(True)
        self.clear_thr.start()

    def save_scheduler_task_history(self, scheduler_task, task_result):

        ctx = context.instance()
        history_id = get_uuid(UUID_TYPE_VDI_SCHEDULER_TASK_HISTORY, ctx.checker)
        history = {
                    'scheduler_history_id': history_id,
                    'scheduler_task_id': scheduler_task['scheduler_task_id'],
                    'task_name': scheduler_task["task_name"],
                    "create_time": get_current_time(),
                    "task_msg": json_dump(task_result),
                   }

        if not ctx.pg.insert(TB_SCHEDULER_TASK_HISTORY, history):
            logger.error('insert scheduler history [%s] into db fail', history)
            return -1

        return 0

    def delete_scheduler_history(self, history_id=None, scheduler_task_id=None):
    
        ctx = context.instance()
        
        if not history_id and not scheduler_task_id:
            return
        
        condition = {}
        if history_id:
            condition["scheduler_history_id"] = history_id
        
        if scheduler_task_id:
            condition["scheduler_task_id"] = scheduler_task_id
        
        ctx.pg.base_delete(TB_SCHEDULER_TASK_HISTORY, condition)
        
        return
