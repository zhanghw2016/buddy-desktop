from log.logger import logger
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error

def check_desktop_group_gpus(sender, desktop_count, gpu, gpu_class):
    
    ctx = context.instance()

    gpus = ctx.res.resource_describe_gpus(sender["zone"], gpu_class)
    if not gpus:
        logger.error("no enough gpu count to create desktop group")
        return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_NO_ENOUGH_GPU_COUNT, 0)

    gpu_count = desktop_count * gpu
    if gpu_count > len(gpus):
        logger.error("no enough gpu count to create desktop group")
        return Error(ErrorCodes.PERMISSION_DENIED,
                         ErrorMsg.ERR_MSG_NO_ENOUGH_GPU_COUNT, len(gpus))

    return None
