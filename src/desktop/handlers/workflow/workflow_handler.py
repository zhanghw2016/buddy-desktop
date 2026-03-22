import context
from db.constants  import (
    GOLBAL_ADMIN_COLUMNS,
    CONSOLE_ADMIN_COLUMNS,
)
import db.constants as dbconst
import constants as const
from common import (
    build_filter_conditions,
    get_sort_key,
    get_reverse,
    return_error,
    return_items,
    return_success,
)
import resource_control.desktop.resource_permission as ResCheck
from utils.json import json_load
from utils.misc import get_columns
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.workflow.workflow_service as WorkflowService
import resource_control.workflow.workflow as Workflow
import api.user.user as APIUser


def handle_describe_workflow_service_env(req):
    
    ret = ResCheck.check_request_param(req, ["service_type", "zone_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    service_type = req["service_type"]
    zone_id = req["zone_id"]
    
    env_set = WorkflowService.build_workflow_service_env(zone_id, service_type)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    rep = {"env_set": env_set}
    
    return return_items(req, rep, "workflow_service_env")

def handle_describe_workflow_services(req):
    
    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_WORKFLOW_SERVICE)
    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_WORKFLOW_SERVICE]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_WORKFLOW_SERVICE]
    else:
        display_columns = []

    workflow_service_set = ctx.pg.get_by_filter(dbconst.TB_WORKFLOW_SERVICE, filter_conditions, display_columns)
    if workflow_service_set is None:
        logger.error("describe workflow service failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    WorkflowService.format_workflow_services(workflow_service_set)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_WORKFLOW_SERVICE, filter_conditions)
    if total_count is None:
        logger.error("get workflow service count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, workflow_service_set, "workflow_service", **rep)

def handle_describe_workflow_models(req):
    
    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_WORKFLOW_MODEL)
    del filter_conditions["zone"]
    workflow_model_ids = req.get("workflow_models")
    if workflow_model_ids:
        filter_conditions["workflow_model_id"] = workflow_model_ids

    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_WORKFLOW_MODEL]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_WORKFLOW_MODEL]
    else:
        display_columns = []

    workflow_model_set = ctx.pg.get_by_filter(dbconst.TB_WORKFLOW_MODEL, filter_conditions, display_columns, 
                                      sort_key = get_sort_key(dbconst.TB_WORKFLOW_MODEL, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", dbconst.DEFAULT_LIMIT)
                                      )
                                      
    if workflow_model_set is None:
        logger.error("describe workflow model failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    WorkflowService.format_workflow_models(workflow_model_set)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_WORKFLOW_MODEL, filter_conditions)
    if total_count is None:
        logger.error("get workflow model count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, workflow_model_set, "workflow_model", **rep)

def handle_create_workflow_model(req):
    
    ret = ResCheck.check_request_param(req, ["zone_id", "service_type", "env_params", "api_actions"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    zone_id = req["zone_id"]
    service_type = req["service_type"]
    api_actions = json_load(req["api_actions"])
    env_params = req.get("env_params")
    if env_params:
        env_params = json_load(req["env_params"])
    else:
        env_params = {}

    is_check = req.get("is_check", 0)
    
    ret = WorkflowService.check_workflow_service_actions(zone_id, service_type, api_actions, env_params)
    if isinstance(ret, Error):
        return return_error(req, ret)

    rep = {}
    if is_check:
        return return_success(req, None, **rep)
        
    ret = WorkflowService.create_workflow_model(zone_id, service_type, api_actions, env_params, req)
    if isinstance(ret, Error):
        return return_error(req, ret)

    workflow_model_id = ret
    rep = {"workflow_model_id": workflow_model_id}
    return return_success(req, None, **rep)

def hanlde_modify_workflow_model_attributes(req):
    
    ret = ResCheck.check_request_param(req, ["workflow_model"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    workflow_model_id = req["workflow_model"]
    public_params = req.get("public_params")
    ret = WorkflowService.check_workflow_model_vaild(workflow_model_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    workflow_model = ret[workflow_model_id]

    # need maintenance mode
    need_maint_columns = get_columns(req, ["description", "workflow_model_name"])
    if need_maint_columns:
        ret = WorkflowService.modify_workflow_model_attributes(workflow_model_id, need_maint_columns)
        if isinstance(ret, Error):
            return return_error(req, ret)
    
    if public_params:
        public_params = json_load(public_params)
        ret = WorkflowService.modify_workflow_model_public_params(workflow_model, public_params)
        if isinstance(ret, Error):
            return return_error(req, ret)

    return return_success(req, None)

def handle_delete_workflow_models(req):
    
    ret = ResCheck.check_request_param(req, ["workflow_models"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    workflow_model_ids = req["workflow_models"]

    ret = WorkflowService.check_workflow_model_vaild(workflow_model_ids, True, const.WORKFLOW_STATUS_SUCCESS)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = WorkflowService.delete_workflow_models(workflow_model_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ctx = context.instance()
    ret = ctx.pgm.get_workflow_configs(workflow_model_id=workflow_model_ids)
    workflow_configs=ret
    if ret:
        for workflow_config_id,_ in workflow_configs.items():
            columns = {}
            columns["status"] = 0
            ret = WorkflowService.modify_workflow_config(workflow_config_id, columns)

    return return_success(req, None)

def handle_describe_workflows(req):

    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_WORKFLOW)
    
    workflow_ids = req.get("workflows")
    if workflow_ids:
        filter_conditions["workflow_id"] = workflow_ids
        
    workflow_model_id = req.get("workflow_model")
    if workflow_model_id:
        filter_conditions["workflow_model_id"] = workflow_model_id
    
    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_WORKFLOW]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_WORKFLOW]
    else:
        display_columns = []

    workflow_set = ctx.pg.get_by_filter(dbconst.TB_WORKFLOW, filter_conditions, display_columns,
                                      sort_key = get_sort_key(dbconst.TB_WORKFLOW, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", dbconst.DEFAULT_LIMIT))
    if workflow_set is None:
        logger.error("describe workflow model failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    Workflow.format_workflows(workflow_set)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_WORKFLOW, filter_conditions)
    if total_count is None:
        logger.error("get workflow model count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, workflow_set, "workflow", **rep)

def handle_create_workflows(req):
    
    ret = ResCheck.check_request_param(req, ["workflow_model", "action_params"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    workflow_model_id = req["workflow_model"]
    action_params = json_load(req["action_params"])

    ret = WorkflowService.check_workflow_model_vaild(workflow_model_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    workflow_model = ret[workflow_model_id]
    
    ret = Workflow.check_workflow_action_params(workflow_model, action_params)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Workflow.create_workflow(workflow_model, action_params)
    if isinstance(ret, Error):
        return return_error(req, ret)
    workflow_ids = ret

    ret = {"workflow_ids": workflow_ids}
    return return_success(req, None, **ret)

def handle_modify_workflow_attributes(req):
    
    ret = ResCheck.check_request_param(req, ["workflow", "action_params"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    workflow_id = req["workflow"]
    
    action_params = json_load(req["action_params"])

    ret = Workflow.check_workflow_vaild(workflow_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    workflow = ret[workflow_id]
    workflow_model_id = workflow["workflow_model_id"]
    
    ret = WorkflowService.check_workflow_model_vaild(workflow_model_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    workflow_model = ret[workflow_model_id]

    ret = Workflow.check_workflow_action_params(workflow_model, action_params)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Workflow.modify_workflow_attributes(workflow_id, action_params)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_delete_workflows(req):
    
    ret = ResCheck.check_request_param(req, ["workflows"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    workflow_ids = req["workflows"]

    ret = Workflow.check_workflow_vaild(workflow_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Workflow.delete_workflows(workflow_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_execute_workflows(req):
    
    sender = req["sender"]
    
    ret = ResCheck.check_request_param(req, ["workflows", "workflow_model"], True)
    if isinstance(ret, Error):
        return return_error(req, ret)

    workflow_ids = req.get("workflows")
    workflow_model_id = req.get("workflow_model")

    ret = Workflow.check_workflow_vaild(workflow_ids, workflow_model_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    workflows = ret
    
    ret = Workflow.execute_workflows(workflows)
    if isinstance(ret, Error):
        return return_error(req, ret)
    job_workflows = ret
    job_uuid=None
    if job_workflows:     
        ret = Workflow.send_workflow_job(sender, job_workflows, const.JOB_ACTION_EXECUTE_WORKFLOWS)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_uuid = ret
    ret = {"workflow_ids": job_workflows}
    
    return return_success(req, None, job_uuid, **ret)

def handle_describe_workflow_model_configs(req):
    
    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_WORKFLOW_CONFIG)
    # global admin user can see all resources
    if APIUser.is_global_admin_user(sender):
        display_columns = GOLBAL_ADMIN_COLUMNS[dbconst.TB_WORKFLOW_CONFIG]
    elif APIUser.is_console_admin_user(sender):
        display_columns = CONSOLE_ADMIN_COLUMNS[dbconst.TB_WORKFLOW_CONFIG]
    else:
        display_columns = []

    workflow_config_set = ctx.pg.get_by_filter(dbconst.TB_WORKFLOW_CONFIG, filter_conditions, display_columns,
                                      sort_key = get_sort_key(dbconst.TB_WORKFLOW_CONFIG, req.get("sort_key")),
                                      reverse = get_reverse(req.get("reverse")),
                                      offset = req.get("offset", 0),
                                      limit = req.get("limit", dbconst.DEFAULT_LIMIT)                                               )
    if workflow_config_set is None:
        logger.error("describe workflow service failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_WORKFLOW_CONFIG, filter_conditions)
    if total_count is None:
        logger.error("get workflow service count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))

    rep = {'total_count':total_count} 
    return return_items(req, workflow_config_set, "workflow_config", **rep)

def handle_create_workflow_model_config(req):
    
    ret = ResCheck.check_request_param(req, ["workflow_model", "request_type", "service_type"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    workflow_model_id = req["workflow_model"]
    request_type = req["request_type"]
    service_type = req["service_type"]

    ret = WorkflowService.check_workflow_model_vaild(workflow_model_id, service_type=service_type)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ret = WorkflowService.check_workflow_config(workflow_model_id, request_type, service_type=service_type)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = WorkflowService.create_workflow_config(workflow_model_id,request_type,service_type)
    if isinstance(ret, Error):
        return return_error(req, ret)
    workflow_config_id = ret

    ret = {"workflow_config": workflow_config_id}
    return return_success(req, None, **ret)

def handle_modify_workflow_model_config(req):
    
    ret = ResCheck.check_request_param(req, ["workflow_config"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    workflow_config_id = req["workflow_config"]

    ret = WorkflowService.check_workflow_config_vaild(workflow_config_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    columns = get_columns(req, ["request_type", "status"])
    if columns:
        ret = WorkflowService.modify_workflow_config(workflow_config_id, columns)

    return return_success(req, None)

def handle_delete_workflow_model_configs(req):

    ret = ResCheck.check_request_param(req, ["workflow_configs"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    workflow_config_ids = req["workflow_configs"]

    ret = WorkflowService.check_workflow_config_vaild(workflow_config_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = WorkflowService.delete_workflow_configs(workflow_config_ids)
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    return return_success(req, None)

def handle_send_desktop_request(req):
    

    ret = ResCheck.check_request_param(req, ["request_type", "ou_dn", "data_info", "request_action"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    ou_dn = req["ou_dn"]
    request_type = req["request_type"]
    data_info = json_load(req["data_info"])
    request_action = req["request_action"]
    data_info["ou_dn"] = ou_dn
    ret = WorkflowService.match_workflow_config(request_type, request_action)
    if isinstance(ret, Error):
        return return_error(req, ret)

    workflow_model = ret
    
    ret = WorkflowService.check_workflow_request_action(request_action, workflow_model)
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret = Workflow.create_workflow(workflow_model, data_info)
    if isinstance(ret, Error):
        return return_error(req, ret)
    workflow_ids = ret
    sender = {"zone": workflow_model["zone"]}
    ret = Workflow.send_workflow_job(sender, workflow_ids, const.JOB_ACTION_EXECUTE_WORKFLOWS)
    if isinstance(ret, Error):
        return return_error(req, ret)

    job_uuid = ret
    ret = {"workflow_ids": workflow_ids}
    
    return return_success(req, None, job_uuid, **ret)
