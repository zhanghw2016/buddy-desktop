import context
import db.constants as dbconst
from utils.misc import get_current_time
from utils.id_tool import UUID_TYPE_RECORD_DESKTOP_LOGIN, get_uuid
from log.logger import logger

def create_desktop_login_record(user_id, zone_id, desktop_id, client_ip, connect_status, connect_time=None, disconnect_time=None, session_uid=None):
    ctx = context.instance()
    
    curtime = get_current_time(to_seconds=False)
    desktop_login_record_id = get_uuid(UUID_TYPE_RECORD_DESKTOP_LOGIN,
                                       ctx.checker, 
                                       long_format=True)

    login_record = {}
    login_record['desktop_login_record_id'] = desktop_login_record_id
    login_record['user_id'] = user_id
    login_record['user_name'] = ctx.pgm.get_user_name(user_id)
    login_record['zone_id'] = zone_id
    login_record['desktop_id'] = desktop_id
    login_record['client_ip'] = client_ip
    login_record['connect_status'] = connect_status
    if connect_time:
        login_record['connect_time'] = connect_time
    else:
        login_record['connect_time'] = curtime
    if disconnect_time:
        login_record['disconnect_time'] = disconnect_time
    if session_uid:
        login_record['session_uid'] = session_uid

    if not ctx.pg.insert(dbconst.TB_DESKTOP_LOGIN_RECORD, login_record):
        logger.error("create desktop login record [%s] failed." % (login_record))
        return None

    return desktop_login_record_id

def modify_desktop_login_record(desktop_login_record_id, connect_status=None, disconnect_time=None):
    ctx = context.instance()
    
    curtime = get_current_time(to_seconds=False)

    conds = {
        "desktop_login_record_id": desktop_login_record_id
        }

    login_record = {}
    if connect_status:
        login_record['connect_status'] = connect_status
    else:
        login_record['connect_time'] = curtime
    if disconnect_time:
        login_record['disconnect_time'] = disconnect_time

    if len(login_record) == 0:
        return desktop_login_record_id

    if not ctx.pg.base_update(dbconst.TB_DESKTOP_LOGIN_RECORD, conds, login_record):
        logger.error("modify desktop login record [%s] failed." % (login_record))
        return None

    return desktop_login_record_id

def describe_desltop_login_record(user_id=None, zone_id=None, desktop_id=None):
    ctx = context.instance()

    if user_id is None and zone_id is None and desktop_id is None:
        return []

    login_record = {}
    if user_id:
        login_record['user_id'] = user_id
    if zone_id:
        login_record['zone_id'] = zone_id
    if desktop_id:
        login_record['desktop_id'] = desktop_id

    result = ctx.pg.base_get(dbconst.TB_DESKTOP_LOGIN_RECORD, 
                             login_record,
                             sort_key="connect_time",
                             reverse=True,
                             limit=1)
    if result is None:
        logger.error("describe desktop login record [%s] failed." % (login_record))
        return None

    return result
