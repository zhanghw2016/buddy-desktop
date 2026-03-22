'''
Created on 2018-5-16

@author: yunify
'''
import context
from db.constants import TB_GUEST
from log.logger import logger


def describe_guest(desktop_id):
    ''' get guest info by desktop_id '''
    ctx = context.instance()

    try:
        result = ctx.pg.get(TB_GUEST,
                            desktop_id)
        if not result or len(result) == 0:
            logger.error("describe guest by desktop_id:[%s] failed" % desktop_id)
            return None
        return result
    except Exception,e:
        logger.error("describe guest with Exception:%s" % e)
        return None


def update_guest(desktop_id, hostname, conditions):
    ''' update guest by desktop_id and hostname'''
    ctx = context.instance()
    # get owner from db
    try:
        if describe_guest(desktop_id) is None:
            conditions.update({"desktop_id": desktop_id})
            conditions.update({"hostname": hostname})
            result = ctx.pg.insert(TB_GUEST, conditions)
            if result is None:
                return False

        result = ctx.pg.update(TB_GUEST,
                               desktop_id,
                               conditions)
        if not result:
            logger.error("update guest by desktop_id:[%s] failed" % desktop_id)
            return False
        return True
    except Exception,e:
        logger.error("pdate guest with Exception:%s" % e)
        return True