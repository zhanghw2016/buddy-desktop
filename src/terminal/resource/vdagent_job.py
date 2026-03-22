'''
Created on 2018-5-16

@author: yunify
'''

import context
from db.constants import TB_VDAGENT_JOB
from utils.misc import get_current_time
from utils.id_tool import UUID_TYPE_VDAGENT_JOB, get_uuid
from utils.json import json_dump
from log.logger import logger
from constants import SUPPORT_JOB_STATUS, JOB_STATUS_PEND

def create_vdagent_job(action, directive, resource_id):
    ctx = context.instance()
    curtime = get_current_time(to_seconds=False)
    job_id = get_uuid(UUID_TYPE_VDAGENT_JOB, 
                      ctx.checker, 
                      long_format=True)
    job = {
        "job_id": job_id,
        "status": JOB_STATUS_PEND,
        "job_action": action,
        "directive": json_dump(directive),
        "resource_id": resource_id,
        "create_time": curtime,
        "status_time": curtime,
        }
    if not ctx.pg.insert(TB_VDAGENT_JOB, job):
        logger.error("insert vdagent job [%s] to db failed" % job)
        return None

    return job_id

def modify_vdagent_job(job_id, status):
    ctx = context.instance()
    if status not in SUPPORT_JOB_STATUS:
        logger.error("parameter status [%s] illegal" % (status))
        return False

    job = {"status": status,
           "status_time": get_current_time(to_seconds=False)}
    if not ctx.pg.update(TB_VDAGENT_JOB, 
                         job_id, 
                         job):
        logger.error("update job [%s] status failed" % (job_id))
        return False

    return True

def delete_vdagent_job(job_id):
    ctx = context.instance()

    if not ctx.pg.delete(TB_VDAGENT_JOB, job_id):
        logger.error("delete job [%s] failed" % (job_id))
        return False

    return True

def describe_vdagent_job(job_id):
    ctx = context.instance()

    job = ctx.pg.get(TB_VDAGENT_JOB, job_id)
    if job is None:
        logger.error("describe job [%s] failed" % (job_id))
        return None

    return job

def get_vdagent_job_status(job_id):
    ctx = context.instance()
    columns = ["status"]
    job = ctx.pg.get(TB_VDAGENT_JOB, job_id, columns)
    if not job:
        logger.error("describe job [%s] failed" % (job_id))
        return None

    return job[0]["status"]
