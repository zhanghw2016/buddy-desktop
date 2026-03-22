import constants as const
import api.user.resource_user as ResUser
import db.constants as dbconst
from log.logger import logger

def build_refresh_desktop_info(desktop, computer):
    
    update_keys = {
        "reg_state": "reg_state",
        "status": "power_state",
        "connect_status":"session_state" ,
        "desktop_mode": "mode",
        "instance_id": "hosted_machine_id",
        "delivery_group_name": "delivery_group_name"
        }

    update_info = {}
    for desk_key, comp_key in update_keys.items():
        
        desk_value = desktop[desk_key]
        comp_value = computer[comp_key]
        if desk_key == "status":
            if comp_value not in const.CITRIX_STATUS_MAP:
                continue
            
            comp_value = const.CITRIX_STATUS_MAP[comp_value]
        
        if desk_key == "connect_status":
            if comp_value:
                comp_value = 1
            else:
                comp_value = 0

        if desk_key == "desktop_mode":
            comp_value = const.DESKTOP_GROUP_STATUS_MAINT if comp_value == 'True' else const.DESKTOP_GROUP_STATUS_NORMAL
        
        if desk_value != comp_value:
            update_info[desk_key] = comp_value
    
    return update_info

def build_citrix_desktop_delivery_group(ctx, update_info,zone_id):
    
    delivery_group_name = update_info.get("delivery_group_name")
    if delivery_group_name is None:
        return None
    
    if not delivery_group_name:
        update_info["delivery_group_name"] = ''
        update_info["delivery_group_id"] = ''
        return None
    
    ret = ctx.pgm.get_delivery_group_by_name(delivery_group_name,zone_id)
    if not ret:
        update_info["delivery_group_name"] = ''
        update_info["delivery_group_id"] = ''
        return None
    
    delivery_group = ret.get(delivery_group_name)
    if not delivery_group:
        return None
    
    update_info["delivery_group_name"] = delivery_group_name
    update_info["delivery_group_id"] = delivery_group["delivery_group_id"]

    return None

def check_citrix_update(ctx, desktop, computer):
    
    desktop_id = desktop["desktop_id"]
    zone_id = desktop["zone"]
    update_info = build_refresh_desktop_info(desktop, computer)
    ResUser.refresh_citrix_desktop_owner(ctx, desktop, computer)
    build_citrix_desktop_delivery_group(ctx, update_info,zone_id)

    if update_info:
        if not ctx.pg.batch_update(dbconst.TB_DESKTOP, {desktop_id: update_info}):
            logger.error("update refresh desktop info %s to desktop fail %s" % (desktop_id, update_info))
            return None

    return update_info
