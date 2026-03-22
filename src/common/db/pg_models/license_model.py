import base64
import constants as const
import db.constants as dbconst
from log.logger import logger

class LicensePGModel():
    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def load_license_info(self):
        result = const.DEFAULT_LICENSE
        condition = {"config_key": "license_str"}
        lincense_info = self.pg.base_get(dbconst.TB_VDI_SYSTEM_CONFIG, condition)
        if lincense_info is None or len(lincense_info) == 0:
            logger.error("lincese unknown")
            return result

        license_str = lincense_info[0].get("config_value", "")
        
        if not license_str:
            logger.error("lincese is none")
            return result

        missing_padding = 4-len(license_str)%4
        if missing_padding:
            license_str+=b'='*missing_padding
        license_str = base64.decodestring(license_str)

        missing_padding = 4-len(license_str)%4
        if missing_padding:
            license_str+=b'='*missing_padding
        license_str = base64.decodestring(license_str)

        missing_padding = 4-len(license_str)%4
        if missing_padding:
            license_str+=b'='*missing_padding
        license_str = base64.decodestring(license_str)

        origin = str.split(license_str, ";")
        if not origin or len(origin)!=3:
            return result

        logger.info(origin)
        result["number"] = int(origin[0])
        result["company"] = origin[1]
        result["terminate_date"] = origin[2]

        return result
