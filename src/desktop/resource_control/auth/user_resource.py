
import context

import db.constants as dbconst
import resource_control.desktop.desktop as Desktop
import resource_control.desktop.desktop_group as DesktopGroup
import resource_control.citrix.delivery_group as DeliveryGroup
import resource_control.permission as Permission
from common import is_citrix_platform

def check_auth_user_resource(sender, user_id):
    
    ctx = context.instance()
    # check desktop
    ret = ctx.pgm.get_desktops(owner=user_id)
    if ret:
        desktop_ids = ret.keys()
        if is_citrix_platform(ctx, sender["zone"]):
            for _, desktop in ret.items():
                DeliveryGroup.detach_desktop_from_delivery_group_user(sender, desktop)
        else:
            for desktop_id in desktop_ids:
                Desktop.detach_user_from_dekstop(desktop_id)
    
    # check desktop group
    ret = ctx.pgm.get_desktop_group_by_user(user_id)
    if ret:
        desktop_group_ids = ret.keys()
        ret = ctx.pgm.get_desktop_groups(desktop_group_ids)
        if not ret:
            ret = {}

        desktop_groups = ret
        for _, desktop_group in desktop_groups.items():
            DesktopGroup.detach_user_from_dekstop_group(sender, desktop_group, user_id)
    
    # check delivery group
    ret = ctx.pgm.get_delivery_group_by_user(user_id)
    if ret:
        delivery_group_ids = ret
        for delivery_group_id in delivery_group_ids:
            DeliveryGroup.del_user_from_delivery_group(sender, delivery_group_id, user_id)
    
    # check user scope
    ret = ctx.pgm.get_resource_scope_by_user(user_id)
    if ret:
        Permission.clear_user_resource_scope(user_ids=user_id)
    
    # check custom
    ret = ctx.pgm.get_module_custom_user(user_ids=user_id)
    if ret:
        conditions = {"user_id": user_id}
        ctx.pg.base_delete(dbconst.TB_MODULE_CUSTOM_USER, conditions)
        
    # notice
    ret = ctx.pgm.get_notice_by_user(user_id)
    if ret:
        conditions = {"user_id": user_id}
        ctx.pg.base_delete(dbconst.TB_NOTICE_USER, conditions)

    import resource_control.user.apply_approve as ApplyApprove
    ApplyApprove.clean_user_in_apply_group(user_id)
    ApplyApprove.clean_user_in_approve_group(user_id)
    ApplyApprove.clear_user_apply_form(user_id)

    return

def check_auth_user_group_resource(sender, user_group_id):
    
    ctx = context.instance()
    
    # check delivery group
    ret = ctx.pgm.get_delivery_group_by_user(user_group_id)
    if ret:
        delivery_group_ids = ret
        for delivery_group_id in delivery_group_ids:
            DeliveryGroup.del_user_from_delivery_group(sender, delivery_group_id, user_group_id)
       
    # notice
    ret = ctx.pgm.get_notice_by_user(user_group_id)
    if ret:
        conditions = {"user_id": user_group_id}
        ctx.pg.base_delete(dbconst.TB_NOTICE_USER, conditions)
    
    return