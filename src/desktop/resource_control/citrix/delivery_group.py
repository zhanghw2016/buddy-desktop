import db.constants as dbconst
from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from utils.id_tool import(
    get_uuid,
    UUID_TYPE_DESKTOP_USER,
    UUID_TYPE_DELIVERY_GROUP, 
    UUID_TYPE_DESKTOP_USER_GROUP
)
from utils.misc import get_current_time, explode_array
import constants as const
import resource_control.policy.policy_group as PolicyGroup
import resource_control.desktop.disk as DesktopDisk
import api.user.resource_user as ResUser

def check_delivery_group_name(zone_id, delivery_group_names, is_load=False):
    
    ctx = context.instance()
    ret = ctx.pgm.get_delivery_groups(delivery_group_name=delivery_group_names, zone_id=zone_id)
    if ret:
        logger.error("delivery group name %s already existed" % (delivery_group_names))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_DELIVERY_GROUP_NAME_ALREADY_EXISTED, (delivery_group_names))

    delivery_groups = ctx.res.resource_describe_delivery_groups(zone_id, delivery_group_names)
    
    if is_load:
        if not delivery_groups:
            logger.error("delivery group name %s no found" % (delivery_group_names))
            return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_DELIVERY_GROUP_NAME_NO_FOUND, (delivery_group_names))
    else:
        if delivery_groups:
            logger.error("delivery group name %s already existed" % (delivery_group_names))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DELIVERY_GROUP_NAME_ALREADY_EXISTED, (delivery_group_names))
    
    return None

def register_delivery_group(sender, delivery_group_name, delivery_group_type, allocation_type, description, req):
    
    ctx = context.instance()
    delivery_type = req.get("delivery_type", const.CITRIX_DELIVERY_TYPE_DESKTOP)
    desktop_hide_mode=req.get("desktop_hide_mode",0)    
    desktop_kind = const.CITRIX_DESKTOP_KIND_PRIVATE if allocation_type == const.CITRIX_ALLOC_TYPE_STATIC else const.CITRIX_DESKTOP_KIND_SHARED
    
    ret = ctx.res.resource_create_delivery_group(sender["zone"], delivery_group_name, delivery_group_type, desktop_kind, description, delivery_type)
    if ret is None:
        logger.error("create resource delivery group fail  %s" % (delivery_group_name))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_CLOUD_RESOURCE_FAILED, delivery_group_name)

    delivery_groups = ctx.res.resource_describe_delivery_groups(sender["zone"], delivery_group_name)
    if not delivery_groups or delivery_group_name not in delivery_groups:
        logger.error("describe resource delivery group fail  %s" % (delivery_group_name))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, delivery_group_name)
    
    delivery_group = delivery_groups[delivery_group_name]
    mode = delivery_group["mode"]
    if mode == "True":
        mode = const.DG_STATUS_MAINT
    else:
        mode = const.DG_STATUS_NORMAL
    
    desktop_hide_mode = desktop_hide_mode if delivery_type == const.CITRIX_DELIVERY_TYPE_DESKTOP_APP else 0
    
    delivery_group_id = get_uuid(UUID_TYPE_DELIVERY_GROUP, ctx.checker)
    delivery_group_info = dict(
                              delivery_group_id = delivery_group_id,
                              delivery_group_name = delivery_group_name,
                              delivery_group_type = delivery_group_type,
                              allocation_type = allocation_type,
                              desktop_kind = desktop_kind,
                              description = description if description else '',
                              create_time = get_current_time(),
                              delivery_type = delivery_type,
                              delivery_group_uid = delivery_group.get("delivery_group_uid", ""),
                              zone = sender["zone"],
                              mode = mode,
                              desktop_hide_mode=desktop_hide_mode
                              )
    # register desktop group
    if not ctx.pg.insert(dbconst.TB_DELIVERY_GROUP, delivery_group_info):
        logger.error("insert newly created delivery group for [%s] to db failed" % (delivery_group_info))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    security_group_id = req.get("security_group", "")
    if security_group_id:
        ret = PolicyGroup.add_resource_group_policy(sender, security_group_id, delivery_group_id, dbconst.RESTYPE_DELIVERY_GROUP, const.POLICY_TYPE_SECURITY)
        if isinstance(ret, Error):
            return ret

    return delivery_group_id

def update_delivery_group_status(delivery_group_ids, status):
    ctx = context.instance()
    if not isinstance(delivery_group_ids, list):
        delivery_group_ids = [delivery_group_ids]
    
    update_info = {delivery_group_id: {"status": status} for delivery_group_id in delivery_group_ids}
    if not ctx.pg.batch_update(dbconst.TB_DELIVERY_GROUP, update_info):
        logger.error("update delivery group status %s fail" % update_info)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    return None

def refresh_delivery_group_name(delivery_group_id, new_name):
    
    ctx = context.instance()

    conditions = {}
    conditions["delivery_group_id"] = delivery_group_id
    update_info = {"delivery_group_name": new_name}
    
    desktops = ctx.pgm.get_desktops(delivery_group_id=delivery_group_id)
    if not desktops:
        return None
    
    if not ctx.pg.base_update(dbconst.TB_DESKTOP, conditions, update_info):
        logger.error("update refresh delivery group name in desktop %s fail" % update_info)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def modify_delivery_group_attributes(sender, delivery_group_id, delivery_group_name, description,desktop_hide_mode=None):

    ctx = context.instance()
    delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_id)
    if not delivery_groups:
        logger.error("no found resource %s" % delivery_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id)
    
    delivery_group = delivery_groups[delivery_group_id]
    update_delivery_group = {}
    if delivery_group_name:
        if delivery_group_name != delivery_group["delivery_group_name"]:
            update_delivery_group["delivery_group_name"] = delivery_group_name

    if description:
        update_delivery_group["description"] = description

    if desktop_hide_mode is not None:
        
        desktop_hide_mode = desktop_hide_mode if delivery_group.get("delivery_type") == const.CITRIX_DELIVERY_TYPE_DESKTOP_APP else 0
        update_delivery_group["desktop_hide_mode"] = desktop_hide_mode

    if not update_delivery_group:
        return None
    
    ret = ctx.res.resource_modify_delivery_group(sender["zone"], delivery_group["delivery_group_name"], delivery_group_name, description)
    if ret is None:
        logger.error("modify resource delivery group fail  %s" % (delivery_group_name))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_CLOUD_RESOURCE_FAILED, delivery_group_id)
        
    if not ctx.pg.batch_update(dbconst.TB_DELIVERY_GROUP, {delivery_group_id: update_delivery_group}):
        logger.error("update modify delivery group status %s fail" % update_delivery_group)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    if "delivery_group_name" in update_delivery_group:
        ret = refresh_delivery_group_name(delivery_group_id, update_delivery_group["delivery_group_name"])
        if isinstance(ret, Error):
            return ret
    
    return None

