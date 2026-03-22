/* init component_version*/
INSERT INTO component_version(component_id,component_name,component_type,version,filename,description) VALUES ('compvn-default-client','linux_client','client', '2.0.0-10','qingcloud-desktop-client-64-upgrade-2.0.0-201905101105-10-gfa1f91f.bin','linux client upgrade package');
INSERT INTO component_version(component_id,component_name,component_type,version,filename,description) VALUES ('compvn-default-server','desktop_server','server', '2.0.0-101','qingcloud-desktop-server-upgrade-2.0.0-201905201832-101-g9c07c72.bin','desktop server upgrade package');

ALTER TABLE component_version ADD COLUMN upgrade_packet_md5 varchar(256) DEFAULT '' NOT NULL;
ALTER TABLE component_version ADD COLUMN upgrade_packet_size integer DEFAULT 0 NOT NULL;