
from log.logger import logger
import constants as const
from qingcloud import const as qconst
import time
import db.constants as dbconst
from utils.misc import rLock
from utils.misc import get_current_time
import context

last_check_job_time = 0

class ResourceJob():

    def __init__(self, conn):
        
        if not conn:
            return None
        
        self.conn = conn
        
    def resource_describe_jobs(self, job_ids, retries=qconst.RES_ACTION_RETRIES):

        jobs = {}
        body = {"jobs": job_ids}

        while True:
            ret = self.conn.describe_jobs(body)
            if self.conn.check_res_error(ret, body):
                retries -= 1
                if retries == 0:
                    logger.error("describe job [%s] fail, retries: %s" % (body, retries))
                    return None
    
                time.sleep(qconst.RES_ACTION_RETRY_INTERVAL)
            else:
                job_set = ret["job_set"]
                for job in job_set:
                    job_id = job["job_id"]
                    jobs[job_id] = job

                return jobs

    def check_working_jobs(self):
        
        ctx = context.instance()
        global last_check_job_time

        if last_check_job_time > time.time() - qconst.CHECK_JOB_INTERVAL:
            return 0

        jobs = ctx.pgm.get_resource_jobs(status=[const.JOB_STATUS_PEND, const.JOB_STATUS_WORKING])
        if not jobs:
            logger.error("no found working job")
            return 0

        job_ids = jobs.keys()
        update_job = {}
        for i in xrange(0, len(job_ids), const.MAX_LIMIT_PARAM):
            end = i + const.MAX_LIMIT_PARAM
            if end > len(job_ids):
                end = len(job_ids)
    
            _job_ids = job_ids[i:end]
    
            ret = self.resource_describe_jobs( _job_ids)
            if not ret:
                logger.error("resource describe job fail: %s" % _job_ids)
                continue
    
            jobs = ret
            for job_id, job in jobs.items():
                status = job["status"]
                if status not in [const.JOB_STATUS_PEND, const.JOB_STATUS_WORKING, const.JOB_STATUS_SUCC]:
                    status = const.JOB_STATUS_FAIL
                
                update_job[job_id] = {
                                      "action": job.get("job_action", ""),
                                      "resource_ids": job.get("resource_ids", ''),
                                      "status": status
                                     }
        
        if update_job:
            if not ctx.pg.batch_update(dbconst.TB_RESOURCE_JOB, update_job):
                logger.error("Pull server, update resource job %s status fail" % (update_job))
                return -1
        
        last_check_job_time = time.time()
    
        return 0
    
    def refresh_resource_job(self, job_id):
        
        ctx = context.instance()
        jobs = ctx.pgm.get_resource_jobs(job_id)
        if not jobs:
            return const.JOB_STATUS_NEW
        
        job = jobs[job_id]    
        status = job["status"]

        if status in [const.JOB_STATUS_PEND, const.JOB_STATUS_WORKING]:
            return const.JOB_STATUS_WORKING

        elif status in [const.JOB_STATUS_SUCC]:
            return const.JOB_STATUS_SUCC

        else:
            return const.JOB_STATUS_FAIL
    
    def add_new_job(self, job_id):
        
        ctx = context.instance()
        new_job = {}
        job_info = {
                    "job_id": job_id,
                    "status": const.JOB_STATUS_PEND,
                    "action": '',
                    "resource_ids": '',
                    "create_time": get_current_time(),
                    "status_time": get_current_time(),
                    }
        new_job[job_id] = job_info

        if not ctx.pg.batch_insert(dbconst.TB_RESOURCE_JOB, new_job):
            logger.error("insert newly resource job [%s] to db failed" % new_job)
            return -1
        
        return 0
    
    def check_resource_job(self, job_id):

        job_status = self.refresh_resource_job(job_id)

        if job_status == const.JOB_STATUS_NEW:
            ret = self.add_new_job(job_id)
            if ret < 0:
                logger.error("add new job fail %s" % job_id)
                return -1

            return 1
        
        elif job_status == const.JOB_STATUS_WORKING:
            ret = self.check_working_jobs()
            if ret < 0:
                logger.error("check working job fail: %s" % job_id)
                return -1
            
            job_status = self.refresh_resource_job(job_id)

        if job_status == const.JOB_STATUS_FAIL:
            logger.error("check resouce job status %s" % job_status)
            return -1
        elif job_status == const.JOB_STATUS_SUCC:
            return 0
        else:
            return 1

    def wait_job_done(self, job_id, timeout=qconst.WAIT_JOB_TIMEOUT, interval=qconst.CHECK_JOB_INTERVAL):

        ctx = context.instance()
        end_time = time.time() + timeout

        while time.time() < end_time:

            with rLock(qconst.QC_RESOURCE_JOB_LOCK):

                ret = self.check_resource_job(job_id)
                if ret == -1:
                    logger.error("check resource jobs fail %s" % job_id)
                    return -1

                elif ret == 0:
                    return 0

            time.sleep(interval)

        update_job = {job_id: {"status": const.JOB_STATUS_FAIL}}
        if not ctx.pg.batch_update(dbconst.TB_RESOURCE_JOB, update_job):
            logger.error("wait job done, update resource job %s status fail" % (update_job))
            return -1

        logger.error("wait job[%s] status timeout" % job_id)
    
        return -1
