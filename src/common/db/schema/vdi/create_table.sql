

CREATE TABLE desktop_group
(
   desktop_group_id varchar(50) PRIMARY KEY NOT NULL,
   desktop_group_name text,
   desktop_group_type varchar(50) NOT NULL,
   description text,
   desktop_dn text,
   dn_guid varchar(255) DEFAULT '' NOT NULL,
   desktop_count integer DEFAULT 0 NOT NULL,
   transition_status varchar(50) DEFAULT '' NOT NULL,
   status varchar(50) NOT NULL,
   desktop_image_id varchar(50) NOT NULL,
   image_name text,
   naming_rule varchar(50) DEFAULT 'default' NOT NULL,
   naming_count integer DEFAULT 0 NOT NULL,
   is_apply integer DEFAULT 0 NOT NULL,
   is_create integer DEFAULT 1 NOT NULL,
   save_disk integer DEFAULT 0 NOT NULL,
   save_desk integer DEFAULT 0 NOT NULL,
   -- iaas resource
   cpu integer NOT NULL,
   memory integer NOT NULL,
   gpu integer DEFAULT 0 NOT NULL,
   gpu_class integer DEFAULT 0 NOT NULL,
   instance_class integer DEFAULT 0 NOT NULL,
   ivshmem_enable integer DEFAULT 0 NOT NULL,
   usbredir integer DEFAULT 1 NOT NULL,
   clipboard integer DEFAULT 1 NOT NULL,
   filetransfer integer DEFAULT 1 NOT NULL,
   qxl_number integer DEFAULT 1 NOT NULL,
   place_group_id varchar(255) DEFAULT '' NOT NULL,
   cpu_model varchar(255) DEFAULT '' NOT NULL,
   cpu_topology varchar(255) DEFAULT '' NOT NULL,
   place_group_name varchar(255) DEFAULT '' NOT NULL,
   citrix_uuid varchar(255) DEFAULT '' NOT NULL,
   allocation_type varchar(255) DEFAULT '' NOT NULL,
   provision_type varchar(255) DEFAULT 'MCS' NOT NULL,
   managed_resource varchar(255) DEFAULT '' NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   status_time timestamp DEFAULT current_timestamp NOT NULL,
   owner varchar(255) NOT NULL,
   zone varchar(255) DEFAULT '' NOT NULL
);
CREATE INDEX desktop_group_desktop_image_id_index ON desktop_group (desktop_image_id);
CREATE INDEX desktop_group_status_index ON desktop_group (status);
CREATE INDEX desktop_group_create_time_index ON desktop_group (create_time);
CREATE INDEX desktop_group_desktop_group_type_index ON desktop_group (desktop_group_type);


