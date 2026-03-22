import base64
from log.logger import logger
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from common import (
    return_success, return_error
)
from common import is_admin_user, is_global_admin_user
import context
from resource_control.user.system_config import set_system_config


def handle_update_license(req):
    if not is_global_admin_user(req['sender']):
        logger.error("only global admin can modify system config.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))
    lic_str = license_str = req.get("license_str", "")
    if not license_str:
        logger.error("lincese is none")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_MISSING_PARAMETER, "license_str"))

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

    logger.info("license_str: [%s]" % license_str)
    origin = str.split(license_str, ";")
    if not origin or len(origin)!=3:
        logger.error("invalid license")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_MISSING_PARAMETER, "license_str"))

    ret = set_system_config("license_str", lic_str)
    if isinstance(ret, Error):
        logger.error("update license error.")
        return return_error(req, ret)

    return return_success(req, {})

def handle_describe_license(req):
    if not is_admin_user(req['sender']):
        logger.error("only admin can modify system config.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED, 
                                       ErrorMsg.ERR_MSG_SUPER_USER_ONLY))
    ctx = context.instance()
    lic = ctx.pgm.load_license_info()
    if not lic:
        logger.error("update license error")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_CODE_MSG_UPDATE_LICENSE_ERROR))
    ctx.license = lic
    return return_success(req, {"license": lic})
