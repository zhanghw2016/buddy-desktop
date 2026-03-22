
import db.constants as dbconst
from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.id_tool import(
    get_uuid
)
from utils.json import json_load
import constants as const
from utils.id_tool import(
    UUID_TYPE_WORKFLOW
)
from utils.json import json_dump
from utils.misc import get_current_time
import resource_control.desktop.job as Job
from common import (
    check_resource_transition_status
)

def send_workflow_job(sender, workflow_ids, action):
    
    if not isinstance(workflow_ids, list):
        workflow_ids = [workflow_ids]
    
    directive = {
                "sender": sender,
                "action": action,
                "workflows" : workflow_ids,
                }

    ret= Job.submit_desktop_job(action, directive, workflow_ids, const.REQ_TYPE_DESKTOP_JOB)
    if isinstance(ret, Error):
        return ret
    (job_uuid, _) = ret

    return job_uuid

def format_workflows(workflow_set):
    
    ctx = context.instance()
    for _, workflow in workflow_set.items():
        
        action_param = workflow["action_param"]
        if action_param:
            workflow["action_param"] = json_load(action_param)
        
        api_return = workflow["api_return"]
        if api_return:
            workflow["api_return"] = json_load(api_return)
        
        result = workflow["result"]
        if result:
            workflow["result"] = json_load(result)
            
        param_names = ctx.pgm.get_service_param_names()
        if param_names:
            workflow["param_names"] = param_names

    return workflow_set

def check_workflow_action_params(workflow_model, action_params):
    
    ctx = context.instance()
    if not isinstance(action_params, list):
        action_params = [action_params]

    workflow_model_id = workflow_model["workflow_model_id"]
    api_actions = json_load(workflow_model["api_actions"])
    service_type = workflow_model["service_type"]

    ret = ctx.pgm.get_workflow_service_action(service_type, api_actions, is_head=[1,8])
    if not ret:
        logger.error("workflow model no found action [%s][%s]" % (workflow_model_id, api_actions))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    head_action_info = ret.values()[0]
    
    service_action_info = head_action_info["service_action_info"]
    required_params = service_action_info["required_params"]
    for action_param in action_params:        
        for required_param in required_params:
            if required_param in action_param:
                continue
            return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)

    return None

def check_workflow_vaild(workflow_ids=None, workflow_model_id=None, check_trans_status=True, check_status=None):

    ctx = context.instance()
    
    if workflow_ids and not isinstance(workflow_ids, list):
        workflow_ids = [workflow_ids]
    
    if check_status and not isinstance(check_status, list):
        check_status = [check_status]    
        
    workflows = ctx.pgm.get_workflows(workflow_ids, workflow_model_id)
    if not workflows:
        workflows = {}
    
    if not workflow_ids:
        workflow_ids = []
    
    
    for workflow_id in workflow_ids:
        if workflow_id not in workflows:
            logger.error("workflow %s no found" % (workflow_id))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, workflow_id)
    
    if check_trans_status:
        ret = check_resource_transition_status(workflows)
        if isinstance(ret, Error):
            return ret

    if check_status:
        for workflow_id, workflow in workflows.items():
            if workflow["status"] not in check_status:
                logger.error("workflow %s status dismatch %s, %s" % (workflow_id, workflow["status"], check_status))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_WORKFLOW_STATUS_DISMATCH, (workflow_id, check_status))

    return workflows

def create_workflow(workflow_model, action_params):
    
    ctx = context.instance()
    workflow_model_id = workflow_model["workflow_model_id"]
    
    if not isinstance(action_params, list):
        action_params = [action_params]
    
    update_infos = {}
    workflow_ids = []
    for action_param in action_params:
        workflow_id = get_uuid(UUID_TYPE_WORKFLOW, ctx.checker)
        update_info = dict(
                          workflow_id = workflow_id,
                          workflow_model_id = workflow_model_id,
                          action_param = json_dump(action_param),
                          status = const.WORKFLOW_STATUS_PENDING,
                          curr_action = '',
                          workflow_params = json_dump(action_param),
                          create_time = get_current_time(),
                          status_time = get_current_time()
                          )
        update_infos[workflow_id] = update_info
        workflow_ids.append(workflow_id)

    # register desktop group
    if not ctx.pg.batch_insert(dbconst.TB_WORKFLOW, update_infos):
        logger.error("insert newly created workflow for [%s] to db failed" % (update_infos))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return workflow_ids

def modify_workflow_attributes(workflow_id, action_params):
    
    ctx = context.instance()
    
    if isinstance(action_params, list):
        action_param = action_params[0]
    if not ctx.pg.batch_update(dbconst.TB_WORKFLOW, {workflow_id: {"action_param": json_dump(action_param),"workflow_params": json_dump(action_param)}}):
        logger.error("Failed to update desktop network[%s] " % (workflow_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def delete_workflows(workflow_ids):
    
    ctx = context.instance()
    
    ctx.pg.base_delete(dbconst.TB_WORKFLOW, {"workflow_id": workflow_ids})
    
    return None

def execute_workflows(workflows):
    
    exec_workflows = []
    
    for workflow_id, workflow in workflows.items():

        status = workflow["status"]
        if status not in [const.WORKFLOW_STATUS_FAIL, const.WORKFLOW_STATUS_PENDING]:
            continue
        
        exec_workflows.append(workflow_id)
    
    return exec_workflows
