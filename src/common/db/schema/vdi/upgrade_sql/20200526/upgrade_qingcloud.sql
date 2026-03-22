/*add need_upgrade in component_version*/
ALTER TABLE component_version ADD COLUMN need_upgrade integer DEFAULT 0 NOT NULL;
