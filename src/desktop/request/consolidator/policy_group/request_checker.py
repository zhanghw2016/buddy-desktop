
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
from constants import (
    POLICY_GROUP_TYPES
)
from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import PolicyGroupRequestBuilder

class PolicyGroupRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(PolicyGroupRequestChecker, self).__init__(sender, checker)
        self.builder = PolicyGroupRequestBuilder(sender)

        self.handler_map = {
            ACTION_VDI_DESCRIBE_POLICY_GROUPS: self.describe_policy_groups,
            ACTION_VDI_CREATE_POLICY_GROUP: self.create_policy_group,
            ACTION_VDI_MODIFY_POLICY_GROUP_ATTRIBUTES: self.modify_policy_group_attributes,
            ACTION_VDI_DELETE_POLICY_GROUPS: self.delete_policy_groups,
            ACTION_VDI_ADD_RESOURCE_TO_POLICY_GROUP: self.add_resource_to_policy_group,
            ACTION_VDI_REMOVE_RESOURCE_FROM_POLICY_GROUP: self.remove_resource_from_policy_group,
            ACTION_VDI_ADD_POLICY_TO_POLICY_GROUP: self.add_policy_to_policy_group,
            ACTION_VDI_REMOVE_POLICY_FROM_POLICY_GROUP: self.remove_policy_from_policy_group,
            ACTION_VDI_APPLY_POLICY_GROUP: self.apply_policy_group,
            ACTION_VDI_MODIFY_RESOURCE_GROUP_POLICY: self.modify_resource_group_policy,
            }
    
    def _check_policy_group_type(self, policy_group_types):
        
        if not isinstance(policy_group_types, list):
            policy_group_types = [policy_group_types]
        
        for policy_group_type in policy_group_types:
            if policy_group_type not in POLICY_GROUP_TYPES:
                logger.error("unsupported policy group Type" % policy_group_type)
                self.set_error(ErrorMsg.ERR_MSG_UNSUPPORTED_POLICY_GROUP_TYPE, (policy_group_type, POLICY_GROUP_TYPES))
                return False

        return True
    
    def describe_policy_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse", "is_default", "ignore_zone"],
                                  list_params=["policy_groups", "policy_group_type"]
                                  ):
            return None

        if directive.get("policy_group_type") and not self._check_policy_group_type(directive["policy_group_type"]):
            return None

        return self.builder.describe_policy_groups(**directive)

    def create_policy_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "policy_group_type"],
                                  str_params=["zone", "policy_group_type", "policy_group_name", "description"],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return None
        
        if directive.get("policy_group_type") and not self._check_policy_group_type(directive["policy_group_type"]):
            return None

        return self.builder.create_policy_group(**directive)

    def modify_policy_group_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "policy_group"],
                                  str_params=["zone", "policy_group_name", "policy_group", "description"]):
            return None

        return self.builder.modify_policy_group_attributes(**directive)

    def delete_policy_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "policy_groups"],
                                  list_params=["policy_groups"]
                                  ):
            return None

        return self.builder.delete_policy_groups(**directive)

    def add_resource_to_policy_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "policy_group", "resources"],
                                  str_params=["zone", "policy_group"],
                                  list_params=["resources"]
                                  ):
            return None
    
        return self.builder.add_resource_to_policy_group(**directive)


    def remove_resource_from_policy_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "resources"],
                                  str_params=["zone"],
                                  list_params=["resources"]
                                  ):
            return None
    
        return self.builder.remove_resource_from_policy_group(**directive)


    def add_policy_to_policy_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "policy_groups", "policys"],
                                  str_params=["zone"],
                                  list_params=["policys", "policy_groups"]
                                  ):
            return None
    
        return self.builder.add_policy_to_policy_group(**directive)


    def remove_policy_from_policy_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "policy_groups", "policys"],
                                  str_params=["zone"],
                                  list_params=["policys", "policy_groups"]
                                  ):
            return None
    
        return self.builder.remove_policy_from_policy_group(**directive)

    def apply_policy_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "policy_group"],
                                  str_params=["zone", "policy_group"],
                                  list_params=[]
                                  ):
            return None
    
        return self.builder.apply_policy_group(**directive)

    def modify_resource_group_policy(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone", "resource_group", "policy_group"],
                                  str_params=["zone", "resource_group"],
                                  list_params=["policy_group"]
                                  ):
            return None
    
        return self.builder.modify_resource_group_policy(**directive)
