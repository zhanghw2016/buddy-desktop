
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

from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import ModuleCustomRequestBuilder

class ModuleCustomRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(ModuleCustomRequestChecker, self).__init__(sender, checker)
        self.builder = ModuleCustomRequestBuilder(sender)

        self.handler_map = {
                    # module custom
                    ACTION_VDI_DESCRIBE_USER_MODULE_CUSTOMS: self.describe_user_module_customs,
                    ACTION_VDI_CREATE_USER_MODULE_CUSTOM: self.create_user_module_custom,
                    ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_ATTRIBUTES: self.modify_user_module_custom_attributes,
                    ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_CONFIGS: self.modify_user_module_custom_configs,
                    ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_ZONE_USER: self.modify_user_module_custom_zone_user,
                    ACTION_VDI_DELETE_USER_MODULE_CUSTOMS: self.delete_user_module_customs,
                    ACTION_VDI_DESCRIBE_SYSTEM_MODULE_TYPES: self.describe_system_module_types
        }

    def describe_user_module_customs(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone",'search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=['module_customs'],
                                  filter_params=[]):
            return None

        return self.builder.describe_user_module_customs(**directive)

    def create_user_module_custom(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "modify_contents", "custom_name"],
                                  str_params=["zone", "description", "custom_name"],
                                  integer_params=[],
                                  list_params=['modify_contents'],
                                  json_params=["zone_users"],
                                  filter_params=[]):
            return None

        return self.builder.create_user_module_custom(**directive)

    def modify_user_module_custom_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "module_customs","custom_name"],
                                  str_params=["zone","module_customs","custom_name","description"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.modify_user_module_custom_attributes(**directive)

    def modify_user_module_custom_configs(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "module_customs","modify_contents"],
                                  str_params=["zone","module_customs"],
                                  integer_params=[],
                                  list_params=['modify_contents'],
                                  filter_params=[]):
            return None

        return self.builder.modify_user_module_custom_configs(**directive)

    def modify_user_module_custom_zone_user(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "module_customs","zone_users"],
                                  str_params=["zone","module_customs"],
                                  integer_params=[],
                                  list_params=[],
                                  json_params=["zone_users"],
                                  filter_params=[]):
            return None

        return self.builder.modify_user_module_custom_zone_user(**directive)

    def delete_user_module_customs(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "module_customs"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['module_customs'],
                                  filter_params=[]):
            return None

        return self.builder.delete_user_module_customs(**directive)

    def describe_system_module_types(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone",'search_word','sort_key','item_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and",'enable_module'],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.describe_system_module_types(**directive)

