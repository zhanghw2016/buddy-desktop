# ---------------------------------------------
#       Constants for PostgreSQL DB
# ---------------------------------------------
DB_VDI = "vdi"

TB_DESKTOP_GROUP = "desktop_group"
TB_DESKTOP_GROUP_DISK = "desktop_group_disk"
TB_DESKTOP_GROUP_NETWORK = "desktop_group_network"
TB_DESKTOP_GROUP_USER = "desktop_group_user"
TB_DESKTOP = "desktop"
TB_RESOURCE_USER = "resource_user"

TB_DESKTOP_DISK = "desktop_disk"
TB_DESKTOP_IMAGE = "desktop_image"
TB_DESKTOP_NETWORK = "desktop_network"
TB_DESKTOP_NIC = "desktop_nic"
TB_DESKTOP_VERSION = "desktop_version"
TB_DESKTOP_JOB = 'desktop_job'
TB_DESKTOP_TASK = 'desktop_task'
TB_SCHEDULER_TASK = 'scheduler_task'
TB_SCHEDULER_TASK_RESOURCE = 'scheduler_task_resource'
TB_SCHEDULER_TASK_HISTORY = 'scheduler_task_history'
TB_RESOURCE_JOB = 'resource_job'
TB_DESKTOP_SNAPSHOT = 'desktop_snapshot'
TB_SNAPSHOT_RESOURCE = 'snapshot_resource'
TB_SNAPSHOT_DISK_SNAPSHOT = 'snapshot_disk_snapshot'

TB_SNAPSHOT_GROUP = 'snapshot_group'
TB_SNAPSHOT_GROUP_RESOURCE = "snapshot_group_resource"
TB_SNAPSHOT_GROUP_SNAPSHOT = "snapshot_group_snapshot"
TB_DELIVERY_GROUP = "delivery_group"
TB_DELIVERY_GROUP_USER = "delivery_group_user"

# policy
TB_POLICY_GROUP = "policy_group"
TB_POLICY_GROUP_RESOURCE = "policy_group_resource"
TB_POLICY_GROUP_POLICY = "policy_group_policy"
TB_SECURITY_POLICY = "security_policy"
TB_SECURITY_RULE = "security_rule"
TB_SECURITY_IPSET = "security_ipset"

TB_POLICY_RESOURCE_GROUP = "policy_resource_group"
#citrix policy
TB_CITRIX_POLICY = "citrix_policy"
TB_CITRIX_POLICY_ITEM_CONFIG = "citrix_policy_item_config"
TB_CITRIX_POLICY_ITEM = "citrix_policy_item"
TB_CITRIX_POLICY_FILTER= "citrix_policy_filter"

TB_VDI_SYSTEM_CONFIG = "vdi_system_config"
TB_VDI_SYSTEM_LOG = "vdi_system_log"
TB_DESKTOP_USER = "desktop_user"
TB_DESKTOP_USER_OU = "desktop_user_ou"
TB_DESKTOP_USER_GROUP='desktop_user_group'
TB_ZONE_USER_GROUP='zone_user_group'
TB_DESKTOP_USER_GROUP_USER='desktop_user_group_user'

TB_ZONE_USER_SCOPE = "zone_user_scope"
TB_ZONE_USER_SCOPE_ACTION = "zone_user_scope_action"
TB_APPLY = "apply"
TB_APPLY_GROUP = "apply_group"
TB_APPLY_GROUP_USER = "apply_group_user"
TB_APPLY_GROUP_RESOURCE = "apply_group_resource"
TB_APPROVE_GROUP = "approve_group"
TB_APPROVE_GROUP_USER = "approve_group_user"
TB_APPLY_APPROVE_GROUP_MAP = "apply_approve_group_map"
TB_VDI_DESKTOP_MESSAGE = "vdi_desktop_message"

TB_VDAGENT_JOB = "vdagent_job"
TB_VDHOST_JOB = "vdhost_job"
TB_GUEST = "guest"
TB_USB_POLICY = "usb_policy"
TB_COMPONENT_VERSION = "component_version"
TB_SOFTWARE_INFO = "software_info"

# zone
TB_DESKTOP_ZONE = "desktop_zone"
TB_ZONE_USER = "zone_user"
TB_ZONE_CONNECTION = "zone_connection"
TB_ZONE_RESOURCE_LIMIT= "zone_resource_limit"
TB_ZONE_CITRIX_CONNECTION = "zone_citrix_connection"
TB_ZONE_AUTH = "zone_auth"
TB_AUTH_SERVICE = "auth_service"

TB_RADIUS_SERVICE = 'radius_service'
TB_RADIUS_USER = 'radius_user'
TB_NOTICE_PUSH = "notice_push"
TB_NOTICE_USER = 'notice_user'
TB_NOTICE_ZONE = "notice_zone"
TB_NOTICE_READ = "notice_read"
TB_PROMPT_QUESTION = "prompt_question"
TB_PROMPT_ANSWER = "prompt_answer"
TB_USER_LOGIN_RECORD = "user_login_record"

TB_DESKTOP_LOGIN_RECORD = "desktop_login_record"
TB_SYSLOG_SERVER = "syslog_server"

TB_TERMINAL_MANAGEMENT = "terminal_management"
TB_TERMINAL_GROUP = "terminal_group"
TB_TERMINAL_GROUP_TERMINAL = "terminal_group_terminal"
TB_MODULE_CUSTOM = "module_custom"
TB_MODULE_CUSTOM_ZONE = "module_custom_zone"
TB_MODULE_CUSTOM_USER = "module_custom_user"
TB_MODULE_CUSTOM_CONFIG = "module_custom_config"
TB_MODULE_TYPE = "module_type"
TB_SYSTEM_CUSTOM = "system_custom"
TB_SYSTEM_CUSTOM_CONFIG = "system_custom_config"
TB_DESKTOP_SERVICE_MANAGEMENT = "desktop_service_management"

TB_WORKFLOW_SERVICE = "workflow_service"
TB_WORKFLOW_SERVICE_ACTION = "workflow_service_action"
TB_WORKFLOW_SERVICE_ACTION_INFO = "workflow_service_action_info"
TB_WORKFLOW_SERVICE_PARAM = "workflow_service_param"
TB_WORKFLOW_MODEL = "workflow_model"
TB_WORKFLOW = "workflow"
TB_WORKFLOW_CONFIG = "workflow_config"

TB_INSTANCE_CLASS_DISK_TYPE = "instance_class_disk_type"
TB_GPU_CLASS_TYPE = "gpu_class_type"

TB_FILE_SHARE_GROUP = "file_share_group"
TB_FILE_SHARE_GROUP_ZONE = "file_share_group_zone"
TB_FILE_SHARE_GROUP_USER = "file_share_group_user"
TB_FILE_SHARE_GROUP_FILE = "file_share_group_file"
TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY = "file_share_group_file_download_history"
TB_FILE_SHARE_SERVICE = "file_share_service"
TB_FILE_SHARE_SERVICE_VNAS = "file_share_service_vnas"


# app
TB_BROKER_APP = "broker_app"
TB_BROKER_APP_DELIVERY_GROUP = "broker_app_delivery_group"
TB_BROKER_APP_GROUP = "broker_app_group"
TB_BROKER_APP_GROUP_BROKER_APP = "broker_app_group_broker_app"

# desktop_maintainer
TB_DESKTOP_MAINTAINER = "desktop_maintainer"
TB_DESKTOP_MAINTAINER_RESOURCE = "desktop_maintainer_resource"

TB_GUEST_SHELL_COMMAND = "guest_shell_command"
TB_GUEST_SHELL_COMMAND_RESOURCE = "guest_shell_command_resource"
TB_GUEST_SHELL_COMMAND_RUN_HISTORY = "guest_shell_command_run_history"

# api limit
TB_API_LIMIT = "api_limit"
    

