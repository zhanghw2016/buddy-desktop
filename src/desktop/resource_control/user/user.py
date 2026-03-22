'''
Created on 2012-10-17

@author: yunify
'''
import context
import constants as const
import db.constants as dbconst
from utils.misc import get_current_time
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from log.logger import logger
from utils.id_tool import (
    UUID_TYPE_RECORD_USER_LOGIN,
    get_uuid,
)

from api.auth.auth_const import DONT_EXPIRE_PASSWORD
from resource_control.desktop.desktop import get_desktop_with_monitor
from utils.id_tool import(
    UUID_TYPE_DESKTOP_GROUP, UUID_TYPE_DESKTOP_GROUP_DISK, UUID_TYPE_DESKTOP,UUID_TYPE_DESKTOP_DISK, UUID_TYPE_DESKTOP_GROUP_NETWORK,
    UUID_TYPE_DESKTOP_IMAGE,
    UUID_TYPE_DESKTOP_NETWORK,
    UUID_TYPE_DESKTOP_OU, UUID_TYPE_DESKTOP_USER, UUID_TYPE_DESKTOP_USER_GROUP,
    UUID_TYPE_SNAPHSOT_GROUP, UUID_TYPE_SNAPSHOT_RESOURCET, UUID_TYPE_SNAPSHOT_GROUP_SNAPSHOT, UUID_TYPE_SNAPSHOT_DISK_SNAPSHOT,
    UUID_TYPE_VDI_SCHEDULER_TASK_HISTORY, UUID_TYPE_VDI_SCHEDULER_TASK,
    UUID_TYPE_DELIVERY_GROUP,
    UUID_TYPE_POLICY_GROUP
)


def get_resource_scope_type(resource_ids):
    resource_scope = {}
    for resource_id in resource_ids:
        prefix = resource_id.split("-")[0]
        resource_type = None
        if prefix in [UUID_TYPE_DESKTOP_GROUP, UUID_TYPE_DESKTOP, UUID_TYPE_DESKTOP_GROUP_DISK, UUID_TYPE_DESKTOP_DISK, UUID_TYPE_DESKTOP_GROUP_NETWORK]:
            resource_type = dbconst.RESTYPE_DESKTOP_GROUP
        elif prefix in [UUID_TYPE_DESKTOP_OU, UUID_TYPE_DESKTOP_USER, UUID_TYPE_DESKTOP_USER_GROUP]:
            resource_type = dbconst.RESTYPE_USER_OU
        elif prefix in [UUID_TYPE_SNAPHSOT_GROUP, UUID_TYPE_SNAPSHOT_RESOURCET, UUID_TYPE_SNAPSHOT_GROUP_SNAPSHOT, UUID_TYPE_SNAPSHOT_DISK_SNAPSHOT]:
            resource_type = dbconst.RESTYPE_SNAPSHOT_GROUP
        elif prefix in [UUID_TYPE_VDI_SCHEDULER_TASK_HISTORY, UUID_TYPE_VDI_SCHEDULER_TASK]:
            resource_type = dbconst.RESTYPE_SCHEDULER_TASK
        elif prefix in [UUID_TYPE_DESKTOP_NETWORK]:
            resource_type = dbconst.RESTYPE_DESKTOP_NETWORK
        elif prefix in [UUID_TYPE_DESKTOP_IMAGE]:
            resource_type = dbconst.RESTYPE_DESKTOP_IMAGE
        elif prefix in [UUID_TYPE_DELIVERY_GROUP]:
            resource_type = dbconst.RESTYPE_DELIVERY_GROUP
        elif prefix in [UUID_TYPE_POLICY_GROUP]:
            resource_type = dbconst.RESTYPE_POLICY_GROUP

        if not resource_type:
            continue

        if resource_type not in resource_scope:
            resource_scope[resource_type] = []
        resource_scope[resource_type].append(resource_id)

    return resource_scope

def get_user_password(user_name):
    ctx = context.instance()  
    # build conditions
    condition = {'user_name': user_name}
    columns = ['password']
    
    # get from db
    try:
        result = ctx.pg.base_get(dbconst.TB_DESKTOP_USER, condition, columns)
        if not result:
            logger.error("get user [%s] password failed" % user_name)
            return None
    except Exception,e:
        logger.error("get user password with Exception:%s" % e)
        return None
    return result[0]['password']

