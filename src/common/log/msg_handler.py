import time
import logging
from utils.thread_local import get_msg_id

DEFAULT_MSG_PRE = 'j-'
DEFAULT_CAPACITY = 128
DEFAULT_TTL = 3600 * 24 * 7 * 2  # two weeks
FLUSH_INTERVAL = 60 * 5  # five mins

# for app cluster health checking
APP_HEALTH_CHECK_MSG_PRE = 'ahcj-'
APP_HEALTH_CHECK_TTL = 3600         # one hour

# for app cluster monitoring
APP_MONITOR_MSG_PRE = 'amj-'
APP_MONITOR_TTL = 900               # 15 minutes


class MsgLogHandler(logging.Handler):
    """
    A handler class which buffers logging records in memory, periodically
    flushing them to cassandra.
    Flushing occurs whenever the buffer is FULL or after INTERVAL TIME.
    Only emit the record which level > INFO with special msg_pre
    """
    def __init__(self, logger,
                 cassandra, msg_pre=DEFAULT_MSG_PRE,
                 capacity=DEFAULT_CAPACITY,
                 ttl=DEFAULT_TTL,
                 flush_interval=FLUSH_INTERVAL,
                 level=logging.WARNING):
        """
        Initialize the handler with the cassandra, msg_ore, buffer size

        cass = (cassandra_keyspance, column_family)
        """
        logging.Handler.__init__(self)
        self.logger = logger
        self.cass_keyspace = cassandra[0]
        self.cass_cf = cassandra[1]
        self.msg_pre = msg_pre
        self.capacity = capacity
        self.buffer = []
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.ttl = ttl
        self.flush_interval = flush_interval
        self.last_flush = time.time()
        self.level = level

    def shouldAppend(self, record):
        """
        Should the handler emit this record?
        """
        msg_id = get_msg_id() or ""
        record.origin_msg_id = msg_id
        if record.levelno >= self.level and msg_id and msg_id.startswith(self.msg_pre):
            return True
        return False

    def shouldFlush(self, record):
        """
        Should the handler flush its buffer?

        Returns true if the buffer is up to capacity. This method can be
        overridden to implement custom flushing strategies.
        """
        if time.time() - self.last_flush > self.flush_interval:
            return True
        return (len(self.buffer) >= self.capacity)

    def emit(self, record):
        """
        Append the record. If shouldFlush() tells us to, call flush() to process
        the buffer.
        """
        if self.shouldAppend(record):
            self.buffer.append(record)

        if self.shouldFlush(record):
            self.flush()

    def flush(self):
        """
        For a MemoryHandler, flushing means just sending the buffered
        records to the target which means cassandra here.
        """
        self.acquire()
        # copy buffer out and release the lock
        bf = self.buffer
        self.buffer = []
        self.last_flush = time.time()
        self.release()

        try:
            addHandler = False
            if self in self.logger.handlers:
                # remove self from dispatch_handler, because cassandra print log casuse
                # recursion depth exceeded
                self.logger.removeHandler(self)
                addHandler = True

            self.submit_to_cassandra(bf)

            if addHandler:
                self.logger.addHandler(self)
        finally:
            pass

    def get_rows(self, records):
        data_rows = {}
        for record in records:
            msg_id = record.origin_msg_id
            message = self.formatter.format(record)
            ct = str(int(float(record.created) * 1000 * 1000))  # keep microseconds
            if msg_id not in data_rows:
                data_rows[msg_id] = {}
            data_rows[msg_id][ct] = message
        return data_rows

    def submit_to_cassandra(self, records):
        data_rows = self.get_rows(records)
        if data_rows and len(data_rows) > 0:
            self.cass_keyspace.batch_insert(self.cass_cf, data_rows, ttl=self.ttl)

    def close(self):
        """
        Flush and close this handler
        """
        try:
            self.flush()
        finally:
            logging.Handler.close(self)


def add_msg_handler(logger, cassandra, msg_pre=DEFAULT_MSG_PRE,
                    capacity=DEFAULT_CAPACITY, ttl=DEFAULT_TTL,
                    flush_interval=FLUSH_INTERVAL,
                    level=logging.WARNING):
    """
        cassandra = (cassandra_keyspance, column_family)
    """
    handler = MsgLogHandler(logger=logger,
                            cassandra=cassandra, msg_pre=msg_pre,
                            capacity=capacity, ttl=ttl, flush_interval=flush_interval,
                            level=level)
    logger.addHandler(handler)


if __name__ == '__main__':
    # Test
    from log.logger_name import set_logger_name
    set_logger_name("msg_test")
    from log.logger import logger, app_developer_logger
    from utils.thread_local import set_msg_id

    # start test
    set_msg_id('j-test')
    app_developer_logger.debug("j-test debug, should ignore")
    app_developer_logger.info("j-test info, should ignore")
    app_developer_logger.warn("j-test warn")
    app_developer_logger.error("j-test error")
    app_developer_logger.critical("j-test critiacl")

    set_msg_id('h-test')
    app_developer_logger.debug("h-test debug, should ignore")
    app_developer_logger.info("h-test info, should ignore")
    app_developer_logger.warn("h-test warn should ignore")
    app_developer_logger.error("h-test error, should ignore")
    app_developer_logger.critical("h-test critiacl, should ignore")

    for x in range(5):
        time.sleep(1)
        set_msg_id('j-test%s' % x)
        logger.debug("j-test%s debug, should ignore", x)
        logger.info("j-test%s info, should ignore", x)
        logger.error("j-test%s error", x)
        logger.critical("j-test%s critiacl", x)

        time.sleep(1)
        app_developer_logger.debug("j-test%s developer debug, should ignore", x)
        app_developer_logger.info("j-test%s developer info, should ignore", x)
        app_developer_logger.error("j-test%s developer error", x)
        app_developer_logger.critical("j-test%s developer critiacl", x)
