
from constants import (

    # desktop_service_management
    ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_MANAGEMENTS,
    ACTION_VDI_MODIFY_DESKTOP_SERVICE_MANAGEMENT_ATTRIBUTES,
    ACTION_VDI_REFRESH_DESKTOP_SERVICE_MANAGEMENT,
    ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_INSTANCES,
    ACTION_VDI_LOAD_DESKTOP_SERVICE_INSTANCES,
    ACTION_VDI_REMOVE_DESKTOP_SERVICE_INSTANCES
)
from request.consolidator.base.base_request_builder import BaseRequestBuilder
from log.logger import logger

class DesktopServiceManagementRequestBuilder(BaseRequestBuilder):

    def describe_desktop_service_managements(self,
                                zone=None,
                                service_management_type=None,
                                service_type=None,
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
        action = ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_MANAGEMENTS
        body = {}
        if zone:
            body['zone'] = zone
        if service_management_type:
            body['service_management_type'] = service_management_type
        if service_type:
            body['service_type'] = service_type
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

    def modify_desktop_service_management_attributes(self,
                              zone,
                              services,
                              service_name,
                              description=None,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_SERVICE_MANAGEMENT_ATTRIBUTES

        body = {}
        body["zone"] = zone
        body["services"] = services
        body["service_name"] = service_name
        if description:
            body['description'] = description

        return self._build_params(action, body)

    def refresh_deskop_service_management(self,
                              zone,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_REFRESH_DESKTOP_SERVICE_MANAGEMENT

        body = {}
        body["zone"] = zone

        return self._build_params(action, body)

    def describe_desktop_service_instances(self,
                               zone,
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
        action = ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_INSTANCES

        body = {}
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

    def load_desktop_service_instances(self,
                              zone,
                              service_type,
                              instances,
                              service_management_type,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_LOAD_DESKTOP_SERVICE_INSTANCES

        body = {}
        body["zone"] = zone
        body["service_type"] = service_type
        body["instances"] = instances
        body["service_management_type"] = service_management_type

        return self._build_params(action, body)

    def remove_desktop_service_instances(self,
                              zone,
                              service_type,
                              instances,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_REMOVE_DESKTOP_SERVICE_INSTANCES

        body = {}
        body["zone"] = zone
        body["service_type"] = service_type
        body["instances"] = instances

        return self._build_params(action, body)






