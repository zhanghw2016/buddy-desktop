import db.constants as dbconst

class SchedulerPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_scheduler_tasks(self, scheduler_task_ids=None, status=None):

        conditions = {}

        if scheduler_task_ids:
            conditions["scheduler_task_id"] = scheduler_task_ids
        
            
        if status is not None:
            conditions["status"] = status
        
        scheduler_task_set = self.pg.base_get(dbconst.TB_SCHEDULER_TASK, conditions)
        if scheduler_task_set is None or len(scheduler_task_set) == 0:
            return None

        scheduler_tasks = {}
        for scheduler_task in scheduler_task_set:
            scheduler_task_id = scheduler_task["scheduler_task_id"]
            scheduler_tasks[scheduler_task_id] = scheduler_task

        return scheduler_tasks

    def get_scheduler_task_resource(self, scheduler_task_id, resource_ids=None):

        conditions = {}

        if scheduler_task_id:
            conditions["scheduler_task_id"] = scheduler_task_id
        
        if resource_ids:
            conditions["resource_id"] = resource_ids
        
        task_resource_set = self.pg.base_get(dbconst.TB_SCHEDULER_TASK_RESOURCE, conditions)
        if task_resource_set is None or len(task_resource_set) == 0:
            return None

        task_resources = {}
        for task_resource in task_resource_set:
            resource_id = task_resource["resource_id"]
            task_resources[resource_id] = task_resource

        return task_resources
