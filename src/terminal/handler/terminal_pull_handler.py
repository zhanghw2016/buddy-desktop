'''
Created on 2018-5-17

@author: yunify
'''
from log.logger import logger
import context

def handle_sync_zone_info(req):
    zone_id = req.get("zone_id")
    if not zone_id:
        return 0

    ctx = context.instance()
    ctx.zone_builder.load_zone(zone_id)

    return 0
