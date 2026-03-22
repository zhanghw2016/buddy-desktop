ALTER TABLE component_version ADD COLUMN create_time timestamp DEFAULT current_timestamp NOT NULL;
ALTER TABLE component_version ADD COLUMN transition_status varchar(50) DEFAULT '' NOT NULL;