def clear_delivery_group_info(sender, delivery_group_id):
    
    ctx = context.instance()
    
    delivery_group = ctx.pgm.get_delivery_group(delivery_group_id)
    if not delivery_group:
        return None
    
    desktops = ctx.pgm.get_desktops(delivery_group_id=delivery_group_id)
    if desktops:
        update_desktop = {}
        for desktop_id, _ in desktops.items():
            update_info = {
                "delivery_group_id": '',
                "delivery_group_name": ''
                }
            update_desktop[desktop_id] = update_info

        if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_desktop):
            logger.error("update desktop delivery group %s fail" % update_desktop)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    users = ctx.pgm.get_delivery_group_user(delivery_group_id)
    if users:
        user_ids = users.keys()
        ctx.pg.base_delete(dbconst.TB_DELIVERY_GROUP_USER, {"delivery_group_id": delivery_group_id, "user_id": user_ids})

    broker_apps = ctx.pgm.get_delivery_group_broker_apps(delivery_group_id)
    if broker_apps:

        broker_apps = ctx.pgm.get_broker_apps(broker_apps.keys())
        if broker_apps:
            from resource_control.citrix.virtual_app import detach_broker_app_from_group
            ret = detach_broker_app_from_group(sender, broker_apps, delivery_group_id)
            if isinstance(ret, Error):
                return ret

    broker_app_groups = ctx.pgm.get_delivery_group_broker_app_groups(delivery_group_id)
    if broker_app_groups:
        from resource_control.citrix.virtual_app import detach_broker_app_group_from_delivery_group
        for broker_app_group_id, _ in broker_app_groups.items():
            ret = detach_broker_app_group_from_delivery_group(sender, broker_app_group_id, delivery_group)
            if isinstance(ret, Error):
                return ret

    ctx.pg.delete(dbconst.TB_DELIVERY_GROUP, delivery_group_id)

    return None

def delete_delivery_groups(sender, delivery_group_ids):

    ctx = context.instance()
    delivery_group_names = ctx.pgm.get_delivery_group_name(delivery_group_ids)
    if not delivery_group_names:
        return None
    
    resource_delivery_groups = ctx.res.resource_describe_delivery_groups(sender["zone"], delivery_group_names.values())
    if not resource_delivery_groups:
        resource_delivery_groups = {}
    
    delete_delivery_group = {}
    for delivery_group_id, delivery_group_name in delivery_group_names.items():
        if delivery_group_name not in resource_delivery_groups:
            ret = clear_delivery_group_info(sender, delivery_group_id)
            if isinstance(ret, Error):
                return ret
            continue
    
        delete_delivery_group[delivery_group_id] = delivery_group_name

    for delivery_group_id, delivery_group_name in delete_delivery_group.items():
        ret = ctx.res.resource_delete_delivery_group(sender["zone"], delivery_group_name)
        if ret is None:
            logger.error("delete resource delivery group fail  %s" % (delivery_group_name))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_DELETE_CLOUD_RESOURCE_FAILED, delivery_group_id)
        
        ret = clear_delivery_group_info(sender, delivery_group_id)
        if isinstance(ret, Error):
            return ret
    
    return None

def describe_system_delivery_groups(sender):

    ctx = context.instance()
    ret = ctx.res.resource_describe_delivery_groups(sender["zone"])
    if not ret:
        return None

    delivery_group_set = ret

    existed_delivery_groups = ctx.pgm.get_delivery_group_name(zone_id=sender["zone"])
    if not existed_delivery_groups:
        existed_delivery_groups = {}
    
    system_delivery_group = {}
    for delivery_group_name, delivery_group in delivery_group_set.items():
        if delivery_group_name in existed_delivery_groups.values():
            continue
        delivery_group["delivery_group_name"] = delivery_group_name
        system_delivery_group[delivery_group_name] = delivery_group

    return system_delivery_group

def check_delivery_group_computers(sender, delivery_group_name, computer_names=None):
    
    ctx = context.instance()
    computers = ctx.res.resource_describe_computers(sender["zone"], deliverygroup_names=delivery_group_name, machine_names=computer_names)
    if not computers:
        return None
    
    computer_names = computers.keys()
    desktop_names = ctx.pgm.get_desktop_by_hostnames(computer_names, zone_id=sender["zone"])
    if not desktop_names:
        desktop_names = {}
    
    desktops = {}
    for compter_name in computer_names:
        if compter_name not in desktop_names:
            continue
        
        desktop = desktop_names[compter_name]
        desktop_id = desktop["desktop_id"]
        desktops[desktop_id] = desktop
        
    return desktops

