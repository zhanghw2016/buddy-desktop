
from constants import (

    ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_POLICYS,
    ACTION_VDI_CREATE_DESKTOP_SECURITY_POLICY,
    ACTION_VDI_MODIFY_DESKTOP_SECURITY_POLICY_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOP_SECURITY_POLICYS,
    ACTION_VDI_APPLY_DESKTOP_SECURITY_POLICY,
    
    ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_RULES,
    ACTION_VDI_ADD_DESKTOP_SECURITY_RULES,
    ACTION_VDI_REMOVE_DESKTOP_SECURITY_RULES,
    ACTION_VDI_MODIFY_DESKTOP_SECURITY_RULE_ATTRIBUTES,
    
    ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_IPSETS,
    ACTION_VDI_CREATE_DESKTOP_SECURITY_IPSET,
    ACTION_VDI_DELETE_DESKTOP_SECURITY_IPSETS,
    ACTION_VDI_MODIFY_DESKTOP_SECURITY_IPSET_ATTRIBUTES,
    ACTION_VDI_APPLY_DESKTOP_SECURITY_IPSET,

    ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_POLICYS,
    ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_IPSETS,
    ACTION_VDI_LOAD_SYSTEM_SECURITY_RULES,
    ACTION_VDI_LOAD_SYSTEM_SECURITY_IPSETS,

)

from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import SecurityPolicyRequestBuilder

class SecurityPolicyRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(SecurityPolicyRequestChecker, self).__init__(sender, checker)
        self.builder = SecurityPolicyRequestBuilder(sender)

        self.handler_map = {
                            ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_POLICYS: self.describe_desktop_security_policys,
                            ACTION_VDI_CREATE_DESKTOP_SECURITY_POLICY: self.create_desktop_security_policy,
                            ACTION_VDI_MODIFY_DESKTOP_SECURITY_POLICY_ATTRIBUTES: self.modify_desktop_security_policy_attributes,
                            ACTION_VDI_DELETE_DESKTOP_SECURITY_POLICYS: self.delete_desktop_security_policys,
                            ACTION_VDI_APPLY_DESKTOP_SECURITY_POLICY: self.apply_desktop_security_policy,

                            ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_RULES:self.describe_desktop_security_rules,
                            ACTION_VDI_ADD_DESKTOP_SECURITY_RULES: self.add_desktop_security_rules,
                            ACTION_VDI_REMOVE_DESKTOP_SECURITY_RULES: self.remove_desktop_security_rules,
                            ACTION_VDI_MODIFY_DESKTOP_SECURITY_RULE_ATTRIBUTES: self.modify_desktop_security_rule_attributes,

                            ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_IPSETS: self.describe_desktop_security_ipsets,
                            ACTION_VDI_CREATE_DESKTOP_SECURITY_IPSET: self.create_desktop_security_ipset,
                            ACTION_VDI_DELETE_DESKTOP_SECURITY_IPSETS: self.delete_desktop_security_ipsets,
                            ACTION_VDI_MODIFY_DESKTOP_SECURITY_IPSET_ATTRIBUTES: self.modify_desktop_security_ipset_attributes,
                            ACTION_VDI_APPLY_DESKTOP_SECURITY_IPSET: self.apply_desktop_security_ipset,

                            ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_POLICYS: self.describe_system_security_policys,
                            ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_IPSETS: self.describe_system_security_ipsets,
                            ACTION_VDI_LOAD_SYSTEM_SECURITY_RULES: self.load_system_security_rules,
                            ACTION_VDI_LOAD_SYSTEM_SECURITY_IPSETS: self.load_system_security_ipsets,

            }

    def describe_desktop_security_policys(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["security_policys", "policy_mode", "security_policy_type"]
                                  ):
            return None
        
        return self.builder.describe_desktop_security_policys(**directive)

    def create_desktop_security_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "security_policy_name"],
                                  str_params=["zone", "description", "security_policy_type"],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return None

        return self.builder.create_desktop_security_policy(**directive)

    def modify_desktop_security_policy_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "security_policy"],
                                  str_params=["zone", "security_policy", "security_policy_name", "description"]):
            return None

        return self.builder.modify_desktop_security_policy_attributes(**directive)

    def delete_desktop_security_policys(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "security_policys"]
                                  ):
            return None

        return self.builder.delete_desktop_security_policys(**directive)

    def apply_desktop_security_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "security_policy"],
                                  list_params=[]
                                  ):
            return None
    
        return self.builder.apply_desktop_security_policy(**directive)

    def describe_desktop_security_rules(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "search_word", "sort_key", "security_policy"],
                                  integer_params=["limit", "offset", "verbose", "reverse", "direction", "rule_action"],
                                  list_params=["security_rules"]
                                  ):
            return None
        
        return self.builder.describe_desktop_security_rules(**directive)

    def add_desktop_security_rules(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "security_policy", "rules"],
                                  str_params=["zone", "security_policy"],
                                  integer_params=[],
                                  list_params=[],
                                  list_dict_params=["rules"]
                                  ):
            return None

        return self.builder.add_desktop_security_rules(**directive)

    def modify_desktop_security_rule_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["security_rule", "zone"],
                                  str_params=["zone", "security_rule", "security_rule_name",
                                              "protocol", "rule_action","val1", "val2", "val3"],
                                  integer_params=["priority", "direction", "disabled"],
                                  list_params=[]):
            return None

        return self.builder.modify_desktop_security_rule_attributes(**directive)

    def remove_desktop_security_rules(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "security_rules", "security_policy"],
                                  list_params=["security_rules"]
                                  ):
            return None

        return self.builder.remove_desktop_security_rules(**directive)

    def describe_desktop_security_ipsets(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["ipset_type", "security_ipsets"]
                                  ):
            return None
        
        return self.builder.describe_desktop_security_ipsets(**directive)

    def create_desktop_security_ipset(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "ipset_type", "val"],
                                  integer_params=["ipset_type"],
                                  str_params=["zone", "security_ipset_name"],
                                  list_params=[]):
            return None

        return self.builder.create_desktop_security_ipset(**directive)

    def modify_desktop_security_ipset_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["security_ipset", "zone"],
                                  str_params=["zone", "security_ipset", "security_ipset_name", "description"],
                                  list_params=[]):
            return None

        return self.builder.modify_desktop_security_ipset_attributes(**directive)

    def delete_desktop_security_ipsets(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "security_ipsets"],
                                  list_params=["security_ipsets"]
                                  ):
            return None

        return self.builder.delete_desktop_security_ipsets(**directive)

    def apply_desktop_security_ipset(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "security_ipset"],
                                  list_params=[]
                                  ):
            return None
    
        return self.builder.apply_desktop_security_ipset(**directive)

    def describe_system_security_policys(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=[],
                                  list_params=["security_policys"]):
            return None

        return self.builder.describe_system_security_policys(**directive)

    def describe_system_security_ipsets(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=[],
                                  list_params=["security_ipsets"]):
            return None

        return self.builder.describe_system_security_ipsets(**directive)

    def load_system_security_rules(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "security_rules", "security_policy"],
                                  str_params=[],
                                  list_params=["security_rules"]):
            return None

        return self.builder.load_system_security_rules(**directive)

    def load_system_security_ipsets(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "security_ipsets"],
                                  str_params=[],
                                  list_params=["security_ipsets"]):
            return None

        return self.builder.load_system_security_ipsets(**directive)
