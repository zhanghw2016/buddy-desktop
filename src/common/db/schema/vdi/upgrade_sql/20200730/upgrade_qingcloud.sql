
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
    PRIMARY KEY(file_share_group_id, user_id, zone_id)
);

CREATE TABLE file_share_group_file
(
    file_share_group_file_id varchar(50) PRIMARY KEY NOT NULL,
    file_share_group_id varchar(50) NOT NULL,
    file_share_group_file_name varchar(255) DEFAULT '' NOT NULL,
    file_share_group_file_alias_name text DEFAULT '',
    description text DEFAULT '',
    file_share_group_file_size integer DEFAULT 0 NOT NULL,
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

UPDATE module_type SET enable_module=0 WHERE item_key='support_softwares';
INSERT INTO module_type (item_key,enable_module) VALUES ('support_file_shares',1);
