insert into workflow_service_action_info(api_action,action_name,public_params,required_params,extra_params,result_params) values('RemoveAuthUserFromUserGroup', '指定用户组删除用户','["auth_service","user_groups"]','["user_name"]','','');
UPDATE workflow_service_action SET priority = 6 where api_action= 'DeleteDesktops' ;
insert into workflow_service_action(service_type,api_action,action_name,priority,is_head) values('DeleteUserAndResource','RemoveAuthUserFromUserGroup', '指定用户组删除用户',7,0);
