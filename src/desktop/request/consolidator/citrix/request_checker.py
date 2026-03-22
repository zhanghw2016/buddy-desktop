
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

from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import CitrixRequestBuilder

class CitrixRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(CitrixRequestChecker, self).__init__(sender, checker)
        self.builder = CitrixRequestBuilder(sender)

        self.handler_map = {
                        ACTION_VDI_DESCRIBE_DELIVERY_GROUPS: self.describe_delivery_groups,
                        ACTION_VDI_CREATE_DELIVERY_GROUP: self.create_delivery_group,
                        ACTION_VDI_MODIFY_DELIVERY_GROUP_ATTRIBUTES: self.modify_delivery_group_attributes,
                        ACTION_VDI_DELETE_DELIVERY_GROUPS: self.delete_delivery_groups,
                        ACTION_VDI_LOAD_DELIVERY_GROUPS: self.load_delivery_groups,
                        ACTION_VDI_ADD_DESKTOP_TO_DELIVERY_GROUP: self.add_desktop_to_delivery_group,
                        ACTION_VDI_DEL_DESKTOP_FROM_DELIVERY_GROUP: self.del_desktop_from_delivery_group,
                        ACTION_VDI_ADD_USER_TO_DELIVERY_GROUP: self.add_user_to_delivery_group,
                        ACTION_VDI_DEL_USER_FROM_DELIVERY_GROUP: self.del_user_from_delivery_group,
                        ACTION_VDI_ATTACH_DESKTOP_TO_DELIVERY_GROUP_USER: self.attach_desktop_to_delivery_group_user,
                        ACTION_VDI_DETACH_DESKTOP_FROM_DELIVERY_GROUP_USER: self.detach_desktop_from_delivery_group_user,
                        ACTION_VDI_SET_DELIVERY_GROUP_MODE: self.set_delivery_group_mode,
                        ACTION_VDI_SET_CITRIX_DESKTOP_MODE: self.set_citrix_desktop_mode,
                        ACTION_VDI_DESCRIBE_COMPUTER_CATALOGS: self.describe_computer_catalogs,
                        ACTION_VDI_LOAD_COMPUTER_CATALOGS: self.load_computer_catalogs,
                        ACTION_VDI_DESCRIBE_COMPUTERS: self.describe_computers,
                        ACTION_VDI_LOAD_COMPUTERS: self.load_computers,
                        ACTION_VDI_REFRESH_CITRIX_DESKTOPS: self.refresh_citrix_desktops,

            }

    def describe_delivery_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "delivery_group_name", "search_word"],
                                  integer_params=["limit", "offset", "is_system", "verbose"],
                                  list_params=["delivery_groups", "delivery_group_type", "allocation_type", "delivery_type"],
                                  filter_params=[]):
            return None
        
        return self.builder.describe_delivery_groups(**directive)
    
    def create_delivery_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "delivery_group_name", "delivery_group_type", "allocation_type"],
                                  str_params=["zone", "delivery_group_name", "delivery_group_type", "description", "allocation_type", "security_group", 
                                              "delivery_type","desktop_hide_mode"],
                                  integer_params=["desktop_hide_mode"],
                                  list_params=["users"],
                                  filter_params=[]):
            return None
        
        if not self._check_delivery_group_type(directive["delivery_group_type"]):
            return None
        
        if not self._check_allocation_type_type(directive["allocation_type"]):
            return None
        
        if directive.get("delivery_type") and not self._check_delivery_type(directive["delivery_type"]):
            return None
        
        if directive.get("desktop_hide_mode") and not self._check_hide_desktop_type(directive["desktop_hide_mode"]):
            return None
        
        return self.builder.create_delivery_group(**directive)

    def modify_delivery_group_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "delivery_group"],
                                  str_params=["zone", "delivery_group_name", "description","desktop_hide_mode"],
                                  integer_params=['desktop_hide_mode'],
                                  list_params=[],
                                  filter_params=[]):
            return None

        if directive.get("desktop_hide_mode") and not self._check_hide_desktop_type(directive["desktop_hide_mode"]):
            return None

        return self.builder.modify_delivery_group_attributes(**directive)

    def delete_delivery_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "delivery_groups"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["delivery_groups"],
                                  filter_params=[]):
            return None
        
        return self.builder.delete_delivery_groups(**directive)
    
    def load_delivery_groups(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "delivery_group_names"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["delivery_group_names"],
                                  filter_params=[]):
            return None
        
        return self.builder.load_delivery_groups(**directive)

    def add_desktop_to_delivery_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "delivery_group", "desktop_user"],
                                  str_params=["zone", "delivery_group"],
                                  integer_params=[],
                                  list_params=["desktop_user"],
                                  filter_params=[]):
            return None
        
        return self.builder.add_desktop_to_delivery_group(**directive)
    
    def del_desktop_from_delivery_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "desktops"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["desktops"],
                                  filter_params=[]):
            return None
        
        return self.builder.del_desktop_from_delivery_group(**directive)

    def add_user_to_delivery_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "delivery_group", "users"],
                                  str_params=["zone", "delivery_group"],
                                  integer_params=[],
                                  list_params=["users"],
                                  filter_params=[]):
            return None
        
        return self.builder.add_user_to_delivery_group(**directive)
    
    def del_user_from_delivery_group(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "delivery_group", "users"],
                                  str_params=["zone", "delivery_group"],
                                  integer_params=[],
                                  list_params=["users"],
                                  filter_params=[]):
            return None
        
        return self.builder.del_user_from_delivery_group(**directive)

    def attach_desktop_to_delivery_group_user(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "desktop"],
                                  str_params=["zone", "desktop"],
                                  integer_params=[],
                                  list_params=["user_ids"],
                                  filter_params=[]):
            return None
        
        return self.builder.attach_desktop_to_delivery_group_user(**directive)
    
    def detach_desktop_from_delivery_group_user(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "desktop"],
                                  str_params=["zone", "desktop"],
                                  integer_params=[],
                                  list_params=["user_ids"],
                                  filter_params=[]):
            return None
        
        return self.builder.detach_desktop_from_delivery_group_user(**directive)

    def set_delivery_group_mode(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "delivery_group", "mode"],
                                  str_params=["zone", "delivery_group", "mode"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None
        
        return self.builder.set_delivery_group_mode(**directive)

    def set_citrix_desktop_mode(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone", "desktop", "mode"],
                                  str_params=["zone", "desktop", "mode"],
                                  integer_params=[],
                                  list_params=[],
                                  filter_params=[]):
            return None
        
        return self.builder.set_citrix_desktop_mode(**directive)

    def describe_computer_catalogs(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone"],
                                  integer_params=[],
                                  list_params=["catalog_names"],
                                  filter_params=[]):
            return None
        
        return self.builder.describe_computer_catalogs(**directive)

    def load_computer_catalogs(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "disk_name", "managed_resource"],
                                  integer_params=["disk_size"],
                                  list_params=["catalog_names"],
                                  filter_params=[]):
            return None
        
        return self.builder.load_computer_catalogs(**directive)

    def describe_computers(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "desktop_group", "delivery_group"],
                                  integer_params=["offset", "limit"],
                                  list_params=["computers"],
                                  filter_params=[]):
            return None
        
        return self.builder.describe_computers(**directive)

    def load_computers(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "desktop_group", "delivery_group"],
                                  integer_params=[],
                                  list_params=["computers"],
                                  filter_params=[]):
            return None
        
        return self.builder.load_computers(**directive)

    def refresh_citrix_desktops(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone"],
                                  str_params=["zone", "desktop_group", "delivery_group"],
                                  integer_params=[],
                                  list_params=["desktops"],
                                  filter_params=[]):
            return None
        
        return self.builder.refresh_citrix_desktops(**directive)
