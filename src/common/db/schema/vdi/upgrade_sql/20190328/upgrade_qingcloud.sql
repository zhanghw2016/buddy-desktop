/*alter  table*/
/*ALTER TABLE vdi_system_config ADD  test varchar(255);*/


/*update table*/
/*UPDATE vdi_system_config SET config_value = 'ch' WHERE config_key = 'lang';*/
ALTER TABLE zone_config ADD COLUMN storefront_uri varchar(50) DEFAULT '' NOT NULL;
ALTER TABLE zone_config ADD COLUMN storefront_port integer DEFAULT 80 NOT NULL;

ALTER TABLE delivery_group_user ADD COLUMN is_hide integer DEFAULT 0 NOT NULL;
ALTER TABLE delivery_group_user ADD COLUMN user_group_name text;

ALTER TABLE vdi_user ADD COLUMN radius_black integer NOT NULL DEFAULT 0;
ALTER TABLE vdi_user ADD COLUMN user_error_times integer NOT NULL DEFAULT 0;
