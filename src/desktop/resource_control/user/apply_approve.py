'''
Created on 2012-10-17

@author: yunify
'''
import context
import constants as const
import db.constants as dbconst
from utils.misc import get_current_time, time_to_utc
from utils.id_tool import (
    UUID_TYPE_APPLY_FORM,
    UUID_TYPE_APPLY_GROUP_FORM,
    UUID_TYPE_APPROVE_GROUP_FORM,
    get_uuid,
    UUID_TYPE_DESKTOP_GROUP,
    UUID_TYPE_DELIVERY_GROUP,
    UUID_TYPE_DESKTOP_USER_GROUP,
    UUID_TYPE_DESKTOP_USER,
)
from common import is_citrix_platform
from error.error import Error
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from log.logger import logger
from utils.json import json_load

def get_approve_users(apply_group_id, exclude_user_ids=None):
    
    ctx = context.instance()
    
    if not apply_group_id:
        return None
    
    if exclude_user_ids and not isinstance(exclude_user_ids, list):
        exclude_user_ids = [exclude_user_ids]

    ret = ctx.pgm.get_apply_groups(apply_group_id)
    if not ret:
        return None
    
    apply_group = ret[apply_group_id]
    zone_id = apply_group["zone_id"]
    
    ret = ctx.pgm.get_apply_approve_group_maps(apply_group_id)
    if not ret:
        return None
    
    relate_approve_groups = ret
    approve_group_ids = relate_approve_groups.keys()

    approve_groups = ctx.pgm.get_approve_groups(approve_group_ids)
    if not approve_groups:
        approve_groups = {}

    for approve_group_id, _approve_group in approve_groups.items():
        
        approve_group_user_ids = []
        
        approve_group = approve_groups.get(approve_group_id)
        if not approve_group:
            continue
        
        approve_group_name = approve_group["approve_group_name"]
        _approve_group["approve_group_name"] = approve_group_name
        ret = ctx.pgm.get_approve_group_user(approve_group_id)
        if not ret:
            continue
        approve_user_ids = ret.keys()
        
        ret = ctx.pgm.get_zone_user_groups(zone_id, approve_user_ids)
        if ret:
            user_group_ids = ret.keys()
            ret = ctx.pgm.get_user_group_users(user_group_ids)
            if ret:
                approve_group_user_ids.extend(ret)

        for user_id in approve_user_ids:
            if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
                continue
            if user_id in approve_group_user_ids:
                continue
            
            if exclude_user_ids and user_id in exclude_user_ids:
                continue
            
            approve_group_user_ids.append(user_id)

        ret = ctx.pgm.get_zone_users(zone_id, approve_group_user_ids)
        if not ret:
            continue
    
        _approve_group["approve_users"] = ret.values()
    
    return approve_groups

def check_create_desktop_apply_form(sender, req):

    ctx = context.instance()
    zone_id = sender["zone"]
    apply_type = req.get("apply_type")
    
    if const.APPLY_TYPE_UNLOCK != apply_type:
        return None

    resource_group_id = req.get("resource_group_id")
    resource_id = req.get("resource_id")
    
    if not resource_group_id and not resource_id:
        logger.error("missing parameter resource_group_id or resource_id")
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "resource_group_id")

    ret = check_apply_form_apply_group(resource_id, resource_group_id)
    if not ret:
        logger.error("missing parameter resource_group_id")
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "resource_group_id")
    apply_group_id = ret
    
    ret = refresh_apply_forms(zone_id=zone_id)
    if isinstance(ret, Error):
        return ret
    
    apply_forms = ctx.pgm.get_resource_apply_forms(resource_id = resource_id, 
                                           user_id=sender["owner"], 
                                           resource_group_id=resource_group_id,
                                           status=const.APPLY_FORM_VAILD_STATUS)
    if apply_forms:
        logger.error("can't create repeat apply form")
        return Error(ErrorCodes.CREATE_APPLY_FORM_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_REPEAT_APPLY_FORM_ERROR)

    return apply_group_id

def build_apply_form(req):

    apply_form = {}
    apply_form_key = ["apply_type", "apply_title","apply_description","status","apply_user_id",
                      "apply_resource_type","apply_parameter","approve_user_id","resource_group_id",
                      "resource_id", "apply_age"]

    for key in apply_form_key:
        if key not in req:
            continue
        apply_form[key] = req[key]

    return apply_form

def refresh_desktop_apply_form(resource_ids=None, resource_group_ids=None):
    
    ctx = context.instance()
    ret = ctx.pgm.get_resource_apply_forms(resource_ids, resource_group_id=resource_group_ids, status=const.APPLY_FORM_VAILD_STATUS)
    if not ret:
        return None
    apply_form_ids = ret.keys()
    refresh_apply_forms(apply_form_ids)

def refresh_apply_forms(apply_form_ids=None, zone_id =None):
    
    ctx = context.instance()
    
    ret = ctx.pgm.get_apply_forms(apply_form_ids, 
                                  const.APPLY_TYPE_UNLOCK,
                                  status=const.APPLY_FORM_VAILD_STATUS,
                                  zone_id=zone_id)
    
    if not ret:
        return None

    for apply_id, apply_form in ret.items():
        
        update_apply = {}
        status = apply_form["status"]
        approve_status = apply_form["approve_status"]

        start_time = apply_form["start_time"]
        end_time = apply_form["end_time"]
        now = get_current_time()
    
        _start_time = start_time.__format__('%Y-%m-%d %H:%M:%S')
        _end_time = end_time.__format__('%Y-%m-%d %H:%M:%S')
        _now = now.__format__('%Y-%m-%d %H:%M:%S')   
        if _now < _start_time:
            curr_status = const.APPLY_FORM_STATUS_LOCKED
            if status == curr_status:
                continue

            update_apply["status"] = curr_status

        elif _now > _end_time:
            curr_status = const.APPLY_FORM_STATUS_FINISHED
            update_apply["status"] = curr_status
            
            if approve_status == const.APPLY_FORM_RESULT_APPROVING:
                update_apply["approve_status"] = const.APPLY_FORM_RESULT_TIMEOUT
            
        else:
            if approve_status == const.APPLY_FORM_RESULT_APPROVING:
                if status != const.APPLY_FORM_STATUS_LOCKED:
                    update_apply["status"] = const.APPLY_FORM_STATUS_LOCKED
            elif approve_status == const.APPLY_FORM_RESULT_PASSED:
                if status != const.APPLY_FORM_STATUS_EFFECTIVE:
                    update_apply["status"] = const.APPLY_FORM_STATUS_EFFECTIVE
            elif approve_status == const.APPLY_FORM_RESULT_REJECTED:
                if status != const.APPLY_FORM_STATUS_FINISHED:
                    update_apply["status"] = const.APPLY_FORM_STATUS_FINISHED
        
        if not update_apply:
            continue

        if not ctx.pg.batch_update(dbconst.TB_APPLY, {apply_id: update_apply}):
            logger.error("update apply form update db fail %s" % {apply_id, update_apply})
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def check_starttime_and_endtime(req):
    
    start_time = req.get("start_time")
    end_time = req.get("end_time")
    
    if start_time:
        start_time = time_to_utc(start_time)
        req["start_time"] = start_time

    if end_time:
        end_time = time_to_utc(end_time)
        req["end_time"] = end_time
    
    if not start_time or not end_time:
        return None
    
    if end_time <= start_time:
        logger.error("apply start time %s and end time %s dismatch %s" % (start_time, end_time))
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                         ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "end_time")
    return

