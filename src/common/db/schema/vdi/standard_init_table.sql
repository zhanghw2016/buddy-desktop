/* init module_type*/
INSERT INTO module_type (item_key,enable_module) VALUES ('support_desktop_groups',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_load_computer_catalogs',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_load_computers',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_update_desktop_images',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_delivery_groups',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_load_delivery_groups',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_desktops',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_desktop_images',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_desktop_networks',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_scheduler_tasks',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_policy_groups',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_snapshot_groups',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_authous',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_userscope',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_resource_apply_froms',0);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_desktop_system_logs',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_desktop_jobs',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_notice_pushs',0);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_radius_services',0);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_desktop_service_management',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_system_config',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_module_custom',0);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_resource_permission',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_terminal_management',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_config_management',1);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_workflow',0);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_share_security_policys',0);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_file_shares',0);
INSERT INTO module_type (item_key,enable_module) VALUES ('support_citrix_policy',0);

update module_type set enable_module=1;
update module_type set enable_module=0 where item_key='support_resource_apply_froms';
update module_type set enable_module=0 where item_key='support_notice_pushs';
update module_type set enable_module=0 where item_key='support_radius_services';
update module_type set enable_module=0 where item_key='support_module_custom';
update module_type set enable_module=0 where item_key='support_workflow';
update module_type set enable_module=0 where item_key='support_share_security_policys';
update module_type set enable_module=0 where item_key='support_file_shares';
update module_type set enable_module=0 where item_key='support_citrix_policy';

/*删除user_login_record索引*/
drop index user_login_record_user_id_index;
drop index user_login_record_user_name_index;
drop index user_login_record_zone_id_index;
drop index user_login_record_status_index;
drop index user_login_record_errmsg_index;