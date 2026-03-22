'''
Created on 2017-3-8

@author: yunify
'''
from log.logger import logger
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from common import (
    return_success, return_error, return_items
)
from utils.json import json_dump
from common import is_global_admin_user, is_admin_user, is_console_admin_user, is_normal_console, is_admin_console
from resource_control.permission import check_user_resource_permission
import resource_control.guest.guest as Guest
import context
from constants import INST_STATUS_RUN
from resource_control.desktop.desktop import send_desktop_job
import resource_control.guest.json_rpc as GuestJsonRpc
import constants as const
import db.constants as dbconst
from common import build_filter_conditions, get_sort_key, get_reverse


def handle_send_desktop_hot_keys(req):
    sender = req["sender"]
    ''' send desktop hot keys ''' 
    ctx = context.instance()
    desktop_ids = req.get("desktop_ids", [])
    if is_console_admin_user(req["sender"]) and not is_normal_console(req["sender"]):
        check_desktop_groups = ctx.pgm.get_group_by_desktop(desktop_ids)
        ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                          check_desktop_groups.keys(), 
                                          dbconst.RES_SCOPE_READONLY)
        if isinstance(ret, Error):
            return return_error(req, ret)
        if ret==None or len(ret)==0:
            return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                           ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                           (req['sender']["owner"], desktop_ids)))

    owner = None
    if is_normal_console(req["sender"]):
        if(len(desktop_ids) == 0):
            return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                           ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                           (req['sender']["owner"], desktop_ids)))
        owner = req["sender"]["owner"]
    
    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,owner=owner)
    if desktops is None:
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_CODE_MSG_RESOURCE_NOT_FOUND))

    instances = []
    for desktop_id in desktops.keys():
        hot_keys = {}
        hot_keys["keys"] = req.get("keys","")
        hot_keys["timeout"] = req.get("timeout",0)
        hot_keys["time_step"] = req.get("time_step",0)
        hot_keys["desktop_id"] = desktop_id
        instance_id = desktops[desktop_id].get("instance_id", None)
        if instance_id:
            instances.append(instance_id)

    if len(instances) > 0:
        extra = {
            "keys": req.get("keys",""),
            "timeout": req.get("timeout",0),
            "time_step":req.get("time_step",0)
            }
        ret = send_desktop_job(sender, desktops.keys(), const.JOB_ACTION_SEND_DESKTOP_HOT_KEYS, extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_id = ret
    
    ret = {"desktop_ids": desktops.keys()}
    return return_success(req, None, job_id, **ret)

def handle_modify_guest_server_config(req):

    ''' modify guest server config ''' 
    sender = req["sender"]
    ctx = context.instance()
    desktop_group_ids = req.get("desktop_group_ids")
    desktop_ids = req.get("desktop_ids", [])
    if not desktop_ids and not desktop_group_ids:
        return return_success(req, {"desktop_ids": []})

    guest_server_config = req.get("guest_server_config")
    if not guest_server_config:
        logger.error("guest_server_config is %s" % guest_server_config)
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE, 
                                       ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "guest_server_config"))
    
    desktops = None
    if is_console_admin_user(req["sender"]) and not is_normal_console(req["sender"]):
        if desktop_ids:
            check_desktop_groups = ctx.pgm.get_group_by_desktop(desktop_ids)
            ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                              check_desktop_groups.keys(), 
                                              dbconst.RES_SCOPE_READONLY)
            if isinstance(ret, Error):
                return return_error(req, ret)
            if ret==None or len(ret)==0:
                return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                               ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                               (req['sender']["owner"], desktop_ids)))
        if desktop_group_ids:
            ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                              desktop_group_ids, 
                                              dbconst.RES_SCOPE_READONLY)
            if isinstance(ret, Error):
                return return_error(req, ret)
            if ret==None or len(ret)==0:
                return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                               ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                               (req['sender']["owner"], desktop_group_ids)))

        if desktop_ids:
            desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)

        dg_desktops = None
        if desktop_group_ids:
            dg_desktops = ctx.pgm.get_desktops(status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)
    
        if desktops:
            if dg_desktops:
                desktops.update(dg_desktops)
        else:
            if dg_desktops:
                desktops = dg_desktops
    
    if is_normal_console(req["sender"]):
        if(len(desktop_ids) == 0):
            return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                           ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                           (req['sender']["owner"], desktop_group_ids)))
        owner = req["sender"]["owner"]
    
        ctx = context.instance()
        desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,owner=owner)
        if desktops is None:
            return return_success(req, {"desktop_ids": desktop_ids})

    if is_global_admin_user(req["sender"]):
        desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)

    if desktops is None or len(desktops) == 0:
        return return_success(req, {"desktop_ids": []})

    
    extra = {
        "guest_server_config": guest_server_config
        }
    ret = send_desktop_job(sender, desktops.keys(), const.JOB_ACTION_VDI_MODIFY_GUEST_SERVER_CONFIG, extra)
    if isinstance(ret, Error):
        return return_error(req, ret)
    job_id = ret

    ret = {"desktop_ids": desktops.keys()}
    return return_success(req, None, job_id, **ret) 