def check_apply_form_apply_group(resource_id=None, resource_group_id=None):
    
    ctx = context.instance()

    if not resource_group_id:
        ret = ctx.pgm.get_desktops(resource_id)
        if not ret:
            return None
        
        desktop = ret[resource_id]
        
        resource_group_id = desktop["desktop_group_id"]
        if is_citrix_platform(ctx, desktop["zone"]):
            resource_group_id = desktop["delivery_group_id"]
    
    if not resource_group_id:
        return None
    
    ret = ctx.pgm.get_apply_resource_groups(resource_group_id)
    if not ret:
        return None
    
    apply_group_resource = ret[resource_group_id]
    return apply_group_resource["apply_group_id"]

def create_desktop_apply_form(sender, req, apply_group_id=None):

    ctx = context.instance()
    apply_id = get_uuid(UUID_TYPE_APPLY_FORM, ctx.checker)
    apply_form_info = build_apply_form(req)
    
    curr_time = get_current_time(to_seconds=False)

    update_info = dict(
        zone_id = sender["zone"],
        apply_id = apply_id,
        status = req.get("status", const.APPLY_FORM_STATUS_LOCKED),
        approve_status = const.APPLY_FORM_RESULT_APPROVING,
        apply_resource_type = req.get("apply_resource_type",const.APPLY_RESOURCE_TYPE_DESKTOP),
        start_time = req.get("start_time", curr_time),
        approve_group_id = req.get("approve_group_id", ""),
        end_time = req.get("end_time", curr_time),
        apply_group_id = apply_group_id if apply_group_id else '',
        create_time = get_current_time(to_seconds=False),
        update_time = get_current_time(to_seconds=False)
    )
    update_info.update(apply_form_info)

    # # register apply_form
    if not ctx.pg.insert(dbconst.TB_APPLY, update_info):
        logger.error("insert newly created apply form for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.CREATE_APPLY_FORM_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_APPLY_FORM_ERROR)

    return apply_id

def format_apply(apply_set):

    ctx = context.instance()
    for apply_id, _apply in apply_set.items():
        
        if _apply.get('apply_parameter'):
            apply_set[apply_id]['apply_parameter'] = json_load(apply_set[apply_id]['apply_parameter'])

        if _apply.get('approve_parameter'):
            apply_set[apply_id]['approve_parameter'] = json_load(apply_set[apply_id]['approve_parameter'])

        resource_group_id = _apply["resource_group_id"]
        if resource_group_id:
            if resource_group_id.startswith(const.UUID_TYPE_DELIVERY_GROUP):
                ret = ctx.pgm.get_delivery_group(resource_group_id)
                if ret:
                    delivery_group_name = ret["delivery_group_name"]
                    _apply["resource_group_name"] = delivery_group_name
            elif resource_group_id.startswith(const.UUID_TYPE_DESKTOP_GROUP):
                ret = ctx.pgm.get_desktop_group(resource_group_id, extras=[])
                if ret:
                    desktop_group_name = ret["desktop_group_name"]
                    _apply["resource_group_name"] = desktop_group_name
        
        resource_id = _apply["resource_id"]
        if resource_id:
            if resource_id.startswith(const.UUID_TYPE_DESKTOP):
                ret = ctx.pgm.get_desktops(resource_id)
                if ret:
                    desktop = ret[resource_id]
                    desktop_name = desktop["hostname"]
                    _apply["resource_name"] = desktop_name

        apply_user_id = _apply["apply_user_id"]
        apply_user = ctx.pgm.get_desktop_user_detail(user_id=apply_user_id)
        if apply_user:
            _apply["apply_user_name"] = apply_user["user_name"]
            _apply["apply_real_name"] = apply_user["real_name"]
            _apply["apply_ou_dn"] = apply_user["ou_dn"]

        approve_user_id = _apply["approve_user_id"]
        approve_user = ctx.pgm.get_desktop_user_detail(user_id=approve_user_id)
        if approve_user:
            _apply["approve_user_name"] = approve_user["user_name"]
            _apply["approve_real_name"] = approve_user["real_name"]
            _apply["approve_ou_dn"] = approve_user["ou_dn"]
        
        apply_group_id = _apply["apply_group_id"]
        if apply_group_id:
            approve_groups = get_approve_users(apply_group_id)
            if approve_groups:
                _apply["approve_groups"] = approve_groups.values()

    return None

def check_apply_form_valid(apply_form_ids):
    
    ctx = context.instance()
    
    if not isinstance(apply_form_ids, list):
        apply_form_ids = [apply_form_ids]
    
    ret = refresh_apply_forms(apply_form_ids)
    if isinstance(ret, Error):
        return ret
    
    apply_forms = ctx.pgm.get_apply_forms(apply_form_ids, status=const.APPLY_FORM_VAILD_STATUS)
    if not apply_forms:
        apply_forms = {} 
    
    for apply_form_id in apply_form_ids:
        apply_form = apply_forms.get(apply_form_id)
        if not apply_form:
            logger.error("no found apply form %s" % apply_form_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_APPLY_FORM_NOT_EXISTED_ERROR, apply_form_ids)
    
    return apply_forms

def modify_apply_form(apply_id, need_maint_columns):

    ctx = context.instance()

    if not ctx.pg.batch_update(dbconst.TB_APPLY, {apply_id: need_maint_columns}):
        logger.error("modify apply form update db fail %s" % need_maint_columns)
        return Error(ErrorCodes.MODIFY_APPLY_FORM_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_APPLY_FORM_ERROR)

    return None

def check_modify_apply_form(sender, apply_forms):

    for _, apply_form in apply_forms.items():

        if sender["owner"] == apply_form["apply_user_id"]:
            if apply_form["approve_status"] != const.APPLY_FORM_RESULT_APPROVING:
                logger.error("normal user %s cant delete apply form" % sender["owner"])
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_NORMAL_USER_CANT_DELETE_APPLY_FORM, sender["owner"])
        
    return

