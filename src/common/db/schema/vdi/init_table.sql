/* init vdi_system_config*/
INSERT INTO vdi_system_config (config_key, config_value) VALUES ('lang', 'zh-cn');
INSERT INTO vdi_system_config (config_key, config_value) VALUES ('enable_trash', 'N');
INSERT INTO vdi_system_config (config_key, config_value) VALUES ('license_str', '');
INSERT INTO vdi_system_config (config_key, config_value) VALUES ('syslog_lock', 'N');

/* init vdi_user */
INSERT INTO desktop_user(user_id, user_name, real_name, description, password, role, status,user_control) VALUES ('global_admin', 'admin', 'admin', 'This is global admin user!', 'password', 'global_admin', 'active', 546);


/*init instance class*/
/*性能型主机*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy) VALUES ('high_performance',0,0,'standard');
/*超高性能主机*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy) VALUES ('high_performance_plus',1,3,'standard');
/*SANC型主机 全闪存*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy) VALUES ('san_container_all_flash',6,5,'standard');
/*SANC型主机 混插*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy) VALUES ('san_container_mixed_flash',7,6,'standard');

/*性能型主机*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy) VALUES ('high_performance',0,5,'express');
/*超高性能主机*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy) VALUES ('high_performance_plus',1,5,'express');
/*SANC型主机 全闪存*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy) VALUES ('san_container_all_flash',6,5,'express');
/*SANC型主机 混插*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy) VALUES ('san_container_mixed_flash',7,5,'express');

/* init image*/
INSERT INTO desktop_image(desktop_image_id,image_id,image_name,description,platform,os_version,os_family,image_type, session_type,ui_type) VALUES ('default_win7_tui','desktop_win7prox64cn_tui','Windows7基础镜像', 'Windows7基础镜像(未安装桌面Tools)','windows','Windows7','windows','model','SingleSession','tui');
INSERT INTO desktop_image (desktop_image_id,image_id,image_name,description,platform,os_version,os_family,image_type, session_type,ui_type) VALUES ('default_win10_tui','desktop_win10prox64cn_tui','Windows10基础镜像', 'Windows10基础镜像(未安装桌面Tools)','windows','Windows10','windows','model','SingleSession','tui');

INSERT INTO desktop_image(desktop_image_id,image_id,image_name,description,platform,os_version,os_family,image_type, session_type,ui_type) VALUES ('default_win7_gui','desktop_win7prox64cn_gui','Windows7基础镜像', 'Windows7基础镜像(未安装桌面Tools)','windows','Windows7','windows','model','SingleSession','gui');
INSERT INTO desktop_image (desktop_image_id,image_id,image_name,description,platform,os_version,os_family,image_type, session_type,ui_type) VALUES ('default_win10_gui','desktop_win10prox64cn_gui','Windows10基础镜像', 'Windows10基础镜像(未安装桌面Tools)','windows','Windows10','windows','model','SingleSession','gui');
/* init workflow_service*/
insert into workflow_service(service_type,service_name,description) values('CreateUserAndResource','新建用户和资源','测试Workflow');
insert into workflow_service(service_type,service_name,description) values('DeleteUserAndResource','清理用户和资源','测试Workflow');


insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('CreateUserAndResource','CreateAuthUser', '创建新用户',0,1);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('CreateUserAndResource','AddAuthUserToUserGroup', '用户添加到用户组',1,0);

insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','DeleteAuthUsers', '删除用户',8,8);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','DeleteDesktops', '删除桌面',6,0);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','DescribeAuthUsers', '查询用户',0,1);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','DisableAuthUsers', '禁用用户',8,8);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','RemoveAuthUserFromUserGroup', '指定用户组删除用户',7,0);

insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('CreateAuthUser', '创建新用户','["auth_service"]','["user_name","password", "ou_dn"]','["account_control","real_name","email","description"]','["user_id"]');

insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('AddAuthUserToUserGroup', '用户添加到用户组','["auth_service","user_group"]','["user_name"]','','');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('DeleteAuthUsers', '删除用户','','["user_id","user_name"]','','');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('DescribeAuthUsers', '查询用户','["auth_service"]','["user_name"]','','["user_id"]');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('DisableAuthUsers', '禁用用户','["auth_service"]','["user_id"]','','');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('DeleteDesktops', '删除桌面','','["user_id"]','','["desktops"]');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('RemoveAuthUserFromUserGroup', '指定用户组删除用户','["auth_service","user_groups"]','["user_name"]','','');

