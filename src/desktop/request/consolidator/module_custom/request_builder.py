
from constants import (

    # module_custom
    ACTION_VDI_DESCRIBE_USER_MODULE_CUSTOMS,
    ACTION_VDI_CREATE_USER_MODULE_CUSTOM,
    ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_ATTRIBUTES,
    ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_CONFIGS,
    ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_ZONE_USER,
    ACTION_VDI_DELETE_USER_MODULE_CUSTOMS,
    ACTION_VDI_DESCRIBE_SYSTEM_MODULE_TYPES

)
from request.consolidator.base.base_request_builder import BaseRequestBuilder
from log.logger import logger

class ModuleCustomRequestBuilder(BaseRequestBuilder):

    def describe_user_module_customs(self,
                                    zone,
                                    module_customs=None,
                                    search_word=None,
                                    offset=None,
                                    limit=20,
                                    verbose=0,
                                    reverse=0,
                                    sort_key=None,
                                    is_and=1,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_USER_MODULE_CUSTOMS
        body = {}
        body["zone"] = zone
        if module_customs:
            body['module_customs'] = module_customs
        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if verbose is not None:
            body['verbose'] = int(verbose)
        if reverse == 0:
            body['reverse'] = 0
        else:
            body['reverse'] = 1
        if sort_key:
            body["sort_key"] = sort_key
        if is_and == 0:
            body['is_and'] = 0
        else:
            body['is_and'] = 1

        return self._build_params(action, body)

    def create_user_module_custom(self,
                                  zone,
                                  modify_contents,
                                  custom_name,
                                  zone_users,
                                  description=None,
                                  **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_USER_MODULE_CUSTOM

        body = {}
        body["zone"] = zone
        body["modify_contents"] = modify_contents
        body["custom_name"] = custom_name
        body["zone_users"] = zone_users
        if description:
            body["description"] = description

        return self._build_params(action, body)

    def modify_user_module_custom_attributes(self,
                              zone,
                              module_customs,
                              custom_name,
                              description=None,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_ATTRIBUTES

        body = {}
        body["zone"] = zone
        body["module_customs"] = module_customs
        body["custom_name"] = custom_name
        if description:
            body["description"] = description

        return self._build_params(action, body)

    def modify_user_module_custom_configs(self,
                              zone,
                              module_customs,
                              modify_contents,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_CONFIGS

        body = {}
        body["zone"] = zone
        body["module_customs"] = module_customs
        body["modify_contents"] = modify_contents

        return self._build_params(action, body)

    def modify_user_module_custom_zone_user(self,
                              zone,
                              module_customs,
                              zone_users,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_ZONE_USER

        body = {}
        body["zone"] = zone
        body["module_customs"] = module_customs
        body["zone_users"] = zone_users

        return self._build_params(action, body)

    def delete_user_module_customs(self,
                              zone,
                              module_customs,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_USER_MODULE_CUSTOMS

        body = {}
        body["zone"] = zone
        body["module_customs"] = module_customs

        return self._build_params(action, body)

    def describe_system_module_types(self,
                                     zone,
                                     item_key=None,
                                     enable_module=None,
                                     search_word=None,
                                     offset=None,
                                     limit=100,
                                     verbose=0,
                                     reverse=0,
                                     sort_key=None,
                                     is_and=1,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_SYSTEM_MODULE_TYPES
        body = {}
        body["zone"] = zone
        if item_key:
            body['item_key'] = item_key
        if enable_module is not None:
            body['enable_module'] = int(enable_module)
        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if verbose is not None:
            body['verbose'] = int(verbose)
        if reverse == 0:
            body['reverse'] = 0
        else:
            body['reverse'] = 1
        if sort_key:
            body["sort_key"] = sort_key
        if is_and == 0:
            body['is_and'] = 0
        else:
            body['is_and'] = 1

        return self._build_params(action, body)

