
from constants import (
    # auth service
    ACTION_VDI_DESCRIBE_AUTH_SERVICES,
    ACTION_VDI_CREATE_AUTH_SERVICE,
    ACTION_VDI_MODIFY_AUTH_SERVICE_ATTRIBUTES,
    ACTION_VDI_DELETE_AUTH_SERVICES,
    ACTION_VDI_ADD_AUTH_SERVICE_TO_ZONE,
    ACTION_VDI_REMOVE_AUTH_SERVICE_FROM_ZONES,
    ACTION_VDI_REFRESH_AUTH_SERVICE,
    ACTION_VDI_CHECK_AUTH_SERVICE_OUS,

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

from request.consolidator.base.base_request_builder import BaseRequestBuilder

class AuthRequestBuilder(BaseRequestBuilder):
    ''' API request builder '''

    def describe_auth_services(self, 
                                 auth_services=None,
                                 auth_service_type=None,
                                 status=None,
                                 reverse = None,
                                 sort_key = None,
                                 offset = 0,
                                 limit = 20,
                                 search_word = None,
                                 verbose = 0,
                                 **params
                                 ):

        action = ACTION_VDI_DESCRIBE_AUTH_SERVICES
        body = {}
        
        if auth_services:
            body["auth_services"] = auth_services
        
        if auth_service_type:
            body["auth_service_type"] = auth_service_type

        if status:
            body["status"] = status

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

    def create_auth_service(self,
                            auth_service_type,
                            admin_name,
                            admin_password,
                            base_dn,
                            domain,
                            host=None,
                            port=None,
                            secret_port=None,
                            secondary_host=None,
                            auth_service_name=None,
                            is_sync=None,
                            description=None,
                            modify_password=None,
                            **params
                            ):

        action = ACTION_VDI_CREATE_AUTH_SERVICE
        body = {}
        body["auth_service_type"] = auth_service_type
        body["admin_name"] = admin_name
        body["admin_password"] = admin_password
        body["base_dn"] = base_dn
        body["domain"] = domain
        if host:
            body["host"] = host
        
        if port:
            body["port"] = port
        if secret_port:
            body["secret_port"] = secret_port
        if auth_service_name:
            body["auth_service_name"] = auth_service_name
        
        if secondary_host:
            body["secondary_host"] = secondary_host
        
        if is_sync is not None:
            body["is_sync"] = is_sync
        if description:
            body["description"] = description
        
        if modify_password is not None:
            body["modify_password"] = modify_password

        return self._build_params(action, body)

    def check_auth_service_ous(self,
                            auth_service_type,
                            admin_name,
                            admin_password,
                            domain,
                            host,
                            port,
                            secret_port,
                            **params
                            ):

        action = ACTION_VDI_CHECK_AUTH_SERVICE_OUS
        body = {}
        body["auth_service_type"] = auth_service_type
        body["admin_name"] = admin_name
        body["admin_password"] = admin_password
        body["domain"] = domain
        body["host"] = host
        body["port"] = port
        body["secret_port"] = secret_port

        return self._build_params(action, body)

    def modify_auth_service_attributes(self, 
                                       auth_service,
                                       auth_service_name=None,
                                       admin_name=None,
                                       admin_password=None,
                                       base_dn=None,
                                       host=None,
                                       port=None,
                                       secret_port=None,
                                       is_sync=None,
                                       modify_password=None,
                                       description=None,
                                       **params
                                       ):

        action = ACTION_VDI_MODIFY_AUTH_SERVICE_ATTRIBUTES
        body = {"auth_service": auth_service}
        if auth_service_name is not None:
            body["auth_service_name"] = auth_service_name
        
        if admin_name:
            body["admin_name"] = admin_name
            
        if admin_password:
            body["admin_password"] = admin_password
        
        if base_dn:
            body["base_dn"] = base_dn
        
        if host:
            body["host"] = host
        
        if port:
            body["port"] = port
        
        if secret_port:
            body["secret_port"] = secret_port

        if is_sync is not None:
            body["is_sync"] = is_sync
        if modify_password is not None:
            body["modify_password"] = modify_password
        
        if description is not None:
            body["description"] = description
         
        return self._build_params(action, body)
    
    def delete_auth_services(self,
                            auth_services,
                            **params
                            ):

        action = ACTION_VDI_DELETE_AUTH_SERVICES
        body = {"auth_services": auth_services}
        
        return self._build_params(action, body)
    
    def add_auth_service_to_zone(self,
                                  auth_service,
                                  zone_id,
                                  base_dn=None,
                                  **params
                                  ):
        
        action = ACTION_VDI_ADD_AUTH_SERVICE_TO_ZONE
        body = {"auth_service": auth_service, "zone_id": zone_id}
        if base_dn:
            body["base_dn"] = base_dn
        
        return self._build_params(action, body)

    def remove_auth_service_from_zones(self,
                                      auth_service,
                                      zone_ids,
                                      **params
                                      ):
        
        action = ACTION_VDI_REMOVE_AUTH_SERVICE_FROM_ZONES
        body = {"auth_service": auth_service, "zone_ids": zone_ids}
        
        return self._build_params(action, body)

    def refresh_auth_service(self,
                                  auth_service,
                                  base_dn=None,
                                  **params
                                  ):
        
        action = ACTION_VDI_REFRESH_AUTH_SERVICE
        body = {"auth_service": auth_service}
        if base_dn:
            body["base_dn"] = base_dn

        return self._build_params(action, body)

    # auth user
    def describe_auth_users(self,
                            auth_service,
                            user_names=None,
                            base_dn=None,
                            search_name=None,
                            scope = None,
                            syn_desktop=None,
                            global_search=None,
                            **params):

        action = ACTION_VDI_DESCRIBE_AUTH_USERS

        body = {"auth_service": auth_service}

        if user_names:
            body['user_names'] = user_names

        if base_dn:
            body['base_dn'] = base_dn
            
        if search_name:
            body["search_name"] = search_name
        
        if scope is not None:
            body["scope"] = scope
        
        if syn_desktop is not None:
            body["syn_desktop"] = syn_desktop
        
        if global_search is not None:
            body["global_search"] = global_search
        
        return self._build_params(action, body)

    def create_auth_user(self,
                         auth_service,
                         user_name,
                         password,
                         base_dn,
                         account_control=None,
                         real_name='',
                         email='',
                         description='',
                         position='',
                         title='',
                         personal_phone='',
                         company_phone='',
                         **params):

        action = ACTION_VDI_CREATE_AUTH_USER
        body = {}
        body["auth_service"] = auth_service
        body['user_name'] = user_name
        body['userPassword'] = password
        body['base_dn'] = base_dn

        if account_control is not None:
            body["account_control"] = account_control
        
        if real_name:
            body['displayName'] = real_name
        if email:
            body['email'] = email
        if description:
            body['description'] = description
        if position:
            body['physicalDeliveryOfficeName'] = position
        if title:
            body['title'] = title
        if personal_phone:
            body['telephoneNumber'] = personal_phone
        if company_phone:
            body['homePhone'] = company_phone

        return self._build_params(action, body)

    def modify_auth_user_attributes(self,
                                     auth_service,
                                     user_name,
                                     real_name=None,
                                     email=None,
                                     description=None,
                                     position=None,
                                     title=None,
                                     personal_phone=None,
                                     company_phone=None,
                                     **params):

        action = ACTION_VDI_MODIFY_AUTH_USER_ATTRIBUTES
        body = {"auth_service": auth_service}
        if user_name:
            body['user_name'] = user_name
        if real_name:
            body['displayName'] = real_name
        if email is not None:
            body['mail'] = email
        if description is not None:
            body['description'] = description
        if position is not None:
            body['physicalDeliveryOfficeName'] = position
        if title is not None:
            body['title'] = title
        if personal_phone is not None:
            body['telephoneNumber'] = personal_phone
        if company_phone is not None:
            body['homePhone'] = company_phone

        return self._build_params(action, body)

    def delete_auth_users(self,
                         auth_service,
                         user_names,
                         **params):

        action = ACTION_VDI_DELETE_AUTH_USERS
        body = {"auth_service": auth_service}
        if user_names:
            body['user_names'] = user_names

        return self._build_params(action, body)

    def describe_auth_ous(self,
                                 auth_service,
                                 base_dn=None,
                                 ou_names=None,
                                 user_names=None,
                                 verbose=0,
                                 scope=0,
                                 syn_desktop=None,
                                 **params):

        action = ACTION_VDI_DESCRIBE_AUTH_OUS
        body = {"auth_service": auth_service}
        if base_dn:
            body['base_dn'] = base_dn
        if ou_names:
            body['ou_names'] = ou_names

        if user_names:
            body["user_names"] = user_names
        
        if scope is not None:
            body['scope'] = scope

        if verbose is not None:
            body["verbose"] = verbose

        if syn_desktop is not None:
            body["syn_desktop"] = syn_desktop

        return self._build_params(action, body)

    def create_auth_ou(self,
                       auth_service,
                       ou_name,
                       base_dn=None,
                       description='',
                       **params):
        action = ACTION_VDI_CREATE_AUTH_OU
        body = {"auth_service": auth_service}
        if base_dn:
            body['base_dn'] = base_dn
        if ou_name:
            body['ou_name'] = ou_name
        if description:
            body['description'] = description
        return self._build_params(action, body)
    
    def delete_auth_ou(self,
                       auth_service,
                       ou_dn,
                       **params):
        action = ACTION_VDI_DELETE_AUTH_OU
        body = {"auth_service":auth_service}
        body['ou_dn'] = ou_dn
        return self._build_params(action, body)
    
    def modify_auth_ou_attributes(self,
                                 auth_service,
                                 ou_dn,
                                 description='',
                                 **params):
        action = ACTION_VDI_MODIFY_AUTH_OU_ATTRIBUTES
        body = {"auth_service": auth_service}
        body['ou_dn'] = ou_dn

        if description:
            body['description'] = description
        return self._build_params(action, body)
   
    def change_auth_user_in_ou(self,
                                  auth_service,
                                  user_names,
                                  new_ou_dn,
                                  **params):
        action = ACTION_VDI_CHANGE_AUTH_USER_IN_OU
        body = {"auth_service": auth_service}
        if user_names:
            body['user_names'] = user_names
        if new_ou_dn:
            body['new_ou_dn'] = new_ou_dn
        return self._build_params(action, body)

    def create_auth_user_group(self,
                             auth_service,
                             user_group_name,
                             base_dn=None,
                             group_type=None,
                             description=None,
                             **params):

        action = ACTION_VDI_CREATE_AUTH_USER_GROUP
        body = {"auth_service": auth_service}
        body['user_group_name'] = user_group_name

        if base_dn:
            body['base_dn'] = base_dn

        if group_type:
            body['group_type'] = group_type
        if description:
            body['description'] = description

        return self._build_params(action, body)

    def modify_auth_user_group_attributes(self,
                                         auth_service,
                                         user_group_dn,
                                         new_user_group_dn=None,
                                         group_type=None,
                                         description=None,
                                         **params):
        action = ACTION_VDI_MODIFY_AUTH_USER_GROUP_ATTRIBUTES
        body = {"auth_service": auth_service}
        body['user_group_dn'] = user_group_dn
        if group_type:
            body['group_type'] = group_type
        if description is not None:
            body['description'] = description
        if new_user_group_dn:
            body['new_user_group_dn'] = new_user_group_dn
        return self._build_params(action, body)

    def rename_auth_user_dn(self,
                             auth_service,
                             user_dn,
                             new_name,
                             dn_type,
                             login_name=None,
                             **params):

        action = ACTION_VDI_RENAME_AUTH_USER_DN
        body = {"auth_service": auth_service}
        body['user_dn'] = user_dn
        body['new_name'] = new_name
        body['dn_type'] = dn_type
        if login_name:
            body["login_name"] = login_name
        
        return self._build_params(action, body)

    def set_auth_user_status(self,
                             auth_service,
                             user_names,
                             status,
                             **params):

        action = ACTION_VDI_SET_AUTH_USER_STATUS
        body = {"auth_service": auth_service}
        body['user_names'] = user_names
        body['status'] = status
        
        return self._build_params(action, body)

    def delete_auth_user_groups(self,
                                 auth_service,
                                 user_group_dns,
                                 **params):
        action = ACTION_VDI_DELETE_AUTH_USER_GROUPS
        body = {"auth_service":auth_service}
        body['user_group_dns'] = user_group_dns
        return self._build_params(action, body)

    def describe_auth_user_groups(self,
                                auth_service,
                                base_dn=None,
                                user_group_names=None,
                                user_names=None,
                                search_name=None,
                                scope = None,
                                verbose = None,
                                syn_desktop=None,
                                **params):
        action = ACTION_VDI_DESCRIBE_AUTH_USER_GROUPS
        body = {"auth_service": auth_service}
        if base_dn:
            body['base_dn'] = base_dn
        if user_group_names:
            body['user_group_names'] = user_group_names
        if user_names:
            body["user_names"] = user_names
        
        if search_name:
            body['search_name'] = search_name
        
        if scope is not None:
            body["scope"] = scope
        
        if verbose is not None:
            body["verbose"] = verbose
        
        if syn_desktop is not None:
            body["syn_desktop"] = syn_desktop

        return self._build_params(action, body)

    def add_auth_user_to_user_group(self,
                                     auth_service,
                                     user_group_dn=None,
                                     user_names=None,
                                     **params):
        action = ACTION_VDI_ADD_AUTH_USER_TO_USER_GROUP
        body = {"auth_service": auth_service}
        if user_group_dn:
            body['user_group_dn'] = user_group_dn
        if user_names:
            body['user_names'] = user_names

        return self._build_params(action, body)

    def remove_auth_user_from_user_group(self,
                                     auth_service,
                                     user_group_dn=None,
                                     user_names=None,
                                     **params):
        action = ACTION_VDI_REMOVE_AUTH_USER_FROM_USER_GROUP
        body = {"auth_service":auth_service}

        if user_group_dn:
            body['user_group_dn'] = user_group_dn

        if user_names:
            body['user_names'] = user_names

        return self._build_params(action, body)
    
    def modify_auth_user_password(self,
                                  auth_service,
                                  user_name,
                                  old_password,
                                  new_password,
                                  **params):
        action = ACTION_VDI_MODIFY_AUTH_USER_PASSWORD
        body = {"auth_service": auth_service}
        if user_name:
            body['user_name'] = user_name
        if old_password:
            body['old_password'] = old_password
        if new_password:
            body['new_password'] = new_password
        return self._build_params(action, body)
    
    def reset_auth_user_password(self,
                                  user_name,
                                  password,
                                  auth_service=None,
                                  **params):
        action = ACTION_VDI_RESET_AUTH_USER_PASSWORD
        body = {}
        if user_name:
            body['user_name'] = user_name
        if password:
            body['password'] = password
        if auth_service:
            body["auth_service"] = auth_service
        return self._build_params(action, body)

    def import_auth_users(self,
                          auth_service,
                          base_dn,
                          json_items,
                          **params):
        action = ACTION_VDI_IMPORT_AUTH_USERS
        body = {}
        if auth_service:
            body['auth_service'] = auth_service
        if base_dn:
            body['base_dn'] = base_dn
        if json_items:
            body['json_items'] = json_items
        return self._build_params(action, body)

    def describe_radius_services(self,
                                 radius_services=None,
                                 status=None,
                                 reverse = None,
                                 sort_key = None,
                                 offset = 0,
                                 limit = 20,
                                 search_word = None,
                                 verbose = 0,
                                 **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_RADIUS_SERVICES
        body = {}
        if radius_services:
            body["radius_services"] = radius_services

        if status:
            body["status"] = status

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

    def create_radius_service(self,
                                host,
                                port,
                                secret,
                                acct_session = None,
                                identifier = None,
                                radius_service_name=None,
                                auth_service_id=None,
                                ou_dn=None,
                                description=None,
                                enable_radius = None,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_RADIUS_SERVICE
        body = {}
        body["host"] = host
        body['port'] = port
        if acct_session:
            body['acct_session'] = acct_session
        
        if identifier:
            body["identifier"] = identifier
        body['secret'] = secret
        if radius_service_name:
            body['radius_service_name'] = radius_service_name
        
        if auth_service_id:
            body["auth_service_id"] = auth_service_id
        
        if ou_dn:
            body["ou_dn"] = ou_dn
        
        if enable_radius is not None:
            body["enable_radius"] = enable_radius
        
        if description:
            body['description'] = description

        return self._build_params(action, body)

    def modify_radius_service_attributes(self,
                                         radius_service,
                                         host=None,
                                         port=None,
                                         acct_session=None,
                                         identifier=None,
                                         secret=None,
                                         enable_radius=None,
                                         radius_service_name=None,
                                         description=None,
                                         ou_dn = None,
                                         **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_RADIUS_SERVICE_ATTRIBUTES
        body = {"radius_service": radius_service}
        if host:
            body["host"] = host
        
        if port is not None:
            body['port'] = port
        if acct_session:
            body['acct_session'] = acct_session
        if identifier:
            body["identifier"] = identifier
        
        if secret:
            body['secret'] = secret

        if radius_service_name:
            body['radius_service_name'] = radius_service_name

        if enable_radius is not None:
            body['enable_radius'] = enable_radius

        if ou_dn:
            body["ou_dn"] = ou_dn
        
        if description:
            body['description'] = description
        return self._build_params(action, body)

    def delete_radius_services(self,
                                radius_services,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_RADIUS_SERVICES
        body = {}
        body["radius_services"] = radius_services

        return self._build_params(action, body)

    def add_auth_radius_users(self,
                                radius_service,
                                user_ids,
                                check_radius,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_ADD_AUTH_RADIUS_USERS
        body = {}
        body["radius_service"] = radius_service
        body['user_ids'] = user_ids
        body["check_radius"] = check_radius

        return self._build_params(action, body)

    def remove_auth_radius_users(self,
                                radius_service,
                                user_ids,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_REMOVE_AUTH_RADIUS_USERS
        body = {}
        body["radius_service"] = radius_service
        body['user_ids'] = user_ids

        return self._build_params(action, body)

    def modify_radius_user_attributes(self,
                                user_id,
                                check_radius=None,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_RADIUS_USER_ATTRIBUTES
        body = {}
        body['user_id'] = user_id
        if check_radius is not None:
            body["check_radius"] = check_radius
        
        return self._build_params(action, body)

    def check_radius_token(self,
                                user_id,
                                token,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CHECK_RADIUS_TOKEN
        body = {}
        body['user_id'] = user_id
        body["token"] = token

        return self._build_params(action, body)

    def create_password_prompt_question(self,
                                        question_content,
                                        **params):
        action = ACTION_VDI_CREATE_PASSWORD_PROMPT_QUESTION
        body = {}
        if question_content:
            body['question_content'] = question_content
        return self._build_params(action, body)

    def modify_password_prompt_question(self,
                                        prompt_question,
                                        question_content=None,
                                        **params):
        action = ACTION_VDI_MODIFY_PASSWORD_PROMPT_QUESTION
        body = {}
        if prompt_question:
            body['prompt_question'] = prompt_question
        if question_content:
            body['question_content'] = question_content
        return self._build_params(action, body)

    def delete_password_prompt_question(self,
                                        prompt_questions=None,
                                        **params):
        action = ACTION_VDI_DELETE_PASSWORD_PROMPT_QUESTION
        body = {}
        if prompt_questions:
            body['prompt_questions'] = prompt_questions
        return self._build_params(action, body)

    def describe_password_prompt_question(self,
                                          prompt_questions=None,
                                          title=None,
                                          search_word = None,
                                          columns=[],
                                          is_and=-1,
                                          sort_key='',
                                          reverse=-1,
                                          offset=-1,
                                          limit=-1,
                                          verbose=0,
                                          **params):

        action = ACTION_VDI_DESCRIBE_PASSWORD_PROMPT_QUESTION
        body = {}
        if prompt_questions:
            body['prompt_questions'] = prompt_questions
        if title:
            body['title'] = title
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

    def create_password_prompt_answer(self,
                                        user_name,
                                        prompt_question,
                                        answer_content,
                                        **params):
        action = ACTION_VDI_CREATE_PASSWORD_PROMPT_ANSWER
        body = {}
        if user_name:
            body['user_name'] = user_name
        if prompt_question:
            body['prompt_question'] = prompt_question
        if answer_content:
            body['answer_content'] = answer_content
        return self._build_params(action, body)

    def modify_password_prompt_answer(self,
                                        prompt_answer,
                                        answer_content,
                                        **params):
        action = ACTION_VDI_MODIFY_PASSWORD_PROMPT_ANSWER
        body = {}
        if prompt_answer:
            body['prompt_answer'] = prompt_answer
        if answer_content:
            body['answer_content'] = answer_content
        return self._build_params(action, body)

    def delete_password_prompt_answer(self,
                                        prompt_answers=None,
                                        **params):
        action = ACTION_VDI_DELETE_PASSWORD_PROMPT_ANSWER
        body = {}
        if prompt_answers:
            body['prompt_answers'] = prompt_answers
        return self._build_params(action, body)

    def check_password_prompt_answer(self,
                                          json_answers,
                                          **params):

        action = ACTION_VDI_CHECK_PASSWORD_PROMPT_ANSWER
        body = {}
        if json_answers:
            body['json_answers'] = json_answers
        return self._build_params(action, body)

    def describe_password_prompt_have_answer(self,
                                             user_name,
                                             **params):

        action = ACTION_VDI_DESCRIBE_PASSWORD_PROMPT_HAVE_ANSWER
        body = {}
        if user_name:
            body['user_name'] = user_name
        return self._build_params(action, body)

    def describe_have_password_answer_users(self,
                                            user_name=None,
                                            search_word = None,
                                            columns=[],
                                            is_and=-1,
                                            sort_key='',
                                            reverse=-1,
                                            offset=-1,
                                            limit=-1,
                                            verbose=0,
                                            **params):

        action = ACTION_VDI_DESCRIBE_HAVE_PASSWORD_ANSWER_USERS
        body = {}
        if user_name:
            body['user_name'] = user_name
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

    def ignore_password_prompt_question(self,
                                        user,
                                        security_question,
                                        **params):
        action = ACTION_VDI_IGNORE_PASSWORD_PROMPT_QUESTION
        body = {}
        if user:
            body['user'] = user
        if security_question>=0:
            body['security_question'] = security_question
        return self._build_params(action, body)
