
from constants import (

    # component upgrade
    ACTION_VDI_DESCRIBE_COMPONENT_VERSION,
    ACTION_VDI_UPDATE_COMPONENT_VERSION,
    ACTION_VDI_EXECUTE_COMPONENT_UPGRADE

)
from request.consolidator.base.base_request_builder import BaseRequestBuilder
from log.logger import logger

class ComponentVersionRequestBuilder(BaseRequestBuilder):

    def describe_component_version(self,
                                   zone,
                                   components=None,
                                   component_name=None,
                                   **params):
        action = ACTION_VDI_DESCRIBE_COMPONENT_VERSION
        body = {}
        body["zone"] = zone
        if components:
            body["components"] = components
        if component_name:
            body["component_name"] = component_name
        return self._build_params(action, body)

    def update_component_version(self,
                                 zone,
                                 component_id=None,
                                 component_name=None,
                                 component_type=None,
                                 version=None,
                                 filename=None,
                                 description=None,
                                 upgrade_packet_md5=None,
                                 upgrade_packet_size=None,
                                 **params):
        action = ACTION_VDI_UPDATE_COMPONENT_VERSION
        body = {}
        body["zone"] = zone
        if component_id:
            body["component_id"] = component_id
        if component_name:
            body["component_name"] = component_name
        if component_type:
            body["component_type"] = component_type
        if version:
            body["version"] = version
        if filename:
            body["filename"] = filename
        if description:
            body["description"] = description
        if upgrade_packet_md5:
            body["upgrade_packet_md5"] = upgrade_packet_md5
        if upgrade_packet_size:
            body["upgrade_packet_size"] = upgrade_packet_size

        return self._build_params(action, body)

    def execute_component_upgrade(self,
                                  zone,
                                  component_id,
                                  upgrade_hosts=None,
                                  **params):
        action = ACTION_VDI_EXECUTE_COMPONENT_UPGRADE
        body = {}
        body["zone"] = zone
        body["component_id"] = component_id
        if upgrade_hosts:
            body["upgrade_hosts"] = upgrade_hosts

        return self._build_params(action, body)