################################################################################
INDEXED_COLUMNS = {
                   TB_DESKTOP_GROUP: ["desktop_group_id", "desktop_group_name", "desktop_group_type", "description", "desktop_dn", "desktop_count", "dn_guid", "provision_type",
                                          "transition_status", "status", "desktop_image_id", "image_name", "naming_rule", "naming_count", "is_apply", "is_create", "save_disk", "save_desk",
                                          "cpu", "memory", "gpu", "gpu_class", "instance_class", "ivshmem_enable", "usbredir", "clipboard", "filetransfer", "managed_resource", "citrix_uuid",
                                          "qxl_number", "allocation_type", "create_time", "status_time", "owner", "zone"],

                   TB_DESKTOP_GROUP_DISK: ["disk_config_id", "disk_name", "desktop_group_id", "desktop_group_name",
                                           "disk_type", "size", "create_time", "status_time"],

                   TB_DESKTOP_GROUP_NETWORK: ["network_config_id", "desktop_group_id", "desktop_group_name", "network_id", "network_type", "start_ip", "end_ip", 
                                                  "create_time", "status_time"],

                   TB_DESKTOP_GROUP_USER: ["user_id", "user_name", "real_name", "desktop_group_id", "desktop_group_name", "status",
                                           "desktop_reserve", "need_desktop", "create_time"],

                   TB_DESKTOP: ["desktop_id", "instance_id", "desktop_image_id", "image_name", "description", "desktop_group_id", "desktop_group_name", "dn_guid",
                                "desktop_group_type", "instance_class", "hostname", "connect_status", "login_time", "logout_time", "status", "transition_status", 
                                "connect_time", "in_domain", "save_disk", "save_desk", "cpu", "memory", "gpu", "gpu_class", "instance_class", "ivshmem_enable", 
                                "usbredir", "clipboard", "filetransfer", "need_update", "need_monitor", "desktop_dn", "no_sync", "delivery_group_id", "desktop_mode", "assign_state", "reg_state",
                                "delivery_group_name", "auto_login", "create_time", "status_time", "qxl_number", "cpu_model","zone", "user_name"],
                   TB_RESOURCE_USER:["resource_id", "resource_type", "user_id", "user_name", "is_sync"],
                   TB_DESKTOP_DISK: ["disk_id", "volume_id", "desktop_id", "desktop_name", "description", "disk_config_id", "disk_name", 
                                       "disk_type","desktop_group_id", "desktop_group_name", "size", "need_update", "status", "transition_status", 
                                       "create_time", "status_time", "owner", "user_name", "zone"],
                   TB_DESKTOP_IMAGE: ["desktop_image_id", "image_id", "image_name", "description", "cpu", "memory", "instance_class",  "os_version", "base_image_id",
                                      "image_type", "status", "instance_id", "platform", "os_family", "transition_status", "session_type", "image_size", "is_default",
                                      "create_time", "status_time", "owner", "zone", "ui_type"],
                   TB_DESKTOP_NETWORK: ["network_id", "network_type", "router_id", "ip_network", "network_name", "description", "status", 
                                        "manager_ip", "dyn_ip_start", "dyn_ip_end", "create_time", "status_time", "transition_status", "zone"],
                   TB_DESKTOP_NIC: ["nic_id", "nic_name", "instance_id", "network_id", "network_name", "resource_id", "resource_name", "ip_network"
                                    "private_ip", "is_occupied", "network_type", "need_update", 
                                    "desktop_group_id", "desktop_group_name", "network_config_id", "status", "transition_status", 
                                    "create_time", "status_time"],
                   TB_RESOURCE_JOB: ["job_id", "status", "action", "resource_ids", "create_time", "status_time"],
                   TB_DESKTOP_JOB: ["job_id", "status", "job_action", "resource_ids", "directive", "create_time", "status_time", "owner", "zone"],
                   TB_DESKTOP_TASK: ["task_id", "status", "task_type", "job_id", "resource_ids", "directive", "create_time", "status_time", "owner", "zone", "task_level"],
                   
                   TB_POLICY_GROUP:["policy_group_id", "policy_group_name", "policy_group_type", "description", "is_apply", "transition_status", "is_default",
                                    "status", "create_time", "zone"],
                   TB_POLICY_GROUP_RESOURCE: ["policy_group_id","resource_id","status", "is_apply", "is_lock"],
                   TB_POLICY_GROUP_POLICY: ["policy_group_id","policy_id","status", "is_base"],
                   TB_SECURITY_POLICY: ["security_policy_id","security_policy_name", "security_policy_type", "description","create_time",
                                        "policy_mode", "share_policy_id", "need_sync" ,"status","is_apply","zone", "is_default"],
                   TB_SECURITY_RULE: ["security_rule_id", "security_rule_name", "security_policy_id", "protocol", "direction","security_rule_type", "share_rule_id" ,"need_sync",
                                      "val1", "val2", "val3", "priority", "disabled", "create_time", "zone" ],
                   TB_SECURITY_IPSET: ["security_ipset_id","security_ipset_name","description","ipset_type","val","is_apply","create_time", "zone", "is_default"],
                   
                   TB_POLICY_RESOURCE_GROUP: ["policy_group_id", "resource_id", "resource_type"],
                   
                   TB_CITRIX_POLICY:["pol_id", "policy_name", "pol_priority","user_priority", "cmo_priority",  "description", "pol_state", "update_time", "create_time", "zone"],
                   TB_CITRIX_POLICY_ITEM_CONFIG:[ "pol_item_name", "pol_item_type", "pol_item_state", "pol_item_value","pol_item_datatype", "update_time", 
                                                 "pol_item_name_ch","pol_item_tip","pol_item_unit","pol_item_value_ch","pol_item_path_ch","pol_item_path","col1","col2","col3","update_time","create_time","description"],
                   TB_CITRIX_POLICY_ITEM:[ "pol_item_id","pol_id","pol_item_name", "pol_item_type", "pol_item_state","pol_item_value", "update_time", "create_time", "zone"],
                   TB_CITRIX_POLICY_FILTER:["pol_filter_id" ,"pol_id" ,"pol_filter_name","pol_filter_type","pol_filter_state","pol_filter_value","pol_filter_mode","update_time", "create_time", "zone"],

                   TB_DESKTOP_SNAPSHOT: ['snapshot_id', 'desktop_snapshot_id','snapshot_name', 'description', 'desktop_resource_id','resource_id', 'snapshot_type', 'root_id', "total_count",
                                         'parent_id', 'is_head','head_chain', 'raw_size', 'store_size', 'total_store_size', 'size', 'total_size', "status_time",
                                         'transition_status', 'status', 'status_time', 'snapshot_time', 'create_time','owner', 'zone'],
                   TB_SNAPSHOT_RESOURCE: ['desktop_snapshot_id','snapshot_group_snapshot_id','snapshot_name', 'snapshot_id', "resource_id",
                                          'desktop_resource_id', 'resource_name', 'resource_type','create_time', 'status_time', 'ymd','owner', 'zone'],
                   TB_SNAPSHOT_GROUP: ["snapshot_group_id", "snapshot_group_name", "description","status","create_time", "zone"],
                   TB_SNAPSHOT_GROUP_RESOURCE: ["snapshot_group_id", "desktop_resource_id", "resource_name"],
                   TB_SNAPSHOT_GROUP_SNAPSHOT: ["snapshot_group_snapshot_id", "snapshot_group_id",'transition_status', 'status', "create_time"],
                   TB_SNAPSHOT_DISK_SNAPSHOT: ["snapshot_disk_snapshot_id", "desktop_id", "disk_id","create_time"],
                   
                   TB_SCHEDULER_TASK: ["scheduler_task_id", "task_name", "task_type", "status", "transition_status", "description", "resource_type",
                                       "repeat", "period", "ymd", "hhmm", "term_time", "create_time", "update_time", "execute_time", "term_time", "owner", "zone"],
                   TB_SCHEDULER_TASK_RESOURCE: ["scheduler_task_id", "task_name", "task_type", "resource_id", "task_param", "task_msg", "job_id", "create_time"],
                   TB_SCHEDULER_TASK_HISTORY: ["scheduler_history_id", "scheduler_task_id", "task_name", "history_type", "task_msg", "create_time"],
                   TB_DESKTOP_VERSION: ["version_id", "version", "description", "sequence", "curr_version", "create_time"],
                   TB_VDI_SYSTEM_CONFIG: ["config_key", "config_value"],
                   TB_VDI_SYSTEM_LOG: ["system_log_id","user_id", "user_name", "user_role", "action_name", "log_info", "req_params", "log_type","req_time","create_time"],
                   
                   TB_DESKTOP_USER: ["user_id","auth_service_id","user_name","object_guid","real_name","description","password", "password_protect"
                                     "ou_dn", "user_dn","status","user_control","create_time","update_time", "role"],

                   TB_ZONE_USER: ["user_id","zone_id","role","status","user_name"],
                   TB_DESKTOP_USER_OU: ["user_ou_id","auth_service_id","ou_name","object_guid",
                                        "ou_dn","description","create_time","update_time"],
                   TB_DESKTOP_USER_GROUP:["user_group_id","auth_service_id","user_group_name",
                                          "object_guid","description","group_dn","create_time","update_time"],
                   TB_ZONE_USER_GROUP: ["user_group_id", "zone_id"],
                   TB_DESKTOP_USER_GROUP_USER: ["user_group_id", "user_id"],
                   TB_ZONE_USER_SCOPE: ["user_id", "resource_type", "resource_id", "action_type", "zone_id"],
                   TB_ZONE_USER_SCOPE_ACTION: ["action_id", "action_name", "action_api"],
                   TB_APPLY: ["apply_id", "apply_type", "apply_title", "apply_description", "status", "apply_user_id", "apply_group_id", "approve_status",
                              "apply_resource_type","apply_parameter","approve_user_id", "approve_advice", "apply_age", "approve_group_id",
                              "start_time","end_time","create_time","update_time", "approve_parameter", "resource_group_id", "zone_id"],
                   TB_APPLY_GROUP: ["apply_group_id","apply_group_name","description","create_time","update_time", "zone_id"],
                   TB_APPLY_GROUP_USER: ["user_id","apply_group_id","user_type","create_time"],
                   TB_APPLY_GROUP_RESOURCE: ["resource_id","apply_group_id","create_time"],
                   TB_APPROVE_GROUP: ["approve_group_id","approve_group_name","description","create_time","update_time", "zone_id"],
                   TB_APPROVE_GROUP_USER: ["user_id","approve_group_id","user_type","create_time"],
                   TB_APPLY_APPROVE_GROUP_MAP: ["apply_group_id","approve_group_id","create_time"],
                   TB_VDI_DESKTOP_MESSAGE: ["message_id", "message","desktop_ids","message_time"],
                   TB_DELIVERY_GROUP: ["delivery_group_id", "delivery_group_name", "delivery_group_type", "desktop_kind", "description", "assign_name", "delivery_type","desktop_hide_mode",
                                       "allocation_type", "mode", "create_time", "zone"],
                   TB_DELIVERY_GROUP_USER: ["user_id", "delivery_type", "delivery_group_id", "user_type", "create_time"],
                   TB_VDAGENT_JOB: ["job_id", "status", "job_action", "resource_id", "directive", "create_time", "status_time"],
                   TB_VDHOST_JOB: ["job_id", "status", "job_action", "resource_id", "directive", "create_time", "status_time"],
                   TB_GUEST: ["desktop_id", "hostname", "login_user", "client_ip", "connect_status", "connect_time", "disconnect_time" ],
                   TB_USB_POLICY: ["usb_policy_id", "object_id", "policy_type", "priority", "class_id", "vendor_id", "product_id", "version_id", "allow", "create_time", "update_time"],
                   TB_COMPONENT_VERSION: ["component_id", "component_name", "component_type", "version", "filename", "description", "upgrade_packet_md5","upgrade_packet_size","status","transition_status","component_version_log","component_version_log_history","need_upgrade","update_time","create_time"],
                   TB_SOFTWARE_INFO: ["software_id", "software_name", "software_size","zone_id","create_time"],
                   TB_DESKTOP_ZONE: ["zone_id", "zone_name", "platform", "status", "visibility", "description","zone_deploy", "create_time", "status_time"],
                   TB_ZONE_CONNECTION: ["zone_id", "base_zone_id", "base_zone_name", "account_user_id",
                                  "account_user_name", "access_key_id", "secret_access_key", "host", "port", "protocol", "host_ip",
                                  "http_socket_timeout", "status", "create_time", "status_time"],
                   TB_ZONE_RESOURCE_LIMIT:["zone_id", "instance_class", "disk_size","cpu_cores","memory_size","cpu_memory_pairs",
                                           "supported_gpu", "place_group", "max_disk_count","default_passwd", "network_type","router",
                                           "ivshmem","max_snapshot_count","max_chain_count","gpu_class_key","max_gpu_count"],
                   TB_ZONE_CITRIX_CONNECTION: ["zone_id", "host", "port", "protocol", "http_socket_timeout", 
                                    "status", "managed_resource", "storefront_uri", "storefront_port", "netscaler_uri","netscaler_port","support_netscaler","support_citrix_pms", "create_time", "status_time"],
                   TB_AUTH_SERVICE: ["auth_service_id", "auth_service_name", "description", "auth_service_type", "admin_name","admin_password", "base_dn", "domain", 
                                     "host", "port", "secret_port", "is_sync", "modify_password", "status", "create_time", "status_time", "dn_guid"],
                   TB_ZONE_AUTH: ["zone_id", "auth_service_id", "base_dn"],
                   TB_RADIUS_SERVICE: ["radius_service_id","radius_service_name","description","host","port", "dn_guid",
                                       "acct_session","identifier","secret", "status", "enable_radius", "create_time","status_time", "auth_service_id", "ou_dn"],
                   TB_RADIUS_USER: ["radius_service_id", "user_id", "user_name", "check_radius", "user_type"],
                   TB_NOTICE_PUSH: ["notice_id", "notice_type", "notice_level", "title", "content", "status", "scope", "create_time", "expired_time", "execute_time", "owner", "force_read"],
                   TB_NOTICE_USER: ["notice_id", "user_id", "user_type"],
                   TB_NOTICE_ZONE: ["notice_id", "zone_id", "user_scope"],
                   TB_NOTICE_READ: ["notice_id", "user_id", "user_name"],
                   TB_PROMPT_QUESTION: ["prompt_question_id", "question_content", "create_time"],
                   TB_PROMPT_ANSWER: ["prompt_answer_id", "prompt_question_id", "question_content", "user_id", "answer_content", "create_time"],
                   TB_SYSLOG_SERVER: ["syslog_server_id", "host", "port", "protocol", "runtime", "status", "create_time"],
                   TB_DESKTOP_LOGIN_RECORD: ["desktop_login_record_id", "desktop_id", "user_id", "user_name", "client_ip", "zone_id", "session_uid", "connect_status", "connect_time", "disconnect_time" ],
                   TB_USER_LOGIN_RECORD: ["user_login_record_id", "user_id", "user_name", "zone_id", "client_ip", "create_time", "status", "errmsg"],
                   TB_TERMINAL_MANAGEMENT: ["terminal_id", "terminal_group_id","terminal_serial_number", "status", "login_user_name","terminal_ip","terminal_mac","terminal_type","terminal_version_number","login_hostname","connection_disconnection_time","create_time","zone_id","terminal_server_ip"],
                   TB_TERMINAL_GROUP: ["terminal_group_id", "terminal_group_name","description","create_time"],
                   TB_TERMINAL_GROUP_TERMINAL: ["terminal_group_id", "terminal_id", "create_time"],
                   TB_MODULE_CUSTOM: ["module_custom_id", "is_default","custom_name","description", "create_time"],
                   TB_MODULE_CUSTOM_ZONE: ["module_custom_id", "zone_id","user_scope"],
                   TB_MODULE_CUSTOM_USER: ["module_custom_id","user_id","zone_id","user_type"],
                   TB_MODULE_CUSTOM_CONFIG: ["module_custom_id","module_type","item_key","item_value","enable_module","create_time"],
                   TB_MODULE_TYPE: ["item_key", "enable_module"],
                   TB_SYSTEM_CUSTOM:["system_custom_id", "is_default","current_system_custom", "create_time"],
                   TB_SYSTEM_CUSTOM_CONFIG: ["system_custom_id","module_type","item_key","item_value","enable_module","create_time"],
                   TB_DESKTOP_SERVICE_MANAGEMENT: ["service_node_id", "service_id", "service_name", "description", "status","service_version","service_ip",
                                                   "service_node_status","service_node_ip","service_node_name","service_node_version","service_node_type","service_port","service_type","service_management_type","zone_id","create_time"],

                   TB_WORKFLOW_SERVICE: ["service_type", "service_name", "description"],
                   TB_WORKFLOW_SERVICE_ACTION: ["service_type", "api_action", "action_name", "priority", "is_head"],
                   TB_WORKFLOW_SERVICE_ACTION_INFO: ["api_action", "action_name", "required_params", "result_params", "public_params", "extra_params"],
                   TB_WORKFLOW_SERVICE_PARAM: ["param_key", "param_name"],
                   TB_WORKFLOW_MODEL: ["workflow_model_id", "workflow_model_name", "api_actions", "service_type", "env_params", "description", "create_time", "zone"],
                   TB_WORKFLOW: ["workflow_id", "workflow_model_id", "transition_status", "curr_action", "action_param", "workflow_params",
                                 "api_return", "api_error", "result", "status", "create_time", "status_time"],
                   TB_WORKFLOW_CONFIG: ["workflow_config_id", "workflow_model_id", "request_type", "status","request_action"],
                   TB_INSTANCE_CLASS_DISK_TYPE: ["instance_class_key", "instance_class", "disk_type","zone_deploy"],
                   TB_GPU_CLASS_TYPE: ["gpu_class_key", "gpu_class"],
                   TB_FILE_SHARE_GROUP: ["file_share_group_id","file_share_service_id", "file_share_group_name", "description", "show_location","scope","file_share_group_dn","base_dn","trashed_status","trashed_time","create_time","update_time"],
                   TB_FILE_SHARE_GROUP_ZONE: ["file_share_group_id", "zone_id","user_scope"],
                   TB_FILE_SHARE_GROUP_USER: ["file_share_group_id", "user_id", "zone_id", "user_type","file_share_group_dn"],
                   TB_FILE_SHARE_GROUP_FILE: ["file_share_group_file_id", "file_share_group_id","file_share_group_file_name", "file_share_group_file_alias_name",
                                              "description","file_share_group_file_size","transition_status","file_share_group_dn","file_share_group_file_dn","trashed_status","trashed_time","create_time"],
                   TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY: ["file_download_history_id", "file_share_group_file_id", "user_id", "user_name","create_time","update_time"],
                   TB_FILE_SHARE_SERVICE: ["file_share_service_id", "file_share_service_name", "description","network_id","desktop_server_instance_id","file_share_service_instance_id","private_ip",
                                           "eip_addr","vnas_private_ip","vnas_id","is_sync","transition_status","status","scope","limit_rate","limit_conn","loaded_clone_instance_ip",
                                           "fuser","fpw","ftp_chinese_encoding_rules","create_method","max_download_file_size", "max_upload_size_single_file","create_time","status_time"],
                   TB_FILE_SHARE_SERVICE_VNAS: ["vnas_id", "vnas_name","vnas_private_ip","status","create_time"],

                   TB_BROKER_APP: ["broker_app_id", "display_name", "cmd_argument", "cmd_exe_path", "working_dir", "normal_display_name", "admin_display_name", 
                                   "icon_data", "floder_name", "create_time", "status_time", "zone", "description"],
                   TB_BROKER_APP_DELIVERY_GROUP: ["broker_app_id", "broker_app_name", "delivery_group_id", "delivery_group_name"],
                   TB_BROKER_APP_GROUP: ["broker_app_group_id", "broker_app_group_name", "description", "broker_app_group_uid", "create_time", "zone"],
                   TB_BROKER_APP_GROUP_BROKER_APP: ["broker_app_group_id", "broker_app_group_name", "broker_app_id", "broker_app_name"],
                   TB_API_LIMIT:["api_action", "enable", "refresh_interval", "refresh_time", "update_time"],
                   
                   TB_DESKTOP_MAINTAINER: ["desktop_maintainer_id", "desktop_maintainer_name", "desktop_maintainer_type",
                                           "description", "json_detail","status","transition_status","is_apply","zone_id","create_time"],
                   TB_DESKTOP_MAINTAINER_RESOURCE: ["desktop_maintainer_id", "resource_id", "resource_type", "resource_name", "zone_id","create_time"],
                   TB_GUEST_SHELL_COMMAND: ["guest_shell_command_id", "guest_shell_command_name", "guest_shell_command_type","command",'transition_status','status','command_response','create_time'],
                   TB_GUEST_SHELL_COMMAND_RESOURCE: ["guest_shell_command_id", "resource_id", "resource_type","zone_id", 'create_time'],
                   TB_GUEST_SHELL_COMMAND_RUN_HISTORY: ["guest_shell_command_run_history_id", "guest_shell_command_id","resource_id", "create_time", "update_time"],

}

