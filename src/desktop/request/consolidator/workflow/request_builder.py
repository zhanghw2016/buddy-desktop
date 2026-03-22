
from constants import (
    ACTION_VDI_DESCRIBE_WORKFLOW_MODELS,
    ACTION_VDI_CREATE_WORKFLOW_MODEL,
    ACTION_VDI_MODIFY_WORKFLOW_MODEL_ATTRIBUTES,
    ACTION_VDI_DELETE_WORKFLOW_MODELS,
    ACTION_VDI_DESCRIBE_WORKFLOW_SERVICE_ENV,
    ACTION_VDI_DESCRIBE_WORKFLOW_SERVICES,
    ACTION_VDI_DESCRIBE_WORKFLOWS,
    ACTION_VDI_CREATE_WORKFLOWS,
    ACTION_VDI_MODIFY_WORKFLOW_ATTRIBUTES,
    ACTION_VDI_DELETE_WORKFLOWS,
    ACTION_VDI_EXECUTE_WORKFLOWS,
    ACTION_VDI_DESCRIBE_WORKFLOW_MODEL_CONFIGS,
    ACTION_VDI_CREATE_WORKFLOW_MODEL_CONFIG,
    ACTION_VDI_MODIFY_WORKFLOW_MODEL_CONFIG,
    ACTION_VDI_DELETE_WORKFLOW_MODEL_CONFIGS,
    ACTION_VDI_SEND_DESKTOP_REQUEST
)
from request.consolidator.base.base_request_builder import BaseRequestBuilder

