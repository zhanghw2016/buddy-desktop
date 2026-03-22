
from constants import (
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
from request.consolidator.base.base_request_builder import BaseRequestBuilder

class ZoneRequestBuilder(BaseRequestBuilder):

    def describe_desktop_zones(self, 
                               zones = None,
                               platform=None,
                               reverse = None,
                               sort_key = None,
                               offset = 0,
                               limit = 20,
                               search_word = None,
                               verbose = 0,
                               status = None,
                               **params
                               ):

        action = ACTION_VDI_DESCRIBE_DESKTOP_ZONES
        body = {}
        
        if zones:
            body["zones"] = zones
        
        if platform:
            body["platform"] = platform

        if reverse:
            body["reverse"] = reverse
        
        if sort_key:
            body["sort_key"] = sort_key
        
        if offset is not None:
            body["offset"] = offset

        if limit:
            body["limit"] = limit

        if search_word:
            body["search_word"] = search_word
        
        if verbose is not None:
            body["verbose"] = verbose

        if status:
            body["status"] = status
         
        return self._build_params(action, body)

    def refresh_desktop_zones(self,
                               zones=None,
                               platform=None,
                               reverse=None,
                               sort_key=None,
                               offset=0,
                               limit=20,
                               search_word=None,
                               verbose=0,
                               status=None,
                               **params
                               ):

        action = ACTION_VDI_REFRESH_DESKTOP_ZONES
        body = {}

        if zones:
            body["zones"] = zones

        if platform:
            body["platform"] = platform

        if reverse:
            body["reverse"] = reverse

        if sort_key:
            body["sort_key"] = sort_key

        if offset is not None:
            body["offset"] = offset

        if limit:
            body["limit"] = limit

        if search_word:
            body["search_word"] = search_word

        if verbose is not None:
            body["verbose"] = verbose

        if status:
            body["status"] = status

        return self._build_params(action, body)

    def create_desktop_zone(self,
                            zone_id,
                            platform=None,
                            zone_name=None,
                            description=None,
                            **params
                            ):

        action = ACTION_VDI_CREATE_DESKTOP_ZONE
        body = {"zone_id": zone_id}
        if platform:
            body["platform"] = platform

        if zone_name:
            body["zone_name"] = zone_name
        if description:
            body["description"] = description

        return self._build_params(action, body)

    def modify_desktop_zone_attributes(self,
                                       zone_id,
                                       zone_name=None,
                                       description=None,
                                       **params):

        action = ACTION_VDI_MODIFY_DESKTOP_ZONE_ATTRIBUTES
        body = {"zone_id": zone_id}
        if zone_name:
            body["zone_name"] = zone_name
        if description is not None:
            body["description"] = description
     
        return self._build_params(action, body)
    
    def delete_desktop_zones(self,
                             zones,
                             **params
                             ):

        action = ACTION_VDI_DELETE_DESKTOP_ZONES
        body = {"zones": zones}
        return self._build_params(action, body)

    def modify_desktop_zone_resource_limit(self,
                                  zone_id,
                                  instance_class=None,
                                  disk_size=None,
                                  cpu_cores=None,
                                  memory_size=None,
                                  cpu_memory_pairs=None,
                                  supported_gpu=None,
                                  place_group=None,
                                  max_disk_count=None,
                                  default_passwd=None,
                                  network_type=None,
                                  ivshmem=None,
                                  max_snapshot_count=None,
                                  max_chain_count=None,
                                  router=None,
                                  gpu_class_key=None,
                                  max_gpu_count=None,
                                  **params
                                  ):

        action = ACTION_VDI_MODIFY_DESKTOP_ZONE_RESOURCE_LIMIT
        body = {"zone_id": zone_id}
        if instance_class:
            body["instance_class"] = instance_class
        
        if disk_size:
            body["disk_size"] = disk_size
        
        if cpu_cores:
            body["cpu_cores"] = cpu_cores
        
        if memory_size:
            body["memory_size"] = memory_size
        
        if cpu_memory_pairs:
            body["cpu_memory_pairs"] = cpu_memory_pairs
        
        if supported_gpu is not None:
            body["supported_gpu"] = supported_gpu

        if place_group is not None:
            body["place_group"] = place_group
        
        if max_disk_count is not None:
            body["max_disk_count"] = max_disk_count
        
        if default_passwd:
            body["default_passwd"] = default_passwd
        
        if network_type:
            body["network_type"] = network_type
        
        if ivshmem is not None:
            body["ivshmem"] = ivshmem

        if max_snapshot_count is not None:
            body["max_snapshot_count"] = max_snapshot_count

        if max_chain_count is not None:
            body["max_chain_count"] = max_chain_count

        if router:
            body["router"] = router

        if gpu_class_key:
            body["gpu_class_key"] = gpu_class_key

        if max_gpu_count is not None:
            body["max_gpu_count"] = max_gpu_count
        
        return self._build_params(action, body)

    def modify_desktop_zone_connection(self, 
                                           zone_id,
                                           base_zone_id,
                                           account_user_id,
                                           zone_access_key_id,
                                           zone_secret_access_key,
                                           host,
                                           host_ip=None,
                                           port=80,
                                           protocol='http',
                                           http_socket_timeout= 120,
                                           **params
                                           ):

        action = ACTION_VDI_MODIFY_DESKTOP_ZONE_CONNECTION
        body = {"zone_id": zone_id}
        body["base_zone_id"] = base_zone_id
        body["account_user_id"] = account_user_id
        body["zone_access_key_id"] = zone_access_key_id
        body["zone_secret_access_key"] = zone_secret_access_key
        body["host"] = host
        if host_ip is not None:
            body["host_ip"] = host_ip
        body["port"] = port
        body["protocol"] = protocol
        body["http_socket_timeout"] = http_socket_timeout
        
        return self._build_params(action, body)

    def modify_desktop_zone_citrix_connection(self, 
                                               zone_id,
                                               host,
                                               managed_resource,
                                               storefront_uri=None,
                                               netscaler_uri=None,
                                               http_socket_timeout=120,
                                               port = 10080,
                                               storefront_port=None,
                                               netscaler_port=None,
                                               protocol = "http",
                                               support_netscaler=None,
                                               support_citrix_pms=None,
                                               **params
                                               ):
        
        action = ACTION_VDI_MODIFY_DESKTOP_ZONE_CITRIX_CONNECTION
        body = {"zone_id": zone_id}
        body["host"] = host
        body["port"] = port
        body["protocol"] = protocol
        body["storefront_port"] = storefront_port
        body["netscaler_port"] = netscaler_port
        if http_socket_timeout:
            body["http_socket_timeout"] = http_socket_timeout
        body["managed_resource"] = managed_resource
        if storefront_uri is not None:
            body["storefront_uri"] = storefront_uri
        if netscaler_uri is not None:
            body["netscaler_uri"] = netscaler_uri
     
        if storefront_port is not None:
            body["storefront_port"] = storefront_port

        if netscaler_port is not None:
            body["netscaler_port"] = netscaler_port             

        if support_netscaler is not None:
            body["support_netscaler"] = support_netscaler

        if support_citrix_pms is not None:
            body["support_citrix_pms"] = support_citrix_pms

        return self._build_params(action, body)

    def describe_instance_class_disk_type(self,
                                          instance_class=None,
                                          disk_type=None,
                                          reverse=None,
                                          sort_key=None,
                                          offset=0,
                                          limit=20,
                                          search_word=None,
                                          verbose=0,
                                          **params
                                          ):
        action = ACTION_VDI_DESCRIBE_INSTANCE_CLASS_DISK_TYPE
        body = {}

        if instance_class is not None:
            body["instance_class"] = instance_class

        if disk_type is not None:
            body["disk_type"] = disk_type

        if reverse:
            body["reverse"] = reverse

        if sort_key:
            body["sort_key"] = sort_key

        if offset is not None:
            body["offset"] = offset

        if limit:
            body["limit"] = limit

        if search_word:
            body["search_word"] = search_word

        if verbose is not None:
            body["verbose"] = verbose

        return self._build_params(action, body)

    def describe_gpu_class_type(self,
                                gpu_class_key=None,
                                gpu_class=None,
                                reverse=None,
                                sort_key=None,
                                offset=0,
                                limit=20,
                                search_word=None,
                                verbose=0,
                                **params):

        action = ACTION_VDI_DESCRIBE_GPU_CLASS_TYPE
        body = {}

        if gpu_class_key is not None:
            body["gpu_class_key"] = gpu_class_key

        if gpu_class is not None:
            body["gpu_class"] = gpu_class

        if reverse:
            body["reverse"] = reverse

        if sort_key:
            body["sort_key"] = sort_key

        if offset is not None:
            body["offset"] = offset

        if limit:
            body["limit"] = limit

        if search_word:
            body["search_word"] = search_word

        if verbose is not None:
            body["verbose"] = verbose

        return self._build_params(action, body)

    def check_network_connection(self,
                                ip_addr,
                                port,
                                **params):

        action = ACTION_VDI_CHECK_NETWORK_CONNECTION
        body = {}
        body["ip_addr"] = ip_addr
        body["port"] = port

        return self._build_params(action, body)

    def check_gpu_config(self, zone_id,
                                **params):

        action = ACTION_VDI_CHECK_GPU_CONFIG
        body = {}
        body["zone_id"] = zone_id

        return self._build_params(action, body)