def handle_send_desktop_message(req):
    sender = req["sender"]
    ''' send desktop message ''' 
    if not is_admin_user(req["sender"]):
        logger.error("only admin can send guest message.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))

    desktop_group_ids = req.get("desktop_group_ids")
    desktop_ids = req.get("desktop_ids")
    
    if not desktop_ids and not desktop_group_ids:
        return return_success(req, {"desktop_ids": []})

    desktops = None
    ctx = context.instance()
    if desktop_ids:
        desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)

    dg_desktops = None
    if desktop_group_ids:
        dg_desktops = ctx.pgm.get_desktops(status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)
    
    if desktops:
        if dg_desktops:
            desktops.update(dg_desktops)
    else:
        if dg_desktops:
            desktops = dg_desktops
    if desktops is None:
        return return_success(req, {"desktop_ids": []})

    if not is_global_admin_user(req["sender"]):
        check_desktop_groups = ctx.pgm.get_group_by_desktop(desktops.keys())
        ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                          check_desktop_groups.keys(), 
                                          dbconst.RES_SCOPE_READONLY)
        if isinstance(ret, Error):
            return return_error(req, ret)
        if ret==None or len(ret)==0:
            return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                           ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                           (req['sender']["owner"], desktops.keys())))

    if len(desktops) > 0:
        message = {}
        message["message"] = req.get("base64_message","")
        message["desktop_id"] = json_dump(desktops.keys)
        ret = Guest.create_desktop_message(message)
        if isinstance(ret, Error):
            return_error(req, ret)

        extra = {"base64_message": req.get("base64_message","")}
        ret = send_desktop_job(sender, desktops.keys(), const.JOB_ACTION_SEND_DESKTOP_MESSAGE, extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_id = ret
    
    ret = {"desktop_ids": desktops.keys()}
    return return_success(req, None, job_id, **ret)

def handle_send_desktop_notify(req):
    sender = req["sender"]
    ctx = context.instance()
    desktop_group_ids = req.get("desktop_group_ids")
    desktop_ids = req.get("desktop_ids", [])
    if not desktop_ids and not desktop_group_ids:
        return return_success(req, {"desktop_ids": []})
    
    desktops = None
    if is_console_admin_user(req["sender"]) and not is_normal_console(req["sender"]):
        if desktop_ids:
            check_desktop_groups = ctx.pgm.get_group_by_desktop(desktop_ids)
            ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                              check_desktop_groups.keys(), 
                                              dbconst.RES_SCOPE_READONLY)
            if isinstance(ret, Error):
                return return_error(req, ret)
            if ret==None or len(ret)==0:
                return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                               ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                               (req['sender']["owner"], desktop_ids)))
        if desktop_group_ids:
            ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                              desktop_group_ids, 
                                              dbconst.RES_SCOPE_READONLY)
            if isinstance(ret, Error):
                return return_error(req, ret)
            if ret==None or len(ret)==0:
                return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                               ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                               (req['sender']["owner"], desktop_group_ids)))

        if desktop_ids:
            desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)

        dg_desktops = None
        if desktop_group_ids:
            dg_desktops = ctx.pgm.get_desktops(status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)
    
        if desktops:
            if dg_desktops:
                desktops.update(dg_desktops)
        else:
            if dg_desktops:
                desktops = dg_desktops
    
    if is_normal_console(req["sender"]):
        if(len(desktop_ids) != 0):
            return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                           ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                           (req['sender']["owner"], desktop_group_ids)))
        owner = req["sender"]["owner"]
    
        ctx = context.instance()
        desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,owner=owner)
        if desktops is None:
            return return_success(req, {"desktop_ids": desktop_ids})

    if is_global_admin_user(req["sender"]):
        desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)

    if desktops is None:
        return return_success(req, {"desktop_ids": []})

    if len(desktops) > 0:
        extra = {"base64_notify": req.get("base64_notify", "")}
        ret = send_desktop_job(sender, desktops.keys(), const.JOB_ACTION_SEND_DESKTOP_NOTIFY, extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_id = ret
    
    ret = {"desktop_ids": desktops.keys()}
    return return_success(req, None, job_id, **ret)

def handle_check_desktop_agent_status(req):
    ''' check desktop agent status ''' 
    sender = req["sender"]
    ctx = context.instance()
    desktop_group_ids = req.get("desktop_group_ids")
    desktop_ids = req.get("desktop_ids", [])
    if not desktop_ids and not desktop_group_ids:
        return return_success(req, {"desktop_ids": []})
    
    desktops = None
    if is_console_admin_user(req["sender"]) and not is_normal_console(req["sender"]):
        if desktop_ids:
            check_desktop_groups = ctx.pgm.get_group_by_desktop(desktop_ids)
            ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                              check_desktop_groups.keys(), 
                                              dbconst.RES_SCOPE_READONLY)
            if isinstance(ret, Error):
                return return_error(req, ret)
            if ret==None or len(ret)==0:
                return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                               ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                               (req['sender']["owner"], desktop_ids)))
        if desktop_group_ids:
            ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                              desktop_group_ids, 
                                              dbconst.RES_SCOPE_READONLY)
            if isinstance(ret, Error):
                return return_error(req, ret)
            if ret==None or len(ret)==0:
                return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                               ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                               (req['sender']["owner"], desktop_group_ids)))

        if desktop_ids:
            desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)

        dg_desktops = None
        if desktop_group_ids:
            dg_desktops = ctx.pgm.get_desktops(status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)
    
        if desktops:
            if dg_desktops:
                desktops.update(dg_desktops)
        else:
            if dg_desktops:
                desktops = dg_desktops
    
    if is_normal_console(req["sender"]):
        if(len(desktop_ids) != 0):
            return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                           ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                           (req['sender']["owner"], desktop_group_ids)))
        owner = req["sender"]["owner"]
    
        ctx = context.instance()
        desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,owner=owner)
        if desktops is None:
            rep = {
                "desktop_set": [],
                "total_count": 0
                }
            return return_success(req, rep)

    if is_global_admin_user(req["sender"]):
        desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)

    if desktops is None:
        rep = {
            "desktop_set": [],
            "total_count": 0
        }
        return return_success(req, rep)

    desktop_set = {}
    for desktop_id in desktops.keys():
        ret = Guest.check_vdhost_server_status(desktop_id)
        if ret is None:
            desktop_set[desktop_id] = {}
        else:
            desktop_set[desktop_id] = {
                const.REQUEST_TYPE_VDHOST: ret.get(const.REQUEST_TYPE_VDHOST, "unknown"),
                const.REQUEST_TYPE_QDP_SERVER: ret.get(const.REQUEST_TYPE_QDP_SERVER, "unknown"),
                const.REQUEST_TYPE_SPICE_AGENT: ret.get("vdagent", "unknown"),
                }

    rep = {
        "desktop_set": desktop_set,
        "total_count": len(desktop_set)
        }
    return return_success(req, rep)