# support sort columns
SORT_COLUMNS = {
                   TB_DESKTOP_GROUP: ["desktop_group_id", "desktop_group_name", "desktop_group_type", "status", "create_time", "status_time", "provision_type"],
                   TB_DESKTOP_GROUP_DISK: ["disk_config_id", "desktop_group_id", "disk_name", "disk_type", "create_time", "status_time"],
                   TB_DESKTOP_GROUP_NETWORK: ["network_config_id", "desktop_group_id", "network_id", "create_time", "status_time"],
                   TB_DESKTOP_GROUP_USER: ["user_id", "desktop_group_id", "hostname", "status", "create_time"],
                   TB_DESKTOP: ["desktop_id", "instance_id", "desktop_group_id", "connect_status", "login_time", "create_time", "status_time", "instance_class",
                                "hostname", "desktop_group_name", "delivery_group_name", "status", "in_domain", "user_name"],
                   TB_DESKTOP_DISK: ["disk_id", "volume_id", "desktop_id", "disk_config_id", "disk_name", "disk_type", "create_time", "status_time"],
                   TB_DESKTOP_IMAGE: ["desktop_image_id", "image_id", "image_name", "status", "create_time", "status_time"],
                   
                   TB_POLICY_GROUP:["policy_group_id", "policy_group_name", "policy_group_type","description", "is_apply", "create_time", "zone"],
                   TB_POLICY_GROUP_RESOURCE: ["policy_group_id","resource_id","status", "is_apply", "is_lock"],
                   TB_POLICY_GROUP_POLICY: ["policy_group_id","policy_id","status","is_base"],
                   TB_SECURITY_POLICY: ["security_policy_id","security_policy_name","security_policy_type","description","is_default","create_time","zone", "is_default"],
                   TB_SECURITY_RULE: ["security_rule_id","security_rule_name","security_policy_id","protocol","direction","security_rule_type", "share_rule_id" ,"need_sync",
                                       "val1","val2","val3","priority","action","disabled", "create_time","zone" ],
                   TB_SECURITY_IPSET: ["security_ipset_id","security_ipset_name","description","ipset_type","val","is_apply","create_time", "zone", "is_default"],
                   TB_POLICY_RESOURCE_GROUP: ["policy_group_id", "resource_id", "resource_type", "policy_group_type"],
                   TB_CITRIX_POLICY_ITEM_CONFIG:["pol_item_name", "pol_item_type", "pol_item_state", "pol_item_value","pol_item_datatype", "update_time", 
                                                 "pol_item_name_ch","pol_item_tip","pol_item_unit","pol_item_value_ch","pol_item_path_ch","pol_item_path","col1","col2","col3","update_time","create_time","description"],
                   TB_CITRIX_POLICY:["pol_id", "policy_name", "pol_priority", "user_priority", "cmo_priority", "description", "pol_state", "update_time", "create_time", "zone"],
                   TB_CITRIX_POLICY_ITEM:["pol_item_id","pol_id","pol_item_name",  "pol_item_type", "pol_item_state","pol_item_value", "update_time", "create_time", "zone"],
                   TB_CITRIX_POLICY_FILTER:["pol_filter_id" ,"pol_id" ,"pol_filter_name","pol_filter_type","pol_filter_state","pol_filter_value","pol_filter_mode","update_time", "create_time", "zone"],
                   TB_DESKTOP_SNAPSHOT: ["snapshot_id","snapshot_name", "snapshot_type", "status", "status_time", "create_time"],
                   TB_SNAPSHOT_GROUP: ["snapshot_group_id", "snapshot_group_name", "status","create_time"],
                   TB_SNAPSHOT_GROUP_RESOURCE: ["snapshot_group_id", "desktop_resource_id", "resource_name"],
                   TB_SNAPSHOT_GROUP_SNAPSHOT: ["snapshot_group_snapshot_id", "snapshot_group_id", 'transition_status', 'status',"create_time"],
                   TB_SNAPSHOT_DISK_SNAPSHOT: ["snapshot_disk_snapshot_id", "desktop_id", "disk_id", "create_time"],

                   TB_SCHEDULER_TASK: ["scheduler_task_id", "task_name", "task_type", "status", "create_time", "update_time", "execute_time", "term_time"],
                   TB_SCHEDULER_TASK_RESOURCE: ["scheduler_task_id", "task_name", "task_type"],
                   TB_SCHEDULER_TASK_HISTORY: ["scheduler_history_id", "history_type", "create_time"],
                   TB_DESKTOP_JOB: ["job_id", "status", "create_time", "status_time"],
                   TB_VDI_SYSTEM_LOG: ["system_log_id","user_id", "user_name", "user_role", "action_name", "log_info", "req_params", "log_type","req_time","create_time"],
                   TB_DESKTOP_USER: ["auth_service_id","user_name","real_name","status","create_time"],
                   TB_DESKTOP_USER_OU: ["auth_service_id","ou_name", "create_time"],
                   TB_DESKTOP_USER_GROUP:["auth_service_id","user_group_name","create_time"],
                   TB_ZONE_USER_GROUP: ["user_group_id", "zone_id"],
                   TB_DESKTOP_USER_GROUP_USER: ["user_group_id", "user_id"],
                   TB_ZONE_USER_SCOPE: ["user_id", "resource_type", "action_type", "zone_id"],
                   TB_APPLY: ["apply_id", "apply_type", "apply_title", "apply_description", "status", "apply_user_id","apply_group_id",
                              "apply_resource_type","apply_parameter","approve_user_id", "approve_advice", "apply_age","approve_group_id",
                              "start_time","end_time","create_time","update_time", "approve_parameter", "resource_group_id", "zone_id"],
                   TB_APPLY_GROUP: ["apply_group_id","apply_group_name","description","create_time","update_time", "zone_id"],
                   TB_APPLY_GROUP_USER: ["user_id","apply_group_id","user_type","create_time"],
                   TB_APPLY_GROUP_RESOURCE: ["resource_id","apply_group_id","create_time"],
                   TB_APPROVE_GROUP: ["approve_group_id","approve_group_name","description","create_time","update_time", "zone_id"],
                   TB_APPROVE_GROUP_USER: ["user_id","approve_group_id","user_type","create_time"],
                   TB_APPLY_APPROVE_GROUP_MAP: ["apply_group_id","approve_group_id","create_time"],
                   TB_VDI_DESKTOP_MESSAGE: ["message_id", "message","desktop_ids","message_time"],
                   TB_DELIVERY_GROUP: ["delivery_group_id", "delivery_group_name", "delivery_group_type", "create_time", "allocation_type", "delivery_type","desktop_hide_mode"],
                   TB_VDAGENT_JOB: ["job_id", "status", "job_action", "resource_id", "directive", "create_time", "status_time"],
                   TB_VDHOST_JOB: ["job_id", "status", "job_action", "resource_id", "directive", "create_time", "status_time"],
                   TB_GUEST: ["desktop_id", "hostname", "login_user", "client_ip", "connect_status", "connect_time", "disconnect_time" ],
                   TB_USB_POLICY: ["usb_policy_id", "object_id", "policy_type", "priority", "class_id", "vendor_id", "product_id", "version_id", "allow", "create_time", "update_time"],
                   TB_COMPONENT_VERSION: ["component_id", "component_name", "component_type", "version", "filename", "description", "upgrade_packet_md5","upgrade_packet_size","status","transition_status","component_version_log","component_version_log_history","need_upgrade","update_time","create_time"],
                   TB_SOFTWARE_INFO: ["software_id", "software_name", "software_size","zone_id","create_time"],
                   TB_PROMPT_QUESTION: ["prompt_question_id", "question_content", "create_time"],
                   TB_PROMPT_ANSWER: ["prompt_answer_id", "prompt_question_id", "question_content", "user_id", "answer_content", "create_time"],
                   TB_SYSLOG_SERVER: ["syslog_server_id", "host", "port", "protocol", "runtime", "status", "create_time"],
                   TB_DESKTOP_LOGIN_RECORD: ["desktop_login_record_id", "desktop_id", "user_id", "user_name", "client_ip", "zone_id", "session_uid", "connect_status", "connect_time", "disconnect_time" ],
                   TB_USER_LOGIN_RECORD: ["user_login_record_id", "user_id", "user_name", "zone_id", "client_ip", "create_time", "status", "errmsg"],

                   TB_TERMINAL_MANAGEMENT: ["terminal_id","terminal_group_id", "terminal_serial_number", "status", "login_user_name","terminal_ip","terminal_mac","terminal_type","terminal_version_number","login_hostname","connection_disconnection_time","create_time","zone_id","terminal_server_ip"],
                   TB_TERMINAL_GROUP: ["terminal_group_id", "terminal_group_name","description", "create_time"],
                   TB_TERMINAL_GROUP_TERMINAL: ["terminal_group_id", "terminal_id", "create_time"],
                   TB_MODULE_CUSTOM: ["module_custom_id", "is_default", "custom_name","description","create_time"],
                   TB_MODULE_CUSTOM_ZONE: ["module_custom_id", "zone_id","user_scope"],
                   TB_MODULE_CUSTOM_USER: ["module_custom_id", "user_id", "zone_id","user_type"],
                   TB_MODULE_CUSTOM_CONFIG: ["module_custom_id","module_type","item_key","item_value","enable_module","create_time"],
                   TB_MODULE_TYPE: ["item_key", "enable_module"],
                   TB_SYSTEM_CUSTOM:["system_custom_id", "is_default","current_system_custom", "create_time"],
                   TB_SYSTEM_CUSTOM_CONFIG: ["system_custom_id","module_type","item_key","item_value","enable_module","create_time"],
                   TB_DESKTOP_SERVICE_MANAGEMENT: ["service_node_id", "service_id", "service_name", "description", "status","service_version", "service_ip",
                                                   "service_node_status", "service_node_ip","service_node_name","service_node_version","service_node_type", "service_port", "service_type","service_management_type","zone_id","create_time"],

                   TB_WORKFLOW_SERVICE: ["service_type", "service_name", "description"],
                   TB_WORKFLOW_SERVICE_ACTION: ["service_type", "api_action", "action_name", "priority", "is_head"],
                   TB_WORKFLOW_SERVICE_ACTION_INFO: ["api_action", "action_name", "required_params", "result_params", "public_params", "extra_params"],
                   TB_WORKFLOW_SERVICE_PARAM: ["param_key", "param_name"],
                   TB_WORKFLOW_MODEL: ["workflow_model_id", "workflow_model_name", "api_actions", "service_type", "env_params", "description", "create_time", "zone"],
                   TB_WORKFLOW: ["workflow_id", "workflow_model_id", "transition_status", "curr_action", "action_param", "workflow_params",
                                 "api_return","api_error", "result", "status", "create_time", "status_time"],
                   TB_WORKFLOW_CONFIG: ["workflow_config_id","workflow_model_id", "request_type","status","request_action"],
                   TB_INSTANCE_CLASS_DISK_TYPE: ["instance_class_key", "instance_class", "disk_type","zone_deploy"],
                   TB_GPU_CLASS_TYPE: ["gpu_class_key", "gpu_class"],
                   TB_FILE_SHARE_GROUP: ["file_share_group_id", "file_share_service_id","file_share_group_name", "description","show_location","scope","file_share_group_dn","base_dn","trashed_status","trashed_time","create_time","update_time"],
                   TB_FILE_SHARE_GROUP_ZONE: ["file_share_group_id", "zone_id", "user_scope"],
                   TB_FILE_SHARE_GROUP_USER: ["file_share_group_id", "user_id", "zone_id", "user_type","file_share_group_dn"],
                   TB_FILE_SHARE_GROUP_FILE: ["file_share_group_file_id", "file_share_group_id","file_share_group_file_name","file_share_group_file_alias_name",
                                              "description", "file_share_group_file_size", "transition_status","file_share_group_dn","file_share_group_file_dn", "trashed_status","trashed_time","create_time"],
                   TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY: ["file_download_history_id", "file_share_group_file_id", "user_id","user_name", "create_time","update_time"],
                   TB_FILE_SHARE_SERVICE: ["file_share_service_id", "file_share_service_name", "description","network_id","desktop_server_instance_id","file_share_service_instance_id",
                                           "private_ip","eip_addr","vnas_private_ip","vnas_id","is_sync","transition_status","status","scope","limit_rate","limit_conn","loaded_clone_instance_ip",
                                           "fuser","fpw","ftp_chinese_encoding_rules","create_method","max_download_file_size","max_upload_size_single_file","create_time","status_time"],
                   TB_FILE_SHARE_SERVICE_VNAS: ["vnas_id", "vnas_name", "vnas_private_ip", "status", "create_time"],
                   TB_DESKTOP_MAINTAINER: ["desktop_maintainer_id", "desktop_maintainer_name", "desktop_maintainer_type",
                            "description", "json_detail", "status","transition_status", "is_apply", "zone_id", "create_time"],
                   TB_DESKTOP_MAINTAINER_RESOURCE: ["desktop_maintainer_id", "resource_id", "resource_type", "resource_name", "zone_id","create_time"],
                   TB_GUEST_SHELL_COMMAND: ["guest_shell_command_id", "guest_shell_command_name", "guest_shell_command_type","command",'transition_status','status','command_response','create_time'],
                   TB_GUEST_SHELL_COMMAND_RESOURCE: ["guest_shell_command_id", "resource_id", "resource_type", "zone_id",'create_time'],
                   TB_GUEST_SHELL_COMMAND_RUN_HISTORY: ["guest_shell_command_run_history_id", "guest_shell_command_id","resource_id", "create_time","update_time"],
}

# columns that can be search through sql 'like' operator
SEARCH_COLUMNS = {
                   TB_DESKTOP_GROUP: ["desktop_group_name", "description"],
                   TB_DESKTOP_GROUP_USER: ["desktop_group_name", "user_name"],
                   TB_DESKTOP: ["hostname", "desktop_group_name", "delivery_group_name"],
                   TB_DESKTOP_DISK: ["disk_name", "user_name", "desktop_name"],
                   TB_DESKTOP_NIC: ["private_ip", "ip_network", "resource_name", "resource_id"],
                   TB_DESKTOP_IMAGE: ["image_name", "description", "os_family"],
                   TB_SCHEDULER_TASK: ["task_name"],
                   TB_SCHEDULER_TASK_RESOURCE: ["task_name"],
                   TB_SCHEDULER_TASK_HISTORY: ["scheduler_task_id", "task_name"],
                   TB_SNAPSHOT_GROUP: ["snapshot_group_name"],
                   TB_SNAPSHOT_GROUP_RESOURCE: ["desktop_resource_id","resource_name"],
                   TB_SCHEDULER_TASK: ["task_name"],
                   TB_DESKTOP_NETWORK: ["network_name", "ip_network"],
                   TB_DESKTOP_NIC: ["private_ip", "desktop_group_id", "resource_id", "network_id"],
                   TB_VDI_SYSTEM_LOG: ["log_info", "action_name", "user_name", "user_id", "system_log_id"],
                   TB_DESKTOP_JOB: ['resource_ids', "job_id", "job_action"],
                   TB_DESKTOP_USER: ["user_name", "real_name"],
                   TB_ZONE_USER: ["user_name"],
                   TB_DESKTOP_USER_OU: ["ou_name", "ou_dn", "base_dn"],
                   TB_DESKTOP_USER_GROUP:["user_group_name", "group_dn"],
                   TB_RADIUS_SERVICE: ["radius_service_name","description"],
                   TB_APPLY: ["apply_title", "apply_description","resource_group_id","resource_id","approve_group_id"],
                   TB_APPLY_GROUP: ["apply_group_name","description"],
                   TB_APPROVE_GROUP: ["approve_group_name","description"],
                   TB_VDI_DESKTOP_MESSAGE: ["message_id", "message","desktop_ids","message_time"],
                   TB_DELIVERY_GROUP: ["delivery_group_name", "description"],
                   TB_USB_POLICY: ["policy_type", "priority"],
                   TB_POLICY_GROUP: ["policy_group_name", "description"],
                   TB_CITRIX_POLICY:[ "policy_name","description"],
                   TB_CITRIX_POLICY_ITEM:["pol_item_name"],
                   TB_CITRIX_POLICY_ITEM_CONFIG:["pol_item_name_ch"],                   
                   TB_SECURITY_POLICY: ["security_policy_name"],
                   TB_SECURITY_RULE: ["security_rule_name"],
                   TB_SECURITY_IPSET:["security_ipset_name", "description"],
                   TB_AUTH_SERVICE: ["auth_service_name","host"],
                   TB_NOTICE_PUSH: ["title", "content"],
                   TB_PROMPT_QUESTION: ["question_content"],
                   TB_PROMPT_ANSWER: ["answer_content"],
                   TB_TERMINAL_MANAGEMENT: ["terminal_serial_number", "login_user_name","terminal_ip", "terminal_mac", "terminal_version_number","login_hostname","terminal_server_ip"],
                   TB_TERMINAL_GROUP: ["terminal_group_name"],
                   TB_MODULE_CUSTOM: ["custom_name"],
                   TB_MODULE_CUSTOM_CONFIG: ["module_type","custom_name","item_key","item_value"],
                   TB_DESKTOP_SERVICE_MANAGEMENT: ["service_name",'service_type'],
                   TB_DESKTOP_ZONE: ["zone_id", "zone_name"],
                   TB_SYSLOG_SERVER: ["syslog_server_id","host"],
                   TB_FILE_SHARE_GROUP: ["file_share_group_name"],
                   TB_FILE_SHARE_GROUP_FILE: ["file_share_group_file_name","file_share_group_file_alias_name","description"],
                   TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY: ["user_name"],
                   TB_FILE_SHARE_SERVICE: ["file_share_service_name","private_ip","vnas_private_ip"],
                   TB_FILE_SHARE_SERVICE_VNAS: ["vnas_name","vnas_private_ip"],
                   TB_RESOURCE_USER: ["user_name"],
                   TB_BROKER_APP: ["display_name"],
                   TB_BROKER_APP_GROUP: ["broker_app_group_name"],

                   TB_DESKTOP_MAINTAINER: ["desktop_maintainer_name"],
                   TB_DESKTOP_MAINTAINER_RESOURCE: ["resource_name"],
                   TB_GUEST_SHELL_COMMAND: ["command"],
                   TB_WORKFLOW_MODEL: ["workflow_model_name"],
                   TB_WORKFLOW: ["workflow_params","status"],
                   TB_WORKFLOW_CONFIG: ["request_type"],
}