def refresh_broker_app_in_delivery_group(sender, delivery_group):
    
    ctx = context.instance()
    delivery_group_uid = delivery_group.get("delivery_group_uid")
    if not delivery_group_uid:
        return None
    delivery_group_id = delivery_group["delivery_group_id"]
    
    ret = ctx.res.resource_describe_broker_apps(sender["zone"], delivery_group_uids=delivery_group_uid, index_uid=True)
    if not ret:
        return None
    
    broker_apps = ret

    refresh_broker_apps = ctx.pgm.get_broker_app_by_uid(broker_apps.keys())
    if not refresh_broker_apps:
        return None
    
    broker_app_ids = refresh_broker_apps.keys()  
    
    existed_broker_apps = ctx.pgm.get_delivery_group_broker_apps(delivery_group_id)
    if not existed_broker_apps:
        existed_broker_apps = {}
    
    new_broker_app_ids = []
    
    for broker_app_id in broker_app_ids:
        if broker_app_id in existed_broker_apps:
            continue
        
        new_broker_app_ids.append(broker_app_id)
    
    if new_broker_app_ids:
        from resource_control.citrix.virtual_app import attach_broker_app_to_delivery_group
        ret = attach_broker_app_to_delivery_group(sender, delivery_group, new_broker_app_ids, is_load=True)
        if isinstance(ret, Error):
            return ret
    
    del_broker_app_ids = []
    for broker_app_id, _ in existed_broker_apps.items():
        if broker_app_id in broker_app_ids:
            continue
        
        del_broker_app_ids.append(broker_app_id)
    
    if del_broker_app_ids:
        ctx.pg.base_delete(dbconst.TB_BROKER_APP_DELIVERY_GROUP, {"broker_app_id": del_broker_app_ids, "delivery_group_id": delivery_group_id})
        
    return broker_app_ids

def refresh_broker_app_group_in_delivery_group(sender, delivery_group):
    
    ctx = context.instance()
    delivery_group_uid = delivery_group.get("delivery_group_uid")
    if not delivery_group_uid:
        return None
    delivery_group_id = delivery_group["delivery_group_id"]
    
    ret = ctx.res.resource_describe_broker_app_groups(sender["zone"], delivery_group_uids=delivery_group_uid, index_uid=True)
    if not ret:
        return None
    
    broker_app_groups = ret

    refresh_broker_app_groups = ctx.pgm.get_broker_app_group_by_uid(broker_app_groups.keys())
    if not refresh_broker_app_groups:
        return None
    
    broker_app_group_ids = refresh_broker_app_groups.keys()  
    
    existed_broker_app_groups = ctx.pgm.get_delivery_group_broker_app_groups(delivery_group_id)
    if not existed_broker_app_groups:
        existed_broker_app_groups = {}
    
    new_broker_app_group_ids = []
    
    for broker_app_group_id in broker_app_group_ids:
        if broker_app_group_id in existed_broker_app_groups:
            continue
        
        new_broker_app_group_ids.append(broker_app_group_id)

    if new_broker_app_group_ids:
        from resource_control.citrix.virtual_app import attach_broker_app_group_to_delivery_group
        ret = attach_broker_app_group_to_delivery_group(sender, delivery_group, new_broker_app_group_ids, is_load=True)
        if isinstance(ret, Error):
            return ret
    
    del_broker_app_group_ids = []
    for broker_app_group_id, _ in existed_broker_app_groups.items():
        if broker_app_group_id in broker_app_group_ids:
            continue
        
        del_broker_app_group_ids.append(broker_app_group_id)
    
    if del_broker_app_group_ids:
        ctx.pg.base_delete(dbconst.TB_BROKER_APP_DELIVERY_GROUP, {"broker_app_id": del_broker_app_group_ids, "delivery_group_id": delivery_group_id})

    return del_broker_app_group_ids

def load_system_delivery_groups(sender, delivery_group_names):
    
    ctx = context.instance()
    delivery_groups = ctx.res.resource_describe_delivery_groups(sender["zone"], delivery_group_names)
    if not delivery_groups:
        logger.error("describe resource delivery group fail  %s" % (delivery_group_names))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_CLOUD_RESOURCE_NOT_FOUND, delivery_group_names)
    
    delivery_group_ids = []
    for delivery_group_name in delivery_group_names:
        delivery_group = delivery_groups[str(delivery_group_name)]
    
        ret = check_delivery_group_computers(sender, delivery_group_name)
        if isinstance(ret, Error):
            return ret
        desktops = ret
        
        delivery_type = delivery_group.get("delivery_type", const.CITRIX_DELIVERY_TYPE_DESKTOP)
        delivery_group_uid = delivery_group.get("delivery_group_uid")
        if delivery_group_uid is not None:
            delivery_group_uid = str(delivery_group_uid)
        else:
            delivery_group_uid = ''
        
        delivery_group_id = get_uuid(UUID_TYPE_DELIVERY_GROUP, ctx.checker)
        delivery_group_info = dict(
                                  delivery_group_id = delivery_group_id,
                                  delivery_group_name = delivery_group_name,
                                  delivery_type = delivery_type,
                                  delivery_group_type = delivery_group["session_support"],
                                  delivery_group_uid = delivery_group_uid,
                                  desktop_kind = delivery_group["desktop_kind"],
                                  allocation_type = const.CITIRX_ALLOC_KIND_MAP[delivery_group["desktop_kind"]],
                                  description =delivery_group["description"],
                                  assign_name = delivery_group.get("assign_name", ""),
                                  mode = const.DG_STATUS_NORMAL if delivery_group["mode"] == "False" else const.DG_STATUS_MAINT,
                                  create_time = get_current_time(),
                                  zone = sender["zone"],
                                  desktop_hide_mode=1 if delivery_type== const.CITRIX_DELIVERY_TYPE_DESKTOP_APP else 0,
                                  )
        # register desktop group
        if not ctx.pg.insert(dbconst.TB_DELIVERY_GROUP, delivery_group_info):
            logger.error("insert newly created delivery group for [%s] to db failed" % (delivery_group_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
        
        include_users = delivery_group["include_users"] 
        if include_users:
            user_names = explode_array(include_users)
            ret = set_delivery_group_users(sender, delivery_group_id, user_names)
            if isinstance(ret, Error):
                clear_delivery_group_info(sender, delivery_group_id)
                return ret

        if desktops:
            ret = set_delivery_group_desktops(sender, delivery_group_id, desktops)
            if isinstance(ret, Error):
                clear_delivery_group_info(sender, delivery_group_id)
                return ret
            
        if delivery_type == const.CITRIX_DELIVERY_TYPE_DESKTOP_APP:
            ret = refresh_broker_app_in_delivery_group(sender, delivery_group_info)
            if isinstance(ret, Error):
                return ret
            ret = refresh_broker_app_group_in_delivery_group(sender, delivery_group_info)
            if isinstance(ret, Error):
                return ret

        delivery_group_ids.append(delivery_group_id)

    return delivery_group_ids

def set_delivery_group_users(sender, delivery_group_id, user_names):
    
    ctx = context.instance()
    users = ctx.pgm.get_user_by_user_names(user_names, zone_id=sender["zone"])
    if not users:
        users = {}
    
    user_groups = ctx.pgm.get_user_group_by_user_group_names(user_names, zone_id=sender["zone"])
    if not user_groups:
        user_groups = {}
    user_ids = users.values()    
    user_group_ids = user_groups.values()
    if user_group_ids:
        user_ids.extend(user_group_ids)
    
    ret = add_user_to_delivery_group(sender, delivery_group_id, user_ids, is_load=True)
    if isinstance(ret, Error):
        return ret
    
    return user_ids

def set_delivery_group_desktops(sender, delivery_group_id, desktops):
    
    ctx = context.instance()
    
    delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_id)
    if not delivery_groups:
        logger.error("no found delivery group %s" % delivery_group_id)
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id) 
    
    delivery_group = delivery_groups[delivery_group_id]

    desktop_ids = desktops.keys()
    ret = check_attach_delivery_group_desktop(sender, delivery_group, desktop_ids, is_load=True)
    if isinstance(ret, Error):
        return ret
    desktops = ret

    ret = add_desktop_to_delivery_group(sender, delivery_group, desktops, None, is_load=True)
    if isinstance(ret, Error):
        return ret
    
    return None

