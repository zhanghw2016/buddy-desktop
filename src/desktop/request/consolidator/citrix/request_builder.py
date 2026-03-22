
from constants import (
    ACTION_VDI_DESCRIBE_DELIVERY_GROUPS,
    ACTION_VDI_CREATE_DELIVERY_GROUP,
    ACTION_VDI_MODIFY_DELIVERY_GROUP_ATTRIBUTES,
    ACTION_VDI_DELETE_DELIVERY_GROUPS,
    ACTION_VDI_LOAD_DELIVERY_GROUPS,
    ACTION_VDI_ADD_DESKTOP_TO_DELIVERY_GROUP,
    ACTION_VDI_DEL_DESKTOP_FROM_DELIVERY_GROUP,
    ACTION_VDI_ADD_USER_TO_DELIVERY_GROUP,
    ACTION_VDI_DEL_USER_FROM_DELIVERY_GROUP,
    ACTION_VDI_ATTACH_DESKTOP_TO_DELIVERY_GROUP_USER,
    ACTION_VDI_DETACH_DESKTOP_FROM_DELIVERY_GROUP_USER,
    ACTION_VDI_SET_DELIVERY_GROUP_MODE,
    ACTION_VDI_SET_CITRIX_DESKTOP_MODE,
    ACTION_VDI_DESCRIBE_COMPUTER_CATALOGS,
    ACTION_VDI_LOAD_COMPUTER_CATALOGS,
    ACTION_VDI_DESCRIBE_COMPUTERS,
    ACTION_VDI_LOAD_COMPUTERS,
    ACTION_VDI_REFRESH_CITRIX_DESKTOPS,
)
from request.consolidator.base.base_request_builder import BaseRequestBuilder

