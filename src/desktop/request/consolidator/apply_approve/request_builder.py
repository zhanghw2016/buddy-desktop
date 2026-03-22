
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
from request.consolidator.base.base_request_builder import BaseRequestBuilder

class ApplyApproveRequestBuilder(BaseRequestBuilder):

    def create_resource_apply_group(self,
                                   zone,
                                   apply_group_name,
                                   description=None,
                                   **params):
        action = ACTION_VDI_CREATE_RESOURCE_APPLY_GROUP
        body = {}
        body["zone"] = zone
        body["apply_group_name"] = apply_group_name
        if description:
            body["description"] = description
        return self._build_params(action, body)

    def modify_resource_apply_group(self,
                                   zone,
                                   apply_group_id,
                                   apply_group_name=None,
                                   description='',
                                   **params):
        action = ACTION_VDI_MODIFY_RESOURCE_APPLY_GROUP
        body = {}
        body["zone"] = zone
        body["apply_group_id"] = apply_group_id
        if apply_group_name is not None:
            body['apply_group_name'] = apply_group_name
        if description is not None:
            body['description'] = description
        return self._build_params(action, body)

    def describe_resource_apply_groups(self,
                                       zone,
                                       apply_groups=[],
                                       apply_group_name='',
                                       columns=[],
                                       sort_key='',
                                       search_word=None,
                                       offset=-1,
                                       limit=-1,
                                       reverse=0,
                                       is_and=1,
                                       check_resource_group=None,
                                       **params):
        action = ACTION_VDI_DESCRIBE_RESOURCE_APPLY_GROUPS
        body = {}
        body["zone"] = zone
        if apply_groups:
            body['apply_group_ids'] = apply_groups
        if apply_group_name:
            body['apply_group_name'] = apply_group_name
        if columns:
            body['columns'] = columns
        if sort_key:
            body['sort_key'] = sort_key
        if search_word:
            body['search_word'] = search_word
        if reverse == 1:
            body['reverse'] = 1
        else:
            body['reverse'] = 0
        if offset >= 0:
            body['offset'] = offset
        if limit >= 0:
            body['limit'] = limit
        if is_and == 0:
            body['is_and'] = 0
        else:
            body['is_and'] = 1
            
        if check_resource_group is not None:
            body["check_resource_group"] = check_resource_group
            
        return self._build_params(action, body)

    def delete_resource_apply_groups(self,
                                     zone,
                                     apply_groups,
                                     **params):
        action = ACTION_VDI_DELETE_RESOURCE_APPLY_GROUPS
        body = {}
        body["zone"] = zone
        body['apply_group_ids'] = apply_groups

        return self._build_params(action, body)

    def insert_user_to_apply_group(self,
                                   zone,
                                   apply_group_id,
                                   user_ids,
                                     **params):
        action = ACTION_VDI_INSERT_USER_TO_APPLY_GROUP
        body = {}
        body["zone"] = zone
        body['apply_group_id'] = apply_group_id
        body['user_ids'] = user_ids

        return self._build_params(action, body)

    def remove_user_from_apply_group(self,
                                   zone,
                                   apply_group_id,
                                   user_ids,
                                     **params):
        action = ACTION_VDI_REMOVE_USER_FROM_APPLY_GROUP
        body = {}
        body["zone"] = zone
        body['apply_group_id'] = apply_group_id
        body['user_ids'] = user_ids

        return self._build_params(action, body)

    def insert_resource_to_apply_group(self,
                                   zone,
                                   apply_group_id,
                                   resource_ids,
                                     **params):
        action = ACTION_VDI_INSERT_RESOURCE_TO_APPLY_GROUP
        body = {}
        body["zone"] = zone
        body['apply_group_id'] = apply_group_id
        body['resource_ids'] = resource_ids

        return self._build_params(action, body)

    def remove_resource_from_apply_group(self,
                                   zone,
                                   apply_group_id,
                                   resource_ids,
                                     **params):
        action = ACTION_VDI_REMOVE_RESOURCE_FROM_APPLY_GROUP
        body = {}
        body["zone"] = zone
        body['apply_group_id'] = apply_group_id
        body['resource_ids'] = resource_ids

        return self._build_params(action, body)

    def create_resource_approve_group(self,
                                   zone,
                                   approve_group_name,
                                   description='',
                                   **params):
        action = ACTION_VDI_CREATE_RESOURCE_APPROVE_GROUP
        body = {}
        body["zone"] = zone
        body['approve_group_name'] = approve_group_name
        if description:
            body['description'] = description
        return self._build_params(action, body)

    def modify_resource_approve_group(self,
                                   zone,
                                   approve_group_id,
                                   approve_group_name,
                                   description=None,
                                   **params):
        action = ACTION_VDI_MODIFY_RESOURCE_APPROVE_GROUP
        body = {}
        body["zone"] = zone
        body['approve_group_id'] = approve_group_id
        body['approve_group_name'] = approve_group_name
        if description is not None:
            body['description'] = description
        return self._build_params(action, body)

    def describe_resource_approve_groups(self,
                                    zone,
                                    approve_groups=[],
                                    approve_group_name='',
                                    columns=[],
                                    sort_key='',
                                    search_word=None,
                                    offset=-1,
                                    limit=-1,
                                    reverse=0,
                                    is_and=1,
                                    **params):
        action = ACTION_VDI_DESCRIBE_RESOURCE_APPROVE_GROUPS
        body = {}
        body["zone"] = zone
        if approve_groups:
            body['approve_group_ids'] = approve_groups
        if approve_group_name:
            body['approve_group_name'] = approve_group_name
        if columns:
            body['columns'] = columns
        if sort_key:
            body['sort_key'] = sort_key
        if search_word:
            body['search_word'] = search_word
        if reverse == 1:
            body['reverse'] = 1
        else:
            body['reverse'] = 0
        if offset >= 0:
            body['offset'] = offset
        if limit >= 0:
            body['limit'] = limit
        if is_and == 0:
            body['is_and'] = 0
        else:
            body['is_and'] = 1
        return self._build_params(action, body)

    def delete_resource_approve_groups(self,
                                       zone,
                                       approve_groups,
                                       **params):
        action = ACTION_VDI_DELETE_RESOURCE_APPROVE_GROUPS
        body = {}
        body["zone"] = zone
        body['approve_group_ids'] = approve_groups
        return self._build_params(action, body)

    def insert_user_to_approve_group(self,
                                   zone,
                                   approve_group_id,
                                   user_ids,
                                   **params):
        action = ACTION_VDI_INSERT_USER_TO_APPROVE_GROUP
        body = {}
        body["zone"] = zone
        body['approve_group_id'] = approve_group_id
        body['user_ids'] = user_ids

        return self._build_params(action, body)

    def remove_user_from_approve_group(self,
                                     zone,
                                     approve_group_id,
                                     user_ids,
                                     **params):
        action = ACTION_VDI_REMOVE_USER_FROM_APPROVE_GROUP
        body = {}
        body["zone"] = zone
        body['approve_group_id'] = approve_group_id
        body['user_ids'] = user_ids

        return self._build_params(action, body)

    def map_apply_group_and_approve_group(self,
                                          zone,
                                          apply_group_id,
                                          approve_group_id,
                                          **params):
        action = ACTION_VDI_MAP_APPLY_GROUP_AND_APPROVE_GROUP
        body = {}
        body["zone"] = zone
        body['apply_group_id'] = apply_group_id
        body['approve_group_id'] = approve_group_id

        return self._build_params(action, body)

    def unmap_apply_group_and_approve_group(self,
                                          zone,
                                          apply_group_id,
                                          approve_group_id,
                                          **params):
        action = ACTION_VDI_UNMAP_APPLY_GROUP_AND_APPROVE_GROUP
        body = {}
        body["zone"] = zone
        body['apply_group_id'] = apply_group_id
        body['approve_group_id'] = approve_group_id

        return self._build_params(action, body)

    def create_desktop_apply_form(self,
                                  zone,
                                  apply_user_id,
                                  approve_user_id,
                                  approve_group_id,
                                  start_time,
                                  end_time,
                                  apply_type=None,
                                  apply_title=None,
                                  apply_resource_type=None,
                                  apply_parameter=None,
                                  apply_description=None,
                                  resource_group_id=None,
                                  resource_id = None,
                                  apply_age=None,
                                  **params):
        action = ACTION_VDI_CREATE_DESKTOP_APPLY_FORM
        body = {}
        body["zone"] = zone
        body['apply_user_id'] = apply_user_id
        body['approve_user_id'] = approve_user_id
        
        body["start_time"] = start_time
        body["end_time"] = end_time
        body["approve_group_id"] = approve_group_id
        if apply_type:
            body['apply_type'] = apply_type
        if apply_title:
            body['apply_title'] = apply_title
        if apply_resource_type:
            body['apply_resource_type'] = apply_resource_type
        if apply_parameter:
            body['apply_parameter'] = apply_parameter
        if apply_description is not None:
            body['apply_description'] = apply_description
        if resource_group_id:
            body['resource_group_id'] = resource_group_id
        if resource_id:
            body["resource_id"] = resource_id

        if apply_age is not None:
            body['apply_age'] = apply_age

        return self._build_params(action, body)

    def describe_desktop_apply_form(self,
                                    zone,
                                    applys=None,
                                    apply_type=None,
                                    apply_title=None,
                                    apply_user_id=None,
                                    approve_user_id=None,
                                    status=None,
                                    approve_status=None,
                                    apply_resource_type=None,
                                    resource_group_id=None,
                                    create_time = None,
                                    search_word=None,
                                    approve_result=None,
                                    columns=[],
                                    sort_key='',
                                    offset=-1,
                                    limit=-1,
                                    reverse=0,
                                    is_and=1,
                                    **params):
        action = ACTION_VDI_DESCRIBE_DESKTOP_APPLY_FORMS
        body = {}
        body["zone"] = zone
        if applys:
            body['apply_ids'] = applys
        if apply_type:
            body['apply_type'] = apply_type
        if apply_title:
            body['apply_title'] = apply_title
        if apply_user_id:
            body['apply_user_id'] = apply_user_id
        if approve_user_id:
            body['approve_user_id'] = approve_user_id
        if status:
            body['status'] = status
        if approve_status:
            body["approve_status"] = approve_status
        if apply_resource_type:
            body['apply_resource_type'] = apply_resource_type
        if resource_group_id:
            body['resource_group_id'] = resource_group_id
        if search_word:
            body['search_word'] = search_word
        if create_time:
            body["create_time"] = create_time
        if columns:
            body['columns'] = columns
        if sort_key:
            body['sort_key'] = sort_key
        if reverse == 1:
            body['reverse'] = True
        if approve_result:
            body["approve_status"] = approve_result
        elif reverse == 0:
            body['reverse'] = False
        if offset >= 0:
            body['offset'] = offset
        if limit >= 0:
            body['limit'] = limit
        if is_and == 1:
            body['is_and'] = True
        elif is_and == 0:
            body['is_and'] = False
        return self._build_params(action, body)

    def modify_desktop_apply_form(self,
                                  zone,
                                  apply_id,
                                  apply_title=None,
                                  apply_parameter=None,
                                  approve_user_id=None,
                                  apply_description=None,
                                  apply_age=None,
                                  start_time = None,
                                  end_time = None,
                                  **params):
        action = ACTION_VDI_MODIFY_DESKTOP_APPLY_FORM
        body = {}
        body["zone"] = zone
        body['apply_id'] = apply_id
        if apply_title:
            body['apply_title'] = apply_title
        if apply_parameter:
            body['apply_parameter'] = apply_parameter
        if approve_user_id:
            body['approve_user_id'] = approve_user_id
        if apply_description is not None:
            body['apply_description'] = apply_description
        if apply_age is not None:
            body['apply_age'] = apply_age
            
        if start_time:
            body["start_time"] = start_time
        
        if end_time:
            body["end_time"] = end_time
        
        return self._build_params(action, body)

    def delete_desktop_apply_form(self,
                                  zone,
                                  applys=[],
                                  **params):
        action = ACTION_VDI_DELETE_DESKTOP_APPLY_FORMS
        body = {}
        body["zone"] = zone
        body['applys'] = applys

        return self._build_params(action, body)

    def deal_desktop_apply_form(self,
                                zone,
                                apply_id,
                                approve_user_id,
                                result,
                                approve_advice=None,
                                approve_parameter=None,
                                apply_age=None,
                                start_time=None,
                                end_time=None,
                                **params):
        action = ACTION_VDI_DEAL_DESKTOP_APPLY_FORM
        body = {}
        body["zone"] = zone
        if apply_id:
            body['apply_id'] = apply_id
        if approve_user_id:
            body['approve_user_id'] = approve_user_id
        if result:
            body['result'] = result
        if approve_advice:
            body['approve_advice'] = approve_advice
        if approve_parameter:
            body['approve_parameter'] = approve_parameter
        if apply_age is not None:
            body['apply_age'] = apply_age
        if start_time:
            body['start_time'] = start_time
        if end_time:
            body['end_time'] = end_time
        return self._build_params(action, body)

    def get_approve_users(self,
                          zone,
                          apply_user_id,
                          resource_group_id,
                          **params):
        action = ACTION_VDI_GET_APPROVE_USERS
        body = {}
        body["zone"] = zone
        body['apply_user_id'] = apply_user_id
        body['resource_group_id'] = resource_group_id

        return self._build_params(action, body)



