
from constants import (
    ALL_PLATFORMS,

    # component upgrade
    ACTION_VDI_DESCRIBE_COMPONENT_VERSION,
    ACTION_VDI_UPDATE_COMPONENT_VERSION,
    ACTION_VDI_EXECUTE_COMPONENT_UPGRADE
)
from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import ComponentVersionRequestBuilder

class ComponentVersionRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(ComponentVersionRequestChecker, self).__init__(sender, checker)
        self.builder = ComponentVersionRequestBuilder(sender)

        self.handler_map = {
                    ACTION_VDI_DESCRIBE_COMPONENT_VERSION: self.describe_component_version,
                    ACTION_VDI_UPDATE_COMPONENT_VERSION: self.update_component_version,
                    ACTION_VDI_EXECUTE_COMPONENT_UPGRADE: self.execute_component_upgrade
        }

    def describe_component_version(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["component_name"],
                                  list_params=['components']
                                  ):
            return None

        return self.builder.describe_component_version(**directive)

    def update_component_version(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone","component_id", "component_name", "version", "filename",
                                                   "upgrade_packet_md5", "upgrade_packet_size"],
                                  integer_params=["upgrade_packet_size"],
                                  str_params=["component_id", "component_name", "component_type", "version", "filename",
                                              "description", "upgrade_packet_md5"]):
            return None

        return self.builder.update_component_version(**directive)

    def execute_component_upgrade(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["component_id"],
                                  list_params=['upgrade_hosts']
                                  ):
            return None

        return self.builder.execute_component_upgrade(**directive)