# columns that can filter by timestamp range
TIMESTAMP_COLUMNS = {
                   TB_DESKTOP_GROUP: ["create_time"],
                   TB_DESKTOP: ["create_time"],
                   TB_DESKTOP_DISK: ["create_time"],
                   TB_DESKTOP_IMAGE: ["create_time"],
                   TB_VDI_SYSTEM_LOG: ["create_time"],
                   TB_DESKTOP_USER: ["create_time"],
                   TB_DESKTOP_JOB:["create_time"],
                   TB_APPLY: ["create_time", "start_time", "end_time"],
                   TB_VDAGENT_JOB: ["create_time"],
                   TB_VDHOST_JOB: ["create_time"],
                   TB_SNAPSHOT_RESOURCE: ["create_time"],
                   TB_DESKTOP_SNAPSHOT: ["create_time"],
                   TB_SNAPSHOT_GROUP: ["create_time"],
                   TB_SNAPSHOT_GROUP_SNAPSHOT: ["create_time"],
                   TB_USER_LOGIN_RECORD: ["create_time"],
                   TB_DESKTOP_LOGIN_RECORD: ["connect_time", "disconnect_time"],
                   TB_TERMINAL_MANAGEMENT:["create_time"],
                   TB_TERMINAL_GROUP:["create_time"],
                   TB_TERMINAL_GROUP_TERMINAL: ["create_time"],
                   TB_MODULE_CUSTOM: ["create_time"],
                   TB_DESKTOP_SERVICE_MANAGEMENT: ["create_time"],
                   TB_GUEST: ["connect_time"],
                   TB_FILE_SHARE_GROUP: ["create_time","trashed_time"],
                   TB_FILE_SHARE_GROUP_FILE: ["create_time","trashed_time"],
                   TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY: ["create_time"],
                   TB_FILE_SHARE_SERVICE: ["create_time"],
                   TB_FILE_SHARE_SERVICE_VNAS: ["create_time"],
                   TB_DESKTOP_MAINTAINER: ["create_time"],
                   TB_DESKTOP_MAINTAINER_RESOURCE: ["create_time"],
                   TB_GUEST_SHELL_COMMAND: ['create_time'],
                   TB_GUEST_SHELL_COMMAND_RESOURCE: ['create_time'],
                   TB_GUEST_SHELL_COMMAND_RUN_HISTORY: [ "create_time"],
                   }
# columns that can filter by range
RANGE_COLUMNS = {
    TB_APPLY: ["apply_age"],
    }
# not equal column
NOT_COLUMNS = {
                TB_DESKTOP_USER: ["user_id"],
                TB_DESKTOP:["delivery_group_id"]
            }
# the tables that supports search word column
# if search word column is specified, it will search all search columns and also the resource id
SEARCH_WORD_COLUMN_TABLE = [
                   TB_DESKTOP_GROUP, TB_DESKTOP_GROUP_DISK, TB_DESKTOP_GROUP_USER,
                   TB_DESKTOP, TB_DESKTOP_DISK, TB_DESKTOP_IMAGE, TB_VDI_SYSTEM_LOG,
                   TB_DESKTOP_USER, TB_DESKTOP_USER_OU, TB_APPLY, TB_APPLY_GROUP,TB_APPROVE_GROUP,TB_DESKTOP_JOB,
                   TB_DESKTOP_NIC, TB_SCHEDULER_TASK, TB_SCHEDULER_TASK_RESOURCE,TB_RADIUS_SERVICE,
                   TB_DESKTOP_NETWORK, TB_DELIVERY_GROUP, TB_DELIVERY_GROUP_USER, TB_APPROVE_GROUP_USER, 
                   TB_APPLY_GROUP_USER, TB_CITRIX_POLICY,TB_CITRIX_POLICY_ITEM,TB_CITRIX_POLICY_ITEM_CONFIG,TB_POLICY_GROUP,TB_SECURITY_POLICY,TB_SECURITY_IPSET,TB_SECURITY_RULE, TB_NOTICE_PUSH,
                   TB_TERMINAL_MANAGEMENT,TB_TERMINAL_GROUP,TB_MODULE_CUSTOM,TB_MODULE_CUSTOM_CONFIG,TB_DESKTOP_SERVICE_MANAGEMENT,
                   TB_DESKTOP_ZONE,TB_SYSLOG_SERVER,TB_PROMPT_QUESTION,TB_SNAPSHOT_GROUP,TB_AUTH_SERVICE,TB_RESOURCE_USER,
                   TB_FILE_SHARE_GROUP,TB_FILE_SHARE_GROUP_FILE,TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY,TB_FILE_SHARE_SERVICE,TB_FILE_SHARE_SERVICE_VNAS,
                   TB_BROKER_APP, TB_BROKER_APP_GROUP,
                   TB_DESKTOP_MAINTAINER,TB_DESKTOP_MAINTAINER_RESOURCE,TB_GUEST_SHELL_COMMAND,TB_ZONE_USER,
                   TB_WORKFLOW_MODEL,TB_WORKFLOW,TB_WORKFLOW_CONFIG
                   ]
SEARCH_WORD_COLUMN_NAME = "search_word"

