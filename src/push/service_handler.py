'''
Created on 2012-5-2

@author: yunify
'''
from utils.json import json_load
from log.logger import logger
from constants import REQ_PUBLISH,REQ_SUBSCRIBE,REQ_UNSUBSCRIBE
import context


def handle_subscribe(req):
    ''' subscribe a topic '''
    subscriber = req.get('subscriber')
    topic_dict = req.get('topic_dict')

    if subscriber == None or topic_dict == None:
        logger.error("request paramters [%s] is error" % req)
        return None
    
    ctx = context.instance()
    ctx.topic_mgr.subscribe(subscriber, topic_dict) 
    return 0

def handle_unsubscribe(req):
    ''' unsubscribes a topic '''
    subscriber = req.get('subscriber')
    topic_dict = req.get('topic_dict')

    if subscriber == None or topic_dict == None:
        logger.error("request paramters [%s] is error" % req)
        return None
    
    ctx = context.instance()
    ctx.topic_mgr.unsubscribe(subscriber, topic_dict) 
    return 0

def handle_publish(req):
    ''' publish data to web client '''

    subscriber = req.get('subscriber')
    topic_type = req.get('topic_type')
    topic_sub_type = req.get('topic_sub_type')
    data = req.get('data')
    
    if subscriber == None or topic_type == None or topic_sub_type == None or data == None:
        logger.error("request parameters [%s] is error" % req)
        return None

    ctx = context.instance()
    ctx.topic_mgr.publish(subscriber, topic_type, topic_sub_type, data)
    return 0

class ServiceHandler(object):
    ''' peer service handler '''
    
    def __init__(self):
        self.handle_map = {
            REQ_SUBSCRIBE: handle_subscribe,
            REQ_UNSUBSCRIBE:handle_unsubscribe,
            REQ_PUBLISH : handle_publish
        }

    def handle(self, req_msg, title, **kargs):
        ''' no return'''
        
        # decode to request object
        req = json_load(req_msg)
        if req == None:
            logger.error("invalid request: %s" % req_msg)
            return
        
        logger.info(" request received: [%s]" % req)
        
        if "action" not in req:
            logger.error("invalid request: %s" % req_msg)
            return

        # get message handler 
        action = req["action"] 
        if action not in self.handle_map:   
            logger.error("invalid request: %s" % req_msg)
            return
        
        # handle it  
        self.handle_map[action](req)
