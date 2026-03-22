
import db.constants as dbconst
from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.id_tool import(
    get_uuid
)
import constants as const
from common import (
    check_resource_transition_status
)
from utils.id_tool import(
    UUID_TYPE_WORKFLOW_MODEL,
    UUID_TYPE_WORKFLOW_CONFIG
)
from utils.json import json_dump, json_load
from utils.misc import get_current_time
import random

def build_workflow_service_env(zone_id, service_type, api_action=None):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_workflow_service_action(service_type, api_action)
    if not ret:
        logger.error("no found service type %s" % (service_type))
        return Error(ErrorCodes.WF_SERVICE_TYPE_ENV_ERROR,
                     ErrorMsg.ERR_MSG_WORKFLOW_SERVICE_TYPE_NOT_FOUND, (service_type))

    public_param_list = []

    for _, action_data in ret.items():
        
        service_action_info = action_data["service_action_info"]
        
        public_params = service_action_info.get("public_params")
        if not public_params:
            continue
        
        public_param_list.extend(public_params)
        
    env_data = {}
    
    if "auth_service" in public_param_list:
        ret = ctx.pgm.get_auth_zone(zone_id)
        if not ret:
            logger.error("workflow evn error %s" % (service_type))
            return Error(ErrorCodes.WF_SERVICE_TYPE_ENV_ERROR,
                         ErrorMsg.ERR_MSG_AUTH_SERVICE_NO_FOUND, (zone_id))
        
        auth_service = ret
        env_data["auth_service"] = auth_service

        if "user_group" in public_param_list:
            ret = ctx.pgm.get_desktop_user_groups(auth_service["auth_service_id"])
            if not ret:
                ret = {}
                
            env_data["user_group"] = ret.values()

        if "user_groups" in public_param_list:
            ret = ctx.pgm.get_desktop_user_groups(auth_service["auth_service_id"])
            if not ret:
                ret = {}
                
            env_data["user_groups"] = ret.values()

    if "desktop_group" in public_param_list:
        ret = ctx.pgm.get_desktop_groups(zone_id=zone_id)
        if not ret:
            ret = {}
        
        env_data["desktop_group"] = ret.values()
    
    if "delivery_group" in public_param_list:
        ret = ctx.pgm.get_delivery_groups(zone_id=zone_id)
        if not ret:
            ret = {}
        env_data["delivery_group"] = ret.values()

    return env_data

def format_service_params(api_actions):
    ctx = context.instance()
    
    param_keys = []
    for api_action in api_actions:
        result_params = api_action["result_params"]
        if result_params:
            for key in result_params:
                if key in param_keys:
                    continue
                param_keys.append(key)
        
        public_params = api_action["public_params"]
        if public_params:
            for key in public_params:
                if key in param_keys:
                    continue
                param_keys.append(key)
        
        extra_params = api_action["extra_params"]
        if extra_params:
            for key in extra_params:
                if key in param_keys:
                    continue
                param_keys.append(key)

        required_params = api_action["required_params"]
        if required_params:
            for key in required_params:
                if key in param_keys:
                    continue
                param_keys.append(key)
    
    if not param_keys:
        return None

    ret = ctx.pgm.get_service_param_names(param_keys)
    if not ret:
        return None

    return ret

def format_workflow_services(workflow_service_set):
    
    ctx = context.instance()
    for _, workflow_service in workflow_service_set.items():
        
        service_type = workflow_service["service_type"]
        
        ret = ctx.pgm.get_workflow_service_action(service_type)
        if not ret:
            continue

        service_actions = ret.values()
        for service_action in service_actions:
            if "service_action_info" in service_action:
                del service_action["service_action_info"]
                
        param_names = ctx.pgm.get_service_param_names()
        if param_names:
            workflow_service["param_names"] = param_names

        workflow_service["service_actions"] = service_actions

    return workflow_service_set

def check_workflow_service_actions(zone_id, service_type, api_actions, env_params):

    ctx = context.instance()

    service_actions = ctx.pgm.get_workflow_service_action(service_type, api_actions)
    if not service_actions:
        logger.error("no found service action %s, %s" % (service_type, service_actions))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                 ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, service_type)
    
    # check api action
    for api_action in api_actions:
        if api_action in service_actions:
            continue
        logger.error("no found service action.1 %s" % api_action)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                 ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, api_action)
        
    env_data = build_workflow_service_env(zone_id, service_type, api_actions)
    if not env_data:
        logger.error("no found service env_data %s" % api_actions)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                 ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, api_action)
    
    for env_key, _ in env_data.items():
        if env_key not in env_params:
            logger.error("no found service env_data.1 %s" % env_data)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                 ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, api_action)
    
    ret = ctx.pgm.get_workflow_service_action(service_type, api_actions,is_head=[1, 8])
    if not ret:
        logger.error("no found service head %s" % ret)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                 ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, api_action)
    
    return None

