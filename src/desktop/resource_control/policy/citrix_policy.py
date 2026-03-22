import context
from log.logger import logger
from utils.misc import get_current_time
from db.constants import TB_USB_POLICY, PUBLIC_COLUMNS
from utils.id_tool import UUID_TYPE_CITRIX_POLICY,UUID_TYPE_POLICY_ITEM, UUID_TYPE_POLICY_FILTER,get_uuid
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
from db.data_types import SearchWordType
from db.constants  import (
    TB_CITRIX_POLICY,
    TB_CITRIX_POLICY_ITEM_CONFIG,
    TB_CITRIX_POLICY_ITEM,
    TB_CITRIX_POLICY_FILTER,
)
import db.constants as dbconst

def create_citrix_policy(sender,citrix_policy):
    ctx = context.instance()
    ret = ctx.res.resource_create_citrix_policy(sender["zone"], citrix_policy)
    if not ret:
        logger.error("ddc create citrix_policy_name %s fail" % citrix_policy["citrix_policy_name"])
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    citrix_policy_id = get_uuid(UUID_TYPE_CITRIX_POLICY, ctx.checker)         
    citrix_policy_info = dict(
                              pol_id = citrix_policy_id,
                              policy_name = citrix_policy["citrix_policy_name"],
                              pol_priority = ret["pol_priority"],
                              com_priority = ret["com_priority"],
                              user_priority = ret["user_priority"],
                              description = citrix_policy["description"] if citrix_policy["description"] else '',
                              create_time = get_current_time(),
                              update_time = get_current_time(),
                              pol_state=citrix_policy["policy_state"] if citrix_policy["policy_state"] else 0,
                              zone = sender["zone"]                                  
                              )
    if not ctx.pg.insert(dbconst.TB_CITRIX_POLICY, citrix_policy_info):
        logger.error("insert citrix policy %s fail" % citrix_policy)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
     
    citrix_policy["citrix_policy_id"]=citrix_policy_id
    citrix_policy["pol_priority"]=ret["pol_priority"] 
    return citrix_policy

def config_citrix_policy_item(sender,citrix_policy_name,citrix_policy_id, policy_items):
    
    ctx = context.instance()
    ret = ctx.res.resource_config_citrix_policy_item(sender["zone"], citrix_policy_name,policy_items)
    if ret is None:
        logger.error("ddc create citrix_policy_item fail")
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    policy_items_error_set=ret
    policy_items_set=[]    
    flag=-1              
    for item in policy_items:
        if policy_items_error_set and item["pol_item_name"] in policy_items_error_set.keys():
            continue
        policy_item_id=item.get("pol_item_id")
        ret=check_citrix_policy_item_name(sender["zone"],item["pol_item_name"],citrix_policy_id)         

        if policy_item_id is None:
            if ret:
                logger.info("policy_item_name %s is exist " % ret)
                policy_item_id=ret    
                flag=0        
            else:
                flag=1
                policy_item_id = get_uuid(UUID_TYPE_POLICY_ITEM, 
                                     ctx.checker, 
                                     long_format=True)
        else:
            policy_value=  item.get("pol_item_value")   
            if policy_value=="NotConfigured":
                flag=2                   
        citrix_policy_item_info = dict(
                              pol_item_id = policy_item_id,
                              pol_item_name=item["pol_item_name"],
                              pol_id=citrix_policy_id,
                              pol_item_type = item["pol_item_type"],
                              pol_item_state = item["pol_item_state"],
                              pol_item_value= item["pol_item_value"],
                              update_time = get_current_time(),
                              zone = sender["zone"]                              
                              )
        if flag==1:
            citrix_policy_item_info["create_time"]=get_current_time()
            if not ctx.pg.insert(dbconst.TB_CITRIX_POLICY_ITEM, citrix_policy_item_info):
                logger.error("insert citrix policy item %s fail" % citrix_policy_item_info)
                continue
        elif flag==0:              
            if not ctx.pg.update(dbconst.TB_CITRIX_POLICY_ITEM, policy_item_id,citrix_policy_item_info):
                logger.error("update citrix policy  item %s fail" % citrix_policy_item_info)
                continue  
        elif flag==2:
            if not ctx.pg.delete(dbconst.TB_CITRIX_POLICY_ITEM, policy_item_id):
                logger.error("delete citrix policy item %s fail" % citrix_policy_item_info)
                continue     
        else:
            continue            
        policy_items_set.append(policy_item_id)
    return policy_items_set,policy_items_error_set    

