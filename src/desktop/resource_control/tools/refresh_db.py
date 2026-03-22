import db.constants as dbconst
import context

from error.error import Error
from api.user.resource_user import refresh_desktop_users

def refresh_desktop_owner():
    
    ctx = context.instance()
    ret = ctx.pg.get_all(dbconst.TB_DESKTOP, columns=["desktop_id"])
    if not ret:
        return None

    desktop_ids = []
    for desktop in ret:
        desktop_id = desktop["desktop_id"]
        desktop_ids.append(desktop_id)
    
    ret = refresh_desktop_users(ctx, desktop_ids)
    if isinstance(ret, Error):
        return ret

    return ret

