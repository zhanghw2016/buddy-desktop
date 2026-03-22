'''
Created on 2012-9-9

@author: yunify
'''
import re
import time
from constants import (
    CHANNEL_API, CHANNEL_INTERNAL, CHANNEL_SESSION,
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

    # vxnet
    ACTION_VDI_DESCRIBE_DESKTOP_NETWORKS,
    ACTION_VDI_CREATE_DESKTOP_NETWORK,
    ACTION_VDI_MODIFY_DESKTOP_NETWORK_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOP_NETWORKS,
    ACTION_VDI_DESCRIBE_SYSTEM_NETWORKS,
    ACTION_VDI_LOAD_SYSTEM_NETWORK,
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
    ACTION_VDI_DESKTOP_LEAVE_NETWORKS,
    ACTION_VDI_DESKTOP_JOIN_NETWORKS,
    ACTION_VDI_MODIFY_DESKTOP_IP,
    ACTION_VDI_GET_DESKTOP_MONITOR,
    
    # jobs
    ACTION_VDI_DESCRIBE_DESKTOP_JOBS,
    ACTION_VDI_DESCRIBE_DESKTOP_TASKS,
    # volume
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
    # security group
    ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_POLICYS,
    ACTION_VDI_CREATE_DESKTOP_SECURITY_POLICY,
    ACTION_VDI_MODIFY_DESKTOP_SECURITY_POLICY_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOP_SECURITY_POLICYS,
    ACTION_VDI_APPLY_DESKTOP_SECURITY_POLICY,
    
    ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_RULES,
    ACTION_VDI_ADD_DESKTOP_SECURITY_RULES,
    ACTION_VDI_REMOVE_DESKTOP_SECURITY_RULES,
    ACTION_VDI_MODIFY_DESKTOP_SECURITY_RULE_ATTRIBUTES,
    
    ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_IPSETS,
    ACTION_VDI_CREATE_DESKTOP_SECURITY_IPSET,
    ACTION_VDI_DELETE_DESKTOP_SECURITY_IPSETS,
    ACTION_VDI_MODIFY_DESKTOP_SECURITY_IPSET_ATTRIBUTES,
    ACTION_VDI_APPLY_DESKTOP_SECURITY_IPSET,

    ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_POLICYS,
    ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_IPSETS,
    ACTION_VDI_LOAD_SYSTEM_SECURITY_RULES,
    ACTION_VDI_LOAD_SYSTEM_SECURITY_IPSETS,

    # policy group
    ACTION_VDI_DESCRIBE_POLICY_GROUPS,
    ACTION_VDI_CREATE_POLICY_GROUP,
    ACTION_VDI_MODIFY_POLICY_GROUP_ATTRIBUTES,
    ACTION_VDI_DELETE_POLICY_GROUPS,
    ACTION_VDI_ADD_RESOURCE_TO_POLICY_GROUP,
    ACTION_VDI_REMOVE_RESOURCE_FROM_POLICY_GROUP,
    ACTION_VDI_ADD_POLICY_TO_POLICY_GROUP,
    ACTION_VDI_REMOVE_POLICY_FROM_POLICY_GROUP,
    ACTION_VDI_APPLY_POLICY_GROUP,
    ACTION_VDI_MODIFY_RESOURCE_GROUP_POLICY,
    #citrix policy
    ACTION_CREATE_CITRIX_POLICY,
    ACTION_CONFIG_CITRIX_POLICY_ITEM,
    ACTION_DESCRIBE_CITRIX_POLICY,
    ACTION_DESCRIBE_CITRIX_POLICY_ITEM ,
    ACTION_DESCRIBE_CITRIX_POLICY_CONFIG,
    ACTION_DELETE_CITRIX_POLICY,
    ACTION_MODIFY_CITRIX_POLICY,
    ACTION_RENAME_CITRIX_POLICY,  
    ACTION_REFRESH_CITRIX_POLICY,
    ACTION_SET_CITRIX_POLICY_PRIORITY,
    ACTION_DESCRIBE_CITRIX_POLICY_FILTER,
    ACTION_ADD_CITRIX_POLICY_FILTER,
    ACTION_MODIFY_CITRIX_POLICY_FILTER,
    ACTION_DELETE_CITRIX_POLICY_FILTER,     
    # snapshot
    ACTION_VDI_DESCRIBE_DESKTOP_SNAPSHOTS,
    ACTION_VDI_CREATE_DESKTOP_SNAPSHOTS,
    ACTION_VDI_DELETE_DESKTOP_SNAPSHOTS,
    ACTION_VDI_APPLY_DESKTOP_SNAPSHOTS,
    ACTION_VDI_MODIFY_DESKTOP_SNAPSHOT_ATTRIBUTES,
    ACTION_VDI_CAPTURE_DESKTOP_FROM_DESKTOP_SNAPSHOT,
    ACTION_VDI_CREATE_DISK_FROM_DESKTOP_SNAPSHOT,
    ACTION_VDI_DESCRIBE_SNAPSHOT_GROUPS,
    ACTION_VDI_CREATE_SNAPSHOT_GROUP,
    ACTION_VDI_MODIFY_SNAPSHOT_GROUP,
    ACTION_VDI_DELETE_SNAPSHOT_GROUPS,
    ACTION_VDI_ADD_RESOURCE_TO_SNAPSHOT_GROUP,
    ACTION_VDI_DELETE_RESOURCE_FROM_SNAPSHOT_GROUP,
    ACTION_VDI_DESCRIBE_SNAPSHOT_GROUP_SNAPSHOTS,
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
    # user

    ACTION_VDI_ENABLE_ZONE_USERS,
    ACTION_VDI_DISABLE_ZONE_USERS,
    ACTION_VDI_DESCRIBE_ZONE_USERS,
    ACTION_VDI_MODIFY_ZONE_USER_ROLE,
    ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_CONFIG,
    ACTION_VDI_MODIFY_DESKTOP_SYSTEM_CONFIG,
    ACTION_VDI_DESCRIBE_DESKTOP_BASE_SYSTEM_CONFIG,
    ACTION_VDI_CREATE_DESKTOP_USER_SESSION,
    ACTION_VDI_DELETE_DESKTOP_USER_SESSION,
    ACTION_VDI_CHECK_DESKTOP_USER_SESSION,
    ACTION_VDI_MODIFY_ZONE_USER_SCOPE,
    ACTION_VDI_DESCRIBE_ZONE_USER_SCOPE,
    ACTION_VDI_DESCRIBE_API_ACTIONS,
    ACTION_VDI_DESCRIBE_ZONE_USER_LOGIN_RECORD,
    # auth user
    ACTION_VDI_DESCRIBE_AUTH_USERS,
    ACTION_VDI_CREATE_AUTH_USER,
    ACTION_VDI_DELETE_AUTH_USERS,
    ACTION_VDI_MODIFY_AUTH_USER_ATTRIBUTES,
    ACTION_VDI_MODIFY_AUTH_USER_PASSWORD,
    ACTION_VDI_RESET_AUTH_USER_PASSWORD,
    ACTION_VDI_IMPORT_AUTH_USERS,

    # org unit
    ACTION_VDI_DESCRIBE_AUTH_OUS,
    ACTION_VDI_CREATE_AUTH_OU,
    ACTION_VDI_DELETE_AUTH_OU,
    ACTION_VDI_MODIFY_AUTH_OU_ATTRIBUTES,
    ACTION_VDI_CHANGE_AUTH_USER_IN_OU,

    # user group
    ACTION_VDI_DESCRIBE_AUTH_USER_GROUPS,
    ACTION_VDI_CREATE_AUTH_USER_GROUP,
    ACTION_VDI_MODIFY_AUTH_USER_GROUP_ATTRIBUTES,
    ACTION_VDI_DELETE_AUTH_USER_GROUPS,
    ACTION_VDI_ADD_AUTH_USER_TO_USER_GROUP,
    ACTION_VDI_REMOVE_AUTH_USER_FROM_USER_GROUP,
    ACTION_VDI_GET_ZONE_USER_ADMINS,
    
    ACTION_VDI_RENAME_AUTH_USER_DN,
    ACTION_VDI_SET_AUTH_USER_STATUS,
    # apply and approve
    ACTION_VDI_CREATE_DESKTOP_APPLY_FORM,
    ACTION_VDI_DESCRIBE_DESKTOP_APPLY_FORMS,
    ACTION_VDI_MODIFY_DESKTOP_APPLY_FORM,
    ACTION_VDI_DELETE_DESKTOP_APPLY_FORMS,
    ACTION_VDI_DEAL_DESKTOP_APPLY_FORM,
    # apply group
    ACTION_VDI_CREATE_RESOURCE_APPLY_GROUP,
    ACTION_VDI_MODIFY_RESOURCE_APPLY_GROUP,
    ACTION_VDI_DESCRIBE_RESOURCE_APPLY_GROUPS,
    ACTION_VDI_DELETE_RESOURCE_APPLY_GROUPS,
    ACTION_VDI_INSERT_USER_TO_APPLY_GROUP,
    ACTION_VDI_REMOVE_USER_FROM_APPLY_GROUP,
    ACTION_VDI_INSERT_RESOURCE_TO_APPLY_GROUP,
    ACTION_VDI_REMOVE_RESOURCE_FROM_APPLY_GROUP,
    # approve group
    ACTION_VDI_CREATE_RESOURCE_APPROVE_GROUP,
    ACTION_VDI_MODIFY_RESOURCE_APPROVE_GROUP,
    ACTION_VDI_DESCRIBE_RESOURCE_APPROVE_GROUPS,
    ACTION_VDI_DELETE_RESOURCE_APPROVE_GROUPS,
    ACTION_VDI_INSERT_USER_TO_APPROVE_GROUP,
    ACTION_VDI_REMOVE_USER_FROM_APPROVE_GROUP,
    ACTION_VDI_MAP_APPLY_GROUP_AND_APPROVE_GROUP,
    ACTION_VDI_UNMAP_APPLY_GROUP_AND_APPROVE_GROUP,
    ACTION_VDI_GET_APPROVE_USERS,
    # USB policy
    ACTION_VDI_CREATE_USB_PROLICY,
    ACTION_VDI_MODIFY_USB_PROLICY,
    ACTION_VDI_DELETE_USB_PROLICY,
    ACTION_VDI_DESCRIBE_USB_PROLICY,

    # license
    ACTION_VDI_UPDATE_LICENSE,
    ACTION_VDI_DESCRIBE_LICENSE,

    #log
    ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_LOGS,
    ACTION_VDI_CREATE_SYSLOG_SERVER,
    ACTION_VDI_MODIFY_SYSLOG_SERVER,
    ACTION_VDI_DELETE_SYSLOG_SERVERS,
    ACTION_VDI_DESCRIBE_SYSLOG_SERVERS,

    #component upgrade
    ACTION_VDI_DESCRIBE_COMPONENT_VERSION,
    ACTION_VDI_UPDATE_COMPONENT_VERSION,
    ACTION_VDI_EXECUTE_COMPONENT_UPGRADE,

    # guest
    ACTION_VDI_SEND_DESKTOP_MESSAGE,
    ACTION_VDI_SEND_DESKTOP_HOT_KEYS,
    ACTION_VDI_SEND_DESKTOP_NOTIFY,
    ACTION_VDI_CHECK_DESKTOP_AGENT_STATUS,
    ACTION_VDI_LOGIN_DESKTOP,
    ACTION_VDI_LOGOFF_DESKTOP,
    ACTION_VDI_ADD_DESKTOP_ACTIVE_DIRECTORY,
    ACTION_VDI_MODIFY_GUEST_SERVER_CONFIG,
    ACTION_VDI_DESCRIBE_SPICE_INFO,
    ACTION_VDI_DESCRIBE_GUEST_PROCESSES,
    ACTION_VDI_DESCRIBE_GUEST_PROGRAMS,
    ACTION_VDI_GUEST_JSON_RCP,

    # desktop maintainer
    ACTION_VDI_CREATE_DESKTOP_MAINTAINER,
    ACTION_VDI_MODIFY_DESKTOP_MAINTAINER_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOP_MAINTAINERS,
    ACTION_VDI_DESCRIBE_DESKTOP_MAINTAINERS,
    ACTION_VDI_GUEST_CHECK_DESKTOP_MAINTAINER,
    ACTION_VDI_APPLY_DESKTOP_MAINTAINER,
    ACTION_VDI_ATTACH_RESOURCE_TO_DESKTOP_MAINTAINER,
    ACTION_VDI_DETACH_RESOURCE_FROM_DESKTOP_MAINTAINER,
    ACTION_VDI_RUN_GUEST_SHELL_COMMAND,
    ACTION_VDI_DESCRIBE_GUEST_SHELL_COMMANDS,
    ACTION_VDI_GUEST_CHECK_SHELL_COMMAND,
    
    # delivery group
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
    
    # sync citrix
    ACTION_VDI_DESCRIBE_COMPUTER_CATALOGS,
    ACTION_VDI_LOAD_COMPUTER_CATALOGS,
    ACTION_VDI_DESCRIBE_COMPUTERS,
    ACTION_VDI_LOAD_COMPUTERS,
    ACTION_VDI_REFRESH_CITRIX_DESKTOPS,

    ACTION_VDI_DESCRIBE_DESKTOP_ZONES,
    ACTION_VDI_REFRESH_DESKTOP_ZONES,
    ACTION_VDI_CREATE_DESKTOP_ZONE,
    ACTION_VDI_MODIFY_DESKTOP_ZONE_ATTRIBUTES,
    ACTION_VDI_DELETE_DESKTOP_ZONES,
    ACTION_VDI_MODIFY_DESKTOP_ZONE_RESOURCE_LIMIT,
    ACTION_VDI_MODIFY_DESKTOP_ZONE_CONNECTION,
    ACTION_VDI_MODIFY_DESKTOP_ZONE_CITRIX_CONNECTION,
    # user desktop session
    ACTION_VDI_DESCRIBE_USER_DESKTOP_SESSION,
    ACTION_VDI_LOGOUT_USER_DESKTOP_SESSION,
    ACTION_VDI_MODIFY_USER_DESKTOP_SESSION,
	
    # radius
    ACTION_VDI_DESCRIBE_RADIUS_SERVICES,
    ACTION_VDI_CREATE_RADIUS_SERVICE,
    ACTION_VDI_MODIFY_RADIUS_SERVICE_ATTRIBUTES,
    ACTION_VDI_DELETE_RADIUS_SERVICES,
    ACTION_VDI_ADD_AUTH_RADIUS_USERS,
    ACTION_VDI_REMOVE_AUTH_RADIUS_USERS,
    ACTION_VDI_MODIFY_RADIUS_USER_ATTRIBUTES,
    ACTION_VDI_CHECK_RADIUS_TOKEN,

    ACTION_VDI_MODIFY_APPROVALNOTICE_CONFIG,
    ACTION_VDI_DESCRIBE_APPROVALNOTICE_CONFIG,

    #log
    ACTION_VDI_DOWNLOAD_LOG,
    # auth
    ACTION_VDI_DESCRIBE_AUTH_SERVICES,
    ACTION_VDI_CREATE_AUTH_SERVICE,
    ACTION_VDI_CHECK_AUTH_SERVICE_OUS,
    ACTION_VDI_MODIFY_AUTH_SERVICE_ATTRIBUTES,
    ACTION_VDI_DELETE_AUTH_SERVICES,
    ACTION_VDI_ADD_AUTH_SERVICE_TO_ZONE,
    ACTION_VDI_REMOVE_AUTH_SERVICE_FROM_ZONES,
    ACTION_VDI_REFRESH_AUTH_SERVICE,
    # notice push
    ACTION_VDI_DESCRIBE_NOTICE_PUSHS,
    ACTION_VDI_CREATE_NOTICE_PUSH,
    ACTION_VDI_MODIFY_NOTICE_PUSH_ATTRIBUTES,
    ACTION_VDI_DELETE_NOTICE_PUSHS,
    ACTION_VDI_MODIFY_NOTICE_PUSH_ZONE_USER,
    ACTION_VDI_SET_USER_NOTICE_READ,
    
    # password prompt
    ACTION_VDI_CREATE_PASSWORD_PROMPT_QUESTION,
    ACTION_VDI_MODIFY_PASSWORD_PROMPT_QUESTION,
    ACTION_VDI_DELETE_PASSWORD_PROMPT_QUESTION,
    ACTION_VDI_DESCRIBE_PASSWORD_PROMPT_QUESTION,
    ACTION_VDI_CREATE_PASSWORD_PROMPT_ANSWER,
    ACTION_VDI_MODIFY_PASSWORD_PROMPT_ANSWER,
    ACTION_VDI_DELETE_PASSWORD_PROMPT_ANSWER,
    ACTION_VDI_CHECK_PASSWORD_PROMPT_ANSWER,
    ACTION_VDI_DESCRIBE_PASSWORD_PROMPT_HAVE_ANSWER,
    ACTION_VDI_DESCRIBE_HAVE_PASSWORD_ANSWER_USERS,
    ACTION_VDI_IGNORE_PASSWORD_PROMPT_QUESTION,

    # software
    ACTION_VDI_DESCRIBE_SOFTWARES,
    ACTION_VDI_UPLOAD_SOFTWARES,
    ACTION_VDI_DOWNLOAD_SOFTWARES,
    ACTION_VDI_DELETE_SOFTWARES,
    ACTION_VDI_CHECK_SOFTWARE_VNAS_NODE_DIR,

    # terminal management
    ACTION_VDI_DESCRIBE_TERMINAL_MANAGEMENTS,
    ACTION_VDI_MODIFY_TERMINAL_MANAGEMENT_ATTRIBUTES,
    ACTION_VDI_DELETE_TERMINAL_MANAGEMENTS,
    ACTION_VDI_RESTART_TERMINALS,
    ACTION_VDI_STOP_TERMINALS,

    ACTION_VDI_DESCRIBE_TERMINAL_GROUPS,
    ACTION_VDI_CREATE_TERMINAL_GROUP,
    ACTION_VDI_MODIFY_TERMINAL_GROUP_ATTRIBUTES,
    ACTION_VDI_DELETE_TERMINAL_GROUPS,
    ACTION_VDI_ADD_TERMINAL_TO_TERMINAL_GROUP,
    ACTION_VDI_DELETE_TERMINAL_FROM_TERMINAL_GROUP,
    ACTION_VDI_DESCRIBE_MASTER_BACKUP_IPS,
    ACTION_VDI_DESCRIBE_CBSERVER_HOSTS,

    # module_custom
    ACTION_VDI_DESCRIBE_USER_MODULE_CUSTOMS,
    ACTION_VDI_CREATE_USER_MODULE_CUSTOM,
    ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_ATTRIBUTES,
    ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_CONFIGS,
    ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_ZONE_USER,
    ACTION_VDI_DELETE_USER_MODULE_CUSTOMS,
    ACTION_VDI_DESCRIBE_SYSTEM_MODULE_TYPES,

    #system_custom
    ACTION_VDI_DESCRIBE_SYSTEM_CUSTOM_CONFIGS,
    ACTION_VDI_MODIFY_SYSTEM_CUSTOM_CONFIG_ATTRIBUTES,
    ACTION_VDI_RESET_SYSTEM_CUSTOM_CONFIGS,

    # desktop_service_management
    ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_MANAGEMENTS,
    ACTION_VDI_MODIFY_DESKTOP_SERVICE_MANAGEMENT_ATTRIBUTES,
    ACTION_VDI_REFRESH_DESKTOP_SERVICE_MANAGEMENT,
    ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_INSTANCES,
    ACTION_VDI_LOAD_DESKTOP_SERVICE_INSTANCES,
    ACTION_VDI_REMOVE_DESKTOP_SERVICE_INSTANCES,
    # workflow
    ACTION_VDI_DESCRIBE_WORKFLOW_SERVICE_ENV,
    ACTION_VDI_DESCRIBE_WORKFLOW_SERVICES,
    ACTION_VDI_DESCRIBE_WORKFLOW_MODELS,
    ACTION_VDI_CREATE_WORKFLOW_MODEL,
    ACTION_VDI_MODIFY_WORKFLOW_MODEL_ATTRIBUTES,
    ACTION_VDI_DELETE_WORKFLOW_MODELS,
    
    ACTION_VDI_DESCRIBE_WORKFLOWS,
    ACTION_VDI_CREATE_WORKFLOWS,
    ACTION_VDI_MODIFY_WORKFLOW_ATTRIBUTES,
    ACTION_VDI_DELETE_WORKFLOWS,
    ACTION_VDI_EXECUTE_WORKFLOWS,
    ACTION_VDI_DESCRIBE_WORKFLOW_MODEL_CONFIGS,
    ACTION_VDI_CREATE_WORKFLOW_MODEL_CONFIG,
    ACTION_VDI_MODIFY_WORKFLOW_MODEL_CONFIG,
    ACTION_VDI_DELETE_WORKFLOW_MODEL_CONFIGS,
    ACTION_VDI_SEND_DESKTOP_REQUEST,

    # instance_class
    ACTION_VDI_DESCRIBE_INSTANCE_CLASS_DISK_TYPE,

    # gpu_class
    ACTION_VDI_DESCRIBE_GPU_CLASS_TYPE,
    ACTION_VDI_CHECK_NETWORK_CONNECTION,
    ACTION_VDI_CHECK_GPU_CONFIG,

    # file_share
    ACTION_VDI_DESCRIBE_FILE_SHARE_GROUPS,
    ACTION_VDI_CREATE_FILE_SHARE_GROUP,
    ACTION_VDI_MODIFY_FILE_SHARE_GROUP_ATTRIBUTES,
    ACTION_VDI_RENAME_FILE_SHARE_GROUP,
    ACTION_VDI_DELETE_FILE_SHARE_GROUPS,
    ACTION_VDI_MODIFY_FILE_SHARE_GROUP_ZONE_USER,

    ACTION_VDI_DESCRIBE_FILE_SHARE_GROUP_FILES,
    ACTION_VDI_UPLOAD_FILE_SHARE_GROUP_FILES,
    ACTION_VDI_DOWNLOAD_FILE_SHARE_GROUP_FILES,
    ACTION_VDI_MODIFY_FILE_SHARE_GROUP_FILE_ATTRIBUTES,
    ACTION_VDI_DELETE_FILE_SHARE_GROUP_FILES,
    ACTION_VDI_DESCRIBE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY,

    ACTION_VDI_DESCRIBE_FILE_SHARE_CAPACITY,
    ACTION_VDI_CHANGE_FILE_IN_FILE_SHARE_GROUP,
    ACTION_VDI_DESCRIBE_FILE_SHARE_RECYCLES,
    ACTION_VDI_RESTORE_FILE_SHARE_RECYCLES,
    ACTION_VDI_DELETE_PERMANENTLY_FILE_SHARE_RECYCLES,
    ACTION_VDI_EMPTY_FILE_SHARE_RECYCLES,

    ACTION_VDI_CREATE_FILE_SHARE_SERVICE,
    ACTION_VDI_LOAD_FILE_SHARE_SERVICE,
    ACTION_VDI_DESCRIBE_FILE_SHARE_SERVICES,
    ACTION_VDI_MODIFY_FILE_SHARE_SERVICE_ATTRIBUTES,
    ACTION_VDI_DELETE_FILE_SHARE_SERVICES,
    ACTION_VDI_REFRESH_FILE_SHARE_SERVICE,
    ACTION_VDI_DESCRIBE_FILE_SHARE_SERVICE_VNAS,
    ACTION_VDI_RESET_FILE_SHARE_SERVICE_PASSWORD,

)

