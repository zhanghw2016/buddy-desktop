'''
Created on 2012-10-17

@author: yunify
'''
import context
from log.logger import logger

def check_sync_zone_info():

    ctx = context.instance()
    zones = ctx.pgm.get_zones()
    if zones:
        zone_ids = []
        for zone_id, zone in zones.items():
            zone_ids.append(zone_id)

        for zone_id,_ in ctx.zones.items():
            if zone_id not in zone_ids:
                zone_ids.append(zone_id)

        for zone_id in zone_ids:
            ctx.zone_builder.load_zone(zone_id)

    return 0