def reset_user_password(user_name, password):
    ctx = context.instance()
    
    try:
        ret = ctx.pg.base_get(dbconst.TB_DESKTOP_USER, {"user_name": user_name})
        if not ret or len(ret)!=1:
            logger.error("user [%s] not found." % user_name)
            return False
        
        update_info = {'password': password,
                       'update_time': get_current_time(to_seconds=False),
                       'user_control': DONT_EXPIRE_PASSWORD}
        
        if not ctx.pg.base_update(dbconst.TB_DESKTOP_USER, 
                                  {'user_name': user_name}, update_info):
            logger.error("update user password [%s] failed" % (user_name))
            return False
    except Exception, e:
        logger.error("update user password from table [%s] error,Exception:%s" % (dbconst.TB_DESKTOP_USER, e))
        return False
    return True

def delete_users(user_ids):
    ''' delete user by user id '''
    ctx = context.instance()
    condition = {'user_id': user_ids}

    try:
        if ctx.pg.base_delete(dbconst.TB_DESKTOP_USER, condition) < 0:
            logger.error("delete user [%s] failed" % (condition))
            return Error(ErrorCodes.DELETE_USER_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_USER_ERROR)

        return user_ids
    except Exception, e:
        logger.error("delete user form table [%s] error,Exception:%s" % (dbconst.TB_DESKTOP_USER, e))
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION, 
                     ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def enable_users(user_ids, zone_id):
    if len(user_ids) == 0:
        return True
    
    ctx = context.instance()
    try:
        conds = {
            'user_id': user_ids,
            'zone_id': zone_id
            }
        if ctx.pg.base_update(dbconst.TB_ZONE_USER, 
                              conds, 
                              {'status': const.USER_STATUS_ACTIVE, 'update_time': get_current_time(to_seconds=False)}) < 0:
            logger.error("enable users [%s] failed" % user_ids)
            return Error(ErrorCodes.ENABLE_DESKTOP_USER_ERROR,
                         ErrorMsg.ERR_MSG_ENABLE_DESKTOP_USER_ERROR)

        return user_ids
    except Exception,e:
        logger.error("Enable Users with Exception:%s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION, 
                     ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def disable_users(user_ids, zone_id):
    if len(user_ids) == 0:
        return True
    
    ctx = context.instance()
    try:
        conds = {
            'user_id': user_ids,
            'zone_id': zone_id
            }
        if ctx.pg.base_update(dbconst.TB_ZONE_USER, 
                              conds, 
                              {'status': const.USER_STATUS_DISABLED, 'update_time': get_current_time(to_seconds=False)}) < 0:
            logger.error("disable users [%s] failed" % user_ids)
            return Error(ErrorCodes.DISABLE_DESKTOP_USER_ERROR, 
                         ErrorMsg.ERR_MSG_DISABLE_DESKTOP_USER_ERROR)

        return user_ids
    except Exception,e:
        logger.error("Disable Users with Exception:%s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION, 
                     ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)


def modify_user_role(user_id, role, zone_id):
    ''' modify user role'''
    ctx = context.instance()
    
    try:
        conds = {
            "user_id": user_id,
            'zone_id': zone_id
            }
        if not ctx.pg.base_update(dbconst.TB_ZONE_USER, 
                             conds, 
                             {'role':role}):
            logger.error("update user role [%s] failed" % (user_id))
            return False
    
        return True
    except Exception, e:
        logger.error("update user role from table [%s] error,Exception:%s " % (dbconst.TB_ZONE_USER, e))
        return False


def modify_desktop_user(user_id, attrs):
    ''' modify user role'''
    ctx = context.instance()
    
    try:
        conds = {
            "user_id": user_id,
            }
        if not ctx.pg.base_update(dbconst.TB_DESKTOP_USER, 
                             conds, 
                             attrs):
            logger.error("update desktop user [%s] failed" % (user_id))
            return False
    
        return True
    except Exception, e:
        logger.error("update desktop role from table [%s] error,Exception:%s " % (dbconst.TB_DESKTOP_USER, e))
        return False


def modify_user_scope(operation, user_id, resource_type, resource_id, action_type, zone_id):
    condition = {'user_id': user_id,
                 'resource_type': resource_type,
                 'resource_id': resource_id,
                 'zone_id': zone_id}
    
    if action_type < 0 and operation != const.USER_SCOPE_OPERATION_DELETE:
        logger.error("operation type and action_type is not matched")
        return Error(ErrorCodes.MODIFY_USER_SCOPE_ERROR, 
                     ErrorMsg.ERR_MSG_MODIFY_USER_SCOPE_ERROR)
        
    action_type = {'action_type': action_type}
    scope = dict(condition.items() + action_type.items())
    
    ctx = context.instance()
    try:
        
        if operation == const.USER_SCOPE_OPERATION_MODIFY:
            ret = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, condition)
            if len(ret) == 1:
                if ctx.pg.base_update(dbconst.TB_ZONE_USER_SCOPE, condition, action_type) >= 0:
                    return True
            else:
                if not ctx.pg.insert(dbconst.TB_ZONE_USER_SCOPE, scope):
                    logger.error("insert user scope [%s] failed." % (user_id))
                    return Error(ErrorCodes.MODIFY_USER_SCOPE_ERROR, 
                                 ErrorMsg.ERR_MSG_MODIFY_USER_SCOPE_ERROR)
                else:
                    return True
    
        if operation == const.USER_SCOPE_OPERATION_DELETE:
            ret = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, condition)
            if len(ret) > 0:
                if ctx.pg.base_delete(dbconst.TB_ZONE_USER_SCOPE, condition) < 0:
                    logger.error("delete user scope [%s] failed." % (user_id))
                    return Error(ErrorCodes.MODIFY_USER_SCOPE_ERROR, 
                                 ErrorMsg.ERR_MSG_MODIFY_USER_SCOPE_ERROR)
            else:
                return True

    except Exception,e:
        logger.error("modify user resource scope with Excepiton: %s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION, 
                     ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def describe_user_scope(user_id, resource_type=None):
    ''' get user user scope '''
    condition = {'user_id': user_id}
    if resource_type:
        condition['resource_type'] = resource_type

    ctx = context.instance()
    try:
        ret = ctx.pg.base_get(dbconst.TB_ZONE_USER_SCOPE, condition)
        if not ret:
            return None
        return ret

    except Exception,e:
        logger.error("get user resrouce scope with Excepiton: %s" % e)
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION, 
                     ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)


