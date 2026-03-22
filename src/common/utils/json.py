# coding=utf-8

'''
Created on 2012-5-3

@author: yunify
'''

import simplejson as jsmod
from log.logger import logger
from datetime import date, datetime
from db.data_types import RangeType, SearchType, SearchWordType, TimeStampType

def __default(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, RangeType) or isinstance(obj, SearchType) or isinstance(obj, SearchWordType) or isinstance(obj, TimeStampType):
        return str(obj)
    else:
        raise TypeError('%r is not JSON serializable' % obj)

def json_dump(obj, indent=None):
    ''' dump an object to json string, only basic python types are supported

    @return json string or None if failed
    '''
    try:
        jstr = jsmod.dumps(obj, separators=(',', ':'), default=__default, indent=indent)
    except Exception, e:
        jstr = None
        logger.error("dump json failed: %s" % e)
    return jstr

def json_load(json, suppress_warning=False):
    ''' load from json string and create a new python object

    @return object or None if failed
    '''
    if not json:
        return None

    try:
        # always return unicode
        obj = jsmod.loads(json, encoding='utf-8')
    except Exception, e:
        obj = None
        if not suppress_warning:
            logger.error("load json failed: %s, %s" % (e, json))
    return obj

__all__ = [json_dump, json_load]
