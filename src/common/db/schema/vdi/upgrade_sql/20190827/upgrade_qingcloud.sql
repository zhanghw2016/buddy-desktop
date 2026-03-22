CREATE TABLE desktop_user
(
   user_id varchar(255) PRIMARY KEY NOT NULL,
   auth_service_id varchar(255) NOT NULL,
   user_name varchar(255) NOT NULL,
   role varchar(255) DEFAULT '' NOT NULL,
   object_guid varchar(255) DEFAULT '' NOT NULL,
   real_name varchar(255) DEFAULT '' NOT NULL,
   description text,
   password varchar(255) DEFAULT '' NOT NULL,
   ou_dn varchar(255) DEFAULT '' NOT NULL,
   user_dn varchar(255) DEFAULT '',
   status varchar(50) DEFAULT 'active' NOT NULL,
   user_control varchar(50) NOT NULL,
   last_zone varchar(255) DEFAULT '' NOT NULL,
   default_zone varchar(255) DEFAULT '' NOT NULL,
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   update_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE zone_user
(
    user_id varchar(255) NOT NULL,                       -- the user_id
    zone_id varchar(50) NOT NULL,                        -- the zone_id
    user_name varchar(255) NOT NULL,
    role varchar(50) DEFAULT 'normal' NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    radius_black integer DEFAULT 0 NOT NULL,
    user_error_times integer DEFAULT 0 NOT NULL,
    PRIMARY KEY(user_id, zone_id)
);

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
   auth_service_id varchar(255) NOT NULL,
   user_group_name varchar(255) NOT NULL,
   object_guid varchar(255) DEFAULT '' NOT NULL,
   description text DEFAULT '',
   user_group_dn varchar(255) DEFAULT '',
   base_dn varchar(255) DEFAULT '',
   create_time timestamp DEFAULT current_timestamp NOT NULL,
   update_time timestamp DEFAULT current_timestamp NOT NULL
);

CREATE TABLE desktop_user_group_user
(
   user_group_id varchar(255) NOT NULL,
   user_id varchar(255) NOT NULL,
   PRIMARY KEY(user_group_id, user_id)
);


CREATE TABLE zone_user_group
(
    user_group_id varchar(255) NOT NULL,                       -- the user_id
    zone_id varchar(50) NOT NULL,                        -- the zone_id
    PRIMARY KEY(user_group_id, zone_id)
);

CREATE TABLE desktop_user_scope_action
(
   action_id varchar(255) NOT NULL,
   action_name varchar(255) DEFAULT '' NOT NULL,
   action_api varchar(255) NOT NULL,
   PRIMARY KEY(action_id, action_api)
);


CREATE TABLE security_policy_share
(
    security_policy_id varchar(50) PRIMARY KEY NOT NULL,
    shared_policy_id varchar(50) NOT NULL,
    is_sync integer DEFAULT 0 NOT NULL,
    zone varchar(255) DEFAULT '' NOT NULL
);

-- desktop zone table
CREATE TABLE desktop_zone
(
    zone_id varchar(50) PRIMARY KEY NOT NULL,
    zone_name varchar(50) DEFAULT '' NOT NULL,
    platform varchar(50) NOT NULL,
    status varchar(50) NOT NULL,
    visibility varchar(50) DEFAULT '' NOT NULL,
    description text,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL
);

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
    host_url varchar(255) DEFAULT '' NOT NULL,
    host varchar(255) NOT NULL,
    port integer DEFAULT 80 NOT NULL,
    protocol varchar(50) DEFAULT 'http' NOT NULL,
    http_socket_timeout integer DEFAULT 120 NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL
);


CREATE TABLE zone_citrix_connection
(
    zone_id varchar(50) PRIMARY KEY NOT NULL,
    host varchar(255) DEFAULT '' NOT NULL,
    port integer DEFAULT 80 NOT NULL,
    protocol varchar(50) DEFAULT 'http' NOT NULL,
    http_socket_timeout integer DEFAULT 120 NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    managed_resource varchar(255) DEFAULT '' NOT NULL,
    storefront_uri varchar(50) DEFAULT '' NOT NULL,
    storefront_port integer DEFAULT 80 NOT NULL
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
    desktop_count_per_group integer DEFAULT 256 NOT NULL,
    default_passwd varchar(255) DEFAULT 'Desktop123' NOT NULL,
    network_type text,
    ivshmem varchar(50) DEFAULT '' NOT NULL
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
    domain varchar(255) NOT NULL,
    host varchar(255) DEFAULT '' NOT NULL,
    port integer DEFAULT 80 NOT NULL,
    secret_port integer DEFAULT 80 NOT NULL,
    is_sync integer DEFAULT 0 NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL
);






