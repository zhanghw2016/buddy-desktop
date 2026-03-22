import context
from log.logger import logger
from utils.misc import get_current_time
from db.constants import TB_USB_POLICY, PUBLIC_COLUMNS
from utils.id_tool import UUID_TYPE_USB_POLICY, get_uuid

def create_usb_policy(object_id, params):
    try:
        # create usb policy
        ctx = context.instance()
        policy = {}
        usb_policy_id = get_uuid(UUID_TYPE_USB_POLICY, 
                                 ctx.checker, 
                                 long_format=True)
        
        curtime = get_current_time(to_seconds=False)
        policy['usb_policy_id'] = usb_policy_id
        policy['object_id'] = object_id
        policy['policy_type'] = params.get('policy_type', "black")
        policy['priority'] = params.get('priority', 1000)
        policy['class_id'] = params.get('class_id', '-1')
        policy['vendor_id'] = params.get('vendor_id', '-1')
        policy['product_id'] = params.get('product_id', '-1')
        policy['version_id'] = params.get('version_id', '-1')
        policy['allow'] = params.get('allow', '1')
        
        policy['create_time'] = curtime
        policy['update_time'] = curtime
    
        if not ctx.pg.insert(TB_USB_POLICY, policy):
            logger.error("create usb policy on desktop [%s] failed." % (object_id))
            return None

        return usb_policy_id
    except Exception, e:
        logger.error("insert usb policy with Exception:%s" % e)
        return None

def modify_usb_policy(usb_policy_id, params={}):
    ctx = context.instance()
    
    try:
        condiction = {"usb_policy_id": usb_policy_id}
        if params:
            params.update({"update_time": get_current_time(to_seconds=False)})
        else:
            return True

        if not ctx.pg.base_update(TB_USB_POLICY, 
                                  condiction,
                                  params):
            logger.error("modify usb policy on desktop [%s] failed" % (usb_policy_id))
            return False
    
        return True
    except Exception, e:
        logger.error("modify usb policy on desktop, Exception:%s " % e)
        return False

def delete_usb_policy(usb_policy_ids=None, object_ids=None):
    ctx = context.instance()
    condition = {}
    if usb_policy_ids:
        condition['usb_policy_id'] = usb_policy_ids
    if object_ids:
        condition['object_id'] = object_ids
    if len(condition) == 0:
        return True

    try:
        if ctx.pg.base_delete(TB_USB_POLICY, condition) < 0:
            logger.error("delete usb policy on desktop [%s] failed" % (usb_policy_ids))
            return None

        return True
    except Exception, e:
        logger.error("delete usb policy on desktop, Exception:%s" % e)
        return None

def describe_usb_policy(condition={}, sort_key=None, reverse=False, offset=None, limit=None, is_and=True, columns=None):
    ctx = context.instance()
    try:
        if not columns:
            columns=PUBLIC_COLUMNS[TB_USB_POLICY]
        policys = ctx.pg.base_get(TB_USB_POLICY, 
                                  condition,
                                  columns=columns,
                                  sort_key=sort_key,
                                  reverse=reverse, 
                                  offset=offset,
                                  limit=limit,
                                  is_and=is_and)
        if policys == None:
            logger.error("get usb policy failed with condition: %s " % (condition))
            return []

        return policys
    except Exception, e:
        logger.error("get usb policy failed,Exception:%s" % (e))
        return []

def get_usb_policy_object(usb_policy_id):
    ctx = context.instance()  
    
    result = ctx.pg.get(TB_USB_POLICY, usb_policy_id)
    if result is None or len(result)==0:
        logger.error("get usb policy [%s] failed" % usb_policy_id)
        return None

    return result[0]["object_id"]