# pubic columns for normal user
PUBLIC_COLUMNS = {
                   TB_DESKTOP_GROUP: ["desktop_group_name", "desktop_group_id", "description", "status", "desktop_count", "desktop_group_type", "transition_status"],

                   TB_DESKTOP_GROUP_DISK: [],

                   TB_DESKTOP_GROUP_NETWORK: ["network_config_id", "desktop_group_id", "desktop_group_name", "network_id", "network_type", "start_ip", "end_ip", 
                                                  "create_time", "status_time"],

                   TB_DESKTOP_GROUP_USER: ["user_id", "user_name", "real_name", "desktop_group_id", "desktop_group_name", "status", 
                                           "desktop_reserve", "need_desktop", "create_time"],

                   TB_DESKTOP: ["desktop_id", "instance_id", "desktop_image_id", "image_name", "description", 
                                "desktop_group_id", "desktop_group_name", "desktop_group_type", 
                                "instance_class", "hostname", "connect_status","delivery_group_id","delivery_group_name",
                                "status", "transition_status", "in_domain", "cpu", "memory", "gpu", "gpu_class", "instance_class", "ivshmem_enable", 
                                "usbredir", "clipboard", "filetransfer", "need_update", "need_monitor", 
                                "desktop_mode", "assign_state", "reg_state",
                                "auto_login", "create_time", "status_time", "zone", "qxl_number","cpu_model", "user_name"],

                   TB_DESKTOP_DISK: ["disk_id", "volume_id", "desktop_id", "desktop_name", "description", "disk_config_id", "disk_name", 
                                       "disk_type","desktop_group_id", "desktop_group_name", "size", "need_update", "status", "transition_status",
                                       "create_time", "status_time", "owner", "user_name", "zone"],
                   TB_RESOURCE_USER:["resource_id", "resource_type", "user_id", "user_name", "is_sync"],
                   TB_DESKTOP_IMAGE: ["desktop_image_id", "image_id", "image_name", "description", "cpu", "memory", "instance_class", "os_version", "base_image_id",
                                      "image_type", "status", "instance_id", "platform", "os_family", "transition_status", "session_type", "image_size", "is_default",
                                      "create_time", "status_time", "owner", "zone", "ui_type"],
                   TB_DESKTOP_NETWORK: ["network_id", "network_type", "router_id", "ip_network", "network_name", "description", "status", 
                                        "manager_ip", "dyn_ip_start", "dyn_ip_end", "create_time", "status_time", "transition_status", "zone"],
                   TB_DESKTOP_NIC: ["nic_id", "nic_name", "instance_id", "network_id", "network_name", "resource_id", "resource_name", "ip_network", 
                                    "private_ip", "is_occupied", "network_type", "need_update", 
                                    "desktop_group_id", "desktop_group_name", "network_config_id", "status", "transition_status", 
                                    "create_time", "status_time"],
                   TB_RESOURCE_JOB: ["job_id", "status", "action", "resource_ids", "create_time", "status_time"],
                   TB_DESKTOP_JOB: ["job_id", "status", "job_action", "resource_ids", "directive", "create_time", "status_time", "owner", "zone"],
                   TB_DESKTOP_TASK: ["task_id", "status", "task_type", "job_id", "resource_ids", "directive", "create_time", "status_time", "owner", "zone", "task_level"],
                   TB_CITRIX_POLICY_ITEM_CONFIG:["pol_item_name", "pol_item_type", "pol_item_state", "pol_item_value","pol_item_datatype", "update_time", 
                                                 "pol_item_name_ch","pol_item_tip","pol_item_unit","pol_item_value_ch","pol_item_path_ch","pol_item_path","col1","col2","col3","update_time","create_time","description"], 
                   TB_CITRIX_POLICY:["pol_id", "policy_name", "pol_priority","user_priority", "cmo_priority",  "description", "pol_state", "update_time", "create_time", "zone"],
                   TB_CITRIX_POLICY_ITEM:["pol_item_id","pol_id","pol_item_name", "pol_item_type", "pol_item_state","pol_item_value",  "update_time", "create_time", "zone"],
                   TB_CITRIX_POLICY_FILTER:["pol_filter_id" ,"pol_id" ,"pol_filter_name","pol_filter_type","pol_filter_state","pol_filter_value","pol_filter_mode","update_time", "create_time", "zone"],   
                   TB_POLICY_GROUP:["policy_group_id", "policy_group_name", "policy_group_type", "description", "is_apply", "is_default",
                                    "transition_status", "status", "create_time", "zone"],
                   TB_POLICY_GROUP_RESOURCE: ["policy_group_id","resource_id","status", "is_apply", "is_lock"],
                   TB_POLICY_GROUP_POLICY: ["policy_group_id","policy_id","status","is_base"],
                   TB_SECURITY_POLICY: ["security_policy_id","security_policy_name", "security_policy_type","description", "status",
                                        "policy_mode", "share_policy_id", "need_sync" ,"create_time","is_apply","zone", "is_default"],
                   TB_SECURITY_RULE: ["security_rule_id","security_rule_name","security_policy_id","protocol","direction","security_rule_type", "share_rule_id" ,"need_sync",
                                       "val1","val2","val3","priority","action","disabled", "create_time","zone" ],
                   TB_SECURITY_IPSET: ["security_ipset_id","security_ipset_name","description","ipset_type","val","is_apply","create_time", "zone", "is_default"],
                   TB_POLICY_RESOURCE_GROUP: ["policy_group_id", "resource_id", "resource_type", "policy_group_type"],
                   TB_DESKTOP_SNAPSHOT: ['snapshot_id', 'desktop_snapshot_id','snapshot_name', 'description', 'desktop_resource_id','resource_id', 'snapshot_type', 'root_id', "total_count",
                                         'parent_id', 'is_head','head_chain', 'raw_size', 'store_size', 'total_store_size', 'size', 'total_size', "status_time",
                                         'transition_status', 'status', 'status_time', 'snapshot_time', 'create_time','owner', 'zone'],
                   TB_SNAPSHOT_RESOURCE: ['desktop_snapshot_id','snapshot_group_snapshot_id','snapshot_name', 'snapshot_id', "resource_id",
                                          'desktop_resource_id', 'resource_name', 'resource_type','create_time', 'status_time', 'ymd','owner', 'zone'],
                   TB_SNAPSHOT_GROUP: ["snapshot_group_id", "snapshot_group_name", "description", "create_time","status","zone"],
                   TB_SNAPSHOT_GROUP_RESOURCE: ["snapshot_group_id", "desktop_resource_id", "resource_name"],
                   TB_SNAPSHOT_GROUP_SNAPSHOT: ["snapshot_group_snapshot_id", "snapshot_group_id", 'transition_status', 'status',"create_time"],
                   TB_SNAPSHOT_DISK_SNAPSHOT: ["snapshot_disk_snapshot_id", "desktop_id", "disk_id", "create_time"],
                   TB_SCHEDULER_TASK: ["scheduler_task_id", "task_name", "task_type", "status", "transition_status", "description", "resource_type", 
                                       "repeat", "period", "ymd", "hhmm", "term_time", "create_time", "update_time", "term_time", "execute_time", "owner", "zone"],
                   TB_SCHEDULER_TASK_RESOURCE: ["scheduler_task_id", "task_name", "task_type", "resource_id", "task_param", "task_msg", "job_id", "create_time"],
                   TB_SCHEDULER_TASK_HISTORY: ["scheduler_history_id", "scheduler_task_id", "task_name", "history_type", "task_msg", "create_time"],
                   TB_DESKTOP_VERSION: ["version_id", "version", "description", "sequence", "curr_version", "create_time"],                   
                   TB_VDI_SYSTEM_CONFIG: ["config_key", "config_value"],
                   TB_VDI_SYSTEM_LOG: ["system_log_id","user_id", "user_name", "user_role", "action_name", "log_info", "req_params", "log_type", "req_time","create_time"],
                   TB_DESKTOP_USER: ["user_id","auth_service_id","user_name","object_guid","real_name","description","password", "password_protect",
                                     "ou_dn", "user_dn","status","user_control","create_time","update_time", "role"],
                   TB_ZONE_USER: ["user_id","zone_id","role","status","user_name"],
                   TB_DESKTOP_USER_OU: ["user_ou_id","auth_service_id","ou_name","object_guid",
                                        "ou_dn","description","create_time","update_time"],
                   TB_DESKTOP_USER_GROUP:["user_group_id","auth_service_id","user_group_name",
                                          "object_guid","description","group_dn","create_time","update_time"],
                   TB_ZONE_USER_GROUP: ["user_group_id", "zone_id"],
                   TB_DESKTOP_USER_GROUP_USER: ["user_group_id", "user_id"],
                   TB_ZONE_USER_SCOPE: ["user_id", "resource_type", "resource_id", "action_type", "zone_id"],
                   TB_ZONE_USER_SCOPE_ACTION: ["action_id", "action_name", "action_api"],
                   TB_APPLY: ["apply_id", "apply_type", "apply_title", "apply_description", "status", "apply_user_id","resource_id","approve_status","apply_group_id",
                              "apply_resource_type","apply_parameter","approve_user_id", "approve_advice", "apply_age","approve_group_id",
                              "start_time","end_time","create_time","update_time", "approve_parameter", "resource_group_id", "zone_id"],
                   TB_APPLY_GROUP: ["apply_group_id","apply_group_name","description","create_time","update_time", "zone_id"],
                   TB_APPLY_GROUP_USER: ["user_id","apply_group_id","user_type","create_time"],
                   TB_APPLY_GROUP_RESOURCE: ["resource_id","apply_group_id","create_time"],
                   TB_APPROVE_GROUP: ["approve_group_id","approve_group_name","description","create_time","update_time", "zone_id"],
                   TB_APPROVE_GROUP_USER: ["user_id", "approve_group_id","user_type","create_time"],
                   TB_APPLY_APPROVE_GROUP_MAP: ["apply_group_id","approve_group_id","create_time"],
                   TB_VDI_DESKTOP_MESSAGE: ["message_id", "message","desktop_ids","message_time"],
                   TB_DELIVERY_GROUP: ["delivery_group_id", "delivery_group_name", "delivery_group_type", "desktop_kind", "description", "assign_name",
                                       "allocation_type", "delivery_type","desktop_hide_mode", "mode", "create_time", "zone"],
                   TB_DELIVERY_GROUP_USER: ["user_id", "delivery_group_id", "create_time"],
                   TB_VDAGENT_JOB: ["job_id", "status", "job_action", "resource_id", "directive", "create_time", "status_time"],
                   TB_VDHOST_JOB: ["job_id", "status", "job_action", "resource_id", "directive", "create_time", "status_time"],
                   TB_GUEST: ["desktop_id", "hostname", "login_user", "client_ip", "connect_status", "connect_time", "disconnect_time" ],
                   TB_USB_POLICY: ["usb_policy_id", "object_id", "policy_type", "priority", "class_id", "vendor_id", "product_id", "version_id", "allow", "create_time", "update_time"],
                   TB_COMPONENT_VERSION: ["component_id", "component_name", "component_type", "version", "filename", "description", "upgrade_packet_md5","upgrade_packet_size","status","transition_status","component_version_log","component_version_log_history","need_upgrade","update_time","create_time"],
                   TB_SOFTWARE_INFO: ["software_id", "software_name", "software_size","zone_id","create_time"],
                   TB_DESKTOP_ZONE: ["zone_id", "zone_name", "status", "platform","zone_deploy"],
                   TB_ZONE_CONNECTION: ["zone_id", "base_zone_id", "base_zone_name", "account_user_id",
                                  "account_user_name", "access_key_id", "secret_access_key", "host", "port", "protocol","host_ip",
                                  "http_socket_timeout", "status", "create_time", "status_time"],
                   TB_ZONE_RESOURCE_LIMIT:["zone_id", "instance_class", "disk_size","cpu_cores","memory_size","cpu_memory_pairs",
                                           "supported_gpu", "place_group", "max_disk_count","default_passwd", "network_type","router",
                                           "ivshmem","max_snapshot_count","max_chain_count","gpu_class_key","max_gpu_count"],
                   TB_ZONE_CITRIX_CONNECTION: ["zone_id", "host", "port", "protocol", "http_socket_timeout", 
                                    "status", "managed_resource", "storefront_uri","support_netscaler", "storefront_port", "netscaler_uri","netscaler_port","support_citrix_pms",  "create_time", "status_time"],
                   TB_AUTH_SERVICE: ["auth_service_id", "auth_service_name", "description", "auth_service_type", "admin_name","admin_password", "base_dn", "domain",
                                     "host", "port", "secret_port", "is_sync", "modify_password", "status", "create_time", "status_time", "dn_guid"],
                   TB_ZONE_AUTH: ["zone_id", "auth_service_id", "base_dn"],
                   TB_RADIUS_SERVICE: ["radius_service_id","radius_service_name","description","host","port","dn_guid",
                                       "acct_session","identifier","secret","status", "enable_radius","create_time","status_time", "auth_service_id", "ou_dn"],
                   TB_RADIUS_USER: ["radius_service_id", "user_id", "user_name", "check_radius", "user_type"],
                   TB_NOTICE_PUSH: ["notice_id", "notice_level", "title", "content", "scope", "notice_type", "force_read", "create_time"],
                   TB_NOTICE_USER: ["notice_id", "user_id", "user_type"],
                   TB_NOTICE_ZONE: ["notice_id", "zone_id", "user_scope"],
                   TB_NOTICE_READ: ["notice_id", "user_id", "user_name"],
                   TB_PROMPT_QUESTION: ["prompt_question_id", "question_content", "create_time"],
                   TB_PROMPT_ANSWER: ["prompt_answer_id", "prompt_question_id", "question_content", "user_id", "answer_content", "create_time"],
                   TB_SYSLOG_SERVER: ["syslog_server_id", "host", "port", "protocol", "runtime", "status", "create_time"],
                   TB_DESKTOP_LOGIN_RECORD: ["desktop_login_record_id", "desktop_id", "user_id", "user_name", "client_ip", "zone_id", "session_uid", "connect_status", "connect_time", "disconnect_time" ],
                   TB_USER_LOGIN_RECORD: ["user_login_record_id", "user_id", "user_name", "zone_id", "client_ip", "create_time", "status", "errmsg"],
                   TB_TERMINAL_MANAGEMENT: ["terminal_id","terminal_group_id","terminal_serial_number", "status", "login_user_name","terminal_ip","terminal_mac","terminal_type","terminal_version_number","login_hostname","connection_disconnection_time","create_time","zone_id","terminal_server_ip"],
                   TB_TERMINAL_GROUP: ["terminal_group_id", "terminal_group_name", "description", "create_time"],
                   TB_TERMINAL_GROUP_TERMINAL: ["terminal_group_id", "terminal_id", "create_time"],
                   TB_MODULE_CUSTOM: ["module_custom_id", "is_default", "custom_name","description","create_time"],
                   TB_MODULE_CUSTOM_ZONE: ["module_custom_id", "zone_id","user_scope"],
                   TB_MODULE_CUSTOM_USER: ["module_custom_id", "user_id", "zone_id","user_type"],
                   TB_MODULE_CUSTOM_CONFIG: ["module_custom_id","module_type","item_key","item_value","enable_module","create_time"],
                   TB_MODULE_TYPE: ["item_key", "enable_module"],
                   TB_SYSTEM_CUSTOM:["system_custom_id", "is_default","current_system_custom", "create_time"],
                   TB_SYSTEM_CUSTOM_CONFIG: ["system_custom_id","module_type","item_key","item_value","enable_module","create_time"],
                   TB_DESKTOP_SERVICE_MANAGEMENT: ["service_node_id", "service_id", "service_name", "description", "status","service_version", "service_ip",
                                                   "service_node_status", "service_node_ip","service_node_name","service_node_version","service_node_type", "service_port", "service_type","service_management_type","zone_id","create_time"],
                   TB_WORKFLOW_SERVICE: ["service_type", "service_name", "description"],
                   TB_WORKFLOW_SERVICE_ACTION: ["service_type", "api_action", "action_name", "priority", "is_head"],
                   TB_WORKFLOW_SERVICE_ACTION_INFO: ["api_action", "action_name", "required_params", "result_params", "public_params", "extra_params"],
                   TB_WORKFLOW_SERVICE_PARAM: ["param_key", "param_name"],
                   TB_WORKFLOW_MODEL: ["workflow_model_id", "workflow_model_name", "api_actions", "service_type", "env_params", "description", "create_time", "zone"],
                   TB_WORKFLOW: ["workflow_id", "workflow_model_id", "transition_status", "curr_action", "action_param", "workflow_params",
                                 "api_return", "api_error","result", "status", "create_time", "status_time"],
                   TB_WORKFLOW_CONFIG: ["workflow_config_id","workflow_model_id", "request_type","status","request_action"],
                   TB_INSTANCE_CLASS_DISK_TYPE: ["instance_class_key", "instance_class", "disk_type", "zone_deploy"],
                   TB_GPU_CLASS_TYPE: ["gpu_class_key", "gpu_class"],
                   TB_FILE_SHARE_GROUP: ["file_share_group_id", "file_share_service_id","file_share_group_name", "description","show_location","scope","file_share_group_dn","base_dn","trashed_status","trashed_time", "create_time","update_time"],
                   TB_FILE_SHARE_GROUP_ZONE: ["file_share_group_id", "zone_id", "user_scope"],
                   TB_FILE_SHARE_GROUP_USER: ["file_share_group_id", "user_id", "zone_id", "user_type","file_share_group_dn"],
                   TB_FILE_SHARE_GROUP_FILE: ["file_share_group_file_id", "file_share_group_id","file_share_group_file_name","file_share_group_file_alias_name",
                                              "description", "file_share_group_file_size", "transition_status", "file_share_group_dn","file_share_group_file_dn","trashed_status","trashed_time","create_time"],
                   TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY: ["file_download_history_id", "file_share_group_file_id", "user_id","user_name", "create_time","update_time"],
                   TB_FILE_SHARE_SERVICE: ["file_share_service_id", "file_share_service_name", "description","network_id","desktop_server_instance_id",
                                           "file_share_service_instance_id","private_ip","eip_add","vnas_private_ip","vnas_id","is_sync","transition_status",
                                           "status","scope","limit_rate","limit_conn","loaded_clone_instance_ip","fuser","fpw","ftp_chinese_encoding_rules",
                                           "create_method","max_download_file_size","max_upload_size_single_file","create_time","status_time"],
                                          
                   TB_BROKER_APP: ["broker_app_id", "display_name", "cmd_argument", "cmd_exe_path", "working_dir", "normal_display_name", "admin_display_name", 
                                   "icon_data", "floder_name", "create_time", "status_time", "zone", "description"],
                   TB_BROKER_APP_DELIVERY_GROUP: ["broker_app_id", "broker_app_name", "delivery_group_id", "delivery_group_name"],
                   TB_BROKER_APP_GROUP: ["broker_app_group_id", "broker_app_group_name", "description", "broker_app_group_uid", "create_time", "zone"],
                   TB_BROKER_APP_GROUP_BROKER_APP: ["broker_app_group_id", "broker_app_group_name", "broker_app_id", "broker_app_name"],
                   TB_API_LIMIT:["api_action", "enable", "refresh_interval", "refresh_time", "update_time"],
                   TB_DESKTOP_MAINTAINER: ["desktop_maintainer_id", "desktop_maintainer_name", "desktop_maintainer_type",
                            "description", "json_detail", "status", "transition_status","is_apply", "zone_id", "create_time"],
                   TB_DESKTOP_MAINTAINER_RESOURCE: ["desktop_maintainer_id", "resource_id", "resource_type", "resource_name", "zone_id","create_time"],
                   TB_GUEST_SHELL_COMMAND: ["guest_shell_command_id", "guest_shell_command_name", "guest_shell_command_type","command",'transition_status','status','command_response','create_time'],
                   TB_GUEST_SHELL_COMMAND_RESOURCE: ["guest_shell_command_id", "resource_id", "resource_type", "zone_id",'create_time'],
                   TB_GUEST_SHELL_COMMAND_RUN_HISTORY: ["guest_shell_command_run_history_id", "guest_shell_command_id", "resource_id","create_time","update_time"],
}

