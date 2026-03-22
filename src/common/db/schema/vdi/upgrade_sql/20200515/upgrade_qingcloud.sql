/*add status in component_version*/
ALTER TABLE component_version ADD COLUMN status varchar(50) DEFAULT 'normal' NOT NULL;
