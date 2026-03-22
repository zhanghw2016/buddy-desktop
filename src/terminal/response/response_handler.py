'''
Created on 2018-5-17

@author: yunify
'''
import time
import context
import error.error_msg as ErrorMsg
import error.error_code as ErrorCodes
from error.error import Error
from log.logger import logger
from send_request import send_desktop_server_request
from constants import ACTION_VDI_DESCRIBE_DESKTOP_JOBS
from constants import JOB_STATUS_PEND, JOB_STATUS_WORKING, JOB_STATUS_SUCC

def wait_terminal_response(request_id, timeout=10):
    ''' wait terminal response '''
    ctx = context.instance()
    if request_id not in ctx.terminal_request.keys():
        return Error(ErrorCodes.TERMINAL_SERVER_INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_TERMINAL_UNKNOWK_REQUEST_ERROR,request_id)

    response = None
    for _ in range(timeout * 10):
        response = ctx.terminal_request.get(request_id)
        if response is None:
            time.sleep(0.2)
            continue
        else:
            break
    return ctx.terminal_request.pop(request_id)

def send_response_to_terminal(server, sock, rep_str):

    size = len(rep_str)
    try:
        ret = server.send(sock, rep_str, size)
        if ret != size:
            return -1
    except Exception,e:
        logger.error("send response to terminal with excepton: %s" % e)
        return -1
    return 0
    
def wait_desktop_job(job_id, zone, timeout=120, interval=3):
    ''' wait desktop server job '''
    end_time = time.time() + timeout

    while time.time() < end_time:

        req = {
        "type":"internal",
        "params":{"action": ACTION_VDI_DESCRIBE_DESKTOP_JOBS,
                  "jobs": [job_id],
                  "zone": zone
                },
        }
        ret = send_desktop_server_request(req)
        if ret.get("ret_code", -1) != 0:
            logger.error("wait job timeout.[%s][%s]" % (ret, job_id))
            return -1

        job_set = ret["desktop_job_set"]
        if not job_set:
            logger.error("describe jobs none.[%s][%s]" % (ret, job_id))
            return -1

        job = job_set[0]
        status = job["status"]

        if status in [JOB_STATUS_PEND, JOB_STATUS_WORKING]:
            time.sleep(interval)
            continue

        if status in [JOB_STATUS_SUCC]:
            return 0
        else:
            logger.error("jobs status fail.[%s][%s]" % (status, job_id))
            return -1

    return -1