# pubic columns for console admin
CONSOLE_ADMIN_COLUMNS = {
                   TB_DESKTOP_GROUP: ["desktop_group_id", "desktop_group_name", "desktop_group_type", "description", "desktop_dn", "desktop_count", "dn_guid",
                                          "transition_status", "status", "desktop_image_id", "image_name", "naming_rule", "naming_count", "is_apply", "is_create", "save_disk", "save_desk",
                                          "cpu", "memory", "gpu", "gpu_class", "instance_class", "ivshmem_enable", "usbredir", "clipboard", "filetransfer", "managed_resource", "citrix_uuid",
                                          "qxl_number", "allocation_type", "provision_type", "create_time", "status_time", "owner", "zone"],

                   TB_DESKTOP_GROUP_DISK: ["disk_config_id", "disk_name", "desktop_group_id", "desktop_group_name", "disk_type", "size", "create_time", "status_time"],

                   TB_DESKTOP_GROUP_NETWORK: ["network_config_id", "desktop_group_id", "desktop_group_name", "network_id", "network_type", "start_ip", "end_ip", 
                                                  "create_time", "status_time"],

                   TB_DESKTOP_GROUP_USER: ["user_id", "user_name", "real_name", "desktop_group_id", "desktop_group_name", "status", 
                                           "desktop_reserve", "need_desktop", "create_time"],

                   TB_DESKTOP: ["desktop_id", "instance_id", "desktop_image_id", "image_name", "description", "desktop_group_id", "desktop_group_name", 
                                "desktop_group_type", "instance_class", "hostname", "connect_status", "dn_guid",
                                "login_time", "logout_time", "status", "transition_status", "connect_time", "in_domain", "save_disk", "save_desk", "cpu", 
                                "memory", "gpu", "gpu_class", "instance_class", "ivshmem_enable", "desktop_mode", "assign_state", "reg_state",
                                "usbredir", "clipboard", "filetransfer", "need_update", "need_monitor", "desktop_dn", "no_sync", "delivery_group_id", "delivery_group_name",
                                "qxl_number", "cpu_model","auto_login", "create_time", "status_time", "zone", "user_name"],

                   TB_DESKTOP_DISK: ["disk_id", "volume_id", "desktop_id", "desktop_name", "description", "disk_config_id", "disk_name", 
                                       "disk_type","desktop_group_id", "desktop_group_name", "size", "need_update", "status", "transition_status",
                                       "create_time", "status_time", "owner", "user_name", "zone"],
                   TB_RESOURCE_USER:["resource_id", "resource_type", "user_id", "user_name", "is_sync"],
                   TB_DESKTOP_IMAGE: ["desktop_image_id", "image_id", "image_name", "description", "cpu", "memory", "instance_class", "os_version","base_image_id",
                                      "image_type", "status", "instance_id", "platform", "os_family", "transition_status", "session_type","image_size", "is_default",
                                      "create_time", "status_time", "owner", "zone", "ui_type"],
                   TB_DESKTOP_NETWORK: ["network_id", "network_type", "router_id", "ip_network", "network_name", "description", "status", 
                                        "manager_ip", "dyn_ip_start", "dyn_ip_end", "create_time", "status_time", "transition_status", "zone"],
                   TB_DESKTOP_NIC: ["nic_id", "nic_name", "instance_id", "network_id", "network_name", "resource_id", "resource_name", "ip_network", "private_ip", "is_occupied", "network_type", "need_update", 
                                    "desktop_group_id", "desktop_group_name", "network_config_id", "status", "transition_status", 
                                    "create_time", "status_time"],
                   TB_RESOURCE_JOB: ["job_id", "status", "action", "resource_ids", "create_time", "status_time"],
                   TB_DESKTOP_JOB: ["job_id", "status", "job_action", "resource_ids", "directive", "create_time", "status_time", "owner", "zone"],
                   TB_DESKTOP_TASK: ["task_id", "status", "task_type", "job_id", "resource_ids", "directive", "create_time", "status_time", "owner", "zone", "task_level"],
                   TB_DESKTOP_SNAPSHOT: ['snapshot_id', 'desktop_snapshot_id','snapshot_name', 'description', 'desktop_resource_id','resource_id', 'snapshot_type', 'root_id', "total_count",
                                         'parent_id', 'is_head','head_chain', 'raw_size', 'store_size', 'total_store_size', 'size', 'total_size', "status_time",
                                         'transition_status', 'status', 'status_time', 'snapshot_time', 'create_time', 'owner', 'zone'],
                   TB_CITRIX_POLICY_ITEM_CONFIG:["pol_item_name", "pol_item_type", "pol_item_state", "pol_item_value","pol_item_datatype", "update_time", 
                                                 "pol_item_name_ch","pol_item_tip","pol_item_unit","pol_item_value_ch","pol_item_path_ch","pol_item_path","col1","col2","col3","update_time","create_time","description"],
                   TB_CITRIX_POLICY:["pol_id", "policy_name", "pol_priority","user_priority", "cmo_priority",  "description", "pol_state", "update_time", "create_time", "zone"],
                   TB_CITRIX_POLICY_ITEM:["pol_item_id","pol_id","pol_item_name", "pol_item_type", "pol_item_state","pol_item_value",  "update_time", "create_time", "zone"],
                   TB_CITRIX_POLICY_FILTER:["pol_filter_id" ,"pol_id" ,"pol_filter_name","pol_filter_type","pol_filter_state","pol_filter_value","pol_filter_mode","update_time", "create_time", "zone"],
                   TB_POLICY_GROUP:["policy_group_id", "policy_group_name", "policy_group_type", "description", "is_apply","transition_status", "is_default",
                                    "status", "create_time", "zone"],
                   TB_POLICY_GROUP_RESOURCE: ["policy_group_id","resource_id","status", "is_apply", "is_lock"],
                   TB_POLICY_GROUP_POLICY: ["policy_group_id","policy_id","status","is_base"],
                   TB_SECURITY_POLICY: ["security_policy_id","security_policy_name", "security_policy_type","description", "status",
                                        "policy_mode", "share_policy_id", "need_sync" , "create_time","is_apply","zone", "is_default"],
                   TB_SECURITY_RULE: ["security_rule_id","security_rule_name","security_policy_id","protocol","direction","security_rule_type", "share_rule_id" ,"need_sync",
                                       "val1","val2","val3","priority","action","disabled", "create_time","zone" ],
                   TB_SECURITY_IPSET: ["security_ipset_id","security_ipset_name","description","ipset_type","val","is_apply","create_time", "zone", "is_default"],
                   TB_POLICY_RESOURCE_GROUP: ["policy_group_id", "resource_id", "resource_type", "policy_group_type"],
                   TB_SNAPSHOT_RESOURCE: ['desktop_snapshot_id','snapshot_group_snapshot_id','snapshot_name', 'snapshot_id', "resource_id",
                                          'desktop_resource_id', 'resource_name', 'resource_type','create_time', 'status_time', 'ymd','owner', 'zone'],
                   TB_SNAPSHOT_GROUP: ["snapshot_group_id", "snapshot_group_name", "description", "create_time", "status","zone"],
                   TB_SNAPSHOT_GROUP_RESOURCE: ["snapshot_group_id", "desktop_resource_id", "resource_name"],
                   TB_SNAPSHOT_GROUP_SNAPSHOT: ["snapshot_group_snapshot_id", "snapshot_group_id",'transition_status', 'status', "create_time"],
                   TB_SNAPSHOT_DISK_SNAPSHOT: ["snapshot_disk_snapshot_id", "desktop_id", "disk_id", "create_time"],

                   TB_SCHEDULER_TASK: ["scheduler_task_id", "task_name", "task_type", "status", "transition_status", "description", "resource_type", 
                                       "repeat", "period", "ymd", "hhmm", "term_time", "create_time", "update_time", "execute_time", "term_time", "owner", "zone"],
                   TB_SCHEDULER_TASK_RESOURCE: ["scheduler_task_id", "task_name", "task_type", "resource_id", "task_param", "task_msg", "job_id", "create_time"],
                   TB_SCHEDULER_TASK_HISTORY: ["scheduler_history_id", "scheduler_task_id", "task_name", "history_type", "task_msg", "create_time"],
                   TB_DESKTOP_VERSION: ["version_id", "version", "description", "sequence", "curr_version", "create_time"],
                   TB_VDI_SYSTEM_CONFIG: ["config_key", "config_value"],
                   TB_VDI_SYSTEM_LOG: ["system_log_id","user_id", "user_name", "user_role", "action_name", "log_info", "req_params", "log_type","req_time","create_time"],
                   TB_DESKTOP_USER: ["user_id","auth_service_id","user_name","object_guid","real_name","description","password", "password_protect",
                                     "ou_dn", "user_dn","status","user_control","create_time","update_time", "role"],
                   TB_ZONE_USER: ["user_id","zone_id","role","status","user_name"],
                   TB_DESKTOP_USER_OU: ["user_ou_id","auth_service_id","ou_name","object_guid",
                                        "ou_dn","description","create_time","update_time"],
                   TB_DESKTOP_USER_GROUP:["user_group_id","auth_service_id","user_group_name",
                                          "object_guid","description","group_dn","create_time","update_time"],
                   TB_ZONE_USER_GROUP: ["user_group_id", "zone_id"],
                   TB_DESKTOP_USER_GROUP_USER: ["user_group_id", "user_id"],
                   TB_ZONE_USER_SCOPE: ["user_id", "resource_type", "resource_id", "action_type", "zone_id"],
                   TB_ZONE_USER_SCOPE_ACTION: ["action_id", "action_name", "action_api"],
                   TB_APPLY: ["apply_id", "apply_type", "apply_title", "apply_description", "status", "apply_user_id","resource_id","approve_status", "apply_group_id",
                              "apply_resource_type","apply_parameter","approve_user_id", "approve_advice", "apply_age","approve_group_id",
                              "start_time","end_time","create_time","update_time", "approve_parameter", "resource_group_id", "zone_id"],
                   TB_APPLY_GROUP: ["apply_group_id","apply_group_name","description","create_time","update_time", "zone_id"],
                   TB_APPLY_GROUP_USER: ["user_id","apply_group_id","user_type","create_time"],
                   TB_APPLY_GROUP_RESOURCE: ["resource_id","apply_group_id","create_time"],
                   TB_APPROVE_GROUP: ["approve_group_id","approve_group_name","description","create_time","update_time", "zone_id"],
                   TB_APPROVE_GROUP_USER: ["user_id", "approve_group_id","user_type","create_time"],
                   TB_APPLY_APPROVE_GROUP_MAP: ["apply_group_id","approve_group_id","create_time"],
                   TB_VDI_DESKTOP_MESSAGE: ["message_id", "message","desktop_ids","message_time"],
                   TB_DELIVERY_GROUP: ["delivery_group_id", "delivery_group_name", "delivery_group_type", "desktop_kind", "description", "assign_name",
                                       "allocation_type", "delivery_type","desktop_hide_mode", "mode", "create_time", "zone"],
                   TB_DELIVERY_GROUP_USER: ["user_id", "delivery_group_id", "create_time"],
                   TB_VDAGENT_JOB: ["job_id", "status", "job_action", "resource_id", "directive", "create_time", "status_time"],
                   TB_VDHOST_JOB: ["job_id", "status", "job_action", "resource_id", "directive", "create_time", "status_time"],
                   TB_GUEST: ["desktop_id", "hostname", "login_user", "client_ip", "connect_status", "connect_time", "disconnect_time" ],
                   TB_USB_POLICY: ["usb_policy_id", "object_id", "policy_type", "priority", "class_id", "vendor_id", "product_id", "version_id", "allow", "create_time", "update_time"],
                   TB_COMPONENT_VERSION: ["component_id", "component_name", "component_type", "version", "filename", "description", "upgrade_packet_md5","upgrade_packet_size","status","transition_status","component_version_log","component_version_log_history","need_upgrade","update_time","create_time"],
                   TB_SOFTWARE_INFO: ["software_id", "software_name", "software_size","zone_id","create_time"],
                   TB_DESKTOP_ZONE: ["zone_id", "zone_name", "platform", "status", "visibility", "description", "zone_deploy","create_time", "status_time"],
                   TB_ZONE_CONNECTION: ["zone_id", "base_zone_id", "base_zone_name", "account_user_id",
                                  "account_user_name", "access_key_id", "secret_access_key", "host", "port", "protocol","host_ip",
                                  "http_socket_timeout", "status", "create_time", "status_time"],
                   TB_ZONE_RESOURCE_LIMIT:["zone_id", "instance_class", "disk_size","cpu_cores","memory_size","cpu_memory_pairs",
                                           "supported_gpu", "place_group", "max_disk_count","default_passwd", "network_type","router",
                                           "ivshmem","max_snapshot_count","max_chain_count","gpu_class_key","max_gpu_count"],
                   TB_ZONE_CITRIX_CONNECTION: ["zone_id", "host", "port", "protocol", "http_socket_timeout", 
                                    "status", "managed_resource", "storefront_uri", "storefront_port", "netscaler_uri","netscaler_port","support_netscaler","support_citrix_pms",  "create_time", "status_time"],
                   TB_AUTH_SERVICE: ["auth_service_id", "auth_service_name", "description", "auth_service_type", "admin_name","admin_password", "base_dn", "domain", 
                                     "host", "port", "secret_port", "is_sync", "modify_password", "status", "create_time", "status_time", "dn_guid"],
                   TB_ZONE_AUTH: ["zone_id", "auth_service_id", "base_dn"],
                   TB_RADIUS_SERVICE: ["radius_service_id","radius_service_name","description","host","port","dn_guid",
                                       "acct_session","identifier","secret","status", "enable_radius","create_time","status_time", "auth_service_id", "ou_dn"],
                   TB_RADIUS_USER: ["radius_service_id", "user_id", "user_name", "check_radius", "user_type"],
                   TB_NOTICE_PUSH: ["notice_id", "notice_type", "notice_level", "title", "status", "content", "create_time", "expired_time", "execute_time", "owner", "scope", "force_read"],
                   TB_NOTICE_USER: ["notice_id", "user_id", "user_type"],
                   TB_NOTICE_ZONE: ["notice_id", "zone_id", "user_scope"],
                   TB_NOTICE_READ: ["notice_id", "user_id", "user_name"],
                   TB_PROMPT_QUESTION: ["prompt_question_id", "question_content", "create_time"],
                   TB_PROMPT_ANSWER: ["prompt_answer_id", "prompt_question_id", "question_content", "user_id", "answer_content", "create_time"],
                   TB_SYSLOG_SERVER: ["syslog_server_id", "host", "port", "protocol", "runtime", "status", "create_time"],
                   TB_DESKTOP_LOGIN_RECORD: ["desktop_login_record_id", "desktop_id", "user_id", "user_name", "client_ip", "zone_id", "session_uid", "connect_status", "connect_time", "disconnect_time" ],
                   TB_USER_LOGIN_RECORD: ["user_login_record_id", "user_id", "user_name", "zone_id", "client_ip", "create_time", "status", "errmsg"],
                   TB_TERMINAL_MANAGEMENT: ["terminal_id", "terminal_group_id","terminal_serial_number", "status", "login_user_name","terminal_ip","terminal_mac","terminal_type","terminal_version_number","login_hostname","connection_disconnection_time","create_time","zone_id","terminal_server_ip"],
                   TB_TERMINAL_GROUP: ["terminal_group_id", "terminal_group_name", "description", "create_time"],
                   TB_TERMINAL_GROUP_TERMINAL: ["terminal_group_id", "terminal_id", "create_time"],
                   TB_MODULE_CUSTOM: ["module_custom_id", "is_default","custom_name","description", "create_time"],
                   TB_MODULE_CUSTOM_ZONE: ["module_custom_id", "zone_id","user_scope"],
                   TB_MODULE_CUSTOM_USER: ["module_custom_id", "user_id", "zone_id","user_type"],
                   TB_MODULE_CUSTOM_CONFIG: ["module_custom_id","module_type","item_key","item_value","enable_module","create_time"],
                   TB_MODULE_TYPE: ["item_key", "enable_module"],
                   TB_SYSTEM_CUSTOM:["system_custom_id", "is_default","current_system_custom", "create_time"],
                   TB_SYSTEM_CUSTOM_CONFIG: ["system_custom_id","module_type","item_key","item_value","enable_module","create_time"],
                   TB_DESKTOP_SERVICE_MANAGEMENT: ["service_node_id", "service_id", "service_name", "description", "status","service_version", "service_ip",
                                                   "service_node_status", "service_node_ip","service_node_name","service_node_version","service_node_type", "service_port", "service_type","service_management_type","zone_id","create_time"],
                   TB_WORKFLOW_SERVICE: ["service_type", "service_name", "description"],
                   TB_WORKFLOW_SERVICE_ACTION: ["service_type", "api_action", "action_name", "priority", "is_head"],
                   TB_WORKFLOW_SERVICE_ACTION_INFO: ["api_action", "action_name", "required_params", "result_params", "public_params", "extra_params"],
                   TB_WORKFLOW_SERVICE_PARAM: ["param_key", "param_name"],
                   TB_WORKFLOW_MODEL: ["workflow_model_id", "workflow_model_name", "api_actions", "service_type", "env_params", "description", "create_time", "zone"],
                   TB_WORKFLOW: ["workflow_id", "workflow_model_id", "transition_status", "curr_action", "action_param", "workflow_params",
                                 "api_return","api_error", "result", "status", "create_time", "status_time"],
                   TB_WORKFLOW_CONFIG: ["workflow_config_id", "workflow_model_id", "request_type", "status","request_action"],
                   TB_INSTANCE_CLASS_DISK_TYPE: ["instance_class_key", "instance_class", "disk_type", "zone_deploy"],
                   TB_GPU_CLASS_TYPE: ["gpu_class_key", "gpu_class"],
                   TB_FILE_SHARE_GROUP: ["file_share_group_id","file_share_service_id", "file_share_group_name", "description", 
                                         "show_location","scope","file_share_group_dn","base_dn","trashed_status","trashed_time","create_time","update_time"],
                   TB_FILE_SHARE_GROUP_ZONE: ["file_share_group_id", "zone_id", "user_scope"],
                   TB_FILE_SHARE_GROUP_USER: ["file_share_group_id", "user_id", "zone_id", "user_type","file_share_group_dn"],
                   TB_FILE_SHARE_GROUP_FILE: ["file_share_group_file_id", "file_share_group_id","file_share_group_file_name","file_share_group_file_alias_name",
                                              "description", "file_share_group_file_size", "transition_status","file_share_group_dn",
                                              "file_share_group_file_dn","trashed_status","trashed_time", "create_time"],
                   TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY: ["file_download_history_id", "file_share_group_file_id", "user_id","user_name", "create_time","update_time"],
                   TB_FILE_SHARE_SERVICE: ["file_share_service_id", "file_share_service_name", "description","network_id",
                                           "desktop_server_instance_id","file_share_service_instance_id","private_ip","eip_addr",
                                           "vnas_private_ip","vnas_id","is_sync","transition_status","status","scope",
                                           "limit_rate","limit_conn","loaded_clone_instance_ip","fuser","fpw","ftp_chinese_encoding_rules",
                                           "create_method","max_download_file_size","max_upload_size_single_file","create_time","status_time"],
                   TB_FILE_SHARE_SERVICE_VNAS: ["vnas_id", "vnas_name", "vnas_private_ip", "status", "create_time"],

                   TB_BROKER_APP: ["broker_app_id", "display_name", "cmd_argument", "cmd_exe_path", "working_dir", "normal_display_name", "admin_display_name", 
                                   "icon_data", "floder_name", "create_time", "status_time", "zone", "description"],
                   TB_BROKER_APP_DELIVERY_GROUP: ["broker_app_id", "broker_app_name", "delivery_group_id", "delivery_group_name"],
                   TB_BROKER_APP_GROUP: ["broker_app_group_id", "broker_app_group_name", "description", "broker_app_group_uid", "create_time", "zone"],
                   TB_BROKER_APP_GROUP_BROKER_APP: ["broker_app_group_id", "broker_app_group_name", "broker_app_id", "broker_app_name"],
                   TB_API_LIMIT:["api_action", "enable", "refresh_interval", "refresh_time", "update_time"],

                   TB_DESKTOP_MAINTAINER: ["desktop_maintainer_id", "desktop_maintainer_name", "desktop_maintainer_type",
                            "description", "json_detail", "status", "transition_status","is_apply", "zone_id", "create_time"],
                   TB_DESKTOP_MAINTAINER_RESOURCE: ["desktop_maintainer_id", "resource_id", "resource_type", "resource_name", "zone_id","create_time"],
                   TB_GUEST_SHELL_COMMAND: ["guest_shell_command_id", "guest_shell_command_name", "guest_shell_command_type","command",'transition_status','status','command_response','create_time'],
                   TB_GUEST_SHELL_COMMAND_RUN_HISTORY: ["guest_shell_command_run_history_id", "guest_shell_command_id","resource_id", "create_time","update_time"],
}

