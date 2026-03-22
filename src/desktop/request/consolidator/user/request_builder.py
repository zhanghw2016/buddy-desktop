
from constants import (
    ACTION_VDI_DESCRIBE_ZONE_USERS,
    ACTION_VDI_ENABLE_ZONE_USERS,
    ACTION_VDI_DISABLE_ZONE_USERS,
    ACTION_VDI_MODIFY_ZONE_USER_ROLE,
    ACTION_VDI_GET_ZONE_USER_ADMINS,
    ACTION_VDI_MODIFY_ZONE_USER_SCOPE,
    ACTION_VDI_DESCRIBE_ZONE_USER_SCOPE,
    ACTION_VDI_DESCRIBE_API_ACTIONS,
    ACTION_VDI_DESCRIBE_ZONE_USER_LOGIN_RECORD,

    ACTION_VDI_DESCRIBE_USER_DESKTOP_SESSION,
    ACTION_VDI_LOGOUT_USER_DESKTOP_SESSION,
    ACTION_VDI_MODIFY_USER_DESKTOP_SESSION,
    ACTION_VDI_CREATE_DESKTOP_USER_SESSION,
    ACTION_VDI_DELETE_DESKTOP_USER_SESSION,
    ACTION_VDI_CHECK_DESKTOP_USER_SESSION,
)

from request.consolidator.base.base_request_builder import BaseRequestBuilder