def delete_citrix_policy(sender, citrix_policy_id,policy_name):
    
    ctx = context.instance()
    resource_citrix_policies = ctx.res.resource_describe_citrix_policies(sender["zone"], policy_name)
    if resource_citrix_policies :
        ret = ctx.res.resource_delete_citrix_policy(sender["zone"], policy_name)
        if not ret:
            logger.error("no found resource policy %s" % policy_name)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
            
    conditions = {"pol_id": citrix_policy_id,"zone":sender["zone"]}
    if ctx.pg.base_delete(dbconst.TB_CITRIX_POLICY_ITEM, conditions) is None:
        logger.error("delete citrix policy item %s fail" % policy_name)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DELETE_RESOURCE_FAILED)
        
    if ctx.pg.base_delete(dbconst.TB_CITRIX_POLICY_FILTER, conditions) is None:
        logger.error("delete citrix policy filter %s fail" % policy_name)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DELETE_RESOURCE_FAILED)
    
    if not ctx.pg.delete(dbconst.TB_CITRIX_POLICY, citrix_policy_id):
        logger.error("delete citrix policy %s fail" % policy_name)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DELETE_RESOURCE_FAILED)    
  
    return citrix_policy_id

def refresh_citrix_policy(sender):       
    ctx = context.instance()
    citrix_policies = ctx.pgm.get_citrix_policies(zone_id=sender["zone"])
    if not citrix_policies:
        citrix_policies = {}

    resource_citrix_policies = ctx.res.resource_describe_citrix_policies(sender["zone"])
    if resource_citrix_policies is None:
        return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CITRIX_POLICY_NAME_NO_FOUND)
    new_citrix_policies = []
    del_citrix_policies = []
    
    for _, policy in citrix_policies.items():
        citrix_policy_name=policy["policy_name"]
        if citrix_policy_name not in resource_citrix_policies:
            del_citrix_policies.append(policy)
            continue        
        resource_citrix_policy = resource_citrix_policies[citrix_policy_name]
        update_info = check_citrix_policy_info(resource_citrix_policy, policy)

        if update_info:
            conditions = {"pol_id": policy["pol_id"],"zone":sender["zone"]}        
            if not ctx.pg.base_update(dbconst.TB_CITRIX_POLICY, conditions, update_info):
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    for policy_name, resource_policy in resource_citrix_policies.items():
        if policy_name not in citrix_policies:
            new_citrix_policies.append(resource_policy)
            continue
    if new_citrix_policies:
        for policy in new_citrix_policies:
            ret = register_citrix_policy(sender["zone"], policy)
            if isinstance(ret, Error):
                return ret
    if del_citrix_policies:
        for policy in del_citrix_policies:
            policy_id = policy["pol_id"]
            policy_name = policy["policy_name"]
            ret = delete_citrix_policy(sender, policy_id,policy_name)
            if isinstance(ret, Error):
                return ret
    return None

def refresh_citrix_policy_item(sender,policy_id,policy_name):
    
    ctx = context.instance()
    policy_items = ctx.pgm.get_citrix_policy_items(citrix_policy_id=policy_id,zone_id=sender["zone"])
    if not policy_items:
        policy_items = {}
    resource_policy_items = ctx.res.resource_describe_citrix_policy_items(sender["zone"], policy_name)
    if resource_policy_items is None:
        return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CITRIX_POLICY_NAME_NO_FOUND)
    new_policy_items = []
    del_policy_items = []
    for policy_item_name, policy_item in policy_items.items():
        if policy_item_name not in resource_policy_items:
            del_policy_items.append(policy_item)
            continue
        resource_policy_item = resource_policy_items[policy_item_name]        
        update_info =check_citrix_policy_item_info(resource_policy_item,policy_item) 
        if update_info:
            conditions = {"pol_item_id": policy_item["pol_item_id"],"zone":sender["zone"]}        
            if not ctx.pg.base_update(dbconst.TB_CITRIX_POLICY_ITEM, conditions, update_info):
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED) 

    for policy_item_name, resource_policy_item in resource_policy_items.items():
        if policy_item_name not in policy_items:
            new_policy_items.append(resource_policy_item)
    
    if new_policy_items:
        for policy_item in new_policy_items:
            ret = register_citrix_policy_item(sender["zone"], policy_item,policy_id)
            if isinstance(ret, Error):
                return ret
    del_ids=[]
    if del_policy_items:
        for policy_item in del_policy_items:
            del_ids.append(policy_item["pol_item_id"])
        ret=delete_citrix_policy_item(del_ids,sender["zone"])
        if isinstance(ret,Error):
            return ret
    return None