def get_desktop_hostname(desktops, desktop_ids):
    
    desktop_names = {}
    for desktop_id in desktop_ids:
        desktop = desktops.get(desktop_id)
        
        if not desktop:
            continue
        
        hostname = desktop["hostname"]
        desktop_names[desktop_id] = hostname
    
    return desktop_names

def add_desktop_to_delivery_group(sender, delivery_group, desktops, desktop_users=None, is_load=False):
    
    ctx = context.instance()
    
    delivery_group_id = delivery_group["delivery_group_id"]
    delivery_group_name = delivery_group["delivery_group_name"]
    
    desktop_ids = desktops.keys()
    update_desktop = {}
    
    if not desktop_users:
        desktop_users = {}
    
    for i in xrange(0, len(desktop_ids), const.CITRIX_MAX_LIMIT_PARAM):
        end = i + const.CITRIX_MAX_LIMIT_PARAM
        if end > len(desktop_ids):
            end = len(desktop_ids)
        
        update_desktop_users = {}
        update_desktop = {}
        desk_ids = desktop_ids[i:end]
        compute_info = {}
        for desktop_id in desk_ids:
            
            desktop = desktops[desktop_id]
            hostname = desktop["hostname"]
            update_info = {
                      "delivery_group_name": delivery_group_name,
                      "delivery_group_id": delivery_group_id
                      }
            user_name_str = ""
            user_ids = desktop_users.get(desktop_id, '')
            if not is_load and user_ids:
                user_names = ctx.pgm.get_user_names(user_ids)
                user_name_str = user_names.values() if user_names else ""
                update_desktop_users[desktop_id] = user_ids
            
            compute_info.update({hostname: user_name_str})
            update_desktop[desktop_id] = update_info
        
        if not is_load and compute_info:
            ret = ctx.res.resource_attach_computer_to_delivery_group(sender["zone"], delivery_group_name, compute_info)
            if not ret:
                logger.error("resource attach compute to delivery group fail %s, %s" % (delivery_group_name, compute_info))
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_ATTACH_DESKTOP_TO_DELIVERY_GROUP_FAIL, (desk_ids, delivery_group_name)) 
        
        if update_desktop:
            if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_desktop):
                logger.error("update attach delivery group fail %s" % delivery_group_id)
                return Error(ErrorCodes.INTERNAL_ERROR,
                             ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
            
            DesktopDisk.refresh_desktop_disk_owner(update_desktop.keys())
        
        if update_desktop_users:
            for resource_id, user_ids in update_desktop_users.items():
                ret = ResUser.attach_user_to_desktop_resource(ctx, resource_id, user_ids)
                if isinstance(ret, Error):
                    return ret
        
    ret = PolicyGroup.set_desktop_security_policy_group(sender, desktop_ids)
    if isinstance(ret, Error):
        return ret
    
    return ret

def _detach_desktop_from_delivery_group(sender, delivery_group, desktops, desktop_ids):
    
    ctx = context.instance()
    delivery_group_name = delivery_group["delivery_group_name"]
    delivery_group_id = delivery_group["delivery_group_id"]
    update_desktop = {}
    for i in xrange(0, len(desktop_ids), const.CITRIX_MAX_LIMIT_PARAM):
        end = i + const.CITRIX_MAX_LIMIT_PARAM
        if end > len(desktop_ids):
            end = len(desktop_ids)

        desk_ids = desktop_ids[i:end]

        desktop_names = get_desktop_hostname(desktops, desk_ids)
        if not desktop_names:
            continue

        computers = ctx.res.resource_describe_computers(sender["zone"], machine_names=desktop_names.values())
        if not computers:
            computers = {}
        
        if computers:
            
            detach_names = []
            for computer_name, computer in computers.items():
                
                delivery_group_name = computer.get("delivery_group_name")
                if not delivery_group_name:
                    continue
                
                detach_names.append(computer_name)
            
            if detach_names:
                ret = ctx.res.resource_detach_computer_from_delivery_group(sender["zone"], delivery_group_name, detach_names)
                if not ret:
                    logger.error("detacg delivery group resource fail %s" % delivery_group_id)
                    return Error(ErrorCodes.INTERNAL_ERROR,
                                 ErrorMsg.ERR_MSG_DDC_DETACH_DESKTOP_FROM_DELIVERY_GROUP_FAIL, (delivery_group_id, desktop_names))

        update_info = {
                        "delivery_group_name": '',
                        "delivery_group_id": '',
                      }
        for desktop_id in desk_ids:
            desktop_name = desktop_names.get(desktop_id)
            if not desktop_name:
                continue
            desktop = desktops.get(desktop_id)
            if not desktop:
                continue
            computer = computers.get(desktop_name)
            if not computer:
                continue

            ret = ResUser.refresh_citrix_desktop_owner(ctx, desktop, computer)
            if isinstance(ret, Error):
                return ret
            update_desktop[desktop_id] = update_info

        update_desktop = {desktop_id: update_info for desktop_id in desk_ids}
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP, update_desktop):
            logger.error("update attach delivery group fail %s" % update_desktop)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
            
    return None


