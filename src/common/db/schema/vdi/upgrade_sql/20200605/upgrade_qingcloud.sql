/*add service_node_name service_node_version in desktop_service_management*/
ALTER TABLE desktop_service_management ADD COLUMN service_node_name varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE desktop_service_management ADD COLUMN service_node_version varchar(255) DEFAULT '' NOT NULL;