def modify_user_dn_by_user_name(user_name, user_dn):
    ''' modify the available user dn'''
    ctx = context.instance()  
    
    # update user dn
    try:
        if not ctx.pg.base_update(dbconst.TB_DESKTOP_USER, 
                                  {'user_name': user_name}, 
                                  {'user_dn': user_dn, 'update_time': get_current_time(to_seconds=False)}):
            logger.error("update user dn [%s] failed" % (user_name))
            return False
        return True
    except Exception,e:
        logger.error("modify user_dn with Exception:%s" % e)
        return False

def get_user_resource_detail(sender, user_ids):
    
    ctx = context.instance()
    
    user_resource = {}
    desktop_group_name = {}
    
    user_desktops = ctx.pgm.get_resource_by_user(user_ids, resource_type=dbconst.RESTYPE_DESKTOP)
    if not user_desktops:
        user_desktops = {}

    user_disks = ctx.pgm.get_resource_by_user(user_ids, resource_type=dbconst.RESTYPE_DESKTOP_DISK)
    if not user_disks:
        user_disks = {}

    for user_id in user_ids:

        desktop_ids = user_desktops.get(user_id, [])
        resource = {}
        desktops = {}
        if desktop_ids:
            desktops = ctx.pgm.get_desktops(desktop_ids)
            if not desktops:
                desktops = {}

        for desktop_id, desktop in desktops.items():
            new_desktop = ctx.pgm.format_user_desktop(desktop, desktop_group_name)
            new_desktop["resource_type"] = dbconst.RESTYPE_DESKTOP
            resource[desktop_id] = new_desktop

        disk_ids = user_disks.get(user_id, [])
        disks = {}
        if disk_ids:
            disks = ctx.pgm.get_disks(disk_ids)
            if not disks:
                disks = {}
        
        for disk_id, disk in disks.items():
            disk_id = disk["disk_id"]
            desktop_id = disk["desktop_id"]
            if desktop_id in resource:
                if "disks" not in resource[desktop_id]:
                    resource[desktop_id]["disks"] = []
                fort_disk = ctx.pgm.format_user_disk(disk, desktop_group_name)
                resource[desktop_id]["disks"].append(fort_disk)
            else:
                new_disk = ctx.pgm.format_user_disk(disk, desktop_group_name)
                new_disk["resource_type"] = dbconst.RESTYPE_DESKTOP_DISK
                resource[disk_id] = new_disk

        if desktop_ids:
            desktop_nics = ctx.pgm.get_desktop_nics(desktop_ids)
            if not desktop_nics:
                desktop_nics = {}
            for desktop_id, nics in desktop_nics.items():
                if desktop_id not in resource:
                    continue
                resource[desktop_id]["nics"] = ctx.pgm.format_user_nics(nics)
        
            ret = get_desktop_with_monitor(sender, desktop_ids)
            if ret:
                desktop_monitor = ret
                for desktop_id in desktop_ids:
                    if desktop_id not in desktop_monitor:
                        continue

                    monitor_data = desktop_monitor[desktop_id]
                    resource[desktop_id]["monitor_data"] = monitor_data["monitor_data"]
        
        user_resource[user_id] = resource

    return user_resource