def refresh_citrix_policy_filter(sender,policy_id,policy_name):
    
    ctx = context.instance()    
    policy_filters = ctx.pgm.get_citrix_policy_filters(citrix_policy_id=policy_id,zone_id=sender["zone"])
    if not policy_filters:
        policy_filters = {}
    resource_policy_filters = ctx.res.resource_describe_citrix_policy_filters(sender["zone"], policy_name)
    if resource_policy_filters is None:
        return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_CITRIX_POLICY_NAME_NO_FOUND)
    new_policy_filters = []
    del_policy_filters = []
    for policy_filter_name, policy_filter in policy_filters.items():
        if policy_filter_name not in resource_policy_filters:
            del_policy_filters.append(policy_filter)
            continue
        resource_policy_filter = resource_policy_filters[policy_filter_name]
        update_info =check_citrix_policy_filter_info(resource_policy_filter,policy_filter) 
        if update_info:
            conditions = {"pol_filter_id": policy_filter["pol_filter_id"],"zone":sender["zone"]}
            if not ctx.pg.base_update(dbconst.TB_CITRIX_POLICY_FILTER, conditions, update_info):
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED) 
        
    for policy_filter_name, resource_policy_filter in resource_policy_filters.items():
        if policy_filter_name not in policy_filters:
            new_policy_filters.append(resource_policy_filter)    
    if new_policy_filters:
        for policy_filter in new_policy_filters:
            ret = register_citrix_policy_filter(sender["zone"], policy_filter,policy_id)
            if isinstance(ret, Error):
                return ret
    if del_policy_filters:
        ret=delete_citrix_policy_filter(sender["zone"],policy_name,del_policy_filters)
        if isinstance(ret,Error):
            return ret

    return None

def describe_citrix_policy(sender,citrix_policy_names,search_word):    
    ctx = context.instance()      
    conditions={"zone":sender["zone"]}
    if search_word:
        conditions["search_word"]=SearchWordType(search_word)  
    if not citrix_policy_names:
        policys_set = ctx.pg.base_get(dbconst.TB_CITRIX_POLICY,conditions,sort_key="pol_priority")    
    else:
        conditions["policy_name"]=citrix_policy_names
        policys_set = ctx.pg.base_get(dbconst.TB_CITRIX_POLICY, conditions) 
    return policys_set 

def describe_citrix_policy_item(sender,citrix_policy_id):
    ctx = context.instance()
    policy_items = ctx.pgm.get_citrix_policy_items_info(citrix_policy_id,zone_id=sender["zone"])
    if not policy_items:
        return None         
    for item in policy_items:
        pol_item_datatype=  item["pol_item_datatype"]  
        datalist=[] 
        if pol_item_datatype:
            datatype = pol_item_datatype.split("(;)")
            for data_item in datatype:
                data={}
                (name,value,description) = str.split(data_item,':')
                data["name"]=name
                data["value"]=value
                data["description"]=description
                datalist.append(data)
            item["pol_item_datatype"]=datalist                   
    
    return policy_items