class DesktopUserRequestBuilder(BaseRequestBuilder):
    ''' API request builder '''

    def describe_zone_users(self,
                            users=[],
                            zones=[],
                            user_names=[],
                            status=[],
                            role=[],
                            user_dns=[],
                            search_word = None,
                            excluded_user_ids=[],
                            columns=[],
                            is_and=-1,
                            sort_key='',
                            reverse=-1,
                            offset=-1,
                            limit=-1,
                            verbose=0,
                            check_module_custom_user=0,
                            **params):

        action = ACTION_VDI_DESCRIBE_ZONE_USERS
        body = {}
        if users:
            body['users'] = users
        if zones:
            body['zones'] = zones
        if status:
            body['status'] = status
        if role:
            body['role'] = role
        if user_names:
            body['user_names'] = user_names
        if user_dns:
            body['user_dns'] = user_dns
        if excluded_user_ids:
            body["excluded_user_ids"] = excluded_user_ids
        if columns:
            body['columns'] = columns
        if sort_key:
            body['sort_key'] = sort_key
        if reverse == 1:
            body['reverse'] = True
        else:
            body['reverse'] = False
        if is_and == 0:
            body['is_and'] = False
        else:
            body['is_and'] = True
        if offset >= 0:
            body['offset'] = offset
        if limit >= 0:
            body['limit'] = limit
        if verbose:
            body["verbose"] = verbose
        if search_word:
            body["search_word"] = search_word

        if check_module_custom_user:
            body["check_module_custom_user"] = check_module_custom_user
        return self._build_params(action, body)

    def enable_zone_users(self,
                            user_ids,
                            **params):
        action = ACTION_VDI_ENABLE_ZONE_USERS
        body = {}
        if user_ids:
            body['user_ids'] = user_ids

        return self._build_params(action, body)

    def disable_zone_users(self,
                            user_ids,
                            **params):
        action = ACTION_VDI_DISABLE_ZONE_USERS
        body = {}
        if user_ids:
            body['user_ids'] = user_ids

        return self._build_params(action, body)

    def modify_zone_user_role(self,
                                user_id,
                                role,
                                **params):
        action = ACTION_VDI_MODIFY_ZONE_USER_ROLE
        body = {}
        if user_id:
            body['user_id'] = user_id
        if role:
            body['role'] = role

        return self._build_params(action, body)

    def get_zone_user_admins(self,
                                user_id,
                                apply_group_id=None,
                                **params):
        action = ACTION_VDI_GET_ZONE_USER_ADMINS
        body = {}
        if user_id:
            body['user_id'] = user_id
        
        if apply_group_id:
            body["apply_group_id"] = apply_group_id

        return self._build_params(action, body)

    def create_desktop_user_session(self,
                                user_name,
                                password,
                                session_type='',
                                client_ip=None,
                                zone=None,
                                **params):
        action = ACTION_VDI_CREATE_DESKTOP_USER_SESSION
        body = {}
        if user_name:
            body['user_name'] = user_name
        if password:
            body['password'] = password
        if session_type:
            body['session_type'] = session_type
        if client_ip:
            body['client_ip'] = client_ip
        
        if zone:
            body["zone"] = zone

        return self._build_params(action, body)

    def delete_desktop_user_session(self,
                                    sk,
                                    **params):
        action = ACTION_VDI_DELETE_DESKTOP_USER_SESSION
        body = {}
        if sk:
            body['sk'] = sk

        return self._build_params(action, body)
    
    def check_desktop_user_session(self,
                                    sk,
                                    **params):
        action = ACTION_VDI_CHECK_DESKTOP_USER_SESSION
        body = {}
        if sk:
            body['sk'] = sk

        return self._build_params(action, body)

    def modify_zone_user_scope(self,
                                  user_id,
                                  json_items,
                                  **params):
        action = ACTION_VDI_MODIFY_ZONE_USER_SCOPE
        body = {}
        if user_id:
            body['user_id'] = user_id
        if json_items:
            body['json_items'] = json_items
        return self._build_params(action, body)

    def describe_zone_user_scope(self,
                                  user=None,
                                  exclude_user=None,
                                  resource_type=None,
                                  resources=None,
                                  action_type=None,
                                  reverse = None,
                                  sort_key = None,
                                  offset = 0,
                                  limit = 20,
                                  search_word = None,
                                  **params):
        action = ACTION_VDI_DESCRIBE_ZONE_USER_SCOPE
        body = {}
        if user:
            body['user'] = user
        if exclude_user:
            body['exclude_user'] = exclude_user
        if resource_type:
            body["resource_type"] = resource_type
        if resources:
            body["resources"] = resources
        if action_type:
            body["action_type"] = action_type
        if search_word:
            body['search_word'] = search_word
        if offset:
            body['offset'] = int(offset)
        if limit:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        return self._build_params(action, body)

    def describe_api_actions(self,
                             resource_type=None,
                             resources=None,
                             action_api=None,
                             **params):
        action = ACTION_VDI_DESCRIBE_API_ACTIONS
        body = {}
        if resource_type:
            body["resource_type"] = resource_type
        if resources:
            body["resources"] = resources
        if action_api:
            body["action_api"] = action_api

        return self._build_params(action, body)

    def describe_zone_user_login_record(self,
                                        user_login_records=[],
                                        users=[],
                                        zones=[],
                                        search_word = None,
                                        columns=[],
                                        is_and=-1,
                                        sort_key='',
                                        reverse=-1,
                                        offset=-1,
                                        limit=-1,
                                        verbose=0,
                                        **params):

        action = ACTION_VDI_DESCRIBE_ZONE_USER_LOGIN_RECORD
        body = {}
        if user_login_records:
            body['user_login_records'] = user_login_records
        if users:
            body['users'] = users
        if zones:
            body['zones'] = zones
        if columns:
            body['columns'] = columns
        if sort_key:
            body['sort_key'] = sort_key
        if reverse == 1:
            body['reverse'] = True
        else:
            body['reverse'] = False
        if is_and == 0:
            body['is_and'] = False
        else:
            body['is_and'] = True
        if offset >= 0:
            body['offset'] = offset
        if limit >= 0:
            body['limit'] = limit
        if verbose:
            body["verbose"] = verbose
        if search_word:
            body["search_word"] = search_word   
        return self._build_params(action, body)

    def describe_user_desktop_session(self,
                                      approveEmpId=None,
                                      approveState=None,
                                      pageNo=None,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_USER_DESKTOP_SESSION

        body = {}
        if approveEmpId:
            body["approveEmpId"] = approveEmpId
        if approveState:
            body["approveState"] = approveState
        if pageNo:
            body["pageNo"] = pageNo

        return self._build_params(action, body)

    def logout_user_desktop_session(self,
                                    workerUid,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_LOGOUT_USER_DESKTOP_SESSION

        body = {}
        if workerUid:
            body["workerUid"] = workerUid

        return self._build_params(action, body)

    def modify_user_desktop_session(self,
                                    applyEmpId=None,
                                    hostname=None,
                                    deliverGrpName=None,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_USER_DESKTOP_SESSION

        body = {}
        if applyEmpId:
            body["applyEmpId"] = applyEmpId
        if hostname:
            body["hostname"] = hostname
        if deliverGrpName:
            body["deliverGrpName"] = deliverGrpName

        return self._build_params(action, body)
