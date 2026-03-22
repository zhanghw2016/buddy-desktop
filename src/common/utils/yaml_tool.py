# coding=utf-8

'''
Created on 2012-5-3

@author: yunify
'''

from yaml import load, dump
from yaml import Loader, Dumper
from log.logger import logger

def yaml_dump(obj):
    ''' dump an object to yaml string, only basic python types are supported 
    
    @return yaml string or None if failed
    ''' 
    try:
        output = dump(obj, Dumper=Dumper)
    except Exception, e:
        output = None
        logger.error("dump yaml failed: %s" % e)       
    return output

def yaml_load(stream):
    ''' load from yaml stream and create a new python object 
    
    @return object or None if failed
    ''' 
    try:
        obj = load(stream, Loader=Loader)
    except Exception, e:
        obj = None
        logger.error("load yaml failed: %s" % e)       
    return obj

__all__ = [yaml_dump, yaml_load]
                
    
    