def del_desktop_from_delivery_group(sender, desktops):
    
    ctx = context.instance()
    desktop_ids = desktops.keys()
    
    delivery_group_desktops = {}
    for desktop_id, desktop in desktops.items():
        delivery_group_id = desktop["delivery_group_id"]
        if not delivery_group_id:
            continue
        
        if delivery_group_id not in delivery_group_desktops:
            delivery_group_desktops[delivery_group_id] = []
        
        delivery_group_desktops[delivery_group_id].append(desktop_id)

    
    if not delivery_group_desktops:
        return None
    
    delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_desktops.keys())
    if not delivery_groups:
        logger.error("no found delivery group resource %s" % delivery_group_desktops.keys())
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_desktops.keys())
        
    for delivery_group_id, _desktop_ids in delivery_group_desktops.items():
        delivery_group = delivery_groups.get(delivery_group_id)
        if not delivery_group:
            continue
        
        ret = _detach_desktop_from_delivery_group(sender, delivery_group, desktops, _desktop_ids)
        if isinstance(ret, Error):
            return ret

    ret = PolicyGroup.set_desktop_security_policy_group(sender, desktop_ids)
    if isinstance(ret, Error):
        return ret

    return ret

def add_group_user_to_delivery_group(user, delivery_groups, group_name):
    
    ctx = context.instance()
    user_id = user.get("user_id")
    if not user_id:
        return None

    update_info = {}
    for delivery_group in delivery_groups:
        delivery_group_id = delivery_group["delivery_group_id"]
        existed_users = ctx.pgm.get_delivery_group_users(delivery_group_id)
        if not existed_users:
            existed_users = {}
        
        if user_id in existed_users:
            continue
        
        user_info = {
            "user_id": user_id,
            "user_name": user.get("user_name", ''),
            "real_name": user.get("real_name", ''),
            "delivery_group_id": delivery_group_id,
            "delivery_group_name": delivery_group["delivery_group_name"],
            "user_type": const.USER_TYPE_USER,
            "create_time": get_current_time(),
            "is_hide": 1,
            "user_group_name": group_name
            }

        update_info[user_id] = user_info

    if not ctx.pg.batch_insert(dbconst.TB_DELIVERY_GROUP_USER, update_info):
        logger.error("insert newly created delivery group for [%s] to db failed" % (delivery_group_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
    
    return None

def register_deliever_group_user(delivery_group, user_ids, desktop_users):

    ctx = context.instance()
    delivery_group_id = delivery_group["delivery_group_id"]
    
    existed_users = ctx.pgm.get_delivery_group_users(delivery_group_id)
    if not existed_users:
        existed_users = {}
    
    new_users = {}
    for user_id in user_ids:
        
        if user_id in existed_users:
            continue
        
        user_type = const.USER_TYPE_USER
        if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
            user_type = const.USER_TYPE_GROUP
        
        # check delivery group is in apply group
        user_info = {
            "user_id": user_id,
            "user_name": desktop_users.get(user_id, ""),
            "delivery_group_id": delivery_group_id,
            "user_type": user_type,
            "create_time": get_current_time(),
            }
        new_users[user_id] = user_info

    if new_users:
        if not ctx.pg.batch_insert(dbconst.TB_DELIVERY_GROUP_USER, new_users):
            logger.error("insert newly created delivery group for [%s] to db failed" % (delivery_group_id))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)
        
    return None

def check_delivery_group_user_names(delivery_group_id, new_user_ids=None):

    ctx = context.instance()
    if new_user_ids and not isinstance(new_user_ids, list):
        new_user_ids = [new_user_ids]

    user_names = {}
    if not new_user_ids:
        new_user_ids = []

    deli_users = ctx.pgm.get_delivery_group_users(delivery_group_id)
    if deli_users:
        user_names.update(deli_users)
    
    user_ids = []
    user_group_ids = []
    for user_id in new_user_ids:
        if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
            user_group_ids.append(user_id)
        elif user_id.startswith(UUID_TYPE_DESKTOP_USER):
            user_ids.append(user_id)

    if user_ids:
        ret = ctx.pgm.get_user_names(user_ids)
        if ret:
            user_names.update(ret)
    
    if user_group_ids:
        ret = ctx.pgm.get_user_group_names(user_group_ids)
        if ret:
            user_names.update(ret)

    return user_names

def check_delivery_group_in_auth_services(sender, desktop_names):
    
    ctx = context.instance()
    zone_id = sender["zone"]

    ret = ctx.pgm.get_auth_zone(zone_id)
    if not ret:
        return None
    
    auth_service_id = ret["auth_service_id"]
    user_names = {}
    user_group_names = {}
    for user_id, user_name in desktop_names.items():
        if user_id.startswith(UUID_TYPE_DESKTOP_USER_GROUP):
            user_group_names[user_name] = user_id
        elif user_id.startswith(UUID_TYPE_DESKTOP_USER):
            user_names[user_name] = user_id
    
    auth_users = {}
    if user_names:
        auth_users = ctx.auth.get_auth_users(auth_service_id,user_names=user_names.keys())
        if not auth_users:
            auth_users = {}
    
    auth_user_groups = {}
    if user_group_names:
        auth_user_groups = ctx.auth.get_auth_user_groups(auth_service_id,user_group_names=user_group_names.keys(), index_name=True)
        if not auth_user_groups:
            auth_user_groups = {}
    
    desktop_users = {}
    
    if auth_users:
        for user_name, _ in auth_users.items():
            user_id = user_names[user_name]
            desktop_users[user_id] = user_name
    
    if auth_user_groups:
        for user_group_name, _ in auth_user_groups.items():
            user_group_id = user_group_names[user_group_name]
            desktop_users[user_group_id] = user_group_name
    
    return desktop_users

def add_user_to_delivery_group(sender, delivery_group_id, user_ids, is_load=False):

    ctx = context.instance()
    if user_ids and not isinstance(user_ids, list):
        user_ids = [user_ids]
        
    if not user_ids:
        user_ids = []

    delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_id)
    if not delivery_groups:
        logger.error("no found delivery group %s" % (delivery_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id)
    delivery_group = delivery_groups[delivery_group_id]
    
    desktop_users = check_delivery_group_user_names(delivery_group_id, user_ids)
    if not desktop_users:
        return None
    
    desktop_users = check_delivery_group_in_auth_services(sender, desktop_users)
    if not desktop_users:
        return None
    
    if not is_load:

        delivery_group_name = delivery_group["delivery_group_name"]
        desktop_kind = delivery_group["desktop_kind"]

        ret = ctx.res.resource_reset_users_to_delivery_group(sender["zone"], delivery_group_name, desktop_users.values(), desktop_kind)
        if not ret:
            logger.error("create delivery group resource fail %s" % delivery_group_id)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_CLOUD_RESOURCE_FAILED, delivery_group_id)

    ret = register_deliever_group_user(delivery_group, user_ids, desktop_users)
    if isinstance(ret, Error):
        return ret

    return None

