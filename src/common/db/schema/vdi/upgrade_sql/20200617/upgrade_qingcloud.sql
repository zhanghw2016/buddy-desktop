      /*add netscaler_uri and netscaler_port in zone_citrix_connection*/
ALTER TABLE zone_citrix_connection ADD COLUMN netscaler_port integer DEFAULT 443 NOT NULL;
ALTER TABLE zone_citrix_connection ADD COLUMN netscaler_uri varchar(50) DEFAULT '' NOT NULL;