def format_workflow_models(workflow_model_set):

    ctx = context.instance()
    for workflow_model_id, workflow_model in workflow_model_set.items():
        
        service_type = workflow_model["service_type"]
        api_actions = json_load(workflow_model["api_actions"])
       
        service_actions = ctx.pgm.get_workflow_service_action(service_type, api_actions, ignore_action_info=True)
        if not service_actions:
            service_actions = {}

        workflow_model["model_actions"] = service_actions.values()
        
        service_actions = ctx.pgm.get_workflow_service_action(service_type, api_actions, is_head=[1,8])
        if not service_actions:
            service_actions = {}
            
        required_params = []
        extra_params = []
        for _, api_data in service_actions.items():
            service_action_info = api_data["service_action_info"]
            if not service_action_info:
                continue
            _required_params = service_action_info["required_params"]
            if not _required_params:
                continue
            
            required_params.extend(_required_params)
            
            _extra_params = service_action_info["extra_params"]
            if not _extra_params:
                continue
            extra_params.extend(_extra_params)
            
        workflow_model["required_params"] = required_params
        workflow_model["extra_params"] = extra_params
        
        workflows = ctx.pgm.get_workflows(workflow_model_id=workflow_model_id)
        if not workflows:
            workflows = {}
            
        workflow_status = {}
        wait_workflow = 0
        fail_workflow = 0
        
        for _, workflow in workflows.items():
            status = workflow["status"]
            if status == const.WORKFLOW_STATUS_PENDING:
                wait_workflow = wait_workflow+1
            elif status == const.WORKFLOW_STATUS_FAIL:
                fail_workflow = fail_workflow +1
            
        workflow_status["pending"] = wait_workflow
        workflow_status["fail"] = fail_workflow
        workflow_status["total"] = len(workflows)
        
        workflow_model["workflow_status"] = workflow_status
    
        param_names = ctx.pgm.get_service_param_names()
        if param_names:
            workflow_model["param_names"] = param_names


    return workflow_model_set

def create_workflow_model(zone_id, service_type, api_actions, env_params, req):
    
    ctx = context.instance()
    workflow_model_id = get_uuid(UUID_TYPE_WORKFLOW_MODEL, ctx.checker)

    update_info = dict(
                      workflow_model_id = workflow_model_id,
                      service_type = service_type,
                      api_actions = json_dump(api_actions),
                      env_params = json_dump(env_params),
                      description= req.get("description", ""), 
                      create_time = get_current_time(),
                      workflow_model_name = req.get("workflow_model_name"),
                      zone = zone_id
                      )

    # register desktop group
    if not ctx.pg.insert(dbconst.TB_WORKFLOW_MODEL, update_info):
        logger.error("insert newly created workflow model for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return workflow_model_id

def check_workflow_model_vaild(workflow_model_ids, check_trans_status=False, check_status=None, service_type=None):
    
    ctx = context.instance()
    
    if not isinstance(workflow_model_ids, list):
        workflow_model_ids = [workflow_model_ids]
    
    ret = ctx.pgm.get_workflow_models(workflow_model_ids)
    if not ret:
        logger.error("no found workflow model %s" % (workflow_model_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, workflow_model_ids)

    workflow_models = ret

    for workflow_model_id, workflow_model in workflow_models.items():
        
        if service_type:
            if service_type != workflow_model["service_type"]:
                return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_WORKFLOW_MODEL_DISMATCH, workflow_model_id)
        
        if workflow_model_id not in workflow_models:
            logger.error("no found workflow model %s" % (workflow_model_id))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, workflow_model_id)
        
        workflows = ctx.pgm.get_workflows(workflow_model_id=workflow_model_id)
        if not workflows:
            workflows = {}

        if check_trans_status and workflows:
            ret = check_resource_transition_status(workflows)
            if isinstance(ret, Error):
                return ret
        
        for workflow_id, workflow in workflows.items():
            if check_status and workflow["status"] != check_status:
                logger.error("workflow %s status dismatch %s, %s" % (workflow_id, workflow["status"], check_status))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_WORKFLOW_STATUS_DISMATCH, (workflow_id, check_status))

    return workflow_models