from request.internal_request import InternalRequest
from request.api_request import APIRequest
from request.session_request import SessionRequest
from common import return_error, return_success
from common import is_console_admin_user, is_admin_console
import resource_control.permission as ResourcePermission
from constants import LONG_HANDLE_TIME
import error.error_msg as ErrorMsg
import error.error_code as ErrorCodes
from error.error import Error
from utils.json import json_load
from utils.misc import format_params
from log.logger import logger
from server.shutdown.helper import handle_sync_message
import handlers.desktop.desktop_handler as DesktopHandler
import handlers.desktop.desktop_group_handler as DesktopGroupHandler
import handlers.desktop.network_handler as NetworkHandler
import handlers.desktop.image_handler as ImagekHandler
import handlers.desktop.disk_handler as DiskHandler
import handlers.desktop.job_handler as JobkHandler
import handlers.user.user_handler as UserHandler

import handlers.auth.auth_user_handler as AuthUserHandler
import handlers.user.apply_approve_handler as ApplyApproveHandler
import handlers.system_config_handler as SystemConfigHandler
import handlers.session_handler as SessionHandler
import handlers.guest.guest_handler as GuestHandler
import handlers.guest.desktop_maintainer_handler as DesktopMaintainerHandler
import handlers.citrix.delivery_group_handler as DeliveryGroupHandler
import handlers.policy.policy_group_handler as PolicyGroupHandler
import handlers.policy.security_policy_handler as SecurityPolicyHandler
import handlers.policy.snapshot_handler as SnapshotHandler
import handlers.policy.scheduler_task_handler as SchedulerTaskHandler
import handlers.citrix.sync_citrix_handler as SyncCitrixHandler
import handlers.policy.usb_handler as UsbHandler
import handlers.license_handler as LicenseHandler
import handlers.citrix.desktop_session_handler as DesktopSession
import handlers.auth.radius_handler as RadiusHandler
import handlers.component_version_handler as ComponentVersion
import handlers.zone.zone_handler as ZoneHandler
import handlers.auth.auth_service_handler as AuthServiceHandler
import handlers.system.notice_push_handler as NoticePushHandler
import handlers.auth.password_prompt_handler as PasswordPrompt
import handlers.system.software_handler as SoftwareHandler
import handlers.terminal.terminal_handler as TerminalHandler
import handlers.module_custom.module_custom_handler as ModuleCustomHandler
import handlers.system_custom.system_custom_handler as SystemCustomHandler
import handlers.desktop_service_management.desktop_service_management_handler as DesktopServiceManagementHandler
import handlers.syslog_server_handler as SyslogServerHandler
import handlers.workflow.workflow_handler as WorkflowHandler
import handlers.file_share.file_share_handler as FileShareHandler
import handlers.citrix.virtual_app_handler as VirtualAPPHandler 
import handlers.policy.citrix_policy_handler as CitrixPolicyHandler
class ServiceHandler(object):
    ''' front gate - service handler '''

    def __init__(self):

        self.handler_map = {
            # desktop group
            ACTION_VDI_DESCRIBE_DESKTOP_GROUPS: DesktopGroupHandler.handle_describe_desktop_groups,
            ACTION_VDI_CREATE_DESKTOP_GROUP: DesktopGroupHandler.handle_create_desktop_group,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_ATTRIBUTES: DesktopGroupHandler.handle_modify_desktop_group_attributes,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_IMAGE: DesktopGroupHandler.handle_modify_desktop_group_image,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_DESKTOP_COUNT: DesktopGroupHandler.handle_modify_desktop_group_desktop_count,
            ACTION_VDI_DELETE_DESKTOP_GROUPS: DesktopGroupHandler.handle_delete_desktop_groups,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_STATUS: DesktopGroupHandler.handle_modify_desktop_group_status,
            ACTION_VDI_DESCRIBE_DESKTOP_GROUP_DISKS: DesktopGroupHandler.handle_describe_desktop_group_disks,
            ACTION_VDI_CREATE_DESKTOP_GROUP_DISK: DesktopGroupHandler.handle_create_desktop_group_disk,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_DISK: DesktopGroupHandler.handle_modify_desktop_group_disk,
            ACTION_VDI_DELETE_DESKTOP_GROUP_DISKS: DesktopGroupHandler.handle_delete_desktop_group_disks,
            ACTION_VDI_DESCRIBE_DESKTOP_GROUP_NETWORKS: DesktopGroupHandler.handle_describe_desktop_group_networks,
            ACTION_VDI_CREATE_DESKTOP_GROUP_NETWORK: DesktopGroupHandler.handle_create_desktop_group_network,
            ACTION_VDI_MODIFY_DESKTOP_GROUP_NETWORK: DesktopGroupHandler.handle_modify_desktop_group_network,
            ACTION_VDI_DELETE_DESKTOP_GROUP_NETWORKS: DesktopGroupHandler.handle_delete_desktop_group_networks,
            ACTION_VDI_ATTACH_USER_TO_DESKTOP_GROUP: DesktopGroupHandler.handle_attach_user_to_desktop_group,
            ACTION_VDI_DETACH_USER_FROM_DESKTOP_GROUP: DesktopGroupHandler.handle_detach_user_from_desktop_group,
            ACTION_VDI_SET_DESKTOP_GROUP_USER_STATUS: DesktopGroupHandler.handle_set_desktop_group_user_status,
            ACTION_VDI_APPLY_DESKTOP_GROUP: DesktopGroupHandler.handle_apply_desktop_group,
            ACTION_VDI_DESCRIBE_DESKTOP_GROUP_USERS: DesktopGroupHandler.handle_describe_desktop_group_users,
            ACTION_VDI_DESCRIBE_DESKTOP_IPS: DesktopGroupHandler.handle_describe_desktop_ips,
            # network
            ACTION_VDI_DESCRIBE_DESKTOP_NETWORKS: NetworkHandler.handle_describe_desktop_networks,
            ACTION_VDI_CREATE_DESKTOP_NETWORK: NetworkHandler.handle_create_desktop_network,
            ACTION_VDI_MODIFY_DESKTOP_NETWORK_ATTRIBUTES: NetworkHandler.handle_modify_desktop_network_attributes,
            ACTION_VDI_DELETE_DESKTOP_NETWORKS: NetworkHandler.handle_delete_desktop_networks,
            ACTION_VDI_DESCRIBE_SYSTEM_NETWORKS: NetworkHandler.handle_describe_system_networks,
            ACTION_VDI_LOAD_SYSTEM_NETWORK: NetworkHandler.handle_load_system_network,
            ACTION_VDI_DESCRIBE_DESKTOP_ROUTERS: NetworkHandler.handle_describe_desktop_routers,
            
            # desktop
            ACTION_VDI_CREATE_DESKTOP: DesktopHandler.handle_create_desktop,
            ACTION_VDI_DESCRIBE_NORMAL_DESKTOPS: DesktopHandler.handle_describe_normal_desktops,
            ACTION_VDI_DESCRIBE_DESKTOPS: DesktopHandler.handle_describe_desktops,
            ACTION_VDI_MODIFY_DESKTOP_ATTRIBUTES: DesktopHandler.handle_modify_desktop_attributes,
            ACTION_VDI_DELETE_DESKTOPS: DesktopHandler.handle_delete_desktops,
            ACTION_VDI_ATTACH_USER_TO_DESKTOP: DesktopHandler.handle_attach_user_to_desktop,
            ACTION_VDI_DETACH_USER_FROM_DESKTOP: DesktopHandler.handle_detach_user_from_desktop,
            ACTION_VDI_RESTART_DESKTOPS: DesktopHandler.handle_restart_desktops,
            ACTION_VDI_START_DESKTOPS: DesktopHandler.handle_start_desktops,
            ACTION_VDI_STOP_DESKTOPS: DesktopHandler.handle_stop_desktops,
            ACTION_VDI_RESET_DESKTOPS: DesktopHandler.handle_reset_desktops,
            ACTION_VDI_SET_DESKTOP_MONITOR: DesktopHandler.handle_set_desktop_monitor,
            ACTION_VDI_SET_DESKTOP_AUTO_LOGIN: DesktopHandler.handle_set_desktop_auto_login,
            ACTION_VDI_MODIFY_DESKTOP_DESCRIPTION: DesktopHandler.handle_modify_desktop_description,
            ACTION_VDI_APPLY_RANDOM_DESKTOP: DesktopHandler.handle_apply_random_desktop,
            ACTION_VDI_FREE_RANDOM_DESKTOPS: DesktopHandler.handle_free_random_desktops,
            ACTION_VDI_CREATE_BROKERS: DesktopHandler.handle_create_brokers,
            ACTION_VDI_DELETE_BROKERS: DesktopHandler.handle_delete_brokers,
            ACTION_VDI_GET_DESKTOP_MONITOR: DesktopHandler.handle_get_desktop_monitor,
            ACTION_VDI_DESKTOP_LEAVE_NETWORKS: DesktopHandler.handle_desktop_leave_networks,
            ACTION_VDI_DESKTOP_JOIN_NETWORKS: DesktopHandler.handle_desktop_join_networks,
            ACTION_VDI_MODIFY_DESKTOP_IP: DesktopHandler.handle_modify_desktop_ip,
            ACTION_VDI_CHECK_DESKTOP_HOSTNAME: DesktopHandler.handle_check_desktop_hostname,
            ACTION_VDI_REFRESH_DESKTOP_DB: DesktopHandler.handle_refresh_desktop_db,
            # app
            ACTION_VDI_CREATE_APP_DESKTOP_GROUP: VirtualAPPHandler.handle_create_app_desktop_group,
            ACTION_VDI_DESCRIBE_APP_COMPUTES: VirtualAPPHandler.handle_describe_app_computes,
            ACTION_VDI_ADD_COMPUTE_TO_DESKTOP_GROUP: VirtualAPPHandler.handle_add_compute_to_desktop_group,
            ACTION_VDI_DESCRIBE_APP_STARTMEMUS: VirtualAPPHandler.handle_describe_app_startmemus,
            ACTION_VDI_DESCRIBE_BROKER_APPS: VirtualAPPHandler.handle_describe_broker_apps,
            ACTION_VDI_CREATE_BROKER_APPS: VirtualAPPHandler.handle_create_broker_apps,
            ACTION_VDI_MODIFY_BROKER_APP: VirtualAPPHandler.handle_modify_broker_app,
            ACTION_VDI_DELETE_BROKER_APPS: VirtualAPPHandler.handle_delete_broker_apps,
            ACTION_VDI_ATTACH_BROKER_APP_TO_DELIVERY_GROUP: VirtualAPPHandler.handle_attach_broker_app_to_delivery_group,
            ACTION_VDI_DETACH_BROKER_APP_FROM_DELIVERY_GROUP: VirtualAPPHandler.handle_detach_broker_app_from_delivery_group,
            ACTION_VDI_CREATE_BROKER_FOLDER: VirtualAPPHandler.handle_create_broker_folder,
            ACTION_VDI_DELETE_BROKER_FOLDERS: VirtualAPPHandler.handle_delete_broker_folders,
            ACTION_VDI_DESCRIBE_BROKER_FOLDERS: VirtualAPPHandler.handle_describe_broker_folers,
            ACTION_VDI_CREATE_BROKER_APP_GROUP: VirtualAPPHandler.handle_create_broker_app_group,
            ACTION_VDI_DELETE_BROKER_APP_GROUPS: VirtualAPPHandler.handle_delete_broker_app_groups,
            ACTION_VDI_DESCRIBE_BROKER_APP_GROUPS: VirtualAPPHandler.handle_describe_broker_app_groups,
            ACTION_VDI_ATTACH_BROKER_APP_TO_APP_GROUP: VirtualAPPHandler.handle_attach_broker_app_to_app_group,
            ACTION_VDI_DETACH_BROKER_APP_FROM_APP_GROUP: VirtualAPPHandler.handle_detach_broker_app_from_app_group,
            ACTION_VDI_REFRESH_BROKER_APPS: VirtualAPPHandler.handle_refresh_broker_apps,
            # job
            ACTION_VDI_DESCRIBE_DESKTOP_JOBS: JobkHandler.handle_describe_desktop_jobs,
            ACTION_VDI_DESCRIBE_DESKTOP_TASKS: JobkHandler.handle_describe_desktop_tasks,

            # disk
            ACTION_VDI_CREATE_DESKTOP_DISKS: DiskHandler.handle_create_desktop_disks,
            ACTION_VDI_DELETE_DESKTOP_DISKS: DiskHandler.handle_delete_desktop_disks,
            ACTION_VDI_ATTACH_DISK_TO_DESKTOP: DiskHandler.handle_attach_disk_to_desktop,
            ACTION_VDI_DETACH_DISK_FROM_DESKTOP: DiskHandler.handle_detach_disk_from_desktop,
            ACTION_VDI_DESCRIBE_DESKTOP_DISKS: DiskHandler.handle_describe_desktop_disks,
            ACTION_VDI_RESIZE_DESKTOP_DISKS: DiskHandler.handle_resize_desktop_disks,
            ACTION_VDI_MODIFY_DESKTOP_DISK_ATTRIBUTES: DiskHandler.handle_modify_desktop_disk_attributes,
            # image
            ACTION_VDI_CREATE_DESKTOP_IMAGE: ImagekHandler.handle_create_desktop_image,
            ACTION_VDI_SAVE_DESKTOP_IMAGES: ImagekHandler.handle_save_desktop_images,
            ACTION_VDI_DESCRIBE_DESKTOP_IMAGES: ImagekHandler.handle_describe_desktop_images,
            ACTION_VDI_DELETE_DESKTOP_IMAGES: ImagekHandler.handle_delete_desktop_images,
            ACTION_VDI_MODIFY_DESKTOP_IMAGE_ATTRIBUTES: ImagekHandler.handle_modify_desktop_image_attributes,
            ACTION_VDI_DESCRIBE_SYSTEM_IMAGES: ImagekHandler.handle_describe_system_images,
            ACTION_VDI_LOAD_SYSTEM_IMAGES: ImagekHandler.handle_load_system_images,
            
            # policy group
            ACTION_VDI_DESCRIBE_POLICY_GROUPS: PolicyGroupHandler.handle_describe_policy_groups,
            ACTION_VDI_CREATE_POLICY_GROUP: PolicyGroupHandler.handle_create_policy_group,
            ACTION_VDI_MODIFY_POLICY_GROUP_ATTRIBUTES: PolicyGroupHandler.handle_modify_policy_group_attributes,
            ACTION_VDI_DELETE_POLICY_GROUPS: PolicyGroupHandler.handle_delete_policy_groups,
            ACTION_VDI_ADD_RESOURCE_TO_POLICY_GROUP: PolicyGroupHandler.handle_add_resource_to_policy_group,
            ACTION_VDI_REMOVE_RESOURCE_FROM_POLICY_GROUP: PolicyGroupHandler.handle_remove_resource_from_policy_group,
            ACTION_VDI_ADD_POLICY_TO_POLICY_GROUP: PolicyGroupHandler.handle_add_policy_to_policy_group,
            ACTION_VDI_REMOVE_POLICY_FROM_POLICY_GROUP: PolicyGroupHandler.handle_remove_policy_from_policy_group,
            ACTION_VDI_APPLY_POLICY_GROUP: PolicyGroupHandler.handle_apply_policy_group,
            ACTION_VDI_MODIFY_RESOURCE_GROUP_POLICY: PolicyGroupHandler.handle_modify_resource_group_policy,
            #citrix policy
            ACTION_CREATE_CITRIX_POLICY: CitrixPolicyHandler.handle_create_citrix_policy,
            ACTION_CONFIG_CITRIX_POLICY_ITEM: CitrixPolicyHandler.handle_config_citrix_policy_item,
            ACTION_DESCRIBE_CITRIX_POLICY: CitrixPolicyHandler.handle_describe_citrix_policy,
            ACTION_DESCRIBE_CITRIX_POLICY_ITEM : CitrixPolicyHandler.handle_describe_citrix_policy_item,
            ACTION_DESCRIBE_CITRIX_POLICY_CONFIG: CitrixPolicyHandler.handle_describe_citrix_policy_item_config,
            ACTION_DELETE_CITRIX_POLICY: CitrixPolicyHandler.handle_delete_citrix_policy,     
            ACTION_MODIFY_CITRIX_POLICY: CitrixPolicyHandler.handle_modify_citrix_policy, 
            ACTION_RENAME_CITRIX_POLICY: CitrixPolicyHandler.handle_rename_citrix_policy,   
            ACTION_REFRESH_CITRIX_POLICY: CitrixPolicyHandler.handle_refresh_citrix_policy, 
            ACTION_SET_CITRIX_POLICY_PRIORITY: CitrixPolicyHandler.handle_set_citrix_policy_priority,
            ACTION_DESCRIBE_CITRIX_POLICY_FILTER: CitrixPolicyHandler.handle_describe_citrix_policy_filter,
            ACTION_ADD_CITRIX_POLICY_FILTER: CitrixPolicyHandler.handle_add_citrix_policy_filter,
            ACTION_MODIFY_CITRIX_POLICY_FILTER: CitrixPolicyHandler.handle_modify_citrix_policy_filter,
            ACTION_DELETE_CITRIX_POLICY_FILTER: CitrixPolicyHandler.handle_delete_citrix_policy_filter,                        
            
            # security group
            ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_POLICYS: SecurityPolicyHandler.handle_describe_desktop_security_policys,
            ACTION_VDI_CREATE_DESKTOP_SECURITY_POLICY: SecurityPolicyHandler.handle_create_desktop_security_policy,
            ACTION_VDI_MODIFY_DESKTOP_SECURITY_POLICY_ATTRIBUTES: SecurityPolicyHandler.handle_modify_desktop_security_policy_attributes,
            ACTION_VDI_DELETE_DESKTOP_SECURITY_POLICYS: SecurityPolicyHandler.handle_delete_desktop_security_policys,
            ACTION_VDI_APPLY_DESKTOP_SECURITY_POLICY: SecurityPolicyHandler.handle_apply_desktop_security_policy,
    
            ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_RULES: SecurityPolicyHandler.handle_describe_desktop_security_rules,
            ACTION_VDI_ADD_DESKTOP_SECURITY_RULES: SecurityPolicyHandler.handle_add_desktop_security_rules,
            ACTION_VDI_REMOVE_DESKTOP_SECURITY_RULES: SecurityPolicyHandler.handle_remove_desktop_security_rules,
            ACTION_VDI_MODIFY_DESKTOP_SECURITY_RULE_ATTRIBUTES: SecurityPolicyHandler.handle_modify_desktop_security_rule_attributes,
            ACTION_VDI_DESCRIBE_DESKTOP_SECURITY_IPSETS: SecurityPolicyHandler.handle_describe_desktop_security_ipsets,
            ACTION_VDI_CREATE_DESKTOP_SECURITY_IPSET: SecurityPolicyHandler.handle_create_desktop_security_ipset,
            ACTION_VDI_DELETE_DESKTOP_SECURITY_IPSETS: SecurityPolicyHandler.handle_delete_desktop_security_ipsets,
            ACTION_VDI_MODIFY_DESKTOP_SECURITY_IPSET_ATTRIBUTES: SecurityPolicyHandler.handle_modify_desktop_security_ipset_attributes,
            ACTION_VDI_APPLY_DESKTOP_SECURITY_IPSET: SecurityPolicyHandler.handle_apply_desktop_security_ipset,

            ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_POLICYS: SecurityPolicyHandler.handle_describe_system_security_policys,
            ACTION_VDI_DESCRIBE_SYSTEM_SECURITY_IPSETS: SecurityPolicyHandler.handle_describe_system_security_ipsets,
            ACTION_VDI_LOAD_SYSTEM_SECURITY_RULES: SecurityPolicyHandler.handle_load_system_security_rules,
            ACTION_VDI_LOAD_SYSTEM_SECURITY_IPSETS: SecurityPolicyHandler.handle_load_system_security_ipsets,

            # snapshot
            ACTION_VDI_DESCRIBE_DESKTOP_SNAPSHOTS: SnapshotHandler.handle_describe_desktop_snapshots,
            ACTION_VDI_CREATE_DESKTOP_SNAPSHOTS: SnapshotHandler.handle_create_desktop_snapshots,
            ACTION_VDI_DELETE_DESKTOP_SNAPSHOTS: SnapshotHandler.handle_delete_desktop_snapshots,
            ACTION_VDI_APPLY_DESKTOP_SNAPSHOTS: SnapshotHandler.handle_apply_desktop_snapshots,
            ACTION_VDI_MODIFY_DESKTOP_SNAPSHOT_ATTRIBUTES: SnapshotHandler.handle_modify_desktop_snapshot_attributes,
            ACTION_VDI_CAPTURE_DESKTOP_FROM_DESKTOP_SNAPSHOT: SnapshotHandler.handle_capture_desktop_from_desktop_snapshot,
            ACTION_VDI_CREATE_DISK_FROM_DESKTOP_SNAPSHOT: SnapshotHandler.handle_create_disk_from_desktop_snapshot,
            # snapshot group
            ACTION_VDI_DESCRIBE_SNAPSHOT_GROUPS: SnapshotHandler.handle_describe_snapshot_groups,
            ACTION_VDI_CREATE_SNAPSHOT_GROUP: SnapshotHandler.handle_create_snapshot_group,
            ACTION_VDI_MODIFY_SNAPSHOT_GROUP: SnapshotHandler.handle_modify_snapshot_group,
            ACTION_VDI_DELETE_SNAPSHOT_GROUPS: SnapshotHandler.handle_delete_snapshot_groups,
            ACTION_VDI_ADD_RESOURCE_TO_SNAPSHOT_GROUP: SnapshotHandler.handle_add_resource_to_snapshot_group,
            ACTION_VDI_DELETE_RESOURCE_FROM_SNAPSHOT_GROUP: SnapshotHandler.handle_delete_resource_from_snapshot_group,
            ACTION_VDI_DESCRIBE_SNAPSHOT_GROUP_SNAPSHOTS: SnapshotHandler.handle_describe_snapshot_group_snapshots,

            # scheduler
            ACTION_VDI_DESCRIBE_SCHEDULER_TASKS: SchedulerTaskHandler.handle_describe_scheduler_tasks,
            ACTION_VDI_CREATE_SCHEDULER_TASK: SchedulerTaskHandler.handle_create_scheduler_task,
            ACTION_VDI_MODIFY_SCHEDULER_TASK_ATTRIBUTES: SchedulerTaskHandler.handle_modify_scheduler_task_attributes,
            ACTION_VDI_DELETE_SCHEDULER_TASKS: SchedulerTaskHandler.handle_delete_scheduler_tasks,
            ACTION_VDI_DESCRIBE_SCHEDULER_TASK_HISTORY: SchedulerTaskHandler.handle_describe_scheduler_task_history,
            ACTION_VDI_ADD_RESOURCE_TO_SCHEDULER_TASK: SchedulerTaskHandler.handle_add_resource_to_scheduler_task,
            ACTION_VDI_DELETE_RESOURCE_FROM_SCHEDULER_TASK: SchedulerTaskHandler.handle_delete_resource_from_scheduler_task,
            ACTION_VDI_SET_SCHEDULER_TASK_STATUS: SchedulerTaskHandler.handle_set_scheduler_task_status,
            ACTION_VDI_EXECUTE_SCHEDULER_TASK: SchedulerTaskHandler.handle_execute_scheduler_task,
            ACTION_VDI_GET_SCHEDULER_TASK_RESOURCES: SchedulerTaskHandler.handle_get_scheduler_task_resources,
            ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_COUNT: SchedulerTaskHandler.handle_modify_scheduler_resource_desktop_count,
            ACTION_VDI_MODIFY_SCHEDULER_RESOURCE_DESKTOP_IMAGE: SchedulerTaskHandler.handle_modify_scheduler_resource_desktop_image,
            # user
            ACTION_VDI_ENABLE_ZONE_USERS: UserHandler.handle_enable_zone_users,
            ACTION_VDI_DISABLE_ZONE_USERS: UserHandler.handle_disable_zone_users,
            ACTION_VDI_DESCRIBE_ZONE_USERS: UserHandler.handle_describe_zone_users,
            ACTION_VDI_MODIFY_ZONE_USER_ROLE: UserHandler.handle_modify_zone_user_role,
            ACTION_VDI_DESCRIBE_ZONE_USER_SCOPE: UserHandler.handle_describe_zone_user_scope,
            ACTION_VDI_MODIFY_ZONE_USER_SCOPE: UserHandler.handle_modify_zone_user_scope,
            ACTION_VDI_DESCRIBE_API_ACTIONS: UserHandler.handle_describe_api_actions,
            ACTION_VDI_GET_ZONE_USER_ADMINS: UserHandler.handle_get_zone_user_admins,
            ACTION_VDI_DESCRIBE_ZONE_USER_LOGIN_RECORD: UserHandler.handle_describe_zone_user_login_record,
            # user session
            ACTION_VDI_CREATE_DESKTOP_USER_SESSION: SessionHandler.handle_create_desktop_user_session,
            ACTION_VDI_DELETE_DESKTOP_USER_SESSION: SessionHandler.handle_delete_desktop_user_session,
            ACTION_VDI_CHECK_DESKTOP_USER_SESSION: SessionHandler.handle_check_desktop_user_session,
            # auth user
            ACTION_VDI_DESCRIBE_AUTH_USERS: AuthUserHandler.handle_describe_auth_users,
            ACTION_VDI_CREATE_AUTH_USER: AuthUserHandler.handle_create_auth_user,
            ACTION_VDI_DELETE_AUTH_USERS: AuthUserHandler.handle_delete_auth_users,
            ACTION_VDI_MODIFY_AUTH_USER_ATTRIBUTES: AuthUserHandler.handle_modify_auth_user_attributes,
            ACTION_VDI_MODIFY_AUTH_USER_PASSWORD: AuthUserHandler.handle_modify_auth_user_password,
            ACTION_VDI_RESET_AUTH_USER_PASSWORD: AuthUserHandler.handle_reset_auth_user_password,
            ACTION_VDI_IMPORT_AUTH_USERS: AuthUserHandler.handle_import_auth_users,
        
            # org unit
            ACTION_VDI_DESCRIBE_AUTH_OUS: AuthUserHandler.handle_describe_auth_ous,
            ACTION_VDI_CREATE_AUTH_OU: AuthUserHandler.handle_create_auth_ou,
            ACTION_VDI_DELETE_AUTH_OU: AuthUserHandler.handle_delete_auth_ou,
            ACTION_VDI_MODIFY_AUTH_OU_ATTRIBUTES: AuthUserHandler.handle_modify_auth_ou_attributes,
            ACTION_VDI_CHANGE_AUTH_USER_IN_OU: AuthUserHandler.handle_change_auth_user_in_ou,
        
            # user group
            ACTION_VDI_DESCRIBE_AUTH_USER_GROUPS: AuthUserHandler.handle_describe_auth_user_groups,
            ACTION_VDI_CREATE_AUTH_USER_GROUP: AuthUserHandler.handle_create_auth_user_group,
            ACTION_VDI_MODIFY_AUTH_USER_GROUP_ATTRIBUTES: AuthUserHandler.handle_modify_auth_user_group_attributes,
            ACTION_VDI_DELETE_AUTH_USER_GROUPS: AuthUserHandler.handle_delete_auth_user_groups,
            ACTION_VDI_ADD_AUTH_USER_TO_USER_GROUP: AuthUserHandler.handle_add_auth_user_to_user_group,
            ACTION_VDI_REMOVE_AUTH_USER_FROM_USER_GROUP: AuthUserHandler.handle_remove_auth_user_from_user_group,
            ACTION_VDI_RENAME_AUTH_USER_DN: AuthUserHandler.handle_rename_auth_user_dn,
            ACTION_VDI_SET_AUTH_USER_STATUS: AuthUserHandler.handle_set_auth_user_status,
            
            # apply and approve
            ACTION_VDI_CREATE_DESKTOP_APPLY_FORM: ApplyApproveHandler.handle_create_desktop_apply_form,
            ACTION_VDI_DESCRIBE_DESKTOP_APPLY_FORMS: ApplyApproveHandler.handle_describe_desktop_apply_form,
            ACTION_VDI_MODIFY_DESKTOP_APPLY_FORM: ApplyApproveHandler.handle_modify_desktop_apply_form,
            ACTION_VDI_DELETE_DESKTOP_APPLY_FORMS: ApplyApproveHandler.handle_delete_desktop_apply_form,
            ACTION_VDI_DEAL_DESKTOP_APPLY_FORM: ApplyApproveHandler.handle_deal_desktop_apply_form,
            #apply group
            ACTION_VDI_CREATE_RESOURCE_APPLY_GROUP: ApplyApproveHandler.handle_create_resource_apply_group,
            ACTION_VDI_MODIFY_RESOURCE_APPLY_GROUP: ApplyApproveHandler.handle_modify_resource_apply_group,
            ACTION_VDI_DESCRIBE_RESOURCE_APPLY_GROUPS: ApplyApproveHandler.handle_describe_resource_apply_groups,
            ACTION_VDI_DELETE_RESOURCE_APPLY_GROUPS: ApplyApproveHandler.handle_delete_resource_apply_groups,
            ACTION_VDI_INSERT_USER_TO_APPLY_GROUP: ApplyApproveHandler.handle_insert_user_to_apply_group,
            ACTION_VDI_REMOVE_USER_FROM_APPLY_GROUP: ApplyApproveHandler.handle_remove_user_from_apply_group,
            ACTION_VDI_INSERT_RESOURCE_TO_APPLY_GROUP: ApplyApproveHandler.handle_insert_resource_to_apply_group,
            ACTION_VDI_REMOVE_RESOURCE_FROM_APPLY_GROUP: ApplyApproveHandler.handle_remove_resource_from_apply_group,
            # approve group
            ACTION_VDI_CREATE_RESOURCE_APPROVE_GROUP: ApplyApproveHandler.handle_create_resource_approve_group,
            ACTION_VDI_MODIFY_RESOURCE_APPROVE_GROUP: ApplyApproveHandler.handle_modify_resource_approve_group,
            ACTION_VDI_DESCRIBE_RESOURCE_APPROVE_GROUPS: ApplyApproveHandler.handle_describe_resource_approve_groups,
            ACTION_VDI_DELETE_RESOURCE_APPROVE_GROUPS: ApplyApproveHandler.handle_delete_resource_approve_groups,
            ACTION_VDI_INSERT_USER_TO_APPROVE_GROUP: ApplyApproveHandler.handle_insert_user_to_approve_group,
            ACTION_VDI_REMOVE_USER_FROM_APPROVE_GROUP: ApplyApproveHandler.handle_remove_user_from_approve_group,
            ACTION_VDI_MAP_APPLY_GROUP_AND_APPROVE_GROUP: ApplyApproveHandler.handle_map_apply_group_and_approve_group,
            ACTION_VDI_UNMAP_APPLY_GROUP_AND_APPROVE_GROUP: ApplyApproveHandler.handle_unmap_apply_group_and_approve_group,
            ACTION_VDI_GET_APPROVE_USERS: ApplyApproveHandler.handle_get_approve_users,
            # policy
            ACTION_VDI_CREATE_USB_PROLICY: UsbHandler.handle_create_desktop_usb_policy,
            ACTION_VDI_MODIFY_USB_PROLICY: UsbHandler.handle_modify_desktop_usb_policy,
            ACTION_VDI_DELETE_USB_PROLICY: UsbHandler.handle_delete_desktop_usb_policy,
            ACTION_VDI_DESCRIBE_USB_PROLICY: UsbHandler.handle_describe_desktop_usb_policy,
            # license
            ACTION_VDI_UPDATE_LICENSE: LicenseHandler.handle_update_license,
            ACTION_VDI_DESCRIBE_LICENSE: LicenseHandler.handle_describe_license,
            # system config
            ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_CONFIG: SystemConfigHandler.handle_describe_system_config,
            ACTION_VDI_MODIFY_DESKTOP_SYSTEM_CONFIG: SystemConfigHandler.handle_modify_system_config,
            ACTION_VDI_DESCRIBE_DESKTOP_BASE_SYSTEM_CONFIG: SystemConfigHandler.handle_describe_base_system_config,

            ACTION_VDI_MODIFY_APPROVALNOTICE_CONFIG: SystemConfigHandler.handle_modify_approvalnotice_config,
            ACTION_VDI_DESCRIBE_APPROVALNOTICE_CONFIG: SystemConfigHandler.handle_describe_approvalnotice_config,                                    
                                              
            # operation logs
            ACTION_VDI_DESCRIBE_DESKTOP_SYSTEM_LOGS: SystemConfigHandler.handle_describe_desktop_system_logs,
            ACTION_VDI_CREATE_SYSLOG_SERVER: SyslogServerHandler.handle_create_syslog_server,
            ACTION_VDI_MODIFY_SYSLOG_SERVER: SyslogServerHandler.handle_modify_syslog_server,
            ACTION_VDI_DELETE_SYSLOG_SERVERS: SyslogServerHandler.handle_delete_syslog_servers,
            ACTION_VDI_DESCRIBE_SYSLOG_SERVERS: SyslogServerHandler.handle_describe_syslog_servers,

            # guest
            ACTION_VDI_SEND_DESKTOP_MESSAGE: GuestHandler.handle_send_desktop_message,
            ACTION_VDI_SEND_DESKTOP_HOT_KEYS: GuestHandler.handle_send_desktop_hot_keys,
            ACTION_VDI_SEND_DESKTOP_NOTIFY: GuestHandler.handle_send_desktop_notify,
            ACTION_VDI_CHECK_DESKTOP_AGENT_STATUS: GuestHandler.handle_check_desktop_agent_status,
            ACTION_VDI_LOGIN_DESKTOP: GuestHandler.handle_login_desktop,
            ACTION_VDI_LOGOFF_DESKTOP: GuestHandler.handle_logoff_desktop,
            ACTION_VDI_ADD_DESKTOP_ACTIVE_DIRECTORY: GuestHandler.handle_add_desktop_active_directory,
            ACTION_VDI_MODIFY_GUEST_SERVER_CONFIG: GuestHandler.handle_modify_guest_server_config,
            ACTION_VDI_DESCRIBE_SPICE_INFO: GuestHandler.handle_describe_spice_info,
            ACTION_VDI_DESCRIBE_GUEST_PROCESSES: GuestHandler.describe_guest_processes,
            ACTION_VDI_DESCRIBE_GUEST_PROGRAMS: GuestHandler.describe_guest_programs,
            ACTION_VDI_GUEST_JSON_RCP: GuestHandler.handle_guest_json_rpc,

            # desktop maintainer
            ACTION_VDI_CREATE_DESKTOP_MAINTAINER: DesktopMaintainerHandler.handle_create_desktop_maintainer,
            ACTION_VDI_MODIFY_DESKTOP_MAINTAINER_ATTRIBUTES: DesktopMaintainerHandler.handle_modify_desktop_maintainer_attributes,
            ACTION_VDI_DELETE_DESKTOP_MAINTAINERS: DesktopMaintainerHandler.handle_delete_desktop_maintainers,
            ACTION_VDI_DESCRIBE_DESKTOP_MAINTAINERS: DesktopMaintainerHandler.handle_describe_desktop_maintainers,

            ACTION_VDI_GUEST_CHECK_DESKTOP_MAINTAINER: DesktopMaintainerHandler.handle_guest_check_desktop_maintainer,
            ACTION_VDI_APPLY_DESKTOP_MAINTAINER: DesktopMaintainerHandler.handle_apply_desktop_maintainer,
            ACTION_VDI_ATTACH_RESOURCE_TO_DESKTOP_MAINTAINER: DesktopMaintainerHandler.handle_attach_resource_to_desktop_maintainer,
            ACTION_VDI_DETACH_RESOURCE_FROM_DESKTOP_MAINTAINER: DesktopMaintainerHandler.handle_detach_resource_from_desktop_maintainer,

            ACTION_VDI_RUN_GUEST_SHELL_COMMAND: DesktopMaintainerHandler.handle_run_guest_shell_command,
            ACTION_VDI_DESCRIBE_GUEST_SHELL_COMMANDS: DesktopMaintainerHandler.handle_describe_guest_shell_commands,
            ACTION_VDI_GUEST_CHECK_SHELL_COMMAND: DesktopMaintainerHandler.handle_guest_check_shell_command,

            # component upgrade
            ACTION_VDI_DESCRIBE_COMPONENT_VERSION: ComponentVersion.handle_describe_component_version,
            ACTION_VDI_UPDATE_COMPONENT_VERSION: ComponentVersion.handle_update_component_version,
            ACTION_VDI_EXECUTE_COMPONENT_UPGRADE: ComponentVersion.handle_execute_component_upgrade,

            # delivery group
            ACTION_VDI_DESCRIBE_DELIVERY_GROUPS: DeliveryGroupHandler.handle_describe_delivery_groups,
            ACTION_VDI_CREATE_DELIVERY_GROUP: DeliveryGroupHandler.handle_create_delivery_group,
            ACTION_VDI_MODIFY_DELIVERY_GROUP_ATTRIBUTES: DeliveryGroupHandler.handle_modify_delivery_group_attributes,
            ACTION_VDI_DELETE_DELIVERY_GROUPS: DeliveryGroupHandler.handle_delete_delivery_groups,
            ACTION_VDI_LOAD_DELIVERY_GROUPS: DeliveryGroupHandler.handle_load_delivery_groups,
            ACTION_VDI_ADD_DESKTOP_TO_DELIVERY_GROUP: DeliveryGroupHandler.handle_add_desktop_to_delivery_group,
            ACTION_VDI_DEL_DESKTOP_FROM_DELIVERY_GROUP: DeliveryGroupHandler.handle_del_desktop_from_delivery_group,
            ACTION_VDI_ADD_USER_TO_DELIVERY_GROUP: DeliveryGroupHandler.handle_add_user_to_delivery_group,
            ACTION_VDI_DEL_USER_FROM_DELIVERY_GROUP: DeliveryGroupHandler.handle_del_user_from_delivery_group,
            ACTION_VDI_ATTACH_DESKTOP_TO_DELIVERY_GROUP_USER: DeliveryGroupHandler.handle_attach_desktop_to_delivery_group_user,
            ACTION_VDI_DETACH_DESKTOP_FROM_DELIVERY_GROUP_USER: DeliveryGroupHandler.handle_detach_desktop_from_delivery_group_user,
            ACTION_VDI_SET_DELIVERY_GROUP_MODE: DeliveryGroupHandler.handle_set_delivery_group_mode,
            ACTION_VDI_SET_CITRIX_DESKTOP_MODE: DeliveryGroupHandler.handle_set_citrix_desktop_mode,
            
            # sync computer
            ACTION_VDI_DESCRIBE_COMPUTER_CATALOGS: SyncCitrixHandler.handle_describe_computer_catalogs,
            ACTION_VDI_LOAD_COMPUTER_CATALOGS: SyncCitrixHandler.handle_load_computer_catalogs,
            ACTION_VDI_DESCRIBE_COMPUTERS: SyncCitrixHandler.handle_describe_computers,
            ACTION_VDI_LOAD_COMPUTERS: SyncCitrixHandler.handle_load_computers,
            ACTION_VDI_REFRESH_CITRIX_DESKTOPS: SyncCitrixHandler.handle_refresh_citrix_desktops,

            ACTION_VDI_DESCRIBE_DESKTOP_ZONES: ZoneHandler.handle_describe_desktop_zones,
            ACTION_VDI_REFRESH_DESKTOP_ZONES: ZoneHandler.handle_refresh_desktop_zones,
            ACTION_VDI_CREATE_DESKTOP_ZONE: ZoneHandler.handle_create_desktop_zone,
            ACTION_VDI_MODIFY_DESKTOP_ZONE_ATTRIBUTES: ZoneHandler.handle_modify_desktop_zone_attributes,
            ACTION_VDI_DELETE_DESKTOP_ZONES: ZoneHandler.handle_delete_desktop_zones,
            ACTION_VDI_MODIFY_DESKTOP_ZONE_RESOURCE_LIMIT: ZoneHandler.handle_modify_desktop_zone_resource_limit,
            ACTION_VDI_MODIFY_DESKTOP_ZONE_CONNECTION: ZoneHandler.handle_modify_desktop_zone_connection,
            ACTION_VDI_MODIFY_DESKTOP_ZONE_CITRIX_CONNECTION: ZoneHandler.handle_modify_desktop_zone_citrix_connection,
            # instance_class
            ACTION_VDI_DESCRIBE_INSTANCE_CLASS_DISK_TYPE: ZoneHandler.handle_describe_instance_class_disk_type,
            # gpu_class
            ACTION_VDI_DESCRIBE_GPU_CLASS_TYPE: ZoneHandler.handle_describe_gpu_class_type,
            ACTION_VDI_CHECK_NETWORK_CONNECTION: ZoneHandler.handle_check_network_connection,
            ACTION_VDI_CHECK_GPU_CONFIG: ZoneHandler.handle_check_gpu_config,

            # user desktop session
            ACTION_VDI_DESCRIBE_USER_DESKTOP_SESSION: DesktopSession.handle_describe_user_desktop_session,
            ACTION_VDI_LOGOUT_USER_DESKTOP_SESSION: DesktopSession.handle_logout_user_desktop_session,
            ACTION_VDI_MODIFY_USER_DESKTOP_SESSION: DesktopSession.handle_modify_user_desktop_session,
            #radius
            ACTION_VDI_DESCRIBE_RADIUS_SERVICES: RadiusHandler.handle_describe_radius_services,
            ACTION_VDI_CREATE_RADIUS_SERVICE: RadiusHandler.handle_create_radius_service,
            ACTION_VDI_MODIFY_RADIUS_SERVICE_ATTRIBUTES: RadiusHandler.handle_modify_radius_service_attributes,
            ACTION_VDI_DELETE_RADIUS_SERVICES: RadiusHandler.handle_delete_radius_services,
            ACTION_VDI_ADD_AUTH_RADIUS_USERS: RadiusHandler.handle_add_auth_radius_users,
            ACTION_VDI_REMOVE_AUTH_RADIUS_USERS: RadiusHandler.handle_remove_auth_radius_users,
            ACTION_VDI_MODIFY_RADIUS_USER_ATTRIBUTES: RadiusHandler.handle_modify_radius_user_attributes,
            ACTION_VDI_CHECK_RADIUS_TOKEN: RadiusHandler.handle_check_radius_token,

            #log
            ACTION_VDI_DOWNLOAD_LOG: DesktopHandler.handle_download_log,
            # auth
            ACTION_VDI_DESCRIBE_AUTH_SERVICES: AuthServiceHandler.handle_describe_auth_services,
            ACTION_VDI_CREATE_AUTH_SERVICE: AuthServiceHandler.handle_create_auth_service,
            ACTION_VDI_CHECK_AUTH_SERVICE_OUS: AuthServiceHandler.handle_check_auth_service_ous,
            ACTION_VDI_MODIFY_AUTH_SERVICE_ATTRIBUTES: AuthServiceHandler.handle_modify_auth_service_attributes,
            ACTION_VDI_DELETE_AUTH_SERVICES: AuthServiceHandler.handle_delete_auth_services,
            ACTION_VDI_ADD_AUTH_SERVICE_TO_ZONE: AuthServiceHandler.handle_add_auth_service_to_zone,
            ACTION_VDI_REMOVE_AUTH_SERVICE_FROM_ZONES: AuthServiceHandler.handle_remove_auth_service_from_zones,
            ACTION_VDI_REFRESH_AUTH_SERVICE: AuthServiceHandler.handle_refresh_auth_service,
            
            # notice push
            ACTION_VDI_DESCRIBE_NOTICE_PUSHS: NoticePushHandler.handle_describe_notice_pushs,
            ACTION_VDI_CREATE_NOTICE_PUSH: NoticePushHandler.handle_create_notice_push,
            ACTION_VDI_MODIFY_NOTICE_PUSH_ATTRIBUTES: NoticePushHandler.handle_modify_notice_push_attributes,
            ACTION_VDI_DELETE_NOTICE_PUSHS: NoticePushHandler.handle_delete_notice_pushs,
            ACTION_VDI_MODIFY_NOTICE_PUSH_ZONE_USER: NoticePushHandler.handle_modify_notice_push_zone_user,
            ACTION_VDI_SET_USER_NOTICE_READ: NoticePushHandler.handle_set_user_notice_read,
            
            ACTION_VDI_CREATE_PASSWORD_PROMPT_QUESTION: PasswordPrompt.handle_create_password_prompt_question,
            ACTION_VDI_MODIFY_PASSWORD_PROMPT_QUESTION: PasswordPrompt.handle_modify_password_prompt_question,
            ACTION_VDI_DELETE_PASSWORD_PROMPT_QUESTION: PasswordPrompt.handle_delete_password_prompt_question,
            ACTION_VDI_DESCRIBE_PASSWORD_PROMPT_QUESTION: PasswordPrompt.handle_describe_password_prompt_question,
            ACTION_VDI_CREATE_PASSWORD_PROMPT_ANSWER: PasswordPrompt.handle_create_password_prompt_answer,
            ACTION_VDI_MODIFY_PASSWORD_PROMPT_ANSWER: PasswordPrompt.handle_modify_password_prompt_answer,
            ACTION_VDI_DELETE_PASSWORD_PROMPT_ANSWER: PasswordPrompt.handle_delete_password_prompt_answer,
            ACTION_VDI_CHECK_PASSWORD_PROMPT_ANSWER: PasswordPrompt.handle_check_password_prompt_answer,
            ACTION_VDI_DESCRIBE_PASSWORD_PROMPT_HAVE_ANSWER: PasswordPrompt.handle_describe_password_prompt_have_answer,
            ACTION_VDI_DESCRIBE_HAVE_PASSWORD_ANSWER_USERS: PasswordPrompt.handle_describe_have_password_answer_users,
            ACTION_VDI_IGNORE_PASSWORD_PROMPT_QUESTION: PasswordPrompt.handle_ignore_password_prompt_question,

            # software
            ACTION_VDI_DESCRIBE_SOFTWARES: SoftwareHandler.handle_describe_softwares,
            ACTION_VDI_UPLOAD_SOFTWARES: SoftwareHandler.handle_upload_softwares,
            ACTION_VDI_DOWNLOAD_SOFTWARES: SoftwareHandler.handle_download_softwares,
            ACTION_VDI_DELETE_SOFTWARES: SoftwareHandler.handle_delete_softwares,
            ACTION_VDI_CHECK_SOFTWARE_VNAS_NODE_DIR: SoftwareHandler.handle_check_software_vnas_node_dir,

            # terminal management
            ACTION_VDI_DESCRIBE_TERMINAL_MANAGEMENTS: TerminalHandler.handle_describe_terminal_managements,
            ACTION_VDI_MODIFY_TERMINAL_MANAGEMENT_ATTRIBUTES: TerminalHandler.handle_modify_terminal_management_attributes,
            ACTION_VDI_DELETE_TERMINAL_MANAGEMENTS: TerminalHandler.handle_delete_terminal_managements,
            ACTION_VDI_RESTART_TERMINALS: TerminalHandler.handle_restart_terminals,
            ACTION_VDI_STOP_TERMINALS: TerminalHandler.handle_stop_terminals,

            ACTION_VDI_DESCRIBE_TERMINAL_GROUPS: TerminalHandler.handle_describe_terminal_groups,
            ACTION_VDI_CREATE_TERMINAL_GROUP: TerminalHandler.handle_create_terminal_group,
            ACTION_VDI_MODIFY_TERMINAL_GROUP_ATTRIBUTES: TerminalHandler.handle_modify_terminal_group_attributes,
            ACTION_VDI_DELETE_TERMINAL_GROUPS: TerminalHandler.handle_delete_terminal_groups,
            ACTION_VDI_ADD_TERMINAL_TO_TERMINAL_GROUP: TerminalHandler.handle_add_terminal_to_terminal_group,
            ACTION_VDI_DELETE_TERMINAL_FROM_TERMINAL_GROUP: TerminalHandler.handle_delete_terminal_from_terminal_group,
            ACTION_VDI_DESCRIBE_MASTER_BACKUP_IPS: TerminalHandler.handle_describe_master_backup_ips,
            ACTION_VDI_DESCRIBE_CBSERVER_HOSTS: TerminalHandler.handle_describe_cbserver_hosts,

            # module_custom
            ACTION_VDI_DESCRIBE_USER_MODULE_CUSTOMS: ModuleCustomHandler.handle_describe_user_module_customs,
            ACTION_VDI_CREATE_USER_MODULE_CUSTOM: ModuleCustomHandler.handle_create_user_module_custom,
            ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_ATTRIBUTES: ModuleCustomHandler.handle_modify_user_module_custom_attributes,
            ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_CONFIGS: ModuleCustomHandler.handle_modify_user_module_custom_configs,
            ACTION_VDI_MODIFY_USER_MODULE_CUSTOM_ZONE_USER: ModuleCustomHandler.handle_modify_modue_custom_zone_user,
            ACTION_VDI_DELETE_USER_MODULE_CUSTOMS: ModuleCustomHandler.handle_delete_user_module_customs,
            ACTION_VDI_DESCRIBE_SYSTEM_MODULE_TYPES: ModuleCustomHandler.handle_describe_system_module_types,

            # system_custom
            ACTION_VDI_DESCRIBE_SYSTEM_CUSTOM_CONFIGS: SystemCustomHandler.handle_describe_system_custom_configs,
            ACTION_VDI_MODIFY_SYSTEM_CUSTOM_CONFIG_ATTRIBUTES: SystemCustomHandler.handle_modify_system_custom_config_attributes,
            ACTION_VDI_RESET_SYSTEM_CUSTOM_CONFIGS: SystemCustomHandler.handle_reset_system_custom_configs,

            # system_custom
            ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_MANAGEMENTS: DesktopServiceManagementHandler.handle_describe_desktop_service_managements,
            ACTION_VDI_MODIFY_DESKTOP_SERVICE_MANAGEMENT_ATTRIBUTES: DesktopServiceManagementHandler.handle_modify_desktop_service_management_attributes,
            ACTION_VDI_REFRESH_DESKTOP_SERVICE_MANAGEMENT: DesktopServiceManagementHandler.handle_refresh_deskop_service_management,
            ACTION_VDI_DESCRIBE_DESKTOP_SERVICE_INSTANCES: DesktopServiceManagementHandler.handle_describe_desktop_service_instances,
            ACTION_VDI_LOAD_DESKTOP_SERVICE_INSTANCES: DesktopServiceManagementHandler.handle_load_desktop_service_instances,
            ACTION_VDI_REMOVE_DESKTOP_SERVICE_INSTANCES: DesktopServiceManagementHandler.handle_remove_desktop_service_instances,

            # workflow
            ACTION_VDI_DESCRIBE_WORKFLOW_SERVICE_ENV: WorkflowHandler.handle_describe_workflow_service_env,
            ACTION_VDI_DESCRIBE_WORKFLOW_SERVICES: WorkflowHandler.handle_describe_workflow_services,
            ACTION_VDI_DESCRIBE_WORKFLOW_MODELS: WorkflowHandler.handle_describe_workflow_models,
            ACTION_VDI_CREATE_WORKFLOW_MODEL: WorkflowHandler.handle_create_workflow_model,
            ACTION_VDI_MODIFY_WORKFLOW_MODEL_ATTRIBUTES: WorkflowHandler.hanlde_modify_workflow_model_attributes,
            ACTION_VDI_DELETE_WORKFLOW_MODELS: WorkflowHandler.handle_delete_workflow_models,
            
            ACTION_VDI_DESCRIBE_WORKFLOWS: WorkflowHandler.handle_describe_workflows,
            ACTION_VDI_CREATE_WORKFLOWS: WorkflowHandler.handle_create_workflows,
            ACTION_VDI_MODIFY_WORKFLOW_ATTRIBUTES: WorkflowHandler.handle_modify_workflow_attributes,
            ACTION_VDI_DELETE_WORKFLOWS: WorkflowHandler.handle_delete_workflows,
            ACTION_VDI_EXECUTE_WORKFLOWS: WorkflowHandler.handle_execute_workflows,
            ACTION_VDI_DESCRIBE_WORKFLOW_MODEL_CONFIGS: WorkflowHandler.handle_describe_workflow_model_configs,
            ACTION_VDI_CREATE_WORKFLOW_MODEL_CONFIG: WorkflowHandler.handle_create_workflow_model_config,
            ACTION_VDI_MODIFY_WORKFLOW_MODEL_CONFIG: WorkflowHandler.handle_modify_workflow_model_config,
            ACTION_VDI_DELETE_WORKFLOW_MODEL_CONFIGS: WorkflowHandler.handle_delete_workflow_model_configs,
            ACTION_VDI_SEND_DESKTOP_REQUEST: WorkflowHandler.handle_send_desktop_request,

            # file_share
            ACTION_VDI_DESCRIBE_FILE_SHARE_GROUPS: FileShareHandler.handle_describe_file_share_groups,
            ACTION_VDI_CREATE_FILE_SHARE_GROUP: FileShareHandler.handle_create_file_share_group,
            ACTION_VDI_MODIFY_FILE_SHARE_GROUP_ATTRIBUTES: FileShareHandler.handle_modify_file_share_group_attributes,
            ACTION_VDI_RENAME_FILE_SHARE_GROUP: FileShareHandler.handle_rename_file_share_group,
            ACTION_VDI_DELETE_FILE_SHARE_GROUPS: FileShareHandler.handle_delete_file_share_groups,
            ACTION_VDI_MODIFY_FILE_SHARE_GROUP_ZONE_USER: FileShareHandler.handle_modify_file_share_group_zone_user,

            ACTION_VDI_DESCRIBE_FILE_SHARE_GROUP_FILES: FileShareHandler.handle_describe_file_share_group_files,
            ACTION_VDI_UPLOAD_FILE_SHARE_GROUP_FILES: FileShareHandler.handle_upload_file_share_group_files,
            ACTION_VDI_DOWNLOAD_FILE_SHARE_GROUP_FILES: FileShareHandler.handle_download_file_share_group_files,
            ACTION_VDI_MODIFY_FILE_SHARE_GROUP_FILE_ATTRIBUTES: FileShareHandler.handle_modify_file_share_group_file_attributes,
            ACTION_VDI_DELETE_FILE_SHARE_GROUP_FILES: FileShareHandler.handle_delete_file_share_group_files,
            ACTION_VDI_DESCRIBE_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY: FileShareHandler.handle_describe_file_share_group_file_download_history,

            ACTION_VDI_DESCRIBE_FILE_SHARE_CAPACITY: FileShareHandler.handle_describe_file_share_capacity,
            ACTION_VDI_CHANGE_FILE_IN_FILE_SHARE_GROUP: FileShareHandler.handle_change_file_in_file_share_group,
            ACTION_VDI_DESCRIBE_FILE_SHARE_RECYCLES: FileShareHandler.handle_describe_file_share_recycles,
            ACTION_VDI_RESTORE_FILE_SHARE_RECYCLES: FileShareHandler.handle_restore_file_share_recycles,
            ACTION_VDI_DELETE_PERMANENTLY_FILE_SHARE_RECYCLES: FileShareHandler.handle_delete_permanently_file_share_recycles,
            ACTION_VDI_EMPTY_FILE_SHARE_RECYCLES: FileShareHandler.handle_empty_file_share_recycles,

            ACTION_VDI_CREATE_FILE_SHARE_SERVICE: FileShareHandler.handle_create_file_share_service,
            ACTION_VDI_LOAD_FILE_SHARE_SERVICE: FileShareHandler.handle_load_file_share_service,
            ACTION_VDI_DESCRIBE_FILE_SHARE_SERVICES: FileShareHandler.handle_describe_file_share_services,
            ACTION_VDI_MODIFY_FILE_SHARE_SERVICE_ATTRIBUTES: FileShareHandler.handle_modify_file_share_service_attributes,
            ACTION_VDI_DELETE_FILE_SHARE_SERVICES: FileShareHandler.handle_delete_file_share_services,
            ACTION_VDI_REFRESH_FILE_SHARE_SERVICE: FileShareHandler.handle_refresh_file_share_service,
            ACTION_VDI_DESCRIBE_FILE_SHARE_SERVICE_VNAS: FileShareHandler.handle_describe_file_share_service_vnas,
            ACTION_VDI_RESET_FILE_SHARE_SERVICE_PASSWORD: FileShareHandler.handle_reset_file_share_service_password,
        }

    def handle(self, req_msg, title, **kargs):
        # if program is shutting down, notify frontend with special reply
        # title is request type
        return handle_sync_message(False, self._handle, req_msg)

    def _is_valid_reqid(self, req_id):
        # A valid req_id should include digit and ascii letter,
        # and value must be between 20 and 100
        pattern = r'^(?=.*[a-z])(?=.*\d).{20,100}$'
        return bool(req_id and re.match(pattern, str(req_id)))

    def _is_readonly_action(self, action):
        return action.startswith(('Describe', 'Get'))

    def _serialize(self, req):
        ''' serialize request '''
        rtype = req.get('sender', {}).get('channel', '')
        action = req.get('action', '')
        zone = req.get('zone', 'global')
        identity = req.get('sender', {}).get('user_id', '')
        return (('type:(%s) action:(%s) identity(%s) zone(%s)') % (rtype,
                                                                   action,
                                                                   identity,
                                                                   zone))

    def _handle(self, req_msg):
        ''' @return reply message '''

        # decode to request object
        req = json_load(req_msg)

        # record receive request
        logger.info("request received [%s]" % format_params(req))
        start_time = time.time()

        # discard none type request
        if req is None or not isinstance(req, dict):
            logger.error(
                "illegal request, try it again [%s]" % format_params(req))
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                           ErrorMsg.ERR_MSG_ILLEGAL_REQUEST))

        # check request type
        if "type" not in req:
            logger.error("[type] should be provided in request [%s]" %
                         format_params(req))
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                           ErrorMsg.ERR_MSG_MISSING_PARAMETER, "type"))

        req_type = req["type"]
        if req_type == CHANNEL_INTERNAL:
            request = InternalRequest(req["params"])
        elif req_type == CHANNEL_SESSION:
            # set language
            req["sender"] = {'lang': req["params"].get('lang', ErrorMsg.EN)}
            request = SessionRequest(req["headers"], req["params"])
        elif req_type == CHANNEL_API:
            request = APIRequest(req["headers"], req["params"])

        else:
            logger.error("illegal type [%s]" % (req_type))
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                           ErrorMsg.ERR_MSG_ILLEGAL_REQUEST))

        # validate request
        if not request.validate():
            logger.error("validate request [%s] failed" % format_params(req))
            return return_error(req, request.get_error())

        # check api access
        if not request.check_api_access():
            logger.error("check api access [%s] failed" % format_params(req))
            return return_error(req, request.get_error())

        # check sub channel access
        if not request.check_sub_channel():
            logger.error(
                "check sub channel access [%s] failed" % format_params(req))
            return return_error(req, request.get_error())

        # build internal request format
        internal_request = request.build_internal_request()
        if internal_request is None:
            logger.error("build request [%s] failed" % format_params(req))
            return return_error(req, request.get_error())

        # handle it
        action = internal_request["action"]
        if action not in self.handler_map:
            logger.error(
                "sorry, we can't handle this request [%s]" % format_params(req))
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                                           ErrorMsg.ERR_MSG_CAN_NOT_HANDLE_REQUEST))
        try:
            if is_console_admin_user(internal_request["sender"]) and is_admin_console(internal_request["sender"]):
                ret = ResourcePermission.check_user_scope_permission(internal_request)
                if isinstance(ret, Error):
                    if self._is_readonly_action(internal_request["action"]):
                        rep = {"total_count": 0}
                        if action in ResourcePermission.READONLY_API_RETURN_DATA_SET:
                            rep[ResourcePermission.READONLY_API_RETURN_DATA_SET[action]] = []
                        return return_success(internal_request, rep)

                    logger.error("check user scope permision error.")
                    return return_error(req, ret)

            rep = self.handler_map[action](internal_request)
        except Exception, e:
            logger.exception(
                "handle request [%s] failed, [%s]" % (format_params(req), e))
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR))

        # logging request
        end_time = time.time()
        elapsed_time = end_time - start_time
        if int(elapsed_time) >= LONG_HANDLE_TIME:
            logger.critical(
                "handled request [%s], exec_time is [%.3f]s" % (req, elapsed_time))
        else:
            logger.info("handled request [%s], exec_time is [%.3f]s" % (
                self._serialize(internal_request), elapsed_time))
        return rep
