/* alter workflow_service_action*/
ALTER TABLE workflow_service_action DROP COLUMN workflow_action;
ALTER TABLE workflow_service_action DROP COLUMN public_params;
ALTER TABLE workflow_service_action DROP COLUMN required_params;
ALTER TABLE workflow_service_action DROP COLUMN extra_params;
ALTER TABLE workflow_service_action DROP COLUMN result_params;
ALTER TABLE workflow_service_action DROP COLUMN describe_params;

ALTER TABLE workflow_service_action ADD COLUMN priority integer DEFAULT 0 NOT NULL;
ALTER TABLE workflow_service_action ADD COLUMN is_head integer DEFAULT 0 NOT NULL;


/* add table workflow_service_action_info*/
CREATE TABLE workflow_service_action_info
(
    api_action varchar(255) PRIMARY KEY NOT NULL,
    action_name text,
    public_params text,
    required_params text,
    extra_params text,
    result_params text
);

/* alter workflow_model*/
ALTER TABLE workflow_model DROP COLUMN head_action;
ALTER TABLE workflow_model DROP COLUMN public_params;

ALTER TABLE workflow_model ADD COLUMN api_actions varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE workflow_model ADD COLUMN env_params text;

/* drop table workflow_model_action*/
drop table workflow_model_action;

/* alter workflow*/
ALTER TABLE workflow ADD COLUMN api_error text;

delete from workflow_service_action;
delete from workflow_service_action_info;

insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('CreateUserAndResource','CreateAuthUser', '创建新用户',0,1);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('CreateUserAndResource','AddAuthUserToUserGroup', '用户添加到用户组',1,0);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('CreateUserAndResource','AddUserToDeliveryGroup', '用户添加到交付组',1,0);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','DeleteAuthUsers', '删除用户',8,8);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','DelUserFromDeliveryGroup', '从交付组移除用户',1,0);
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','RemoveAuthUserFromUserGroup', '从用户组移除用户',1,0);

insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('CreateAuthUser', '创建新用户','["auth_service", "ou_dn"]','["user_name","password"]','["account_control","real_name","email","description"]','["user_id"]');

insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('AddAuthUserToUserGroup', '用户添加到用户组','["auth_service","user_group"]','["user_name"]','','');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('AddUserToDeliveryGroup', '用户添加到交付组','["delivery_group"]','["user_id"]','','');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('DeleteAuthUsers', '删除用户','','["user_id","user_name"]','','');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('DelUserFromDeliveryGroup', '从交付组移除用户','["delivery_group"]','["user_id"]','','');
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('RemoveAuthUserFromUserGroup', '从用户组移除用户','["auth_service","user_group"]','["user_id"]','','');

