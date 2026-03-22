
from constants import (
    ACTION_VDI_DESCRIBE_WORKFLOW_SERVICE_ENV,
    ACTION_VDI_DESCRIBE_WORKFLOW_SERVICES,
    ACTION_VDI_DESCRIBE_WORKFLOW_MODELS,
    ACTION_VDI_CREATE_WORKFLOW_MODEL,
    ACTION_VDI_MODIFY_WORKFLOW_MODEL_ATTRIBUTES,
    ACTION_VDI_DELETE_WORKFLOW_MODELS,
    
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

from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import WorkFlowRequestBuilder

class WorkFlowRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(WorkFlowRequestChecker, self).__init__(sender, checker)
        self.builder = WorkFlowRequestBuilder(sender)

        self.handler_map = {
                            ACTION_VDI_DESCRIBE_WORKFLOW_SERVICE_ENV: self.describe_workflow_service_env,
                            ACTION_VDI_DESCRIBE_WORKFLOW_SERVICES: self.describe_workflow_services,
                            ACTION_VDI_DESCRIBE_WORKFLOW_MODELS: self.describe_workflow_models,
                            ACTION_VDI_CREATE_WORKFLOW_MODEL: self.create_workflow_model,
                            ACTION_VDI_MODIFY_WORKFLOW_MODEL_ATTRIBUTES: self.modify_workflow_model_attributes,
                            ACTION_VDI_DELETE_WORKFLOW_MODELS: self.delete_workflow_models,
                            
                            ACTION_VDI_DESCRIBE_WORKFLOWS: self.describe_workflows,
                            ACTION_VDI_CREATE_WORKFLOWS: self.create_workflows,
                            ACTION_VDI_MODIFY_WORKFLOW_ATTRIBUTES: self.modify_workflow_attributes,
                            ACTION_VDI_DELETE_WORKFLOWS: self.delete_workflows,
                            ACTION_VDI_EXECUTE_WORKFLOWS: self.execute_workflows,
                            ACTION_VDI_DESCRIBE_WORKFLOW_MODEL_CONFIGS: self.describe_workflow_model_configs,
                            ACTION_VDI_CREATE_WORKFLOW_MODEL_CONFIG: self.create_workflow_model_config,
                            ACTION_VDI_MODIFY_WORKFLOW_MODEL_CONFIG: self.modify_workflow_model_config,
                            ACTION_VDI_DELETE_WORKFLOW_MODEL_CONFIGS: self.delete_workflow_model_configs,
                            ACTION_VDI_SEND_DESKTOP_REQUEST: self.send_desktop_request
            }


    def describe_workflow_service_env(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone_id", "service_type"],
                                  str_params=[],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return None

        return self.builder.describe_workflow_service_env(**directive)

    def describe_workflow_services(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=[],
                                  integer_params=[],
                                  list_params=["service_type", "service_actions"]
                                  ):
            return None

        return self.builder.describe_workflow_services(**directive)

    def describe_workflow_models(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["service_type", "workflow_models"]
                                  ):
            return None

        return self.builder.describe_workflow_models(**directive)

    def create_workflow_model(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone_id", "service_type", "api_actions", "env_params"],
                                  str_params=["service_type"],
                                  integer_params=["is_check"],
                                  json_params = ["env_params"],
                                  list_params=[]
                                  ):
            return None

        return self.builder.create_workflow_model(**directive)


    def modify_workflow_model_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "workflow_model"],
                                  str_params=["workflow_model", "description", "workflow_model_name"],
                                  json_params = ["public_params"],
                                  integer_params=[]):
            return None

        return self.builder.modify_workflow_model_attributes(**directive)

    def delete_workflow_models(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["workflow_models"]
                                  ):
            return None

        return self.builder.delete_workflow_models(**directive)

    def describe_workflows(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["search_word", "sort_key", "workflow_model"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["service_type", "workflows"]
                                  ):
            return None

        return self.builder.describe_workflows(**directive)

    def create_workflows(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["workflow_model", "action_params"],
                                  str_params=[],
                                  integer_params=[],
                                  list_params=[],
                                  list_dict_params=[],
                                  json_params=[]
                                  ):
            return None

        return self.builder.create_workflows(**directive)

    def modify_workflow_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["workflow", "action_params"],
                                  str_params=[],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return None

        return self.builder.modify_workflow_attributes(**directive)

    def delete_workflows(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["workflows"],
                                  str_params=[],
                                  integer_params=[],
                                  list_params=["workflows"]
                                  ):
            return None

        return self.builder.delete_workflows(**directive)

    def execute_workflows(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["workflow_model"],
                                  integer_params=[],
                                  list_params=["workflows"]
                                  ):
            return None

        return self.builder.execute_workflows(**directive)

    def describe_workflow_model_configs(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["workflow_model", "request_type","search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["workflow_configs","status"]
                                  ):
            return None

        return self.builder.describe_workflow_model_configs(**directive)

    def create_workflow_model_config(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["workflow_model", "request_type", "service_type"],
                                  str_params=["workflow_model", "request_type", "service_type"],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return None

        return self.builder.create_workflow_model_config(**directive)

    def modify_workflow_model_config(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["workflow_model"],
                                  integer_params=[],
                                  list_params=["workflows"]
                                  ):
            return None

        return self.builder.modify_workflow_model_config(**directive)

    def delete_workflow_model_configs(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["workflow_model"],
                                  integer_params=[],
                                  list_params=["workflows"]
                                  ):
            return None

        return self.builder.delete_workflow_model_configs(**directive)

    def send_desktop_request(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["data_info", "ou_dn", "request_type", "request_action"],
                                  str_params=[],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return None

        return self.builder.send_desktop_request(**directive)