def handle_login_desktop(req):
    
    sender = req["sender"]
    ''' login desktop ''' 
    ctx = context.instance()
    zone_id = sender["zone"]
    desktop_id = req.get("desktop_id", "")
    desktop_ids = [desktop_id]
    if is_console_admin_user(req["sender"]) and not is_normal_console(req["sender"]):
        check_desktop_groups = ctx.pgm.get_group_by_desktop(desktop_ids)
        ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                          check_desktop_groups.keys(), 
                                          dbconst.RES_SCOPE_READONLY)
        if isinstance(ret, Error):
            return return_error(req, ret)
        if ret==None or len(ret)==0:
            return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                           ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                           (req['sender']["owner"], desktop_ids)))

    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,in_domain=1)
    if desktops is None:
        return return_success(req, {"desktop_ids": desktop_ids})

    auth_service = ctx.pgm.get_zone_auth(zone_id)
    if not auth_service:
        logger.error("zone %s no found auth service" %(zone_id))
        return -1

    if len(desktops) > 0:            
        extra = {"username": req["username"],
                 "password": req["password"],
                 "domain": auth_service["domain"]}
        ret = send_desktop_job(sender, desktops.keys(), const.JOB_ACTION_VDI_LOGIN_DESKTOP, extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_id = ret
    
    ret = {"desktop_ids": desktops.keys()}
    return return_success(req, None, job_id, **ret)

def handle_logoff_desktop(req):
    
    sender = req["sender"]
    ''' logoff desktop ''' 
    ctx = context.instance()
    desktop_id = req.get("desktop_id", "")
    desktop_ids = [desktop_id]
    if is_console_admin_user(req["sender"]) and not is_normal_console(req["sender"]):
        check_desktop_groups = ctx.pgm.get_group_by_desktop(desktop_ids)
        ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                          check_desktop_groups.keys(), 
                                          dbconst.RES_SCOPE_READONLY)
        if isinstance(ret, Error):
            return return_error(req, ret)
        if ret==None or len(ret)==0:
            return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                           ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                           (req['sender']["owner"], desktop_ids)))

    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN)
    if desktops is None:
        return return_success(req, {"desktop_ids": desktop_ids})

    if len(desktops) > 0:
        ret = send_desktop_job(sender, desktops.keys(), const.JOB_ACTION_VDI_LOGOFF_DESKTOP)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_id = ret

    ret = {"desktop_ids": desktops.keys()}
    return return_success(req, None, job_id, **ret)