def describe_citrix_policy_item_config(sender,col1,col2,col3,search_word,pol_id):
    ctx = context.instance()
    condition={}
    if search_word:
        condition["search_word"]=SearchWordType(search_word)              
    if col1:
        condition["col1"]=col1
    if col2:
        condition["col2"]=col2       
    if col3:
        condition["col3"]=col3      

    policy_item_configs = ctx.pg.base_get(TB_CITRIX_POLICY_ITEM_CONFIG, condition)
    if not policy_item_configs:
        return None

    itemList = None
    if pol_id:
        condition={}
        condition["pol_id"]=pol_id
        condition["zone"]=sender["zone"]    
        itemList=ctx.pg.base_get(TB_CITRIX_POLICY_ITEM, condition)    
    policy_cfg_items={}
    pol_item_config_set=[]
    
    for policy_item_config in policy_item_configs:
        policy_item={}  
        if itemList:
            for item in itemList:                       
                pol_item_config_name = policy_item_config["pol_item_name"]
                if pol_item_config_name==item["pol_item_name"]:
                    policy_item["pol_item_value"]=item["pol_item_value"]
            policy_cfg_items["total_sel_count"]=len(itemList)
                                    
        policy_item["pol_item_name"] = policy_item_config["pol_item_name"]
        policy_item["pol_item_type"] = policy_item_config["pol_item_type"]
        policy_item["pol_item_default_state"] = policy_item_config["pol_item_state"]
        policy_item["pol_item_default_value"] = policy_item_config["pol_item_value"]
        policy_item["pol_item_path"]  = policy_item_config["pol_item_path"]  
        policy_item["pol_item_path_ch"]  = policy_item_config["pol_item_path_ch"]               
        policy_item["description"]   = policy_item_config["description"]    
        policy_item["pol_item_name_ch"]   = policy_item_config["pol_item_name_ch"] 
        policy_item["pol_item_tip"]   = policy_item_config["pol_item_tip"] 
        policy_item["pol_item_unit"]   = policy_item_config["pol_item_unit"] 
        policy_item["pol_item_value_ch"]   = policy_item_config["pol_item_value_ch"] 
        pol_item_datatype=  policy_item_config["pol_item_datatype"]  
        datalist=[] 
        if pol_item_datatype:
            datatype = pol_item_datatype.split("(;)")
            for data_item in datatype:
                data={}
                (name,value,description) = str.split(data_item,':')
                data["name"]=name
                data["value"]=value
                data["description"]=description
                datalist.append(data)
            policy_item["pol_item_datatype"]=datalist                   
        pol_item_config_set.append(policy_item)        
    policy_cfg_items["config_set"]=pol_item_config_set  
    if col1 is None and col2 is None and col3 is None:
        filter_condition={}
        columns=["col1"]
        sort_key="col1"
        if search_word:
            filter_condition={"pol_item_path": SearchWordType(search_word)}                                
        retcol1 = ctx.pg.base_get(dbconst.TB_CITRIX_POLICY_ITEM_CONFIG,filter_condition,columns,sort_key=sort_key,distinct=True)
        if not retcol1:
            return None                    
        policy_cfg_items["col0"]=retcol1
        policy_cfg_items["col1"]=[]
        policy_cfg_items["col2"]=[]
        policy_cfg_items["col3"]=[]
        return policy_cfg_items       
    if col1 and col2 is None and col3 is None:
        filter_condition={}
        filter_condition["col1"] = col1
        columns=["col2"]
        sort_key="col2"
        if search_word:
            filter_condition={"pol_item_path": SearchWordType(search_word)}                          
        retcol1 = ctx.pg.base_get(dbconst.TB_CITRIX_POLICY_ITEM_CONFIG,filter_condition,columns,sort_key=sort_key,distinct=True)
        if not retcol1:
            return None                    
        policy_cfg_items["col1"]=retcol1
        policy_cfg_items["col2"]=[]
        policy_cfg_items["col3"]=[]            
        return policy_cfg_items            
    if col1 and col2 and col3 is None:                
        filter_condition = {}
        filter_condition["col1"] = col1
        filter_condition["col2"] = col2
        columns=["col3"]
        sort_key="col3"            
        if search_word:
            filter_condition={"pol_item_path": SearchWordType(search_word)}                              
        retcol2 = ctx.pg.base_get(dbconst.TB_CITRIX_POLICY_ITEM_CONFIG,filter_condition,columns,sort_key=sort_key,distinct=True)
        if not retcol2:
            return None                    
        policy_cfg_items["col2"]=retcol2
        policy_cfg_items["col3"]=[]            
        return policy_cfg_items                        
    return policy_cfg_items

