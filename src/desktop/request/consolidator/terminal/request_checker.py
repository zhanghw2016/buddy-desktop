
from constants import (
    ALL_PLATFORMS,

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
from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import TerminalRequestBuilder

class TerminalRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(TerminalRequestChecker, self).__init__(sender, checker)
        self.builder = TerminalRequestBuilder(sender)

        self.handler_map = {
                            ACTION_VDI_DESCRIBE_TERMINAL_MANAGEMENTS: self.describe_terminal_managements,
                            ACTION_VDI_MODIFY_TERMINAL_MANAGEMENT_ATTRIBUTES: self.modify_terminal_management_attributes,
                            ACTION_VDI_DELETE_TERMINAL_MANAGEMENTS: self.delete_terminal_managements,
                            ACTION_VDI_RESTART_TERMINALS: self.restart_terminals,
                            ACTION_VDI_STOP_TERMINALS: self.stop_terminals,

                            ACTION_VDI_DESCRIBE_TERMINAL_GROUPS: self.describe_terminal_groups,
                            ACTION_VDI_CREATE_TERMINAL_GROUP: self.create_terminal_group,
                            ACTION_VDI_MODIFY_TERMINAL_GROUP_ATTRIBUTES: self.modify_terminal_group_attributes,
                            ACTION_VDI_DELETE_TERMINAL_GROUPS: self.delete_terminal_groups,
                            ACTION_VDI_ADD_TERMINAL_TO_TERMINAL_GROUP: self.add_terminal_to_terminal_group,
                            ACTION_VDI_DELETE_TERMINAL_FROM_TERMINAL_GROUP: self.delete_terminal_from_terminal_group,

                            ACTION_VDI_DESCRIBE_MASTER_BACKUP_IPS: self.describe_master_backup_ips,
                            ACTION_VDI_DESCRIBE_CBSERVER_HOSTS: self.describe_cbserver_hosts,

            }

    def describe_terminal_managements(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", 'terminal_group','terminal_serial_number', 'login_user_name', 'terminal_ip', 'terminal_mac','terminal_version_number','login_hostname','search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and","filter_joined_terminal_group"],
                                  list_params=['terminals', 'status','terminal_type'],
                                  filter_params=[]):
            return None

        return self.builder.describe_terminal_managements(**directive)

    def modify_terminal_management_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "terminals"],
                                  str_params=["zone", 'terminal_server_ip'],
                                  integer_params=[],
                                  list_params=['terminals'],
                                  filter_params=[]):
            return None

        return self.builder.modify_terminal_management_attributes(**directive)

    def delete_terminal_managements(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","terminals"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["terminals"],
                                  filter_params=[]):
            return None

        return self.builder.delete_terminal_managements(**directive)

    def restart_terminals(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","terminals"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["terminals"],
                                  filter_params=[]):
            return None

        return self.builder.restart_terminals(**directive)

    def stop_terminals(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","terminals"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["terminals"],
                                  filter_params=[]):
            return None

        return self.builder.stop_terminals(**directive)

    def describe_terminal_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", 'terminal_group_name','search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=['terminal_groups'],
                                  filter_params=[]):
            return None

        return self.builder.describe_terminal_groups(**directive)

    def create_terminal_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","terminal_group_name"],
                                  str_params=["zone", 'terminal_group_name', 'description'],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.create_terminal_group(**directive)

    def modify_terminal_group_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "terminal_groups"],
                                  str_params=["zone", 'terminal_groups','terminal_group_name', 'description'],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.modify_terminal_group_attributes(**directive)

    def delete_terminal_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","terminal_groups"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["terminal_groups"],
                                  filter_params=[]):
            return None

        return self.builder.delete_terminal_groups(**directive)

    def add_terminal_to_terminal_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", 'terminal_groups', 'terminals'],
                                  str_params=["zone","terminal_groups"],
                                  integer_params=[],
                                  list_params=["terminals"],
                                  filter_params=[]):
            return None

        return self.builder.add_terminal_to_terminal_group(**directive)

    def delete_terminal_from_terminal_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", 'terminal_groups', 'terminals'],
                                  str_params=["zone","terminal_groups"],
                                  integer_params=[],
                                  list_params=["terminals"],
                                  filter_params=[]):
            return None

        return self.builder.delete_terminal_from_terminal_group(**directive)

    def describe_master_backup_ips(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["zone", 'search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.describe_master_backup_ips(**directive)

    def describe_cbserver_hosts(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["zone", 'search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.describe_cbserver_hosts(**directive)




