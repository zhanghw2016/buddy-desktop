import db.constants as dbconst

class DispatchPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm
    
    def get_tasks(self, task_ids=None, status=None, job_id=None, task_level=None,resource_ids=None,task_type=None):

        conditions = {}
        if task_ids:
            conditions["task_id"] = task_ids
        if job_id:
            conditions["job_id"] = job_id
        if status is not None:
            conditions["status"] = status
        
        if task_level is not None:
            conditions["task_level"] = task_level

        if resource_ids is not None:
            conditions["resource_ids"] = resource_ids

        if task_type is not None:
            conditions["task_type"] = task_type
        
        task_set = self.pg.base_get(dbconst.TB_DESKTOP_TASK, conditions)
        if task_set is None or len(task_set) == 0:
            return None

        tasks = {}
        for task in task_set:
            task_id = task["task_id"]
            tasks[task_id] = task

        return tasks
    
    def get_desktop_tasks(self, job_id, status=None):
        
        conditions = {}
        if job_id:
            conditions["job_id"] = job_id

        if status is not None:
            conditions["status"] = status
        
        task_set = self.pg.base_get(dbconst.TB_DESKTOP_TASK, conditions)
        if task_set is None or len(task_set) == 0:
            return None

        tasks = {}
        for task in task_set:
            task_id = task["task_id"]
            tasks[task_id] = task

        return tasks
  
    def get_desktop_jobs(self, job_ids=None, status=None,resource_ids=None):

        conditions = {}
        if job_ids:
            conditions["job_id"] = job_ids
        if status:
            conditions["status"] = status
        if resource_ids is not None:
            conditions["resource_ids"] = resource_ids

       
        job_set = self.pg.base_get(dbconst.TB_DESKTOP_JOB, conditions)
        if job_set is None or len(job_set) == 0:
            return None

        jobs = {}
        for job in job_set:
            job_id = job["job_id"]
            jobs[job_id] = job

        return jobs