def delete_apply_form(apply_ids):

    ctx = context.instance()
    
    condition = {"apply_id": apply_ids}
    
    ctx.pg.base_delete(dbconst.TB_APPLY, condition)

    return None

def modify_apply_form_status(apply_id, update_apply_attrs):

    ctx = context.instance()
    ret = ctx.pgm.get_apply_forms(apply_ids=apply_id)
    if not ret:
        logger.error("apply form no found %s" % apply_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_APPLY_FORM_NOT_EXISTED_ERROR, apply_id)

    update_apply_form = {}
    apply_form_info = dict(
        status=update_apply_attrs.get("status"),
        approve_parameter=update_apply_attrs.get("approve_parameter", ""),
        approve_advice=update_apply_attrs.get("approve_advice"),
        apply_age=update_apply_attrs.get("apply_age",-1),
        update_time=get_current_time(to_seconds=False)
    )
    if update_apply_attrs.get("start_time"):
        apply_form_info["start_time"] = update_apply_attrs.get("start_time")
    if update_apply_attrs.get("end_time"):
        apply_form_info["end_time"] = update_apply_attrs.get("end_time")
    update_apply_form[apply_id] = apply_form_info

    if not ctx.pg.batch_update(dbconst.TB_APPLY, update_apply_form):
        logger.error("modify apply form update db fail %s" % update_apply_form)
        return Error(ErrorCodes.MODIFY_APPLY_FORM_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_APPLY_FORM_ERROR)

    return None

def check_deal_desktop_apply_form(apply_form, apporve_user_id):
    
    approve_status = apply_form["approve_status"]
    if apporve_user_id != apply_form["approve_user_id"]:
        logger.error("apprrove user dismatch %s" % apporve_user_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_APPLY_FORM_NOT_EXISTED_ERROR, apporve_user_id)
    
    if approve_status != const.APPLY_FORM_RESULT_APPROVING:
        logger.error("apprrove user dismatch %s" % apporve_user_id)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_APPLY_FORM_NOT_EXISTED_ERROR, apporve_user_id)
    
    return

def deal_desktop_apply_form(apply_form, result, start_time, end_time):

    ctx = context.instance()
    apply_id = apply_form["apply_id"]
    
    update_apply_form = {"approve_status": result}
    if result == const.APPLY_FORM_RESULT_PASSED:
        update_apply_form["status"] = const.APPLY_FORM_STATUS_EFFECTIVE
    elif result == const.APPLY_FORM_RESULT_REJECTED:
        update_apply_form["status"] = const.APPLY_FORM_STATUS_FINISHED
    
    if start_time:
        update_apply_form["start_time"] = start_time
    
    if end_time:
        update_apply_form["end_time"] = end_time
    
    if not ctx.pg.batch_update(dbconst.TB_APPLY, {apply_id: update_apply_form}):
        logger.error("modify apply form update db fail %s" % update_apply_form)
        return Error(ErrorCodes.MODIFY_APPLY_FORM_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_APPLY_FORM_ERROR)

    return None

def clear_user_apply_form(user_ids):
    ctx = context.instance()
    condition = {'apply_user_id': user_ids}
    try:
        if ctx.pg.base_delete(dbconst.TB_APPLY, condition) < 0:
            logger.error("delete apply form [%s] failed" % (condition))
            return Error(ErrorCodes.DELETE_APPLY_FORM_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_APPLY_FORM_ERROR)

        return True
    except Exception, e:
        logger.error("delete apply form with Exception:%s" % (e))
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def build_apply_group(req):

    apply_group = {}
    apply_group_key = ["apply_group_name", "description"]

    for key in apply_group_key:
        if key not in req:
            continue
        apply_group[key] = req[key]

    return apply_group

def create_apply_group_form(sender, req):

    ctx = context.instance()
    apply_group_id = get_uuid(UUID_TYPE_APPLY_GROUP_FORM, ctx.checker)
    apply_group_info = build_apply_group(req)

    update_info = dict(
        zone_id=sender["zone"],
        apply_group_id=apply_group_id,
        create_time=get_current_time(to_seconds=False),
        update_time=get_current_time(to_seconds=False)
    )
    update_info.update(apply_group_info)

    # # register apply_group
    if not ctx.pg.insert(dbconst.TB_APPLY_GROUP, update_info):
        logger.error("insert newly created apply group for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.CREATE_APPLY_GROUP_FORM_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_APPLY_GROUP_FORM_ERROR)

    return apply_group_id

def check_apply_group_valid(apply_group_ids):
    
    ctx = context.instance()
    if not isinstance(apply_group_ids, list):
        apply_group_ids = [apply_group_ids]
    
    apply_groups = ctx.pgm.get_apply_groups(apply_group_ids)
    if not apply_groups:
        apply_groups = {}
    
    for apply_group_id in apply_group_ids:
        apply_group = apply_groups.get(apply_group_id)
        if not apply_group:
            logger.error("apply group no found %s" % apply_group_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_APPLY_GROUP_FORM_NO_FOUND, apply_group_id)
    return None

def modify_apply_group(apply_group_id, need_maint_columns):

    ctx = context.instance()

    if not ctx.pg.batch_update(dbconst.TB_APPLY_GROUP, {apply_group_id: need_maint_columns}):
        logger.error("modify apply_group update db fail %s" % need_maint_columns)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_APPLY_GROUP_FORM_ERROR)

    return None

def check_apply_group_resource(zone_id):
    
    ctx = context.instance()
    
    if is_citrix_platform(ctx, zone_id):
        resource_groups = ctx.pgm.get_delivery_groups(zone_id=zone_id)
        if not resource_groups:
            return None
        
    else:
        resource_groups = ctx.pgm.get_desktop_groups(zone_id=zone_id)
        if not resource_groups:
            return None
    
    resource_group_ids = resource_groups.keys()
    ret = ctx.pgm.get_apply_group_resources(resource_ids= resource_group_ids)
    if not ret:
        return resource_groups
    
    existed_resource_groups = ret
    
    return_resource_groups = {}
    for resource_group_id, resource_group in resource_groups.items():
        if resource_group_id in existed_resource_groups:
            continue
        return_resource_groups[resource_group_id] = resource_group
    
    return return_resource_groups

