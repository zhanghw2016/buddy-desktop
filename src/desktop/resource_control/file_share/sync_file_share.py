from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
import constants as const
import db.constants as dbconst

def check_update_file_share_group(current_base_dn,current_file_share_group_dn, old_file_share_group_dn,new_file_share_group_dn):

    update_file_share_group = {}
    if old_file_share_group_dn in current_file_share_group_dn:
        update_file_share_group["file_share_group_dn"] = current_file_share_group_dn.replace(old_file_share_group_dn,new_file_share_group_dn)
        update_file_share_group["base_dn"] = current_base_dn.replace(old_file_share_group_dn,new_file_share_group_dn)

    return update_file_share_group

def check_update_file_share_group_user(current_file_share_group_dn, old_file_share_group_dn,new_file_share_group_dn):

    update_file_share_group_user = {}
    if old_file_share_group_dn in current_file_share_group_dn:
        update_file_share_group_user["file_share_group_dn"] = current_file_share_group_dn.replace(old_file_share_group_dn,new_file_share_group_dn)

    return update_file_share_group_user

def check_update_file_share_group_file(current_file_share_group_dn,current_file_share_group_file_dn, old_file_share_group_dn,new_file_share_group_dn):

    update_file_share_group_file = {}
    if old_file_share_group_dn in current_file_share_group_dn:
        update_file_share_group_file["file_share_group_dn"] = current_file_share_group_dn.replace(old_file_share_group_dn,new_file_share_group_dn)
        update_file_share_group_file["file_share_group_file_dn"] = current_file_share_group_file_dn.replace(old_file_share_group_dn,new_file_share_group_dn)

    return update_file_share_group_file

def update_file_share_group_dn(update_file_share_groups):

    ctx = context.instance()
    for file_share_group_id, update_info in update_file_share_groups.items():

        conditions = {"file_share_group_id": file_share_group_id}
        if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_GROUP, conditions, update_info):
            logger.error("update file share group %s info %s fail" % (conditions, update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def update_file_share_group_user_dn(update_file_share_group_users):

    ctx = context.instance()
    for file_share_group_id, update_info in update_file_share_group_users.items():

        conditions = {"file_share_group_id": file_share_group_id}
        if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_GROUP_USER, conditions, update_info):
            logger.error("update file share group user %s info %s fail" % (conditions, update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def update_file_share_group_file_dn(update_file_share_group_files):

    ctx = context.instance()
    for file_share_group_file_id, update_info in update_file_share_group_files.items():

        conditions = {"file_share_group_file_id": file_share_group_file_id}
        if not ctx.pg.base_update(dbconst.TB_FILE_SHARE_GROUP_FILE, conditions, update_info):
            logger.error("update file share group file %s info %s fail" % (conditions, update_info))
            return Error(ErrorCodes.INTERNAL_ERROR,
                         ErrorMsg.ERR_MSG_UPDATE_RESOURCE_FAILED)

    return None

def sync_file_share_group(file_share_group_id, old_file_share_group_dn,new_file_share_group_dn):

    ctx = context.instance()
    file_share_groups = ctx.pgm.search_file_share_groups(file_share_group_dn=old_file_share_group_dn)
    if not file_share_groups:
        file_share_groups = {}

    update_file_share_groups = {}
    for file_share_group_id, file_share_group in file_share_groups.items():

        current_file_share_group_dn = file_share_group["file_share_group_dn"]
        current_base_dn = file_share_group["base_dn"]
        ret = check_update_file_share_group(current_base_dn,current_file_share_group_dn, old_file_share_group_dn,new_file_share_group_dn)
        if ret:
            update_file_share_groups[file_share_group_id] = ret

    if update_file_share_groups:
        ret = update_file_share_group_dn(update_file_share_groups)
        if isinstance(ret, Error):
            return ret

    return None

def sync_file_share_group_user(file_share_group_id, old_file_share_group_dn,new_file_share_group_dn):

    ctx = context.instance()
    file_share_group_users = ctx.pgm.search_file_share_group_users(file_share_group_dn=old_file_share_group_dn)

    if not file_share_group_users:
        file_share_group_users = {}

    update_file_share_group_users = {}
    for file_share_group_id, file_share_group_user in file_share_group_users.items():

        current_file_share_group_dn = file_share_group_user["file_share_group_dn"]
        ret = check_update_file_share_group_user(current_file_share_group_dn, old_file_share_group_dn,new_file_share_group_dn)
        if ret:
            update_file_share_group_users[file_share_group_id] = ret

    if update_file_share_group_users:
        ret = update_file_share_group_user_dn(update_file_share_group_users)
        if isinstance(ret, Error):
            return ret

    return None

def sync_file_share_group_file(file_share_group_id, old_file_share_group_dn,new_file_share_group_dn):

    ctx = context.instance()
    file_share_group_files = ctx.pgm.search_file_share_group_files(file_share_group_dn=old_file_share_group_dn,trashed_status=const.FILE_SHARE_RECYCLES_TRASHED_STATUS_INACTIVE)
    if not file_share_group_files:
        file_share_group_files = {}

    update_file_share_group_files = {}
    for file_share_group_file_id, file_share_group_file in file_share_group_files.items():

        current_file_share_group_dn = file_share_group_file["file_share_group_dn"]
        current_file_share_group_file_dn = file_share_group_file["file_share_group_file_dn"]
        ret = check_update_file_share_group_file(current_file_share_group_dn,current_file_share_group_file_dn, old_file_share_group_dn,new_file_share_group_dn)
        if ret:
            update_file_share_group_files[file_share_group_file_id] = ret

    if update_file_share_group_files:
        ret = update_file_share_group_file_dn(update_file_share_group_files)
        if isinstance(ret, Error):
            return ret

    return None


