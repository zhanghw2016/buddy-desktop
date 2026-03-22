
from constants import (
    # auth service
    ACTION_VDI_DESCRIBE_AUTH_SERVICES,
    ACTION_VDI_CREATE_AUTH_SERVICE,
    ACTION_VDI_CHECK_AUTH_SERVICE_OUS,
    ACTION_VDI_MODIFY_AUTH_SERVICE_ATTRIBUTES,
    ACTION_VDI_DELETE_AUTH_SERVICES,
    ACTION_VDI_ADD_AUTH_SERVICE_TO_ZONE,
    ACTION_VDI_REMOVE_AUTH_SERVICE_FROM_ZONES,
    ACTION_VDI_REFRESH_AUTH_SERVICE,
    # auth user
    ACTION_VDI_DESCRIBE_AUTH_USERS,
    ACTION_VDI_CREATE_AUTH_USER,
    ACTION_VDI_DELETE_AUTH_USERS,
    ACTION_VDI_MODIFY_AUTH_USER_ATTRIBUTES,
    ACTION_VDI_MODIFY_AUTH_USER_PASSWORD,
    ACTION_VDI_RESET_AUTH_USER_PASSWORD,
    ACTION_VDI_IMPORT_AUTH_USERS,

    # org unit
    ACTION_VDI_DESCRIBE_AUTH_OUS,
    ACTION_VDI_CREATE_AUTH_OU,
    ACTION_VDI_DELETE_AUTH_OU,
    ACTION_VDI_MODIFY_AUTH_OU_ATTRIBUTES,
    ACTION_VDI_CHANGE_AUTH_USER_IN_OU,

    # user group
    ACTION_VDI_DESCRIBE_AUTH_USER_GROUPS,
    ACTION_VDI_CREATE_AUTH_USER_GROUP,
    ACTION_VDI_MODIFY_AUTH_USER_GROUP_ATTRIBUTES,
    ACTION_VDI_DELETE_AUTH_USER_GROUPS,
    ACTION_VDI_ADD_AUTH_USER_TO_USER_GROUP,
    ACTION_VDI_REMOVE_AUTH_USER_FROM_USER_GROUP,
    ACTION_VDI_RENAME_AUTH_USER_DN,
    ACTION_VDI_SET_AUTH_USER_STATUS,

    # radius
    ACTION_VDI_DESCRIBE_RADIUS_SERVICES,
    ACTION_VDI_CREATE_RADIUS_SERVICE,
    ACTION_VDI_MODIFY_RADIUS_SERVICE_ATTRIBUTES,
    ACTION_VDI_DELETE_RADIUS_SERVICES,
    ACTION_VDI_ADD_AUTH_RADIUS_USERS,
    ACTION_VDI_REMOVE_AUTH_RADIUS_USERS,
    ACTION_VDI_MODIFY_RADIUS_USER_ATTRIBUTES,
    ACTION_VDI_CHECK_RADIUS_TOKEN,
    # password prompt
    ACTION_VDI_CREATE_PASSWORD_PROMPT_QUESTION,
    ACTION_VDI_MODIFY_PASSWORD_PROMPT_QUESTION,
    ACTION_VDI_DELETE_PASSWORD_PROMPT_QUESTION,
    ACTION_VDI_DESCRIBE_PASSWORD_PROMPT_QUESTION,
    ACTION_VDI_CREATE_PASSWORD_PROMPT_ANSWER,
    ACTION_VDI_MODIFY_PASSWORD_PROMPT_ANSWER,
    ACTION_VDI_DELETE_PASSWORD_PROMPT_ANSWER,
    ACTION_VDI_CHECK_PASSWORD_PROMPT_ANSWER,
    ACTION_VDI_DESCRIBE_PASSWORD_PROMPT_HAVE_ANSWER,
    ACTION_VDI_DESCRIBE_HAVE_PASSWORD_ANSWER_USERS,
    ACTION_VDI_IGNORE_PASSWORD_PROMPT_QUESTION,
)
from constants import (
    AUTH_SERVICE_TYPES,GLOBAL_ADMIN_USER_NAME
)
from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import AuthRequestBuilder
from utils.json import json_load

class AuthRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(AuthRequestChecker, self).__init__(sender, checker)
        self.builder = AuthRequestBuilder(sender)

        self.handler_map = {
            ACTION_VDI_DESCRIBE_AUTH_SERVICES: self.describe_auth_services,
            ACTION_VDI_CREATE_AUTH_SERVICE: self.create_auth_service,
            ACTION_VDI_CHECK_AUTH_SERVICE_OUS: self.check_auth_service_ous,
            ACTION_VDI_MODIFY_AUTH_SERVICE_ATTRIBUTES: self.modify_auth_service_attributes,
            ACTION_VDI_DELETE_AUTH_SERVICES: self.delete_auth_services,
            ACTION_VDI_ADD_AUTH_SERVICE_TO_ZONE: self.add_auth_service_to_zone,
            ACTION_VDI_REMOVE_AUTH_SERVICE_FROM_ZONES: self.remove_auth_service_from_zones,
            ACTION_VDI_REFRESH_AUTH_SERVICE: self.refresh_auth_service,

            ACTION_VDI_DESCRIBE_AUTH_USERS: self.describe_auth_users,
            ACTION_VDI_CREATE_AUTH_USER: self.create_auth_user,
            ACTION_VDI_DELETE_AUTH_USERS: self.delete_auth_users,
            ACTION_VDI_MODIFY_AUTH_USER_ATTRIBUTES: self.modify_auth_user_attributes,
            ACTION_VDI_MODIFY_AUTH_USER_PASSWORD: self.modify_auth_user_password,
            ACTION_VDI_RESET_AUTH_USER_PASSWORD: self.reset_auth_user_password,
            ACTION_VDI_IMPORT_AUTH_USERS: self.import_auth_users,
        
            # org unit
            ACTION_VDI_DESCRIBE_AUTH_OUS: self.describe_auth_ous,
            ACTION_VDI_CREATE_AUTH_OU: self.create_auth_ou,
            ACTION_VDI_DELETE_AUTH_OU: self.delete_auth_ou,
            ACTION_VDI_MODIFY_AUTH_OU_ATTRIBUTES: self.modify_auth_ou_attributes,
            ACTION_VDI_CHANGE_AUTH_USER_IN_OU: self.change_auth_user_in_ou,
        
            # user group
            ACTION_VDI_DESCRIBE_AUTH_USER_GROUPS: self.describe_auth_user_groups,
            ACTION_VDI_CREATE_AUTH_USER_GROUP: self.create_auth_user_group,
            ACTION_VDI_MODIFY_AUTH_USER_GROUP_ATTRIBUTES: self.modify_auth_user_group_attributes,
            ACTION_VDI_DELETE_AUTH_USER_GROUPS: self.delete_auth_user_groups,
            ACTION_VDI_ADD_AUTH_USER_TO_USER_GROUP: self.add_auth_user_to_user_group,
            ACTION_VDI_REMOVE_AUTH_USER_FROM_USER_GROUP: self.remove_auth_user_from_user_group,
            ACTION_VDI_RENAME_AUTH_USER_DN: self.rename_auth_user_dn,
            ACTION_VDI_SET_AUTH_USER_STATUS: self.set_auth_user_status,
            # radius
            ACTION_VDI_DESCRIBE_RADIUS_SERVICES: self.describe_radius_services,
            ACTION_VDI_CREATE_RADIUS_SERVICE: self.create_radius_service,
            ACTION_VDI_MODIFY_RADIUS_SERVICE_ATTRIBUTES: self.modify_radius_service_attributes,
            ACTION_VDI_DELETE_RADIUS_SERVICES: self.delete_radius_services,
            ACTION_VDI_ADD_AUTH_RADIUS_USERS: self.add_auth_radius_users,
            ACTION_VDI_REMOVE_AUTH_RADIUS_USERS: self.remove_auth_radius_users,
            ACTION_VDI_MODIFY_RADIUS_USER_ATTRIBUTES : self.modify_radius_user_attributes,
            ACTION_VDI_CHECK_RADIUS_TOKEN: self.check_radius_token,
        
            # password
            ACTION_VDI_CREATE_PASSWORD_PROMPT_QUESTION: self.create_password_prompt_question,
            ACTION_VDI_MODIFY_PASSWORD_PROMPT_QUESTION: self.modify_password_prompt_question,
            ACTION_VDI_DELETE_PASSWORD_PROMPT_QUESTION: self.delete_password_prompt_question,
            ACTION_VDI_DESCRIBE_PASSWORD_PROMPT_QUESTION: self.describe_password_prompt_question,
            ACTION_VDI_CREATE_PASSWORD_PROMPT_ANSWER: self.create_password_prompt_answer,
            ACTION_VDI_MODIFY_PASSWORD_PROMPT_ANSWER: self.modify_password_prompt_answer,
            ACTION_VDI_DELETE_PASSWORD_PROMPT_ANSWER: self.delete_password_prompt_answer,
            ACTION_VDI_CHECK_PASSWORD_PROMPT_ANSWER: self.check_password_prompt_answer,
            ACTION_VDI_DESCRIBE_PASSWORD_PROMPT_HAVE_ANSWER: self.describe_password_prompt_have_answer,
            ACTION_VDI_DESCRIBE_HAVE_PASSWORD_ANSWER_USERS: self.describe_have_password_answer_users,
            ACTION_VDI_IGNORE_PASSWORD_PROMPT_QUESTION: self.ignore_password_prompt_question,
            }
    
    def _check_auth_service_type(self, auth_service_types):
        
        if not isinstance(auth_service_types, list):
            auth_service_types = [auth_service_types]
        
        for auth_service_type in auth_service_types:
            if auth_service_type not in AUTH_SERVICE_TYPES:
                logger.error("unsupported auth service Type" % auth_service_type)
                self.set_error(ErrorMsg.ERR_MSG_UNSUPPORTED_POLICY_GROUP_TYPE, (auth_service_type, AUTH_SERVICE_TYPES))
                return False

        return True

    def _check_auth_user_info_items(self, json_str):

        json_items = json_load(json_str)
        if not isinstance(json_items, list):
            return False
        
        if len(json_items) == 0:
            return False
        
        for item in json_items:
            if 'user_name' not in item.keys():
                self.set_error(ErrorMsg.ERR_MSG_USER_NAME_NOT_FOUND)
                return False
            if 'password' not in item.keys():
                self.set_error(ErrorMsg.ERR_MSG_USER_PASSWD_NOT_FOUND)
                return False

        return True

    def describe_auth_services(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["auth_services", "auth_service_type", "status"]
                                  ):
            return None

        if directive.get("auth_service_type") and not self._check_auth_service_type(directive["auth_service_type"]):
            return None

        return self.builder.describe_auth_services(**directive)

    def create_auth_service(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["auth_service_type", "admin_name", "admin_password", "base_dn", "domain",
                                                   ],
                                  str_params=["auth_service_type", "admin_name","admin_password", "base_dn", "domain", "host","description", "secondary_host"],
                                  integer_params=["port", "secret_port", "is_sync", "modify_password"],
                                  list_params=[]
                                  ):
            return None

        if directive.get("auth_service_type") and not self._check_auth_service_type(directive["auth_service_type"]):
            return None

        return self.builder.create_auth_service(**directive)

    def check_auth_service_ous(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["auth_service_type", "admin_name", "admin_password", "domain", "host",
                                                   "port", "secret_port"],
                                  str_params=["auth_service_type", "admin_name","admin_password", "base_dn", "domain", "host"],
                                  integer_params=["port", "secret_port"],
                                  list_params=[]
                                  ):
            return None

        if directive.get("auth_service_type") and not self._check_auth_service_type(directive["auth_service_type"]):
            return None

        return self.builder.check_auth_service_ous(**directive)


    def modify_auth_service_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["auth_service"],
                                  str_params=["auth_service", "auth_service_name", "admin_name", "admin_password", "base_dn", "host", "description"],
                                  integer_params=["port", "secret_port", "is_sync", "modify_password"]):
            return None

        return self.builder.modify_auth_service_attributes(**directive)

    def delete_auth_services(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["auth_services"],
                                  list_params=["auth_services"]
                                  ):
            return None

        return self.builder.delete_auth_services(**directive)

    def add_auth_service_to_zone(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["auth_service", "zone_id"],
                                  str_params=['auth_service', 'base_dn', 'zone_id'],
                                  ):
            return None

        return self.builder.add_auth_service_to_zone(**directive)

    def remove_auth_service_from_zones(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["auth_service", "zone_ids"],
                                  str_params=['auth_service'],
                                  list_params=["zone_ids"]
                                  ):
            return None

        return self.builder.remove_auth_service_from_zones(**directive)

    def refresh_auth_service(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["auth_service"],
                                  str_params=['auth_service', 'base_dn'],
                                  list_params=[]
                                  ):
            return None

        return self.builder.refresh_auth_service(**directive)

    # auth user
    def describe_auth_users(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service"],
                                  list_params=['user_names'],
                                  integer_params=["scope", 'syn_desktop', "global_search"],
                                  str_params=['base_dn', "search_name"]):
            return None

        return self.builder.describe_auth_users(**directive)

    def create_auth_user(self, directive):

        if not self._check_params(directive,
                                  required_params=['auth_service','user_name', 'password', 'base_dn'],
                                  integer_params=["account_control"],
                                  str_params=['user_name', 'real_name', 'password', 'description','position', 'base_dn', 'title',
                                      'email', 'personal_phone', 'company_phone']):
            return None

        if 'email' in directive and len(directive['email'])>0 and not self._check_email(directive['email']):
            return None
        
        user_name = directive["user_name"]
        if not self._check_str_length(user_name):
            return None

        real_name = directive.get("real_name")
        if real_name:
            if not self._check_str_length(real_name):
                return None

            if not self._check_user_password(directive['password'], real_name):
                return None

        if not self._check_user_password(directive['password'], user_name):
            return None

        return self.builder.create_auth_user(**directive)

    def modify_auth_user_attributes(self, directive):

        if not self._check_params(directive,
                                  required_params=['auth_service', 'user_name'],
                                  str_params=['email', 'personal_phone', 'company_phone', 'title','description','position']):
            return None
        
        return self.builder.modify_auth_user_attributes(**directive)

    def delete_auth_users(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service", "user_names"],
                                  str_params=['auth_service'],
                                  list_params=['user_names']):
            return None
        
        return self.builder.delete_auth_users(**directive)

    def modify_auth_user_password(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service",'user_name', 'old_password', 'new_password'],
                                  str_params=['user_name', 'old_password', 'new_password']):
            return None
        
        user_name = directive["user_name"]
        new_password = directive["new_password"]
        
        if not self._check_user_password(new_password, user_name):
            return None

        return self.builder.modify_auth_user_password(**directive)
    
    def reset_auth_user_password(self, directive):

        if not self._check_params(directive,
                                  required_params=['user_name', 'password'],
                                  str_params=['user_name', 'password']):
            return None

        user_name = directive["user_name"]
        password = directive["password"]
        if not self._check_user_password(password, user_name):
            return None

        return self.builder.reset_auth_user_password(**directive)

    def import_auth_users(self, directive):

        if not self._check_params(directive,
                                  required_params=['auth_service', 'base_dn', 'json_items'],
                                  str_params=['auth_service', 'base_dn'],
                                  json_params=['json_items']):
            return None

        if not self._check_auth_user_info_items(directive['json_items']):
            logger.error("json_items invalid")
            return None

        return self.builder.import_auth_users(**directive)

    def describe_auth_ous(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service"],
                                  list_params=['ou_names', "user_names"],
                                  integer_params=['verbose', 'scope', "syn_desktop"],
                                  str_params=["auth_service",'base_dn']):
            return None
        
        return self.builder.describe_auth_ous(**directive)

    def create_auth_ou(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service", 'ou_name'],
                                  str_params=['base_dn', 'ou_name', 'description','base_dn']):
            return None
        ou_name = directive["ou_name"]
        if not self._check_str_length(ou_name):
            return None
        
        return self.builder.create_auth_ou(**directive)
    
    def delete_auth_ou(self, directive):
        if not self._check_params(directive,
                                  required_params=['auth_service', 'ou_dn'],
                                  str_params=['ou_dn']):
            return None
        
        return self.builder.delete_auth_ou(**directive)
    
    def modify_auth_ou_attributes(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service", 'ou_dn'],
                                  str_params=["auth_service", 'ou_dn', 'description']):
            return None
        
        return self.builder.modify_auth_ou_attributes(**directive)
    
    def change_auth_user_in_ou(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service", 'user_names', 'new_ou_dn'],
                                  list_params=['user_names'],
                                  str_params=['new_ou_dn']):
            return None
        
        return self.builder.change_auth_user_in_ou(**directive)

    def describe_auth_user_groups(self, directive):

        if not self._check_params(directive,
                                  required_params=['auth_service'],
                                  str_params=['auth_service', 'search_name', 'base_dn'],
                                  integer_params=['verbose', 'scope', 'syn_desktop'],
                                  list_params=['user_group_names', 'user_names']):
            return None
        
        return self.builder.describe_auth_user_groups(**directive)

    def create_auth_user_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service", 'user_group_name'],
                                  str_params=['user_group_name', 'description', 'group_type', 'base_dn']):
            return None
        
        user_group_name = directive["user_group_name"]
        if not self._check_str_length(user_group_name):
            return None

        return self.builder.create_auth_user_group(**directive)

    def modify_auth_user_group_attributes(self, directive):

        if not self._check_params(directive,
                                  required_params=['auth_service', 'user_group_dn'],
                                  str_params=['user_group_dn', 'new_user_group_dn', 'description', 'group_type']):
            return None
        
        return self.builder.modify_auth_user_group_attributes(**directive)

    def delete_auth_user_groups(self, directive):

        if not self._check_params(directive,
                                  required_params=['auth_service', 'user_group_dns'],
                                  list_params=['user_group_dns']):
            return None

        return self.builder.delete_auth_user_groups(**directive)

    def add_auth_user_to_user_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service", 'user_group_dn', 'user_names'],
                                  list_params=['user_names'],
                                  str_params=['user_group_dn']):
            return None
 
        return self.builder.add_auth_user_to_user_group(**directive)

    def remove_auth_user_from_user_group(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service", 'user_group_dn', 'user_names'],
                                  list_params=['user_names'],
                                  str_params=['user_group_dn']):
            return None
        
        return self.builder.remove_auth_user_from_user_group(**directive)

    def rename_auth_user_dn(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service", 'user_dn', 'new_name', 'dn_type'],
                                  str_params=['new_name', 'user_dn', "login_name"]):
            return None
        
        return self.builder.rename_auth_user_dn(**directive)

    def set_auth_user_status(self, directive):

        if not self._check_params(directive,
                                  required_params=["auth_service",'user_names', "status"],
                                  integer_params=["status"],
                                  str_params=[]):
            return None
        
        return self.builder.set_auth_user_status(**directive)

    def describe_radius_services(self, directive):

        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["radius_services", "status"]
                                  ):
            return None
        
        return self.builder.describe_radius_services(**directive)
    
    def create_radius_service(self, directive):

        if not self._check_params(directive,
                                  required_params=['host', 'port', 
                                                   'acct_session', 'identifier', 'secret'],
                                  integer_params=["port", 'port', 'enable_radius'],
                                  str_params=['host', 'radius_service_name', 'description', 'acct_session', 
                                              'identifier', 'secret', "auth_service_id", "ou_dn"]):
            return None
        
        return self.builder.create_radius_service(**directive)

    def modify_radius_service_attributes(self, directive):

        if not self._check_params(directive,
                                  required_params=["radius_service"],
                                  integer_params=["port", "enable_radius"],
                                  str_params=['host', 'radius_service_name', 'description', 'acct_session', 'identifier', 'secret', 'ou_dn']):
            return None
        
        return self.builder.modify_radius_service_attributes(**directive)

    def delete_radius_services(self, directive):

        if not self._check_params(directive,
                                  required_params=["radius_services"],
                                  list_params=["radius_services"]):
            return None
        
        return self.builder.delete_radius_services(**directive)

    def add_auth_radius_users(self, directive):

        if not self._check_params(directive,
                                  required_params=["radius_service", 'user_ids', 'check_radius'],
                                  str_params=["radius_service"],
                                  list_params=["user_ids"]):
            return None
        
        return self.builder.add_auth_radius_users(**directive)

    def remove_auth_radius_users(self, directive):

        if not self._check_params(directive,
                                  required_params=["radius_service", 'user_ids'],
                                  str_params=["radius_service"],
                                  list_params=["user_ids"]):
            return None
        
        return self.builder.remove_auth_radius_users(**directive)

    def modify_radius_user_attributes(self, directive):

        if not self._check_params(directive,
                                  required_params=["user_id"],
                                  str_params=["user_id"],
                                  integer_params=["check_radius"]):
            return None
        
        return self.builder.modify_radius_user_attributes(**directive)

    def check_radius_token(self, directive):

        if not self._check_params(directive,
                                  required_params=["user_id", "token"],
                                  str_params=["user_id", "token"],
                                  integer_params=[],):
            return None
        
        return self.builder.check_radius_token(**directive)

    def create_password_prompt_question(self, directive):
        if not self._check_params(directive,
                                  required_params=['question_content'],
                                  str_params=['question_content']):
            return None
        return self.builder.create_password_prompt_question(**directive)

    def modify_password_prompt_question(self, directive):
        if not self._check_params(directive,
                                  required_params=['prompt_question'],
                                  str_params=['prompt_question', 'question_content']):
            return None
        return self.builder.modify_password_prompt_question(**directive)

    def delete_password_prompt_question(self, directive):
        if not self._check_params(directive,
                                  required_params=['prompt_questions'],
                                  list_params=['prompt_questions']):
            return None
        return self.builder.delete_password_prompt_question(**directive)

    def describe_password_prompt_question(self, directive):
        if not self._check_params(directive,
                                  str_params=['sort_key', "search_word"],
                                  integer_params=['is_and', 'reverse', 'offset', 'limit', 'verbose'],
                                  list_params=['prompt_questions', 'title']):
            return None
        return self.builder.describe_password_prompt_question(**directive)

    def create_password_prompt_answer(self, directive):
        if not self._check_params(directive,
                                  required_params=['user_name', 'prompt_question', 'answer_content'],
                                  str_params=['user_name', 'prompt_question', 'answer_content']):
            return None
        return self.builder.create_password_prompt_answer(**directive)

    def modify_password_prompt_answer(self, directive):
        if not self._check_params(directive,
                                  required_params=['prompt_answer'],
                                  str_params=['prompt_answer', 'answer_content']):
            return None
        return self.builder.modify_password_prompt_answer(**directive)

    def delete_password_prompt_answer(self, directive):
        if not self._check_params(directive,
                                  required_params=['prompt_answers'],
                                  list_params=['prompt_answers']):
            return None
        return self.builder.delete_password_prompt_answer(**directive)

    def check_password_prompt_answer(self, directive):
        if not self._check_params(directive,
                                  required_params=['json_answers'],
                                  json_params=['json_answers']):
            return None
        return self.builder.check_password_prompt_answer(**directive)

    def describe_password_prompt_have_answer(self, directive):
        if not self._check_params(directive,
                                  required_params=['user_name'],
                                  str_params=['user_name']):
            return None
        if directive.get("user_name") == GLOBAL_ADMIN_USER_NAME:
            self.set_error(ErrorMsg.ERR_MSG_ADMIN_CAN_NOT_USE_PASSWORD_PROMPT_ERROR)
            return None
        return self.builder.describe_password_prompt_have_answer(**directive)

    def describe_have_password_answer_users(self, directive):
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=['user_name', 'sort_key', "search_word"],
                                  integer_params=['is_and', 'reverse', 'offset', 'limit', 'verbose']):
            return None
        return self.builder.describe_have_password_answer_users(**directive)

    def ignore_password_prompt_question(self, directive):
        if not self._check_params(directive,
                                  required_params=['user', 'security_question'],
                                  str_params=['user'],
                                  integer_params=['security_question']):
            return None
        return self.builder.ignore_password_prompt_question(**directive)
