
from constants import (
    ACTION_VDI_DESCRIBE_POLICY_GROUPS,
    ACTION_VDI_CREATE_POLICY_GROUP,
    ACTION_VDI_MODIFY_POLICY_GROUP_ATTRIBUTES,
    ACTION_VDI_DELETE_POLICY_GROUPS,
    ACTION_VDI_ADD_RESOURCE_TO_POLICY_GROUP,
    ACTION_VDI_REMOVE_RESOURCE_FROM_POLICY_GROUP,
    ACTION_VDI_ADD_POLICY_TO_POLICY_GROUP,
    ACTION_VDI_REMOVE_POLICY_FROM_POLICY_GROUP,
    ACTION_VDI_APPLY_POLICY_GROUP,
    ACTION_VDI_MODIFY_RESOURCE_GROUP_POLICY,
)

from request.consolidator.base.base_request_builder import BaseRequestBuilder

class PolicyGroupRequestBuilder(BaseRequestBuilder):
    ''' API request builder '''

    def describe_policy_groups(self, 
                                 zone,
                                 policy_groups = None,
                                 policy_group_type = None,
                                 is_default=None,
                                 reverse = None,
                                 sort_key = None,
                                 offset = 0,
                                 limit = 20,
                                 search_word = None,
                                 verbose = 0,
                                 ignore_zone=None,
                                 **params
                                 ):

        action = ACTION_VDI_DESCRIBE_POLICY_GROUPS
        body = {"zone": zone}
        
        if policy_groups:
            body["policy_groups"] = policy_groups
        
        if policy_group_type:
            body["policy_group_type"] = policy_group_type
        
        if reverse:
            body["reverse"] = reverse
        
        if sort_key:
            body["sort_key"] = sort_key
        
        if offset is not None:
            body["offset"] = offset

        if limit:
            body["limit"] = limit
        if is_default is not None:
            body["is_default"] = is_default
        if search_word:
            body["search_word"] = search_word
        
        if verbose is not None:
            body["verbose"] = verbose
        
        if ignore_zone is not None:
            body["ignore_zone"] = ignore_zone
         
        return self._build_params(action, body)

    def create_policy_group(self,
                              zone,
                              policy_group_type,
                              policy_group_name=None,
                              description = None,
                              **params
                              ):

        action = ACTION_VDI_CREATE_POLICY_GROUP
        body = {"zone": zone, "policy_group_type": policy_group_type}
        if policy_group_name:
            body["policy_group_name"] = policy_group_name
        
        if description:
            body["description"] = description

        return self._build_params(action, body)
    
    def modify_policy_group_attributes(self, 
                                       zone,
                                       policy_group,
                                       policy_group_name=None,
                                       description=None,
                                       **params
                                       ):

        action = ACTION_VDI_MODIFY_POLICY_GROUP_ATTRIBUTES
        body = {"zone": zone, "policy_group": policy_group}
        
        if description is not None:
            body["description"] = description

        if policy_group_name is not None:
            body["policy_group_name"] = policy_group_name
         
        return self._build_params(action, body)
    
    def delete_policy_groups(self, zone,
                            policy_groups,
                            **params
                            ):

        action = ACTION_VDI_DELETE_POLICY_GROUPS
        body = {"zone": zone, "policy_groups": policy_groups}
        
        return self._build_params(action, body)

    def add_resource_to_policy_group(self, zone,
                                 policy_group,
                                 resources,
                                 **params
                                 ):

        action = ACTION_VDI_ADD_RESOURCE_TO_POLICY_GROUP
        body = {}
        body["zone"] = zone
    
        body["policy_group"] = policy_group
        body["resources"] = resources

        return self._build_params(action, body) 

    def remove_resource_from_policy_group(self, zone,
                                 resources,
                                 **params
                                 ):

        action = ACTION_VDI_REMOVE_RESOURCE_FROM_POLICY_GROUP
        body = {}
        body["zone"] = zone
        body["resources"] = resources

        return self._build_params(action, body) 

    def add_policy_to_policy_group(self, zone,
                                 policy_groups,
                                 policys,
                                 **params
                                 ):

        action = ACTION_VDI_ADD_POLICY_TO_POLICY_GROUP
        body = {}
        body["zone"] = zone
        body["policy_groups"] = policy_groups
        body["policys"] = policys

        return self._build_params(action, body) 

    def remove_policy_from_policy_group(self, zone,
                                 policy_groups,
                                 policys,
                                 **params
                                 ):

        action = ACTION_VDI_REMOVE_POLICY_FROM_POLICY_GROUP
        body = {}
        body["zone"] = zone
        body["policy_groups"] = policy_groups
        body["policys"] = policys

        return self._build_params(action, body) 

    def apply_policy_group(self, zone,
                                 policy_group,
                                 **params
                                 ):

        action = ACTION_VDI_APPLY_POLICY_GROUP
        body = {}
        body["zone"] = zone
        body["policy_group"] = policy_group

        return self._build_params(action, body)
    
    def modify_resource_group_policy(self, zone,
                                           resource_group,
                                           policy_group,
                                           **params
                                           ):

        action = ACTION_VDI_MODIFY_RESOURCE_GROUP_POLICY
        body = {}
        body["zone"] = zone
        body["resource_group"] = resource_group
        body["policy_group"] = policy_group

        return self._build_params(action, body)
