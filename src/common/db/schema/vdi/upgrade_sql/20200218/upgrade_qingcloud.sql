ALTER TABLE desktop_zone ADD COLUMN zone_deploy varchar(50) DEFAULT 'standard' NOT NULL;
ALTER TABLE instance_class_disk_type DROP COLUMN current_zone_deploy;