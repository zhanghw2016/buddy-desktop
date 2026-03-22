INSERT INTO module_custom_config (module_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_module_custom','CitrixPolicy','support_citrix_policy','0',1);


CREATE TABLE workflow_config
(
    workflow_config_id varchar(50) PRIMARY KEY NOT NULL,
    workflow_model_id varchar(50) NOT NULL,
    request_type varchar(255) DEFAULT '' NOT NULL,
    ou_dn text,
    request_action varchar(255) DEFAULT '' NOT NULL,
    status integer DEFAULT 1 NOT NULL
);

delete from workflow_service_action;
delete from workflow_service_action_info;


insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('CreateUserAndResource','CreateAuthUser', '创建新用户',0,1);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('CreateUserAndResource','AddAuthUserToUserGroup', '用户添加到用户组',1,0);

insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','DeleteAuthUsers', '删除用户',8,8);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','DeleteDesktops', '删除桌面',7,0);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','DescribeAuthUsers', '查询用户',0,1);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','DisableAuthUsers', '禁用用户',8,8);

insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('CreateAuthUser', '创建新用户','["auth_service", "ou_dn"]','["user_name","password"]','["account_control","real_name","email","description"]','["user_id"]');

insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('AddAuthUserToUserGroup', '用户添加到用户组','["auth_service","user_group"]','["user_name"]','','');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('DeleteAuthUsers', '删除用户','','["user_id","user_name"]','','');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('DescribeAuthUsers', '查询用户','["auth_service"]','["user_name"]','','["user_id"]');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('DisableAuthUsers', '禁用用户','["auth_service"]','["user_id"]','','');

