from log.logger import logger
from db.constants import (
    SUPPORT_SCOPE_RESOURCE_TYPE,
)

from constants import (
    USER_ROLE_NORMAL, 
    USER_ROLE_CONSOLE_ADMIN,

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

from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import DesktopUserRequestBuilder

class DesktopUserRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(DesktopUserRequestChecker, self).__init__(sender, checker)
        self.builder = DesktopUserRequestBuilder(sender)

        self.handler_map = {
                ACTION_VDI_DESCRIBE_ZONE_USERS: self.describe_zone_users,
                ACTION_VDI_ENABLE_ZONE_USERS: self.enable_zone_users,
                ACTION_VDI_DISABLE_ZONE_USERS: self.disable_zone_users,
                ACTION_VDI_MODIFY_ZONE_USER_ROLE: self.modify_zone_user_role,
                ACTION_VDI_GET_ZONE_USER_ADMINS: self.get_zone_user_admins,
                ACTION_VDI_MODIFY_ZONE_USER_SCOPE: self.modify_zone_user_scope,
                ACTION_VDI_DESCRIBE_ZONE_USER_SCOPE: self.describe_zone_user_scope,
                ACTION_VDI_DESCRIBE_API_ACTIONS: self.describe_api_actions,
                ACTION_VDI_DESCRIBE_ZONE_USER_LOGIN_RECORD: self.describe_zone_user_login_record,
                
                ACTION_VDI_DESCRIBE_USER_DESKTOP_SESSION: self.describe_user_desktop_session,
                ACTION_VDI_LOGOUT_USER_DESKTOP_SESSION: self.logout_user_desktop_session,
                ACTION_VDI_MODIFY_USER_DESKTOP_SESSION: self.modify_user_desktop_session,
                ACTION_VDI_CREATE_DESKTOP_USER_SESSION: self.create_desktop_user_session,
                ACTION_VDI_DELETE_DESKTOP_USER_SESSION: self.delete_desktop_user_session,
                ACTION_VDI_CHECK_DESKTOP_USER_SESSION: self.check_desktop_user_session,
            }

    def describe_zone_users(self, directive):
        if not self._check_params(directive,
                                  str_params=['sort_key', "search_word"],
                                  integer_params=['is_and', 'reverse', 'offset', 'limit', 'verbose','check_module_custom_user'],
                                  list_params=['users', 'user_names', 'zones', 'columns', 'status', 'excluded_user_ids',
                                               "role", "status"]):
            return None

        return self.builder.describe_zone_users(**directive)

    def enable_zone_users(self, directive):
        if not self._check_params(directive,
                                  required_params=['user_ids'],
                                  list_params=['user_ids']):
            return None

        return self.builder.enable_zone_users(**directive)

    def disable_zone_users(self, directive):
        if not self._check_params(directive,
                                  required_params=['user_ids'],
                                  list_params=['user_ids']):
            return None

        return self.builder.disable_zone_users(**directive)

    def modify_zone_user_role(self, directive):
        if not self._check_params(directive,
                                  required_params=['user_id', 'role'],
                                  str_params=['user_id', 'role']):
            return None
        if directive['role'] not in [USER_ROLE_NORMAL, USER_ROLE_CONSOLE_ADMIN]:
            return None
        return self.builder.modify_zone_user_role(**directive)

    def get_zone_user_admins(self, directive):
        if not self._check_params(directive,
                                  required_params=['user_id'],
                                  str_params=['user_id', "apply_group_id"]):
            return None
        return self.builder.get_zone_user_admins(**directive)

    def create_desktop_user_session(self, directive):
        if not self._check_params(directive,
                                  required_params=['user_name', 'password'],
                                  str_params=['user_name', 'password', 'session_type', 'client_ip', "zone"]):
            return None
        return self.builder.create_desktop_user_session(**directive)

    def delete_desktop_user_session(self, directive):
        if not self._check_params(directive,
                                  required_params=['sk'],
                                  str_params=['sk']):
            return None
        return self.builder.delete_desktop_user_session(**directive)
    
    def check_desktop_user_session(self, directive):
        if not self._check_params(directive,
                                  required_params=['sk'],
                                  str_params=['sk']):
            return None
        return self.builder.check_desktop_user_session(**directive)
    
    def modify_zone_user_scope(self, directive):
        if not self._check_params(directive,
                                  required_params=['user_id','json_items'],
                                  str_params=['user_id'],
                                  json_params=['json_items']):
            return None
        
        if not self._check_user_scope_items(directive['json_items']):
            logger.error("json_items invalid")
            return None

        return self.builder.modify_zone_user_scope(**directive)

    def describe_zone_user_scope(self, directive):
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=['user', 'exclude_user', "search_word", "sort_key"],
                                  integer_params=["limit", "offset", "reverse"],
                                  list_params=['action_type', 'resource_type', "resources"]):
            return None
        return self.builder.describe_zone_user_scope(**directive)

    def describe_api_actions(self, directive):
        if not self._check_params(directive,
                                  required_params=['resource_type', 'action_api'],
                                  str_params=['resource_type'],
                                  list_params=["resources", "action_api"]):
            return None
        if directive["resource_type"] not in SUPPORT_SCOPE_RESOURCE_TYPE:
            logger.error("resource_type not found.")
            return None
        return self.builder.describe_api_actions(**directive)

    def describe_zone_user_login_record(self, directive):
        if not self._check_params(directive,
                                  str_params=['sort_key', "search_word"],
                                  integer_params=['is_and', 'reverse', 'offset', 'limit', 'verbose'],
                                  list_params=['user_login_records', 'users', 'zones', 'columns']):
            return None

        return self.builder.describe_zone_user_login_record(**directive)
