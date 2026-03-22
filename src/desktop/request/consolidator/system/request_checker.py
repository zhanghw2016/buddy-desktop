
from constants import (
    ACTION_VDI_DESCRIBE_NOTICE_PUSHS,
    ACTION_VDI_CREATE_NOTICE_PUSH,
    ACTION_VDI_MODIFY_NOTICE_PUSH_ATTRIBUTES,
    ACTION_VDI_DELETE_NOTICE_PUSHS,
    ACTION_VDI_MODIFY_NOTICE_PUSH_ZONE_USER,
    ACTION_VDI_SET_USER_NOTICE_READ,

    # software
    ACTION_VDI_DESCRIBE_SOFTWARES,
    ACTION_VDI_UPLOAD_SOFTWARES,
    ACTION_VDI_DOWNLOAD_SOFTWARES,
    ACTION_VDI_DELETE_SOFTWARES,
    ACTION_VDI_CHECK_SOFTWARE_VNAS_NODE_DIR,
)
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import SystemRequestBuilder

class SystemRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(SystemRequestChecker, self).__init__(sender, checker)
        self.builder = SystemRequestBuilder(sender)

        self.handler_map = {
                            ACTION_VDI_DESCRIBE_NOTICE_PUSHS: self.describe_notice_pushs,
                            ACTION_VDI_CREATE_NOTICE_PUSH: self.create_notice_push,
                            ACTION_VDI_MODIFY_NOTICE_PUSH_ATTRIBUTES: self.modify_notice_push_attributes,
                            ACTION_VDI_DELETE_NOTICE_PUSHS: self.delete_notice_pushs,
                            ACTION_VDI_MODIFY_NOTICE_PUSH_ZONE_USER: self.modify_notice_push_zone_user,
                            ACTION_VDI_SET_USER_NOTICE_READ: self.set_user_notice_read,

                            ACTION_VDI_DESCRIBE_SOFTWARES: self.describe_softwares,
                            ACTION_VDI_UPLOAD_SOFTWARES: self.upload_softwares,
                            ACTION_VDI_DOWNLOAD_SOFTWARES: self.download_softwares,
                            ACTION_VDI_DELETE_SOFTWARES: self.delete_softwares,
                            ACTION_VDI_CHECK_SOFTWARE_VNAS_NODE_DIR: self.check_software_vnas_node_dir
            }

    def describe_notice_pushs(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["notices", "notice_type", "notice_level", "scope", "status"]
                                  ):
            return None

        return self.builder.describe_notice_pushs(**directive)

    def create_notice_push(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["title", "content"],
                                  str_params=["notice_type", "notice_level"],
                                  integer_params=[],
                                  time_params = ["expired_time", "execute_time"],
                                  list_params=[]
                                  ):
            return None
        if "title" in directive and not self._check_str_length(directive["title"]):
            return None
        
        return self.builder.create_notice_push(**directive)

    def modify_notice_push_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["notice"],
                                  str_params=["title", "content", "notice_level"],
                                  time_params = ["expired_time", "execute_time"],
                                  ):
            return None
        if "title" in directive and not self._check_str_length(directive["title"]):
            return None
        return self.builder.modify_notice_push_attributes(**directive)

    def delete_notice_pushs(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["notices"]
                                  ):
            return None

        return self.builder.delete_notice_pushs(**directive)

    def modify_notice_push_zone_user(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["notice", "zone_users"],
                                  str_params=["notice"],
                                  integer_params=[],
                                  list_params=[],
                                  json_params=["zone_users"]
                                  ):
            return None

        return self.builder.modify_notice_push_zone_user(**directive)

    def set_user_notice_read(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["notice", "user_id"],
                                  str_params=["notice", "user_id"],
                                  integer_params=[],
                                  list_params=[],
                                  ):
            return None

        return self.builder.set_user_notice_read(**directive)

    def describe_softwares(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", 'software_name', 'search_word','sort_key'],
                                  integer_params=['software_size', 'verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=['softwares'],
                                  filter_params=[]):
            return None

        return self.builder.describe_softwares(**directive)

    def upload_softwares(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","software_name","software_size"],
                                  str_params=["zone", 'software_name'],
                                  integer_params=['software_size','is_system_custom_logo'],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.upload_softwares(**directive)

    def download_softwares(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","softwares"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['softwares'],
                                  filter_params=[]):
            return None

        return self.builder.download_softwares(**directive)

    def delete_softwares(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","softwares"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=['softwares'],
                                  filter_params=[]):
            return None

        return self.builder.delete_softwares(**directive)

    def check_software_vnas_node_dir(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "vnas_node_dir"],
                                  str_params=["zone","vnas_node_dir"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None
        return self.builder.check_software_vnas_node_dir(**directive)
