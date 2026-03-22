
from error.error import Error
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from log.logger import logger

def check_request_param(req, request_params=[], is_or=False):

    for param in request_params:

        if is_or:
            if param in req:
                return None
        else:
            if param not in req:
                logger.error("request param %s no found" % param)
                return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                             ErrorMsg.ERR_MSG_NO_RESOURCE_SPECIFIED)
    
    if is_or:
        logger.error("request %s param %s no found" % (req, request_params))
        return Error(ErrorCodes.INVALID_REQUEST_FORMAT,
                     ErrorMsg.ERR_MSG_NO_RESOURCE_SPECIFIED)
    return None