def recursion_user_group(parent_group_ids):
    result = set()
    ctx = context.instance()
    while True:
        user_groups = ctx.pg.base_get(dbconst.TB_DESKTOP_USER_OU,
                                    {"parent_group_id": parent_group_ids},
                                    columns=['user_group_id'])
        parent_group_ids = []
        if user_groups:
            for user_group in user_groups:
                parent_group_ids.append(user_group["user_group_id"])
                result.add(user_group["user_group_id"])
        if not parent_group_ids:
            break

    return list(result)

def format_user_groups(user):
    
    ctx = context.instance()
    user_id = user["user_id"]
    condition = {"user_id": user_id}
    user_group = {}
    
    for tb, group_type in dbconst.USER_GROUP_TABLES.items():
        
        group_set = ctx.pg.base_get(tb, condition)
        if not group_set:
            group_set = []
        
        user_group[group_type] = group_set

    return user_group

def modify_desktop_user_reset_password_flag(user_id, value):
    
    if not user_id:
        return None
    if value not in [0, 1]:
        return None

    ctx = context.instance()

    conds = {
        'user_id': user_id
        }
    if ctx.pg.base_update(dbconst.TB_DESKTOP_USER, 
                          conds, 
                          {'reset_password': value}) < 0:
        logger.error("update user  [%s] reset_password failed" % user_id)
        return None

    return user_id

def modify_desktop_user_security_question_flag(user_id, value):
    
    if not user_id:
        return None
    if value not in [0, 1, 2]:
        return None

    ctx = context.instance()

    conds = {
        'user_id': user_id
        }
    if ctx.pg.base_update(dbconst.TB_DESKTOP_USER, 
                          conds, 
                          {'security_question': value}) < 0:
        logger.error("update user  [%s] security_question failed" % user_id)
        return None

    return user_id

def create_user_login_record(user_id, zone_id, client_ip, status=const.LOGIN_STATUS_SUCCESS, errmsg=''):
    ctx = context.instance()
    
    curtime = get_current_time(to_seconds=False)
    user_login_record_id = get_uuid(UUID_TYPE_RECORD_USER_LOGIN,
                                    ctx.checker, 
                                    long_format=True)

    login_record = {}
    login_record['user_login_record_id'] = user_login_record_id
    login_record['user_id'] = user_id
    login_record['user_name'] = ctx.pgm.get_user_name(user_id)
    login_record['zone_id'] = zone_id
    login_record['client_ip'] = client_ip
    login_record['status'] = status
    login_record['errmsg'] = errmsg
    login_record['create_time'] = curtime

    if not ctx.pg.insert(dbconst.TB_USER_LOGIN_RECORD, login_record):
        logger.error("create user login record [%s] failed." % (login_record))
        return None

    return user_login_record_id

def describe_user_login_record(user_id, zone_id):
    ctx = context.instance()

    login_record = {}
    login_record['user_id'] = user_id
    login_record['zone_id'] = zone_id

    result = ctx.pg.base_get(dbconst.TB_USER_LOGIN_RECORD, 
                             login_record,
                             sort_key="create_time",
                             reverse=True,
                             limit=1)
    if result is None:
        logger.error("create user login record [%s] failed." % (login_record))
        return None

    return result
    
def format_user_set(sender,user_set,check_module_custom_user=0):

    ctx = context.instance()
    if not check_module_custom_user:
        return None
    zone_id = sender["zone"]
    for user_id, _ in user_set.items():

        module_custom_user = ctx.pgm.get_module_custom_user(user_ids=user_id,zone_id=zone_id)
        if module_custom_user:
            for user_id,_ in module_custom_user.items():
                user_set.pop(user_id)

    return  None
