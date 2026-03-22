ALTER TABLE file_share_service ADD COLUMN fuser varchar(50) DEFAULT '' NOT NULL;
ALTER TABLE file_share_service ADD COLUMN fpw varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE file_share_service ADD COLUMN create_method varchar(50) DEFAULT 'created' NOT NULL;
ALTER TABLE file_share_group_file ALTER COLUMN file_share_group_file_size TYPE BIGINT;


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

/* init guest_shell_command*/
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uaa','shutdown','common_command', 'shutdown /s');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uab','shutdown','common_command', 'shutdown /r');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uac','shutdown','common_command', 'shutdown /l');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uad','shutdown','common_command', 'shutdown /h /f');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uae','shutdown','common_command', 'shutdown /a');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uaf','shutdown','common_command', 'shutdown /s /t 3600');

INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uag','ipconfig','common_command', 'ipconfig /all');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uah','ipconfig','common_command', 'ipconfig /flushdns');

INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uai','task','common_command', 'tasklist');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uaj','task','common_command', 'taskkill /f /im explorer.exe');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uak','task','common_command', 'start explorer.exe');

INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6ual','net','common_command', 'net start');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uam','systeminfo','common_command', 'systeminfo');