def modify_citrix_policy(sender,citrix_policy_id,citrix_policy):
    ctx = context.instance()
    ret = ctx.res.resource_modify_citrix_policy(sender["zone"], citrix_policy)
    if not ret:
        logger.error("ddc modify citrix_policy_name %s fail" % citrix_policy["citrix_policy_name"])
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)   
    citrix_policy_info={}
    if citrix_policy["description"] is not None:
        citrix_policy_info["description"]=citrix_policy["description"] 
         
    if citrix_policy["policy_state"] is not None:
        citrix_policy_info["pol_state"]=citrix_policy["policy_state"]   
        
    citrix_policy_info["update_time"]=  get_current_time()          

    if not ctx.pg.update(dbconst.TB_CITRIX_POLICY, citrix_policy_id,citrix_policy_info):
        logger.error("modify citrix policy %s fail" % citrix_policy)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)          

def rename_citrix_policy(sender,citrix_policy_id,citrix_policy):
    ctx = context.instance()
    ret = ctx.res.resource_rename_citrix_policy(sender["zone"], citrix_policy)
    if not ret:
        logger.error("ddc rename citrix_policy_name %s fail" % citrix_policy["citrix_policy_new_name"])
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    citrix_policy_info = dict(
                              policy_name = citrix_policy["citrix_policy_new_name"] ,
                              update_time = get_current_time()
                              )
    if not ctx.pg.update(dbconst.TB_CITRIX_POLICY, citrix_policy_id,citrix_policy_info):
        logger.error("rename citrix policy %s fail" % citrix_policy)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)   
        
def set_citrix_policy_priority(sender,citrix_policy_name,policy_priority):
    ctx = context.instance()
    ret = ctx.res.resource_set_citrix_policy_priority(sender["zone"], citrix_policy_name,policy_priority)
    if not ret:
        logger.error("ddc set citrix_policy_priority %s fail" % citrix_policy_name)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

        
def describe_citrix_policy_filter(sender,citrix_policy_id):
    ctx = context.instance()
    conditions={}
    conditions["zone"]=sender["zone"]   
    conditions["pol_id"]=citrix_policy_id
    filters_set=[]
    if citrix_policy_id:
        columns = ["pol_filter_mode", "pol_filter_state","pol_filter_value", "pol_filter_name","pol_filter_type","pol_filter_id"]
        filters_set = ctx.pg.base_get(dbconst.TB_CITRIX_POLICY_FILTER,conditions,columns=columns,sort_key="pol_filter_id")       
    return filters_set 


def modify_citrix_policy_filter(sender,citrix_policy_id,citrix_policy_name,citrix_policy_filters):

    ctx = context.instance()
    ret = ctx.res.resource_modify_citrix_policy_filter(sender["zone"],citrix_policy_name, citrix_policy_filters)
    if ret is None:
        logger.error("ddc modify citrix_policy_name %s fail" % citrix_policy_name)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    policy_filter_ret=[]        
    policy_filters_error_set=ret  
    for filter in citrix_policy_filters:
        if "pol_filter_id" in filter:
            pol_filter_id=filter["pol_filter_id"]
        else:
            logger.error("modify citrix policy filter %s fail" % filter)
            continue    
        if "pol_filter_name" in filter:
            pol_filter_name=filter["pol_filter_name"]
            if policy_filters_error_set and pol_filter_name in policy_filters_error_set.keys():
                continue                             
        else:
            logger.error("modify citrix policy filter %s fail" % filter)
            continue          
                
        citrix_policy_filter_info = dict(
                              pol_filter_name=filter["pol_filter_name"],
                              pol_filter_type = filter["pol_filter_type"],
                              pol_filter_state = filter["pol_filter_state"],
                              pol_filter_value= filter["pol_filter_value"],
                              pol_filter_mode= filter["pol_filter_mode"],
                              update_time = get_current_time()                           
                              )
        if not ctx.pg.update(dbconst.TB_CITRIX_POLICY_FILTER, pol_filter_id,citrix_policy_filter_info):
            logger.error("update citrix policy filter %s fail" % citrix_policy_filter_info["pol_filter_name"])
            continue  
        filter_info=dict(pol_filter_id = pol_filter_id,pol_filter_name=filter["pol_filter_name"],)
        policy_filter_ret.append(filter_info)
    return policy_filter_ret,policy_filters_error_set

