import constants as const
from request.consolidator.base.base_request_builder import BaseRequestBuilder
from log.logger import logger

class GuestRequestBuilder(BaseRequestBuilder):

    def send_desktop_message(self,
                             desktop_ids=[],
                             desktop_group_ids=[],
                             base64_message='',
                             **params):
        action = const.ACTION_VDI_SEND_DESKTOP_MESSAGE
        body = {}
        if desktop_ids:
            body['desktop_ids'] = desktop_ids
        if desktop_group_ids:
            body['desktop_group_ids'] = desktop_group_ids
        if base64_message:
            body['base64_message'] = base64_message
        return self._build_params(action, body)

    def send_desktop_notify(self,
                            base64_notify,
                            desktop_ids=[],
                            desktop_group_ids=[],
                            **params):
        action = const.ACTION_VDI_SEND_DESKTOP_NOTIFY
        body = {}
        if desktop_ids:
            body['desktop_ids'] = desktop_ids
        if desktop_group_ids:
            body['desktop_group_ids'] = desktop_group_ids
        if base64_notify:
            body['base64_notify'] = base64_notify
        return self._build_params(action, body)

    def send_desktop_hot_heys(self,
                              desktop_ids=[],
                              keys='',
                              timeout=0,
                              time_step=0,
                              **params):
        action = const.ACTION_VDI_SEND_DESKTOP_HOT_KEYS
        body = {}
        if desktop_ids:
            body['desktop_ids'] = desktop_ids
        if keys:
            body['keys'] = keys
        body['timeout'] = timeout if timeout > 0 else 0
        body['time_step'] = time_step if time_step > 0 else 0
        return self._build_params(action, body)
    
    def check_desktop_guest_agent(self,
                              desktop_ids=[],
                              desktop_group_ids=[],
                              **params):
        action = const.ACTION_VDI_CHECK_DESKTOP_AGENT_STATUS
        body = {}
        if desktop_ids:
            body['desktop_ids'] = desktop_ids
        if desktop_group_ids:
            body['desktop_group_ids'] = desktop_group_ids
        return self._build_params(action, body) 

    def login_desktop(self,
                      desktop_id='',
                      username='',
                      password='',
                      **params):
        action = const.ACTION_VDI_LOGIN_DESKTOP
        body = {}
        if desktop_id:
            body['desktop_id'] = desktop_id
        if username:
            body['username'] = username
        if password:
            body['password'] = password
        return self._build_params(action, body) 

    def login_off(self,
                  desktop_id='',
                  **params):
        action = const.ACTION_VDI_LOGOFF_DESKTOP
        body = {}
        if desktop_id:
            body['desktop_id'] = desktop_id
        return self._build_params(action, body) 

    def add_desktop_active_directory(self,
                              desktop_ids=[],
                              desktop_group_ids=[],
                              org_dn='',
                              **params):
        action = const.ACTION_VDI_ADD_DESKTOP_ACTIVE_DIRECTORY
        body = {}
        if desktop_ids:
            body['desktop_ids'] = desktop_ids
        if desktop_group_ids:
            body['desktop_group_ids'] = desktop_group_ids
        if org_dn:
            body['org_dn'] = org_dn
        return self._build_params(action, body)

    def modify_guest_server_config(self,
                                     guest_server_config,
                                     desktop_ids=[],
                                     desktop_group_ids=[],
                                     **params):
        action = const.ACTION_VDI_MODIFY_GUEST_SERVER_CONFIG
        body = {}
        if guest_server_config:
            body['guest_server_config'] = guest_server_config
        if desktop_ids:
            body['desktop_ids'] = desktop_ids
        if desktop_group_ids:
            body['desktop_group_ids'] = desktop_group_ids
        return self._build_params(action, body)

    def describe_spice_info(self,
                            desktop_id = None,
                            hostname=None,
                            login_user = None,
                            client_ip = None,
                            connect_status = None,
                            offset = None,
                            limit = None,
                            verbose = None,
                            **params):
        '''
            @param directive : the dictionary of params
        '''
        action = const.ACTION_VDI_DESCRIBE_SPICE_INFO
        body = {}

        if desktop_id:
            body['desktop_id'] = desktop_id
        if hostname:
            body['hostname'] = hostname
        if login_user:
            body['login_user'] = login_user
        if client_ip:
            body['client_ip'] = client_ip
        if connect_status is not None and connect_status in [0, 1]:
            body['connect_status'] = connect_status
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if verbose is not None:
            body['verbose'] = int(verbose)

        return self._build_params(action, body)

    def describe_guest_processes(self,
                                 desktop_id = None,
                                 order_by = None,
                                 top=None,
                                 **params):
        '''
            @param directive : the dictionary of params
        '''
        action = const.ACTION_VDI_DESCRIBE_GUEST_PROCESSES
        body = {}

        if desktop_id:
            body['desktop_id'] = desktop_id
        if order_by:
            body['order_by'] = order_by
        if top:
            body['top'] = top

        return self._build_params(action, body)

    def describe_guest_programs(self,
                                 desktop_id = None,
                                 **params):
        '''
            @param directive : the dictionary of params
        '''
        action = const.ACTION_VDI_DESCRIBE_GUEST_PROGRAMS
        body = {}

        if desktop_id:
            body['desktop_id'] = desktop_id

        return self._build_params(action, body)

    def handle_guest_json_rpc(self,
                             json_request=None,
                            **params):
        action = const.ACTION_VDI_GUEST_JSON_RCP
        body = {}
        if json_request:
            body["json_request"] = json_request
        return self._build_params(action, body)

    def create_desktop_maintainer(self,
                                  zone,
                                  desktop_maintainer_name,
                                  desktop_maintainer_type,
                                  json_detail,
                                  description=None,
                                  **params):
        action = const.ACTION_VDI_CREATE_DESKTOP_MAINTAINER
        body = {}
        body["zone"] = zone
        body["desktop_maintainer_name"] = desktop_maintainer_name
        body["desktop_maintainer_type"] = desktop_maintainer_type
        body["json_detail"] = json_detail
        if description:
            body["description"] = description
        return self._build_params(action, body)

    def modify_desktop_maintainer_attributes(self,
                                             zone,
                                             desktop_maintainers,
                                             desktop_maintainer_name=None,
                                             desktop_maintainer_type=None,
                                             description=None,
                                             json_detail=None,
                                             **params):
        action = const.ACTION_VDI_MODIFY_DESKTOP_MAINTAINER_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body["desktop_maintainers"] = desktop_maintainers
        if desktop_maintainer_name:
            body["desktop_maintainer_name"] = desktop_maintainer_name
        if desktop_maintainer_type:
            body["desktop_maintainer_type"] = desktop_maintainer_type
        if description:
            body["description"] = description
        if json_detail:
            body["json_detail"] = json_detail
        return self._build_params(action, body)

    def delete_desktop_maintainers(self,
                                   zone,
                                   desktop_maintainers=None,
                                   **params):
        action = const.ACTION_VDI_DELETE_DESKTOP_MAINTAINERS
        body = {}
        body["zone"] = zone
        if desktop_maintainers:
            body["desktop_maintainers"] = desktop_maintainers
        return self._build_params(action, body)

    def describe_desktop_maintainers(self,
                                     zone,
                                     desktop_maintainers=None,
                                     desktop_maintainer_type=None,
                                     status=None,
                                     search_word=None,
                                     offset=None,
                                     limit=None,
                                     verbose=0,
                                     reverse=0,
                                     sort_key=None,
                                     is_and=1,
                                     **params):
        action = const.ACTION_VDI_DESCRIBE_DESKTOP_MAINTAINERS
        body = {}
        body["zone"] = zone
        if desktop_maintainers:
            body["desktop_maintainers"] = desktop_maintainers
        if desktop_maintainer_type:
            body["desktop_maintainer_type"] = desktop_maintainer_type
        if status:
            body['status'] = status
        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if verbose is not None:
            body['verbose'] = int(verbose)
        if reverse == 0:
            body['reverse'] = 0
        else:
            body['reverse'] = 1
        if sort_key:
            body["sort_key"] = sort_key
        if is_and == 0:
            body['is_and'] = 0
        else:
            body['is_and'] = 1
        return self._build_params(action, body)

    def guest_check_desktop_maintainer(self,
                                       zone,
                                       desktop_id,
                                       **params):
        action = const.ACTION_VDI_GUEST_CHECK_DESKTOP_MAINTAINER
        body = {}
        body["zone"] = zone
        if desktop_id:
            body["desktop_id"] = desktop_id
        return self._build_params(action, body)

    def apply_desktop_maintainer(self,
                                 zone,
                                 desktop_maintainer,
                                 **params):
        action = const.ACTION_VDI_APPLY_DESKTOP_MAINTAINER
        body = {}
        body["zone"] = zone
        body["desktop_maintainer"] = desktop_maintainer
        return self._build_params(action, body)

    def attach_resource_to_desktop_maintainer(self,
                                           zone,
                                           desktop_maintainer,
                                           resources,
                                           **params):
        action = const.ACTION_VDI_ATTACH_RESOURCE_TO_DESKTOP_MAINTAINER
        body = {}
        body["zone"] = zone
        body["desktop_maintainer"] = desktop_maintainer
        body["resources"] = resources

        return self._build_params(action, body)

    def detach_resource_from_desktop_maintainer(self,
                                           zone,
                                           desktop_maintainer,
                                           resources,
                                           **params):
        action = const.ACTION_VDI_DETACH_RESOURCE_FROM_DESKTOP_MAINTAINER
        body = {}
        body["zone"] = zone
        body["desktop_maintainer"] = desktop_maintainer
        body["resources"] = resources
        return self._build_params(action, body)

    def run_guest_shell_command(self,
                                zone,
                                command,
                                resource_id,
                                **params):
        action = const.ACTION_VDI_RUN_GUEST_SHELL_COMMAND
        body = {}
        body["zone"] = zone
        body["command"] = command
        body["resource_id"] = resource_id
        return self._build_params(action, body)

    def describe_guest_shell_commands(self,
                                      zone,
                                      guest_shell_commands=None,
                                      guest_shell_command_type=None,
                                      search_word=None,
                                      offset=None,
                                      limit=None,
                                      verbose=0,
                                      reverse=0,
                                      sort_key=None,
                                      is_and=1,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = const.ACTION_VDI_DESCRIBE_GUEST_SHELL_COMMANDS
        body = {}
        body["zone"] = zone
        if guest_shell_commands:
            body['guest_shell_commands'] = guest_shell_commands
        if guest_shell_command_type:
            body['guest_shell_command_type'] = guest_shell_command_type
        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if verbose is not None:
            body['verbose'] = int(verbose)
        if reverse == 0:
            body['reverse'] = 0
        else:
            body['reverse'] = 1
        if sort_key:
            body["sort_key"] = sort_key
        if is_and == 0:
            body['is_and'] = 0
        else:
            body['is_and'] = 1

        return self._build_params(action, body)

    def guest_check_shell_command(self,
                                  zone,
                                  desktop_id,
                                  **params):
        action = const.ACTION_VDI_GUEST_CHECK_SHELL_COMMAND
        body = {}
        body["zone"] = zone
        if desktop_id:
            body["desktop_id"] = desktop_id
        return self._build_params(action, body)