def handle_add_desktop_active_directory(req):
    ''' add desktop active directory '''
    sender = req["sender"]
    ctx = context.instance()
    desktop_group_ids = req.get("desktop_group_ids")
    desktop_ids = req.get("desktop_ids", [])
    if not desktop_ids and not desktop_group_ids:
        return return_success(req, {"desktop_ids": []})
    
    desktops = None
    if is_console_admin_user(req["sender"]) and not is_normal_console(req["sender"]):
        if desktop_ids:
            check_desktop_groups = ctx.pgm.get_group_by_desktop(desktop_ids)
            ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                              check_desktop_groups.keys(), 
                                              dbconst.RES_SCOPE_READONLY)
            if isinstance(ret, Error):
                return return_error(req, ret)
            if ret==None or len(ret)==0:
                return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                               ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                               (req['sender']["owner"], desktop_ids)))
        if desktop_group_ids:
            ret = check_user_resource_permission(sender, dbconst.TB_DESKTOP_GROUP, 
                                              desktop_group_ids, 
                                              dbconst.RES_SCOPE_READONLY)
            if isinstance(ret, Error):
                return return_error(req, ret)
            if ret==None or len(ret)==0:
                return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                               ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                               (req['sender']["owner"], desktop_group_ids)))

        if desktop_ids:
            desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)

        dg_desktops = None
        if desktop_group_ids:
            dg_desktops = ctx.pgm.get_desktops(status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)
    
        if desktops:
            if dg_desktops:
                desktops.update(dg_desktops)
        else:
            if dg_desktops:
                desktops = dg_desktops
    
    
    if is_normal_console(req["sender"]):
        if(len(desktop_ids) != 0):
            return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                           ErrorMsg.ERR_MSG_RESOURCE_ACCESS_DENIED,
                                           (req['sender']["owner"], desktop_group_ids)))
        owner = req["sender"]["owner"]
    
        ctx = context.instance()
        desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,owner=owner)
        if desktops is None:
            return return_success(req, {"desktop_ids": desktop_ids})

    if is_global_admin_user(req["sender"]):
        desktops = ctx.pgm.get_desktops(desktop_ids=desktop_ids,status=INST_STATUS_RUN,desktop_group_ids=desktop_group_ids)

    if desktops is None:
        return return_success(req, {"desktop_ids": []})

    zone_id = None
    for _,desktop in desktops.items():
        if zone_id is None:
            zone_id = desktop.get("zone")
        else:
            if zone_id != desktop.get("zone"):
                logger.error("resources [%s] not in only zone" % desktops.keys())
                return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                               ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND_OR_NOT_SAME, desktops.keys()))
    if len(desktops) > 0:
        ctx = context.instance()
        if zone_id is None:
            logger.error("zone_id is not found.")
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                           ErrorMsg.ERR_MSG_NO_FOUND_ZONE_INFO, "zone"))
        auth_service = ctx.pgm.get_zone_auth(zone_id)
        if not auth_service:
            logger.error("zone: [%s] have not auth service", sender["zone"])
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                           ErrorMsg.ERR_MSG_AUTH_SERVICE_NO_FOUND, sender["zone"]))
        if auth_service['auth_service_type'] != const.AUTH_TYPE_AD:
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                           ErrorMsg.ERR_MSG_ILLEGAL_LOGIN_SERVER_TYPE % ctx.sysconf['auth_type']))
        extra = {}
        extra["domain"] = auth_service["domain"]
        admin_name = auth_service["admin_name"]
        if admin_name.endswith(auth_service["domain"]):
            pass
        else:
            admin_name = "%s@%s" % (auth_service["admin_name"], auth_service["domain"])
        extra["username"] = admin_name
        extra["password"] = auth_service["admin_password"]
        extra["ou"] = req["org_dn"]
        ret = send_desktop_job(sender, desktops.keys(), const.JOB_ACTION_VDI_ADD_DESKTOP_ACTIVE_DIRECTORY, extra)
        if isinstance(ret, Error):
            return return_error(req, ret)
        job_id = ret

    ret = {"desktop_ids": desktops.keys()}
    return return_success(req, None, job_id, **ret) 


