from log.logger import logger
import constants as const
import db.constants as dbconst
from utils.json import json_load, json_dump
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
import api.auth.auth_const as AuthConst
WF_ACTION_ACTIVE_AUTH_USERS = "ActiveAuthUsers"
WF_ACTION_DISABLE_AUTH_USERS = "DisableAuthUsers"
from common import (
    filter_out_none
)
import time

from send_request import send_desktop_server_request


class WorkFlowModel(object):
    
    def __init__(self, ctx, workflow_model_id):

        self.ctx = ctx
        self.workflow_model_id = workflow_model_id
        self.workflow_model = None
        self.curr_action = None
        self.curr_action_index = 0
        self.action_list = {}
        self.workflow_enable = 0
        self.env_params = {}
        self.api_action_infos = {}
        self.required_params = []
        self.result_params = []
        self.load_workflow_model()
 
    def load_workflow_model(self):
        
        workflow_model = self.ctx.pgm.get_workflow_model(self.workflow_model_id)
        if not workflow_model:
            return None 
        
        service_type = workflow_model["service_type"]
        api_actions = json_load(workflow_model["api_actions"])
        self.env_params = json_load(workflow_model["env_params"])
        
        workflow_model_actions = self.ctx.pgm.get_workflow_service_action(service_type, api_actions)
        if not workflow_model_actions:
            return None
        
        self.api_action_infos = workflow_model_actions
        
        head_action = None
        priority_actions = {}
        
        for _, api_action in workflow_model_actions.items():
            
            priority = api_action["priority"]
            if str(priority) not in priority_actions:
                priority_actions[str(priority)] = []
            
            is_head = api_action["is_head"]
            if is_head == 1:
                head_action = api_action["api_action"]

            priority_actions[str(priority)].append(api_action["api_action"])
            
            service_action_info = api_action["service_action_info"]
            
            required_params = service_action_info["required_params"]
            for required_param in required_params:
                if required_param in self.required_params:
                    continue
                
                self.required_params.append(required_param)
            
            result_params = service_action_info["result_params"]
            for result_param in result_params:
                if result_param in self.result_params:
                    continue
                
                self.result_params.append(result_param)

        if not head_action:
            return None
        
        if not self.curr_action:
            self.curr_action = head_action
        
        action_list = {}
        for i in range(const.WORKFLOW_PRIORITY_MAX_LEN+1):
            
            if str(i) not in priority_actions:
                continue
            
            _actions = priority_actions[str(i)]
            for _action in _actions:
                action_list[str(len(action_list))] = _action
        
        self.action_list = action_list
        
        self.workflow_enable = 1
    
    def get_current_action(self):
        
        return self.curr_action
    
    def done_current_action(self):
        
        curr_action_index = self.curr_action_index
        logger.info("done_current_action: %s, %s" % (self.curr_action_index, self.action_list))
        next_action_index = curr_action_index + 1
        
        if str(next_action_index) not in self.action_list:
            self.curr_action = None
            return None

        self.curr_action = self.action_list[str(next_action_index)]
        self.curr_action_index = next_action_index

    def check_workflow_action(self):
        
        return True if self.workflow_enable else False
    
    def get_api_action_count(self):
        
        return len(self.action_list)

    def get_workflow_model_params(self):

        return self.env_params

