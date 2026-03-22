
import constants as const
from utils.json import json_load

class ZoneInfo():
    
    def __init__(self, ctx, zone):
        
        self.ctx = ctx
        self.zone_id = zone["zone_id"]
        self.platform = zone["platform"]
        self.status = zone["status"]
        self.connection = {}
        self.citrix_connection = {}
        self.desktop_connection = {}
        self.resource_limit = {}
        self.user_id = None
        self.base_zone = None
        self.citrix = {}
   
    def update_zone_connection(self):

        conn_key = ["access_key_id", "secret_access_key", "host",
                         "port", "protocol", "http_socket_timeout"]

        zone_connection = self.ctx.pgm.get_zone_connection(self.zone_id)
        if not zone_connection:
            self.connection = {}
            return -1
        
        for key in conn_key:
            if key not in zone_connection:
                return -1
            self.connection[key] = zone_connection[key]
        
        self.base_zone = zone_connection["base_zone_id"]
        self.user_id = zone_connection["account_user_id"]

        return 0
    
    def update_zone_citrix_connnetion(self):
        
        conn_key = ["host", "port", "protocol", "http_socket_timeout"]
        citrix_key = ["managed_resource", "storefront_uri", "storefront_port","netscaler_uri","netscaler_port","support_netscaler"]
        
        zone_citrix_connection = self.ctx.pgm.get_zone_citrix_connection(self.zone_id)
        if not zone_citrix_connection:
            self.citrix_connection = {}
            return -1
        
        for key in conn_key:
            if key not in zone_citrix_connection:
                return -1
            self.citrix_connection[key] = zone_citrix_connection[key]

        self.citrix_connection["access_key_id"] = const.DESKTOP_ACCESS_KEY_ID
        self.citrix_connection["secret_access_key"] = const.DESKTOP_SECRET_ACCESS_KEY

        for key in citrix_key:
            if key not in zone_citrix_connection:
                return -1
            self.citrix_connection[key] = zone_citrix_connection[key]
        
        return 0

    def update_zone_resource_limit(self):
        
        resource_limit = self.ctx.pgm.get_zone_resource_limit(self.zone_id)
        if not resource_limit:
            self.resource_limit = {}
            return -1
        
        self.resource_limit["instance_class"] = json_load(resource_limit["instance_class"])
        self.resource_limit["disk_size"] = json_load(resource_limit["disk_size"])
        self.resource_limit["cpu_cores"] = json_load(resource_limit["cpu_cores"])
        self.resource_limit["memory_size"] = json_load(resource_limit["memory_size"])
        self.resource_limit["cpu_memory_pairs"] = json_load(resource_limit["cpu_memory_pairs"])
        self.resource_limit["supported_gpu"] = resource_limit["supported_gpu"]
        self.resource_limit["place_group"] = json_load(resource_limit["place_group"])
        self.resource_limit["max_disk_count"] = resource_limit["max_disk_count"]
        self.resource_limit["default_passwd"] = resource_limit["default_passwd"]
        self.resource_limit["ivshmem"] = resource_limit["ivshmem"]
        self.resource_limit["network_type"] = json_load(resource_limit["network_type"])
        self.resource_limit["max_chain_count"] = resource_limit["max_chain_count"]
        self.resource_limit["max_snapshot_count"] = resource_limit["max_snapshot_count"]
        
        if self.platform == const.PLATFORM_TYPE_CITRIX:
            managed_resource = self.citrix_connection["managed_resource"]
            self.resource_limit["managed_resource"] = json_load(managed_resource)
        return 0

    def update_zone_desktop_connnetion(self):
       
        self.desktop_connection["host"] = const.LOCALHOST
        self.desktop_connection["port"] = 7776
        self.desktop_connection["protocol"] = "http"
        self.desktop_connection["access_key_id"] = const.DESKTOP_ACCESS_KEY_ID
        self.desktop_connection["secret_access_key"] = const.DESKTOP_SECRET_ACCESS_KEY

        return 0

    def build_zone_info(self):

        ret = self.update_zone_connection()
        if ret < 0:
            return -1
        
        if self.platform == const.PLATFORM_TYPE_CITRIX:
            ret = self.update_zone_citrix_connnetion()
            if ret < 0:
                return -1
        
        ret = self.update_zone_resource_limit()
        if ret < 0:
            return -1
        
        self.update_zone_desktop_connnetion()
        
        return 0