def handle_describe_spice_info(req):
    sender = req["sender"]
    ctx = context.instance()

    # global admin user can see all resources
    if is_global_admin_user(sender):
        display_columns = dbconst.GOLBAL_ADMIN_COLUMNS[dbconst.TB_GUEST]
    elif is_console_admin_user(sender) and is_admin_console(sender):
        display_columns = dbconst.CONSOLE_ADMIN_COLUMNS[dbconst.TB_GUEST]
        desktop_ids = req.get("desktop_id")
        if desktop_ids:
            desctop_ids = check_user_resource_permission(sender, dbconst.TB_GUEST, desktop_ids)
            if desktop_ids:
                req.update({"desktop_id": desctop_ids})
            else:
                return return_items(req, [], "guest")
    else:
        display_columns = dbconst.PUBLIC_COLUMNS[dbconst.TB_GUEST]
        desktop_ids = req.get("desktop_id")
        if desktop_ids:
            desktops = ctx.pgm.get_desktops(desktop_ids)
            if desktops:
                desktop_ids = []
                for desktop_id,desktop in desktops.items():
                    if desktop["owner"] == sender["owner"]:
                        desktop_ids.append(desktop_id)
                if len(desktop_ids) == 0:
                    return return_items(req, [])
                else:
                    req.update({"desktop_id": desktop_ids})
        else:
            return_items(req, [], "guest")

    filter_conditions = build_filter_conditions(req, dbconst.TB_GUEST)

    guest_set = ctx.pg.get_by_filter(dbconst.TB_GUEST, filter_conditions, display_columns,
                                     sort_key=get_sort_key(dbconst.TB_GUEST, req.get("sort_key"), default_key="connect_time"),
                                     reverse=get_reverse(req.get("reverse")),
                                     offset=req.get("offset", 0),
                                     limit=req.get("limit", dbconst.DEFAULT_LIMIT)
                                     )
    if guest_set is None:
        logger.error("describe guest failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    total_count = ctx.pg.get_count(dbconst.TB_GUEST, filter_conditions)
    if total_count is None:
        logger.error("get guest count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    rep = {'total_count': total_count}

    return return_items(req, guest_set, "guest", **rep)


def describe_guest_processes(req):
    sender = req["sender"]

    rep = {"guest_processes": [], "total": 0}
    if not is_admin_user(sender):
        logger.error("only admin can describe guest processes.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))
    if not is_admin_console(sender):
        logger.error("only admin console can describe guest processes.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_ADMIN_CONSOLE_ONLY))

    desktop_id = req.get("desktop_id")
    if is_console_admin_user(sender):
        desctop_ids = check_user_resource_permission(sender, dbconst.TB_GUEST, desktop_id)
        if desctop_ids is None or len(desctop_ids) == 0:
            return return_success(req, rep)

    order_by = req.get("order_by", const.GUEST_PROCESS_ORDER_BY_CPU)
    top = req.get("top", 10)
    req = {
        "action": "",
        "desktop_id": desktop_id,
        "params":{
            "order_by": order_by,
            "top": top
            }
        }

    rep = {"desktop_id": desktop_id}
    return return_success(req, rep)

def describe_guest_programs(req):
    sender = req["sender"]

    rep = {"guest_programs": [], "total": 0}
    if not is_admin_user(sender):
        logger.error("only admin can describe guest programes.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))
    if not is_admin_console(sender):
        logger.error("only admin console can describe guest programes.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED,
                                       ErrorMsg.ERR_MSG_ADMIN_CONSOLE_ONLY))

    desktop_id = req.get("desktop_id")
    if is_console_admin_user(sender):
        desctop_ids = check_user_resource_permission(sender, dbconst.TB_GUEST, desktop_id)
        if desctop_ids is None or len(desctop_ids) == 0:
            return return_success(req, rep)

    req = {
        "action": "",
        "desktop_id": desktop_id,
        "params":{}
        }

    rep = {"desktop_id": desktop_id}
    return return_success(req, rep)

def handle_guest_json_rpc(req):

    json_request = req.get("json_request")
    if not json_request:
        logger.error("request parameter is error. json_request = %s" % json_request)
        return return_error(req, Error(ErrorCodes.PUSH_SERVER_REQUEST_PARAMS_ERROR,
                                       ErrorMsg.ERR_CODE_MSG_INVALID_REQUEST_PARAMS))

    action = json_request.get("action")
    if action == const.REQUEST_VDHOST_REGISTER:
        ret = GuestJsonRpc.handle_register(json_request)
    elif action == const.REQUEST_GUEST_AGENT_SPICE_CLIENT_CONNECTED:
        ret = GuestJsonRpc.handle_spice_connected(json_request)
    elif action == const.REQUEST_GUEST_AGENT_SPICE_CLIENT_DISCONNECTED:
        ret = GuestJsonRpc.handle_spice_disconnected(json_request)
    elif action == const.REQUEST_GUEST_AGENT_QDP_CLIENT_CONNECTED:
        ret = GuestJsonRpc.handle_qdp_connected(json_request)
    elif action == const.REQUEST_GUEST_AGENT_QDP_CLIENT_DISCONNECTED:
        ret = GuestJsonRpc.handle_qdp_disconnected(json_request)
    elif action == const.REQUEST_GUEST_AGENT_GUEST_SYSTEM_RESTART:
        ret = GuestJsonRpc.handle_guest_system_restart(json_request)
    elif action == const.REQUEST_GUEST_AGENT_GUEST_SYSTEM_SHUTDOWN:
        ret = GuestJsonRpc.handle_guest_system_shutdown(json_request)
    elif action == const.REQUEST_GUEST_AGENT_GUEST_SYSTEM_LOGOUT:
        ret = GuestJsonRpc.handle_guest_system_logout(json_request)
    elif action == const.REQUEST_GUEST_AGENT_GUEST_SYSTEM_UPGRADE:
        ret = GuestJsonRpc.handle_guest_system_upgrade(json_request)
    elif action == const.REQUEST_GUEST_AGENT_GET_FILE_SHARE_GROUPS:
        ret = GuestJsonRpc.handle_get_file_share_groups(req)
        if isinstance(ret, Error):
            return return_error(req, ret)
        if not ret:
            # get total count
            total_count = {'total_count': 0}
            new_req ={'action':const.REQUEST_GUEST_AGENT_GET_FILE_SHARE_GROUPS}
            ret = return_items(new_req, items_set=None, item_type="file_share_group", dump=False,**total_count)
            rep = {"json_response": ret}
            logger.info("return_success(req, rep) == %s" % (return_success(req, rep)))
            return return_success(req, rep)
        else:
            # get total count
            total_count = {'total_count': len(ret)}
            new_req ={'action':const.REQUEST_GUEST_AGENT_GET_FILE_SHARE_GROUPS}
            ret = return_items(new_req, items_set=ret, item_type="file_share_group", dump=False,**total_count)
            rep = {"json_response": ret}
            logger.info("return_success(req, rep) == %s" %(return_success(req, rep)))
            return return_success(req, rep)

    elif action == const.REQUEST_GUEST_AGENT_GET_FILE_SHARE_FILES:
        ret = GuestJsonRpc.handle_get_file_share_files(req)
        if isinstance(ret, Error):
            return return_error(req, ret)
        if not ret:
            # get total count
            total_count = {'total_count': 0}
            new_req = {'action': const.REQUEST_GUEST_AGENT_GET_FILE_SHARE_FILES}
            ret = return_items(new_req, items_set=None, item_type="file_share_group", dump=False, **total_count)
            rep = {"json_response": ret}
            logger.info("return_success(req, rep)  == %s" % (return_success(req, rep)))
            return return_success(req, rep)
        else:
            # get total count
            total_count = {'total_count': len(ret)}
            new_req ={'action':const.REQUEST_GUEST_AGENT_GET_FILE_SHARE_FILES}
            ret = return_items(new_req, items_set=ret, item_type="file_share_group", dump=False, **total_count)
            rep = {"json_response": ret}
            logger.info("return_success(req, rep) == %s" %(return_success(req, rep)))
            return return_success(req, rep)

    elif action == const.REQUEST_GUEST_AGENT_DOWNLOAD_FILE_SHARE_FILES:
        ret = GuestJsonRpc.handle_download_file_share_files(req)

    elif action == const.REQUEST_GUEST_AGENT_GET_FILE_SHARE_TOOLS_COMPONENT_VERSION:
        ret = GuestJsonRpc.handle_get_file_share_tools_component_version(req)

    else:
        logger.error("action [%s] can not handle.")
        return return_error(req, Error(ErrorCodes.PUSH_SERVER_REQUEST_PARAMS_ERROR,
                                       ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, "action"))
    if isinstance(ret, Error):
        return return_error(req, ret)

    ret["action"] = action + "Response"
    rep = {"json_response": ret}
    logger.info("return_success(req, rep) == %s" %(return_success(req, rep)))
    return return_success(req, rep) 
