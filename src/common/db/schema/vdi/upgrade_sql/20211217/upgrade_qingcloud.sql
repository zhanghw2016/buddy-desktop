delete from workflow_service_action_info where api_action='CreateAuthUser';
insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('CreateAuthUser', '创建新用户','["auth_service"]','["user_name","password", "ou_dn"]','["account_control","real_name","email","description"]','["user_id"]');
