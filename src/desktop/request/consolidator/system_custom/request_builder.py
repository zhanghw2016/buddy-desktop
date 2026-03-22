
from constants import (

    # system custom
    ACTION_VDI_DESCRIBE_SYSTEM_CUSTOM_CONFIGS,
    ACTION_VDI_MODIFY_SYSTEM_CUSTOM_CONFIG_ATTRIBUTES,
    ACTION_VDI_RESET_SYSTEM_CUSTOM_CONFIGS
)
from request.consolidator.base.base_request_builder import BaseRequestBuilder
from log.logger import logger

class SystemCustomRequestBuilder(BaseRequestBuilder):

    def describe_system_custom_configs(self,
                                zone=None,
                                module_type=None,
                                offset=None,
                                limit=20,
                                verbose=0,
                                reverse=0,
                                sort_key=None,
                                is_and=1,
                                force_refresh=0,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_SYSTEM_CUSTOM_CONFIGS
        body = {}
        if zone:
            body['zone'] = zone
        if module_type:
            body['module_type'] = module_type
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
        if force_refresh == 0:
            body['force_refresh'] = 0
        else:
            body['force_refresh'] = 1

        return self._build_params(action, body)

    def modify_system_custom_config_attributes(self,
                              zone,
                              modify_contents,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_SYSTEM_CUSTOM_CONFIG_ATTRIBUTES

        body = {}
        body["zone"] = zone
        body["modify_contents"] = modify_contents

        return self._build_params(action, body)

    def reset_system_custom_configs(self,
                              zone,
                              module_type,
                              item_key=None,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_RESET_SYSTEM_CUSTOM_CONFIGS

        body = {}
        body["zone"] = zone
        body["module_type"] = module_type
        if item_key:
            body['item_key'] = item_key

        return self._build_params(action, body)