class WorkFlowRequestBuilder(BaseRequestBuilder):

    def describe_workflow_service_env(self,
                                   service_type,
                                   zone_id,
                                   **params
                                   ):

        action = ACTION_VDI_DESCRIBE_WORKFLOW_SERVICE_ENV
        body = {}
        body["service_type"] = service_type
        body["zone_id"] = zone_id

        return self._build_params(action, body)

    def describe_workflow_services(self,
                                   service_type=None,
                                   service_actions=None,
                                   **params
                                   ):

        action = ACTION_VDI_DESCRIBE_WORKFLOW_SERVICES
        body = {}
        if service_type:
            body["service_type"] = service_type
        if service_actions:
            body["service_actions"] = service_actions

        return self._build_params(action, body)

    def describe_workflow_models(self,
                                 zone,
                                 workflow_models = None,
                                 service_type=None,
                                 reverse = None,
                                 sort_key = None,
                                 offset = 0,
                                 limit = 20,
                                 search_word = None,
                                 verbose = 0,
                                 **params
                                 ):

        action = ACTION_VDI_DESCRIBE_WORKFLOW_MODELS
        body = {"zone": zone}
        
        if workflow_models:
            body["workflow_models"] = workflow_models
        
        if service_type:
            body["service_type"] = service_type

        if reverse:
            body["reverse"] = reverse
        
        if sort_key:
            body["sort_key"] = sort_key
        
        if offset is not None:
            body["offset"] = offset

        if limit:
            body["limit"] = limit

        if search_word:
            body["search_word"] = search_word
        
        if verbose is not None:
            body["verbose"] = verbose
         
        return self._build_params(action, body)

    def create_workflow_model(self,
                              zone_id,
                              service_type,
                              api_actions,
                              env_params,
                              workflow_model_name=None,
                              description=None,
                              is_check=None,
                              **params
                              ):

        action = ACTION_VDI_CREATE_WORKFLOW_MODEL
        body = {"zone_id": zone_id}
        body["service_type"] = service_type
        body["api_actions"] = api_actions
        body["env_params"] = env_params
        if workflow_model_name:
            body["workflow_model_name"] = workflow_model_name
        if description:
            body["description"] = description
        if is_check is not None:
            body["is_check"] = is_check

        return self._build_params(action, body)

    def modify_workflow_model_attributes(self,
                                       zone,
                                       workflow_model,
                                       workflow_model_name=None,
                                       description=None,
                                       public_params = None,
                                       **params):

        action = ACTION_VDI_MODIFY_WORKFLOW_MODEL_ATTRIBUTES
        body = {
            "zone": zone,
            "workflow_model": workflow_model,
            }
        
        if description is not None:
            body["description"] = description
        
        if workflow_model_name is not None:
            body["workflow_model_name"] = workflow_model_name
        
        if public_params:
            body["public_params"] = public_params
     
        return self._build_params(action, body)
    
    def delete_workflow_models(self,
                             workflow_models,
                             **params
                             ):

        action = ACTION_VDI_DELETE_WORKFLOW_MODELS
        body = {"workflow_models": workflow_models}
        return self._build_params(action, body)

    def describe_workflows(self, 
                           workflows = None,
                           workflow_model = None,
                           status = None,
                           reverse = None,
                           sort_key = None,
                           offset = 0,
                           limit = 20,
                           search_word = None,
                           verbose = 0,
                           **params
                           ):

        action = ACTION_VDI_DESCRIBE_WORKFLOWS
        body = {}
        if workflows:
            body["workflows"] = workflows
        
        if workflow_model:
            body["workflow_model"] = workflow_model

        if status:
            body["status"] = status
        
        if reverse:
            body["reverse"] = reverse

        if sort_key:
            body["sort_key"] = sort_key

        if offset is not None:
            body["offset"] = offset

        if limit is not None:
            body["limit"] = limit

        if search_word is not None:
            body["search_word"] = search_word

        if verbose is not None:
            body["verbose"] = verbose
  
        return self._build_params(action, body)

    def create_workflows(self, 
                         workflow_model,
                         action_params,
                         **params
                         ):
        
        action = ACTION_VDI_CREATE_WORKFLOWS
        body = {"workflow_model":workflow_model, "action_params":action_params}

        return self._build_params(action, body)

    def delete_workflows(self, 
                         workflows,
                       **params
                       ):
        
        action = ACTION_VDI_DELETE_WORKFLOWS
        body = {"workflows": workflows}

        return self._build_params(action, body)
    
    def modify_workflow_attributes(self, 
                                   workflow,
                                   action_params,
                                   **params
                                   ):
        
        action = ACTION_VDI_MODIFY_WORKFLOW_ATTRIBUTES
        body = {"workflow": workflow, "action_params": action_params}

        return self._build_params(action, body)

    def execute_workflows(self, 
                          workflows=None,
                          workflow_model=None,
                          **params
                          ):
        
        action = ACTION_VDI_EXECUTE_WORKFLOWS
        body = {}
        
        if workflows:
            body["workflows"] = workflows
        
        if workflow_model:
            body["workflow_model"] = workflow_model

        return self._build_params(action, body)

    def describe_workflow_model_configs(self, 
                                        workflow_configs=None,
                                        workflow_model=None,
                                        request_type = None,
                                        reverse = None,
                                        sort_key = None,
                                        offset = 0,
                                        limit = 20,
                                        search_word = None,
                                        verbose = 0,
                                        status = None,
                                        **params                                        
                                        ):
        
        action = ACTION_VDI_DESCRIBE_WORKFLOW_MODEL_CONFIGS
        body = {}
        
        if workflow_configs:
            body["workflow_configs"] = workflow_configs
        
        if workflow_model:
            body["workflow_model"] = workflow_model

        if request_type:
            body["request_type"] = request_type

        if reverse:
            body["reverse"] = reverse
        
        if sort_key:
            body["sort_key"] = sort_key
        
        if offset is not None:
            body["offset"] = offset

        if limit:
            body["limit"] = limit

        if search_word:
            body["search_word"] = search_word
        
        if verbose is not None:
            body["verbose"] = verbose

        if status is not None:
            body['status'] = status
            
        return self._build_params(action, body)

    def create_workflow_model_config(self, 
                          workflow_model,
                          request_type,
                          service_type,
                          **params
                          ):
        
        action = ACTION_VDI_CREATE_WORKFLOW_MODEL_CONFIG
        body = {"workflow_model": workflow_model, "request_type": request_type, "service_type": service_type}

        return self._build_params(action, body)

    def modify_workflow_model_config(self, 
                          workflow_config,
                          status,
                          **params
                          ):
        
        action = ACTION_VDI_MODIFY_WORKFLOW_MODEL_CONFIG
        body = {"workflow_config": workflow_config, "status": status}

        return self._build_params(action, body)

    def delete_workflow_model_configs(self, 
                                      workflow_configs,
                                      **params
                                      ):
        
        action = ACTION_VDI_DELETE_WORKFLOW_MODEL_CONFIGS
        body = {"workflow_configs": workflow_configs}

        return self._build_params(action, body)

    def send_desktop_request(self,
                          data_info,
                          request_action,
                          request_type,
                          ou_dn,
                          **params
                          ):
        
        action = ACTION_VDI_SEND_DESKTOP_REQUEST
        body = {"data_info": data_info, "request_type": request_type, "ou_dn": ou_dn, "request_action": request_action}

        return self._build_params(action, body)