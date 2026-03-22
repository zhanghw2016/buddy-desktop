import context
from log.logger import logger

def check_terminals(terminal_ids=None):

    ctx = context.instance()

    terminals = ctx.pgm.get_terminals(terminal_ids=terminal_ids)
    if not terminals:
        logger.error("describe terminal %s no found in terminals" % (terminal_ids))
        return -1

    return terminals

