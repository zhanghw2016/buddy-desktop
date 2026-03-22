
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
from request.consolidator.base.base_request_builder import BaseRequestBuilder

class SecurityPolicyRequestBuilder(BaseRequestBuilder):

    def describe_desktop_security_policys(self, 
                                         zone,
                                         security_policys = None,
                                         security_policy_type = None,
                                         policy_group = None,
                                         reverse = None,
                                         sort_key = None,
                                         offset = 0,
                                         limit = 20,
                                         search_word = None,
                                         verbose = 0,
                                         **params
                                         ):

        action = ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_POLICYS
        body = {"zone": zone}
        
        if security_policys:
            body["security_policys"] = security_policys
        if policy_group:
            body["policy_group"] = policy_group
        
        if security_policy_type:
            body["security_policy_type"] = security_policy_type
        
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

    def create_desktop_security_policy(self,
                                      zone,
                                      security_policy_name,
                                      security_policy_type=None,
                                      description=None,
                                      **params
                                      ):

        action = ACTION_VDI_CREATE_DESKTOP_SECURITY_POLICY
        body = {"zone": zone}
        body["security_policy_name"] = security_policy_name
        
        if security_policy_type:
            body["security_policy_type"] = security_policy_type
        
        if description:
            body["description"] = description
        
        return self._build_params(action, body)
    
    def modify_desktop_security_policy_attributes(self,
                                                  zone,
                                                  security_policy,
                                                  security_policy_name=None,
                                                  description=None,
                                                  **params):

        action = ACTION_VDI_MODIFY_DESKTOP_SECURITY_POLICY_ATTRIBUTES
        body = {
            "zone": zone,
            "security_policy": security_policy
            }

        if security_policy_name is not None:
            body["security_policy_name"] = security_policy_name
        if description is not None:
            body["description"] = description
        
        return self._build_params(action, body)
    
    def delete_desktop_security_policys(self,
                                        zone,
                                        security_policys,
                                        **params
                                        ):

        action = ACTION_VDI_DELETE_DESKTOP_SECURITY_POLICYS
        body = {"zone": zone}
        
        body["security_policys"] = security_policys

        return self._build_params(action, body)

    def apply_desktop_security_policy(self,
                                 zone,
                                 security_policy,
                                 **params
                                 ):

        action = ACTION_VDI_APPLY_DESKTOP_SECURITY_POLICY
        body = {"zone": zone}
        body["security_policy"] = security_policy

        return self._build_params(action, body)

    def describe_desktop_security_rules(self, 
                                         zone,
                                         security_policy = None,
                                         security_rules = None,
                                         direction = None,
                                         rule_action = None,
                                         reverse = None,
                                         sort_key = None,
                                         offset = 0,
                                         limit = 20,
                                         search_word = None,
                                         verbose = 0,
                                         **params
                                         ):

        action = ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_RULES
        body = {"zone": zone}
        
        if security_policy:
            body["security_policy"] = security_policy
        
        if security_rules:
            body["security_rules"] = security_rules
        
        if direction is not None:
            body["direction"] = direction
        
        if rule_action:
            body["rule_action"] = rule_action
        
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

    def add_desktop_security_rules(self,
                                      zone,
                                      security_policy,
                                      rules, 
                                      **params
                                      ):

        action = ACTION_VDI_ADD_DESKTOP_SECURITY_RULES
        body = {"zone": zone}
        
        body["security_policy"] = security_policy
        body["rules"] = rules

        return self._build_params(action, body)

    def modify_desktop_security_rule_attributes(self,
                                       zone,
                                       security_rule,
                                       priority=None, 
                                       security_rule_name=None,
                                       protocol=None, 
                                       rule_action=None, 
                                       direction=None,
                                       val1=None, 
                                       val2=None, 
                                       val3=None,
                                       disabled=None,
                                       **params
                                       ):

        action = ACTION_VDI_MODIFY_DESKTOP_SECURITY_RULE_ATTRIBUTES
        body = {"zone": zone}
        body["security_rule"] = security_rule
        
        if priority is not None:
            body['priority'] = priority
        if security_rule_name:
            body['security_rule_name'] = security_rule_name
        if protocol:
            body['protocol'] = protocol
        if rule_action:
            body['rule_action'] = rule_action
        if direction is not None:
            body['direction'] = direction
        if val1 is not None:
            body['val1'] = val1
        if val2 is not None:
            body['val2'] = val2
        if val3 is not None:
            body['val3'] = val3
        if disabled is not None:
            body["disabled"] = 1 if disabled else 0

        return self._build_params(action, body)
    
    def remove_desktop_security_rules(self,
                                        zone,
                                        security_policy,
                                        security_rules,
                                        **params
                                        ):

        action = ACTION_VDI_REMOVE_DESKTOP_SECURITY_RULES
        body = {"zone": zone}
        body["security_rules"] = security_rules
        body["security_policy"] = security_policy
        return self._build_params(action, body)

    def describe_desktop_security_ipsets(self, 
                                         zone,
                                         security_ipsets = None,
                                         ipset_type=None,
                                         reverse = None,
                                         sort_key = None,
                                         offset = 0,
                                         limit = 20,
                                         search_word = None,
                                         verbose = 0,
                                         **params
                                         ):

        action = ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_IPSETS
        body = {"zone": zone}
        
        if security_ipsets:
            body["security_ipsets"] = security_ipsets
        
        if ipset_type:
            body["ipset_type"] = ipset_type
        
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

    def create_desktop_security_ipset(self,
                                      zone,
                                      ipset_type, 
                                      val, 
                                      security_ipset_name=None,
                                      **params
                                      ):

        action = ACTION_VDI_CREATE_DESKTOP_SECURITY_IPSET
        body = {"zone": zone}
        body["ipset_type"] = ipset_type
        body["val"] = val
        
        if security_ipset_name:
            body["security_ipset_name"] = security_ipset_name
         
        return self._build_params(action, body)
    
    def modify_desktop_security_ipset_attributes(self,
                                       zone,
                                       security_ipset,
                                       security_ipset_name=None,
                                       description=None,
                                       val=None,
                                       **params
                                       ):

        action = ACTION_VDI_MODIFY_DESKTOP_SECURITY_IPSET_ATTRIBUTES
        body = {"zone": zone}
        body["security_ipset"] = security_ipset

        if security_ipset_name:
            body["security_ipset_name"] = security_ipset_name
        
        if description:
            body["description"] = description
        
        if val:
            body["val"] = val
         
        return self._build_params(action, body)
    
    def delete_desktop_security_ipsets(self,
                                        zone,
                                        security_ipsets,
                                        **params
                                        ):

        action = ACTION_VDI_DELETE_DESKTOP_SECURITY_IPSETS
        body = {"zone": zone}
        body["security_ipsets"] = security_ipsets

        return self._build_params(action, body)

    def apply_desktop_security_ipset(self,
                                 zone,
                                 security_ipset,
                                 **params
                                 ):

        action = ACTION_VDI_APPLY_DESKTOP_SECURITY_IPSET
        body = {"zone": zone}
        body["security_ipset"] = security_ipset

        return self._build_params(action, body)

    def describe_system_security_policys(self,
                                        zone,
                                        security_policys=None,
                                        **params
                                        ):

        action = ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_POLICYS

        body = {"zone": zone}
        if security_policys:
            body["security_policys"] = security_policys

        return self._build_params(action, body)

    def describe_system_security_ipsets(self,
                                        zone,
                                        security_ipsets=None,
                                        **params
                                        ):

        action = ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_IPSETS
        body = {"zone": zone}
        if security_ipsets:
            body["security_ipsets"] = security_ipsets

        return self._build_params(action, body)

    def load_system_security_rules(self,
                                        zone,
                                        security_policy,
                                        security_rules,
                                        **params
                                        ):

        action = ACTION_VDI_LOAD_SYSTEM_SECURITY_RULES
        body = {"zone": zone}
        body["security_policy"] = security_policy
        body["security_rules"] = security_rules

        return self._build_params(action, body)

    def load_system_security_ipsets(self,
                                        zone,
                                        security_ipsets,
                                        **params
                                        ):

        action = ACTION_VDI_LOAD_SYSTEM_SECURITY_IPSETS
        body = {"zone": zone}
        body["security_ipsets"] = security_ipsets

        return self._build_params(action, body)
