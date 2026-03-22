import context
from log.logger import logger
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
import resource_control.policy.citrix_policy as CitrixPolicy
from common import (
    return_error,
    return_success,
    return_items,
    is_admin_user,
    is_admin_console,
    build_filter_conditions,
    get_sort_key,
    get_reverse
    )

from db.constants import TB_USB_POLICY, PUBLIC_COLUMNS, DEFAULT_LIMIT
from utils.json import json_load
import resource_control.desktop.resource_permission as ResCheck
def handle_create_citrix_policy(req):
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ["citrix_policy_name","policy_state"])
    if isinstance(ret, Error):
        return return_error(req, ret)
        
    citrix_policy={}
    citrix_policy["citrix_policy_name"]=req.get("citrix_policy_name")
    citrix_policy["description"]=req.get("description")
    citrix_policy["policy_state"]=req.get("policy_state")

    if not citrix_policy :
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE, 
                                       ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE,("citrix_policy_name")))
    ret = CitrixPolicy.check_citrix_policy_name(sender["zone"], citrix_policy["citrix_policy_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    citrix_policy_ret = CitrixPolicy.create_citrix_policy(sender ,citrix_policy)
    if isinstance(citrix_policy_ret, Error):
        return return_error(req, citrix_policy_ret)
    return return_success(req, {'citrix_policy': citrix_policy_ret})



def handle_describe_citrix_policy(req):
    sender = req["sender"]
    citrix_policy_names=req.get("citrix_policy_names")
    search_word=req.get("search_word")
    citrix_policy_set = CitrixPolicy.describe_citrix_policy(sender,citrix_policy_names,search_word)
    if citrix_policy_set:
        count=len(citrix_policy_set)
    else:
        count=0    
    ret = {'citrix_policy_set': citrix_policy_set,'total_count':count}
    return return_success(req, None, **ret)    

def handle_delete_citrix_policy(req):
    ret = ResCheck.check_request_param(req, ["citrix_policy_id","citrix_policy_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    sender = req["sender"]
    citrix_policy_id=req.get("citrix_policy_id")
    citrix_policy_name=req.get("citrix_policy_name")
    ret = CitrixPolicy.delete_citrix_policy(sender ,citrix_policy_id,citrix_policy_name)
    if isinstance(ret, Error):
        return return_error(req, ret)

    return return_success(req, {'citrix_policy_id': citrix_policy_id})

def handle_modify_citrix_policy(req):
    ret = ResCheck.check_request_param(req, ["citrix_policy_id","citrix_policy_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    sender = req["sender"]    
    citrix_policy={}
    citrix_policy["citrix_policy_name"]=req.get("citrix_policy_name")
    citrix_policy["description"]=req.get("description")
    citrix_policy["policy_state"]=req.get("policy_state")
    citrix_policy_id=req.get("citrix_policy_id")
    ret = CitrixPolicy.modify_citrix_policy(sender ,citrix_policy_id,citrix_policy)
    if isinstance(ret, Error):
        return return_error(req, ret)
    return return_success(req, {'citrix_policy_name': citrix_policy["citrix_policy_name"]})          

def handle_rename_citrix_policy(req):
    ret = ResCheck.check_request_param(req, ["citrix_policy_id","citrix_policy_old_name","citrix_policy_new_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    sender = req["sender"]    
    citrix_policy={}
    citrix_policy["citrix_policy_old_name"]=req.get("citrix_policy_old_name")
    citrix_policy["citrix_policy_new_name"]=req.get("citrix_policy_new_name")
    citrix_policy_id=req.get("citrix_policy_id")
    ret = CitrixPolicy.rename_citrix_policy(sender ,citrix_policy_id,citrix_policy)
    if isinstance(ret, Error):
        return return_error(req, ret)
    return return_success(req, {'citrix_policy_id': citrix_policy_id})  

def handle_refresh_citrix_policy(req):
    
    sender = req["sender"]
    sync_type = req["sync_type"]
    citrix_policy_id=req.get("citrix_policy_id","")
    citrix_policy_name=req.get("citrix_policy_name","")     
    if sync_type == "policy":    
        ret = CitrixPolicy.refresh_citrix_policy(sender)
        if isinstance(ret, Error):
            return return_error(req, ret)
    elif sync_type == "policy_item":      
        ret = CitrixPolicy.refresh_citrix_policy_item(sender,citrix_policy_id,citrix_policy_name)
        if isinstance(ret, Error):
            return return_error(req, ret)
    elif sync_type == "policy_filter":
        ret = CitrixPolicy.refresh_citrix_policy_filter(sender,citrix_policy_id,citrix_policy_name)
        if isinstance(ret, Error):
            return return_error(req, ret)    
    return return_success(req, None)


def handle_set_citrix_policy_priority(req):
    ret = ResCheck.check_request_param(req, ["citrix_policy_id","citrix_policy_name","policy_priority"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    sender = req["sender"]    
    citrix_policy_name=req.get("citrix_policy_name")
    policy_priority=req.get("policy_priority")
    ret = CitrixPolicy.set_citrix_policy_priority(sender ,citrix_policy_name,policy_priority)
    if isinstance(ret, Error):
        return return_error(req, ret)
    return return_success(req, {'citrix_policy_name': citrix_policy_name})  


def handle_describe_citrix_policy_item(req):
    ret = ResCheck.check_request_param(req, ["citrix_policy_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    sender = req["sender"]
    citrix_policy_id=req.get("citrix_policy_id")
    citrix_policy_items = CitrixPolicy.describe_citrix_policy_item(sender,citrix_policy_id)
    if citrix_policy_items:
        count=len(citrix_policy_items)
    else:
        count=0
    ret = {'citrix_policy_items': citrix_policy_items,'total_count':count}
    return return_success(req, None, **ret)  

def handle_config_citrix_policy_item(req):
    ret = ResCheck.check_request_param(req, ["citrix_policy_name","policy_items","citrix_policy_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    policy_items = json_load(req["policy_items"])
    sender = req["sender"]
    citrix_policy_name=req.get("citrix_policy_name")
    citrix_policy_id=req.get("citrix_policy_id")
    ret= CitrixPolicy.config_citrix_policy_item(sender ,citrix_policy_name,citrix_policy_id, policy_items)
    if isinstance(ret, Error):
        return return_error(req, ret)  
    citrix_policy_item_ret,citrix_policy_item_error_set  =ret    
    return return_success(req, {'citrix_policy_item': citrix_policy_item_ret,'citrix_policy_item_error_set':citrix_policy_item_error_set})

def handle_describe_citrix_policy_item_config(req):
    ret = ResCheck.check_request_param(req, ["pol_id"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    sender = req.get("sender")
    col1=req.get("col1")
    col2=req.get("col2")
    col3=req.get("col3")
    search_word=req.get("search_word")
    pol_id=req.get("pol_id")
    citrix_policy_item_config = CitrixPolicy.describe_citrix_policy_item_config(sender,col1,col2,col3,search_word,pol_id )
    return return_success(req, citrix_policy_item_config)

def handle_describe_citrix_policy_filter(req):
    ret = ResCheck.check_request_param(req, ["citrix_policy_id","citrix_policy_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    
    sender = req["sender"]    
    citrix_policy_id=req.get("citrix_policy_id")
    ret = CitrixPolicy.describe_citrix_policy_filter(sender ,citrix_policy_id)
    if isinstance(ret, Error):
        return return_error(req, ret)
    return return_success(req, {'pol_filter_set': ret}) 

def handle_add_citrix_policy_filter(req):
    ret = ResCheck.check_request_param(req, ["citrix_policy_id","citrix_policy_name","policy_filters"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    policy_filters = json_load(req["policy_filters"])
    sender = req["sender"]
    citrix_policy_name=req.get("citrix_policy_name")
    citrix_policy_id=req.get("citrix_policy_id")
    ret= CitrixPolicy.add_citrix_policy_filter(sender ,citrix_policy_id, citrix_policy_name,policy_filters)
    if isinstance(ret, Error):
        return return_error(req, ret)
    citrix_policy_filter_set,citrix_policy_filter_error_set  =ret  
    citrix_policy_filter={}
    citrix_policy_filter["citrix_policy_id"] =  citrix_policy_id
    citrix_policy_filter["citrix_policy_filter_set"] =  citrix_policy_filter_set
    citrix_policy_filter["citrix_policy_filter_error_set"] =  citrix_policy_filter_error_set
    return return_success(req, {'citrix_policy_filter': citrix_policy_filter})

def handle_modify_citrix_policy_filter(req):
    ret = ResCheck.check_request_param(req, ["citrix_policy_id","citrix_policy_name","policy_filters"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    policy_filters = json_load(req["policy_filters"])
    sender = req["sender"]
    citrix_policy_name=req.get("citrix_policy_name")
    citrix_policy_id=req.get("citrix_policy_id")
    ret= CitrixPolicy.modify_citrix_policy_filter(sender ,citrix_policy_id, citrix_policy_name,policy_filters)
    if isinstance(ret, Error):
        return return_error(req, ret)
    citrix_policy_filter_set,citrix_policy_filter_error_set  =ret  
    citrix_policy_filter={}
    citrix_policy_filter["citrix_policy_id"] =  citrix_policy_id
    citrix_policy_filter["citrix_policy_filter_set"] =  citrix_policy_filter_set
    citrix_policy_filter["citrix_policy_filter_error_set"] =  citrix_policy_filter_error_set
    return return_success(req, {'citrix_policy_filter': citrix_policy_filter})

def handle_delete_citrix_policy_filter(req):
    ret = ResCheck.check_request_param(req, ["citrix_policy_id","citrix_policy_name","policy_filters"])
    if isinstance(ret, Error):
        return return_error(req, ret)
    sender = req["sender"]
    policy_filters = json_load(req["policy_filters"])
    citrix_policy_name=req.get("citrix_policy_name")
    ret= CitrixPolicy.delete_citrix_policy_filter(sender , citrix_policy_name,policy_filters,True)
    if isinstance(ret, Error):
        return return_error(req, ret)
    citrix_policy_filter_set,citrix_policy_filter_error_set  =ret  
    citrix_policy_filter={}
    citrix_policy_filter["citrix_policy_name"] =  citrix_policy_name
    citrix_policy_filter["citrix_policy_filter_set"] =  citrix_policy_filter_set
    citrix_policy_filter["citrix_policy_filter_error_set"] =  citrix_policy_filter_error_set
    return return_success(req, {'citrix_policy_filter': citrix_policy_filter})