insert into workflow_service_param(param_key,param_name) values('auth_service','认证服务ID');
insert into workflow_service_param(param_key,param_name) values('delivery_group','交付组ID');
insert into workflow_service_param(param_key,param_name) values('desktop_group','桌面组ID');
insert into workflow_service_param(param_key,param_name) values('user_name','用户名');
insert into workflow_service_param(param_key,param_name) values('user_id','用户ID');
insert into workflow_service_param(param_key,param_name) values('password','密码');
insert into workflow_service_param(param_key,param_name) values('account_control','首次登陆修改密码');
insert into workflow_service_param(param_key,param_name) values('real_name','真实姓名');
insert into workflow_service_param(param_key,param_name) values('email','邮箱');
insert into workflow_service_param(param_key,param_name) values('description','描述信息');
insert into workflow_service_param(param_key,param_name) values('desktop_id','桌面ID');

/* init module_custom*/
INSERT INTO module_custom (module_custom_id, is_default,custom_name,description) VALUES ('default_module_custom',1,'全局缺省功能定制', '系统默认全局功能配置，不要轻易修改，保存后会在全局应用到没有特殊配置的所有区域和管理员');

/* init module_custom_config*/
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DesktopGroups','support_desktop_groups','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DesktopGroups','support_load_computer_catalogs','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DesktopGroups','support_load_computers','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DesktopGroups','support_update_desktop_images','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DeliveryGroups','support_delivery_groups','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DeliveryGroups','support_load_delivery_groups','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','Desktops','support_desktops','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DesktopImages','support_desktop_images','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DesktopNetworks','support_desktop_networks','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','SchedulerTasks','support_scheduler_tasks','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','PolicyGroups','support_policy_groups','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','SnapshotGroups','support_snapshot_groups','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','AuthOUs','support_authous','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','ZoneUserScope','support_userscope','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','ResourceApplyForms','support_resource_apply_froms','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DesktopSystemLogs','support_desktop_system_logs','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DesktopJobs','support_desktop_jobs','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','NoticePushs','support_notice_pushs','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','RadiusServices','support_radius_services','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','Softwares','support_softwares','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','DesktopServiceManagement','support_desktop_service_management','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','SystemConfig','support_system_config','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','ModuleCustom','support_module_custom','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','ResourcePermission','support_resource_permission','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','TerminalManagement','support_terminal_management','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','ConfigManagement','support_config_management','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','WorkFlow','support_workflow','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','FileShares','support_file_shares','0',1);
INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','CitrixPolicy','support_citrix_policy','0',1);

/* init system_custom*/
INSERT INTO system_custom (system_custom_id, is_default,current_system_custom) VALUES ('default_system_custom', 1,0);
INSERT INTO system_custom (system_custom_id, is_default,current_system_custom) VALUES ('redefine_system_custom',0,1);


INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','console_name','云桌面 - 青云 QingCloud',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','copyright','Copyright © 2021 青云QingCloud',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','icon','/static/img/favicon.ico?v=1',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','header_logo','/static/img/vdi.svg',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','header_logo_text','桌面云',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','header_logo_size','28px',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','login_info_logo','/static/img/logo.svg',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','login_info_title','QingCloud 桌面云',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','login_info_subtitle','QingCloud 桌面云是基于 QingCloud 云平台研发的新一代企业级办公解决方案',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','login_logo_custom_background_color','#006b47',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','custom_login_entry','',0);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','UserConfiguration','support_approval_resource','0',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','UserConfiguration','support_approval_permission','0',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','UserConfiguration','support_import_users_from_excel','0',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','UserConfiguration','support_export_approval_permission_to_excel','0',1);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ProtocolConfiguration','default_connect_vnc_delay','3',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ProtocolConfiguration','vnc_proxy_ip','',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ProtocolConfiguration','qxl_number_max','2',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ProtocolConfiguration','cbserver_host','',1);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','UserPasswordRestore','support_user_password_restore','1', 1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','UserPasswordRestore','user_password_restore_type', 'security_question', 1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','UserPasswordRestore','security_question_policy', 'force',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','UserPasswordRestore','security_question_policy_min_number', '3',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','UserPasswordRestore','security_question_policy_check_number', '3',1);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','PasswordSecurityConfiguration','password_cannot_contain_username','0',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','PasswordSecurityConfiguration','new_password_cannot_be_the_same_as_old_password','0',0);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','PasswordSecurityConfiguration','account_password_policy','1110',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','PasswordSecurityConfiguration','badPwdCount','5',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','PasswordSecurityConfiguration','lockPasswordTime','5',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','PasswordSecurityConfiguration','passwordExpirePeriod','0',0);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','OtherConfiguration','support_load_firewalls','0',0);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','OtherConfiguration','url_prefix','',0);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','OtherConfiguration','os_versions_show','Windows7 Windows10 Windows2016 Linux',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','OtherConfiguration','os_versions','1111',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','OtherConfiguration','support_random_desktop_group_disk','',0);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','OtherConfiguration','support_disk_strategy','',0);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','SecurityDefaultIPSetPort','citrix_protocal_tcp_port','80,1494,2598,8008',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','SecurityDefaultIPSetPort','citrix_protocal_udp_port','1494,2598,8008',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','SecurityDefaultIPSetPort','domain_protocal_udp_port','53,88,123,137,138,389,443,464,636,49152-65535',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','SecurityDefaultIPSetPort','domain_protocal_tcp_port','53,88,135,139,389,443,445,464,636,3268,3269',1);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','InstanceParameter','cpu_model','Westmere,SandyBridge,IvyBridge,Haswell,Broadwell',1);
/* init system_custom_config redefine_system_custom*/
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','console_name','云桌面 - 青云 QingCloud',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','copyright','Copyright © 2021 青云QingCloud',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','icon','/static/img/favicon.ico?v=1',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','header_logo','/static/img/vdi.svg',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','header_logo_text','桌面云',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','header_logo_size','28px',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','login_info_logo','/static/img/logo.svg',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','login_info_title','QingCloud 桌面云',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','login_info_subtitle','QingCloud 桌面云是基于 QingCloud 云平台研发的新一代企业级办公解决方案',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','login_logo_custom_background_color','#006b47',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','custom_login_entry','',0);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','UserConfiguration','support_approval_resource','0',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','UserConfiguration','support_approval_permission','0',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','UserConfiguration','support_import_users_from_excel','0',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','UserConfiguration','support_export_approval_permission_to_excel','0',1);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ProtocolConfiguration','default_connect_vnc_delay','3',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ProtocolConfiguration','vnc_proxy_ip','',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ProtocolConfiguration','qxl_number_max','2',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ProtocolConfiguration','cbserver_host','',1);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','UserPasswordRestore','support_user_password_restore','1', 1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','UserPasswordRestore','user_password_restore_type', 'security_question', 1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','UserPasswordRestore','security_question_policy', 'force',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','UserPasswordRestore','security_question_policy_min_number', '3',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','UserPasswordRestore','security_question_policy_check_number', '3',1);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','PasswordSecurityConfiguration','password_cannot_contain_username','0',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','PasswordSecurityConfiguration','new_password_cannot_be_the_same_as_old_password','0',0);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','PasswordSecurityConfiguration','account_password_policy','1110',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','PasswordSecurityConfiguration','badPwdCount','5',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','PasswordSecurityConfiguration','lockPasswordTime','5',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','PasswordSecurityConfiguration','passwordExpirePeriod','0',0);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','OtherConfiguration','support_load_firewalls','0',0);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','OtherConfiguration','url_prefix','',0);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','OtherConfiguration','os_versions_show','Windows7 Windows10 Windows2016 Linux',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','OtherConfiguration','os_versions','1111',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','OtherConfiguration','support_random_desktop_group_disk','',0);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','OtherConfiguration','support_disk_strategy','',0);


INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','SecurityDefaultIPSetPort','citrix_protocal_tcp_port','80,1494,2598,8008',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','SecurityDefaultIPSetPort','citrix_protocal_udp_port','1494,2598,8008',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','SecurityDefaultIPSetPort','domain_protocal_udp_port','53,88,123,137,138,389,443,464,636,49152-65535',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','SecurityDefaultIPSetPort','domain_protocal_tcp_port','53,88,135,139,389,443,445,464,636,3268,3269',1);

INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','InstanceParameter','cpu_model','Westmere,SandyBridge,IvyBridge,Haswell,Broadwell',1);

