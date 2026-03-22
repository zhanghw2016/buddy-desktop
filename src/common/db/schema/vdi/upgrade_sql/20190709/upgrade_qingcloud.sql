/* alter zone_config*/
ALTER TABLE zone_config ADD COLUMN  max_chain_count integer DEFAULT 2 NOT NULL;
ALTER TABLE zone_config ADD COLUMN  max_snapshot_count integer DEFAULT 30 NOT NULL;
/* alter desktop_snapshot*/
ALTER TABLE desktop_snapshot ADD COLUMN desktop_resource varchar(50) NOT NULL;