CREATE TABLE desktop_group_disk
(
   disk_config_id varchar(50) PRIMARY KEY NOT NULL,
   disk_name text,
   desktop_group_id varchar(50) NOT NULL,
   desktop_group_name text DEFAULT '',
   disk_type integer DEFAULT 0 NOT NULL,
   size integer DEFAULT 0 NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   status_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX desktop_group_disk_disk_type_index ON desktop_group_disk (disk_type);
CREATE INDEX desktop_group_disk_desktop_group_id_index ON desktop_group_disk (desktop_group_id);
CREATE INDEX desktop_group_disk_create_time_index ON desktop_group_disk (create_time);

CREATE TABLE desktop_group_network
(
    network_config_id varchar(50) PRIMARY KEY NOT NULL,
    desktop_group_id varchar(50) NOT NULL,
    desktop_group_name text DEFAULT '',
    network_id varchar(50) NOT NULL,
    network_name text,
    network_type integer DEFAULT 1 NOT NULL,
    start_ip varchar(50) DEFAULT '' NOT NULL,
    end_ip varchar(50) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE INDEX desktop_group_network_create_time_index ON desktop_group_network (create_time);

CREATE TABLE desktop_group_user
(
   user_id varchar(50) NOT NULL,
   desktop_group_id varchar(50) NOT NULL,
   user_name text,
   real_name text,
   desktop_group_name text DEFAULT '',
   status varchar(50) DEFAULT '' NOT NULL,
   desktop_reserve integer DEFAULT 0 NOT NULL,
   need_desktop integer DEFAULT 0 NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   PRIMARY KEY(desktop_group_id, user_id)
);

CREATE INDEX desktop_group_user_status_index ON desktop_group_user (status);
CREATE INDEX desktop_group_user_create_time_index ON desktop_group_user (create_time);


CREATE TABLE desktop
(
   desktop_id varchar(50) PRIMARY KEY NOT NULL,
   instance_id varchar(50) DEFAULT '' NOT NULL,
   desktop_image_id varchar(50) DEFAULT '' NOT NULL,
   image_name text,
   description text,
   desktop_group_id varchar(50) DEFAULT '' NOT NULL,
   desktop_group_name text DEFAULT '',
   desktop_group_type varchar(50) DEFAULT '' NOT NULL,
   instance_class integer DEFAULT 0 NOT NULL,
   hostname varchar(50) DEFAULT '' NOT NULL,
   connect_status integer DEFAULT 0 NOT NULL,
   login_time timestamp,
   logout_time timestamp,
   status varchar(50) DEFAULT '' NOT NULL,
   transition_status varchar(50) DEFAULT '' NOT NULL,
   connect_time integer DEFAULT 0 NOT NULL,
   auto_login integer DEFAULT 0 NOT NULL,
   in_domain integer DEFAULT 0 NOT NULL,
   save_disk integer DEFAULT 1 NOT NULL,
   save_desk integer DEFAULT 1 NOT NULL,
   cpu integer NOT NULL,
   memory integer NOT NULL,
   gpu integer DEFAULT 0 NOT NULL,
   gpu_class integer DEFAULT 0 NOT NULL,
   desktop_mode varchar(50) DEFAULT 'maint' NOT NULL,
   ivshmem_enable integer DEFAULT 0 NOT NULL,
   usbredir integer DEFAULT 0 NOT NULL,
   clipboard integer DEFAULT 0 NOT NULL,
   filetransfer integer DEFAULT 0 NOT NULL,
   qxl_number integer DEFAULT 1 NOT NULL,
   cpu_model varchar(255) DEFAULT '' NOT NULL,
   need_monitor integer DEFAULT 0 NOT NULL,
   need_update integer DEFAULT 0 NOT NULL,
   desktop_dn text,
   dn_guid varchar(255) DEFAULT '' NOT NULL,
   no_sync integer DEFAULT 0 NOT NULL,
   assign_state integer DEFAULT 0 NOT NULL,
   reg_state integer DEFAULT 0 NOT NULL,
   delivery_group_id varchar(50) DEFAULT '' NOT NULL,
   delivery_group_name text,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   status_time timestamp DEFAULT current_timestamp NOT NULL,
   owner varchar(255) DEFAULT '' NOT NULL,
   user_name varchar(255) DEFAULT '' NOT NULL,
   zone varchar(50) DEFAULT '' NOT NULL
);
CREATE INDEX desktop_desktop_group_id_index ON desktop (desktop_group_id);
CREATE INDEX desktop_status_index ON desktop (status);
CREATE INDEX desktop_in_domain_index ON desktop (in_domain);
CREATE INDEX desktop_create_time_index ON desktop (create_time);
CREATE INDEX desktop_zone_index ON desktop (zone);
CREATE INDEX desktop_owner_index ON desktop (owner);

CREATE TABLE resource_user
(
   resource_id varchar(50) NOT NULL,
   resource_type varchar(50) DEFAULT 'desktop' NOT NULL,
   user_id varchar(255) NOT NULL,
   user_name text,
   is_sync integer DEFAULT 0 NOT NULL,
   PRIMARY KEY(resource_id, user_id)
);

CREATE TABLE desktop_disk
(
   disk_id varchar(50) PRIMARY KEY NOT NULL,
   volume_id varchar(50) DEFAULT '' NOT NULL,
   desktop_id varchar(50) DEFAULT '' NOT NULL,
   desktop_name text,
   description text,
   disk_config_id varchar(50) DEFAULT '' NOT NULL,
   disk_name varchar(50) DEFAULT '' NOT NULL,
   disk_type integer NOT NULL,
   desktop_group_id varchar(50) DEFAULT '' NOT NULL,
   desktop_group_name text DEFAULT '',

   size integer DEFAULT 0 NOT NULL,
   need_update integer DEFAULT 0 NOT NULL,
   status varchar(50) DEFAULT '' NOT NULL,
   transition_status varchar(50) DEFAULT '' NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   status_time timestamp DEFAULT current_timestamp NOT NULL,
   owner varchar(255) DEFAULT '' NOT NULL,
   user_name varchar(255) DEFAULT '' NOT NULL,
   zone varchar(50) DEFAULT '' NOT NULL
);
CREATE INDEX desktop_disk_desktop_group_disk_id_index ON desktop_disk (disk_config_id);
CREATE INDEX desktop_disk_disk_type_index ON desktop_disk (disk_type);
CREATE INDEX desktop_disk_desktop_id_index ON desktop_disk (desktop_id);
CREATE INDEX desktop_disk_zone_index ON desktop_disk (zone);
CREATE INDEX desktop_disk_owner_index ON desktop_disk (owner);

CREATE TABLE desktop_image
(
   desktop_image_id varchar(50) PRIMARY KEY NOT NULL,
   image_id varchar(50) DEFAULT '' NOT NULL,
   image_name text,
   description text,
   cpu integer DEFAULT 0 NOT NULL,
   memory integer DEFAULT 0 NOT NULL,
   instance_class integer DEFAULT 0 NOT NULL,
   base_image_id varchar(50) DEFAULT '' NOT NULL,
   image_type varchar(50) NOT NULL,
   status varchar(50) DEFAULT 'pending' NOT NULL,
   instance_id varchar(50) DEFAULT '' NOT NULL,
   network_id varchar(50) DEFAULT '' NOT NULL,
   inst_status varchar(50) DEFAULT '' NOT NULL,
   platform varchar(50) DEFAULT 'windows' NOT NULL,
   os_version varchar(50) DEFAULT '' NOT NULL,
   os_family varchar(50) DEFAULT 'windows' NOT NULL,
   ui_type varchar(50) DEFAULT 'gui' NOT NULL,
   session_type varchar(50) DEFAULT '' NOT NULL,
   image_size integer DEFAULT 50 NOT NULL,
   is_default integer DEFAULT 0 NOT NULL,
   transition_status varchar(50) DEFAULT '' NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   status_time timestamp DEFAULT current_timestamp NOT NULL,
   owner varchar(255) DEFAULT '' NOT NULL,
   zone varchar(50) DEFAULT '' NOT NULL
);
CREATE INDEX desktop_image_image_id_index ON desktop_image (image_id);
CREATE INDEX desktop_image_image_type_index ON desktop_image (image_type);
CREATE INDEX desktop_image_status_index ON desktop_image (status);
CREATE INDEX desktop_image_zone_index ON desktop_image (zone);
CREATE INDEX desktop_image_owner_index ON desktop_image (owner);

CREATE TABLE desktop_network
(
   network_id varchar(50) PRIMARY KEY NOT NULL,
   network_type integer DEFAULT 1 NOT NULL,
   router_id varchar(50) DEFAULT '' NOT NULL,
   ip_network varchar(50) NOT NULL,
   network_name text,
   description text,
   status varchar(50) NOT NULL,
   manager_ip varchar(50) DEFAULT '' NOT NULL,              -- manager ip
   dyn_ip_start varchar(50) DEFAULT '' NOT NULL, -- dynamic ip start
   dyn_ip_end varchar(50) DEFAULT '' NOT NULL,   -- dynamic ip end
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   status_time timestamp DEFAULT current_timestamp NOT NULL,
   transition_status varchar(50) DEFAULT '' NOT NULL,
   zone varchar(50) DEFAULT '' NOT NULL

);
CREATE INDEX desktop_network_router_id_index ON desktop_network (router_id);

CREATE TABLE desktop_nic
(
   nic_id varchar(50) PRIMARY KEY NOT NULL,
   nic_name text,
   instance_id varchar(50) NOT NULL,
   network_id varchar(50) NOT NULL, 
   network_name text,
   resource_id varchar(50) DEFAULT '' NOT NULL,
   resource_name text,
   ip_network varchar(50) NOT NULL,
   private_ip varchar(50) NOT NULL,
   is_occupied integer DEFAULT 0 NOT NULL,
   network_type integer DEFAULT 1 NOT NULL,
   need_update integer DEFAULT 0 NOT NULL,
   desktop_group_id varchar(50) DEFAULT '' NOT NULL,
   desktop_group_name text DEFAULT '' NOT NULL,
   network_config_id varchar(50) DEFAULT '' NOT NULL,
   status varchar(50) NOT NULL,
   transition_status varchar(50) DEFAULT '' NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   status_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE INDEX desktop_nic_desktop_group_id_index ON desktop_nic (desktop_group_id);
CREATE INDEX desktop_nic_network_config_id_index ON desktop_nic (network_config_id);
CREATE INDEX desktop_nic_resource_id_index ON desktop_nic (resource_id);
CREATE INDEX desktop_nic_network_id_index ON desktop_nic (network_id);
CREATE INDEX desktop_nic_need_update_index ON desktop_nic (need_update);

CREATE TABLE snapshot_resource
( 
    desktop_snapshot_id varchar(50) NOT NULL,
    snapshot_group_snapshot_id varchar(50) DEFAULT '' NOT NULL,
    snapshot_name text,
    snapshot_id varchar(50) DEFAULT '' NOT NULL,
    desktop_resource_id varchar(50) DEFAULT '' NOT NULL,
    resource_id varchar(50) NOT NULL,
    resource_name text,
    resource_type varchar(50) NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL,
    ymd varchar(20) DEFAULT '' NOT NULL,  -- Y-m-d, like 2019-08-01
    owner varchar(255) NOT NULL,
    zone varchar(50) DEFAULT '' NOT NULL,
    PRIMARY KEY(desktop_snapshot_id, desktop_resource_id)
);

CREATE TABLE desktop_snapshot
(
    snapshot_id varchar(50) PRIMARY KEY NOT NULL,
    desktop_snapshot_id varchar(50) DEFAULT ''  NOT NULL,
    snapshot_name text,
    description text,
    desktop_resource_id varchar(50) DEFAULT '' NOT NULL,
    resource_id varchar(50) NOT NULL,
    snapshot_type integer DEFAULT 0 NOT NULL,
    root_id varchar(50) DEFAULT '' NOT NULL,  
    parent_id varchar(50) DEFAULT 'self' NOT NULL,
    is_head integer DEFAULT 0 NOT NULL,
    head_chain integer DEFAULT 0 NOT NULL,
    raw_size bigint DEFAULT 0 NOT NULL,		
    store_size bigint DEFAULT 0 NOT NULL,		
    total_store_size bigint DEFAULT 0 NOT NULL,
    size bigint DEFAULT 0 NOT NULL,				
    total_size bigint DEFAULT 0 NOT NULL,			
    transition_status varchar(50) DEFAULT '' NOT NULL,		    
    status varchar(50) NOT NULL,							   
    status_time timestamp DEFAULT current_timestamp NOT NULL,
    snapshot_time timestamp DEFAULT current_timestamp NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    total_count integer DEFAULT 0 NOT NULL,
    owner varchar(255) NOT NULL,
    zone varchar(50) DEFAULT '' NOT NULL
);
CREATE INDEX desktop_snapshot_resource_id_index ON desktop_snapshot (resource_id);
CREATE INDEX desktop_snapshot_parent_id_index ON desktop_snapshot (parent_id);
CREATE INDEX desktop_snapshot_root_id_index ON desktop_snapshot (root_id);
CREATE INDEX desktop_snapshot_create_time_index ON desktop_snapshot (create_time);
CREATE INDEX desktop_snapshot_snapshot_time_index ON desktop_snapshot (snapshot_time);

CREATE TABLE snapshot_group
(
    snapshot_group_id varchar(50) PRIMARY KEY NOT NULL,
    snapshot_group_name text,
    description text,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    status varchar(50) DEFAULT 'normal' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    zone varchar(50) DEFAULT '' NOT NULL
);
CREATE INDEX snapshot_group_create_time_index ON snapshot_group (create_time);

CREATE TABLE snapshot_group_resource
(
    snapshot_group_id varchar(50) NOT NULL,
    desktop_resource_id varchar(50) DEFAULT '' NOT NULL,
    resource_name text,
    PRIMARY KEY(snapshot_group_id, desktop_resource_id)
);

CREATE TABLE snapshot_group_snapshot
(
    snapshot_group_snapshot_id varchar(50) PRIMARY KEY NOT NULL,
    snapshot_group_id varchar(50) DEFAULT '' NOT NULL,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    status varchar(50) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    owner varchar(255) NOT NULL,
    zone varchar(50) DEFAULT '' NOT NULL
);


CREATE TABLE resource_job
(
    job_id varchar(50) PRIMARY KEY NOT NULL,
    status varchar(50) NOT NULL,
    action varchar(50) NOT NULL,
    resource_ids text NOT NULL,
    task_count integer DEFAULT 0 NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX resource_job_status_index ON resource_job (status);
CREATE INDEX resource_job_create_time_index ON resource_job (create_time);


CREATE TABLE desktop_job
(
    job_id varchar(50) PRIMARY KEY NOT NULL,
    status varchar(50) NOT NULL,
    job_action varchar(50) NOT NULL,
    resource_ids text NOT NULL,
    directive text NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL,
    owner varchar(255) DEFAULT '' NOT NULL,
    zone varchar(50) DEFAULT '' NOT NULL
);

CREATE INDEX desktop_job_status_index ON desktop_job (status);
CREATE INDEX desktop_job_create_time_index ON desktop_job (create_time);


CREATE TABLE desktop_task
(
    task_id varchar(50) PRIMARY KEY NOT NULL,
    status varchar(50) NOT NULL,
    task_type varchar(50) NOT NULL,
    job_id varchar(50) NOT NULL,
    resource_ids text NOT NULL,
    directive text NOT NULL,
    task_level integer DEFAULT 0 NOT NULL,   
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL,
    owner varchar(255) DEFAULT '' NOT NULL,
    zone varchar(50) DEFAULT '' NOT NULL
);

CREATE INDEX desktop_task_status_index ON desktop_task (status);
CREATE INDEX desktop_task_create_time_index ON desktop_task (create_time);

CREATE TABLE scheduler_task
(
    scheduler_task_id varchar(50) PRIMARY KEY NOT NULL,
    task_name text DEFAULT '' NOT NULL,
    task_type varchar(50) NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    description text,
    resource_type varchar(50) NOT NULL,

    repeat integer NOT NULL,  -- 0: only once, 1: repeat
    period varchar(255) DEFAULT '' NOT NULL,  -- daily, weekly:1,2,5, monthly:1,7,20,-1
    ymd varchar(20) DEFAULT '' NOT NULL,  -- Y-m-d, like 2011-07-11
    hhmm varchar(10) NOT NULL, -- hh:mm, like 10:58
    term_time varchar(20) DEFAULT '' NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    execute_time timestamp,

    update_time timestamp DEFAULT current_timestamp NOT NULL,
    owner varchar(255) DEFAULT '' NOT NULL,
    zone varchar(50) DEFAULT '' NOT NULL
);

CREATE INDEX scheduler_task_status_index ON scheduler_task (status);
CREATE INDEX scheduler_task_repeat_index ON scheduler_task (repeat);

CREATE TABLE scheduler_task_resource
(
    scheduler_task_id varchar(50) NOT NULL,
    task_name text DEFAULT '' NOT NULL,
    task_type varchar(50) NOT NULL,
    resource_id varchar(50) NOT NULL,
    task_param text DEFAULT '',
    task_msg text DEFAULT '',
    job_id varchar(50) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(scheduler_task_id, resource_id)
);

CREATE TABLE scheduler_task_history
(
    scheduler_history_id varchar(50) PRIMARY KEY NOT NULL,
    scheduler_task_id varchar(50) NOT NULL,
    task_name text,
    history_type integer DEFAULT 0 NOT NULL,
    task_msg text,
    create_time timestamp DEFAULT current_timestamp NOT NULL
);


CREATE TABLE desktop_version
(
   version_id varchar(50) PRIMARY KEY NOT NULL,
   version varchar(50) NOT NULL,
   description text,
   sequence integer DEFAULT 0 NOT NULL,
   curr_version integer DEFAULT 0 NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX desktop_version_version_index ON desktop_version (version);
CREATE INDEX desktop_version_create_time_index ON desktop_version (create_time);

CREATE TABLE vdi_system_config
(
   config_key varchar(255) PRIMARY KEY NOT NULL,
   config_value varchar(255) DEFAULT '' NOT NULL
);
CREATE INDEX vdi_system_config_key ON vdi_system_config(config_key);

CREATE TABLE vdi_system_log
(
   system_log_id varchar(50) PRIMARY KEY NOT NULL,
   user_id varchar(50) NOT NULL,
   user_name varchar(50) NOT NULL,
   user_role varchar(50) NOT NULL,
   action_name varchar(50) DEFAULT '' NOT NULL,
   log_info text,
   req_params text,
   log_type varchar(50) NOT NULL,
   req_time timestamp DEFAULT current_timestamp NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX vdi_system_log_system_log_id_index ON vdi_system_log (system_log_id);
CREATE INDEX vdi_system_log_user_id_index ON vdi_system_log (user_id);
CREATE INDEX vdi_system_log_user_name_index ON vdi_system_log (user_name);
CREATE INDEX vdi_system_log_user_role_index ON vdi_system_log (user_role);
CREATE INDEX vdi_system_log_log_type_index ON vdi_system_log (log_type);
CREATE INDEX vdi_system_log_action_name_index ON vdi_system_log (action_name);

CREATE TABLE desktop_user
(
   user_id varchar(255) PRIMARY KEY NOT NULL,
   auth_service_id varchar(255) DEFAULT '' NOT NULL,
   user_name varchar(255) NOT NULL,
   role varchar(255) DEFAULT '' NOT NULL,
   email varchar(255) DEFAULT '' NOT NULL,
   personal_phone varchar(255) DEFAULT '' NOT NULL,
   object_guid varchar(255) DEFAULT '' NOT NULL,
   real_name varchar(255) DEFAULT '' NOT NULL,
   description text DEFAULT '',
   password varchar(255) DEFAULT '' NOT NULL,
   ou_dn varchar(255) DEFAULT '' NOT NULL,
   user_dn varchar(255) DEFAULT '',
   status varchar(50) DEFAULT 'active' NOT NULL,
   user_control integer DEFAULT 546 NOT NULL,
   reset_password integer DEFAULT 0 NOT NULL,
   password_protect integer DEFAULT 0 NOT NULL,
   security_question integer DEFAULT 0 NOT NULL,
   last_zone varchar(255) DEFAULT '' NOT NULL,
   default_zone varchar(255) DEFAULT '' NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   update_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX desktop_user_user_name_index ON desktop_user (user_name);
CREATE INDEX desktop_user_user_dn_index ON desktop_user (user_dn);
CREATE INDEX desktop_user_reset_password_index ON desktop_user (reset_password);
CREATE INDEX desktop_user_password_protect_index ON desktop_user (password_protect);
CREATE INDEX desktop_user_security_question_index ON desktop_user (security_question);
CREATE INDEX desktop_user_create_time_index ON desktop_user (create_time);

CREATE TABLE zone_user
(
    user_id varchar(255) NOT NULL,                       -- the user_id
    zone_id varchar(50) NOT NULL,                        -- the zone_id
    user_name varchar(255) NOT NULL,
    role varchar(50) DEFAULT 'normal' NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    update_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(user_id, zone_id)
);
CREATE INDEX zone_user_zone_id_index ON zone_user (zone_id);
CREATE INDEX zone_user_user_id_index ON zone_user (user_id);
CREATE INDEX zone_user_create_time_index ON zone_user (create_time);

CREATE TABLE desktop_user_ou
(
   user_ou_id varchar(255) PRIMARY KEY NOT NULL,
   auth_service_id varchar(255) NOT NULL,
   ou_name varchar(255) NOT NULL,
   object_guid varchar(255) DEFAULT '' NOT NULL,
   ou_dn varchar(255) DEFAULT '',
   base_dn varchar(255) DEFAULT '',
   description text DEFAULT '',
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   update_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE desktop_user_group
(
   user_group_id varchar(255) PRIMARY KEY NOT NULL,
   auth_service_id varchar(255) DEFAULT '' NOT NULL,
   user_group_name varchar(255) NOT NULL,
   object_guid varchar(255) DEFAULT '' NOT NULL,
   description text DEFAULT '',
   user_group_dn varchar(255) DEFAULT '',
   base_dn varchar(255) DEFAULT '',
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   update_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX desktop_user_group_user_group_id_index ON desktop_user_group (user_group_id);
CREATE INDEX desktop_user_group_auth_service_id_index ON desktop_user_group (auth_service_id);
CREATE INDEX desktop_user_group_create_time_index ON desktop_user_group (create_time);
CREATE INDEX desktop_user_group_update_time_index ON desktop_user_group (update_time);

CREATE TABLE desktop_user_group_user
(
   user_group_id varchar(255) NOT NULL,
   user_id varchar(255) NOT NULL,
   user_name varchar(255) DEFAULT '' NOT NULL,
   PRIMARY KEY(user_group_id, user_id)
);


CREATE TABLE zone_user_group
(
    user_group_id varchar(255) NOT NULL,                 -- the user_id
    zone_id varchar(50) NOT NULL,                        -- the zone_id
    PRIMARY KEY(user_group_id, zone_id)
);


CREATE TABLE zone_user_scope
(
   user_id varchar(255) NOT NULL,
   resource_type varchar(255) NOT NULL,
   resource_id varchar(255) DEFAULT '',
   action_type integer DEFAULT 1 NOT NULL,
   zone_id varchar(50) NOT NULL,
   PRIMARY KEY(user_id, resource_type, resource_id, action_type, zone_id)
);
CREATE INDEX zone_user_scope_user_id_index ON zone_user_scope (user_id);
CREATE INDEX zone_user_scope_resource_type_index ON zone_user_scope (resource_type);
CREATE INDEX zone_user_scope_id_type_index ON zone_user_scope (resource_id);
CREATE INDEX zone_user_scope_action_type_index ON zone_user_scope (action_type);
CREATE INDEX zone_user_scope_zone_id_index ON zone_user_scope (zone_id);


CREATE TABLE zone_user_scope_action
(
   action_id varchar(255) NOT NULL,
   action_name varchar(255) DEFAULT '' NOT NULL,
   action_api varchar(255) NOT NULL,
   PRIMARY KEY(action_id, action_api)
);
CREATE INDEX zone_user_scope_action_action_id_index ON zone_user_scope_action (action_id);

CREATE TABLE vdi_desktop_message
(
   message_id varchar(255) PRIMARY KEY NOT NULL,
   desktop_id text,
   message text,
   create_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX vdi_desktop_message_message_id_index ON vdi_desktop_message (message_id);


CREATE TABLE delivery_group
(
   delivery_group_id varchar(255) PRIMARY KEY NOT NULL,
   delivery_group_name varchar(255) NOT NULL,
   delivery_group_type varchar(255) NOT NULL,
   delivery_group_uid varchar(50) DEFAULT '' NOT NULL,
   desktop_kind varchar(255) DEFAULT 'Private' NOT NULL,
   allocation_type varchar(255) DEFAULT 'Static' NOT NULL,
   delivery_type varchar(255) DEFAULT 'DesktopsOnly' NOT NULL,
   desktop_hide_mode integer DEFAULT 0 NOT NULL, 
   assign_name varchar(255) DEFAULT '' NOT NULL,
   description text,
   mode varchar(50) DEFAULT 'maint' NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   zone varchar(255) DEFAULT '' NOT NULL
);

CREATE INDEX delivery_group_delivery_group_name_index ON delivery_group (delivery_group_name);

CREATE TABLE delivery_group_user
(
   user_id varchar(50) NOT NULL,
   delivery_group_id varchar(50) DEFAULT '' NOT NULL,
   user_name varchar(255) DEFAULT '' NOT NULL,
   user_type varchar(50) DEFAULT 'user' NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   PRIMARY KEY(delivery_group_id, user_id)
);

CREATE INDEX delivery_group_user_create_time_index ON delivery_group_user (create_time);

CREATE TABLE policy_group
(
    policy_group_id varchar(50) PRIMARY KEY NOT NULL,
    policy_group_name text,
    policy_group_type varchar(50) NOT NULL,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    description text DEFAULT '',
    is_default integer DEFAULT 0 NOT NULL,
    is_apply integer DEFAULT 0 NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    zone varchar(255) DEFAULT '' NOT NULL
);
CREATE INDEX policy_group_policy_group_type_index ON policy_group (policy_group_type);

CREATE TABLE policy_group_resource
(
    policy_group_id varchar(50) NOT NULL,
    resource_id varchar(50) NOT NULL,
    policy_group_type varchar(50) DEFAULT 'security' NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    is_apply integer DEFAULT 0 NOT NULL,
    is_lock integer DEFAULT 0 NOT NULL,
    PRIMARY KEY(policy_group_id, resource_id)
);
CREATE INDEX policy_group_resource_resource_id_index ON policy_group_resource (resource_id);

CREATE TABLE policy_group_policy
(
    policy_group_id varchar(50) NOT NULL,
    policy_id varchar(50) NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    is_base integer DEFAULT 0 NOT NULL,
    slave_policy_id varchar(50) DEFAULT '' NOT NULL,
    PRIMARY KEY(policy_group_id, policy_id)
);
CREATE INDEX policy_group_policy_status_index ON policy_group_policy (status);

CREATE TABLE policy_resource_group
(
    policy_group_id varchar(50) NOT NULL,
    resource_group_id varchar(50) NOT NULL,
    resource_group_type varchar(255) NOT NULL,
    policy_group_type varchar(50) NOT NULL,
    PRIMARY KEY(policy_group_id, resource_group_id)
);

CREATE TABLE security_policy
(
    security_policy_id varchar(50) PRIMARY KEY NOT NULL,
    security_policy_name text DEFAULT '' NOT NULL,
    security_policy_type varchar(50) DEFAULT 'sgrs' NOT NULL,
    description text,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    policy_mode varchar(50) DEFAULT 'master' NOT NULL,
    share_policy_id varchar(50) DEFAULT '' NOT NULL,
    need_sync integer DEFAULT 0 NOT NULL,

    status varchar(50) DEFAULT 'active' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL,
    is_apply integer DEFAULT 0 NOT NULL,
    is_default integer DEFAULT 0 NOT NULL,
    zone varchar(255) DEFAULT '' NOT NULL
);
CREATE INDEX security_policy_create_time_index ON security_policy (create_time);

CREATE TABLE security_rule
(
    security_rule_id varchar(50) PRIMARY KEY NOT NULL, -- security group rule id
    security_rule_name text DEFAULT '' NOT NULL,		-- security group rule name
    security_policy_id varchar(50) NOT NULL,		    		-- security group id
    security_policy_name text,
    
    security_rule_type varchar(50) DEFAULT 'normal' NOT NULL,
    share_rule_id varchar(50) DEFAULT '' NOT NULL,
    need_sync integer DEFAULT 0 NOT NULL,

    protocol varchar(50) NOT NULL,                  -- "tcp/udp/icmp/gre/<protocol_number>"
    direction integer DEFAULT 0 NOT NULL,         	-- 0 for inbound; 1 for outbound
    val1 varchar(50) DEFAULT '' NOT NULL,         	-- if protocol is tcp/udp, this is starting port; for icmp, this is icmp type; 
                                                        -- (it could be security_group_ipset id)
    val2 varchar(50) DEFAULT '' NOT NULL,         	-- if protocol is tcp/udp, this is ending port; for icmp, this is icmp code
    val3 varchar(50) DEFAULT '' NOT NULL,         	-- if protocol is tcp/udp, this is source ip: <ip> for one ip address or <ip>/<cidr mask> for a range of addresses. 
                                                        -- (it could be security_group_ipset id)
    val4 varchar(50) DEFAULT '' NOT NULL, 
    priority integer NOT NULL,                  	-- rule priority, range is [0 - 100]
    action varchar(16) DEFAULT 'accept' NOT NULL,   -- 'accept' to accept packets if matched; 'drop' to drop packets if matched
    disabled integer DEFAULT 0 NOT NULL,             -- 0 for enabled, 1 for disabled.
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    zone varchar(255) DEFAULT '' NOT NULL
);
CREATE INDEX security_rule_security_policy_id_index ON security_rule (security_policy_id);

CREATE TABLE security_ipset
(
    security_ipset_id varchar(50) PRIMARY KEY NOT NULL,    -- security group ipset id
    security_ipset_name text DEFAULT '' NOT NULL,	        -- security group ipset name
    description text DEFAULT '' NOT NULL,										-- security group ipset description
    transition_status varchar(50) DEFAULT '' NOT NULL,
    is_default integer DEFAULT 0 NOT NULL,
    ipset_config_key varchar(50) DEFAULT '' NOT NULL,
    ipset_type integer DEFAULT 0 NOT NULL,        -- ipset type: 0 for hash:ip; 1 for bitmap:port 
    val text DEFAULT '' NOT NULL,	                -- value, if type is 0, this is comma separated ip or ip/cidr or fromip-toip
                                                        --        if type is 1, this is comma separated port or <start>-<end> port
    is_apply integer DEFAULT 0 NOT NULL,                  -- whether the ipset changes is applied to sg.
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    zone varchar(255) DEFAULT '' NOT NULL
);

/* vdagent_server table */
CREATE TABLE vdagent_job
(
    job_id varchar(50) PRIMARY KEY NOT NULL,
    status varchar(50) NOT NULL,
    job_action varchar(50) NOT NULL,
    resource_id varchar(50) NOT NULL,
    directive text NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX vdagent_job_id_index ON vdagent_job (job_id);
CREATE INDEX vdagent_job_status_index ON vdagent_job (status);
CREATE INDEX vdagent_job_create_time_index ON vdagent_job (create_time);

/* vdhost_server table */
CREATE TABLE vdhost_job
(
    job_id varchar(50) PRIMARY KEY NOT NULL,
    status varchar(50) NOT NULL,
    job_action varchar(50) NOT NULL,
    resource_id varchar(50) NOT NULL,
    directive text NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX vdhost_job_id_index ON vdhost_job (job_id);
CREATE INDEX vdhost_job_status_index ON vdhost_job (status);
CREATE INDEX vdhost_job_create_time_index ON vdhost_job (create_time);

CREATE TABLE guest
(
    hostname varchar(50) PRIMARY KEY NOT NULL,
    desktop_id varchar(50) DEFAULT '',
    login_user varchar(50) DEFAULT '',
    client_ip varchar(50) DEFAULT '',
    session_uid varchar(50) DEFAULT '',
    connect_status integer DEFAULT 0 NOT NULL,
    connect_time timestamp DEFAULT current_timestamp NOT NULL,
    disconnect_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX guest_desktop_id_index ON guest (desktop_id);
CREATE INDEX guest_hostname_index ON guest (hostname);
CREATE INDEX guest_session_uid_index ON guest (session_uid);
CREATE INDEX guest_connect_status_index ON guest (connect_status);
CREATE INDEX guest_connect_time_index ON guest (connect_time);
CREATE INDEX guest_disconnect_time_index ON guest (disconnect_time);

CREATE TABLE usb_policy
(
    usb_policy_id varchar(50) PRIMARY KEY NOT NULL,
    object_id varchar(50) NOT NULL,
    policy_type varchar(50) NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    class_id varchar(50) NOT NULL,
    vendor_id varchar(50) NOT NULL,
    product_id varchar(50) NOT NULL,
    version_id varchar(50) NOT NULL,
    allow integer DEFAULT 0 NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    update_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX object_id_index ON usb_policy (object_id);

CREATE TABLE apply
(
   apply_id varchar(50) PRIMARY KEY NOT NULL,
   apply_type varchar(50) DEFAULT '' NOT NULL,
   apply_title varchar(255) DEFAULT '' NOT NULL,
   apply_description text DEFAULT '',
   status varchar(50) DEFAULT '' NOT NULL,
   approve_status varchar(50) DEFAULT '' NOT NULL,
   apply_group_id varchar(50) DEFAULT '' NOT NULL,
   approve_group_id varchar(50) DEFAULT '' NOT NULL,
   apply_user_id varchar(50) DEFAULT '' NOT NULL,
   apply_resource_type varchar(50) DEFAULT '' NOT NULL,
   apply_parameter varchar(2048) DEFAULT '' NOT NULL,
   approve_parameter varchar(2048) DEFAULT '' NOT NULL,
   approve_user_id varchar(50) DEFAULT '' NOT NULL,
   approve_advice varchar(255) DEFAULT '' NOT NULL,
   resource_group_id varchar(50) DEFAULT '' NOT NULL,
   resource_id varchar(50) DEFAULT '' NOT NULL,
   apply_age integer DEFAULT -1,
   start_time timestamp DEFAULT current_timestamp NOT NULL,
   end_time timestamp DEFAULT current_timestamp NOT NULL,
   zone_id varchar(50) NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   update_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX apply_apply_id_index ON apply (apply_id);
CREATE INDEX apply_apply_type_index ON apply (apply_type);
CREATE INDEX apply_status_index ON apply (status);
CREATE INDEX apply_user_id_index ON apply (apply_user_id);
CREATE INDEX apply_resource_id_index ON apply (resource_id);
CREATE INDEX apply_approve_user_id_index ON apply (approve_user_id);
CREATE INDEX apply_start_time_index ON apply (start_time);
CREATE INDEX apply_end_time_index ON apply (end_time);
CREATE INDEX apply_zone_id_index ON apply (zone_id);
CREATE INDEX apply_create_time_index ON apply (create_time);
CREATE INDEX apply_update_time_index ON apply (update_time);

CREATE TABLE apply_group
(
    apply_group_id varchar(50) PRIMARY KEY NOT NULL,
    apply_group_name varchar(256) DEFAULT '' NOT NULL,
    description text DEFAULT '',
    zone_id varchar(50) NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    update_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX apply_group_apply_group_name_index ON apply_group (apply_group_name);
CREATE INDEX apply_group_zone_id_index ON apply_group (zone_id);
CREATE INDEX apply_group_create_time_index ON apply_group (create_time);
CREATE INDEX apply_group_update_time_index ON apply_group (update_time);

CREATE TABLE apply_group_user
(
    user_id varchar(50) NOT NULL,
    apply_group_id varchar(50) NOT NULL,
    user_type varchar(50) DEFAULT 'user' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(user_id, apply_group_id)
);
CREATE INDEX apply_group_user_user_id_index ON apply_group_user (user_id);
CREATE INDEX apply_group_user_apply_group_id_index ON apply_group_user (apply_group_id);

CREATE TABLE apply_group_resource
(
    resource_id varchar(50)  NOT NULL,
    apply_group_id varchar(50) NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(resource_id, apply_group_id)
);
CREATE INDEX apply_group_resource_resource_id_index ON apply_group_resource (resource_id);
CREATE INDEX apply_group_resource_apply_group_id_index ON apply_group_resource (apply_group_id);

CREATE TABLE approve_group
(
    approve_group_id varchar(50) PRIMARY KEY NOT NULL,
    approve_group_name varchar(256) DEFAULT '' NOT NULL,
    description text DEFAULT '',
    zone_id varchar(50) NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    update_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX approve_group_approve_group_name_index ON approve_group (approve_group_name);
CREATE INDEX approve_group_zone_id_index ON approve_group (zone_id);
CREATE INDEX approve_group_create_time_index ON approve_group (create_time);
CREATE INDEX approve_group_update_time_index ON approve_group (update_time);

CREATE TABLE approve_group_user
(
    user_id varchar(50) NOT NULL,
    approve_group_id varchar(50) NOT NULL,
    user_type varchar(50) DEFAULT 'user' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(user_id, approve_group_id)
);
CREATE INDEX approve_group_user_user_id_index ON approve_group_user (user_id);
CREATE INDEX approve_group_user_approve_group_id_index ON approve_group_user (approve_group_id);

CREATE TABLE apply_approve_group_map
(
    apply_group_id varchar(50)  NOT NULL,
    approve_group_id varchar(50) NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(apply_group_id, approve_group_id)
);
CREATE INDEX apply_approve_group_map_apply_group_id_index ON apply_approve_group_map (apply_group_id);
CREATE INDEX apply_approve_group_map_approve_group_id_index ON apply_approve_group_map (approve_group_id);
CREATE INDEX apply_approve_group_map_create_time_index ON apply_approve_group_map (create_time);

CREATE TABLE component_version
(
    component_id varchar(50) PRIMARY KEY NOT NULL,
    component_name varchar(50) NOT NULL,
    component_type varchar(50) NOT NULL,
    version varchar(50) NOT NULL,
    filename varchar(256) NOT NULL,
    description varchar(256) NOT NULL,
    upgrade_packet_md5 varchar(256) DEFAULT '' NOT NULL,
    upgrade_packet_size integer DEFAULT 0 NOT NULL,
    status varchar(50) DEFAULT 'normal' NOT NULL,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    component_version_log text DEFAULT '',
    component_version_log_history text DEFAULT '',
    need_upgrade integer DEFAULT 0 NOT NULL,
    update_time timestamp DEFAULT current_timestamp NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX component_version_component_name_index ON component_version (component_id);

-- desktop zone table
CREATE TABLE desktop_zone
(
    zone_id varchar(50) PRIMARY KEY NOT NULL,
    zone_name varchar(50) DEFAULT '' NOT NULL,
    platform varchar(50) NOT NULL,
    status varchar(50) NOT NULL,
    visibility varchar(50) DEFAULT '' NOT NULL,
    
    description text,
    zone_deploy varchar(50) DEFAULT 'standard' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX desktop_zone_status_index ON desktop_zone (status);
CREATE INDEX desktop_zone_platform_index ON desktop_zone (platform);
CREATE INDEX desktop_zone_visibility_index ON desktop_zone (visibility);

-- user_zone table

CREATE TABLE zone_connection
(
    zone_id varchar(50) PRIMARY KEY NOT NULL,
    base_zone_id varchar(255) NOT NULL,
    base_zone_name varchar(50) DEFAULT '' NOT NULL,
    account_user_id varchar(255) NOT NULL,
    account_user_name varchar(255) DEFAULT '' NOT NULL,
    access_key_id varchar(50) NOT NULL,
    secret_access_key varchar(255) NOT NULL,
    host_ip varchar(255) DEFAULT '' NOT NULL,
    host varchar(255) NOT NULL,
    port integer DEFAULT 80 NOT NULL, 
    protocol varchar(50) DEFAULT 'http' NOT NULL,
    http_socket_timeout integer DEFAULT 120 NOT NULL, 
    status varchar(50) DEFAULT 'active' NOT NULL,
    keypair varchar(50) DEFAULT '' NOT NULL
);

CREATE INDEX zone_connection_base_zone_id_index ON zone_connection (base_zone_id);
CREATE INDEX zone_connection_account_user_id_index ON zone_connection (account_user_id);
CREATE INDEX zone_connection_account_keypair_index ON zone_connection (keypair);


CREATE TABLE zone_citrix_connection
(
    zone_id varchar(50) PRIMARY KEY NOT NULL,
    host varchar(255) DEFAULT '' NOT NULL,
    port integer DEFAULT 10080 NOT NULL, 
    protocol varchar(50) DEFAULT 'http' NOT NULL,
    http_socket_timeout integer DEFAULT 120 NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    managed_resource varchar(255) DEFAULT '' NOT NULL,
    storefront_uri varchar(1000) DEFAULT '' NOT NULL,
    storefront_port integer DEFAULT 80 NOT NULL,
    support_netscaler integer DEFAULT 0 NOT NULL,
    support_citrix_pms integer DEFAULT 0 NOT NULL,
    netscaler_port integer DEFAULT 443 NOT NULL,
    netscaler_uri varchar(1000) DEFAULT '' NOT NULL
);

CREATE TABLE zone_resource_limit
(
    zone_id varchar(50) PRIMARY KEY NOT NULL,
    instance_class varchar(255) NOT NULL,
    disk_size varchar(255) NOT NULL,
    cpu_cores text,
    memory_size text,
    cpu_memory_pairs text,
    supported_gpu integer DEFAULT 0 NOT NULL,
    place_group varchar(255) DEFAULT '' NOT NULL,
    max_disk_count integer DEFAULT 2 NOT NULL,
    default_passwd varchar(255) DEFAULT 'Desktop123' NOT NULL,
    network_type text,
    router varchar(255) DEFAULT '' NOT NULL,
    ivshmem varchar(50) DEFAULT '' NOT NULL,
    max_snapshot_count integer DEFAULT 7 NOT NULL,
    max_chain_count integer DEFAULT 2 NOT NULL,
    gpu_class_key varchar(255) DEFAULT '' NOT NULL,
    max_gpu_count integer DEFAULT 2 NOT NULL
);

CREATE TABLE zone_auth
(
    zone_id varchar(50) PRIMARY KEY NOT NULL,
    auth_service_id varchar(50) NOT NULL,
    base_dn text DEFAULT '' NOT NULL,
    object_guid varchar(255) DEFAULT '' NOT NULL
);

CREATE TABLE auth_service
(
    auth_service_id varchar(50) PRIMARY KEY NOT NULL,
    auth_service_name text,
    description text,
    auth_service_type varchar(50) DEFAULT 'ad' NOT NULL,
    admin_name varchar(50) NOT NULL,
    admin_password varchar(255) NOT NULL,
    base_dn varchar(255) DEFAULT '' NOT NULL,
    dn_guid varchar(255) DEFAULT '' NOT NULL,
    domain varchar(255) NOT NULL,
    host varchar(255) DEFAULT '' NOT NULL,
    secondary_host varchar(255) DEFAULT '' NOT NULL,
    port integer DEFAULT 80 NOT NULL,
    secret_port integer DEFAULT 80 NOT NULL,
    is_sync integer DEFAULT 0 NOT NULL,
    modify_password integer DEFAULT 0 NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE radius_service
(
    radius_service_id varchar(50) PRIMARY KEY NOT NULL,
    radius_service_name text,
    description text,
    host varchar(255) DEFAULT '' NOT NULL,
    port integer DEFAULT 80 NOT NULL,
    acct_session varchar(255) DEFAULT '' NOT NULL,
    identifier varchar(255) DEFAULT '' NOT NULL,
    secret varchar(255) DEFAULT '' NOT NULL,
    rule_type varchar(50) DEFAULT '' NOT NULL,
    enable_radius integer DEFAULT 0 NOT NULL,
    auth_service_id varchar(50) DEFAULT '' NOT NULL,
    ou_dn text,
    dn_guid varchar(255) DEFAULT '' NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE radius_user
(
    radius_service_id varchar(50) NOT NULL,
    user_id varchar(50) NOT NULL,
    user_name text,
    user_type varchar(50) DEFAULT 'user' NOT NULL,
    check_radius integer DEFAULT 0 NOT NULL,
    PRIMARY KEY(radius_service_id, user_id)
);

CREATE TABLE notice_push
(
    notice_id varchar(50) PRIMARY KEY NOT NULL,
    notice_type varchar(50) DEFAULT '' NOT NULL,
    notice_level varchar(50) DEFAULT '' NOT NULL,
    status varchar(50) NOT NULL,
    title varchar(255) NOT NULL,
    content text,
    scope varchar(50) DEFAULT 'public' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    expired_time timestamp,
    execute_time timestamp,
    force_read integer DEFAULT 0 NOT NULL,
    owner varchar(255) NOT NULL
);

CREATE TABLE notice_zone
(
    notice_id varchar(50) NOT NULL,
    zone_id varchar(50) NOT NULL,
    user_scope varchar(50) DEFAULT 'public' NOT NULL,
    PRIMARY KEY(notice_id, zone_id)
);

CREATE TABLE notice_user
(
    notice_id varchar(50) NOT NULL,
    user_id varchar(255) NOT NULL, 
    zone_id varchar(50) NOT NULL,
    user_type varchar(255) DEFAULT 'user' NOT NULL,
    PRIMARY KEY(notice_id, user_id, zone_id)
);

CREATE TABLE notice_read
(
    notice_id varchar(50) NOT NULL,
    user_id varchar(50) NOT NULL,
    user_name text,
    PRIMARY KEY(notice_id, user_id)
);


CREATE TABLE prompt_question
(
    prompt_question_id varchar(50) NOT NULL,
    question_content varchar(1024) NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(prompt_question_id)
);

CREATE INDEX prompt_question_create_time_index ON prompt_question (create_time);

CREATE TABLE prompt_answer
(
    prompt_answer_id varchar(50) NOT NULL,
    prompt_question_id varchar(50) NOT NULL,
    question_content varchar(1024) NOT NULL,
    user_id varchar(255) NOT NULL,
    answer_content varchar(1024) NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(prompt_answer_id)
);
CREATE INDEX prompt_answer_prompt_question_id_index ON prompt_answer (prompt_question_id);
CREATE INDEX prompt_answer_user_id_index ON prompt_answer (user_id);
CREATE INDEX prompt_answer_create_time_index ON prompt_answer (create_time);

CREATE TABLE syslog_server
(
    syslog_server_id varchar(50) PRIMARY KEY NOT NULL,
    host varchar(100) DEFAULT '' NOT NULL,
    port integer DEFAULT 0 NOT NULL,
    protocol varchar(50) NOT NULL,
    runtime varchar(50) UNIQUE NOT NULL,
    status varchar(50) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX syslog_server_status_index ON syslog_server (status);
CREATE INDEX syslog_server_host_index ON syslog_server (host);
CREATE INDEX syslog_server_runtime_index ON syslog_server (runtime);

CREATE TABLE user_login_record
(
    user_login_record_id varchar(50) PRIMARY KEY NOT NULL,
    user_id varchar(50) NOT NULL,
    user_name varchar(50) DEFAULT '' NOT NULL,
    zone_id varchar(50) NOT NULL,
    client_ip varchar(50) DEFAULT '' NOT NULL,
    status varchar(50) DEFAULT '' NOT NULL,
    errmsg varchar(256) DEFAULT '',
    create_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX user_login_record_create_time_index ON user_login_record (create_time);

CREATE TABLE desktop_login_record
(
    desktop_login_record_id varchar(50) PRIMARY KEY NOT NULL,
    desktop_id varchar(50) DEFAULT '',
    user_id varchar(50) DEFAULT '',
    user_name varchar(50) DEFAULT '',
    client_ip varchar(50) DEFAULT '',
    zone_id varchar(50) NOT NULL,
    session_uid varchar(50) DEFAULT '',
    connect_status integer DEFAULT 0 NOT NULL,
    connect_time timestamp DEFAULT current_timestamp NOT NULL,
    disconnect_time timestamp
);
CREATE INDEX desktop_login_record_desktop_id_index ON desktop_login_record (desktop_id);
CREATE INDEX desktop_login_record_user_id_index ON desktop_login_record (user_id);
CREATE INDEX desktop_login_record_user_name_index ON desktop_login_record (user_name);
CREATE INDEX desktop_login_record_zone_id_index ON desktop_login_record (zone_id);
CREATE INDEX desktop_login_record_connect_status_index ON desktop_login_record (connect_status);

CREATE TABLE software_info
(
  software_id varchar(50) PRIMARY KEY NOT NULL,
  software_name varchar(256) DEFAULT '' NOT NULL,
  software_size integer DEFAULT 0 NOT NULL,
  transition_status varchar(50) DEFAULT '' NOT NULL,
  zone_id varchar(50) NOT NULL,
  create_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE terminal_management
(
  terminal_id varchar(50) PRIMARY KEY NOT NULL,
  terminal_group_id varchar(50) DEFAULT '' NOT NULL,
  terminal_serial_number varchar(256) DEFAULT '' NOT NULL,
  status varchar(50) DEFAULT 'active' NOT NULL,
  login_user_name varchar(255) DEFAULT '' NOT NULL,
  terminal_ip varchar(256) DEFAULT '' NOT NULL,
  terminal_mac varchar(256) DEFAULT '' NOT NULL,
  terminal_type varchar(256) DEFAULT '' NOT NULL,
  terminal_version_number varchar(256) DEFAULT '' NOT NULL,
  login_hostname varchar(50) DEFAULT '' NOT NULL,
  connection_disconnection_time  timestamp DEFAULT current_timestamp NOT NULL,
  create_time timestamp DEFAULT current_timestamp NOT NULL,
  zone_id varchar(50) NOT NULL,
  terminal_server_ip varchar(256) DEFAULT '' NOT NULL
);

CREATE TABLE terminal_group
(
  terminal_group_id varchar(50) PRIMARY KEY NOT NULL,
  terminal_group_name varchar(256) DEFAULT '' NOT NULL,
  description text,
  create_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE terminal_group_terminal
(
    terminal_group_id varchar(50) NOT NULL,
    terminal_id varchar(50) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(terminal_group_id, terminal_id)
);

CREATE TABLE module_custom
(
    module_custom_id varchar(50) PRIMARY KEY NOT NULL,
    is_default integer DEFAULT 0 NOT NULL, -- 0 for default custom, 1 for User defined custom.
    custom_name varchar(255) DEFAULT '' NOT NULL,
    description varchar(255) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE module_custom_zone
(
    module_custom_id varchar(50) NOT NULL,
    zone_id varchar(50) NOT NULL,
    user_scope varchar(50) DEFAULT 'part_admin_roles' NOT NULL,
    PRIMARY KEY(module_custom_id, zone_id)
);

CREATE TABLE module_custom_user
(
    module_custom_id varchar(50) NOT NULL,
    user_id varchar(255) NOT NULL,
    zone_id varchar(50) NOT NULL,
    user_type varchar(255) DEFAULT 'user' NOT NULL,
    PRIMARY KEY(module_custom_id, user_id, zone_id)
);

CREATE TABLE module_custom_config
(
    module_custom_id varchar(50) NOT NULL,
    module_type varchar(50) DEFAULT '' NOT NULL,
    item_key varchar(255) DEFAULT '' NOT NULL,
    item_value text,  -- need value if the key has value or not need.
    enable_module integer DEFAULT 0 NOT NULL,   -- 0 for disabled, 1 for enabled.
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(module_custom_id,module_type,item_key)
);

CREATE TABLE module_type
(
    item_key varchar(50) PRIMARY KEY NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    enable_module integer DEFAULT 0 NOT NULL   -- 0 for disabled, 1 for enabled.
);

CREATE TABLE system_custom
(
    system_custom_id varchar(50) PRIMARY KEY NOT NULL,
    is_default integer DEFAULT 0 NOT NULL, -- 1 for default system_custom, 0 for User defined system_custom.
    current_system_custom integer DEFAULT 0 NOT NULL,-- 1 for is current_system_custom, 0 for is not current_system_custom.
    create_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE system_custom_config
(
    system_custom_id varchar(50) NOT NULL,
    module_type varchar(50) DEFAULT '' NOT NULL,
    item_key varchar(255) DEFAULT '' NOT NULL,
    item_value text,  -- need value if the key has value or not need.
    enable_module integer DEFAULT 0 NOT NULL,   -- 0 for disabled, 1 for enabled.
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(system_custom_id,module_type,item_key)
);

CREATE TABLE desktop_service_management
(
    service_node_id varchar(50) NOT NULL,
    service_id varchar(50) DEFAULT '' NOT NULL,
    service_name varchar(255) DEFAULT '' NOT NULL,
    description varchar(255) DEFAULT '' NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    service_version varchar(255) DEFAULT '' NOT NULL,
    service_ip varchar(255) DEFAULT '' NOT NULL,
    service_node_status varchar(50) DEFAULT 'active' NOT NULL,
    service_node_ip varchar(255) DEFAULT '' NOT NULL,
    service_node_name varchar(255) DEFAULT '' NOT NULL,
    service_node_version varchar(255) DEFAULT '' NOT NULL,
    service_node_type varchar(50) DEFAULT '' NOT NULL,
    service_port integer DEFAULT 80 NOT NULL,
    service_type varchar(50) DEFAULT '' NOT NULL,
    service_management_type varchar(50) DEFAULT 'desktop' NOT NULL, -- desktop for desktop_service_management, citrix for citrix service management.
    zone_id varchar(50) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(service_node_id,service_id)
);

CREATE TABLE workflow_service
(
    service_type varchar(50) PRIMARY KEY NOT NULL,
    service_name varchar(255)  NOT NULL,
    description text
);

CREATE TABLE workflow_service_action
(
    service_type varchar(50) NOT NULL,
    api_action varchar(255) NOT NULL,
    action_name text,
    priority integer DEFAULT 0 NOT NULL,
    is_head integer DEFAULT 0 NOT NULL,
    PRIMARY KEY(service_type, api_action)
);

CREATE TABLE workflow_service_action_info
(
    api_action varchar(255) PRIMARY KEY NOT NULL,
    action_name text,
    public_params text,
    required_params text,
    extra_params text,
    result_params text
);


CREATE TABLE workflow_service_param
(
    param_key varchar(50) PRIMARY KEY NOT NULL,
    param_name varchar(50) NOT NULL
);

CREATE TABLE workflow_model
(
    workflow_model_id varchar(50) PRIMARY KEY NOT NULL,
    workflow_model_name text,
    api_actions varchar(255) DEFAULT '' NOT NULL,
    service_type varchar(50) NOT NULL,
    env_params text,
    description text,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    zone varchar(255) DEFAULT '' NOT NULL
);

CREATE TABLE workflow
(
    workflow_id varchar(50) PRIMARY KEY NOT NULL,
    workflow_model_id varchar(50) NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    curr_action varchar(255) DEFAULT '' NOT NULL,
    action_param text,
    workflow_params text,
    api_return text,
    api_error text,
    result text,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE TABLE workflow_config
(
    workflow_config_id varchar(50) PRIMARY KEY NOT NULL,
    workflow_model_id varchar(50) NOT NULL,
    request_type varchar(255) DEFAULT '' NOT NULL,
    request_action varchar(255) DEFAULT '' NOT NULL,
    status integer DEFAULT 0 NOT NULL

);

CREATE TABLE instance_class_disk_type
(
    instance_class_key varchar(50) DEFAULT '' NOT NULL,
    instance_class integer DEFAULT 0 NOT NULL,
    disk_type integer DEFAULT 0 NOT NULL,
    zone_deploy varchar(50) DEFAULT 'standard' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(instance_class_key, zone_deploy)
);


CREATE TABLE gpu_class_type
(
    gpu_class_key varchar(255) NOT NULL,
    gpu_class integer DEFAULT 0 NOT NULL,
    zone_id varchar(50) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(gpu_class_key, zone_id)
);


CREATE TABLE file_share_group
(
    file_share_group_id varchar(50) PRIMARY KEY NOT NULL,
    file_share_service_id varchar(50) DEFAULT '' NOT NULL,
    file_share_group_name varchar(255) DEFAULT '' NOT NULL,
    description text DEFAULT '',
    show_location varchar(255) DEFAULT '' NOT NULL,
    scope varchar(50) DEFAULT 'all_roles' NOT NULL,
    file_share_group_dn text DEFAULT '' NOT NULL,
    base_dn text DEFAULT '' NOT NULL,
    trashed_status varchar(50) DEFAULT 'inactive' NOT NULL,
    trashed_time timestamp DEFAULT current_timestamp NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    update_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE file_share_group_zone
(
    file_share_group_id varchar(50) NOT NULL,
    zone_id varchar(50) NOT NULL,
    user_scope varchar(50) DEFAULT 'all_roles' NOT NULL,
    PRIMARY KEY(file_share_group_id, zone_id)
);

CREATE TABLE file_share_group_user
(
    file_share_group_id varchar(50) NOT NULL,
    user_id varchar(255) NOT NULL,
    zone_id varchar(50) NOT NULL,
    user_type varchar(255) DEFAULT 'user' NOT NULL,
    file_share_group_dn text DEFAULT '' NOT NULL,
    PRIMARY KEY(file_share_group_id, user_id, zone_id)
);

CREATE TABLE file_share_group_file
(
    file_share_group_file_id varchar(50) PRIMARY KEY NOT NULL,
    file_share_group_id varchar(50) NOT NULL,
    file_share_group_file_name varchar(255) DEFAULT '' NOT NULL,
    file_share_group_file_alias_name text DEFAULT '',
    description text DEFAULT '',
    file_share_group_file_size BIGINT DEFAULT 0 NOT NULL,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    file_share_group_dn text DEFAULT '' NOT NULL,
    file_share_group_file_dn text DEFAULT '' NOT NULL,
    trashed_status varchar(50) DEFAULT 'inactive' NOT NULL,
    trashed_time timestamp DEFAULT current_timestamp NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE file_share_group_file_download_history
(
    file_download_history_id varchar(50) PRIMARY KEY NOT NULL,
    file_share_group_file_id varchar(50) NOT NULL,
    user_id varchar(255) DEFAULT '' NOT NULL,
    user_name varchar(255) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    update_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE file_share_service
(
  file_share_service_id varchar(50) PRIMARY KEY NOT NULL,
  file_share_service_name text,
  description text,
  network_id varchar(50) DEFAULT '' NOT NULL,
  desktop_server_instance_id varchar(50) DEFAULT '' NOT NULL,
  file_share_service_instance_id varchar(50) DEFAULT '' NOT NULL,
  private_ip varchar(255) DEFAULT '' NOT NULL,
  eip_addr varchar(255) DEFAULT '' NOT NULL,
  vnas_private_ip varchar(255) DEFAULT '' NOT NULL,
  vnas_id varchar(50) DEFAULT '' NOT NULL,
  is_sync integer DEFAULT 0 NOT NULL,
  transition_status varchar(50) DEFAULT '' NOT NULL,
  status varchar(50) DEFAULT 'active' NOT NULL,
  scope varchar(50) DEFAULT 'part_roles' NOT NULL,
  limit_rate  integer DEFAULT 1 NOT NULL,
  limit_conn  integer DEFAULT 5 NOT NULL,
  loaded_clone_instance_ip varchar(255) DEFAULT '' NOT NULL,
  fuser varchar(50) DEFAULT '' NOT NULL,
  fpw varchar(255) DEFAULT '' NOT NULL,
  ftp_chinese_encoding_rules varchar(50) DEFAULT 'utf-8' NOT NULL,
  create_method varchar(50) DEFAULT 'created' NOT NULL,
  max_download_file_size integer DEFAULT 100 NOT NULL,
  max_upload_size_single_file integer DEFAULT 1 NOT NULL,
  create_time timestamp DEFAULT current_timestamp NOT NULL,
  status_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE file_share_service_vnas
(
  vnas_id varchar(50) PRIMARY KEY NOT NULL,
  vnas_name text,
  vnas_private_ip varchar(255) DEFAULT '' NOT NULL,
  status varchar(50) DEFAULT 'active' NOT NULL,
  create_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE broker_app
(
   broker_app_id varchar(50) PRIMARY KEY NOT NULL,
   broker_app_uid varchar(50) DEFAULT '' NOT NULL,
   display_name text NOT NULL,
   description text,
   cmd_argument text DEFAULT '' NOT NULL,
   cmd_exe_path text DEFAULT '' NOT NULL,
   working_dir text DEFAULT '' NOT NULL,
   shortcut_path text DEFAULT '' NOT NULL,
   normal_display_name text DEFAULT '' NOT NULL,
   admin_display_name text DEFAULT '' NOT NULL,
   icon_data text DEFAULT '' NOT NULL,
   floder_name text DEFAULT '' NOT NULL,
   status varchar(50) DEFAULT 'active' NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   status_time timestamp DEFAULT current_timestamp NOT NULL,
   zone varchar(50) DEFAULT '' NOT NULL
);

CREATE TABLE broker_app_delivery_group
(
   broker_app_id varchar(50) NOT NULL,
   broker_app_name text,
   delivery_group_id varchar(50) NOT NULL,
   delivery_group_name text,
   broker_type varchar(50) DEFAULT 'broker_app' NOT NULL,
   PRIMARY KEY(broker_app_id, delivery_group_id)
);


CREATE TABLE broker_app_group
(
   broker_app_group_id varchar(50) PRIMARY KEY NOT NULL,
   broker_app_group_name text,
   description text,
   broker_app_group_uid varchar(50) DEFAULT '' NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   zone varchar(50) DEFAULT '' NOT NULL
);

CREATE TABLE broker_app_group_broker_app
(
   broker_app_id varchar(50) NOT NULL,
   broker_app_name text,
   broker_app_group_id varchar(50) NOT NULL,
   broker_app_group_name text,
   PRIMARY KEY(broker_app_id, broker_app_group_id)
);

CREATE TABLE desktop_maintainer
(
    desktop_maintainer_id varchar(50) PRIMARY KEY NOT NULL,
    desktop_maintainer_name varchar(50) DEFAULT '' NOT NULL,
    desktop_maintainer_type varchar(50) DEFAULT '' NOT NULL,
    description text,
    json_detail text,
    status varchar(50) DEFAULT 'active' NOT NULL,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    is_apply integer DEFAULT 0 NOT NULL,
    zone_id varchar(50) NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX desktop_maintainer_desktop_maintainer_name_index ON desktop_maintainer (desktop_maintainer_name);
CREATE INDEX desktop_maintainer_desktop_maintainer_type_index ON desktop_maintainer (desktop_maintainer_type);
CREATE INDEX desktop_maintainer_description_index ON desktop_maintainer (description);
CREATE INDEX desktop_maintainer_status_index ON desktop_maintainer (status);
CREATE INDEX desktop_maintainer_zone_id_index ON desktop_maintainer (zone_id);

CREATE TABLE desktop_maintainer_resource
(
    desktop_maintainer_id varchar(50),
    resource_id varchar(50) DEFAULT '' NOT NULL,
    resource_type varchar(50) DEFAULT '' NOT NULL,
    resource_name text,
    zone_id varchar(50) NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(desktop_maintainer_id, resource_id, zone_id)
);
CREATE INDEX desktop_maintainer_resource_resource_id_index ON desktop_maintainer_resource (resource_id);
CREATE INDEX desktop_maintainer_resource_resource_type_index ON desktop_maintainer_resource (resource_type);
CREATE INDEX desktop_maintainer_resource_resource_name_index ON desktop_maintainer_resource (resource_name);
CREATE INDEX desktop_maintainer_resource_zone_id_index ON desktop_maintainer_resource (zone_id);

CREATE TABLE guest_shell_command
(
    guest_shell_command_id varchar(50) PRIMARY KEY NOT NULL,
    guest_shell_command_name varchar(50) DEFAULT '' NOT NULL,
    guest_shell_command_type varchar(50) DEFAULT '' NOT NULL,
    command text,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    command_response text DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE INDEX guest_shell_command_guest_shell_command_name_index ON guest_shell_command (guest_shell_command_name);
CREATE INDEX guest_shell_command_guest_shell_command_type_index ON guest_shell_command (guest_shell_command_type);
CREATE INDEX guest_shell_command_command_index ON guest_shell_command (command);

CREATE TABLE guest_shell_command_resource
(
    guest_shell_command_id varchar(50),
    resource_id varchar(50) DEFAULT '' NOT NULL,
    resource_type varchar(50) DEFAULT '' NOT NULL,
    zone_id varchar(50) NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(guest_shell_command_id, resource_id, zone_id)
);
CREATE INDEX guest_shell_command_resource_resource_id_index ON guest_shell_command_resource (resource_id);
CREATE INDEX guest_shell_command_resource_resource_type_index ON guest_shell_command_resource (resource_type);
CREATE INDEX guest_shell_command_resource_zone_id_index ON guest_shell_command_resource (zone_id);


CREATE TABLE guest_shell_command_run_history
(
    guest_shell_command_run_history_id varchar(50) PRIMARY KEY NOT NULL,
    guest_shell_command_id varchar(50) NOT NULL,
    resource_id varchar(50) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    update_time timestamp DEFAULT current_timestamp NOT NULL
);
CREATE TABLE api_limit
(
   api_action varchar(50) PRIMARY KEY NOT NULL,
   enable integer DEFAULT 0 NOT NULL,
   refresh_interval integer DEFAULT 60 NOT NULL,
   refresh_time integer DEFAULT 5 NOT NULL
);
CREATE TABLE citrix_policy
(
  pol_id character varying(50) NOT NULL,
  policy_name character varying(255) NOT NULL DEFAULT ''::character varying,
  description text DEFAULT ''::text,
  pol_priority integer NOT NULL,
  pol_state integer NOT NULL DEFAULT 0,
  create_time timestamp without time zone NOT NULL DEFAULT now(),
  update_time timestamp without time zone NOT NULL DEFAULT now(),
  zone character varying(255) NOT NULL DEFAULT ''::character varying,
  com_priority integer NOT NULL DEFAULT 0,
  user_priority integer NOT NULL DEFAULT 0,
  CONSTRAINT citrix_policy_pkey PRIMARY KEY (pol_id)
);
CREATE TABLE citrix_policy_filter
(
  pol_filter_id character varying(50) NOT NULL,
  pol_id character varying(50) NOT NULL,
  pol_filter_name character varying(255) NOT NULL DEFAULT ''::character varying,
  pol_filter_type character varying(20) NOT NULL DEFAULT ''::character varying,
  pol_filter_state integer NOT NULL DEFAULT 0,
  pol_filter_value text DEFAULT ''::text,
  pol_filter_mode character varying(20) NOT NULL DEFAULT ''::character varying,
  create_time timestamp without time zone NOT NULL DEFAULT now(),
  update_time timestamp without time zone NOT NULL DEFAULT now(),
  zone character varying(255) NOT NULL DEFAULT ''::character varying,
  CONSTRAINT citrix_policy_filter_pkey PRIMARY KEY (pol_filter_id)
);
CREATE TABLE citrix_policy_item
(
  pol_item_id character varying(50) NOT NULL,
  pol_item_name character varying(50) NOT NULL,
  pol_id character varying(50),
  pol_item_type character varying(20) NOT NULL DEFAULT ''::character varying,
  pol_item_state integer NOT NULL DEFAULT 0,
  pol_item_value text DEFAULT ''::text,
  create_time timestamp without time zone NOT NULL DEFAULT now(),
  update_time timestamp without time zone NOT NULL DEFAULT now(),
  zone character varying(255) NOT NULL DEFAULT ''::character varying,
  CONSTRAINT citrix_policy_item_pkey PRIMARY KEY (pol_item_id)
);
CREATE TABLE citrix_policy_item_config
(
  pol_item_name character varying(255) NOT NULL DEFAULT ''::character varying,
  pol_item_type character varying(20) NOT NULL DEFAULT ''::character varying,
  pol_item_state integer NOT NULL DEFAULT 0,
  pol_item_value text DEFAULT ''::text,
  description text DEFAULT ''::text,
  pol_item_path character varying(255) NOT NULL DEFAULT ''::character varying,
  col1 character varying(255) NOT NULL DEFAULT ''::character varying,
  col2 character varying(255) NOT NULL DEFAULT ''::character varying,
  col3 character varying(255) NOT NULL DEFAULT ''::character varying,
  create_time timestamp without time zone NOT NULL DEFAULT now(),
  update_time timestamp without time zone NOT NULL DEFAULT now(),
  pol_item_datatype text DEFAULT ''::text,
  pol_item_name_ch text DEFAULT ''::text,
  pol_item_tip text DEFAULT ''::text,
  pol_item_unit text DEFAULT ''::text,
  pol_item_value_ch text DEFAULT ''::text,
  pol_item_path_ch text DEFAULT ''::text,
  CONSTRAINT citrix_policy_item_config_pkey PRIMARY KEY (pol_item_name)
);
