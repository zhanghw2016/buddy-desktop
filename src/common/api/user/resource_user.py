import db.constants as dbconst
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
from log.logger import logger

def attach_user_to_desktop_resource(ctx, desktop_id, user_ids):
    
    if not isinstance(user_ids, list):
        user_ids = [user_ids]
    
    ret = add_user_to_resource(ctx, desktop_id, user_ids)
    if isinstance(ret, Error):
        return ret

    desktop_disks = ctx.pgm.get_desktop_disk(desktop_ids=desktop_id)
    if not desktop_disks:
        return None
    desktop_disk = desktop_disks.get(desktop_id)
    if not desktop_disk:
        return None

    for disk_id in desktop_disk:
        ret = add_user_to_resource(ctx, disk_id, user_ids)
        if isinstance(ret, Error):
            return ret
    
    return None

def detach_user_from_desktop_resource(ctx, desktop_id, user_ids):
        
    ret = del_user_from_resource(ctx, desktop_id, user_ids)
    if isinstance(ret, Error):
        return ret

    desktop_disks = ctx.pgm.get_desktop_disk(desktop_ids=desktop_id)
    if not desktop_disks:
        return None
    
    disk_ids = desktop_disks.get(desktop_id)
    if not disk_ids:
        return None

    for disk_id in disk_ids:
        ret = del_user_from_resource(ctx, disk_id, user_ids)
        if isinstance(ret, Error):
            return ret
    
    return None

def del_user_from_resource(ctx, resource_id, user_ids=None):
    
    if user_ids and not isinstance(user_ids, list):
        user_ids = [user_ids]

    existed_users = ctx.pgm.get_resource_user_ids(resource_id, user_ids=user_ids)
    if not existed_users:
        existed_users = {}
    existed_user = existed_users.get(resource_id, [])
    
    if not user_ids:
        user_ids = existed_user
    
    del_users = []
    for user_id in user_ids:
        if user_id not in existed_user:
            continue
        
        del_users.append(user_id)
    
    if del_users:
        ctx.pg.base_delete(dbconst.TB_RESOURCE_USER, {"resource_id" : resource_id, "user_id" :del_users})
        
    return None

def add_user_to_resource(ctx, resource_id, user_ids):
    
    if not user_ids:
        return None

    if not isinstance(user_ids, list):
        user_ids = [user_ids]
    
    existed_users = ctx.pgm.get_resource_user_ids(resource_id, user_ids=user_ids)
    if not existed_users:
        existed_users = {}
    
    existed_user = existed_users.get(resource_id, [])
    
    add_user = []
    for user_id in user_ids:
        if user_id in existed_user:
            continue
        
        add_user.append(user_id)
    
    resource_type = dbconst.RESTYPE_DESKTOP
    if resource_id.startswith(dbconst.RESTYPE_DESKTOP_DISK):
        resource_type = dbconst.RESTYPE_DESKTOP_DISK

    user_names = ctx.pgm.get_user_names(add_user)
    if not user_names:
        user_names = {}

    update_info = {}
    for user_id in add_user:
        user_name = user_names.get(user_id, "")
        
        update_info[user_id] = {
            "resource_id": resource_id,
            "resource_type": resource_type,
            "user_id": user_id,
            "user_name": user_name,
            "is_sync": 1
            }

    if update_info:
        if not ctx.pg.batch_insert(dbconst.TB_RESOURCE_USER, update_info):
            logger.error("insert newly created resource user [%s] to db failed" % (update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_CREATE_RESOURCE_FAILED)

    return add_user

def refresh_desktop_users(ctx, desktop_ids, ignore_sync=False):
    
    is_sync=0
    if not ignore_sync:
        is_sync = None
    
    sync_desktop_users = {}
    
    for i in xrange(0, len(desktop_ids), dbconst.DEFAULT_LIMIT):
        end = i + dbconst.DEFAULT_LIMIT
        if end > len(desktop_ids):
            end = len(desktop_ids)

        desk_ids = desktop_ids[i:end]
        desktop_users = ctx.pgm.get_resource_users(desk_ids, is_sync=is_sync)
        if desktop_users:
            sync_desktop_users.update(desktop_users)

    refresh_desktop = []
    for desktop_id in desktop_ids:
        if not ignore_sync:
            if desktop_id in sync_desktop_users:
                continue
        
        refresh_desktop.append(desktop_id)
    
    desktop_owner = ctx.pgm.get_desktop_owner(refresh_desktop)
    if not desktop_owner:
        return None
    
    update_count = 0
    for desktop_id in refresh_desktop:
        user_id = desktop_owner.get(desktop_id)
        if not user_id:
            continue
        ret = add_user_to_resource(ctx, desktop_id, user_id)
        if ret:
            update_count = update_count + len(ret)
    
    return update_count

def get_desktop_resource_user(ctx, desktop_ids):
        
    if not desktop_ids:
        return None
    
    if not isinstance(desktop_ids, list):
        desktop_ids = [desktop_ids]
    
    ret = refresh_desktop_users(ctx, desktop_ids)
    if isinstance(ret, Error):
        return ret

    desktop_users = ctx.pgm.get_resource_users(desktop_ids)
    if not desktop_users:
        desktop_users = {}
    
    desktop_user_info = {}
    for desktop_id, desktop_user in desktop_users.items():
        
        if desktop_id not in desktop_user_info:
            desktop_user_info[desktop_id] = []
        
        for user in desktop_user:
            user_id = user["user_id"]
            desktop_user_info[desktop_id].append(user_id)
    
    return desktop_user_info

def refresh_citrix_desktop_owner(ctx, desktop, computer):
    
    desktop_id = desktop["desktop_id"]
    desktop_zone = desktop["zone"]
    
    assign_users = []
    assign_user_str = computer["assign_user"]
    if assign_user_str:
        assign_user_list = assign_user_str.split(",")
        for assign_user in assign_user_list:
            assign_users.append(assign_user)

    desktop_users = get_desktop_resource_user(ctx, desktop_id)
    if not desktop_users:
        desktop_users = {}
    desktop_user = desktop_users.get(desktop_id, [])
    
    desktop_usernames = ctx.pgm.get_user_names(desktop_user)
    if not desktop_usernames:
        desktop_usernames = {}

    add_users = []
    for assign_user_name in assign_users:
        if assign_user_name in desktop_usernames.values():
            continue

        add_users.append(assign_user_name)
    
    del_users = []
    for user_id, user_name in desktop_usernames.items():
        
        if user_name in assign_users:
            continue
        
        del_users.append(user_id)
    
    if add_users:
        ret = ctx.pgm.get_zone_user_id_by_name(desktop_zone, add_users)
        if not ret:
            ret = {}

        ret = attach_user_to_desktop_resource(ctx, desktop_id, ret.values())
        if isinstance(ret, Error):
            return ret
        
    if del_users:
        ret = detach_user_from_desktop_resource(ctx, desktop_id, del_users)
        if isinstance(ret, Error):
            return ret

    return None
            