def modify_workflow_model_attributes(workflow_model_id, need_maint_columns):
    
    ctx = context.instance()
    # update network info
    if not ctx.pg.batch_update(dbconst.TB_WORKFLOW_MODEL, {workflow_model_id: need_maint_columns}):
        logger.error("Failed to update desktop network[%s] " % (workflow_model_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def modify_workflow_model_public_params(workflow_model, public_params):
    
    ctx = context.instance()
    workflow_model_id = workflow_model["workflow_model_id"]
    if not public_params:
        return None
    logger.error("public_params %s" % public_params)
    
    update_info = False
    wf_env_params = json_load(workflow_model["env_params"])
    logger.error("public_params %s, %s" % (public_params, wf_env_params))
    for key, value in public_params.items():
        if key not in wf_env_params:
            wf_env_params[key] = value
            update_info = True
            continue
        
        if wf_env_params[key] != public_params[key]:
            wf_env_params[key] = value
            update_info = True
    
    if update_info:
        # update network info
        if not ctx.pg.batch_update(dbconst.TB_WORKFLOW_MODEL, {workflow_model_id: {"env_params": json_dump(wf_env_params)}}):
            logger.error("Failed to update desktop network[%s] " % (workflow_model_id))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def delete_workflow_models(workflow_model_ids):

    ctx = context.instance()
    ctx.pg.base_delete(dbconst.TB_WORKFLOW, {"workflow_model_id": workflow_model_ids})
    ctx.pg.base_delete(dbconst.TB_WORKFLOW_MODEL, {"workflow_model_id": workflow_model_ids})
    
    return

def check_workflow_config(workflow_model_id, request_type, service_type):
    
    ctx = context.instance()
    ret = ctx.pgm.get_workflow_configs(workflow_model_id=workflow_model_id,request_type=request_type, service_type=service_type)
    if ret:
        logger.error("workflow config existed %s, %s" % (request_type, workflow_model_id))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_ALREADY_EXISTED)
    
    return None

def check_workflow_request_action(request_action, workflow_model):

    service_type = workflow_model["service_type"]
    
    if request_action == const.WORKFLOW_REQUEST_ACTION_DELETE:
        if service_type not in const.WF_REQUEST_ACTION_DELETE_LIST:
            logger.error("workflow config error %s" % (request_action))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_WORKFLOW_REQUEST_ACTION_CANT_MATCH, request_action)
    elif request_action == const.WORKFLOW_REQUEST_ACTION_CREATE:
        if service_type not in const.WF_REQUEST_ACTION_CREATE_LIST:
            logger.error("workflow config error %s" % (request_action))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_WORKFLOW_REQUEST_ACTION_CANT_MATCH, request_action)

    return None

def get_workflow_request_action(request_action):

    if request_action == const.WORKFLOW_REQUEST_ACTION_DELETE:
        return const.WF_SERVICE_TYPE_DELETE_RESOURCE
    elif request_action == const.WORKFLOW_REQUEST_ACTION_CREATE:
        return const.WF_SERVICE_TYPE_CREATE_RESOURCE
    elif request_action == const.WF_SERVICE_TYPE_DELETE_RESOURCE or request_action == const.WF_SERVICE_TYPE_CREATE_RESOURCE:
        return request_action
    return None


def match_workflow_config(request_type, request_action):
    
    ctx = context.instance()
    service_type=get_workflow_request_action(request_action)
    if not service_type:
        logger.error("get_workflow_request_action %s not found" % request_action)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND,request_type)
                
    ret = ctx.pgm.get_workflow_configs(request_type=request_type,service_type=service_type,status=const.WORKFLOW_MODEL_CONFIG_STATUS_ACTIVE)

    if not ret:
        logger.error("get_workflow_configs %s,%s,active not found" % (request_type,service_type))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND,request_type)
    
    workflow_config_ids = ret.keys()
    
    config_count = random.randint(0, len(workflow_config_ids)-1)
    
    workflow_config_id = workflow_config_ids[config_count]
    workflow_config = ret[workflow_config_id]
    
    workflow_model_id = workflow_config["workflow_model_id"]
    if not workflow_model_id:
        logger.error("workflow_config_id %s model not found" % workflow_config_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND,request_type)
    
    workflow_model = ctx.pgm.get_workflow_model(workflow_model_id)
    if not workflow_model:
        logger.error("workflow_model id %s not found" % workflow_model_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND,request_type)
    
    return workflow_model
    
def create_workflow_config(workflow_model_id, request_type, service_type):
    
    ctx = context.instance()
    workflow_config_id = get_uuid(UUID_TYPE_WORKFLOW_CONFIG, ctx.checker)

    update_info = dict(
                      workflow_config_id = workflow_config_id,
                      workflow_model_id = workflow_model_id,
                      request_type = request_type,
                      request_action =service_type,
                      )

    # register desktop group
    if not ctx.pg.insert(dbconst.TB_WORKFLOW_CONFIG, update_info):
        logger.error("insert newly created workflow model for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return workflow_config_id

def check_workflow_config_vaild(workflow_config_ids):
    
    ctx = context.instance()
    ret = ctx.pgm.get_workflow_configs(workflow_config_ids)
    if not ret:
        logger.error("no found workflow config %s" % (workflow_config_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, workflow_config_ids)
    
    return ret
    
def modify_workflow_config(workflow_config_id, update_info):
    
    ctx = context.instance()

    # update network info
    if not ctx.pg.batch_update(dbconst.TB_WORKFLOW_CONFIG, {workflow_config_id: update_info}):
        logger.error("Failed to update desktop network[%s] " % (workflow_config_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def delete_workflow_configs(workflow_config_ids):
    
    ctx = context.instance()
    
    ctx.pg.base_delete(dbconst.TB_WORKFLOW_CONFIG, {"workflow_config_id": workflow_config_ids})
    
    return None

