
import db.constants as dbconst

class ResourcePGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm
    
    def get_resource_jobs(self, job_ids=None, status=None):

        conditions = {}
        
        if job_ids:
            conditions["job_id"] = job_ids

        if status:
            conditions["status"] = status
            
        if not job_ids and not status:
            return None
        
        job_set = self.pg.base_get(dbconst.TB_RESOURCE_JOB, conditions)
        if job_set is None or len(job_set) == 0:
            return None

        jobs = {}
        for job in job_set:
            job_id = job["job_id"]
            jobs[job_id] = job

        return jobs