/* init component_version*/
INSERT INTO component_version(component_id,component_name,component_type,version,filename,description) VALUES ('compvn-default-client','linux_client','client', '2.0.0-10','qingcloud-desktop-client-64-upgrade-2.0.0-201905101105-10-gfa1f91f.bin','linux client upgrade package');
INSERT INTO component_version(component_id,component_name,component_type,version,filename,description) VALUES ('compvn-default-server','desktop_server','server', '2.0.0-101','qingcloud-desktop-server-upgrade-2.0.0-201905201832-101-g9c07c72.bin','desktop server upgrade package');
INSERT INTO component_version(component_id,component_name,component_type,version,filename,description) VALUES ('compvn-default-qingcloud-guest-tools','qingcloud_guest_tools','tools', '2.0.0-1','qingcloud-guest-tools-upgrade-2.0.0-201905201832-1-g9c07c72.zip','qingcloud_guest_tools upgrade package');
INSERT INTO component_version(component_id,component_name,component_type,version,filename,description) VALUES ('compvn-default-qingcloud-file-share-tools','qingcloud_file_share_tools','file_share_tools', '2.1.0-1','qingcloud-file-share-tools-upgrade-2.1.0-202101051201-1-g9c07c72.exe','qingcloud_file_share_tools upgrade package');