def del_user_from_delivery_group(sender, delivery_group_id, user_ids):
    
    ctx = context.instance()
    delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_id)
    if not delivery_groups:
        logger.error("no found delivery group resource %s, %s" % (delivery_group_id, user_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id)
    
    delivery_group = delivery_groups[delivery_group_id]

    ret = ctx.pgm.get_delivery_group_users(delivery_group_id)
    if not ret:
        logger.error("no found delivery group user resource %s, %s" % (delivery_group_id, user_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id)
    
    delivery_group_users = ret
    
    for user_id in user_ids:
        if user_id not in delivery_group_users:
            logger.error("user not in delivery group %s, %s" % (delivery_group_id, user_ids))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_USER_NOT_IN_DELIVERY_GROUP, (user_ids, delivery_group_id))
    
    user_names = []
    for user_id, user_name in delivery_group_users.items():

        if user_id in user_ids:
            continue
        user_names.append(user_name)

    delivery_group_name = delivery_group["delivery_group_name"]
    ret = ctx.res.resource_reset_users_to_delivery_group(sender["zone"], delivery_group_name, user_names, delivery_group["desktop_kind"])
    if not ret:
        logger.error("reset delivery group users fail %s" % delivery_group_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_CREATE_CLOUD_RESOURCE_FAILED, delivery_group_id) 

    ctx.pg.base_delete(dbconst.TB_DELIVERY_GROUP_USER, {"delivery_group_id": delivery_group_id, "user_id": user_ids})

    return None

def build_delivery_group_desktop_user(sender, desktop_data):
    
    ctx = context.instance()
    desktop_users = {}

    for desktop_user in desktop_data:
        
        desktop_list = explode_array(desktop_user, "|")
        if not desktop_list:
            continue
        
        desktop_id = desktop_list[0]
        desktop_users[desktop_id] = desktop_list[1:]

    desktop_ids = desktop_users.keys()
    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        logger.error("no found desktop resource %s" % (desktop_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_ids)

    for desktop_id, user_ids in desktop_users.items():
        
        if not user_ids:
            continue
        
        user_names = []
        for user_id in user_ids:
            if user_id.startswith("%s-" % UUID_TYPE_DESKTOP_USER):
                continue
            user_names.append(user_id)

        if user_names:
            name_users = ctx.pgm.get_users_by_name(user_names, sender["zone"])
            if not name_users:
                name_users = {}
                
            for user_name, user in name_users.items():
                if user_name not in user_ids:
                    continue
                
                del user_ids[user_name]
                user_ids.append(user["user_id"])
                
        desktop_users[desktop_id] = user_ids

    return desktop_users

def check_citrix_session_type(delivery_group_id, desktop_ids=None, desktop_group_ids=None):
    
    ctx = context.instance()
    
    if not desktop_group_ids and not desktop_ids:
        return False
    
    if desktop_ids:
        ret = ctx.pgm.get_group_by_desktop(desktop_ids)
        if not ret:
            return False
        desktop_group_ids = ret.keys()
    
    delivery_group = ctx.pgm.get_delivery_group(delivery_group_id)
    if not delivery_group:
        return False
    
    for desktop_group_id in desktop_group_ids:
        desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
        if not desktop_group:
            return False
        
        provision_type = desktop_group["provision_type"]
        if provision_type == const.PROVISION_TYPE_MCS:
            desktop_image_id = desktop_group["desktop_image_id"]
            desktop_image = ctx.pgm.get_desktop_image(desktop_image_id)
            if not desktop_image:
                return False
            session_type = desktop_image["session_type"]
        else:
            session_type = const.OS_SESSION_TYPE_MULTI

        delivery_group_type = delivery_group["delivery_group_type"]
        if session_type != delivery_group_type:
            return False

    return True

def check_delivery_group_user(sender, delivery_group_id, desktop_users):
    
    ctx = context.instance()

    
    delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_id)
    if not delivery_groups:
        logger.error("no found delivery group user resource %s" % (delivery_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id)
     
    delivery_group = delivery_groups[delivery_group_id]

    delivery_group_user = ctx.pgm.get_delivery_group_user_ids(delivery_group_id)
    if not delivery_group_user:
        delivery_group_user = {}

    new_user_ids = []
    for _, user_ids in desktop_users.items():
        if not user_ids:
            continue
        
        for user_id in user_ids:
            if user_id not in delivery_group_user:
                new_user_ids.append(user_id)

    if new_user_ids:
        ret = add_user_to_delivery_group(sender, delivery_group_id, new_user_ids)
        if isinstance(ret, Error):
            return ret
    
    return delivery_group

def check_attach_delivery_group_desktop(sender, delivery_group, desktop_ids, is_load=False):

    ctx = context.instance()
    delivery_group_id = delivery_group["delivery_group_id"]

    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        logger.error("no found desktop %s" % (desktop_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_ids)

    desktop_name = ctx.pgm.get_desktop_name(desktop_ids)
    if not desktop_name:
        desktop_name = {}
    
    hostnames = desktop_name.values()
    computers = ctx.res.resource_describe_computers(sender["zone"], machine_names=hostnames)
    if not computers:
        computers = {}
    delivery_group_user = ctx.pgm.get_delivery_group_users(delivery_group_id)
    if not delivery_group_user:
        delivery_group_user = {}
    
    desktop_group_ids = []
    for desktop_id, desktop in desktops.items():
        instance_id = desktop["instance_id"]
        if not instance_id:
            logger.error("desktop no instance %s" % (desktop_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_id)
        hostname = desktop["hostname"]
        computer = computers.get(hostname)
        c_dg_name = computer["delivery_group_name"] if computer else ""
        dg_id = desktop["delivery_group_id"]
        if dg_id:
            logger.error("desktop %s has already add the delivery group %s" % (desktop_id, dg_id))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_ALREADY_ADD_DELIVERY_GROUP, (desktop_id, dg_id))
        
        if not is_load and c_dg_name:
            logger.error("desktop %s has already add the delivery group %s" % (desktop_id, c_dg_name))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_DESKTOP_ALREADY_ADD_DELIVERY_GROUP, (desktop_id, c_dg_name))

        desktop_group_id = desktop["desktop_group_id"]
        if desktop_group_id not in desktop_group_ids:
            desktop_group_ids.append(desktop_group_id)

    allocation_type = delivery_group["allocation_type"]
    desktop_groups = ctx.pgm.get_desktop_groups(desktop_group_ids)
    if not desktop_groups:
        logger.error("no found desktop group  %s" % (desktop_group_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_group_ids)

    for desktop_group_id, desktop_group in desktop_groups.items():
        if desktop_group["allocation_type"] != allocation_type:
            logger.error("desktop group %s %s, allocation_type dismatch %s, %s" % (desktop_group["desktop_group_name"], delivery_group["delivery_group_name"],desktop_group["allocation_type"], allocation_type))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_CITIRX_ALLOC_TYPE_DISMATCH, (desktop_group["allocation_type"]))
    
    return desktops

def check_detach_delivery_group_desktop(desktop_ids):
    
    detach_desktop = {}
    ctx = context.instance()

    desktops = ctx.pgm.get_desktops(desktop_ids)
    if not desktops:
        logger.error("no found desktop resource %s" % (desktop_ids))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_ids)
    
    for desktop_id, desktop in desktops.items():       
        if not desktop["delivery_group_id"]:
            continue
    
        detach_desktop[desktop_id] = desktop
    
    return detach_desktop

def check_computer_session(sender, desktop):
    
    ctx = context.instance()
    hostname = desktop["hostname"]
    desktop_id = desktop["desktop_id"]
    ret = ctx.res.resource_describe_computers(sender["zone"], machine_names=hostname)
    if not ret:
        logger.error("no found resource computer %s" % (hostname))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, hostname)
    update_info = {}
    for _, computer in ret.items():
        session_status = computer.get("session_state")
        if session_status is None:
            continue
        
        if session_status:
            session_status = 1
        else:
            session_status = 0
        
        if desktop["connect_status"] != session_status:
            update_info["connect_status"] = session_status
    
    if update_info:
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: update_info}):
            logger.error("update desktop session status fail %s" % update_info)
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
        
        desktop["connect_status"] = update_info["connect_status"]
        
    return desktop

