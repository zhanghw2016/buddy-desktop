'''
Created on 2012-9-24

@author: yunify
'''

import threading
import traceback
from contextlib import contextmanager
from log.logger import logger
from constants import (
    TOPIC_TYPE_JOB,
    TOPIC_TYPE_MONITOR,
    TOPIC_TYPE_EVENT,
    TOPIC_TYPE_LIST,
    TOPIC_JOB_SUB_TYPE_LIST,
    TOPIC_MONITOR_SUB_TYPE_LIST,
    TOPIC_EVENT_SUB_TYPE_LIST,
    ALL_SUBSCRIBERS
)
import context

class Subscriber():
    def __init__(self, user_id, session_id, zone_id, uuid4, websocket_handler):
        self._user_id = user_id
        self._session_id = session_id
        self._zone_id = zone_id
        self._uuid4 = uuid4
        self._websocket_handler = websocket_handler

    @property
    def UUID4(self):
        return self._uuid4

    @property
    def user_id(self):
        return self._user_id

    @property
    def session_id(self):
        return self._session_id

    @property
    def zone_id(self):
        return self._zone_id

    @property
    def websocket_handler(self):
        return self._websocket_handler

class SubscriberManager():
    def __init__(self):
        self._subscribers = {}
        self.lock = threading.RLock()

    @property
    def subscribers(self):
        return self._subscribers

    def add_subscriber(self, uuid, subscriber):
        with self._lock():
            if uuid not in self._subscribers.keys():
                self._subscribers.update({uuid: subscriber})

    def remove_subscriber(self, uuid):
        with self._lock():
            if uuid in self._subscribers.keys():
                del self._subscribers[uuid]

    @contextmanager
    def _lock(self):
        self.lock.acquire()
        try:
            yield
        except Exception:
            logger.error("yield exits with exception: %s" % traceback.format_exc())
        self.lock.release()


class Topic():
    def __init__(self, topic_type, topic_sub_type):
        self._topic_type = topic_type
        self._topic_sub_type = topic_sub_type
        self._subscribers = []

    @property
    def topic_type(self):
        return self._topic_type

    @property
    def topic_sub_type(self):
        return self._topic_sub_type

    @property
    def subscribers(self):
        return self._subscribers

    def topic(self):
        return self._topic_type + self.topic_sub_type

