
from constants import (

    # terminal management
    ACTION_VDI_DESCRIBE_TERMINAL_MANAGEMENTS,
    ACTION_VDI_MODIFY_TERMINAL_MANAGEMENT_ATTRIBUTES,
    ACTION_VDI_DELETE_TERMINAL_MANAGEMENTS,
    ACTION_VDI_RESTART_TERMINALS,
    ACTION_VDI_STOP_TERMINALS,

    ACTION_VDI_DESCRIBE_TERMINAL_GROUPS,
    ACTION_VDI_CREATE_TERMINAL_GROUP,
    ACTION_VDI_MODIFY_TERMINAL_GROUP_ATTRIBUTES,
    ACTION_VDI_DELETE_TERMINAL_GROUPS,
    ACTION_VDI_ADD_TERMINAL_TO_TERMINAL_GROUP,
    ACTION_VDI_DELETE_TERMINAL_FROM_TERMINAL_GROUP,

    ACTION_VDI_DESCRIBE_MASTER_BACKUP_IPS,
    ACTION_VDI_DESCRIBE_CBSERVER_HOSTS
)
from request.consolidator.base.base_request_builder import BaseRequestBuilder
from log.logger import logger

class TerminalRequestBuilder(BaseRequestBuilder):

    def describe_terminal_managements(self,
                                    zone,
                                    terminals=None,
                                    terminal_group=None,
                                    terminal_serial_number=None,
                                    status=None,
                                    login_user_name=None,
                                    terminal_ip=None,
                                    terminal_mac=None,
                                    terminal_type=None,
                                    terminal_version_number=None,
                                    login_hostname=None,
                                    filter_joined_terminal_group=0,
                                    search_word=None,
                                    offset=None,
                                    limit=20,
                                    verbose=0,
                                    reverse=0,
                                    sort_key=None,
                                    is_and=1,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_TERMINAL_MANAGEMENTS
        body = {}
        body["zone"] = zone
        if terminals:
            body['terminals'] = terminals
        if terminal_group:
            body['terminal_group'] = terminal_group
        if terminal_serial_number:
            body['terminal_serial_number'] = terminal_serial_number
        if status:
            body['status'] = status
        if login_user_name:
            body['login_user_name'] = login_user_name
        if terminal_ip:
            body['terminal_ip'] = terminal_ip
        if terminal_mac:
            body["terminal_mac"] = terminal_mac
        if terminal_type:
            body["terminal_type"] = terminal_type
        if terminal_version_number:
            body["terminal_version_number"] = terminal_version_number
        if login_hostname:
            body["login_hostname"] = login_hostname
        if filter_joined_terminal_group == 0:
            body['filter_joined_terminal_group'] = 0
        else:
            body['filter_joined_terminal_group'] = 1
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

    def modify_terminal_management_attributes(self,
                                           zone,
                                           terminals,
                                           terminal_server_ip=None,
                                           **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_TERMINAL_MANAGEMENT_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body['terminals'] = terminals
        if terminal_server_ip:
            body['terminal_server_ip'] = terminal_server_ip

        return self._build_params(action, body)

    def delete_terminal_managements(self,
                                 zone,
                                 terminals,
                                 **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_TERMINAL_MANAGEMENTS

        body = {}
        body["zone"] = zone
        body["terminals"] = terminals

        return self._build_params(action, body)

    def restart_terminals(self,
                         zone,
                         terminals,
                         **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_RESTART_TERMINALS

        body = {}
        body["zone"] = zone
        body["terminals"] = terminals

        return self._build_params(action, body)

    def stop_terminals(self,
                         zone,
                         terminals,
                         **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_STOP_TERMINALS

        body = {}
        body["zone"] = zone
        body["terminals"] = terminals

        return self._build_params(action, body)

    def describe_terminal_groups(self,
                                      zone,
                                      terminal_groups=None,
                                      terminal_group_name=None,
                                      description=None,
                                      search_word=None,
                                      offset=None,
                                      limit=20,
                                      verbose=0,
                                      reverse=0,
                                      sort_key=None,
                                      is_and=1,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_TERMINAL_GROUPS
        body = {}
        body["zone"] = zone
        if terminal_groups:
            body['terminal_groups'] = terminal_groups
        if terminal_group_name:
            body['terminal_group_name'] = terminal_group_name
        if description:
            body['description'] = description
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

    def create_terminal_group(self,
                              zone,
                              terminal_group_name,
                              description=None,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_TERMINAL_GROUP
        body = {}
        body["zone"] = zone
        body["terminal_group_name"] = terminal_group_name
        if description:
            body['description'] = description

        return self._build_params(action, body)

    def modify_terminal_group_attributes(self,
                              zone,
                              terminal_groups,
                              terminal_group_name=None,
                              description=None,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_TERMINAL_GROUP_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body["terminal_groups"] = terminal_groups
        if terminal_group_name:
            body['terminal_group_name'] = terminal_group_name
        if description:
            body['description'] = description

        return self._build_params(action, body)

    def delete_terminal_groups(self,
                              zone,
                              terminal_groups,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_TERMINAL_GROUPS
        body = {}
        body["zone"] = zone
        body["terminal_groups"] = terminal_groups

        return self._build_params(action, body)

    def add_terminal_to_terminal_group(self,
                              zone,
                              terminal_groups,
                              terminals,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_ADD_TERMINAL_TO_TERMINAL_GROUP
        body = {}
        body["zone"] = zone
        body["terminal_groups"] = terminal_groups
        body["terminals"] = terminals

        return self._build_params(action, body)

    def delete_terminal_from_terminal_group(self,
                              zone,
                              terminal_groups,
                              terminals,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_TERMINAL_FROM_TERMINAL_GROUP
        body = {}
        body["zone"] = zone
        body["terminal_groups"] = terminal_groups
        body["terminals"] = terminals

        return self._build_params(action, body)

    def describe_master_backup_ips(self,
                                      zone=None,
                                      search_word=None,
                                      offset=None,
                                      limit=20,
                                      verbose=0,
                                      reverse=0,
                                      sort_key=None,
                                      is_and=1,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_MASTER_BACKUP_IPS
        body = {}
        if zone:
            body["zone"] = zone
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

    def describe_cbserver_hosts(self,
                                      zone=None,
                                      search_word=None,
                                      offset=None,
                                      limit=20,
                                      verbose=0,
                                      reverse=0,
                                      sort_key=None,
                                      is_and=1,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_CBSERVER_HOSTS
        body = {}
        if zone:
            body["zone"] = zone
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