def add_citrix_policy_filter(sender,citrix_policy_id,citrix_policy_name,citrix_policy_filters):

    ctx = context.instance()
    ret = ctx.res.resource_add_citrix_policy_filter(sender["zone"],citrix_policy_name, citrix_policy_filters)
    if ret is None:
        logger.error("ddc create citrix_policy_filter %s fail" % citrix_policy_name)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    policy_filters_error_set=ret    
    policy_filter_ret=[]    
    for filter in citrix_policy_filters:
        if policy_filters_error_set and filter["pol_filter_name"] in policy_filters_error_set.keys():
            continue        
        
        pol_filter_id = get_uuid(UUID_TYPE_POLICY_FILTER, 
                                 ctx.checker, 
                                 long_format=True)
        citrix_policy_filter_info = dict(
                              pol_filter_id = pol_filter_id,
                              pol_id=citrix_policy_id,
                              pol_filter_name=filter["pol_filter_name"],
                              pol_filter_type = filter["pol_filter_type"],
                              pol_filter_state = filter["pol_filter_state"],
                              pol_filter_value= filter["pol_filter_value"],
                              pol_filter_mode= filter["pol_filter_mode"],
                              update_time = get_current_time(),
                              create_time = get_current_time(),
                              zone = sender["zone"]                              
                              )
        if not ctx.pg.insert(dbconst.TB_CITRIX_POLICY_FILTER, citrix_policy_filter_info):
            logger.error("insert citrix policy filter %s fail" % citrix_policy_filter_info["pol_filter_name"])
            continue  
        filter_info=dict(pol_filter_id = pol_filter_id,pol_filter_name=filter["pol_filter_name"],)
        policy_filter_ret.append(filter_info)
    return policy_filter_ret,policy_filters_error_set 

def delete_citrix_policy_filter(sender,citrix_policy_name,citrix_policy_filters,flag=None):

    ctx = context.instance()
    if flag:
        ret = ctx.res.resource_delete_citrix_policy_filter(sender["zone"],citrix_policy_name, citrix_policy_filters)
        if ret is None:
            logger.error("ddc delete citrix_policy filter %s fail" % citrix_policy_name)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_RESOURCE_FAILED)
    policy_filters_error_set=ret  
    del_filter_ids=[]
    for filter in citrix_policy_filters:
        if policy_filters_error_set:           
            if "pol_filter_name" in filter:
                pol_filter_name=filter["pol_filter_name"]
                if pol_filter_name in policy_filters_error_set.keys():
                    continue                                        
        if "pol_filter_id" in filter:
            pol_filter_id=filter["pol_filter_id"]
            del_filter_ids.append(pol_filter_id)
        else:
            logger.error("delete citrix policy filter %s fail" % filter)
            continue                
    conditions = {"pol_filter_id":del_filter_ids}    
    if ctx.pg.base_delete(dbconst.TB_CITRIX_POLICY_FILTER, conditions) is None:
        logger.error("delete citrix_policy_filter %s fail" % citrix_policy_name)  
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DELETE_RESOURCE_FAILED)   
        
    return del_filter_ids,policy_filters_error_set
 
def register_citrix_policy(zone, citrix_policy):
    ctx = context.instance()
    citrix_policy_id = get_uuid(UUID_TYPE_CITRIX_POLICY, ctx.checker)         
    citrix_policy_info = dict(
                              pol_id = citrix_policy_id,
                              policy_name = citrix_policy["citrix_policy_name"],
                              pol_priority = citrix_policy["pol_priority"],
                              com_priority = citrix_policy["com_priority"],
                              user_priority = citrix_policy["user_priority"],
                              description = citrix_policy["description"],
                              pol_state=citrix_policy["pol_state"],
                              create_time = get_current_time(),
                              update_time = get_current_time(),
                              zone = zone,                                 
                              )

    if not ctx.pg.insert(dbconst.TB_CITRIX_POLICY, citrix_policy_info):
        logger.error("insert citrix policy %s fail" % citrix_policy)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    return citrix_policy_id

def register_citrix_policy_item(zone, citrix_policy_item,policy_id):
    ctx = context.instance()
    citrix_policy_item_id = get_uuid(UUID_TYPE_POLICY_ITEM, ctx.checker)         
    citrix_policy_item_info = dict(
                              pol_item_id = citrix_policy_item_id,
                              pol_item_name=citrix_policy_item["pol_item_name"],
                              pol_id=policy_id,
                              pol_item_type = citrix_policy_item["pol_item_type"],
                              pol_item_state = citrix_policy_item["pol_item_state"],
                              pol_item_value= citrix_policy_item["pol_item_value"],
                              update_time = get_current_time(),
                              create_time =get_current_time(),
                              zone = zone                                                           
                              )

    if not ctx.pg.insert(dbconst.TB_CITRIX_POLICY_ITEM, citrix_policy_item_info):
        logger.error("insert citrix policy item %s fail" % citrix_policy_item_info)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    return citrix_policy_item_id