# pubic columns for root user
GOLBAL_ADMIN_COLUMNS = {
                   TB_DESKTOP_GROUP: ["desktop_group_id", "desktop_group_name", "desktop_group_type", "description", "desktop_dn", "desktop_count", "dn_guid",
                                          "transition_status", "status", "desktop_image_id", "image_name", "naming_rule", "naming_count", "is_apply", "is_create", "save_disk", "save_desk",
                                          "cpu", "memory", "gpu", "gpu_class", "instance_class", "ivshmem_enable", "usbredir", "clipboard", "filetransfer", "managed_resource", "citrix_uuid",
                                          "qxl_number", "allocation_type", "provision_type", "create_time", "status_time", "owner", "zone"],

                   TB_DESKTOP_GROUP_DISK: ["disk_config_id", "disk_name", "desktop_group_id", "desktop_group_name", "disk_type", "size", "create_time", "status_time"],

                   TB_DESKTOP_GROUP_NETWORK: ["network_config_id", "desktop_group_id", "desktop_group_name", "network_id", "network_type", "start_ip", "end_ip", 
                                                  "create_time", "status_time"],

                   TB_DESKTOP_GROUP_USER: ["user_id", "user_name", "real_name", "desktop_group_id", "desktop_group_name", "status", 
                                           "desktop_reserve", "need_desktop", "create_time"],

                   TB_DESKTOP: ["desktop_id", "instance_id", "desktop_image_id", "image_name", "description", "desktop_group_id", "desktop_group_name", 
                                "desktop_group_type", "instance_class", "hostname", "connect_status", "dn_guid",
                                "login_time", "logout_time", "status", "transition_status", "connect_time", "in_domain", "save_disk", "save_desk", 
                                "cpu", "memory", "gpu", "gpu_class", "instance_class", "ivshmem_enable", "desktop_mode", "assign_state", "reg_state",
                                "usbredir", "clipboard", "filetransfer", "need_update", "need_monitor", "desktop_dn", "no_sync", "delivery_group_id", "delivery_group_name",
                                "qxl_number","cpu_model", "auto_login", "create_time", "status_time", "zone", "user_name"],

                   TB_DESKTOP_DISK: ["disk_id", "volume_id", "desktop_id", "desktop_name", "description", "disk_config_id", "disk_name", 
                                       "disk_type","desktop_group_id", "desktop_group_name", "size", "need_update", "status", "transition_status",
                                       "create_time", "status_time", "owner", "user_name", "zone"],
                   TB_RESOURCE_USER:["resource_id", "resource_type", "user_id", "user_name", "is_sync"],
                   TB_DESKTOP_IMAGE: ["desktop_image_id", "image_id", "image_name", "description", "cpu", "memory", "instance_class", "os_version", "base_image_id",
                                      "image_type", "status", "instance_id", "platform", "os_family", "transition_status", "session_type","image_size", "is_default",
                                      "create_time", "status_time", "owner", "zone", "ui_type"],
                   TB_DESKTOP_NETWORK: ["network_id", "network_type", "router_id", "ip_network", "network_name", "description", "status", 
                                        "manager_ip", "dyn_ip_start", "dyn_ip_end", "create_time", "status_time", "transition_status", "zone"],
                   TB_DESKTOP_NIC: ["nic_id", "nic_name", "instance_id", "network_id", "network_name", "resource_id", "resource_name", "ip_network", "private_ip", "is_occupied", "network_type", "need_update", 
                                    "desktop_group_id", "desktop_group_name", "network_config_id", "status", "transition_status", 
                                    "create_time", "status_time"],
                   TB_RESOURCE_JOB: ["job_id", "status", "action", "resource_ids", "create_time", "status_time"],
                   TB_DESKTOP_JOB: ["job_id", "status", "job_action", "resource_ids", "directive", "create_time", "status_time", "owner", "zone"],
                   TB_DESKTOP_TASK: ["task_id", "status", "task_type", "job_id", "resource_ids", "directive", "create_time", "status_time", "owner", "zone", "task_level"],
                   TB_CITRIX_POLICY_ITEM_CONFIG:["pol_item_name", "pol_item_type", "pol_item_state", "pol_item_value","pol_item_datatype", "update_time", 
                                                 "pol_item_name_ch","pol_item_tip","pol_item_unit","pol_item_value_ch","pol_item_path_ch","pol_item_path","col1","col2","col3","update_time","create_time","description"],
                   TB_CITRIX_POLICY:["pol_id", "policy_name", "pol_priority", "user_priority", "cmo_priority", "description", "pol_state", "update_time", "create_time", "zone"],
                   TB_CITRIX_POLICY_ITEM:["pol_item_id","pol_id","pol_item_name", "pol_item_type", "pol_item_state","pol_item_value", "update_time", "create_time", "zone"],
                   TB_CITRIX_POLICY_FILTER:["pol_filter_id" ,"pol_id" ,"pol_filter_name","pol_filter_type","pol_filter_state","pol_filter_value","pol_filter_mode","update_time", "create_time", "zone"],
                   TB_POLICY_GROUP:["policy_group_id", "policy_group_name", "policy_group_type", "is_apply", "description","transition_status", "is_default",
                                    "status", "create_time", "zone"],
                   TB_POLICY_GROUP_RESOURCE: ["policy_group_id","resource_id","status", "is_apply", "is_lock"],
                   TB_POLICY_GROUP_POLICY: ["policy_group_id","policy_id","status","is_base"],
                   TB_SECURITY_POLICY: ["security_policy_id","security_policy_name", "security_policy_type", "description", "status",
                                        "policy_mode", "share_policy_id", "need_sync" ,"create_time","is_apply","zone", "is_default"],
                   TB_SECURITY_RULE: ["security_rule_id","security_rule_name","security_policy_id","protocol","direction","security_rule_type", "share_rule_id" ,"need_sync",
                                       "val1","val2","val3","priority","action","disabled", "create_time","zone"],
                   TB_SECURITY_IPSET: ["security_ipset_id","security_ipset_name","description","ipset_type","val","is_apply","create_time", "zone", "is_default"],
                   TB_POLICY_RESOURCE_GROUP: ["policy_group_id", "resource_id", "resource_type", "policy_group_type"],
                   TB_DESKTOP_SNAPSHOT: ['snapshot_id', 'desktop_snapshot_id','snapshot_name', 'description', 'desktop_resource_id','resource_id', 'snapshot_type', 'root_id', "total_count",
                                         'parent_id', 'is_head','head_chain', 'raw_size', 'store_size', 'total_store_size', 'size', 'total_size', "status_time",
                                         'transition_status', 'status', 'status_time', 'snapshot_time', 'create_time','owner', 'zone'],
                   TB_SNAPSHOT_RESOURCE: ['desktop_snapshot_id','snapshot_group_snapshot_id','snapshot_name', 'snapshot_id', "resource_id",
                                          'desktop_resource_id', 'resource_name', 'resource_type','create_time', 'status_time', 'ymd','owner', 'zone'],
                   TB_SNAPSHOT_GROUP: ["snapshot_group_id", "snapshot_group_name", "description", "create_time", "status", "zone"],
                   TB_SNAPSHOT_GROUP_RESOURCE: ["snapshot_group_id", "desktop_resource_id", "resource_name"],
                   TB_SNAPSHOT_GROUP_SNAPSHOT: ["snapshot_group_snapshot_id", "snapshot_group_id",'transition_status', 'status', "create_time"],
                   TB_SNAPSHOT_DISK_SNAPSHOT: ["snapshot_disk_snapshot_id", "desktop_id", "disk_id", "create_time"],
                   TB_SCHEDULER_TASK: ["scheduler_task_id", "task_name", "task_type", "status", "transition_status", "description", "resource_type", 
                                       "repeat", "period", "ymd", "hhmm", "term_time", "create_time", "update_time", "execute_time", "term_time", "owner", "zone"],
                   TB_SCHEDULER_TASK_RESOURCE: ["scheduler_task_id", "task_name", "task_type", "resource_id", "task_param", "task_msg", "job_id", "create_time"],
                   TB_SCHEDULER_TASK_HISTORY: ["scheduler_history_id", "scheduler_task_id", "task_name", "history_type", "task_msg", "create_time"],
                   TB_DESKTOP_VERSION: ["version_id", "version", "description", "sequence", "curr_version", "create_time"],
                   TB_VDI_SYSTEM_CONFIG: ["config_key", "config_value"],
                   TB_VDI_SYSTEM_LOG: ["system_log_id","user_id", "user_name", "user_role", "action_name", "log_info", "req_params", "log_type","req_time","create_time"],
                   TB_DESKTOP_USER: ["user_id","auth_service_id","user_name","object_guid","real_name","description","password", "password_protect"
                                     "ou_dn", "user_dn","status","user_control","create_time","update_time", "role"],
                   TB_ZONE_USER: ["user_id","zone_id","role","status","user_name"],
                   TB_DESKTOP_USER_OU: ["user_ou_id","auth_service_id","ou_name","object_guid",
                                        "ou_dn","description","create_time","update_time"],
                   TB_DESKTOP_USER_GROUP:["user_group_id","auth_service_id","user_group_name",
                                          "object_guid","description","group_dn","create_time","update_time"],
                   TB_ZONE_USER_GROUP: ["user_group_id", "zone_id"],
                   TB_DESKTOP_USER_GROUP_USER: ["user_group_id", "user_id"],
                   TB_ZONE_USER_SCOPE: ["user_id", "resource_type", "resource_id", "action_type", "zone_id"],
                   TB_ZONE_USER_SCOPE_ACTION: ["action_id", "action_name", "action_api"],
                   TB_APPLY: ["apply_id", "apply_type", "apply_title", "apply_description", "status", "apply_user_id","resource_id","approve_status", "apply_group_id",
                              "apply_resource_type","apply_parameter","approve_user_id", "approve_advice", "apply_age","approve_group_id",
                              "start_time","end_time","create_time","update_time", "approve_parameter", "resource_group_id", "zone_id"],
                   TB_APPLY_GROUP: ["apply_group_id","apply_group_name","description","create_time","update_time", "zone_id"],
                   TB_APPLY_GROUP_USER: ["user_id","apply_group_id","user_type","create_time"],
                   TB_APPLY_GROUP_RESOURCE: ["resource_id","apply_group_id","create_time"],
                   TB_APPROVE_GROUP: ["approve_group_id","approve_group_name","description","create_time","update_time", "zone_id"],
                   TB_APPROVE_GROUP_USER: ["user_id", "approve_group_id","user_type","create_time"],
                   TB_APPLY_APPROVE_GROUP_MAP: ["apply_group_id","approve_group_id","create_time"],
                   TB_VDI_DESKTOP_MESSAGE: ["message_id", "message","desktop_ids","message_time"],
                   TB_DELIVERY_GROUP: ["delivery_group_id", "delivery_group_name", "delivery_group_type", "desktop_kind", "description", "assign_name",
                                       "allocation_type", "delivery_type", "desktop_hide_mode","mode", "create_time", "zone"],
                   TB_DELIVERY_GROUP_USER: ["user_id", "delivery_group_id", "create_time"],
                   TB_VDAGENT_JOB: ["job_id", "status", "job_action", "resource_id", "directive", "create_time", "status_time"],
                   TB_VDHOST_JOB: ["job_id", "status", "job_action", "resource_id", "directive", "create_time", "status_time"],
                   TB_GUEST: ["desktop_id", "hostname", "login_user", "client_ip", "connect_status", "connect_time", "disconnect_time" ],
                   TB_USB_POLICY: ["usb_policy_id", "object_id", "policy_type", "priority", "class_id", "vendor_id", "product_id", "version_id", "allow", "create_time", "update_time"],
                   TB_COMPONENT_VERSION: ["component_id", "component_name", "component_type", "version", "filename", "description","upgrade_packet_md5", "upgrade_packet_size","status","transition_status","component_version_log","component_version_log_history","need_upgrade","update_time","create_time"],
                   TB_SOFTWARE_INFO: ["software_id", "software_name", "software_size","zone_id","create_time"],
                   TB_DESKTOP_ZONE: ["zone_id", "zone_name", "platform", "status", "visibility", "description", "zone_deploy","create_time", "status_time"],
                   TB_ZONE_CONNECTION: ["zone_id", "base_zone_id", "base_zone_name", "account_user_id",
                                  "account_user_name", "access_key_id", "secret_access_key", "host", "port", "protocol","host_ip",
                                  "http_socket_timeout", "status", "create_time", "status_time"],
                   TB_ZONE_RESOURCE_LIMIT:["zone_id", "instance_class", "disk_size","cpu_cores","memory_size","cpu_memory_pairs",
                                           "supported_gpu", "place_group", "max_disk_count","default_passwd", "network_type","router",
                                           "ivshmem","max_snapshot_count","max_chain_count","gpu_class_key","max_gpu_count"],
                   TB_ZONE_CITRIX_CONNECTION: ["zone_id", "host", "port", "protocol", "http_socket_timeout", 
                                    "status", "managed_resource", "storefront_uri", "storefront_port", "netscaler_uri","netscaler_port","support_netscaler","support_citrix_pms",  "create_time", "status_time"],
                   TB_AUTH_SERVICE: ["auth_service_id", "auth_service_name", "description", "auth_service_type", "admin_name","admin_password", "base_dn", "domain", 
                                     "host", "port", "secret_port", "is_sync", "modify_password", "status", "create_time", "status_time", "dn_guid"],
                   TB_ZONE_AUTH: ["zone_id", "auth_service_id", "base_dn"],
                   TB_RADIUS_SERVICE: ["radius_service_id","radius_service_name","description","host","port","dn_guid",
                                       "acct_session","identifier","secret","status", "enable_radius","create_time","status_time", "auth_service_id", "ou_dn"],
                   TB_RADIUS_USER: ["radius_service_id", "user_id", "user_name", "check_radius", "user_type"],
                   TB_NOTICE_PUSH: ["notice_id", "notice_type", "notice_level", "title", "content", "status", "scope", "create_time", "expired_time", "execute_time", "owner", "force_read"],
                   TB_NOTICE_USER: ["notice_id", "user_id", "user_type"],
                   TB_NOTICE_ZONE: ["notice_id", "zone_id", "user_scope"],
                   TB_NOTICE_READ: ["notice_id", "user_id", "user_name"],
                   TB_PROMPT_QUESTION: ["prompt_question_id", "question_content", "create_time"],
                   TB_PROMPT_ANSWER: ["prompt_answer_id", "prompt_question_id", "question_content", "user_id", "answer_content", "create_time"],
                   TB_SYSLOG_SERVER: ["syslog_server_id", "host", "port", "protocol", "runtime", "status", "create_time"],
                   TB_DESKTOP_LOGIN_RECORD: ["desktop_login_record_id", "desktop_id", "user_id", "user_name", "client_ip", "zone_id", "session_uid", "connect_status", "connect_time", "disconnect_time" ],
                   TB_USER_LOGIN_RECORD: ["user_login_record_id", "user_id", "user_name", "zone_id", "client_ip", "create_time", "status", "errmsg"],
                   TB_TERMINAL_MANAGEMENT: ["terminal_id", "terminal_group_id","terminal_serial_number", "status", "login_user_name","terminal_ip","terminal_mac","terminal_type","terminal_version_number","login_hostname","connection_disconnection_time","create_time","zone_id","terminal_server_ip"],
                   TB_TERMINAL_GROUP: ["terminal_group_id", "terminal_group_name", "description", "create_time"],
                   TB_TERMINAL_GROUP_TERMINAL: ["terminal_group_id", "terminal_id", "create_time"],
                   TB_MODULE_CUSTOM: ["module_custom_id", "is_default","custom_name","description", "create_time"],
                   TB_MODULE_CUSTOM_ZONE: ["module_custom_id", "zone_id","user_scope"],
                   TB_MODULE_CUSTOM_USER: ["module_custom_id", "user_id", "zone_id","user_type"],
                   TB_MODULE_CUSTOM_CONFIG: ["module_custom_id","module_type","item_key","item_value","enable_module","create_time"],
                   TB_MODULE_TYPE: ["item_key", "enable_module"],
                   TB_SYSTEM_CUSTOM:["system_custom_id", "is_default","current_system_custom", "create_time"],
                   TB_SYSTEM_CUSTOM_CONFIG: ["system_custom_id","module_type","item_key","item_value","enable_module","create_time"],
                   TB_DESKTOP_SERVICE_MANAGEMENT: ["service_node_id", "service_id", "service_name", "description", "status","service_version", "service_ip",
                                                   "service_node_status", "service_node_ip","service_node_name","service_node_version","service_node_type", "service_port", "service_type","service_management_type","zone_id","create_time"],
                   TB_WORKFLOW_SERVICE: ["service_type", "service_name", "description"],
                   TB_WORKFLOW_SERVICE_ACTION: ["service_type", "api_action", "action_name", "priority", "is_head"],
                   TB_WORKFLOW_SERVICE_ACTION_INFO: ["api_action", "action_name", "required_params", "result_params", "public_params", "extra_params"],
                   TB_WORKFLOW_SERVICE_PARAM: ["param_key", "param_name"],
                   TB_WORKFLOW_MODEL: ["workflow_model_id", "workflow_model_name", "api_actions", "service_type", "env_params", "description", "create_time", "zone"],
                   TB_WORKFLOW: ["workflow_id", "workflow_model_id", "transition_status", "curr_action", "action_param", "workflow_params",
                                 "api_return","api_error", "result", "status", "create_time", "status_time"],
                   TB_WORKFLOW_CONFIG: ["workflow_config_id", "workflow_model_id", "request_type", "status","request_action"],
                   TB_INSTANCE_CLASS_DISK_TYPE: ["instance_class_key", "instance_class", "disk_type", "zone_deploy"],
                   TB_GPU_CLASS_TYPE: ["gpu_class_key", "gpu_class"],
                   TB_FILE_SHARE_GROUP: ["file_share_group_id","file_share_service_id", "file_share_group_name", "description", "show_location","scope","file_share_group_dn","base_dn","trashed_status","trashed_time","create_time","update_time"],
                   TB_FILE_SHARE_GROUP_ZONE: ["file_share_group_id", "zone_id", "user_scope"],
                   TB_FILE_SHARE_GROUP_USER: ["file_share_group_id", "user_id", "zone_id", "user_type","file_share_group_dn"],
                   TB_FILE_SHARE_GROUP_FILE: ["file_share_group_file_id", "file_share_group_id", "file_share_group_file_name","file_share_group_file_alias_name",
                                              "description", "file_share_group_file_size", "transition_status","file_share_group_dn","file_share_group_file_dn","trashed_status","trashed_time", "create_time"],
                   TB_FILE_SHARE_GROUP_FILE_DOWNLOAD_HISTORY: ["file_download_history_id", "file_share_group_file_id", "user_id","user_name", "create_time","update_time"],
                   TB_FILE_SHARE_SERVICE: ["file_share_service_id", "file_share_service_name", "description","network_id","desktop_server_instance_id","file_share_service_instance_id",
                                           "private_ip","eip_addr","vnas_private_ip","vnas_id","is_sync","transition_status","status","scope","limit_rate","limit_conn",
                                           "loaded_clone_instance_ip","fuser","fpw","ftp_chinese_encoding_rules","create_method",
                                           "max_download_file_size","max_upload_size_single_file","create_time","status_time"],
                   TB_FILE_SHARE_SERVICE_VNAS: ["vnas_id", "vnas_name", "vnas_private_ip", "status", "create_time"],

                   TB_BROKER_APP: ["broker_app_id", "display_name", "cmd_argument", "cmd_exe_path", "working_dir", "normal_display_name", "admin_display_name", 
                                   "icon_data", "floder_name", "create_time", "status_time", "zone", "description"],
                   TB_BROKER_APP_DELIVERY_GROUP: ["broker_app_id", "broker_app_name", "delivery_group_id", "delivery_group_name"],
                   TB_BROKER_APP_GROUP: ["broker_app_group_id", "broker_app_group_name", "description", "broker_app_group_uid", "create_time", "zone"],
                   TB_BROKER_APP_GROUP_BROKER_APP: ["broker_app_group_id", "broker_app_group_name", "broker_app_id", "broker_app_name"],
                   TB_API_LIMIT:["api_action", "enable", "refresh_interval", "refresh_time", "update_time"],
                   TB_DESKTOP_MAINTAINER: ["desktop_maintainer_id", "desktop_maintainer_name", "desktop_maintainer_type",
                            "description", "json_detail", "status", "transition_status","is_apply", "zone_id", "create_time"],
                   TB_DESKTOP_MAINTAINER_RESOURCE: ["desktop_maintainer_id", "resource_id", "resource_type", "resource_name", "zone_id","create_time"],
                   TB_GUEST_SHELL_COMMAND: ["guest_shell_command_id", "guest_shell_command_name", "guest_shell_command_type","command",'transition_status','status','command_response','create_time'],
                   TB_GUEST_SHELL_COMMAND_RESOURCE: ["guest_shell_command_id", "resource_id", "resource_type", "zone_id", 'create_time'],
                   TB_GUEST_SHELL_COMMAND_RUN_HISTORY: ["guest_shell_command_run_history_id", "guest_shell_command_id","resource_id", "create_time","update_time"],

}

