from db.constants import TB_API_LIMIT
from utils.misc import get_current_time
import datetime

def load_api_limit(ctx):

    conditions = {"enable": 1}
    api_limit_set = ctx.pg.base_get(TB_API_LIMIT, conditions)
    if not api_limit_set:
        return {}

    api_limits = {}
    for api_limit in api_limit_set:

        api_action = api_limit["api_action"]
        api_limit["update_time"] = get_current_time()
        api_limit["access_time"] = 0
        api_limits[api_action] = api_limit

    return api_limits

def check_api_limit(ctx, action):
    
    if action not in ctx.api_limits:
        return True
    
    api_limit = ctx.api_limits[action]
    refresh_interval = api_limit.get("refresh_interval", 60)
    refresh_time = api_limit.get("refresh_time", 5)
    access_time = api_limit.get("access_time", 0)
    update_time = api_limit.get("update_time")
    if not update_time:
        update_time = get_current_time()
        ctx.api_limits[action]["update_time"] = update_time
        ctx.api_limits[action]["update_time"] = 1
        return True

    delta = datetime.timedelta(seconds=int(refresh_interval))

    curr_time = get_current_time()
    if update_time + delta <= curr_time:
        ctx.api_limits[action]["update_time"] = curr_time
        ctx.api_limits[action]["access_time"] = 1
        return True
    
    if access_time < refresh_time:
        access_time = access_time + 1
        ctx.api_limits[action]["access_time"] = access_time
        return True
    
    return False
    
        
    
    