def check_desktop_allocate_type(desktop, check_type):
    
    ctx = context.instance()
    desktop_group_id = desktop.get("desktop_group_id")
    if not desktop_group_id:
        logger.error("citrix desktop no found desktop group id")
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED)
        
    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id, extras=[])
    if not desktop_group:
        logger.error("desktop group no found %s" % (desktop_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_group_id)
    
    if check_type != desktop_group["allocation_type"]:
        logger.error("desktop allocate type dismatch %s, %s" % (check_type, desktop_group["allocation_type"]))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_CITIRX_ALLOC_TYPE_DISMATCH, desktop_group["allocation_type"])
    
    return None

def get_compute_users(zone_id, hostnames):
    
    ctx = context.instance()
    
    if not isinstance(hostnames, list):
        hostnames = [hostnames]
    
    computers = ctx.res.resource_describe_computers(zone_id, machine_names=hostnames)
    if not computers:
        return {}
    
    computer_users = {}
    
    for hostname, computer in computers.items():
        assign_user_str = computer["assign_user"]
        if not assign_user_str:
            continue
        assign_users = assign_user_str.split(",")
        
        if hostname not in computer_users:
            computer_users[hostname] = []
        
        for assign_user in assign_users:
            computer_users[hostname].append(assign_user.lower())
    
    return computer_users

