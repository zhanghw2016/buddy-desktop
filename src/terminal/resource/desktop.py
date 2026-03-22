'''
Created on 2018-5-16

@author: yunify
'''
import context
from db.constants import TB_DESKTOP,TB_TERMINAL_MANAGEMENT
from log.logger import logger

def get_terminal_mac(terminal_id):
    ''' get terminal_mac by terminal_id '''
    ctx = context.instance()
    columns = ["terminal_mac"]
    # get terminal_mac from db
    try:
        result = ctx.pg.get(TB_TERMINAL_MANAGEMENT,
                            terminal_id,
                            columns)
        if not result:
            logger.error("get terminal id [%s] terminal_mac failed" % terminal_id)
            return None
    except Exception,e:
        logger.error("get desktop hostname with Exception:%s" % e)
        return None

    return result['terminal_mac']

def get_desktop_hostname(desktop_id):
    ''' get desktop hostname by desktop_id '''
    ctx = context.instance()  
    columns = ["hostname"]
    # get hostname from db
    try:
        result = ctx.pg.get(TB_DESKTOP, 
                            desktop_id, 
                            columns)
        if not result:
            logger.error("get desktop id [%s] hostname failed" % desktop_id)
            return None
    except Exception,e:
        logger.error("get desktop hostname with Exception:%s" % e)
        return None

    return result['hostname'].upper()

def get_db_desktop_hostname(desktop_id):
    ''' get desktop hostname by desktop_id '''
    ctx = context.instance()  
    columns = ["hostname"]
    # get hostname from db
    try:
        result = ctx.pg.get(TB_DESKTOP, 
                            desktop_id, 
                            columns)
        if not result:
            logger.error("get desktop id [%s] hostname failed" % desktop_id)
            return None
    except Exception,e:
        logger.error("get desktop hostname with Exception:%s" % e)
        return None

    return result['hostname']

def get_desktop_id(hostname):
    ''' get desktop id by hostname '''
    ctx = context.instance()  
    columns = ["desktop_id", "hostname"]
    # get desktop_id from db
    try:
        result = ctx.pg.base_get(TB_DESKTOP, {}, columns)
        if not result:
            logger.error("get desktop [%s] failed" % hostname)
            return None
    except Exception,e:
        logger.error("get desktop id with Exception:%s" % e)
        return None
    
    for item in result:
        for key in item.keys():
            if key == "hostname" and item[key].upper() == hostname:
                desktop_id = item["desktop_id"]
                return desktop_id
                
    return None

def get_desktop_group_type(desktop_id):
    ''' get desktop group type by desktop_id '''
    ctx = context.instance()
    columns = ["desktop_group_type"]
    # get owner from db
    try:
        result = ctx.pg.get(TB_DESKTOP,
                            desktop_id,
                            columns)
        if not result or len(result) == 0:
            logger.error("get group_type by desktop_id:[%s] failed" % desktop_id)
            return None
    except Exception,e:
        logger.error("get desktop group_type with Exception:%s" % e)
        return None

    return result['desktop_group_type']

def get_desktop_dn(desktop_id):
    ''' get desktop dn in domain by desktop_id '''
    ctx = context.instance()
    columns = ["desktop_dn", "in_domain"]
    # get owner from db
    try:
        result = ctx.pg.get(TB_DESKTOP,
                            desktop_id,
                            columns)
        if not result or len(result) == 0:
            logger.error("get desktop_dn by desktop_id:[%s] failed" % desktop_id)
            return None
        if result["in_domain"] != 1 or result["desktop_dn"] is None or len(result["desktop_dn"]) == 0:
            logger.error("get desktop_dn error, [%s]" % result)
            return None
    except Exception,e:
        logger.error("get desktop desktop_dn with Exception:%s" % e)
        return None

    return result["desktop_dn"]
