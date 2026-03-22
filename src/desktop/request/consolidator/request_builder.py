'''
Created on 2012-6-26

@author: yunify
'''

import error.error_code as ErrorCodes
from error.error import Error
from common import unicode_to_string
from utils.time_stamp import get_expired_ts, get_ts
from constants import (

    # desktop group
    ACTION_VDI_CREATE_DESKTOP_GROUP,
    ACTION_VDI_DESCRIBE_DESKTOP_GROUPS,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_IMAGE,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_DESKTOP_COUNT,
    ACTION_VDI_DELETE_DESKTOP_GROUPS,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_STATUS,

    ACTION_VDI_DESCRIBE_DESKTOP_GROUP_DISKS,
    ACTION_VDI_CREATE_DESKTOP_GROUP_DISK,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_DISK,
    ACTION_VDI_DELETE_DESKTOP_GROUP_DISKS,

    ACTION_VDI_DESCRIBE_DESKTOP_GROUP_NETWORKS,
    ACTION_VDI_CREATE_DESKTOP_GROUP_NETWORK,
    ACTION_VDI_MODIFY_DESKTOP_GROUP_NETWORK,
    ACTION_VDI_DELETE_DESKTOP_GROUP_NETWORKS,

    ACTION_VDI_DESCRIBE_DESKTOP_GROUP_USERS,

    ACTION_VDI_DESCRIBE_DESKTOP_IPS,

    ACTION_VDI_ATTACH_USER_TO_DESKTOP_GROUP,
    ACTION_VDI_DETACH_USER_FROM_DESKTOP_GROUP,
    ACTION_VDI_SET_DESKTOP_GROUP_USER_STATUS,
    ACTION_VDI_APPLY_DESKTOP_GROUP,

    # network
    ACTION_VDI_DESCRIBE_DESKTOP_NETWORKS,
    ACTION_VDI_CREATE_DESKTOP_NETWORK,
    ACTION_VDI_MODIFY_DESKTOP_NETWORK_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOP_NETWORKS,
    ACTION_VDI_DESCRIBE_SYSTEM_NETWORKS,
    ACTION_VDI_LOAD_SYSTEM_NETWORK,
    ACTION_VDI_DESKTOP_LEAVE_NETWORKS,
    ACTION_VDI_DESKTOP_JOIN_NETWORKS,
    ACTION_VDI_DESCRIBE_DESKTOP_ROUTERS,

    # desktop
    ACTION_VDI_CREATE_DESKTOP,
    ACTION_VDI_DESCRIBE_NORMAL_DESKTOPS,
    ACTION_VDI_DESCRIBE_DESKTOPS,
    ACTION_VDI_MODIFY_DESKTOP_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOPS,
    ACTION_VDI_ATTACH_USER_TO_DESKTOP,
    ACTION_VDI_DETACH_USER_FROM_DESKTOP,
    ACTION_VDI_RESTART_DESKTOPS,
    ACTION_VDI_START_DESKTOPS,
    ACTION_VDI_STOP_DESKTOPS,
    ACTION_VDI_RESET_DESKTOPS,
    ACTION_VDI_SET_DESKTOP_MONITOR,
    ACTION_VDI_SET_DESKTOP_AUTO_LOGIN,
    ACTION_VDI_MODIFY_DESKTOP_DESCRIPTION,
    ACTION_VDI_APPLY_RANDOM_DESKTOP,
    ACTION_VDI_FREE_RANDOM_DESKTOPS,
    ACTION_VDI_CREATE_BROKERS,
    ACTION_VDI_DELETE_BROKERS,
    ACTION_VDI_MODIFY_DESKTOP_IP,
    ACTION_VDI_CHECK_DESKTOP_HOSTNAME,
    ACTION_VDI_REFRESH_DESKTOP_DB,
    # app
    ACTION_VDI_CREATE_APP_DESKTOP_GROUP,
    ACTION_VDI_DESCRIBE_APP_COMPUTES,
    ACTION_VDI_ADD_COMPUTE_TO_DESKTOP_GROUP,
    ACTION_VDI_DESCRIBE_APP_STARTMEMUS,
    ACTION_VDI_DESCRIBE_BROKER_APPS,
    ACTION_VDI_CREATE_BROKER_APPS,
    ACTION_VDI_MODIFY_BROKER_APP,
    ACTION_VDI_DELETE_BROKER_APPS,
    ACTION_VDI_ATTACH_BROKER_APP_TO_DELIVERY_GROUP,
    ACTION_VDI_DETACH_BROKER_APP_FROM_DELIVERY_GROUP,
    ACTION_VDI_CREATE_BROKER_FOLDER,
    ACTION_VDI_DELETE_BROKER_FOLDERS,
    ACTION_VDI_DESCRIBE_BROKER_FOLDERS,
    ACTION_VDI_CREATE_BROKER_APP_GROUP,
    ACTION_VDI_DELETE_BROKER_APP_GROUPS,
    ACTION_VDI_DESCRIBE_BROKER_APP_GROUPS,
    ACTION_VDI_ATTACH_BROKER_APP_TO_APP_GROUP,
    ACTION_VDI_DETACH_BROKER_APP_FROM_APP_GROUP,
    ACTION_VDI_REFRESH_BROKER_APPS,
    # job
    ACTION_VDI_DESCRIBE_DESKTOP_JOBS,
    ACTION_VDI_DESCRIBE_DESKTOP_TASKS,
    # monitor
    ACTION_VDI_GET_DESKTOP_MONITOR,
    # disk
    ACTION_VDI_CREATE_DESKTOP_DISKS,
    ACTION_VDI_DELETE_DESKTOP_DISKS,
    ACTION_VDI_ATTACH_DISK_TO_DESKTOP,
    ACTION_VDI_DETACH_DISK_FROM_DESKTOP,
    ACTION_VDI_DESCRIBE_DESKTOP_DISKS,
    ACTION_VDI_RESIZE_DESKTOP_DISKS,
    ACTION_VDI_MODIFY_DESKTOP_DISK_ATTRIBUTES,
    
    # image
    ACTION_VDI_CREATE_DESKTOP_IMAGE,
    ACTION_VDI_SAVE_DESKTOP_IMAGES,
    ACTION_VDI_DESCRIBE_DESKTOP_IMAGES,
    ACTION_VDI_DELETE_DESKTOP_IMAGES,
    ACTION_VDI_MODIFY_DESKTOP_IMAGE_ATTRIBUTES,
    ACTION_VDI_DESCRIBE_SYSTEM_IMAGES,
    ACTION_VDI_LOAD_SYSTEM_IMAGES,
    # scheduler
    ACTION_VDI_DESCRIBE_SCHEDULER_TASKS,
    ACTION_VDI_CREATE_SCHEDULER_TASK,
    ACTION_VDI_MODIFY_SCHEDULER_TASK_ATTRIBUTES,
    ACTION_VDI_DELETE_SCHEDULER_TASKS,
    ACTION_VDI_DESCRIBE_SCHEDULER_TASK_HISTORY,
    ACTION_VDI_ADD_RESOURCE_TO_SCHEDULER_TASK,
    ACTION_VDI_DELETE_RESOURCE_FROM_SCHEDULER_TASK,
    ACTION_VDI_SET_SCHEDULER_TASK_STATUS,
    ACTION_VDI_EXECUTE_SCHEDULER_TASK,
    ACTION_VDI_GET_SCHEDULER_TASK_RESOURCES,
    ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_COUNT,
    ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_IMAGE,

    ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_CONFIG,
    ACTION_VDI_MODIFY_DESKTOP_SYSTEM_CONFIG,
    ACTION_VDI_DESCRIBE_DESKTOP_BASE_SYSTEM_CONFIG,
    ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_LOGS,

    ACTION_VDI_CREATE_SYSLOG_SERVER,
    ACTION_VDI_MODIFY_SYSLOG_SERVER,
    ACTION_VDI_DELETE_SYSLOG_SERVERS,
    ACTION_VDI_DESCRIBE_SYSLOG_SERVERS,

    # policy
    ACTION_VDI_CREATE_USB_PROLICY,
    ACTION_VDI_MODIFY_USB_PROLICY,
    ACTION_VDI_DELETE_USB_PROLICY,
    ACTION_VDI_DESCRIBE_USB_PROLICY,
    # license
    ACTION_VDI_UPDATE_LICENSE,
    ACTION_VDI_DESCRIBE_LICENSE,

    ACTION_VDI_MODIFY_APPROVALNOTICE_CONFIG,
    ACTION_VDI_DESCRIBE_APPROVALNOTICE_CONFIG,
    #log
    ACTION_VDI_DOWNLOAD_LOG,
)
from constants import (
    REQ_EXPIRED_INTERVAL,
)
class RequestBuilder(object):
    ''' API request builder '''

    def __init__(self, sender):
        '''
        @param sender - the id of the sender of the request
        '''
        self.sender = sender
        # error message
        self.error = Error(ErrorCodes.INVALID_REQUEST_FORMAT)

    def _add_auth(self, params):
        ''' add privilege related parameters '''
        params["sender"] = self.sender

    def _add_expires(self, params):
        ''' add expires time '''
        params["expires"] = get_expired_ts(get_ts(), REQ_EXPIRED_INTERVAL)
    
    def _build_params(self, action, body):
        ''' build parameters '''
        params = {}
        for k in body:
            params[k] = body[k]
        params['action'] = action

        # add auth and expires
        self._add_auth(params)
        self._add_expires(params)
        return params

    def filter_out_none(self, dictionary, keys=None):
        """ Filter out items whose value is None.
            If `keys` specified, only return non-None items with matched key.
        """
        ret = {}
        if keys is None:
            keys = []
        for key, value in dictionary.items():
            if value is None or (keys and key not in keys):
                continue
            ret[key] = value
        return ret

    def create_desktop_group(self, zone,
                             desktop_image,
                             cpu,
                             memory,
                             desktop_group_type,
                             naming_rule,
                             instance_class,
                             networks=None,
                             disk_size=None,
                             disk_name=None,
                             desktop_group_name = None,
                             description = None,
                             ivshmem_enable = None,
                             desktop_count = None,
                             gpu = None,
                             gpu_class = None,
                             is_create = None,
                             usbredir = None,
                             clipboard =None,
                             filetransfer = None,
                             qxl_number = None,
                             users = None,
                             desktop_dn =None,
                             save_disk=None,
                             save_desk=None,
                             managed_resource = None,
                             allocation_type = None,
                             place_group_id = None,
                             cpu_model = None,
                             cpu_topology = None,
                             security_group=None,
                             is_load=0,
                             provision_type=None,
                             **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_DESKTOP_GROUP
        body = {}
        body["zone"] = zone
        body["desktop_image"] = desktop_image
        body["cpu"] = cpu
        body["memory"] = memory
        body["desktop_group_type"] = desktop_group_type
        body["naming_rule"] = naming_rule
        body["instance_class"] = instance_class
        if networks:
            body["networks"] = networks        
        if desktop_group_name:
            body["desktop_group_name"] = desktop_group_name
        if description:
            body["description"] = description
        if ivshmem_enable is not None:
            body["ivshmem_enable"] = ivshmem_enable
        if desktop_count is not None:
            body["desktop_count"] = desktop_count
        if gpu is not None:  
            body["gpu"] = gpu
        if gpu_class is not None:
            body["gpu_class"] = gpu_class
        if is_create is not None:    
            body["is_create"] = is_create
        if usbredir is not None:
            body["usbredir"] = usbredir
        if clipboard is not None:
            body["clipboard"] = clipboard
        if  filetransfer is not None:
            body["filetransfer"] = filetransfer
        if qxl_number is not None:
            body["qxl_number"] = qxl_number
        else:
            body["qxl_number"] = 1
        if users:
            body["users"] = users
        if disk_size:
            body["disk_size"] = disk_size
        if disk_name:
            body["disk_name"] = disk_name
        if desktop_dn:
            body["desktop_dn"] = desktop_dn
        if save_disk is not None:
            body["save_disk"] = save_disk
        if save_desk is not None:
            body["save_desk"] = save_desk
        if managed_resource:
            body["managed_resource"] = managed_resource
        if allocation_type:
            body["allocation_type"] = allocation_type
        
        if place_group_id:
            body["place_group_id"] = place_group_id
        if cpu_model:
            body["cpu_model"] = cpu_model
        if cpu_topology:
            body["cpu_topology"] = cpu_topology
        if is_load:
            body["is_load"] = is_load
        if security_group:
            body["security_group"] = security_group
        
        if provision_type:
            body["provision_type"] = provision_type

        return self._build_params(action, body)

    def describe_desktop_groups(self,
                                zone,
                                desktop_groups = None,
                                desktop_group_type = None,
                                desktop_image = None,
                                user = None,
                                status = None,
                                reverse = None,
                                sort_key = None,
                                offset = 0,
                                limit = 20,
                                search_word = None,
                                verbose = 0,
                                allocation_type = None,
                                session_type =None,
                                provision_type = None,
                                check_desktop_dn = None,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_GROUPS
        body = {}
        body["zone"] = zone

        if desktop_groups:
            body['desktop_groups'] = desktop_groups
        if desktop_image:
            body['desktop_image'] = desktop_image
        if desktop_group_type:
            body['desktop_group_type'] = desktop_group_type
        if status:
            body['status'] = status
        if user:
            body['user'] = user
        if search_word:
            body['search_word'] = search_word
        if verbose is not None:
            body['verbose'] = verbose
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        
        if allocation_type:
            body["allocation_type"] = allocation_type
        
        if session_type:
            body["session_type"] = session_type
        
        if provision_type:
            body["provision_type"] = provision_type
        if check_desktop_dn :
            body['check_desktop_dn'] = check_desktop_dn        
        return self._build_params(action, body)

    def modify_desktop_group_attributes(self, zone,
                                        desktop_group,
                                        cpu = None,
                                        memory = None,
                                        desktop_group_name = None,
                                        description = None,
                                        ivshmem_enable = None,
                                        is_create = None,
                                        usbredir = None,
                                        clipboard =None,
                                        filetransfer = None,
                                        gpu=None,
                                        gpu_class = None,
                                        desktop_dn = None,
                                        qxl_number=None,
                                        **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body["desktop_group"] = desktop_group
        
        if cpu is not None:
            body['cpu'] = cpu
        if memory is not None:
            body['memory'] = memory
        if desktop_group_name:
            body["desktop_group_name"] = desktop_group_name
        if description is not None:
            body["description"] = description
        if ivshmem_enable is not None:
            body["ivshmem_enable"] = ivshmem_enable

        if is_create is not None:    
            body["is_create"] = is_create
        if usbredir is not None:
            body["usbredir"] = usbredir
        if clipboard is not None:
            body["clipboard"] = clipboard
        if  filetransfer is not None:
            body["filetransfer"] = filetransfer
        if  gpu is not None:
            body["gpu"] = gpu
        if gpu_class is not None:
            body["gpu_class"] = gpu_class
            
        if qxl_number:
            body["qxl_number"] = qxl_number
        
        if desktop_dn:
            body["desktop_dn"] = desktop_dn

        return self._build_params(action, body)

    def modify_desktop_group_image(self, zone,
                                        desktop_group,
                                        desktop_image,
                                        **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_GROUP_IMAGE
        body = {}
        body["zone"] = zone
        body["desktop_group"] = desktop_group
        body["desktop_image_id"] = desktop_image

        return self._build_params(action, body)

    def modify_desktop_group_desktop_count(self, zone,
                                            desktop_group,
                                            desktop_count,
                                            **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_GROUP_DESKTOP_COUNT
        body = {}
        body["zone"] = zone
        body["desktop_group"] = desktop_group
        body["desktop_count"] = desktop_count

        return self._build_params(action, body)


    def delete_desktop_groups(self, zone,
                              desktop_groups,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_DESKTOP_GROUPS
        body = {}
        body["zone"] = zone
        body["desktop_groups"] = desktop_groups

        return self._build_params(action, body)

    def modify_desktop_group_status(self, 
                                    zone,
                                    desktop_group,
                                    status,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''

        action = ACTION_VDI_MODIFY_DESKTOP_GROUP_STATUS
        body = {}
        body["zone"] = zone
        body['desktop_group'] = desktop_group
        body['status'] = status

        return self._build_params(action, body) 

    def describe_desktop_group_disks(self, zone,
                                       desktop_group,
                                       disk_config=None,
                                       reverse = None,
                                       sort_key = None,
                                       offset = None,
                                       limit = 20,
                                       search_word = None,
                                       verbose = 0,
                                       **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_GROUP_DISKS
        body = {}
        body["zone"] = zone
        body['desktop_group'] = desktop_group
        if disk_config:
            body['disk_config'] = disk_config
        if search_word:
            body['search_word'] = search_word
        if verbose:
            body['verbose'] = verbose
        if offset:
            body['offset'] = int(offset)
        if limit:
            body['limit'] = int(limit)
        if reverse:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        return self._build_params(action, body) 

    def create_desktop_group_disk(self, zone,
                                    desktop_group,
                                    disk_size,
                                    disk_name,
                                    is_load = None,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_DESKTOP_GROUP_DISK
        body = {}
        body["zone"] = zone
        body['desktop_group'] = desktop_group
        body['disk_size'] = disk_size
        body['disk_name'] = disk_name
        if is_load is not None:
            body["is_load"] = is_load

        return self._build_params(action, body) 
    
    def modify_desktop_group_disk(self, zone,
                                       disk_config,
                                       size=None,
                                       disk_name=None,
                                       **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_GROUP_DISK
        body = {}
        body["zone"] = zone
        body['disk_config'] = disk_config
        if disk_name:
            body['disk_name'] = disk_name
        if size:
            body['size'] = size

        return self._build_params(action, body)

    def delete_desktop_group_disks(self, zone,
                                       disk_configs,
                                       **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_DESKTOP_GROUP_DISKS
        body = {}
        body["zone"] = zone
        body['disk_configs'] = disk_configs
        return self._build_params(action, body)

    def describe_desktop_group_networks(self, zone,
                                        desktop_group=None,
                                        network_type = None,
                                        network_config = None,
                                        reverse = None,
                                        sort_key = None,
                                        offset = None,
                                        limit = 20,
                                        search_word = None,
                                        verbose = 0,
                                        **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_GROUP_NETWORKS
        body = {}
        body["zone"] = zone
        if desktop_group:
            body['desktop_group'] = desktop_group
        if network_config:
            body['network_config'] = network_config
        
        if network_type:
            body["network_type"] = network_type
        if search_word:
            body['search_word'] = search_word
        if verbose:
            body['verbose'] = verbose
        if offset:
            body['offset'] = int(offset)
        if limit:
            body['limit'] = int(limit)
        if reverse:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        
        return self._build_params(action, body)

    def create_desktop_group_network(self, zone,
                                     desktop_group,
                                     network,
                                     start_ip = None,
                                     end_ip = None,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_DESKTOP_GROUP_NETWORK
        body = {}
        body["zone"] = zone
        body['desktop_group'] = desktop_group
        body['network'] = network

        if start_ip:
            body['start_ip'] = start_ip
        if end_ip:
            body['end_ip'] = end_ip

        return self._build_params(action, body) 

    def modify_desktop_group_network(self, zone,
                                     network_config,
                                     start_ip,
                                     end_ip,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_GROUP_NETWORK
        body = {}
        body["zone"] = zone
        body['network_config'] = network_config
        body['start_ip'] = start_ip
        body['end_ip'] = end_ip

        return self._build_params(action, body) 
    
    def delete_desktop_group_networks(self, zone,
                                            network_configs,
                                            **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_DESKTOP_GROUP_NETWORKS
        body = {}
        body["zone"] = zone
        body['network_configs'] = network_configs

        return self._build_params(action, body) 

    def describe_desktop_group_users(self, zone,
                                        desktop_group,
                                        users = None,
                                        status = None,
                                        reverse = None,
                                        sort_key = None,
                                        offset = None,
                                        limit = 20,
                                        search_word = None,
                                        verbose = 0,
                                        **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_GROUP_USERS
        body = {}
        body["zone"] = zone
        body['desktop_group'] = desktop_group
        if users:
            body['users'] = users
        if search_word:
            body['search_word'] = search_word
        if verbose is not None:
            body['verbose'] = verbose
        if status:
            body['status'] = status
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        return self._build_params(action, body)

    def describe_desktop_ips(self, zone,
                                    desktop_group=None,
                                    desktop = None,
                                    network=None,
                                    status=None,
                                    private_ips=None,
                                    is_free=None,
                                    reverse = None,
                                    sort_key = None,
                                    offset = None,
                                    limit = 20,
                                    search_word = None,
                                    verbose = 0,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_IPS
        body = {}
        body["zone"] = zone
        if desktop_group:
            body['desktop_group'] = desktop_group

        if desktop:
            body['desktop'] = desktop
        if network:
            body['network'] = network
        if private_ips:
            body['private_ips'] = private_ips
        if is_free is not None:
            body["is_free"] = is_free
        if search_word:
            body['search_word'] = search_word
        if verbose is not None:
            body['verbose'] = verbose
        if status:
            body['status'] = status
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        return self._build_params(action, body)

    def attach_user_to_desktop_group(self, zone,
                                      desktop_group,
                                      users,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_ATTACH_USER_TO_DESKTOP_GROUP
        body = {}
        body["zone"] = zone
        body['desktop_group'] = desktop_group
        body['users'] = users

        return self._build_params(action, body) 

    def detach_user_from_desktop_group(self, zone,
                                      desktop_group,
                                      users,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DETACH_USER_FROM_DESKTOP_GROUP
        body = {}
        body["zone"] = zone
        body['desktop_group'] = desktop_group
        body['users'] = users

        return self._build_params(action, body) 

    def set_desktop_group_user_status(self, zone,
                                      desktop_group,
                                      users,
                                      status,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_SET_DESKTOP_GROUP_USER_STATUS
        body = {}
        body["zone"] = zone
        body['desktop_group'] = desktop_group
        body['users'] = users
        body['status'] = status
        
        return self._build_params(action, body) 

    def describe_desktop_networks(self, zone,
                                      networks=None,
                                      network_type = None,
                                      status = None,
                                      reverse = None,
                                      sort_key = None,
                                      offset = None,
                                      limit = 20,
                                      search_word = None,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_NETWORKS
        body = {}
        body["zone"] = zone
        if networks:
            body['networks'] = networks

        if network_type:
            body["network_type"] = network_type
        if status:
            body['status'] = status
        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        return self._build_params(action, body) 

    def create_desktop_network(self, zone,
                                   ip_network,
                                   start_ip=None,
                                   end_ip=None,
                                   network_name=None,
                                   description = None,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_DESKTOP_NETWORK
        body = {}
        body["zone"] = zone
        body['ip_network'] = ip_network

        if start_ip:
            body['start_ip'] = start_ip
        
        if end_ip:
            body['end_ip'] = end_ip

        if network_name:
            body['network_name'] = network_name
        
        if description is not None:
            body["description"] = description

        return self._build_params(action, body) 
    
    def modify_desktop_network_attributes(self, zone,
                                               network,
                                               start_ip = None,
                                               end_ip = None,
                                               network_name=None,
                                               description=None,
                                               **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_NETWORK_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body['network'] = network
        
        if start_ip:
            body["start_ip"] = start_ip
            
        if end_ip:
            body["end_ip"] = end_ip

        if network_name:
            body['network_name'] = network_name
        if description is not None:
            body['description'] = description

        return self._build_params(action, body)

    def delete_desktop_networks(self, zone,
                                    networks,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_DESKTOP_NETWORKS
        body = {}
        body["zone"] = zone
        body["networks"] = networks

        return self._build_params(action, body)

    def describe_system_networks(self, zone,
                                   offset=0,
                                   limit=20,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_SYSTEM_NETWORKS
        body = {}
        body["zone"] = zone
        body["offset"] = offset
        body["limit"] = limit

        return self._build_params(action, body) 

    def load_system_network(self, zone,
                                   network,
                                   start_ip=None,
                                   end_ip=None,
                                   network_name=None,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_LOAD_SYSTEM_NETWORK
        body = {}
        body["zone"] = zone
        body["network"] = network
    
        if start_ip:
            body['start_ip'] = start_ip
        
        if end_ip:
            body['end_ip'] = end_ip
        
        if network_name:
            body["network_name"] = network_name

        return self._build_params(action, body)

    def describe_desktop_routers(self,
                                   zone,
                                   routers=None,
                                   verbose=0,
                                   search_word=None,
                                   offset=None,
                                   limit=20,
                                   sort_key=None,
                                   reverse=0,
                                   is_and=1,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_ROUTERS
        body = {}
        body["zone"] = zone
        if routers:
            body['routers'] = routers
        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if verbose is not None:
            body['verbose'] = int(verbose)
        if reverse == 0:
            body["reverse"] = 0
        else:
            body["reverse"] = 1
        if sort_key:
            body["sort_key"] = sort_key

        if is_and == 0:
            body['is_and'] = 0
        else:
            body['is_and'] = 1

        return self._build_params(action, body)

    def apply_desktop_group(self, zone,
                              desktop_group,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_APPLY_DESKTOP_GROUP
        body = {}
        body["zone"] = zone
        body['desktop_group'] = desktop_group

        return self._build_params(action, body) 

    def create_desktop(self, zone,
                             desktop_image,
                             cpu,
                             memory,
                             hostname,
                             instance_class,
                             networks=None,
                             user=None,
                             description = None,
                             ivshmem_enable = None,
                             gpu = None,
                             gpu_class = None,
                             usbredir = None,
                             clipboard =None,
                             filetransfer = None,
                             qxl_number = None,
                             disks = None,
                             desktop_dn=None,
                             disk_size=None,
                             disk_name=None,
                             **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_DESKTOP
        body = {}
        body["zone"] = zone
        body["desktop_image"] = desktop_image
        body["cpu"] = cpu
        body["memory"] = memory
        body["hostname"] = hostname
        if user:
            body["user"] = user
        
        if desktop_dn:
            body["desktop_dn"] = desktop_dn

        body["instance_class"] = instance_class

        if description:
            body["description"] = description
        if ivshmem_enable is not None:
            body["ivshmem_enable"] = ivshmem_enable
        if gpu is not None:  
            body["gpu"] = gpu
        if gpu_class is not None:
            body["gpu_class"] = gpu_class
        if usbredir is not None:
            body["usbredir"] = usbredir
        if clipboard is not None:
            body["clipboard"] = clipboard
        if  filetransfer is not None:
            body["filetransfer"] = filetransfer
        if  qxl_number is not None:
            body["qxl_number"] = qxl_number
        else:
            body["qxl_number"] = 1
        if disks:
            body["disks"] = disks
        if disk_size:
            body["disk_size"] = disk_size
        if disk_name:
            body["disk_name"] = disk_name
        if networks:
            body["networks"] = networks
        return self._build_params(action, body)

    def describe_normal_desktops(self, zone,
                                desktops = None,
                                desktop_group = None,
                                status = None,
                                user = None,
                                hostname = None,
                                reverse = None,
                                sort_key = None,
                                offset = None,
                                limit = 20,
                                search_word = None,
                                verbose = 0,
                                sf_cookies=None,
                                user_name=None,
                                password=None,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_NORMAL_DESKTOPS
        body = {}
        body["zone"] = zone
        if desktops:
            body['desktops'] = desktops

        if desktop_group:
            body['desktop_group'] = desktop_group

        if status:
            body['status'] = status
        if hostname:
            body['hostname'] = hostname

        if user:
            body['user'] = user

        if search_word:
            body['search_word'] = search_word
        if verbose is not None:
            body['verbose'] = verbose
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        
        if user_name:
            body["user_name"] = user_name
        
        if password:
            body["password"] = password
    
        if sf_cookies:
            body['sf_cookies'] = sf_cookies
        return self._build_params(action, body)

    def describe_desktops(self, zone,
                                desktops = None,
                                desktop_group = None,
                                desktop_image = None,
                                status = None,
                                user = None,
                                hostname = None,
                                need_monitor = None,
                                with_monitor = None,
                                instance_class = None,
                                reverse = None,
                                sort_key = None,
                                offset = None,
                                limit = 20,
                                search_word = None,
                                verbose = 0,
                                no_delivery_group=None,
                                delivery_group = None,
                                desktop_mode = None,
                                sf_cookie=None,
                                **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOPS
        body = {}
        body["zone"] = zone
        if desktops:
            body['desktops'] = desktops
        if desktop_image:
            body['desktop_image'] = desktop_image
        if desktop_group:
            body['desktop_group'] = desktop_group
        if instance_class:
            body["instance_class"] = instance_class
        if status:
            body['status'] = status
        if hostname:
            body['hostname'] = hostname
        if need_monitor is not None:
            body['need_monitor'] = need_monitor
        if with_monitor is not None:
            body['with_monitor'] = with_monitor
        
        if delivery_group:
            body["delivery_group_id"] = delivery_group

        if user:
            body['user'] = user

        if search_word:
            body['search_word'] = search_word
        if verbose is not None:
            body['verbose'] = verbose
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        
        if desktop_mode:
            body["desktop_mode"] = desktop_mode
        
        if no_delivery_group:
            body["no_delivery_group"] = no_delivery_group            
        if sf_cookie:
            body['sf_cookie'] = sf_cookie
        return self._build_params(action, body)

    def modify_desktop_attributes(self, zone,
                                        desktop,
                                        cpu = None,
                                        memory = None,
                                        description = None,
                                        ivshmem_enable = None,
                                        gpu = None,
                                        usbredir = None,
                                        clipboard =None,
                                        filetransfer = None,
                                        no_sync=None,
                                        qxl_number=None,
                                        **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body["desktop"] = desktop
        
        if cpu:
            body['cpu'] = cpu
        if memory:
            body['memory'] = memory
        if description is not None:
            body["description"] = description
        if ivshmem_enable is not None:
            body["ivshmem_enable"] = ivshmem_enable
        if gpu is not None:  
            body["gpu"] = gpu
        if usbredir is not None:
            body["usbredir"] = usbredir
        if clipboard is not None:
            body["clipboard"] = clipboard
        if  filetransfer is not None:
            body["filetransfer"] = filetransfer
        if qxl_number:
            body["qxl_number"] = qxl_number
        if no_sync:
            body["no_sync"] = no_sync
        return self._build_params(action, body)
    
    def delete_desktops(self, zone,
                             desktops,
                             save_disk=None,
                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_DESKTOPS
        body = {}
        body["zone"] = zone
        body['desktops'] = desktops
        if save_disk is not None:
            body['save_disk'] = save_disk

        return self._build_params(action, body) 
    
    def attach_user_to_desktop(self, zone,
                                      desktop,
                                      user_ids,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_ATTACH_USER_TO_DESKTOP
        body = {}
        body["zone"] = zone
        body['desktop'] = desktop
        body['user_ids'] = user_ids

        return self._build_params(action, body) 
    
    def detach_user_from_desktop(self, zone,
                                       desktop_id,
                                       user_ids,
                                       **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DETACH_USER_FROM_DESKTOP
        body = {}
        body["zone"] = zone
        body['desktop_id'] = desktop_id
        body["user_ids"] = user_ids

        return self._build_params(action, body) 

    def restart_desktops(self, zone,
                               desktop_group = None,
                               desktops = None,
                               **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_RESTART_DESKTOPS
        body = {}
        body["zone"] = zone
        if desktop_group:
            body['desktop_group'] = desktop_group
        if desktops:
            body['desktops'] = desktops
        
        return self._build_params(action, body) 
    
    def start_desktops(self, zone,
                           desktop_group = None,
                           desktops = None,
                           **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_START_DESKTOPS
        body = {}
        body["zone"] = zone
        if desktop_group:
            body['desktop_group'] = desktop_group
        if desktops:
            body['desktops'] = desktops

        return self._build_params(action, body) 

    def stop_desktops(self, zone,
                           desktop_group = None,
                           desktops = None,
                           **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_STOP_DESKTOPS
        body = {}
        body["zone"] = zone
        if desktop_group:
            body['desktop_group'] = desktop_group
        if desktops:
            body['desktops'] = desktops

        return self._build_params(action, body) 
    
    def reset_desktops(self, zone,
                           desktop_group = None,
                           desktops = None,
                           **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_RESET_DESKTOPS
        body = {}
        body["zone"] = zone
        if desktop_group:
            body['desktop_group'] = desktop_group
        if desktops:
            body['desktops'] = desktops

        return self._build_params(action, body) 

    def set_desktop_monitor(self, zone,
                                  desktops,
                                  monitor,
                                  **params):
        '''
            @param directive : the dictionary of params
        '''

        action = ACTION_VDI_SET_DESKTOP_MONITOR
        body = {}
        body["zone"] = zone
        body['desktops'] = desktops
        body['monitor'] = monitor

        return self._build_params(action, body)

    def set_desktop_auto_login(self, zone,
                                      desktop,
                                      auto_login,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''

        action = ACTION_VDI_SET_DESKTOP_AUTO_LOGIN
        body = {}
        body["zone"] = zone
        body['desktop'] = desktop
        body['auto_login'] = auto_login

        return self._build_params(action, body)

    def modify_desktop_description(self, zone,
                                      desktop,
                                      description=None,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''

        action = ACTION_VDI_MODIFY_DESKTOP_DESCRIPTION
        body = {}
        body["zone"] = zone
        body['desktop'] = desktop
        if description:
            body['description'] = description

        return self._build_params(action, body)

    def apply_random_desktop(self, zone,
                                  desktop_group,
                                  user,
                                  **params):
        '''
            @param directive : the dictionary of params
        '''

        action = ACTION_VDI_APPLY_RANDOM_DESKTOP
        body = {}
        body["zone"] = zone
        body['desktop_group'] = desktop_group
        body['user'] = user

        return self._build_params(action, body)

    def free_random_desktops(self, zone,
                                  desktops,
                                  **params):
        '''
            @param directive : the dictionary of params
        '''

        action = ACTION_VDI_FREE_RANDOM_DESKTOPS
        body = {}
        body["zone"] = zone
        body['desktops'] = desktops

        return self._build_params(action, body)


    def create_brokers(self, zone,
                             desktop=None,
                             desktop_image=None,
                             full_screen=None,
                             ica_uri=None,
                             assign_uri=None,
                             assign_state=-1,
                             sf_cookie=None,
                             protocol_type=None,
                             client_ip=None,
                             **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_BROKERS
        body = {}
        body["zone"] = zone
        if desktop_image:
            body['desktop_image'] = desktop_image
        if desktop:
            body['desktop'] = desktop
        if ica_uri:
            body['ica_uri'] = ica_uri                      
        if full_screen == 0:
            body["full_screen"] = 0
        else:
            body["full_screen"] = 1
        if assign_uri:
            body["assign_uri"] = assign_uri
        if client_ip:
            body["client_ip"] = client_ip
            
        if assign_state >= 0:
            body['assign_state'] = assign_state   
        if sf_cookie:
            body['sf_cookie'] = sf_cookie
        
        if protocol_type:
            body["protocol_type"] = protocol_type
    
        return self._build_params(action, body) 

    def delete_brokers(self, zone,
                             desktops,
                             **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_BROKERS
        body = {}
        body["zone"] = zone
        body['desktops'] = desktops

        return self._build_params(action, body) 

    def check_desktop_hostname(self, zone,
                                    hostname,
                                    name_type,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CHECK_DESKTOP_HOSTNAME
        body = {}
        body["zone"] = zone
        body["hostname"] = hostname
        body["name_type"] = name_type
        
        return self._build_params(action, body)

    def create_desktop_disks(self, zone,
                                     size,
                                     desktops,
                                     disk_name = None,
                                     description=None,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_DESKTOP_DISKS
        body = {}
        body["zone"] = zone
        body['size'] = size
        body['desktops'] = desktops
        if disk_name:
            body['disk_name'] = disk_name
        if description:
            body['description'] = description

        return self._build_params(action, body) 

    def delete_desktop_disks(self, zone,
                                   disks,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_DESKTOP_DISKS
        body = {}
        body["zone"] = zone
        body['disks'] = disks 

        return self._build_params(action, body)
    
    def attach_disk_to_desktop(self, zone,
                                    disks,
                                    desktop,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_ATTACH_DISK_TO_DESKTOP
        body = {}
        body["zone"] = zone
        body['disks'] = disks 
        body['desktop'] = desktop

        return self._build_params(action, body) 

    def detach_disk_from_desktop(self, zone,
                                    disks,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DETACH_DISK_FROM_DESKTOP
        body = {}
        body["zone"] = zone
        body['disks'] = disks 

        return self._build_params(action, body) 

    def describe_desktop_disks(self, zone,
                                    disks = None,
                                    desktop_group = None,
                                    status = None,
                                    disk_config=None,
                                    user = None,
                                    desktop = None,
                                    disk_type=None,
                                    reverse = None,
                                    sort_key = None,
                                    offset = None,
                                    limit = 100,
                                    search_word = None,
                                    verbose = 0,
                                    owner = None,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_DISKS
        body = {}
        body["zone"] = zone
        
        if status:
            body['status'] = status
        if disks:
            body['disks'] = disks
        if desktop_group:
            body['desktop_group'] = desktop_group
        if user:
            body['user'] = user
        if desktop:
            body['desktop'] = desktop
        if disk_type is not None:
            body['disk_type'] = disk_type
        if disk_config:
            body["disk_config"] = disk_config
        if search_word:
            body['search_word'] = search_word
        if verbose is not None:
            body['verbose'] = verbose
        if owner:
            body['owner'] = owner
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        return self._build_params(action, body) 
    
    def resize_desktop_disks(self, zone,
                                    disks,
                                    size,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_RESIZE_DESKTOP_DISKS
        body = {}
        body["zone"] = zone
        body['disks'] = disks
        body['size'] = size

        return self._build_params(action, body)
 
    def modify_desktop_disk_attributes(self, zone,
                                       disk,
                                       disk_name = None,
                                       description = None,
                                       **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_DISK_ATTRIBUTES
        body = {}
        body['disk'] = disk 
        if disk_name:
            body['disk_name'] = disk_name
        if description:
            body['description'] = description
        
        return self._build_params(action, body) 
 
    def desktop_join_networks(self, zone,
                                     desktops,
                                     network,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESKTOP_JOIN_NETWORKS
        body = {}
        body["zone"] = zone
        body['desktops'] = desktops
        body['network'] = network

        return self._build_params(action, body) 

    def desktop_leave_networks(self, zone,
                                     desktops,
                                     network,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESKTOP_LEAVE_NETWORKS
        body = {}
        body["zone"] = zone
        body['desktops'] = desktops
        body['network'] = network

        return self._build_params(action, body)

    def modify_desktop_ip(self, zone,
                                     desktop,
                                     network,
                                     private_ip,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_IP
        body = {}
        body["zone"] = zone
        body['desktop'] = desktop
        body['network'] = network

        body['private_ip'] = private_ip

        return self._build_params(action, body) 

    def describe_desktop_jobs(self, zone,
                                    jobs = None,
                                    status = None,
                                    reverse = None,
                                    sort_key = None,
                                    offset = None,
                                    limit = 100,
                                    search_word = None,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_JOBS
        body = {}
        body["zone"] = zone
        
        if status:
            body['status'] = status
        if jobs:
            body['jobs'] = jobs

        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        return self._build_params(action, body) 

    def describe_desktop_tasks(self, zone,
                                    jobs = None,
                                    tasks=None,
                                    status = None,
                                    reverse = None,
                                    sort_key = None,
                                    offset = None,
                                    limit = 100,
                                    search_word = None,
                                    **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_TASKS
        body = {}
        body["zone"] = zone
        
        if status:
            body['status'] = status
        if jobs:
            body['jobs'] = jobs
        if tasks:
            body["tasks"] = tasks

        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key
        return self._build_params(action, body) 

    def get_desktop_monitor(self, zone,
                    resource,
                    meters,
                    step,
                    start_time,
                    end_time,
                    **params):
        '''
            @param resource: the ID of resource whose monitoring data you want to get.
            @param meters: a list of metering types you want to get.
                           e.g. "cpu", "disk_rd-<volume id>", "disk_wr-<volume id>",
                                "if_rx-<mac address>", "if_tx-<mac address>"
            @param step: the metering time step. e.g. "10s", "1m", "5m", "15m", "30m",
                         "1h", "2h", "1d"
            @param start_time: the starting time stamp. 
            @param end_time: the ending time stamp.  
        '''
        action = ACTION_VDI_GET_DESKTOP_MONITOR
        body = {}
        body["zone"] = zone
        if resource:
            body['resource'] = resource
        if meters:
            body['meters'] = meters
        if step:
            body['step'] = step
        if start_time:
            body['start_time'] = start_time
        if end_time:
            body['end_time'] = end_time

        return self._build_params(action, body)

    def create_desktop_image(self, zone,
                                   desktop_image,
                                   instance_class,
                                   cpu,
                                   memory,
                                   image_size=None,
                                   network = None,
                                   private_ip = None,
                                   image_name = None,
                                   description = None,
                                   **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_CREATE_DESKTOP_IMAGE
        body = {}
        body["zone"] = zone
        body["instance_class"] = instance_class
        body['desktop_image'] = desktop_image
        body["cpu"] = cpu
        body["memory"] = memory
        
        if image_size:
            body["image_size"] = image_size
        
        if network:
            body["network"] = network
        if private_ip:
            body["private_ip"] = private_ip
        if image_name:
            body['image_name'] = image_name
        if description:
            body['description'] = description

        return self._build_params(action, body)


    def save_desktop_images(self, zone,
                                  desktop_images,
                                  **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_SAVE_DESKTOP_IMAGES
        body = {}
        body["zone"] = zone
        body['desktop_images'] = desktop_images

        return self._build_params(action, body) 

    def describe_desktop_images(self, zone,
                                      desktop_images = None,
                                      image_type = None,
                                      status = None,
                                      os_version=None,
                                      session_type=None,
                                      reverse = None,
                                      sort_key = None,
                                      offset = None,
                                      limit = 20,
                                      search_word = None,
                                      verbose = 0,
                                      owner = None,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_DESKTOP_IMAGES
        body = {}
        body["zone"] = zone
        if desktop_images:
            body['desktop_images'] = desktop_images
        if image_type:
            body['image_type'] = image_type
        if status:
            body['status'] = status
        if os_version:
            body["os_version"] = os_version
        if session_type:
            body["session_type"] = session_type
        if search_word:
            body['search_word'] = search_word
        if verbose is not None:
            body['verbose'] = verbose
        if owner:
            body['owner'] = owner
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)
        if reverse is not None:
            body['reverse'] = reverse
        if sort_key:
            body['sort_key'] = sort_key

        return self._build_params(action, body) 
    
    def delete_desktop_images(self, zone,
                                      desktop_images,
                                      **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DELETE_DESKTOP_IMAGES
        body = {}
        body["zone"] = zone
        body['desktop_images'] = desktop_images

        return self._build_params(action, body)

    def modify_desktop_image_attributes(self, zone,
                                              desktop_image,
                                              image_name = None,
                                              description = None,
                                              **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_MODIFY_DESKTOP_IMAGE_ATTRIBUTES
        body = {}
        body["zone"] = zone
        body['desktop_image'] = desktop_image
        if image_name:
            body['image_name'] = image_name
        if description is not None:
            body['description'] = description

        return self._build_params(action, body)

    def describe_system_images(self, zone,
                                     images=None,
                                     provider=None,
                                     os_family=None,
                                     offset = None,
                                     limit = None,
                                     search_word = None,
                                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DESCRIBE_SYSTEM_IMAGES

        body = {}
        body["zone"] = zone
        if images:
            body["images"] = images
        if provider:
            body['provider'] = provider
        if os_family:
            body['os_family'] = os_family
        if search_word:
            body['search_word'] = search_word
        if offset is not None:
            body['offset'] = int(offset)
        if limit is not None:
            body['limit'] = int(limit)

        return self._build_params(action, body)

    def load_system_images(self, zone,
                                 images,
                                 session_type=None,
                                 image_name=None,
                                 os_version=None,
                                 **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_LOAD_SYSTEM_IMAGES
        body = {}
        body["zone"] = zone
        body['images'] = images
        if session_type:
            body["session_type"] = session_type
        
        if image_name:
            body["image_name"] = image_name
    
        if os_version:
            body["os_version"] = os_version

        return self._build_params(action, body)

    def describe_scheduler_tasks(self, zone,
                                  scheduler_tasks=None,
                                  task_name=None,
                                  resources=None,
                                  task_type=None,
                                  status=None,
                                  search_word=None,
                                  sort_key=None,
                                  reverse=None,
                                  verbose=None,
                                  offset=0,
                                  limit=20,
                                  **ignore):

        action = ACTION_VDI_DESCRIBE_SCHEDULER_TASKS
        valid_keys = ['zone', 'scheduler_tasks', 'task_name', 'resources', 'task_type', 'status',
                'verbose', 'search_word', 'offset', 'limit', 'reverse', 'sort_key']

        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def create_scheduler_task(self, zone,
                               task_type,
                               repeat,
                               hhmm,
                               task_name=None,
                               resource_type=None,
                               ymd=None,
                               period=None,
                               description=None,
                               resources=None,
                               term_time=None,
                               **ignore):
        ''' CreateScheduler
            @param zone - which availability zone the request will be send to.
            @param repeat - if is repeatable scheduler, 0: only once, 1: repeat.
            @param ymd - date to run tasks when run only once, formatted as `yyyy-mm-dd`.
            @param hhmm - time to run tasks, formatted as `hh:mm`.
            @param period - if is repeatable scheduler, set repeat period: daily, weekly, monthly.
            @param scheduler_name - the name of scheduler.
            @param description - more detail description of scheduler.
            @param notify_event - a bitflag (integer) for when to notify: task_success | task_fail
            @param notification_lists - an array of notification list IDs.
        '''
        action = ACTION_VDI_CREATE_SCHEDULER_TASK
        repeat = int(bool(repeat)) # 0 or 1
        valid_keys = ['zone', 'repeat', 'ymd', 'hhmm', 'period', 
                      'task_name', 'task_type', 'description', 'term_time', 'resources', 'resource_type']
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def modify_scheduler_task_attributes(self, zone,
                                          scheduler_task,
                                          task_name=None,
                                          description=None,
                                          repeat=None,
                                          period=None,
                                          ymd=None,
                                          hhmm=None,
                                          term_time=None,
                                          **ignore):
        ''' ModifySchedulerAttributes
            @param zone - which availability zone the request will be send to.
            @param scheduler- the ID of scheduler.
            @param scheduler_name - the name of.
            @param description - more detail description of.
            @param repeat - if is repeatable scheduler, 0: only once, 1: repeat.
            @param ymd - date to run tasks when run only once, formatted as `yyyy-mm-dd`.
            @param hhmm - time to run tasks, formatted as `hh:mm`.
            @param period - if is repeatable scheduler, set repeat period: daily, weekly, monthly.
            @param notify_event - a bitflag (integer) for when to notify: task_success | task_fail
            @param notification_lists - an array of notification list IDs.
        '''
        action = ACTION_VDI_MODIFY_SCHEDULER_TASK_ATTRIBUTES
        if repeat is not None:
            repeat = int(bool(repeat)) # 0 or 1
        valid_keys = ['zone', 'scheduler_task', 'repeat', 'ymd', 'hhmm', 'period', 'term_time',
                'task_name', 'description']
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def delete_scheduler_tasks(self, zone,
                                scheduler_tasks,
                                **ignore):
        ''' DeleteSchedulers
            @param zone - which availability zone the request will be send to.
            @param schedulers: the array of IDs of scheduler.
        '''
        action = ACTION_VDI_DELETE_SCHEDULER_TASKS
        valid_keys = ['zone', 'scheduler_tasks']
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def describe_scheduler_task_history(self, zone,
                                         scheduler_task,
                                         resources = None,
                                         verbose=0,
                                         offset=0,
                                         limit=20,
                                         **ignore):
        ''' DescribeSchedulerHistory
            @param scheduler: the ID of scheduler.
            @param scheduler_task: the ID of scheduler task.
            @param verbose: the number to specify the verbose level, larger the number, the more detailed information will be returned.
            @param limit: specify the number of the returning results.
            @param zone - which availability zone the request will be send to.
        '''
        action = ACTION_VDI_DESCRIBE_SCHEDULER_TASK_HISTORY
        valid_keys = ['zone', 'scheduler_task', 'resources',
                'verbose', 'offset', 'limit']
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def add_resource_to_scheduler_task(self, zone,
                                          scheduler_task,
                                          resources,
                                          **ignore):
        ''' AddSchedulerTasks
            @param zone - which availability zone the request will be send to.
            @param scheduler: the ID of scheduler.
            @param scheduler_tasks: a list of tasks you want to add.
        '''
        action = ACTION_VDI_ADD_RESOURCE_TO_SCHEDULER_TASK
        valid_keys = ['zone', 'scheduler_task', 'resources']
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def delete_resource_from_scheduler_task(self, zone,
                                          scheduler_task,
                                          resources,
                                          **ignore):
        ''' AddSchedulerTasks
            @param zone - which availability zone the request will be send to.
            @param scheduler: the ID of scheduler.
            @param scheduler_tasks: a list of tasks you want to add.
        '''
        action = ACTION_VDI_DELETE_RESOURCE_FROM_SCHEDULER_TASK
        valid_keys = ['zone', 'scheduler_task', 'resources']
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def set_scheduler_task_status(self, zone,
                                       scheduler_tasks,
                                       status,
                                       **ignore):
        ''' ActivateSchedulerTasks
            @param zone - which availability zone the request will be send to.
            @param scheduler_tasks: the array of IDs of scheduler task.
        '''
        action = ACTION_VDI_SET_SCHEDULER_TASK_STATUS
        valid_keys = ['zone', 'scheduler_tasks', "status"]
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def execute_scheduler_task(self, zone,
                                     scheduler_task,
                                     **ignore):
        ''' ExecuteSchedulerTask
            @param zone - which availability zone the request will be send to.
            @param scheduler_task: the ID of scheduler task.
        '''
        action = ACTION_VDI_EXECUTE_SCHEDULER_TASK
        valid_keys = ['zone', 'scheduler_task']
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def get_scheduler_task_resources(self, zone,
                                      scheduler_task,
                                      resource_type=None,
                                      search_word=None,
                                      sort_key=None,
                                      reverse=None,
                                      offset=0,
                                      limit=20,
                                      **ignore):

        action = ACTION_VDI_GET_SCHEDULER_TASK_RESOURCES
        valid_keys = ['zone', 'scheduler_task', 'search_word', 'offset', 'limit', 'reverse', 'sort_key', "resource_type"]
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def modify_scheduler_resource_desktop_count(self, zone,
                                                      scheduler_task,
                                                      resource,
                                                      desktop_count,
                                                      **ignore):

        action = ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_COUNT
        valid_keys = ['zone', 'scheduler_task', "resource", "desktop_count"]
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def modify_scheduler_resource_desktop_image(self, zone,
                                                      scheduler_task,
                                                      resource,
                                                      desktop_image,
                                                      **ignore):

        action = ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_IMAGE
        valid_keys = ['zone', 'scheduler_task', "resource", "desktop_image"]
        body = self.filter_out_none(locals(), valid_keys)
        return self._build_params(action, body)

    def describe_system_config(self,
                               keys = None,
                               **params):
        action = ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_CONFIG
        body = {}
        if keys:
            body["keys"] = keys
        return self._build_params(action, body)

    def modify_system_config(self,
                             config_items,
                             **params):
        action = ACTION_VDI_MODIFY_DESKTOP_SYSTEM_CONFIG
        body = {}
        if config_items:
            body['config_items'] = config_items

        return self._build_params(action, body)
    
    def describe_base_system_config(self, **params):
        action = ACTION_VDI_DESCRIBE_DESKTOP_BASE_SYSTEM_CONFIG
        body = {}
        return self._build_params(action, body)

    def describe_desktop_system_logs(self,
                            system_log_ids=[],
                            user_id='', 
                            user_name='',
                            user_role='',
                            log_type=[],
                            action_name='',
                            columns=[],
                            sort_key='',
                            offset=-1,
                            limit=-1,
                            reverse=None,
                            search_word=None,
                            is_and=None,
                            **params):
        action = ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_LOGS
        body = {}
        if system_log_ids:
            body['system_log_ids'] = system_log_ids
        if user_id:
            body['user_id'] = user_id
        if user_name:
            body['user_name'] = user_name
        if user_role:
            body['user_role'] = user_role
        if log_type:
            body['log_type'] = log_type
        if action_name:
            body['action_name'] = action_name
        if columns:
            body['columns'] = columns
        if sort_key:
            body['sort_key'] = sort_key
        body['reverse'] = reverse
        if offset >= 0:
            body['offset'] = offset
        if limit >= 0:
            body['limit'] = limit
        
        if search_word:
            body["search_word"] = search_word
        if is_and:
            body['is_and'] = is_and
  
        return self._build_params(action, body)

    def create_syslog_server(self,
                             host,
                             port,
                             protocol,
                             runtime,
                             **params):
        action = ACTION_VDI_CREATE_SYSLOG_SERVER
        body = {}
        if host:
            body['host'] = host
        if port:
            body['port'] = port
        if protocol:
            body['protocol'] = protocol
        if runtime:
            body['runtime'] = runtime
        return self._build_params(action, body)

    def modify_syslog_server(self,
                             syslog_server,
                             host=None,
                             port=None,
                             protocol=None,
                             runtime=None,
                             status=None,
                             **params):
        action = ACTION_VDI_MODIFY_SYSLOG_SERVER
        body = {}
        if syslog_server:
            body['syslog_server'] = syslog_server
        if host:
            body['host'] = host
        if port:
            body['port'] = port
        if protocol:
            body['protocol'] = protocol
        if runtime:
            body['runtime'] = runtime
        if status:
            body['status'] = status
        return self._build_params(action, body)

    def delete_syslog_servers(self,
                              syslog_servers,
                              **params):
        action = ACTION_VDI_DELETE_SYSLOG_SERVERS
        body = {}
        if syslog_servers:
            body['syslog_servers'] = syslog_servers
        return self._build_params(action, body)

    def describe_syslog_servers(self,
                            syslog_servers=[],
                            host=None, 
                            protocol=None,
                            status=None,
                            port=None,
                            columns=[],
                            sort_key='',
                            offset=-1,
                            limit=-1,
                            reverse=None,
                            search_word=None,
                            is_and=None,
                            **params):
        action = ACTION_VDI_DESCRIBE_SYSLOG_SERVERS
        body = {}
        if syslog_servers:
            body['syslog_servers'] = syslog_servers
        if host:
            body['host'] = host
        if protocol:
            body['protocol'] = protocol
        if status:
            body['status'] = status
        if port:
            body['port'] = port
        if columns:
            body['columns'] = columns
        if sort_key:
            body['sort_key'] = sort_key
        body['reverse'] = reverse
        if offset >= 0:
            body['offset'] = offset
        if limit >= 0:
            body['limit'] = limit
        
        if search_word:
            body["search_word"] = search_word
        if is_and:
            body['is_and'] = is_and
        return self._build_params(action, body)

    def create_desktop_usb_policy(self,
                                  object_id,
                                  policy_type,
                                  priority,
                                  allow,
                                  class_id=None,
                                  vendor_id=None,
                                  product_id=None,
                                  version_id=None,
                                  **params):
        action = ACTION_VDI_CREATE_USB_PROLICY
        body = {}
        if object_id:
            body['object_id'] = object_id
        if policy_type:
            body['policy_type'] = policy_type
        if priority:
            body['priority'] = priority
        if allow in [0, 1]:
            body['allow'] = allow
        if class_id:
            body['class_id'] = class_id
        if vendor_id:
            body['vendor_id'] = vendor_id
        if product_id:
            body['product_id'] = product_id
        if version_id:
            body['version_id'] = version_id
        return self._build_params(action, body)


    def modify_desktop_usb_policy(self,
                                  usb_policy_id,
                                  priority=None,
                                  allow=None,
                                  class_id=None,
                                  vendor_id=None,
                                  product_id=None,
                                  version_id=None,
                                  **params):
        action = ACTION_VDI_MODIFY_USB_PROLICY
        body = {}
        if usb_policy_id:
            body['usb_policy_id'] = usb_policy_id
        if priority:
            body['priority'] = priority
        if allow != None:
            body['allow'] = allow
        if class_id:
            body['class_id'] = class_id
        if vendor_id:
            body['vendor_id'] = vendor_id
        if product_id:
            body['product_id'] = product_id
        if version_id:
            body['version_id'] = version_id
        return self._build_params(action, body)

    def delete_desktop_usb_policy(self,
                                  usb_policy_ids=[],
                                  **params):
        action = ACTION_VDI_DELETE_USB_PROLICY
        body = {}
        if usb_policy_ids:
            body['usb_policy_ids'] = usb_policy_ids
        return self._build_params(action, body)

    def describe_desktop_usb_policy(self,
                                  usb_policy_ids=None,
                                  object_ids=None,
                                  policy_type=None,
                                  priority=None,
                                  allow=None,
                                  class_id=None,
                                  vendor_id=None,
                                  product_id=None,
                                  version_id=None,
                                  columns=[],
                                  sort_key='',
                                  offset=-1,
                                  limit=-1,
                                  reverse=0,
                                  is_and=1,
                                  **params):
        action = ACTION_VDI_DESCRIBE_USB_PROLICY
        body = {}
        if usb_policy_ids:
            body['usb_policy_id'] = usb_policy_ids
        if object_ids:
            body['object_id'] = object_ids
        if policy_type:
            body['policy_type'] = policy_type
        if priority:
            body['priority'] = priority
        if allow:
            body['allow'] = allow
        if class_id:
            body['class_id'] = class_id
        if vendor_id:
            body['vendor_id'] = vendor_id
        if product_id:
            body['product_id'] = product_id
        if version_id:
            body['version_id'] = version_id
        if columns:
            body['columns'] = columns
        if sort_key:
            body['sort_key'] = sort_key
        if reverse == 1:
            body['reverse'] = True
        elif reverse == 0:
            body['reverse'] = False
        if offset >= 0:
            body['offset'] = offset
        if limit >= 0:
            body['limit'] = limit
        if is_and == 1:
            body['is_and'] = True
        elif is_and == 0:
            body['is_and'] = False
        return self._build_params(action, body)

    def describe_license(self, **params):
        action = ACTION_VDI_DESCRIBE_LICENSE
        return self._build_params(action, {})

    def update_license(self,
                       license_str,
                       **params):
        action = ACTION_VDI_UPDATE_LICENSE
        body = {}
        body['license_str'] = license_str
        return self._build_params(action, body)

    def modify_approvalnotice_config(self,
                            approval_notice='',
                            approval_notice_title='',
                            **params):
        action = ACTION_VDI_MODIFY_APPROVALNOTICE_CONFIG
        body = {}
        body['approval_notice'] = approval_notice
        body['approval_notice_title'] = approval_notice_title
        return self._build_params(action, body)

    def describe_approvalnotice_config(self, **params):
        action = ACTION_VDI_DESCRIBE_APPROVALNOTICE_CONFIG
        body = {}
        return self._build_params(action, body)

    def download_log(self,
                     date=None,
                     **params):
        '''
            @param directive : the dictionary of params
        '''
        action = ACTION_VDI_DOWNLOAD_LOG
        body = {}
        if date:
            body['date'] = date
        return self._build_params(action, body)

    def refresh_desktop_db(self,
                           db_type,
                           **params):

        action = ACTION_VDI_REFRESH_DESKTOP_DB
        body = {"db_type": db_type}

        return self._build_params(action, body)

    def create_app_desktop_group(self,
                                zone,
                                desktop_group_name,
                                managed_resource,
                                description=None,
                                is_load=None,
                                **params):

        action = ACTION_VDI_CREATE_APP_DESKTOP_GROUP
        body = {"zone": zone,"desktop_group_name": desktop_group_name, "managed_resource": managed_resource}

        if description:
            body["description"] = description
        
        if is_load is not None:
            body["is_load"] = is_load

        return self._build_params(action, body)

    def describe_app_computes(self,
                              zone,
                              search_word,
                              **params):

        action = ACTION_VDI_DESCRIBE_APP_COMPUTES
        body = {"zone": zone}
        body["search_word"] = search_word

        return self._build_params(action, body)

    def add_compute_to_desktop_group(self,
                                     zone,
                                     desktop_group,
                                     instance_id,
                                     **params):

        action = ACTION_VDI_ADD_COMPUTE_TO_DESKTOP_GROUP
        body = {"zone": zone,
                "desktop_group": desktop_group,
                "instance_id": instance_id,
                }

        return self._build_params(action, body)

    def describe_app_startmemus(self,zone,
                                delivery_group,
                                desktop,
                                **params):

        action = ACTION_VDI_DESCRIBE_APP_STARTMEMUS
        body = {"zone": zone,"delivery_group": delivery_group, "desktop": desktop}

        return self._build_params(action, body)

    def describe_broker_apps(self,
                             zone,
                             delivery_group=None,
                             broker_app_names=None,
                             broker_apps=None,
                             search_word=None,
                             filter_delivery_groups = None,
                             offset=0,
                             limit=100,
                           **params):

        action = ACTION_VDI_DESCRIBE_BROKER_APPS
        body = {"zone": zone}
        if delivery_group:
            body["delivery_group"] = delivery_group
        
        if broker_apps:
            body["broker_apps"] = broker_apps
        
        if search_word:
            body["search_word"] = search_word
        
        if broker_app_names:
            body["broker_app_names"] = broker_app_names
        
        if filter_delivery_groups:
            body["filter_delivery_groups"] = filter_delivery_groups
        
        if offset is not None:
            body["offset"] = offset

        if limit:
            body["limit"] = limit
        

        return self._build_params(action, body)

    def create_broker_apps(self, zone,
                           delivery_group,
                           desktop,
                           app_datas,
                           app_folder = None,
                           is_startmenu = None,
                           **params):

        action = ACTION_VDI_CREATE_BROKER_APPS
        body = {"zone": zone}
        body["delivery_group"] = delivery_group
        body["desktop"] = desktop
        body["app_datas"] = app_datas
        
        if is_startmenu is not None:
            body["is_startmenu"] = is_startmenu
        
        if app_folder:
            body["app_folder"] = app_folder

        return self._build_params(action, body)

    def modify_broker_app(self, zone,
                           broker_app,
                           admin_display_name=None,
                           normal_display_name = None,
                           description = None,
                           **params):

        action = ACTION_VDI_MODIFY_BROKER_APP
        body = {"zone": zone}
        body["broker_app"] = broker_app
        if admin_display_name:
            body["admin_display_name"] = admin_display_name
        
        if normal_display_name:
            body["normal_display_name"] = normal_display_name
        
        if description is not None:
            body["description"] = description

        return self._build_params(action, body)

    def delete_broker_apps(self, zone,
                           broker_apps,
                           **params):

        action = ACTION_VDI_DELETE_BROKER_APPS
        body = {"zone": zone, "broker_apps": broker_apps}

        return self._build_params(action, body)

    def attach_broker_app_to_delivery_group(self,
                                            zone,
                                            delivery_group,
                                            broker_apps=None,
                                            broker_app_groups=None,
                                            **params):

        action = ACTION_VDI_ATTACH_BROKER_APP_TO_DELIVERY_GROUP
        body = {"zone": zone, "delivery_group": delivery_group}
        
        if broker_apps:
            body["broker_apps"] = broker_apps
        
        if broker_app_groups:
            body["broker_app_groups"] = broker_app_groups

        return self._build_params(action, body)

    def detach_broker_app_from_delivery_group(self,
                                              zone,
                                              delivery_group,
                                              broker_apps=None,
                                              broker_app_groups=None,
                                              **params):

        action = ACTION_VDI_DETACH_BROKER_APP_FROM_DELIVERY_GROUP
        body = {"zone": zone}
        
        if broker_apps:
            body["broker_apps"] = broker_apps

        if broker_app_groups:
            body["broker_app_groups"] = broker_app_groups

        body["delivery_group"] = delivery_group

        return self._build_params(action, body)

    def delete_broker_folders(self,
                           db_type,
                           **params):

        action = ACTION_VDI_DELETE_BROKER_FOLDERS
        body = {"db_type": db_type}

        return self._build_params(action, body)
    
    def describe_broker_folers(self, 
                               zone,
                               **params):

        action = ACTION_VDI_DESCRIBE_BROKER_FOLDERS
        body = {"zone": zone}

        return self._build_params(action, body)

    def create_broker_folder(self,
                           db_type,
                           **params):

        action = ACTION_VDI_CREATE_BROKER_FOLDER
        body = {"db_type": db_type}

        return self._build_params(action, body)

    def create_broker_app_group(self,
                                zone,
                                broker_app_group_name,
                                description=None,
                                **params):

        action = ACTION_VDI_CREATE_BROKER_APP_GROUP
        body = {"zone": zone,"broker_app_group_name": unicode_to_string(broker_app_group_name)}

        if description is not None:
            body["description"] = description

        return self._build_params(action, body)

    def describe_broker_app_groups(self,
                                   zone,
                                   broker_app_groups=None,
                                   delivery_group=None,
                                   search_word=None,
                                   is_system=0,                                                         
                                   offset=0,
                                   limit=100,
                                   **params):

        action = ACTION_VDI_DESCRIBE_BROKER_APP_GROUPS
        body = {"zone": zone}
        if broker_app_groups:
            body["broker_app_groups"] = broker_app_groups
        
        if delivery_group:
            body["delivery_group"] = delivery_group
        
        if search_word:
            body["search_word"] = search_word
        
        if is_system:
            body["is_system"] = is_system

        if offset is not None:
            body["offset"] = offset

        if limit:
            body["limit"] = limit

        return self._build_params(action, body)

    def delete_broker_app_groups(self,
                                   zone,
                                   broker_app_groups,
                                   **params):

        action = ACTION_VDI_DELETE_BROKER_APP_GROUPS
        body = {"zone": zone, "broker_app_groups": broker_app_groups}

        return self._build_params(action, body)

    def attach_broker_app_to_app_group(self,
                                   zone,
                                   broker_apps,
                                   broker_app_group,
                                   **params):

        action = ACTION_VDI_ATTACH_BROKER_APP_TO_APP_GROUP
        body = {"zone": zone, "broker_apps": broker_apps, "broker_app_group": broker_app_group}

        return self._build_params(action, body)

    def detach_broker_app_from_app_group(self,
                                   zone,
                                   broker_apps,
                                   broker_app_group,
                                   **params):

        action = ACTION_VDI_DETACH_BROKER_APP_FROM_APP_GROUP
        body = {"zone": zone, "broker_apps": broker_apps, "broker_app_group": broker_app_group}

        return self._build_params(action, body)

    def refresh_broker_apps(self,
                                   zone,
                                   sync_type,
                                   **params):

        action = ACTION_VDI_REFRESH_BROKER_APPS
        body = {"zone": zone, "sync_type": sync_type}
        
        return self._build_params(action, body)