# the columns that need to be push as an update event when it's updated
UPDATE_EVENT_COLUMNS = {
    TB_DESKTOP_GROUP: ["status", "transition_status", "status_time", "create_time", "private_ip"],
}
# the tables that need to be push as an create event when inserted with new records
CREATE_EVENT_TABLES = []
# the tables that need to be push as an delete event when deleting records
DELETE_EVENT_TABLES = []
# tables with composite primary keys
COMPOSITE_PRIMARY_KEY_TABLES = {
    TB_DESKTOP_GROUP_USER: ["desktop_group_id", "user_id"],
}
# default limit number for each selection
DEFAULT_LIMIT = 800
# maximum limit number for each selection
MAX_LIMIT = 5000
# maximum offset number for each selection
MAX_OFFSET = 10000000

#resource type
RESOURCE_TYPE_NOT_DEFINED = "not-defined"
RESTYPE_DESKTOP_GROUP = "desktop-group"
RESTYPE_DESKTOP_NETWORK = "desktop-network"
RESTYPE_DESKTOP = "desktop"
RESTYPE_DESKTOP_IMAGE = "desktop-image"
RESTYPE_SCHEDULER_TASK = 'scheduler-task'
RESTYPE_SCHEDULER_TASK_HISTORY = 'scheduler-history'
RESTYPE_DESKTOP_DISK = "disk"
RESTYPE_USER = "user"
RESTYPE_USER_OU= "user-ou"
RESTYPE_USER_GROUP = "user-group"
RESTYPE_DESKTOP_GROUP_DISK = "desktop-group-disk"
RESTYPE_DESKTOP_GROUP_NETWORK = "desktop-group-network"
RESTYPE_DELIVERY_GROUP = "delivery-group"
RESTYPE_SNAPSHOT_GROUP = "snapshot-group"
RESTYPE_APPROVE_GROUP = "approve-group"
RESTYPE_APPLY_GROUP = "apply-group"
RESTYPE_POLICY_GROUP = "policy-group"
RESTYPE_CITRIX_POLICY = "citrix-policy"
RESTYPE_CITRIX_POLICY_ITEM = "citrix-policy-item"
RESTYPE_CITRIX_POLICY_FILTER = "citrix-policy-filter"
RESTYPE_SECURITY_POLICY = "security-policy"
RESTYPE_SECURITY_RULE = "security-rule"
RESTYPE_SECURITY_IPSET = "security-ipset"
RESTYPE_AUTH_SERVICE = "auth-service"
RESTYPE_RADIUS_SERVICE = "radius-service"
RESTYPE_NOTICE_PUSH = "notice-push"
RESTYPE_TERMINAL_GROUP = "terminal-group"
RESTYPE_WORKFLOW = "workflow"
RESTYPE_WORKFLOW_MODEL = "workflow-model"
SUPPORT_SCOPE_RESOURCE_TYPE = [
                               RESTYPE_DESKTOP_GROUP,
                               RESTYPE_DESKTOP_NETWORK,
                               RESTYPE_DESKTOP_IMAGE,
                               RESTYPE_USER_OU,
                               RESTYPE_DELIVERY_GROUP,
                               RESTYPE_SNAPSHOT_GROUP,
                               RESTYPE_SCHEDULER_TASK,
                               RESTYPE_POLICY_GROUP,
                               RESTYPE_CITRIX_POLICY,
                               RESTYPE_TERMINAL_GROUP
                               ]

RESOURCE_DESCRIBE_ACTION_ID = 'DescribeResource'
RESOURCE_MODIFY_ACTION_ID = 'ModifyResource'
RESOURCE_DELETE_ACTION_ID = 'DeleteResource'
ACCESS_TYPE_RESOURCE = "resource"
ACCESS_TYPE_API = "api"


SUPPORTED_RESOURCE_TYPES =[RESTYPE_DESKTOP_GROUP,
                           RESTYPE_DESKTOP,
                           RESTYPE_DESKTOP_IMAGE,
                           RESTYPE_DESKTOP_DISK,
                           RESTYPE_DESKTOP_NETWORK,
                           RESTYPE_USER,
                           RESTYPE_SNAPSHOT_GROUP,
                           RESTYPE_TERMINAL_GROUP
                           ]

SUPPORTED_MONITOR_RESOURCE_TYPES = [RESTYPE_DESKTOP,
                                    RESTYPE_DESKTOP_DISK]

RESOURCE_TYPE_TABLES = {
    RESTYPE_DESKTOP_GROUP: TB_DESKTOP_GROUP,
    RESTYPE_DESKTOP_NETWORK: TB_DESKTOP_NETWORK,
    RESTYPE_DESKTOP_IMAGE: TB_DESKTOP_IMAGE,
    RESTYPE_DESKTOP: TB_DESKTOP,
    RESTYPE_DESKTOP_DISK: TB_DESKTOP_DISK,
    RESTYPE_USER_OU: TB_DESKTOP_USER_OU,
    RESTYPE_USER: TB_DESKTOP_USER,
    RESTYPE_SCHEDULER_TASK: TB_SCHEDULER_TASK,
    RESTYPE_SNAPSHOT_GROUP: TB_SNAPSHOT_GROUP,
    RESTYPE_TERMINAL_GROUP:TB_TERMINAL_GROUP
}

NORMAL_USER_RESOURCE_TABLE = [
    TB_DESKTOP_GROUP,
    TB_DESKTOP,
    TB_DESKTOP_DISK,
    TB_DESKTOP_USER,
    TB_APPLY
]

RES_SCOPE_DELETE = 3
RES_SCOPE_UPDATE = 2
RES_SCOPE_READONLY = 1
RES_SCOPE_CREATE = 0
RES_SCOPE_LIST = [RES_SCOPE_CREATE,RES_SCOPE_READONLY,RES_SCOPE_UPDATE,RES_SCOPE_DELETE]


USER_GROUP_TABLES = {
    TB_DESKTOP_GROUP_USER: RESTYPE_DESKTOP_GROUP,
    TB_DELIVERY_GROUP_USER: RESTYPE_DELIVERY_GROUP,
    TB_APPLY_GROUP_USER: RESTYPE_APPLY_GROUP,
    TB_APPROVE_GROUP_USER: RESTYPE_APPROVE_GROUP
}


UPDATE_AUTH_USER_NAMES = {
    TB_DESKTOP_GROUP_USER: "user_id",
    TB_DESKTOP: "owner",
    TB_DESKTOP_DISK: "owner",
    TB_VDI_SYSTEM_LOG: "user_id",
    TB_DESKTOP_USER: "user_id",
    TB_ZONE_USER: "user_id",
    TB_DESKTOP_USER_GROUP_USER: "user_id",
    TB_RADIUS_USER: "user_id",
    TB_USER_LOGIN_RECORD: "user_id",
    TB_DESKTOP_LOGIN_RECORD: "user_id",
}

UPDATE_AUTH_BASE_DN = {
    TB_DESKTOP: {"dn_guid": "desktop_dn"},
    TB_ZONE_AUTH: {"object_guid": "base_dn"},
    TB_AUTH_SERVICE: {"dn_guid": "base_dn"},
    TB_RADIUS_SERVICE: {"dn_guid": "ou_dn"}
}