def format_apply_group(apply_group_set, check_resource_group=0):

    ctx = context.instance()

    for apply_group_id, apply_group in apply_group_set.items():

        users = ctx.pgm.get_apply_group_user(apply_group_id)
        if not users:
            users = {}

        ret = ctx.pgm.get_user_and_user_group_names(users.keys())
        if ret:
            for user_id, user in users.items():
                user["user_name"] = ret.get(user_id, '')
                # get user_dn
                desktop_users = ctx.pgm.get_desktop_users(user_ids=user_id,columns=["user_id", "user_name", "real_name", "user_dn"])
                if desktop_users:
                    for _, desktop_user in desktop_users.items():
                        user["user_dn"] = desktop_user["user_dn"]

        apply_group["user_set"] = users.values()
        apply_group["user_set_count"] = len(users)

        apply_group_resources = describe_apply_group_resources(apply_group_id)
        if not isinstance(apply_group_resources, Error) and len(apply_group_resources)>0:
            resource_ids = apply_group_resources.keys()
            if resource_ids[0].startswith(UUID_TYPE_DESKTOP_GROUP):
                resources = ctx.pgm.get_desktop_groups(desktop_group_ids=resource_ids,
                                                       columns=["desktop_group_id","desktop_group_name","cpu","memory","instance_class","status","desktop_group_type"])
                if resources:
                    for resource in resources.values():
                        resource["create_time"] = apply_group_resources[resource["desktop_group_id"]]
                    apply_group["resource_set"] = resources.values()
                    apply_group["resource_set_count"] = len(resources.values())

            if resource_ids[0].startswith(UUID_TYPE_DELIVERY_GROUP):
                resources = ctx.pgm.get_delivery_groups(delivery_group_ids=resource_ids,
                                                        columns=["delivery_group_id","delivery_group_name","mode","desktop_kind","allocation_type","delivery_group_type"])
                if resources:
                    for resource in resources.values():
                        resource["create_time"] = apply_group_resources[resource["delivery_group_id"]]
                    apply_group["resource_set"] = resources.values()
                    apply_group["resource_set_count"] = len(resources.values())
        
        approve_group_map = describe_map_apply_group_and_approve_group(apply_group_id, None)
        approve_apply_groups = []
        if approve_group_map is not None:
            for approve_group in approve_group_map:
                approve_group_id = approve_group["approve_group_id"]
                approve_group_info = get_resource_approve_group(approve_group_id)
                approve_apply_groups.append(approve_group_info)
            apply_group["approve_group_set"] = approve_apply_groups
            apply_group["approve_group_set_count"] = len(approve_apply_groups)
        
        if check_resource_group:
            ret = check_apply_group_resource(apply_group["zone_id"])
            if ret:
                apply_group["resource_groups"] = ret.values()

    return None

def delete_apply_group_form(apply_group_ids):

    ctx = context.instance()

    for apply_group_id in apply_group_ids:
        
        ret = remove_user_from_apply_group(apply_group_ids)
        if isinstance(ret, Error):
            return ret

        ret = remove_resource_from_apply_group(apply_group_id)
        if isinstance(ret, Error):
            return ret

        ret = detach_approve_group_from_apply_group(apply_group_id)
        if isinstance(ret, Error):
            return ret

        ctx.pg.delete(dbconst.TB_APPLY_GROUP, apply_group_id)

    return None

def check_apply_group_user_valid(apply_group_id, user_ids, is_add=False):

    ctx = context.instance()

    desktop_user_ids = []
    desktop_user_group_ids = []
    
    apply_group_users = ctx.pgm.get_apply_group_user(apply_group_id, user_ids)
    if not apply_group_users:
        apply_group_users = {}

    for user_id in user_ids:
        if user_id.startswith(UUID_TYPE_DESKTOP_USER):
            desktop_user_ids.append(user_id)
        elif user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
            desktop_user_group_ids.append(user_id)
    
    desktop_users = {}
    if desktop_user_ids:
        ret = ctx.pgm.get_desktop_users(desktop_user_ids)
        if ret:
            desktop_users = ret
            
    desktop_user_groups = {}
    if desktop_user_group_ids:
        ret = ctx.pgm.get_desktop_user_groups(user_group_ids=desktop_user_group_ids)
        if ret:
            desktop_user_groups = ret
            
    for user_id in user_ids:
        desktop_user = desktop_users.get(user_id)
        desktop_user_group = desktop_user_groups.get(user_id)
        
        if not desktop_user and not desktop_user_group:
            logger.error("add user to apply no found user %s" % user_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_AUTH_USER_NO_FOUND, user_id)
            
        apply_group_user = apply_group_users.get(user_id)
        if is_add and apply_group_user:
            logger.error("user already existed in apply group %s" % user_id)
            return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                         ErrorMsg.ERR_MSG_USER_EXISTED_IN_APPLY_GROUP, user_id)

    return user_ids

def insert_user_to_apply_group(apply_group_id,user_ids):

    ctx = context.instance()

    update_info = {}
    for user_id in user_ids:
        
        user_type = const.USER_TYPE_USER
        if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
            user_type = const.USER_TYPE_GROUP
      
        apply_group_user_info = {
            "apply_group_id": apply_group_id,
            "user_id": user_id,
            "user_type": user_type
        }
        
        update_info[user_id] = apply_group_user_info

    if not ctx.pg.batch_insert(dbconst.TB_APPLY_GROUP_USER, update_info):
        logger.error("insert apply group  user form [%s] failed." % (update_info))
        return Error(ErrorCodes.INSERT_APPLY_GROUP_USER_FORM_ERROR,
                     ErrorMsg.ERR_MSG_INSERT_APPLY_GROUP_USER_FORM_ERROR)

    return True

