
from constants import (
    ALL_PLATFORMS,

    # desktop_service_management
    ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_MANAGEMENTS,
    ACTION_VDI_MODIFY_DESKTOP_SERVICE_MANAGEMENT_ATTRIBUTES,
    ACTION_VDI_REFRESH_DESKTOP_SERVICE_MANAGEMENT,
    ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_INSTANCES,
    ACTION_VDI_LOAD_DESKTOP_SERVICE_INSTANCES,
    ACTION_VDI_REMOVE_DESKTOP_SERVICE_INSTANCES
)
from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import DesktopServiceManagementRequestBuilder

class DesktopServiceManagementRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(DesktopServiceManagementRequestChecker, self).__init__(sender, checker)
        self.builder = DesktopServiceManagementRequestBuilder(sender)

        self.handler_map = {
                            ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_MANAGEMENTS: self.describe_desktop_service_managements,
                            ACTION_VDI_MODIFY_DESKTOP_SERVICE_MANAGEMENT_ATTRIBUTES: self.modify_desktop_service_management_attributes,
                            ACTION_VDI_REFRESH_DESKTOP_SERVICE_MANAGEMENT: self.refresh_deskop_service_management,
                            ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_INSTANCES: self.describe_desktop_service_instances,
                            ACTION_VDI_LOAD_DESKTOP_SERVICE_INSTANCES: self.load_desktop_service_instances,
                            ACTION_VDI_REMOVE_DESKTOP_SERVICE_INSTANCES: self.remove_desktop_service_instances
        }

    def describe_desktop_service_managements(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=['zone','service_management_type','service_type''sort_key'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.describe_desktop_service_managements(**directive)

    def modify_desktop_service_management_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "services","service_name"],
                                  str_params=["zone","services","service_name","description"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.modify_desktop_service_management_attributes(**directive)

    def refresh_deskop_service_management(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.refresh_deskop_service_management(**directive)

    def describe_desktop_service_instances(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=['zone','sort_key','search_word'],
                                  integer_params=['verbose', 'offset', 'limit', "reverse","is_and"],
                                  list_params=[],
                                  filter_params=[]):
            return None

        return self.builder.describe_desktop_service_instances(**directive)

    def load_desktop_service_instances(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["instances","service_type","service_management_type"],
                                  str_params=['zone',"service_type","service_management_type"],
                                  integer_params=[],
                                  list_params=["instances"],
                                  filter_params=[]):
            return None

        return self.builder.load_desktop_service_instances(**directive)

    def remove_desktop_service_instances(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["instances","service_type"],
                                  str_params=['zone',"service_type"],
                                  integer_params=[],
                                  list_params=["instances"],
                                  filter_params=[]):
            return None

        return self.builder.remove_desktop_service_instances(**directive)

