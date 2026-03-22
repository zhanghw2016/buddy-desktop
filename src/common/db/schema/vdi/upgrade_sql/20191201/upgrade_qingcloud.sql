ALTER TABLE desktop_group ADD COLUMN dn_guid varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE desktop ADD COLUMN dn_guid varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE auth_service ADD COLUMN dn_guid varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE radius_service ADD COLUMN dn_guid varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE desktop ADD COLUMN dn_guid varchar(255) DEFAULT '' NOT NULL;


ALTER TABLE desktop_user DROP column error_times;
ALTER TABLE desktop_user DROP column check_time;
ALTER TABLE auth_service DROP column error_times;
ALTER TABLE security_policy DROP column is_default;
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','PasswordSecurityConfiguration','badPwdCount','2',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','PasswordSecurityConfiguration','lockPasswordTime','5',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','PasswordSecurityConfiguration','passwordExpirePeriod','90',1);



ALTER TABLE delivery_group_user add user_name varchar(255) DEFAULT '' NOT NULL;

ALTER TABLE policy_group add is_default integer DEFAULT 0 NOT NULL;
ALTER TABLE policy_group_resource add policy_group_type varchar(50) DEFAULT 'security' NOT NULL;
ALTER TABLE security_ipset add transition_status varchar(50) DEFAULT '' NOT NULL;

ALTER TABLE user_login_record add status varchar(50) DEFAULT '' NOT NULL;
ALTER TABLE user_login_record add errmsg varchar(256) DEFAULT '';
