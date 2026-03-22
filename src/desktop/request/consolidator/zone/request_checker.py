
from constants import (
    ALL_PLATFORMS,
    ACTION_VDI_DESCRIBE_DESKTOP_ZONES,
    ACTION_VDI_REFRESH_DESKTOP_ZONES,
    ACTION_VDI_CREATE_DESKTOP_ZONE,
    ACTION_VDI_MODIFY_DESKTOP_ZONE_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOP_ZONES,
    ACTION_VDI_MODIFY_DESKTOP_ZONE_RESOURCE_LIMIT,
    ACTION_VDI_MODIFY_DESKTOP_ZONE_CONNECTION,
    ACTION_VDI_MODIFY_DESKTOP_ZONE_CITRIX_CONNECTION,
    ACTION_VDI_DESCRIBE_INSTANCE_CLASS_DISK_TYPE,
    ACTION_VDI_DESCRIBE_GPU_CLASS_TYPE,
    ACTION_VDI_CHECK_NETWORK_CONNECTION,
    ACTION_VDI_CHECK_GPU_CONFIG
)
from log.logger import logger
import error.error_msg as ErrorMsg
from request.consolidator.base.base_request_checker import BaseRequestChecker
from .request_builder import ZoneRequestBuilder

class ZoneRequestChecker(BaseRequestChecker):
    
    handler_map = {}
    def __init__(self, checker, sender):
        super(ZoneRequestChecker, self).__init__(sender, checker)
        self.builder = ZoneRequestBuilder(sender)

        self.handler_map = {
                            ACTION_VDI_DESCRIBE_DESKTOP_ZONES: self.describe_desktop_zones,
                            ACTION_VDI_REFRESH_DESKTOP_ZONES: self.refresh_desktop_zones,
                            ACTION_VDI_CREATE_DESKTOP_ZONE: self.create_desktop_zone,
                            ACTION_VDI_MODIFY_DESKTOP_ZONE_ATTRIBUTES: self.modify_desktop_zone_attributes,
                            ACTION_VDI_DELETE_DESKTOP_ZONES: self.delete_desktop_zones,
                            ACTION_VDI_MODIFY_DESKTOP_ZONE_RESOURCE_LIMIT: self.modify_desktop_zone_resource_limit,
                            ACTION_VDI_MODIFY_DESKTOP_ZONE_CONNECTION: self.modify_desktop_zone_connection,
                            ACTION_VDI_MODIFY_DESKTOP_ZONE_CITRIX_CONNECTION: self.modify_desktop_zone_citrix_connection,
                            ACTION_VDI_DESCRIBE_INSTANCE_CLASS_DISK_TYPE: self.describe_instance_class_disk_type,
                            ACTION_VDI_DESCRIBE_GPU_CLASS_TYPE: self.describe_gpu_class_type,
                            ACTION_VDI_CHECK_NETWORK_CONNECTION: self.check_network_connection,
                            ACTION_VDI_CHECK_GPU_CONFIG: self.check_gpu_config
            }

    def _check_platform_type(self, platform):

        if platform not in ALL_PLATFORMS:
            logger.error("illegal zone platform type [%s]" % (platform))
            self.set_error(ErrorMsg.ERR_MSG_ZONE_PLATFORM_INVAILD, platform)
            return False

        return True

    def describe_desktop_zones(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["zones", "platform","status"]
                                  ):
            return None

        return self.builder.describe_desktop_zones(**directive)

    def refresh_desktop_zones(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["search_word", "sort_key"],
                                  integer_params=["limit", "offset", "verbose", "reverse"],
                                  list_params=["zones", "platform","status"]
                                  ):
            return None

        return self.builder.refresh_desktop_zones(**directive)

    def create_desktop_zone(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone_id"],
                                  str_params=["zone_id", "description", "platform", "zone_name", "platform"],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return None
        
        if "platform" in directive and not self._check_platform_type(directive["platform"]):
            return None

        return self.builder.create_desktop_zone(**directive)

    def modify_desktop_zone_attributes(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone_id"],
                                  str_params=["zone_id", "zone_name", "description"],
                                  integer_params=[]):
            return None

        return self.builder.modify_desktop_zone_attributes(**directive)

    def delete_desktop_zones(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zones"]
                                  ):
            return None

        return self.builder.delete_desktop_zones(**directive)

    def modify_desktop_zone_resource_limit(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone_id"],
                                  str_params=["zone_id", "default_passwd", "ivshmem","router"],
                                  integer_params=["supported_gpu", "max_disk_count","max_gpu_count"],
                                  list_params=["instance_class", "disk_size", "cpu_cores", "memory_size", "place_group", "gpu_class_key"]
                                  ):
            return None

        return self.builder.modify_desktop_zone_resource_limit(**directive)

    def modify_desktop_zone_connection(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone_id"],
                                  str_params=["zone_id", "host", "protocol", "account_user_id", "base_zone_id", 
                                              "zone_access_key_id", "zone_secret_access_key", "host_ip"],
                                  integer_params=["port", "http_socket_timeout"],
                                  ):
            return None

        return self.builder.modify_desktop_zone_connection(**directive)

    def modify_desktop_zone_citrix_connection(self, directive):
        '''
            @param directive : the dictionary of params
        '''

        if not self._check_params(directive,
                                  required_params=["zone_id"],
                                  str_params=["zone_id", "host", "protocol"],
                                  integer_params=["port", "http_socket_timeout","support_netscaler","support_citrix_pms","storefront_port","netscaler_port"],
                                  list_params=["managed_resource"],
                                  json_params=["storefront_uri","netscaler_uri"]
                                  ):
            return None

        return self.builder.modify_desktop_zone_citrix_connection(**directive)

    def describe_instance_class_disk_type(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["search_word", "sort_key"],
                                  integer_params=["instance_class","disk_type","limit", "offset", "verbose", "reverse"],
                                  list_params=[]
                                  ):
            return None

        return self.builder.describe_instance_class_disk_type(**directive)

    def describe_gpu_class_type(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["search_word", "sort_key","gpu_class_key"],
                                  integer_params=["gpu_class","limit", "offset", "verbose", "reverse"],
                                  list_params=[]
                                  ):
            return None

        return self.builder.describe_gpu_class_type(**directive)

    def check_network_connection(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=[],
                                  str_params=["ip_addr"],
                                  integer_params=["port"],
                                  list_params=[]
                                  ):
            return None

        return self.builder.check_network_connection(**directive)

    def check_gpu_config(self, directive):
        '''
            @param directive : the dictionary of params
        '''
        if not self._check_params(directive,
                                  required_params=["zone_id"],
                                  str_params=[],
                                  integer_params=[],
                                  list_params=[]
                                  ):
            return None

        return self.builder.check_gpu_config(**directive)