class CitrixRequestBuilder(BaseRequestBuilder):

    def describe_delivery_groups(self,
                                zone,
                                delivery_groups = None,
                                delivery_group_name=None,
                                delivery_group_type = None,
                                allocation_type = None,
                                is_system = None,
                                offset = None,
                                limit = None,
                                search_word = None,
                                verbose = None,
                                delivery_type=None,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DELIVERY_GROUPS
        body = {}
        body["zone"] = zone
        
        if delivery_group_name:
            body['delivery_group_name'] = delivery_group_name
        if delivery_groups:
            body['delivery_groups'] = delivery_groups
        if delivery_group_type:
            body['delivery_group_type'] = delivery_group_type
        if is_system:
            body["is_system"] = is_system
        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if verbose is not None:
            body['verbose'] = int(verbose)
        if allocation_type:
            body["allocation_type"] = allocation_type
        
        if delivery_type:
            body["delivery_type"] = delivery_type

        return self._build_params(action, body)

    def create_delivery_group(self,
                                zone,
                                delivery_group_name,
                                delivery_group_type,
                                allocation_type,
                                users=None,
                                description = None,
                                security_group=None,
                                delivery_type = None,
                                desktop_hide_mode=None,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_DELIVERY_GROUP
        body = {}
        body["zone"] = zone

        body['delivery_group_name'] = delivery_group_name.encode("utf-8")
        body['delivery_group_type'] = delivery_group_type
        body["allocation_type"] = allocation_type
        
        if users:
            body["users"] = users
        
        if description:
            body['description'] = description
        
        if security_group:
            body["security_group"] = security_group
        
        if delivery_type:
            body["delivery_type"] = delivery_type
            
        if desktop_hide_mode is not None:
            body["desktop_hide_mode"] = desktop_hide_mode

        return self._build_params(action, body)

    def modify_delivery_group_attributes(self,
                                        zone,
                                        delivery_group,
                                        delivery_group_name=None,
                                        description = None,
                                        desktop_hide_mode=None,
                                        **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DELIVERY_GROUP_ATTRIBUTES
        body = {}
        body["zone"] = zone

        body['delivery_group'] = delivery_group
        if delivery_group_name:
            body['delivery_group_name'] = delivery_group_name
    
        if description:
            body['description'] = description
        
        if desktop_hide_mode is not None:
            body['desktop_hide_mode'] = desktop_hide_mode        

        return self._build_params(action, body)

    def delete_delivery_groups(self,
                                    zone,
                                    delivery_groups,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_DELIVERY_GROUPS

        body = {}
        body["zone"] = zone
        body['delivery_groups'] = delivery_groups

        return self._build_params(action, body)

    def load_delivery_groups(self,
                                 zone,
                                 delivery_group_names,
                                 **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_LOAD_DELIVERY_GROUPS

        body = {}
        body["zone"] = zone
        body['delivery_group_names'] = delivery_group_names

        return self._build_params(action, body)

    def add_desktop_to_delivery_group(self,
                                     zone,
                                     delivery_group,
                                     desktop_user,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_ADD_DESKTOP_TO_DELIVERY_GROUP

        body = {}
        body["zone"] = zone
        body['delivery_group'] = delivery_group
        body["desktop_user"] = desktop_user

        return self._build_params(action, body)

    def del_desktop_from_delivery_group(self,
                                     zone,
                                     desktops,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DEL_DESKTOP_FROM_DELIVERY_GROUP

        body = {}
        body["zone"] = zone

        body["desktops"] = desktops

        return self._build_params(action, body)

    def add_user_to_delivery_group(self,
                                     zone,
                                     delivery_group,
                                     users,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_ADD_USER_TO_DELIVERY_GROUP

        body = {}
        body["zone"] = zone
        body['delivery_group'] = delivery_group
        body["users"] = users

        return self._build_params(action, body)

    def del_user_from_delivery_group(self,
                                     zone,
                                     delivery_group,
                                     users,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DEL_USER_FROM_DELIVERY_GROUP

        body = {}
        body["zone"] = zone
        body['delivery_group'] = delivery_group
        body["users"] = users

        return self._build_params(action, body)

    def attach_desktop_to_delivery_group_user(self,
                                     zone,
                                     desktop,
                                     user_ids=None,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_ATTACH_DESKTOP_TO_DELIVERY_GROUP_USER

        body = {}
        body["zone"] = zone
        body['desktop'] = desktop
        if user_ids:
            body["user_ids"] = user_ids

        return self._build_params(action, body)

    def detach_desktop_from_delivery_group_user(self,
                                     zone,
                                     desktop,
                                     user_ids=None,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DETACH_DESKTOP_FROM_DELIVERY_GROUP_USER

        body = {}
        body["zone"] = zone
        body['desktop'] = desktop
        if user_ids:
            body["user_ids"] = user_ids

        return self._build_params(action, body)

    def set_citrix_desktop_mode(self,
                                     zone,
                                     desktop,
                                     mode,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_SET_CITRIX_DESKTOP_MODE

        body = {}
        body["zone"] = zone
        body['desktop'] = desktop
        body['mode'] = mode

        return self._build_params(action, body)

    def set_delivery_group_mode(self,
                                     zone,
                                     delivery_group,
                                     mode,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_SET_DELIVERY_GROUP_MODE

        body = {}
        body["zone"] = zone
        body['delivery_group'] = delivery_group
        body['mode'] = mode

        return self._build_params(action, body)

    def describe_computer_catalogs(self,zone,
                                     catalog_names=None,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_COMPUTER_CATALOGS

        body = {}
        body["zone"] = zone
        body['catalog_names'] = catalog_names

        return self._build_params(action, body)

    def load_computer_catalogs(self,zone,
                                     catalog_names=None,
                                     disk_size=None,
                                     disk_name=None,
                                     managed_resource=None,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_LOAD_COMPUTER_CATALOGS

        body = {}
        body["zone"] = zone
        body['catalog_names'] = catalog_names
        if disk_size:
            body["disk_size"] = disk_size
        
        if disk_name:
            body["disk_name"] = disk_name
        
        if managed_resource:
            body["managed_resource"] = managed_resource
        
        return self._build_params(action, body)

    def describe_computers(self,zone,
                                     desktop_group=None,
                                     delivery_group=None,
                                     computers=None,
                                     offset = 0,
                                     limit = 100,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_COMPUTERS

        body = {}
        body["zone"] = zone
        if desktop_group:
            body["desktop_group"] = desktop_group
        
        if delivery_group:
            body["delivery_group"] = delivery_group
        
        if computers:
            body["computers"] = computers
        
        if offset is not None:
            body["offset"] = offset
        
        if limit is not None:
            body["limit"] = limit

        return self._build_params(action, body)

    def load_computers(self,zone,
                         desktop_group=None,
                         delivery_group=None,
                         computers=None,
                         **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_LOAD_COMPUTERS

        body = {}
        body["zone"] = zone
        if desktop_group:
            body["desktop_group"] = desktop_group
        
        if delivery_group:
            body["delivery_group"] = delivery_group
        
        if computers:
            body["computers"] = computers

        return self._build_params(action, body)

    def refresh_citrix_desktops(self, zone,
                                desktops = None,
                                desktop_group=None,
                                delivery_group=None,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_REFRESH_CITRIX_DESKTOPS

        body = {}
        body["zone"] = zone
        if desktops:
            body["desktops"] = desktops

        if desktop_group:
            body["desktop_group"] = desktop_group

        if delivery_group:
            body["delivery_group"] = delivery_group
        
        return self._build_params(action, body)

