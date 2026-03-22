import constants as const
import traceback
from log.logger import logger
import context

def handle_sync_zone_info(req):
    logger.debug("handle_sync_zone_info")
    zone_id = req.get("zone_id")
    if not zone_id:
        return 0

    ctx = context.instance()
    ctx.zone_builder.load_zone(zone_id)
    logger.debug("ctx.zones == %s" %(ctx.zones))

    return 0

class Zone_Sync_Handler():

    def __init__(self):
        self.handler = {
            const.ZONE_SYNC_ACTION_SYNC_ZONE_INFO: handle_sync_zone_info,
        }
   
    def handle(self, action, req):
        try:
            if action in self.handler:
                # handle directly
                ret = self.handler[action](req)
                if ret < 0:
                    logger.error("zone sync handler %s resource %s fail" % (action, req))

            return
        except:
            logger.critical("handle request [%s] failed: [%s] [%s]" % (action, req, traceback.format_exc()))
            return