def update_apply_form_status(apply_group_id=None,
                             user_ids=None, 
                             resource_ids=None,
                             apply_form_ids=None,
                             approve_group_id=None,
                             approve_user_ids=None,
                             status = const.APPLY_FORM_STATUS_LOCKED,
                             set_status=const.APPLY_FORM_STATUS_FINISHED,
                             set_result = const.APPLY_FORM_RESULT_CLOSED):
    
    ctx = context.instance()
    apply_forms = {}
    if apply_form_ids:
        ret = ctx.pgm.get_apply_forms(apply_form_ids)
        if not ret:
            return None
        
        apply_forms = ret
    
    if not apply_form_ids:
        ret = ctx.pgm.get_user_apply_forms(apply_group_id=apply_group_id, 
                                           approve_group_id=approve_group_id, 
                                           user_id=user_ids, 
                                           resource_ids=resource_ids, 
                                           approve_user_ids=approve_user_ids,
                                           status=status)
        if not ret:
            return None
        
        apply_forms = ret
    
    update_apply_form = {}
    for apply_id, apply_form in apply_forms.items():
        
        status = apply_form["status"]
        if status not in const.APPLY_FORM_VAILD_STATUS:
            continue

        update_apply_form[apply_id] = {
            "status": set_status,
            "approve_status": set_result
            }
    if not update_apply_form:
        return None
    
    if not ctx.pg.batch_update(dbconst.TB_APPLY, update_apply_form):
        logger.error("update apply_form user status update db fail %s" % update_apply_form)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None 

def remove_user_from_apply_group(apply_group_id, user_ids=None):

    ctx = context.instance()
    
    if not user_ids:
        ret = ctx.pgm.get_apply_group_user(apply_group_id)
        if not ret:
            return None
        user_ids = ret.keys()
    
    ret = update_apply_form_status(apply_group_id, user_ids, status=const.APPLY_FORM_VAILD_STATUS)
    if isinstance(ret, Error):
        return ret

    conditions = {"apply_group_id": apply_group_id, "user_id": user_ids}
    ctx.pg.base_delete(dbconst.TB_APPLY_GROUP_USER, conditions)

def describe_apply_group_users(apply_group_id=None):
    ctx = context.instance()
    try:
        conditions={}
        if apply_group_id:
            conditions["apply_group_id"] = apply_group_id
        ret = ctx.pg.base_get(dbconst.TB_APPLY_GROUP_USER,
                              condition=conditions, 
                              columns=["user_id", "create_time"])
        if ret is None:
            logger.error("describe apply group user form [%s] failed" % (apply_group_id))
            return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_DATE_NOT_FOUND)
        apply_group_users = {}
        for item in ret:
            apply_group_users[item["user_id"]] = item["create_time"]
        return apply_group_users
    except Exception, e:
        logger.error("describe apply group user form  with Exception:%s" % (e))
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def describe_user_in_apply_groups(user_id):
    ctx = context.instance()
    try:
        ret = ctx.pg.base_get(dbconst.TB_APPLY_GROUP_USER,
                              condition={"user_id": user_id}, 
                              columns=["apply_group_id"])
        if ret is None:
            logger.error("describe user [%s] in apply group failed" % (user_id))
            return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_DATE_NOT_FOUND)
        apply_group_ids = []
        for item in ret:
            apply_group_ids.append(item["apply_group_id"])
        return apply_group_ids
    except Exception, e:
        logger.error("describe user in apply group with Exception:%s" % (e))
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def describe_user_in_approve_groups(user_id):
    ctx = context.instance()
    try:
        ret = ctx.pg.base_get(dbconst.TB_APPROVE_GROUP_USER,
                              condition={"user_id": user_id}, 
                              columns=["approve_group_id"])
        if ret is None:
            logger.error("describe user [%s] in apply group failed" % (user_id))
            return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_DATE_NOT_FOUND)
        approve_group_ids = []
        for item in ret:
            approve_group_ids.append(item["approve_group_id"])
        return approve_group_ids
    except Exception, e:
        logger.error("describe user in apply group with Exception:%s" % (e))
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def describe_resource_in_apply_groups(resource_id):
    ctx = context.instance()
    try:
        ret = ctx.pg.base_get(dbconst.TB_APPLY_GROUP_RESOURCE,
                              condition={"resource_id": resource_id}, 
                              columns=["apply_group_id"])
        if ret is None:
            logger.error("describe resource [%s] in apply group failed" % (resource_id))
            return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_DATE_NOT_FOUND)
        apply_group_ids = []
        for item in ret:
            apply_group_ids.append(item["apply_group_id"])
        return apply_group_ids
    except Exception, e:
        logger.error("describe resource in apply group with Exception:%s" % (e))
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)


def describe_approve_group_users(approve_group_id=None):
    ctx = context.instance()
    try:
        conditions = {}
        if approve_group_id:
            conditions["approve_group_id"] = approve_group_id
        ret = ctx.pg.base_get(dbconst.TB_APPROVE_GROUP_USER,
                              condition=conditions, 
                              columns=["user_id", "create_time"])
        if ret is None:
            logger.error("describe approve group user form [%s] failed" % (approve_group_id))
            return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_DATE_NOT_FOUND)

        approve_group_users = {}
        for item in ret:
            approve_group_users[item["user_id"]] = item["create_time"]
        return approve_group_users
    except Exception, e:
        logger.error("describe approve group user form  with Exception: %s" % (e))
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)

def describe_apply_group_resources(apply_group_id):
    ctx = context.instance()
    try:
        ret = ctx.pg.base_get(dbconst.TB_APPLY_GROUP_RESOURCE,
                              condition={"apply_group_id": apply_group_id}, 
                              columns=["resource_id", "create_time"])
        if ret is None:
            logger.error("describe apply group resource form [%s] failed" % (apply_group_id))
            return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_DATE_NOT_FOUND)
        apply_group_resources = {}
        for item in ret:
            apply_group_resources[item["resource_id"]] = item["create_time"]
        return apply_group_resources
    except Exception, e:
        logger.error("remove apply group resource form  with Exception:%s" % (e))
        return Error(ErrorCodes.DATABASE_OPERATION_EXCEPTION,
                         ErrorMsg.ERR_MSG_DATABASE_OPERATION_EXCEPTION)


def get_resource_apply_group(apply_group_id):
    ctx = context.instance()

    conds = {}
    if apply_group_id:
        conds['apply_group_id'] = apply_group_id

    ret = ctx.pg.base_get(dbconst.TB_APPLY_GROUP, conds)
    if ret is None or len(ret)==0:
        return None

    return ret[0]

