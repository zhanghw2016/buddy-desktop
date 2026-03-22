import db.constants as dbconst
from utils.json import json_load

class WorkflowPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm
    
    def get_workflow_service_action(self, service_type, api_action=None, is_head=[], ignore_action_info=False):
        
        conditions = {"service_type": service_type}
        if api_action:
            conditions["api_action"] = api_action
        
        if is_head:
            conditions["is_head"] = is_head
        
        service_action_set = self.pg.base_get(dbconst.TB_WORKFLOW_SERVICE_ACTION, conditions)
        if not service_action_set:
            return None
        
        service_action_infos = {}
        if not ignore_action_info:
            service_action_info_set = self.pg.base_get(dbconst.TB_WORKFLOW_SERVICE_ACTION_INFO)
            if not service_action_info_set:
                return None

            for service_action_info in service_action_info_set:
                api_action = service_action_info["api_action"]
                service_action_infos[api_action] = service_action_info
        
        service_actions = {}
        for service_action in service_action_set:
            api_action = service_action["api_action"]
            
            service_action_info = service_action_infos.get(api_action)
            
            if service_action_info:
                public_params = service_action_info["public_params"]
                if public_params:
                    service_action_info["public_params"] = json_load(public_params)
                else:
                    service_action_info["public_params"] = []
     
                required_params = service_action_info["required_params"]
                if required_params:
                    service_action_info["required_params"] = json_load(required_params)
                else:
                    service_action_info["required_params"] = []
                
                result_params = service_action_info["result_params"]
                if result_params:
                    service_action_info["result_params"] = json_load(result_params)
                else:
                    service_action_info["result_params"] = []
                
                extra_params = service_action_info["extra_params"]
                if extra_params:
                    service_action_info["extra_params"] = json_load(extra_params)
                else:
                    service_action_info["extra_params"] = []
                
                service_action["service_action_info"] = service_action_info

            service_actions[api_action] = service_action

        return service_actions

    def get_service_param_names(self, param_keys=None):
        
        conditions = {}
        if param_keys:
            conditions["param_key"] = param_keys

        service_param_set = self.pg.base_get(dbconst.TB_WORKFLOW_SERVICE_PARAM, conditions)
        if service_param_set is None or len(service_param_set) == 0:
            return None
        
        service_params = {}
        for service_param in service_param_set:
            param_key = service_param["param_key"]
            param_name = service_param["param_name"]
            if param_key in service_params:
                continue
            service_params[param_key] = param_name
        
        return service_params

    def get_service_type_required_params(self, service_type, api_action=None):
        
        ret = self.get_workflow_service_action(service_type, api_action)
        if not ret:
            return None
        service_actions = ret

        required_params = []
        for api_action, service_action in service_actions.items():
            
            params = service_action.get("required_params")
            if not params:
                continue
            
            for param in params:
                if param in required_params:
                    continue
                
                required_params.append(param)
        
        return required_params

    def get_workflow_model(self, workflow_model_id):
        
        conditions = {}
        conditions["workflow_model_id"] = workflow_model_id

        workflow_model_set = self.pg.base_get(dbconst.TB_WORKFLOW_MODEL, conditions)
        if workflow_model_set is None or len(workflow_model_set) == 0:
            return None

        return workflow_model_set[0]

    def get_workflow_models(self, workflow_model_ids=None, service_type=None):
        
        conditions = {}
        if workflow_model_ids:
            conditions["workflow_model_id"] = workflow_model_ids
        
        if service_type:
            conditions["service_type"] = service_type

        workflow_model_set = self.pg.base_get(dbconst.TB_WORKFLOW_MODEL, conditions)
        if workflow_model_set is None or len(workflow_model_set) == 0:
            return None

        workflow_models = {}
        for workflow_model in workflow_model_set:
            workflow_model_id = workflow_model["workflow_model_id"]            
            workflow_models[workflow_model_id] = workflow_model

        return workflow_models

    def get_workflow(self, workflow_id):
        
        conditions = {"workflow_id": workflow_id}

        workflow_set = self.pg.base_get(dbconst.TB_WORKFLOW, conditions)
        if workflow_set is None or len(workflow_set) == 0:
            return None

        return workflow_set[0]
    
    def get_workflows(self, workflow_ids=None, workflow_model_id=None, status=None):
        
        conditions = {}
        if workflow_ids:
            conditions["workflow_id"] = workflow_ids
        
        if workflow_model_id:
            conditions["workflow_model_id"] = workflow_model_id
        
        if status:
            conditions["status"] = status

        workflow_set = self.pg.base_get(dbconst.TB_WORKFLOW, conditions)
        if workflow_set is None or len(workflow_set) == 0:
            return None

        workflows = {}
        for workflow in workflow_set:
            workflow_id = workflow["workflow_id"]            
            workflows[workflow_id] = workflow

        return workflows
    
    def get_model_action_info(self, api_action):
    
        
        conditions = {"api_action": api_action}

        workflow_action_info_set = self.pg.base_get(dbconst.TB_WORKFLOW_SERVICE_ACTION_INFO, conditions)
        if not workflow_action_info_set:
            return None

        return workflow_action_info_set[0]

    def get_workflow_configs(self, workflow_config_id=None, workflow_model_id=None, ou_dn=None, request_type=None, service_type=None,status=None):

        conditions = {}
        if workflow_config_id:
            conditions["workflow_config_id"] = workflow_config_id

        if workflow_model_id:
            conditions["workflow_model_id"] = workflow_model_id

        if ou_dn:
            conditions["ou_dn"] = ou_dn

        if request_type:
            conditions["request_type"] = request_type
        
        if service_type:
            conditions["request_action"] = service_type
            
        if status is not None:
            conditions["status"] = status

        workflow_config_set = self.pg.base_get(dbconst.TB_WORKFLOW_CONFIG, conditions)
        if not workflow_config_set:
            return None

        workflow_configs = {}
        for workflow_config in workflow_config_set:
            workflow_config_id = workflow_config["workflow_config_id"]
            workflow_configs[workflow_config_id] = workflow_config
        
        return workflow_configs
