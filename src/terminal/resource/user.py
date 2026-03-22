'''
Created on 2018-7-24

@author: yunify
'''
import context
from db.constants import TB_DESKTOP_USER
from log.logger import logger

def get_user_source(user_id):
    ''' get user source by user_id '''
    ctx = context.instance()
    columns = ["source"]
    # get hostname from db
    try:
        result = ctx.pg.get(TB_DESKTOP_USER,
                            user_id,
                            columns)
        if not result:
            logger.error("get user source by user_id:[%s] failed" % user_id)
            return None
    except Exception,e:
        logger.error("get user source with Exception:%s" % e)
        return None

    return result['source']