def get_resource_approve_group(approve_group_id):
    ctx = context.instance()

    conds = {}
    if approve_group_id:
        conds['approve_group_id'] = approve_group_id

    ret = ctx.pg.base_get(dbconst.TB_APPROVE_GROUP, conds)
    if ret is None or len(ret)==0:
        return None

    return ret[0]

def build_approve_group(req):

    approve_group = {}
    approve_group_key = ["approve_group_name", "description"]

    for key in approve_group_key:
        if key not in req:
            continue
        approve_group[key] = req[key]

    return approve_group

def create_approve_group_form(sender, req):

    ctx = context.instance()
    approve_group_id = get_uuid(UUID_TYPE_APPROVE_GROUP_FORM, ctx.checker)
    approve_group_info = build_approve_group(req)

    update_info = dict(
        zone_id=sender["zone"],
        approve_group_id=approve_group_id,
        create_time=get_current_time(to_seconds=False),
        update_time=get_current_time(to_seconds=False)
    )
    update_info.update(approve_group_info)

    # # register approve_group
    if not ctx.pg.insert(dbconst.TB_APPROVE_GROUP, update_info):
        logger.error("insert newly created approve group for [%s] to db failed" % (update_info))
        return Error(ErrorCodes.CREATE_APPROVE_GROUP_FORM_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_APPROVE_GROUP_FORM_ERROR)

    return approve_group_id

def check_approve_group_vaild(approve_group_ids):
    
    ctx = context.instance()
    if not isinstance(approve_group_ids, list):
        approve_group_ids = [approve_group_ids]
    
    approve_groups = ctx.pgm.get_approve_groups(approve_group_ids)
    if not approve_groups:
        approve_groups = {}
    
    for approve_group_id in approve_group_ids:
        approve_group = approve_groups.get(approve_group_id)
        if not approve_group:
            logger.error("approve group no found %s" % approve_group_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_APPLY_GROUP_FORM_NO_FOUND, approve_group_id)
    return None

def modify_approve_group_form(approve_group_id, need_maint_columns):

    ctx = context.instance()
    if not ctx.pg.batch_update(dbconst.TB_APPROVE_GROUP, {approve_group_id: need_maint_columns}):
        logger.error("modify approve group update db fail %s" % need_maint_columns)
        return Error(ErrorCodes.MODIFY_APPROVE_GROUP_FORM_ERROR,
                     ErrorMsg.ERR_MSG_MODIFY_APPROVE_GROUP_FORM_ERROR)

    return None

def format_approve_group(approve_group_set):

    ctx = context.instance()

    for approve_group_id, approve_group in approve_group_set.items():

        users = ctx.pgm.get_approve_group_user(approve_group_id)
        if not users:
            users = {}

        ret = ctx.pgm.get_user_and_user_group_names(users.keys())
        if ret:
            for user_id, user in users.items():
                user["user_name"] = ret.get(user_id, '')
                # get user_dn
                desktop_users = ctx.pgm.get_desktop_users(user_ids=user_id,columns=["user_id", "user_name", "real_name", "user_dn"])
                if desktop_users:
                    for _, desktop_user in desktop_users.items():
                        user["user_dn"] = desktop_user["user_dn"]

        approve_group["user_set"] = users.values()
        approve_group["user_set_count"] = len(users)

        apply_group_map = describe_map_apply_group_and_approve_group(None, approve_group_id)
        apply_groups = []
        if apply_group_map is not None:
            for apply_group in apply_group_map:
                apply_group_id = apply_group["apply_group_id"]
                apply_group_info = get_resource_apply_group(apply_group_id)
                apply_groups.append(apply_group_info)
            approve_group["apply_group_set"] = apply_groups
            approve_group["apply_group_set_count"] = len(apply_groups)

    return None

def delete_approve_group_form(sender,approve_group_ids):

    ctx = context.instance()
    ret = ctx.pgm.get_approve_groups(approve_group_ids=approve_group_ids)
    if not ret:
        logger.error("approve group no found %s" % approve_group_ids)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_APPROVE_GROUP_FORM_NO_FOUND, approve_group_ids)
    approve_groups = ret
    for approve_group_id, _ in approve_groups.items():

        condition = {'approve_group_id': approve_group_id}
        if not ctx.pg.base_delete(dbconst.TB_APPROVE_GROUP, condition):
            logger.error("delete approve group %s fail" % approve_group_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_APPROVE_GROUP_FORM_ERROR,approve_group_id)

    return None

def check_approve_group_user_valid(approve_group_id, user_ids, is_add=False):

    ctx = context.instance()

    desktop_user_ids = []
    desktop_user_group_ids = []
    
    approve_group_users = ctx.pgm.get_approve_group_user(approve_group_id, user_ids)
    if not approve_group_users:
        approve_group_users = {}

    for user_id in user_ids:
        if user_id.startswith(UUID_TYPE_DESKTOP_USER):
            desktop_user_ids.append(user_id)
        elif user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
            desktop_user_group_ids.append(user_id)
    
    desktop_users = {}
    if desktop_user_ids:
        ret = ctx.pgm.get_desktop_users(desktop_user_ids)
        if ret:
            desktop_users = ret
            
    desktop_user_groups = {}
    if desktop_user_group_ids:
        ret = ctx.pgm.get_desktop_user_groups(user_group_ids=desktop_user_group_ids)
        if ret:
            desktop_user_groups = ret
            
    for user_id in user_ids:
        desktop_user = desktop_users.get(user_id)
        desktop_user_group = desktop_user_groups.get(user_id)
        
        if not desktop_user and not desktop_user_group:
            logger.error("add user to apply no found user %s" % user_id)
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_AUTH_USER_NO_FOUND, user_id)
            
        approve_group_user = approve_group_users.get(user_id)
        if is_add and approve_group_user:
            logger.error("user already existed in apply group %s" % user_id)
            return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                         ErrorMsg.ERR_MSG_USER_EXISTED_IN_APPROVE_GROUP, user_id)

    return user_ids

def insert_user_to_approve_group(approve_group_id,user_ids):
    
    ctx = context.instance()
    update_info = {}
    for user_id in user_ids:
        
        user_type = const.USER_TYPE_USER
        if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
            user_type = const.USER_TYPE_GROUP
      
        approve_group_user_info = {
            "approve_group_id": approve_group_id,
            "user_id": user_id,
            "user_type": user_type
        }
        
        update_info[user_id] = approve_group_user_info

    if not ctx.pg.batch_insert(dbconst.TB_APPROVE_GROUP_USER, update_info):
        logger.error("insert approve group  user form [%s] failed." % (update_info))
        return Error(ErrorCodes.INSERT_APPLY_GROUP_USER_FORM_ERROR,
                     ErrorMsg.ERR_MSG_INSERT_APPROVE_GROUP_USER_FORM_ERROR)

    return True

