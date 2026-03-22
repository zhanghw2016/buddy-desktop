import constants as const
from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import GuestRequestBuilder

class GuestRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(GuestRequestChecker, self).__init__(sender, checker)
        self.builder = GuestRequestBuilder(sender)

        self.handler_map = {
            const.ACTION_VDI_SEND_DESKTOP_MESSAGE: self.send_desktop_message,
            const.ACTION_VDI_SEND_DESKTOP_NOTIFY: self.send_desktop_notify,
            const.ACTION_VDI_SEND_DESKTOP_HOT_KEYS: self.send_desktop_hot_heys,
            const.ACTION_VDI_CHECK_DESKTOP_AGENT_STATUS: self.check_desktop_guest_agent,
            const.ACTION_VDI_LOGIN_DESKTOP: self.login_desktop,
            const.ACTION_VDI_LOGOFF_DESKTOP: self.logoff_desktop,
            const.ACTION_VDI_ADD_DESKTOP_ACTIVE_DIRECTORY: self.add_desktop_active_directory,
            const.ACTION_VDI_MODIFY_GUEST_SERVER_CONFIG: self.modify_guest_server_config,
            const.ACTION_VDI_DESCRIBE_SPICE_INFO: self.describe_spice_info,
            const.ACTION_VDI_DESCRIBE_GUEST_PROCESSES: self.describe_guest_processes,
            const.ACTION_VDI_DESCRIBE_GUEST_PROGRAMS: self.describe_guest_programs,
            const.ACTION_VDI_GUEST_JSON_RCP: self.handle_guest_json_rpc,

            # desktop maintainer
            const.ACTION_VDI_CREATE_DESKTOP_MAINTAINER: self.create_desktop_maintainer,
            const.ACTION_VDI_MODIFY_DESKTOP_MAINTAINER_ATTRIBUTES: self.modify_desktop_maintainer_attributes,
            const.ACTION_VDI_DELETE_DESKTOP_MAINTAINERS: self.delete_desktop_maintainers,
            const.ACTION_VDI_DESCRIBE_DESKTOP_MAINTAINERS: self.describe_desktop_maintainers,
            const.ACTION_VDI_GUEST_CHECK_DESKTOP_MAINTAINER: self.guest_check_desktop_maintainer,
            const.ACTION_VDI_APPLY_DESKTOP_MAINTAINER: self.apply_desktop_maintainer,
            const.ACTION_VDI_ATTACH_RESOURCE_TO_DESKTOP_MAINTAINER: self.attach_resource_to_desktop_maintainer,
            const.ACTION_VDI_DETACH_RESOURCE_FROM_DESKTOP_MAINTAINER: self.detach_resource_from_desktop_maintainer,
            const.ACTION_VDI_RUN_GUEST_SHELL_COMMAND: self.run_guest_shell_command,
            const.ACTION_VDI_DESCRIBE_GUEST_SHELL_COMMANDS: self.describe_guest_shell_commands,
            const.ACTION_VDI_GUEST_CHECK_SHELL_COMMAND: self.guest_check_shell_command,
        }

    def send_desktop_message(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['base64_message'],
                                  str_params=['base64_message'],
                                  list_params = ['desktop_ids', 'desktop_group_ids']):
            return None

        return self.builder.send_desktop_message(**directive)

    def send_desktop_notify(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['base64_notify'],
                                  str_params=['base64_notify'],
                                  list_params = ['desktop_ids', 'desktop_group_ids']):
            return None

        return self.builder.send_desktop_notify(**directive)
    
    def send_desktop_hot_heys(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['desktop_ids', 'keys'],
                                  str_params=['keys'],
                                  integer_params=['timeout', 'time_step'],
                                  list_params = ['desktop_ids']):
            return None

        return self.builder.send_desktop_hot_heys(**directive)

    def check_desktop_guest_agent(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  list_params = ['desktop_ids', 'desktop_group_ids']):
            return None

        return self.builder.check_desktop_guest_agent(**directive)


    def login_desktop(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['desktop_id', 'username', 'password'],
                                  str_params=['desktop_id', 'username', 'password']):
            return None

        return self.builder.login_desktop(**directive)

    def logoff_desktop(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['desktop_id'],
                                  str_params=['desktop_id']):
            return None

        return self.builder.login_off(**directive)

    def add_desktop_active_directory(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['org_dn'],
                                  str_params=['org_dn'],
                                  list_params = ['desktop_ids', 'desktop_group_ids']):
            return None

        return self.builder.add_desktop_active_directory(**directive)

    def modify_guest_server_config(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=['guest_server_config'],
                                  json_params=['guest_server_config'],
                                  list_params = ['desktop_ids', 'desktop_group_ids']):
            return None

        return self.builder.modify_guest_server_config(**directive)

    def describe_spice_info(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=[],
                                  integer_params=["connect_status", "limit", "offset", "verbose"],
                                  list_params=["desktop_id", "hostname", "login_user", "client_ip"],
                                  filter_params=[]):
            return None

        return self.builder.describe_spice_info(**directive)

    def describe_guest_processes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["desktop_id"],
                                  str_params=["desktop_id", "order_by"],
                                  integer_params=["top"]):
            return None

        if "order_by" in directive and directive["order_by"] not in const.GUEST_PROCESS_ORDER_BY_LIST:
            return None

        return self.builder.describe_guest_processes(**directive)

    def describe_guest_programs(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["desktop_id"],
                                  str_params=["desktop_id"]):
            return None

        return self.builder.describe_guest_programs(**directive)

    def get_guest_monitor_status(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["desktop_id"],
                                  str_params=["desktop_id"]):
            return None

        return self.builder.get_guest_monitor_status(**directive)

    def set_guest_monitor_status(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["desktop_id", "status"],
                                  str_params=["desktop_id", "status"]):
            return None
        if directive["status"] is None or directive["status"] not in const.CONST_GUEST_MONITOR_STATUS_LIST:
            return None

        return self.builder.set_guest_monitor_status(**directive)

    def handle_guest_json_rpc(self, 
                             directive,
                             json_params=['json_request']):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive):
            return None

        return self.builder.handle_guest_json_rpc(**directive)

    # desktop maintainer
    def create_desktop_maintainer(self, directive):
        if not self._check_params(directive,
                                  required_params=["zone","desktop_maintainer_name", "desktop_maintainer_type",'json_detail'],
                                  str_params=["zone","desktop_maintainer_name", "description"],
                                  list_params=["desktop_maintainer_type"],
                                  json_params=['json_detail']):
            return None
        return self.builder.create_desktop_maintainer(**directive)

    def modify_desktop_maintainer_attributes(self, directive):
        if not self._check_params(directive,
                                  required_params=["zone","desktop_maintainers"],
                                  str_params=["zone","desktop_maintainers", "desktop_maintainer_name", "description"],
                                  list_params=["desktop_maintainer_type"],
                                  json_params=['json_detail']):
            return None
        return self.builder.modify_desktop_maintainer_attributes(**directive)

    def delete_desktop_maintainers(self, directive):
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone"],
                                  list_params=["desktop_maintainers"]):
            return None
        return self.builder.delete_desktop_maintainers(**directive)

    def describe_desktop_maintainers(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone",'search_word','sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=['desktop_maintainers','desktop_maintainer_type','status'],
                                  filter_params=[]):
            return None

        return self.builder.describe_desktop_maintainers(**directive)

    def guest_check_desktop_maintainer(self, directive):
        if not self._check_params(directive,
                                  required_params=["zone","desktop_id"],
                                  str_params=["zone","desktop_id"]):
            return None
        return self.builder.guest_check_desktop_maintainer(**directive)

    def apply_desktop_maintainer(self, directive):
        if not self._check_params(directive,
                                  required_params=["zone","desktop_maintainer"],
                                  str_params=["zone","desktop_maintainer"]):
            return None
        return self.builder.apply_desktop_maintainer(**directive)

    def attach_resource_to_desktop_maintainer(self, directive):
        if not self._check_params(directive,
                                  required_params=["zone","desktop_maintainer", "resources"],
                                  list_params=["resources"],
                                  str_params=["zone","desktop_maintainer"]):
            return None
        return self.builder.attach_resource_to_desktop_maintainer(**directive)

    def detach_resource_from_desktop_maintainer(self, directive):
        if not self._check_params(directive,
                                  required_params=["zone","desktop_maintainer", "resources"],
                                  list_params=["resources"],
                                  str_params=["zone","desktop_maintainer"]):
            return None
        return self.builder.detach_resource_from_desktop_maintainer(**directive)

    def run_guest_shell_command(self, directive):
        if not self._check_params(directive,
                                  required_params=["zone","resource_id", "command"],
                                  list_params=[],
                                  str_params=["zone","resource_id","command"]):
            return None
        return self.builder.run_guest_shell_command(**directive)

    def describe_guest_shell_commands(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", 'search_word','sort_key','guest_shell_command_type'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse", "is_and"],
                                  list_params=['guest_shell_commands'],
                                  filter_params=[]):
            return None

        return self.builder.describe_guest_shell_commands(**directive)

    def guest_check_shell_command(self, directive):
        if not self._check_params(directive,
                                  required_params=["zone","desktop_id"],
                                  str_params=["zone","desktop_id"]):
            return None
        return self.builder.guest_check_shell_command(**directive)