/* init zone_user_scope_action */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-0', 'CreateAuthOU');
/* ACTION_ID_MGMT_USER_GROUPS_READONLY */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-1', 'DescribeZoneUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-1', 'DescribeAuthUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-1', 'DescribeAuthOUs');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-1', 'DescribeAuthUserGroups');
/* ACTION_ID_MGMT_USER_GROUP_UPDATE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'DescribeZoneUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'EnableZoneUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'DisableZoneUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'ModifyZoneUserRole');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'ModifyAuthUserAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'DescribeAuthUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'ModifyAuthUserPassword');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'ResetAuthUserPassword');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'ModifyAuthOUAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'DescribeAuthOUs');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'ChangeAuthUserInOU');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'ModifyAuthUserGroupAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'DescribeAuthUserGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'AddAuthUserToUserGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'RemoveAuthUserFromUserGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'RenameAuthUserDN');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'CreateAuthUserGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-2', 'CreateAuthUser');
/* ACTION_ID_MGMT_USER_GROUP_DELETE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'DescribeZoneUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'EnableZoneUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'DisableZoneUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'ModifyZoneUserRole');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'DeleteAuthUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'ModifyAuthUserAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'DescribeAuthUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'ModifyAuthUserPassword');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'ResetAuthUserPassword');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'DeleteAuthOU');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'ModifyAuthOUAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'DescribeAuthOUs');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'ChangeAuthUserInOU');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'ModifyAuthUserGroupAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'DeleteAuthUserGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'DescribeAuthUserGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'AddAuthUserToUserGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'RemoveAuthUserFromUserGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'RenameAuthUserDN');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'CreateAuthUserGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('user-ou-3', 'CreateAuthUser');

/* ACTION_ID_MGMT_DESKTOP */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-0', 'CreateDesktopGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-0', 'LoadComputerCatalogs');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-0', 'LoadComputers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-0', 'CreateDesktopDisks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-0', 'CreateDesktopSnapshots');
/* ACTION_ID_MGMT_DESKTOP_READONLY */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'DescribeDesktopGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'DescribeDesktopGroupDisks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'DescribeDesktopGroupNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'DescribeDesktopGroupUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'DescribeDesktopIPs');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'DescribeDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'DescribeDesktopDisks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'GetDesktopMonitor');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'FreeRandomDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'SendDesktopMessage');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'SendDesktopNotify');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'RestartDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'StartDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'StopDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'ResetDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'CreateBrokers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'DeleteBrokers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'AddDesktopActiveDirectory');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'LoginDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-1', 'LogoffDesktop');
/* ACTION_ID_MGMT_DESKTOP_UPDATE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DescribeDesktopGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DescribeDesktopGroupDisks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DescribeDesktopGroupNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DescribeDesktopGroupUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DescribeDesktopIPs');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DescribeDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DescribeDesktopDisks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'CreateDesktopGroupDisk');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'GetDesktopMonitor');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ModifyDesktopGroupStatus');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ModifyDesktopGroupAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ModifyDesktopGroupDisk');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ModifyDesktopGroupNetwork');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'CreateDesktopGroupNetwork');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'AttachUserToDesktopGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DetachUserFromDesktopGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ApplyDesktopGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ModifyDesktopAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'AttachUserToDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DetachUserFromDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'RestartDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'StartDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'StopDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ResetDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'SetDesktopMonitor');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'CreateBrokers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DeleteBrokers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ModifyDesktopIP');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DesktopLeaveNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DesktopJoinNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DescribeDesktopJobs');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'AttachDiskToDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DetachDiskFromDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ResizeDesktopDisk');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ModifyDesktopDiskAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'SendDesktopMessage');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'SendDesktopNotify');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'SendDesktopHotKeys');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'AddDesktopActiveDirectory');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'LoginDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'LogoffDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'CheckDesktopAgentStatus');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'SetDesktopGroupUserStatus');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'SetCitrixDesktopMode');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'AttachDesktopToDeliveryGroupUser');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'DetachDesktopFromDeliveryGroupUser');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ModifyResourceGroupPolicy');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'CreateDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ApplyDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'AddResourceToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'RemoveResourceFromPolicyGroup');
/* ACTION_ID_MGMT_DESKTOP_DELETE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DescribeDesktopGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ModifyDesktopGroupAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DeleteDesktopGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ModifyDesktopGroupStatus');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DescribeDesktopGroupDisks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ModifyDesktopGroupDisk');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DeleteDesktopGroupDisks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DescribeDesktopGroupNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ModifyDesktopGroupNetwork');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DeleteDesktopGroupNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DescribeDesktopGroupUsers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DescribeDesktopIPs');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'AttachUserToDesktopGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DetachUserFromDesktopGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ApplyDesktopGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DescribeDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ModifyDesktopAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DeleteDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'AttachUserToDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DetachUserFromDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'RestartDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'StartDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'StopDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ResetDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'SetDesktopMonitor');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'CreateBrokers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DeleteBrokers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ModifyDesktopIP');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DesktopLeaveNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DesktopJoinNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'GetDesktopMonitor');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DescribeDesktopJobs');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DeleteDesktopDisks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'AttachDiskToDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DetachDiskFromDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DescribeDesktopDisks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ResizeDesktopDisk');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ModifyDesktopDiskAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'SendDesktopMessage');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'SendDesktopNotify');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'SendDesktopHotKeys');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'AddDesktopActiveDirectory');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'LoginDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'LogoffDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'CheckDesktopAgentStatus');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'SetDesktopGroupUserStatus');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'SetCitrixDesktopMode');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'AttachDesktopToDeliveryGroupUser');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'DetachDesktopFromDeliveryGroupUser');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ModifyResourceGroupPolicy');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'CreateDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ApplyDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'AddResourceToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'RemoveResourceFromPolicyGroup');

/* ACTION_ID_MGMT_IMAGE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-0', 'CreateDesktopImage');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-0', 'SaveDesktopImages');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-0', 'LoadSystemImages');
/* ACTION_ID_MGMT_IMAGE_READONLY */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-1', 'DescribeDesktopImages');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-1', 'CreateBrokers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-1', 'DescribeSystemImages');
/* ACTION_ID_MGMT_IMAGE_UPDATE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-2', 'SaveDesktopImages');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-2', 'DescribeDesktopImages');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-2', 'ModifyDesktopImageAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-2', 'CreateBrokers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-2', 'DescribeSystemImages');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-2', 'LoadSystemImages');
/* ACTION_ID_MGMT_IMAGE_DELETE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-3', 'SaveDesktopImages');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-3', 'DescribeDesktopImages');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-3', 'DeleteDesktopImages');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-3', 'ModifyDesktopImageAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-3', 'CreateBrokers');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-3', 'DescribeSystemImages');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-image-3', 'LoadSystemImages');

/* ACTION_ID_MGMT_VXNET */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-0', 'CreateDesktopNetwork');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-0', 'LoadSystemNetwork');
/* ACTION_ID_MGMT_VXNET_READONLY */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-1', 'DescribeDesktopNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-1', 'DescribeSystemNetworks');
/* ACTION_ID_MGMT_VXNET_UPDATE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-2', 'ModifyDesktopNetworkAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-2', 'DescribeDesktopNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-2', 'DescribeSystemNetworks');
/* ACTION_ID_MGMT_VXNET_DELETE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-3', 'DescribeDesktopNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-3', 'ModifyDesktopNetworkAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-3', 'DeleteDesktopNetworks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-network-3', 'DescribeSystemNetworks');

/* ACTION_ID_MGMT_DELIVERY_GROUP */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-0', 'CreateDeliveryGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-0', 'LoadDeliveryGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-0', 'LoadComputerCatalogs');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-0', 'LoadComputers');
/* ACTION_ID_MGMT_DELIVERY_GROUP_READONLY */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-1', 'DescribeDeliveryGroups');
/* ACTION_ID_MGMT_DELIVERY_GROUP_UPDATE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'ModifyDeliveryGroupAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'AddDesktopToDeliveryGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'AddUserToDeliveryGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'AttachDesktopToDeliveryGroupUser');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'DetachDesktopFromDeliveryGroupUser');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'DelDesktopFromDeliveryGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'SetCitrixDesktopMode');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'SetDeliveryGroupMode');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'DescribeDeliveryGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'RefreshCitrixDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'ModifyResourceGroupPolicy');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'CreateDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'ApplyDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'RestartDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'StartDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'StopDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'DetachDiskFromDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'ModifyDesktopDiskAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'AddResourceToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'RemoveResourceFromPolicyGroup');
/* ACTION_ID_MGMT_DELIVERY_GROUP_DELETE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'ModifyDeliveryGroupAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'AddDesktopToDeliveryGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'AddUserToDeliveryGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'AttachDesktopToDeliveryGroupUser');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'DetachDesktopFromDeliveryGroupUser');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'DelDesktopFromDeliveryGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'SetCitrixDesktopMode');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'SetDeliveryGroupMode');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'DescribeDeliveryGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'DeleteDeliveryGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'ModifyResourceGroupPolicy');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'CreateDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'ApplyDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'DeleteDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'RestartDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'StartDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'StopDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'DeleteDesktops');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'DetachDiskFromDesktop');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'ModifyDesktopDiskAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'DeleteDesktopDisks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'AddResourceToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'RemoveResourceFromPolicyGroup');


/* ACTION_ID_MGMT_SNAPSHOT */

INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-0', 'CreateSnapshotGroup');
/* ACTION_ID_MGMT_SNAPSHOT_READONLY */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-1', 'DescribeDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-1', 'DescribeSnapshotGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-1', 'DescribeSnapshotGroupSnapshots');
/* ACTION_ID_MGMT_SNAPSHOT_UPDATE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'ApplyDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'CreateDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'ModifyDesktopSnapshotAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'CaptureDesktopFromDesktopSnapshot');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'CreateDiskFromDesktopSnapshot');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'ModifySnapshotGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'AddResourceToSnapshotGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'DeleteResourceFromSnapshotGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'DescribeDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'DescribeSnapshotGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-2', 'DescribeSnapshotGroupSnapshots');
/* ACTION_ID_MGMT_SNAPSHOT_DELETE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'DeleteDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'CreateDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'DeleteSnapshotGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'ApplyDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'ModifyDesktopSnapshotAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'CaptureDesktopFromDesktopSnapshot');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'CreateDiskFromDesktopSnapshot');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'ModifySnapshotGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'AddResourceToSnapshotGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'DeleteResourceFromSnapshotGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'DescribeDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'DescribeSnapshotGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('snapshot-group-3', 'DescribeSnapshotGroupSnapshots');

/* ACTION_ID_MGMT_SCHEDULER_TASK */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-0', 'CreateSchedulerTask');
/* ACTION_ID_MGMT_IMAGE_READONLY */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-1', 'DescribeSchedulerTasks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-1', 'DescribeSchedulerTaskHistory');
/* ACTION_ID_MGMT_SCHEDULER_TASK_UPDATE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-2', 'ModifySchedulerTaskAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-2', 'AddResourceToSchedulerTask');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-2', 'SetSchedulerTaskStatus');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-2', 'ExecuteSchedulerTask');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-2', 'GetSchedulerTaskResources');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-2', 'ModifySchedulerResourceDesktopCount');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-2', 'ModifySchedulerResourceDesktopImage');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-2', 'DeleteResourceFromSchedulerTask');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-2', 'DescribeSchedulerTasks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-2', 'DescribeSchedulerTaskHistory');
/* ACTION_ID_MGMT_SCHEDULER_TASK_DELETE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'DeleteSchedulerTasks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'ModifySchedulerTaskAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'AddResourceToSchedulerTask');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'SetSchedulerTaskStatus');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'ExecuteSchedulerTask');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'GetSchedulerTaskResources');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'ModifySchedulerResourceDesktopCount');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'ModifySchedulerResourceDesktopImage');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'DeleteResourceFromSchedulerTask');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'DescribeSchedulerTasks');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('scheduler-task-3', 'DescribeSchedulerTaskHistory');

/* ACTION_ID_MGMT_POLICY_GROUP */

INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-0', 'CreatePolicyGroup');
/* ACTION_ID_MGMT_POLICY_GROUP_READONLY */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-1', 'DescribeDesktopSecurityPolicys');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-1', 'DescribeDesktopSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-1', 'DescribeDesktopSecurityIPSets');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-1', 'DescribePolicyGroups');
/* ACTION_ID_MGMT_POLICY_GROUP_UPDATE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'ModifyDesktopSecurityPolicyAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'ApplyDesktopSecurityPolicy');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'ModifyDesktopSecurityRuleAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'RemoveDesktopSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'AddDesktopSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'ModifyDesktopSecurityIPSetAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'ApplyDesktopSecurityIPSet');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'SetDesktopSecurityPolicyShare');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'ImportDesktopSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'ModifyPolicyGroupAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'AddResourceToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'RemoveResourceFromPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'AddPolicyToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'RemovePolicyFromPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'ApplyPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'DescribeDesktopSecurityPolicys');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'DescribeDesktopSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'DescribeDesktopSecurityIPSets');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'DescribePolicyGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'ModifyResourceGroupPolicy');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'CreateDesktopSecurityIPSet');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'LoadSystemSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'LoadSystemSecurityIPSets');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'CreateDesktopSecurityPolicy');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'DeleteDesktopSecurityIPSets');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-2', 'DeletePolicyGroups');
/* ACTION_ID_MGMT_POLICY_GROUP_DELETE */
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'DeleteDesktopSecurityPolicys');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'DeleteDesktopSecurityIPSets');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'DeletePolicyGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'ModifyDesktopSecurityPolicyAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'ApplyDesktopSecurityPolicy');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'ModifyDesktopSecurityRuleAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'RemoveDesktopSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'AddDesktopSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'ModifyDesktopSecurityIPSetAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'ApplyDesktopSecurityIPSet');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'SetDesktopSecurityPolicyShare');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'ImportDesktopSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'ModifyPolicyGroupAttributes');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'AddResourceToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'RemoveResourceFromPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'AddPolicyToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'RemovePolicyFromPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'ApplyPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'DescribeDesktopSecurityPolicys');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'DescribeDesktopSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'DescribeDesktopSecurityIPSets');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'DescribePolicyGroups');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'ModifyResourceGroupPolicy');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'CreateDesktopSecurityIPSet');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'LoadSystemSecurityRules');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'LoadSystemSecurityIPSets');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('policy-group-3', 'CreateDesktopSecurityPolicy');

/* init guest_shell_command*/
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uaa','shutdown','common_command', 'shutdown /s');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uab','shutdown','common_command', 'shutdown /r');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uac','shutdown','common_command', 'shutdown /l');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uad','shutdown','common_command', 'shutdown /h /f');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uae','shutdown','common_command', 'shutdown /a');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uaf','shutdown','common_command', 'shutdown /s /t 3600');

INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uag','ipconfig','common_command', 'ipconfig /all');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uah','ipconfig','common_command', 'ipconfig /flushdns');

INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uai','task','common_command', 'tasklist');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uaj','task','common_command', 'taskkill /f /im explorer.exe');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uak','task','common_command', 'start explorer.exe');

INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6ual','net','common_command', 'net start');
INSERT INTO guest_shell_command(guest_shell_command_id,guest_shell_command_name,guest_shell_command_type,command) VALUES ('guestcmd-z6ey6uam','systeminfo','common_command', 'systeminfo');

insert into api_limit(api_action,enable,refresh_interval,refresh_time) values('DescribePasswordPromptHaveAnswer',0,60,5);