def delete_resource_approve_groups(approve_group_ids):
    
    ctx = context.instance()
    for approve_group_id in approve_group_ids:

        ret = remove_user_from_approve_group(approve_group_id)
        if isinstance(ret, Error):
            return ret
        
        ret = detach_apply_group_from_approve_group(approve_group_id)
        if isinstance(ret, Error):
            return ret
        
        ctx.pg.delete(dbconst.TB_APPROVE_GROUP, approve_group_id)
        
    return None

def remove_user_from_approve_group(approve_group_id, user_ids=None):

    ctx = context.instance()

    if not user_ids:
        ret = ctx.pgm.get_approve_group_user(approve_group_id)
        if not ret:
            return None
        user_ids = ret.keys()

    ret = update_apply_form_status(approve_group_id=approve_group_id, approve_user_ids=user_ids)
    if isinstance(ret, Error):
        return ret

    conditions = {"approve_group_id": approve_group_id, "user_id": user_ids}
    ctx.pg.base_delete(dbconst.TB_APPROVE_GROUP_USER, conditions)

    return True

def check_add_resource_to_apply_group(apply_group_id, resource_ids):
    
    ctx = context.instance()

    ret = ctx.pgm.get_apply_group_resources(apply_group_id, resource_ids)
    if ret:
        logger.error("insert apply group  user form [%s] failed." % (resource_ids))
        return Error(ErrorCodes.RESOURCE_ALREADY_EXISTED,
                     ErrorMsg.ERR_MSG_RESOURCE_EXISTED_IN_APPLY_GROUP, resource_ids)

    return None

def insert_resource_to_apply_group(apply_group_id, resource_ids):

    ctx = context.instance()
    apply_group_resource_form = {}
    for resource_id in resource_ids:
        apply_group_resource_form[resource_id] = {
                                                "apply_group_id": apply_group_id,
                                                "resource_id": resource_id
                                                }

    if not ctx.pg.batch_insert(dbconst.TB_APPLY_GROUP_RESOURCE, apply_group_resource_form):
        logger.error("insert apply group  user form [%s] failed." % (apply_group_resource_form))
        return Error(ErrorCodes.INSERT_APPLY_GROUP_RESOURCE_FORM_ERROR,
                     ErrorMsg.ERR_MSG_INSERT_APPLY_GROUP_RESOURCE_FORM_ERROR)
    return None

def remove_resource_from_apply_group(apply_group_id, resource_ids=None):

    ctx = context.instance()
    if not resource_ids:
        ret = ctx.pgm.get_apply_group_resources(apply_group_id)
        if not ret:
            return None
        
        resource_ids = ret.keys()
    
    ret = update_apply_form_status(apply_group_id, resource_ids=resource_ids, status=const.APPLY_FORM_VAILD_STATUS)
    if isinstance(ret, Error):
        return ret
    
    conditions = {"apply_group_id": apply_group_id,
                  "resource_id": resource_ids
                  }
    
    ctx.pg.base_delete(dbconst.TB_APPLY_GROUP_RESOURCE, conditions)

def clean_user_in_apply_group(user_ids):
    ctx = context.instance()
    condition = {'user_id': user_ids}

    try:
        if ctx.pg.base_delete(dbconst.TB_APPLY_GROUP_USER, condition) < 0:
            logger.error("delete user from apply group [%s] failed" % (condition))
            return False

        return True
    except Exception, e:
        logger.error("delete user from apply group with Exception:%s" % (e))
        return False

def clean_user_in_approve_group(user_ids):
    ctx = context.instance()
    condition = {'user_id': user_ids}

    try:
        if ctx.pg.base_delete(dbconst.TB_APPROVE_GROUP_USER, condition) < 0:
            logger.error("delete user from approve group [%s] failed" % (condition))
            return False

        return True
    except Exception, e:
        logger.error("delete user from apply group with Exception:%s" % (e))
        return False

def clean_resource_in_apply_group(resource_ids):
    ctx = context.instance()
    condition = {'resource_id': resource_ids}

    try:
        if ctx.pg.base_delete(dbconst.TB_APPLY_GROUP_RESOURCE, condition) < 0:
            logger.error("delete resource from apply group [%s] failed" % (condition))
            return False

        return True
    except Exception, e:
        logger.error("delete resource from apply group with Exception:%s" % (e))
        return False

def user_is_in_apply_group(user_id):
    ctx = context.instance()
    ret = ctx.pgm.get_apply_group_user(user_ids=user_id)
    if ret:
        return 1
    else:
        ret = ctx.pgm.get_user_group(user_id=user_id)
        if ret:
            user_groups = ret
            for user_group_id in user_groups:
                ret = ctx.pgm.get_apply_group_user(user_ids=user_group_id)
                if ret:
                    return 1
                else:
                    return 0
        else:
            return 0

def user_is_in_approve_group(user_id):
    ctx = context.instance()
    ret = ctx.pgm.get_approve_group_user(user_ids=user_id)
    if ret:
        return 1
    else:
        ret = ctx.pgm.get_user_group(user_id=user_id)
        if ret:
            user_groups = ret
            for user_group_id in user_groups:
                ret = ctx.pgm.get_approve_group_user(user_ids=user_group_id)
                if ret:
                    return 1
                else:
                    return 0
        else:
            return 0

def describe_map_apply_group_and_approve_group(apply_group_ids, approve_group_ids):
    ctx = context.instance()

    apply_approve_map = {}
    if apply_group_ids:
        apply_approve_map['apply_group_id'] = apply_group_ids
    if approve_group_ids:
        apply_approve_map['approve_group_id'] = approve_group_ids

    ret = ctx.pg.base_get(dbconst.TB_APPLY_APPROVE_GROUP_MAP, apply_approve_map)
    if ret is None:
        logger.error("describe map apply group and approve group failed. value: [%s]" % (apply_approve_map))
        return None

    return ret


