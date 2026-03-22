alter table desktop_group add column provision_type varchar(255) DEFAULT 'MCS' NOT NULL;

alter table delivery_group add column delivery_group_uid varchar(50) DEFAULT '' NOT NULL;
alter table delivery_group add column delivery_type varchar(255) DEFAULT 'DesktopsOnly' NOT NULL;
alter table notice_push add column force_read integer DEFAULT 0 NOT NULL;

CREATE TABLE notice_read
(
    notice_id varchar(50) NOT NULL,
    user_id varchar(50) NOT NULL,
    user_name text,
    PRIMARY KEY(notice_id, user_id)
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