def check_attach_desktop_to_delivery_group_user(sender, desktop, users):
    
    ret = check_desktop_allocate_type(desktop, const.CITRIX_ALLOC_TYPE_STATIC)
    if isinstance(ret, Error):
        return ret

    attach_users = {}

    hostname = desktop["hostname"]
    ret = get_compute_users(sender["zone"], hostname)
    if not ret:
        ret = {}
    
    computer_users = ret.get(hostname, [])

    for user_id, user in users.items():
        user_name = user["user_name"]
        
        if user_name.lower() in computer_users:
            continue
        attach_users[user_id] = user
    
    return attach_users

def attach_desktop_to_delivery_group_user(sender, desktop, user):

    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    user_id = user["user_id"]

    ret = ctx.res.resource_attach_computer_to_user(sender["zone"], desktop["hostname"], user["user_name"])
    if not ret:
        logger.error("desktop attach user fail %s, %s" % (desktop_id, user_id))
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_DESKTOP_ATTACH_USER_FAIL, (desktop_id, user_id))

    ret = ResUser.attach_user_to_desktop_resource(ctx, desktop_id, user_id)
    if isinstance(ret, Error):
        return ret

    delivery_group_id = desktop["delivery_group_id"]
    ret = add_user_to_delivery_group(sender, delivery_group_id, user_id)
    if isinstance(ret, Error):
        return ret

    return None

def detach_desktop_from_delivery_group_user(sender, desktop, user_ids=None):
    
    ctx = context.instance()
    desktop_id = desktop["desktop_id"]
    hostname = desktop["hostname"]
    
    desktop_users = ResUser.get_desktop_resource_user(ctx, desktop_id)
    if not desktop_users:
        desktop_users = {}
    
    desktop_user = desktop_users.get(desktop_id, [])
    
    if not user_ids:
        user_ids = desktop_user
    
    if not user_ids:
        return None

    ret = get_compute_users(sender["zone"], hostname)
    if not ret:
        ret = {}
    
    computer_users = ret.get(hostname, [])
    
    user_names = ctx.pgm.get_user_names(user_ids)
    if not user_names:
        user_names = {}
    
    detach_computer_users = []
    detach_desktop_users = []
    for user_id, user_name in user_names.items():
        if user_name in computer_users:
            detach_computer_users.append(user_name)
        
        if user_id in desktop_user:
            detach_desktop_users.append(user_id)
    
    if detach_computer_users:
        for user_name in detach_computer_users:
            ret = ctx.res.resource_detach_computer_from_user(sender["zone"], desktop["hostname"], user_name)
            if not ret:
                logger.error("detach compute from user fail %s, %s" % (desktop_id, user_name))
                return Error(ErrorCodes.PERMISSION_DENIED,
                             ErrorMsg.ERR_MSG_UPDATE_CLOUD_RESOURCE_FAILED, desktop_id)

    if detach_desktop_users:
        ret = ResUser.detach_user_from_desktop_resource(ctx, desktop_id, detach_desktop_users)
        if isinstance(ret, Error):
            return ret

    return None
    
def set_delivery_group_mode(sender, delivery_group_id, mode):
    
    ctx = context.instance()
    delivery_groups = ctx.pgm.get_delivery_groups(delivery_group_id)
    if not delivery_groups:
        logger.error("no found delivery group user resource %s" % (delivery_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, delivery_group_id)
    delivery_group = delivery_groups[delivery_group_id]
    
    dg_mode = delivery_group["mode"]
    if dg_mode == mode:
        return None

    delivery_group_name = delivery_group["delivery_group_name"]

    ret = ctx.res.resource_set_delivery_group_mode(sender["zone"], delivery_group_name, mode)
    if ret is None:
        logger.error("modify delivery group mode %s, %s" % (delivery_group_id, mode))
        return Error(ErrorCodes.PERMISSION_DENIED,
                     ErrorMsg.ERR_MSG_MODIFY_DELIVERY_GROUP_MODE_FAIL, (delivery_group_id, mode))
    
    update_info = {
                    "mode": mode,
                  }
    if not ctx.pg.batch_update(dbconst.TB_DELIVERY_GROUP, {delivery_group_id: update_info}):
        logger.error("update delivery group fail %s" % delivery_group_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None

def set_citrix_desktop_mode(sender, desktop_id, mode):

    ctx = context.instance()
    desktops = ctx.pgm.get_desktops(desktop_id)
    if not desktops:
        logger.error("no found desktop resource %s" % (desktop_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_id)

    desktop = desktops[desktop_id]

    desktop_mode = desktop["desktop_mode"]
    if desktop_mode == mode:
        return None

    desktop_group_id = desktop["desktop_group_id"]
    desktop_group = ctx.pgm.get_desktop_group(desktop_group_id)
    if not desktop_group:
        logger.error("no found desktop group %s" % (desktop_group_id))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND,
                     ErrorMsg.ERR_MSG_RESOURCE_NOT_FOUND, desktop_group_id)
    
    allocation_type = desktop_group["allocation_type"]
    desktop_kind = const.CITRIX_DESKTOP_KIND_PRIVATE
    if allocation_type == const.CITRIX_ALLOC_TYPE_RANDOM:
        desktop_kind = const.CITRIX_DESKTOP_KIND_SHARED

    hostname = desktop["hostname"]
    ret = ctx.res.resource_describe_computers(sender["zone"], machine_names=hostname)
    if ret:
        ret = ctx.res.resource_set_computer_mode(sender["zone"], hostname, desktop_kind, mode)
        if ret is None:
            logger.error("modify delivery group mode %s, %s" % (hostname, mode))
            return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_MODIFY_DELIVERY_GROUP_MODE_FAIL, (hostname, mode))
    
    update_info = {
                    "desktop_mode": mode,
                  }
    if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: update_info}):
        logger.error("update desktop mode fail %s" % desktop_id)
        return Error(ErrorCodes.INTERNAL_ERROR,
                     ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)
    
    return None