class TopicManager():
    ''' manage topic and subscribers '''
    def __init__(self):
        self.lock = threading.RLock()
        self.topics = {}
        for topic_type in TOPIC_TYPE_LIST:
            if topic_type == TOPIC_TYPE_JOB:
                for topic_sub_type in TOPIC_JOB_SUB_TYPE_LIST:
                    self.topics.update({topic_type + topic_sub_type: Topic(topic_type, topic_sub_type)})
            if topic_type == TOPIC_TYPE_MONITOR:
                for topic_sub_type in TOPIC_MONITOR_SUB_TYPE_LIST:
                    self.topics.update({topic_type + topic_sub_type: Topic(topic_type, topic_sub_type)})
            if topic_type == TOPIC_TYPE_EVENT:
                for topic_sub_type in TOPIC_EVENT_SUB_TYPE_LIST:
                    self.topics.update({topic_type + topic_sub_type: Topic(topic_type, topic_sub_type)})

    def subscribe(self, subscriber, topic_dict={}):
        if topic_dict == None or len(topic_dict) == 0:
            logger.error("parameter error topic_dict:[%s]" % topic_dict);
            return False
        if subscriber == None:
            logger.error("parameter subscriber is None");
            return False
        ctx = context.instance()
        if subscriber not in ctx.subscriber_mgr.subscribers.keys():
            return False
        else:
            subscriber = ctx.subscriber_mgr.subscribers[subscriber]

        for topic_type in topic_dict.keys():
            if topic_type not in TOPIC_TYPE_LIST:
                logger.error("parameter error topic_types:[%s] " % (topic_dict.keys()));
                return False

        with self._lock():
            for topic_type in topic_dict.keys():
                topic_sub_types = topic_dict[topic_type]
                if topic_type == TOPIC_TYPE_JOB:
                    for topic_sub_type in topic_sub_types:
                        if topic_sub_type not in TOPIC_JOB_SUB_TYPE_LIST:
                            logger.error("parameter error topic_sub_types:[%s] " % (topic_sub_types));
                            return False
                    for topic_sub_type in topic_sub_types:
                        if subscriber not in self.topics[topic_type+topic_sub_type].subscribers:
                            self.topics[topic_type+topic_sub_type].subscribers.append(subscriber)
                if topic_type == TOPIC_TYPE_MONITOR:
                    for topic_sub_type in topic_sub_types:
                        if topic_sub_type not in TOPIC_MONITOR_SUB_TYPE_LIST:
                            logger.error("parameter error topic_sub_types:[%s] " % (topic_sub_types));
                            return False
                    for topic_sub_type in topic_sub_types:
                        if subscriber not in self.topics[topic_type+topic_sub_type].subscribers:
                            self.topics[topic_type+topic_sub_type].subscribers.append(subscriber)
                if topic_type == TOPIC_TYPE_EVENT:
                    for topic_sub_type in topic_sub_types:
                        if topic_sub_type not in TOPIC_EVENT_SUB_TYPE_LIST:
                            logger.error("parameter error topic_sub_types:[%s] " % (topic_sub_types));
                            return False
                    for topic_sub_type in topic_sub_types:
                        if subscriber not in self.topics[topic_type+topic_sub_type].subscribers:
                            self.topics[topic_type+topic_sub_type].subscribers.append(subscriber)

        return True

    def unsubscribe(self, subscriber, topic_dict={}):
        if topic_dict == None or len(topic_dict) == 0:
            logger.error("parameter error topic_dict:[%s]" % topic_dict);
            return False
        if subscriber == None:
            logger.error("parameter subscriber is None");
            return False
        ctx = context.instance()
        if subscriber not in ctx.subscriber_mgr.subscribers.keys():
            return False
        else:
            subscriber = ctx.subscriber_mgr.subscribers[subscriber]

        for topic_type in topic_dict.keys():
            if topic_type not in TOPIC_TYPE_LIST:
                logger.error("parameter error topic_types:[%s] " % (topic_dict.keys()));
                return False

        with self._lock():
            for topic_type in topic_dict.keys():
                topic_sub_types = topic_dict[topic_type]
                if topic_type == TOPIC_TYPE_JOB:
                    for topic_sub_type in topic_sub_types:
                        if topic_sub_type not in TOPIC_JOB_SUB_TYPE_LIST:
                            logger.error("parameter error topic_sub_types:[%s] " % (topic_sub_types));
                            return False
                    for topic_sub_type in topic_sub_types:
                        if subscriber in self.topics[topic_type+topic_sub_type].subscribers:
                            self.topics[topic_type+topic_sub_type].subscribers.remove(subscriber)
                if topic_type == TOPIC_TYPE_MONITOR:
                    for topic_sub_type in topic_sub_types:
                        if topic_sub_type not in TOPIC_MONITOR_SUB_TYPE_LIST:
                            logger.error("parameter error topic_sub_types:[%s] " % (topic_sub_types));
                            return False
                    for topic_sub_type in topic_sub_types:
                        if subscriber in self.topics[topic_type+topic_sub_type].subscribers:
                            self.topics[topic_type+topic_sub_type].subscribers.remove(subscriber)
                if topic_type == TOPIC_TYPE_EVENT:
                    for topic_sub_type in topic_sub_types:
                        if topic_sub_type not in TOPIC_EVENT_SUB_TYPE_LIST:
                            logger.error("parameter error topic_sub_types:[%s] " % (topic_sub_types));
                            return False
                    for topic_sub_type in topic_sub_types:
                        if subscriber in self.topics[topic_type+topic_sub_type].subscribers:
                            self.topics[topic_type+topic_sub_type].subscribers.remove(subscriber)

        return True

    def publish(self, user_id, topic_type, topic_sub_type, data):

        with self._lock():
            subscribers = self.topics[topic_type+topic_sub_type].subscribers
            for subscriber in subscribers:
                if user_id==subscriber.user_id or user_id==ALL_SUBSCRIBERS:
                    if subscriber.websocket_handler is not None:
                        subscriber.websocket_handler.send_response(data)
        return

    def get_topics(self):
        return self.topics

    @contextmanager
    def _lock(self):
        self.lock.acquire()
        try:
            yield
        except Exception:
            logger.error("yield exits with exception: %s" % traceback.format_exc())
        self.lock.release()