class ResourceWorkflow(WorkFlowModel):

    def __init__(self, ctx, workflow_id, workflow_model_id):
        
        super(ResourceWorkflow, self).__init__(ctx, workflow_model_id)
        
        self.ctx = ctx
        self.workflow_id = workflow_id
        self.workflow = None
        self.workflow_params = {}
        self.api_return = {}
        self.workflow_return = {}
        self.api_error = {}
        self.workflow_result = {}
        self.timeout= 180
        self.action_map = {
            
            # create resource
            const.ACTION_VDI_CREATE_AUTH_USER: self.create_auth_user,
            const.ACTION_VDI_ADD_AUTH_USER_TO_USER_GROUP: self.add_auth_user_to_user_group,
            WF_ACTION_ACTIVE_AUTH_USERS: self.active_auth_users,
            
            # delete resource
            const.ACTION_VDI_DELETE_AUTH_USERS: self.delete_auth_users,
            const.ACTION_VDI_REMOVE_AUTH_USER_FROM_USER_GROUP: self.wf_remove_auth_user_from_user_group,
            const.ACTION_VDI_DELETE_DESKTOPS: self.delete_user_desktop,
            const.ACTION_VDI_DESCRIBE_AUTH_USERS: self.describe_auth_users,
            WF_ACTION_DISABLE_AUTH_USERS: self.disable_auth_users,

            }
        self.init_resource_workflow()


    def init_resource_workflow(self):
        
        workflow = self.ctx.pgm.get_workflow(self.workflow_id)
        if not workflow:
            return None

        self.workflow = workflow
        self.workflow_params = json_load(workflow["workflow_params"])
    
    def set_api_action_error(self, api_action, error):
        
        self.api_error[api_action] = {"code": error.code, "message": error.message}
        update_info = {}
        update_info["api_error"] = json_dump(self.api_error)
        
        if not self.ctx.pg.batch_update(dbconst.TB_WORKFLOW, {self.workflow_id: update_info}):
            logger.error("update workflow api return for [%s] db failed" % (update_info))
            return -1

        return 0

    def get_action_params(self, api_action):
        
        action_info = self.ctx.pgm.get_model_action_info(api_action)
        if not action_info:
            logger.error("no found action params %s" % api_action)
            return None
        
        required_params = []
        if action_info["required_params"]:
            required_params = json_load(action_info["required_params"])
        
        extra_params = []
        if action_info["extra_params"]:
            extra_params = json_load(action_info["extra_params"])

        public_params = []
        if action_info["public_params"]:
            public_params = json_load(action_info["public_params"])
        
        action_params = {}
        workflow_params = self.workflow_params

        for required_param in required_params:
            if required_param not in workflow_params or not workflow_params[required_param]:
                error = Error(ErrorCodes.WF_API_ACTION_PARAMS_ERROR,
                              ErrorMsg.ERROR_MSG_WF_API_ACTION_PARAM_NO_FOUND, (api_action, required_param))
                
                self.set_api_action_error(api_action, error)
                logger.error("get action required params error %s, %s" % (required_param, api_action))
                return None

            action_params[required_param] = workflow_params[required_param]
        for extra_param in extra_params:
            if extra_param in workflow_params:
                action_params[extra_param] = workflow_params[extra_param]
        for public_param in public_params:
            if public_param not in self.env_params or not self.env_params[public_param]:
                error = Error(ErrorCodes.WF_API_ACTION_PARAMS_ERROR,
                              ErrorMsg.ERROR_MSG_WF_API_ACTION_PARAM_NO_FOUND, (api_action, public_param))
                logger.error("public_param %s" % public_param)
                self.set_api_action_error(api_action, error)
                logger.error("get action public params error %s" % api_action)
                return None
            
            action_params[public_param] = self.env_params[public_param]
        
        return action_params
  
    def set_workflow_status(self, workflow_id, api_action, transition_status=None, status=None):
       
        update_info = {}
        
        if not status:
            update_info["transition_status"] = transition_status
        else:
            update_info["transition_status"] = ""
            update_info["status"] = status
        
        update_info["curr_action"] = api_action
        
        if not self.ctx.pg.batch_update(dbconst.TB_WORKFLOW, {workflow_id: update_info}):
            logger.error("update newly workflow status for [%s] db failed" % (update_info))
            return -1
    
        return 0
      
    def set_api_action_result(self, action, result):
        
        update_info = {}

        if not self.workflow_return:
            self.workflow_return = {}

        self.workflow_return[action] = result
        update_info["api_return"] = json_dump(self.workflow_return)
        
        if not self.ctx.pg.batch_update(dbconst.TB_WORKFLOW, {self.workflow_id: update_info}):
            logger.error("update workflow return for [%s] db failed" % (update_info))
            return -1
    
        return 0

    def set_workflow_params(self, result):
        
        if not result:
            return None
        
        update_workflow_params = 0
        for required_param in self.required_params:
            if required_param not in result:
                continue
            
            if required_param not in self.workflow_params:
                self.workflow_params[required_param] = result[required_param]
                update_workflow_params = 1
                continue
            
            if self.workflow_params[required_param] != result[required_param]:
                self.workflow_params[required_param] = result[required_param]
                update_workflow_params = 1
                continue
        
        if not update_workflow_params:
            return 0
        
        update_info = {"workflow_params": json_dump(self.workflow_params)}
        
        if not self.ctx.pg.batch_update(dbconst.TB_WORKFLOW, {self.workflow_id: update_info}):
            logger.error("update workflow return for [%s] db failed" % (update_info))
            return -1

        return 0

    def set_workflow_result(self, result):
        
        if not result:
            return None

        for result_param in self.result_params:
            if result_param not in result:
                continue
            
            self.workflow_result[result_param] = result[result_param]
            
        update_info = {"result": json_dump(self.workflow_result)}
        
        if not self.ctx.pg.batch_update(dbconst.TB_WORKFLOW, {self.workflow_id: update_info}):
            logger.error("update workflow return for [%s] db failed" % (update_info))
            return -1

        return 0

    def is_conn_error(self, action, ret):

        if not ret:
            logger.error("API ACTION %s error" % action)
            return True
    
        if ret["ret_code"] != 0:
            logger.error(ret)
            return True

        return False
    
    def handle_resource_workflow(self, sender, curr_action):
        
        zone =  sender["zone"]
        sender = {"zone": zone, "console": const.USER_CONSOLE_ADMIN, "owner": const.GLOBAL_ADMIN_USER_NAME}
        
        action_params = self.get_action_params(curr_action) 
        if not action_params:
            return -1
        
        result = self.action_map[curr_action](sender, curr_action, action_params)
        if result == -1:
            error = Error(ErrorCodes.WF_API_ACTION_PARAMS_ERROR,
                              ErrorMsg.ERROR_MSG_WF_API_ACTION_HANDLE_PARAM_NO_FOUND, (curr_action))
            self.set_api_action_error(curr_action, error)
            return -1
        
        self.set_workflow_result(result)
        self.set_workflow_params(result)
        self.set_api_action_result(curr_action, result)

        return 0

    def check_existed_auth_user(self, sender, auth_service_id,user_name, action):
        
        ret = self.get_workflow_auth_user(sender, auth_service_id,action, user_name)
        
        if ret == -1:
            logger.error("workflow auth user %s" % ret)
            return -1

        auth_user = ret
        if not auth_user:
            return None
        
        user_id = auth_user["user_id"]
        if not user_id:
            return -1
        # check user status
        status = auth_user["status"]
        if status != const.USER_STATUS_ACTIVE:
            ret = self.remove_auth_user_from_user_group(sender,auth_service_id,auth_user)           
            ret = self.active_auth_users(sender,auth_service_id,action, auth_user)
            if ret < 0:
                return -1
        return auth_user

    def check_existed_auth_ou(self, zone, auth_service_id,base_dn,ou_name, action):

        if not isinstance(ou_name, list):
            ou_names = [ou_name]
        ret = self.resource_describe_auth_ous(zone, auth_service_id,base_dn, ou_names,1, 0)
        if self.is_conn_error(action, ret):
            return -1
        auth_ou_set = ret.get("auth_ou_set")
        if not auth_ou_set or len(auth_ou_set)==0:
            return None
        if len(auth_ou_set) > 1:
            return -1
        return auth_ou_set[0]

    def get_workflow_auth_user(self, sender, auth_service_id,action, user_name):
        
        ret = self.resource_describe_server_auth_users(sender["zone"], auth_service_id,user_name)
        if self.is_conn_error(action, ret):
            return -1

        auth_user_set = ret.get("auth_user_set")
        if not auth_user_set:
            return None
        if len(auth_user_set) > 1:
            return -1

        return auth_user_set[0]
    
    
    def describe_auth_users(self, sender, action, param):
        
        user_name = param.get("user_name")
        if not user_name:
            return -1
        auth_service_id = param["auth_service"]  
        ret = self.get_workflow_auth_user(sender,auth_service_id, action, user_name)
        if ret == -1 or not ret:
            logger.error("workflow auth user %s" % ret)
            return -1   
        
        auth_user = ret
        result = {"user_id": auth_user["user_id"],"user_name":user_name}
        return result
        
    # handle new user
    def active_auth_users(self, sender,auth_service_id, action,auth_user):
        
        if auth_user["status"] == const.USER_STATUS_ACTIVE:
            return 0
        
        status = 1
        user_name = auth_user["user_name"]       
        
        ret = self.resource_set_auth_user_status(sender["zone"], auth_service_id,user_name, status)
        if self.is_conn_error(action, ret):
            return -1

        ret = self.get_workflow_auth_user(sender,auth_service_id, action, user_name)
        if ret == -1 or not ret:
            logger.error("workflow auth user %s" % ret)
            return -1      
        
        auth_user = ret
        if auth_user["status"] != const.USER_STATUS_ACTIVE:
            return -1
        return 0

    # handle new user
    def wf_remove_auth_user_from_user_group(self,sender, action, params):
        auth_service_id = params.get("auth_service")
        user_groups = params.get("user_groups")
        if user_groups and not isinstance(user_groups, list):                   
            logger.error("action remove user to user group not list")
            return -1

        auth_user={}
        auth_user["user_name"] = params["user_name"]
        auth_user["user_groups"] = params["user_groups"]
        ret = self.remove_auth_user_from_user_group(sender,auth_service_id, auth_user)       
        result = auth_user
        return result

    def remove_auth_user_from_user_group(self, sender,auth_service_id,auth_user):
        user_name = auth_user["user_name"]           
        user_groups = auth_user.get("user_groups")
        if user_groups:
            user_group_ids = []
            for group in user_groups:
                _id = group["user_group_id"]
                user_group_ids.append(_id)
            ret = self.ctx.pgm.get_desktop_user_groups(user_group_ids=user_group_ids, index_dn=True)
            if ret:
                user_group_dns = ret.keys()
                for _user_group_dn in user_group_dns:
                    ret = self.resource_remove_auth_user_from_user_group(sender["zone"],auth_service_id, _user_group_dn, user_name)
                    if not ret:
                        continue
  
    def disable_auth_users(self,sender, action, params):
        
        user_id = params["user_id"]
        ret = self.ctx.pgm.get_desktop_users(user_id)
        if not ret:
            return -1        
        auth_user = ret[user_id]
        
        if auth_user["status"] == const.USER_STATUS_DISABLED:
            return 0
        
        status = 0
        user_name = auth_user["user_name"]  
        auth_service_id = params["auth_service"]      
        ret = self.resource_set_auth_user_status(sender["zone"],auth_service_id, user_name, status)
        if self.is_conn_error(action, ret):
            return -1

        ret = self.get_workflow_auth_user(sender,auth_service_id, action, user_name)
        if ret == -1 or not ret:
            logger.error("workflow auth user %s" % ret)
            return -1   
        auth_user = ret
        if auth_user["status"] != const.USER_STATUS_DISABLED:
            return -1
        if "user_groups" not in self.env_params:
            self.remove_auth_user_from_user_group(sender,auth_service_id,auth_user)
        
        result = {"user_id": user_id,"user_name":user_name}
        return result


    def create_auth_user(self, sender, action, params):
        user_name = params["user_name"]
        password = params["password"]
        ou_name = params["ou_dn"]
        auth_user = {}
        if "account_control" not in params:
            params["account_control"] = 0
            
        auth_service_id = params["auth_service"]  
        if not auth_service_id:
            return -1
        ret = self.check_existed_auth_user(sender, auth_service_id,user_name, action)

        
        if ret == -1:
            return -1
        if ret:
            auth_user = ret
       
        if not auth_user:
            
            auth_service = self.ctx.pgm.get_auth_service(auth_service_id)
            
            if not auth_service:
                return -1   
            else:
                base_dn=auth_service["base_dn"]  
                
            base_dn="ou=%s,%s" % (AuthConst.PMS_USER_BASE_DN,base_dn)
            ret = self.check_existed_auth_ou(sender["zone"],auth_service_id, base_dn, ou_name = ou_name,action = action)
            if ret == -1:
                return -1            
            if not ret:
                logger.info(" auth ou not exist %s" % ret)
                ret = self.resource_create_auth_ou(sender["zone"], auth_service_id,base_dn,ou_name)
                if not ret:
                    logger.error("create auth ou%s" % ret)
                    return -1          
            ou_dn="ou=%s,%s" % (ou_name,base_dn)
            params["ou_dn"] = ou_dn
            ret = self.resource_create_auth_user(sender["zone"], auth_service_id,params)
            if not ret:
                logger.error("create auth %s" % ret)
                return -1

            auth_user = ret        
            user_id = auth_user["user_id"]
            if not user_id:
                return -1
        else:
            user_id = auth_user["user_id"]
            if not user_id:
                return -1            
            ret = self.resource_reset_auth_user_password(sender["zone"],auth_service_id, user_name, password)
            if not ret:
                return -1

        result = {"user_id": user_id,"user_name":user_name}
        return result


    def add_auth_user_to_user_group(self, sender, action, params):

        user_group_id = params.get("user_group")
        auth_service_id = params.get("auth_service")
        if not user_group_id:
            logger.error("action add user to user group no found id")
            return -1
        
        user_group = self.ctx.pgm.get_desktop_user_group(user_group_id)
        if not user_group:
            logger.error("no found user group %s" % user_group_id)
            return -1
        user_group_dn = user_group["user_group_dn"]
        user_name = params["user_name"]
        
        ret = self.resource_add_auth_user_to_user_group(sender["zone"],auth_service_id, user_group_dn, user_name)
        if self.is_conn_error(action, ret):
            return -1
        result = {"user_group_dn": user_group_dn,"user_name":user_name}
        return result

    def delete_auth_users(self, sender, action, params):
        
        zone_auth = self.ctx.pgm.get_auth_zone(sender["zone"])
        if not zone_auth:
            return -1
        auth_service_id = zone_auth["auth_service_id"]
        user_name = params["user_name"]
        ret = self.resource_describe_server_auth_users(sender["zone"], auth_service_id,user_name)
        if self.is_conn_error(action, ret):
            return -1
        
        auth_user_set = ret.get("auth_user_set")
        if not auth_user_set:
            return 0

        auth_user = auth_user_set[0]
        user_id = auth_user["user_id"]
        ret = self.resource_delete_auth_users(sender["zone"],auth_service_id, user_name)
        if self.is_conn_error(action, ret):
            return -1
        
        result = {"user_id": user_id,"user_name":user_name}
        return result
    
    def delete_user_desktop(self, sender, action, params):
        user_id = params.get("user_id")
        desktop_names={}
        user_desktops = self.ctx.pgm.get_resource_by_user(user_id, resource_type=dbconst.RESTYPE_DESKTOP)
        if not user_desktops:
            result = {"desktops":desktop_names}
            self.set_workflow_result(result)
            return 0  
        desktop_ids = user_desktops.get(user_id, [])

        desktops = self.ctx.pgm.get_desktops(desktop_ids)
        logger.error("desktops.[%s]" % desktops)
        if not desktops:
            result = {"desktops":desktop_names}
            self.set_workflow_result(result)
            return 0  
        desktop_ids=[]     
        detach_desktop={}
        desktop_names={}
        if "user_groups" in self.env_params:
            user_groups=self.env_params["user_groups"]
            if user_groups:
                user_group_ids = []
                for group in user_groups:
                    _id = group["user_group_id"]
                    user_group_ids.append(_id)            
            ret = self.ctx.pgm.get_delivery_group_by_user(user_group_ids)
            if ret:
                delivery_group_ids = ret
                logger.error("delivery_group_ids.[%s]" % delivery_group_ids)
                for delivery_group_id in delivery_group_ids:
                    for _,desktop in desktops.items():
                        logger.error("desktop.[%s]" % desktop)
                        logger.error("delivery_group_id.[%s]" % delivery_group_id)
                        logger.error("desktop delivery_group_id.[%s]" % desktop["delivery_group_id"])
                        if desktop["delivery_group_id"] == delivery_group_id:
                            desktop_id=desktop["desktop_id"]
                            desktop_ids.append(desktop_id)
                            desktop_names[desktop_id]=desktop["hostname"]
        else:
            desktop_ids = desktops.keys()   
            desktop_names=self.ctx.pgm.get_desktop_name(desktop_ids)
        if not desktop_ids:
            result = {"desktops":desktop_names}
            self.set_workflow_result(result)
            return 0  
        params["desktops"] = desktop_ids        
        result = {"desktops":desktop_names}        
        ret = self.resource_delete_desktop_from_delivery_group(sender["zone"],params)   
        if self.is_conn_error(action, ret):
            self.set_workflow_result(result)
            return -1         
        
        if user_id and not isinstance(user_id, list):
            user_id = [user_id]        
        for desktop_id in desktop_ids:
            detach_desktop["desktop"] = desktop_id
            detach_desktop["user_ids"] = user_id
            ret = self.resource_detach_desktop_from_delivery_group_user(sender["zone"],detach_desktop)          

        ret = self.resource_delete_desktops(sender["zone"], params)  
        if self.is_conn_error(action, ret):
            self.set_workflow_result(result)
            return -1
        
        job_id=ret.get("job_id",'')
        if job_id:            
            ret = self.wait_desktop_job(sender["zone"], job_id)        
            if ret==-1:
                self.set_workflow_result(result)
                return -1
        else:
            self.set_workflow_result(result)
            return -1  

        self.workflow_return = result
        return 0


    def wait_desktop_job(self,zone,job_id,  timeout=1800, interval=10):
        ''' wait desktop server job '''
        end_time = time.time() + timeout
    
        while time.time() < end_time:
    
            req = {
            "type":"internal",
            "params":{"action": const.ACTION_VDI_DESCRIBE_DESKTOP_JOBS,
                      "jobs": [job_id],
                      "zone": zone
                    },
            }
            ret = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
            if ret.get("ret_code", -1) != 0:
                logger.error("wait job timeout.[%s][%s]" % (ret, job_id))
                return -1
    
            job_set = ret["desktop_job_set"]
            if not job_set:
                logger.error("describe jobs none.[%s][%s]" % (ret, job_id))
                return -1
    
            job = job_set[0]
            status = job["status"]
    
            if status in [const.JOB_STATUS_PEND, const.JOB_STATUS_WORKING]:
                time.sleep(interval)
                continue
            if status in [const.JOB_STATUS_SUCC]:
                return 0
            else:
                logger.error("jobs status fail.[%s][%s]" % (status, job_id))
                return -1   
        return -1



    def resource_delete_desktop_from_delivery_group(self, zone,params):

        req = {"type":"internal",
               "params":{"action": const.ACTION_VDI_DEL_DESKTOP_FROM_DELIVERY_GROUP,
                         "desktops": params["desktops"] ,
                         "zone": zone
                         },
               }
    
        # send request
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        return rep

    def resource_detach_desktop_from_delivery_group_user(self, zone,detach_desktop):

        req = {"type":"internal",
               "params":{"action": const.ACTION_VDI_DETACH_DESKTOP_FROM_DELIVERY_GROUP_USER,
                         "desktop": detach_desktop["desktop"],
                         "user_ids":detach_desktop["user_ids"],
                         "zone": zone
                         },
               }
    
        # send request
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        return rep

    def resource_delete_desktops(self, zone,params):

        req = {"type":"internal",
               "params":{"action": const.ACTION_VDI_DELETE_DESKTOPS,
                         "desktops": params["desktops"] ,
                         "zone": zone
                         },
               }
    
        # send request
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        return rep



    def resource_delete_auth_users(self, zone,auth_service_id,user_name):

        if not isinstance(user_name, list):
            user_names = [user_name]
        req = {"type":"internal",
               "params":{"action": const.ACTION_VDI_DELETE_AUTH_USERS,
                         "user_names": user_names,
                         "zone": zone,
                         "auth_service":auth_service_id
                         },
               }
    
        # send request
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        return rep


    def resource_set_auth_user_status(self, zone,auth_service_id,user_names,status):

        if not isinstance(user_names, list):
            user_names = [user_names]
        req = {"type":"internal",
               "params":{"action": const.ACTION_VDI_SET_AUTH_USER_STATUS,
                         "user_names": user_names,
                         "zone": zone,
                         "auth_service":auth_service_id,
                         "status":status
                         },
               }
    
        # send request
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        return rep

    def resource_describe_server_auth_users(self, zone,auth_service_id,user_name,global_search=1,scope=1):
        if user_name and not isinstance(user_name, list):
            user_names = [user_name]
  
        # send request
        req = {"type":"internal",
               "params":{"action": const.ACTION_VDI_DESCRIBE_AUTH_USERS,
                         "user_names": user_names,
                         "zone": zone,
                         "auth_service":auth_service_id,
                         "global_search":global_search,
                         "scope":scope
                         },
               }
    
        # send request 
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        return rep

    def resource_describe_auth_ous(self, zone,auth_service_id,base_dn,ou_names,scope=1,syn_desktop=0):
        # send request
        if ou_names and not isinstance(ou_names, list):
            ou_names = [ou_names]
        req = {"type":"internal",
               "params":{"action": const.ACTION_VDI_DESCRIBE_AUTH_OUS,
                         "ou_names": ou_names,
                         "zone": zone,
                         "auth_service":auth_service_id,
                         "base_dn":base_dn,
                         "syn_desktop":syn_desktop,
                         "scope":scope
                         },
               }
    
        # send request
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        return rep

    def resource_create_auth_ou(self, zone,auth_service_id,base_dn,ou_name):
        # send request
        action =  const.ACTION_VDI_CREATE_AUTH_OU 
        req = {"type":"internal",
               "params":{"action": action,
                         "ou_name": ou_name,
                         "zone": zone,
                         "auth_service":auth_service_id,
                         "base_dn":base_dn
                         },
               }
    
        # send request
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        if not rep:
            logger.error("API ACTION %s is none error " % action)
            return None
    
        if rep["ret_code"] != 0 and rep["ret_code"] != ErrorCodes.RESOURCE_ALREADY_EXISTED:  
            logger.error("API ACTION %s is error % " % (action,rep))          
            return None
         
        return rep

    def resource_create_auth_user(self, zone,auth_service_id,user_info):
        # send request

        valid_keys = ['user_name', 'password', "base_dn", "account_control", "real_name", "email", "description", "auth_service",
                      'position', 'title', 'personal_phone', 'company_phone']
        params = filter_out_none(user_info, valid_keys)  
        action =  const.ACTION_VDI_CREATE_AUTH_USER 
        params["action"]=  action
        if "ou_dn" in user_info:
            params["base_dn"] = user_info["ou_dn"]        
        params["zone"]=  zone
        params["auth_service"]=  auth_service_id
        req={}
        req["type"] = "internal"
        req["params"] = params
        # send request
        ret = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        if not ret:
            logger.error("API ACTION %s is none error " % action)
            return None
        if ret["ret_code"] == ErrorCodes.RESOURCE_ALREADY_EXISTED:
            logger.error("API ACTION %s is exist  " % params["user_name"])
            ret = self.resource_describe_server_auth_users(zone,auth_service_id,params["user_name"],global_search=1,scope=1)         
            if not ret or ret["ret_code"] != 0:
                return None
            auth_user_set = ret.get("auth_user_set")
            if not auth_user_set or len(auth_user_set) !=1:
                return None          
            return auth_user_set[0]        
        if not ret or ret["ret_code"] != 0 :  
            logger.error("API ACTION %s is error %s " % (action,ret))          
            return None        
        return ret 

    def resource_add_auth_user_to_user_group(self, zone,auth_service_id,user_group_dn,user_names):
        if user_names and not isinstance(user_names, list):
            user_names = [user_names]
  
        # send request
        req = {"type":"internal",
               "params":{"action": const.ACTION_VDI_ADD_AUTH_USER_TO_USER_GROUP,
                         "user_names": user_names,
                         "zone": zone,
                         "auth_service":auth_service_id,
                         "user_group_dn":user_group_dn
                         },
               }
    
        # send request
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        return rep

    def resource_reset_auth_user_password(self, zone,auth_service_id,user_name,password):
        action = const.ACTION_VDI_RESET_AUTH_USER_PASSWORD
        req = {"type":"internal",
               "params":{"action": action,
                         "user_name": user_name,
                         "zone": zone,
                         "auth_service":auth_service_id,
                         "password":password
                         },
               }
    
        # send request
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        if self.is_conn_error(action, rep):
            return None           
        return rep



    def resource_remove_auth_user_from_user_group(self, zone,auth_service_id,user_group_dn,user_names):   
        if user_names and not isinstance(user_names, list):
            user_names = [user_names]
        action = const.ACTION_VDI_REMOVE_AUTH_USER_FROM_USER_GROUP
        # send request
        req = {"type":"internal",
               "params":{"action": action,
                         "zone": zone,
                         "auth_service":auth_service_id,
                         "user_group_dn":user_group_dn,
                         "user_names":user_names
                         },
               }
    
        # send request
        rep = send_desktop_server_request(req,need_reply=True,timeout = self.timeout)
        if self.is_conn_error(action, rep):
            return None     
        return rep         

