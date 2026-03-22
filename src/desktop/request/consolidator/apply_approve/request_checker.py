
from constants import (

    # apply group
    ACTION_VDI_CREATE_RESOURCE_APPLY_GROUP,
    ACTION_VDI_MODIFY_RESOURCE_APPLY_GROUP,
    ACTION_VDI_DESCRIBE_RESOURCE_APPLY_GROUPS,
    ACTION_VDI_DELETE_RESOURCE_APPLY_GROUPS,
    ACTION_VDI_INSERT_USER_TO_APPLY_GROUP,
    ACTION_VDI_REMOVE_USER_FROM_APPLY_GROUP,
    ACTION_VDI_INSERT_RESOURCE_TO_APPLY_GROUP,
    ACTION_VDI_REMOVE_RESOURCE_FROM_APPLY_GROUP,

    # approve group
    ACTION_VDI_CREATE_RESOURCE_APPROVE_GROUP,
    ACTION_VDI_MODIFY_RESOURCE_APPROVE_GROUP,
    ACTION_VDI_DESCRIBE_RESOURCE_APPROVE_GROUPS,
    ACTION_VDI_DELETE_RESOURCE_APPROVE_GROUPS,
    ACTION_VDI_INSERT_USER_TO_APPROVE_GROUP,
    ACTION_VDI_REMOVE_USER_FROM_APPROVE_GROUP,
    ACTION_VDI_MAP_APPLY_GROUP_AND_APPROVE_GROUP,
    ACTION_VDI_UNMAP_APPLY_GROUP_AND_APPROVE_GROUP,

    # apply form
    ACTION_VDI_CREATE_DESKTOP_APPLY_FORM,
    ACTION_VDI_DESCRIBE_DESKTOP_APPLY_FORMS,
    ACTION_VDI_MODIFY_DESKTOP_APPLY_FORM,
    ACTION_VDI_DELETE_DESKTOP_APPLY_FORMS,
    ACTION_VDI_DEAL_DESKTOP_APPLY_FORM,
    ACTION_VDI_GET_APPROVE_USERS,

)

from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import ApplyApproveRequestBuilder
import constants as const

class ApplyApproveRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(ApplyApproveRequestChecker, self).__init__(sender, checker)
        self.builder = ApplyApproveRequestBuilder(sender)

        self.handler_map = {
                    # apply group
                    ACTION_VDI_CREATE_RESOURCE_APPLY_GROUP: self.create_resource_apply_group,
                    ACTION_VDI_MODIFY_RESOURCE_APPLY_GROUP: self.modify_resource_apply_group,
                    ACTION_VDI_DESCRIBE_RESOURCE_APPLY_GROUPS: self.describe_resource_apply_groups,
                    ACTION_VDI_DELETE_RESOURCE_APPLY_GROUPS: self.delete_resource_apply_groups,
                    ACTION_VDI_INSERT_USER_TO_APPLY_GROUP: self.insert_user_to_apply_group,
                    ACTION_VDI_REMOVE_USER_FROM_APPLY_GROUP: self.remove_user_from_apply_group,
                    ACTION_VDI_INSERT_RESOURCE_TO_APPLY_GROUP: self.insert_resource_to_apply_group,
                    ACTION_VDI_REMOVE_RESOURCE_FROM_APPLY_GROUP: self.remove_resource_from_apply_group,

                    # approve group
                    ACTION_VDI_CREATE_RESOURCE_APPROVE_GROUP: self.create_resource_approve_group,
                    ACTION_VDI_MODIFY_RESOURCE_APPROVE_GROUP: self.modify_resource_approve_group,
                    ACTION_VDI_DESCRIBE_RESOURCE_APPROVE_GROUPS: self.describe_resource_approve_groups,
                    ACTION_VDI_DELETE_RESOURCE_APPROVE_GROUPS: self.delete_resource_approve_groups,
                    ACTION_VDI_INSERT_USER_TO_APPROVE_GROUP: self.insert_user_to_approve_group,
                    ACTION_VDI_REMOVE_USER_FROM_APPROVE_GROUP: self.remove_user_from_approve_group,
                    ACTION_VDI_MAP_APPLY_GROUP_AND_APPROVE_GROUP: self.map_apply_group_and_approve_group,
                    ACTION_VDI_UNMAP_APPLY_GROUP_AND_APPROVE_GROUP: self.unmap_apply_group_and_approve_group,

                    # apply form
                    ACTION_VDI_CREATE_DESKTOP_APPLY_FORM: self.create_desktop_apply_form,
                    ACTION_VDI_DESCRIBE_DESKTOP_APPLY_FORMS: self.describe_desktop_apply_form,
                    ACTION_VDI_MODIFY_DESKTOP_APPLY_FORM: self.modify_desktop_apply_form,
                    ACTION_VDI_DELETE_DESKTOP_APPLY_FORMS: self.delete_desktop_apply_form,
                    ACTION_VDI_DEAL_DESKTOP_APPLY_FORM: self.deal_desktop_apply_form,
                    ACTION_VDI_GET_APPROVE_USERS: self.get_approve_users,
        }

    def create_resource_apply_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "apply_group_name"],
                                  str_params=["zone", "apply_group_name", "description"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.create_resource_apply_group(**directive)

    def modify_resource_apply_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "apply_group_id","apply_group_name"],
                                  str_params=["zone","apply_group_id","apply_group_name","description"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.modify_resource_apply_group(**directive)

    def describe_resource_apply_groups(self, directive):
        '''
            @param directive : the dictionary of params
             '''
        if not self._check_params(directive,
                                  str_params=['zone','apply_group_name', 'sort_key','search_word'],
                                  list_params = ['apply_groups'],
                                  integer_params=['offset', 'limit', 'reverse', 'is_and']):
            return None

        return self.builder.describe_resource_apply_groups(**directive)

    def delete_resource_apply_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "apply_groups"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['apply_groups'],
                                  filter_params=[]):
            return None

        return self.builder.delete_resource_apply_groups(**directive)

    def insert_user_to_apply_group(self, directive):
        '''
            @param directive : the dictionary of params
             '''
        if not self._check_params(directive,
                                  required_params=['zone','apply_group_id', 'user_ids'],
                                  str_params=['zone','apply_group_id'],
                                  list_params = ['user_ids']):
            return None

        return self.builder.insert_user_to_apply_group(**directive)

    def remove_user_from_apply_group(self, directive):
        '''
            @param directive : the dictionary of params
             '''
        if not self._check_params(directive,
                                  required_params=['zone','apply_group_id','user_ids'],
                                  str_params=['zone','apply_group_id'],
                                  list_params = ['user_ids']):
            return None

        return self.builder.remove_user_from_apply_group(**directive)

    def insert_resource_to_apply_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone','apply_group_id'],
                                  str_params=['zone','apply_group_id'],
                                  list_params = ['resource_ids']):
            return None

        return self.builder.insert_resource_to_apply_group(**directive)

    def remove_resource_from_apply_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone','apply_group_id'],
                                  str_params=['zone','apply_group_id'],
                                  list_params=['resource_ids']):
            return None

        return self.builder.remove_resource_from_apply_group(**directive)

    def create_resource_approve_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone','approve_group_name'],
                                  str_params=['zone','approve_group_name','description']):
            return None

        return self.builder.create_resource_approve_group(**directive)

    def modify_resource_approve_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone','approve_group_id','approve_group_name'],
                                  str_params=['zone','approve_group_id','approve_group_name','description']):
            return None

        return self.builder.modify_resource_approve_group(**directive)

    def describe_resource_approve_groups(self, directive):
        '''
            @param directive : the dictionary of params
             '''
        if not self._check_params(directive,
                                  required_params=['zone'],
                                  str_params=['zone','approve_group_name', 'sort_key', 'search_word'],
                                  list_params = ['approve_groups'],
                                  integer_params=['offset', 'limit', 'reverse', 'is_and']):
            return None

        return self.builder.describe_resource_approve_groups(**directive)

    def delete_resource_approve_groups(self, directive):
        '''
            @param directive : the dictionary of params
             '''
        if not self._check_params(directive,
                                  required_params=['zone','approve_groups'],
                                  str_params=['zone'],
                                  list_params = ['approve_groups']):
            return None

        return self.builder.delete_resource_approve_groups(**directive)

    def insert_user_to_approve_group(self, directive):
        '''
            @param directive : the dictionary of params
             '''
        if not self._check_params(directive,
                                  required_params=['zone','approve_group_id', "user_ids"],
                                  str_params=['zone','approve_group_id'],
                                  list_params=['user_ids']):
            return None

        return self.builder.insert_user_to_approve_group(**directive)

    def remove_user_from_approve_group(self, directive):
        '''
            @param directive : the dictionary of params
             '''
        if not self._check_params(directive,
                                  required_params=['zone','approve_group_id','user_ids'],
                                  str_params=['zone','approve_group_id'],
                                  list_params = ['user_ids']):
            return None

        return self.builder.remove_user_from_approve_group(**directive)

    def map_apply_group_and_approve_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone','apply_group_id', 'approve_group_id'],
                                  str_params=['zone','apply_group_id', 'approve_group_id']):
            return None

        return self.builder.map_apply_group_and_approve_group(**directive)

    def unmap_apply_group_and_approve_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone','apply_group_id', 'approve_group_id'],
                                  str_params=['zone','apply_group_id', 'approve_group_id']):
            return None

        return self.builder.unmap_apply_group_and_approve_group(**directive)

    def create_desktop_apply_form(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone','apply_user_id', 'approve_user_id'],
                                  str_params=['zone','apply_type', 'apply_title', 'apply_description', 'apply_resource_type',
                                              'resource_group_id',
                                              'apply_user_id', 'approve_user_id'],
                                  integer_params=['apply_age'],
                                  time_params = ["start_time", "end_time"],
                                  json_params=['apply_parameter']):
            return None

        if 'apply_resource_type' in directive and directive['apply_resource_type'] not in const.APPLY_RESOURCE_TYPE_LIST:
            return None

        return self.builder.create_desktop_apply_form(**directive)

    def describe_desktop_apply_form(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone'],
                                  str_params=['zone','apply_title', 'apply_user_id', 'approve_user_id', 'apply_type',
                                              'apply_resource_type', 'resource_group_id', 'sort_key', 'search_word'],
                                  list_params=['applys', 'status', "create_time", "approve_status"],
                                  integer_params=['offset', 'limit', 'reverse', 'is_and']):
            return None

        return self.builder.describe_desktop_apply_form(**directive)

    def modify_desktop_apply_form(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone','apply_id'],
                                  str_params=['zone','apply_id', 'apply_title', 'apply_description', 'approve_user_id'],
                                  integer_params=['apply_age'],
                                  time_params = ["start_time", "end_time"],
                                  json_params=['apply_parameter']):
            return None

        return self.builder.modify_desktop_apply_form(**directive)

    def delete_desktop_apply_form(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone', 'applys'],
                                  str_params=['zone'],
                                  list_params=['applys']):
            return None

        return self.builder.delete_desktop_apply_form(**directive)

    def deal_desktop_apply_form(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone','apply_id', 'approve_user_id', 'result'],
                                  str_params=['zone','apply_id', 'approve_user_id', 'result', 'approve_advice'],
                                  integer_params=['apply_age'],
                                  time_params=['start_time', 'end_time'],
                                  json_params=['approve_parameter']):
            return None

        return self.builder.deal_desktop_apply_form(**directive)

    def get_approve_users(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['zone','apply_user_id', 'resource_group_id'],
                                  str_params=['zone','apply_user_id', 'resource_group_id']):
            return None

        return self.builder.get_approve_users(**directive)