def map_apply_group_and_approve_group(apply_group_id, approve_group_id):

    ctx = context.instance()

    curtime = get_current_time(to_seconds=False)
    apply_approve_map = {
        'apply_group_id': apply_group_id,
        'approve_group_id': approve_group_id,
        'create_time': curtime
        }

    if not ctx.pg.base_insert(dbconst.TB_APPLY_APPROVE_GROUP_MAP, apply_approve_map):
        logger.error("map apply group and approve group failed. value: [%s]" % (apply_approve_map))
        return Error(ErrorCodes.MAP_APPLY_GROUP_AND_APPROVE_GROUP_ERROR,
                     ErrorMsg.ERR_MSG_MAP_APPLY_GROUP_AND_APPROVE_GROUP_ERROR)

    return True

def detach_approve_group_from_apply_group(apply_group_id, approve_group_ids=None):

    ctx = context.instance()
    
    ret = ctx.pgm.get_approve_group_by_apply_group(apply_group_id, approve_group_ids)
    if not ret:
        return None
    
    approve_group_ids = ret
    
    apply_forms = ctx.pgm.get_apply_forms(apply_group_id=apply_group_id, approve_group_id=approve_group_ids)
    if not apply_forms:
        apply_forms = {}
    apply_form_ids = apply_forms.keys()
    
    ret = update_apply_form_status(apply_form_ids =apply_form_ids)
    if isinstance(ret, Error):
        return ret

    condition = {"apply_group_id":apply_group_id,"approve_group_id":approve_group_ids}

    ctx.pg.base_delete(dbconst.TB_APPLY_APPROVE_GROUP_MAP, condition)
    
    return None

def detach_apply_group_from_approve_group(approve_group_id, apply_group_ids=None):

    ctx = context.instance()
    
    ret = ctx.pgm.get_apply_group_by_approve_group(approve_group_id, apply_group_ids)
    if not ret:
        return None
    
    apply_group_ids = ret
    
    apply_forms = ctx.pgm.get_apply_forms(apply_group_id=apply_group_ids, approve_group_id=approve_group_id)
    if not apply_forms:
        apply_forms = {}
    apply_form_ids = apply_forms.keys()
    
    ret = update_apply_form_status(apply_form_ids =apply_form_ids)
    if isinstance(ret, Error):
        return ret

    condition = {"apply_group_id":apply_group_ids,"approve_group_id":approve_group_id}

    ctx.pg.base_delete(dbconst.TB_APPLY_APPROVE_GROUP_MAP, condition)
    
    return None

def unmap_apply_group_and_approve_group(apply_group_ids=None, approve_group_ids=None):

    ctx = context.instance()
    if apply_group_ids and approve_group_ids is None:
        for apply_group_id in apply_group_ids:

            ret = ctx.pgm.get_apply_approve_group_maps(apply_group_ids=apply_group_id)
            if not ret:
                continue
            apply_approve_group_maps = ret
            for approve_group_id,_ in apply_approve_group_maps.items():

                condition = {"apply_group_id":apply_group_id,"approve_group_id":approve_group_id}
                if not ctx.pg.base_delete(dbconst.TB_APPLY_APPROVE_GROUP_MAP, condition):
                    logger.error("unmap apply group and approve group failed. value: [%s]" % condition)
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_UNMAP_APPLY_GROUP_AND_APPROVE_GROUP_ERROR)

    if approve_group_ids and apply_group_ids is None:
        for approve_group_id in approve_group_ids:

            ret = ctx.pgm.get_approve_apply_group_maps(approve_group_ids=approve_group_id)
            if not ret:
                continue
            apply_approve_group_maps = ret
            for apply_group_id, _ in apply_approve_group_maps.items():

                condition = {"apply_group_id": apply_group_id, "approve_group_id": approve_group_id}
                if not ctx.pg.base_delete(dbconst.TB_APPLY_APPROVE_GROUP_MAP, condition):
                    logger.error("unmap apply group and approve group failed. value: [%s]" % condition)
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_UNMAP_APPLY_GROUP_AND_APPROVE_GROUP_ERROR)

    if approve_group_ids and apply_group_ids:

        condition = {"apply_group_id": apply_group_ids, "approve_group_id": approve_group_ids}
        if not ctx.pg.base_delete(dbconst.TB_APPLY_APPROVE_GROUP_MAP, condition):
            logger.error("unmap apply group and approve group failed. value: [%s]" % condition)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UNMAP_APPLY_GROUP_AND_APPROVE_GROUP_ERROR)

    return None

def check_approve_group_name(sender, approve_group_name, approve_group_id=None):

    ctx = context.instance()
    approve_group_names = ctx.pgm.get_approve_group_name(zone_id=sender["zone"])
    if not approve_group_names:
        return approve_group_name
    
    if approve_group_name.lower() in approve_group_names.values() and not approve_group_id:
        logger.error("approve_group_name already existd %s" % approve_group_name)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_APPROVE_GROUP_NAME_EXISTED_ERROR, approve_group_name)

    for _id, _name in approve_group_names.items():
        
        if _name == approve_group_name.lower() and _id != approve_group_id:
            logger.error("approve_group_name already existd %s" % approve_group_name)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_APPROVE_GROUP_NAME_EXISTED_ERROR, approve_group_name)
    return approve_group_name

def check_apply_group_name(sender, apply_group_name, apply_group_id=None):

    ctx = context.instance()
    apply_group_names = ctx.pgm.get_apply_group_name(zone_id=sender["zone"])
    if not apply_group_names:
        return apply_group_name

    if apply_group_name.lower() in apply_group_names.values() and not apply_group_id:
        logger.error("apply_group_name already existd %s" % apply_group_name)
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_APPLY_GROUP_NAME_EXISTED_ERROR, apply_group_name)
    
    for _id, _name in apply_group_names.items():
        if _name == apply_group_name.lower() and _id != apply_group_id:
            logger.error("apply_group_name already existd %s" % apply_group_name)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_APPLY_GROUP_NAME_EXISTED_ERROR, apply_group_name)
    return apply_group_name

def check_approve_apply_group_map(apply_group_id, approve_group_ids):
    
    ctx = context.instance()
    
    if not isinstance(approve_group_ids, list):
        approve_group_ids = [approve_group_ids]
    
    apply_approve_group_maps = ctx.pgm.get_apply_approve_group_maps(apply_group_id, approve_group_ids)
    if not apply_approve_group_maps:
        apply_approve_group_maps = {}
    
    for approve_group_id in approve_group_ids:
        if approve_group_id in apply_approve_group_maps:
            logger.error("approve_group already existd %s" % approve_group_id)
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_CREATE_APPROVE_GROUP_FORM_EXISTED_ERROR, approve_group_id)
    
    return None
