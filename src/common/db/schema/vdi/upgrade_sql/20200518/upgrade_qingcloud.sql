/*add component_version_log in component_version*/
ALTER TABLE component_version ADD COLUMN component_version_log text DEFAULT '';
ALTER TABLE component_version ADD COLUMN component_version_log_history text DEFAULT '';
