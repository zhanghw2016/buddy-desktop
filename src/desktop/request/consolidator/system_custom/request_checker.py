
from constants import (
    ALL_PLATFORMS,

    # system custom
    ACTION_VDI_DESCRIBE_SYSTEM_CUSTOM_CONFIGS,
    ACTION_VDI_MODIFY_SYSTEM_CUSTOM_CONFIG_ATTRIBUTES,
    ACTION_VDI_RESET_SYSTEM_CUSTOM_CONFIGS
)
from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import SystemCustomRequestBuilder

class SystemCustomRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(SystemCustomRequestChecker, self).__init__(sender, checker)
        self.builder = SystemCustomRequestBuilder(sender)

        self.handler_map = {
                            ACTION_VDI_DESCRIBE_SYSTEM_CUSTOM_CONFIGS: self.describe_system_custom_configs,
                            ACTION_VDI_MODIFY_SYSTEM_CUSTOM_CONFIG_ATTRIBUTES: self.modify_system_custom_config_attributes,
                            ACTION_VDI_RESET_SYSTEM_CUSTOM_CONFIGS:self.reset_system_custom_configs
        }

    def describe_system_custom_configs(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=['zone','module_type','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and","force_refresh"],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.describe_system_custom_configs(**directive)

    def modify_system_custom_config_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "modify_contents"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['modify_contents'],
                                  filter_params=[]):
            return None

        return self.builder.modify_system_custom_config_attributes(**directive)

    def reset_system_custom_configs(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "module_type"],
                                  str_params=["zone","module_type"],
                                  integer_params=[],
                                  list_params=["item_key"],
                                  filter_params=[]):
            return None

        return self.builder.reset_system_custom_configs(**directive)