def register_citrix_policy_filter(zone, citrix_policy_filter,policy_id):
    ctx = context.instance()
    pol_filter_id = get_uuid(UUID_TYPE_POLICY_FILTER, ctx.checker)         
    citrix_policy_filter_info = dict(
                          pol_filter_id = pol_filter_id,
                          pol_id=policy_id,
                          pol_filter_name=citrix_policy_filter["pol_filter_name"],
                          pol_filter_type = citrix_policy_filter["pol_filter_type"],
                          pol_filter_state = citrix_policy_filter["pol_filter_state"],
                          pol_filter_value= citrix_policy_filter["pol_filter_value"],
                          pol_filter_mode= citrix_policy_filter["pol_filter_mode"],
                          update_time = get_current_time(),
                          create_time = get_current_time(),
                          zone = zone                             
                          )

    if not ctx.pg.insert(dbconst.TB_CITRIX_POLICY_FILTER, citrix_policy_filter_info):
        logger.error("insert citrix policy filter %s fail" % citrix_policy_filter_info)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    return pol_filter_id


def check_citrix_policy_name(zone_id, citrix_policy_name):
    
    ctx = context.instance()
    ret = ctx.pgm.get_citrix_policies(citrix_policy_names=citrix_policy_name, zone_id=zone_id)
    if ret:
        logger.error("citrix policy name %s already existed" % (citrix_policy_name))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_CITRIX_POLICY_NAME_ALREADY_EXISTED, (citrix_policy_name))

    citrix_policy = ctx.res.resource_describe_citrix_policies(zone_id, citrix_policy_name)
    if citrix_policy:
        logger.error("citrix policy name %s already existed" % (citrix_policy_name))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_CITRIX_POLICY_NAME_ALREADY_EXISTED, (citrix_policy_name))
    
    return citrix_policy

def check_citrix_policy_item_name(zone_id, citrix_policy_item_name, citrix_policy_id):
    
    ctx = context.instance()
    ret = ctx.pgm.get_citrix_policy_item(citrix_policy_item_name=citrix_policy_item_name,citrix_policy_id=citrix_policy_id, zone_id=zone_id)
    if ret:
        return ret["pol_item_id"]    
    return None    


def delete_citrix_policy_item(del_ids=None,zone_id=None):
    
    ctx = context.instance()
    if del_ids:        
        conditions = {"pol_item_id": del_ids}    
        if zone_id:
            conditions["zone"] = zone_id       
        if ctx.pg.base_delete(dbconst.TB_CITRIX_POLICY_ITEM, conditions) is None:
            logger.error("delete citrix policy item %s fail" % del_ids)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_RESOURCE_FAILED)


def check_citrix_policy_info(resource_citrix_policy,policy):
    
    check_keys=["pol_priority","user_priority", "cmo_priority",  "description", "pol_state"]
    update_info={}
    for key in check_keys:
        if key not in resource_citrix_policy or key not in policy:
            continue
        if resource_citrix_policy[key] !=policy[key]:
            update_info[key]=resource_citrix_policy[key]
    return update_info

def check_citrix_policy_item_info(resource_citrix_policy_item,policy_item):
    
    check_keys=["pol_item_value"]
    update_info={}
    for key in check_keys:
        if key not in resource_citrix_policy_item or key not in policy_item:
            continue
        if resource_citrix_policy_item[key] !=policy_item[key]:
            update_info[key]=resource_citrix_policy_item[key]
    return update_info

def check_citrix_policy_filter_info(resource_citrix_policy_filter,policy_filter):
    
    check_keys=["pol_filter_value","pol_filter_state","pol_filter_mode"]
    update_info={}
    for key in check_keys:
        if key not in resource_citrix_policy_filter or key not in policy_filter:
            continue
        if resource_citrix_policy_filter[key] !=policy_filter[key]:
            update_info[key]=resource_citrix_policy_filter[key]    
    return update_info
