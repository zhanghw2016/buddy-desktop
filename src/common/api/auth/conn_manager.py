
import codecs

from threading import RLock
import time

import ldap

from log.logger import logger
import re
import six

CONN_STEP_SIZE = 32

_utf8_encoder = codecs.getencoder('utf-8')
from ldap.ldapobject import ReconnectLDAPObject

def utf8_encode(value):
    """Encode a basestring to UTF-8.

    If the string is unicode encode it to UTF-8, if the string is
    str then assume it's already encoded. Otherwise raise a TypeError.

    :param value: A basestring
    :returns: UTF-8 encoded version of value
    :raises TypeError: If value is not basestring
    """
    if isinstance(value, six.text_type):
        return _utf8_encoder(value)[0]
    elif isinstance(value, six.binary_type):
        return value
    else:
        raise TypeError("bytes or Unicode expected, got %s"
                        % type(value).__name__)

class MaxConnectionReachedError(Exception):
    pass


class BackendError(Exception):
    def __init__(self, msg, backend):
        self.bacend = backend
        Exception.__init__(self, msg)

class LDAPConnector(ReconnectLDAPObject):

    def __init__(self, *args, **kw):

        ReconnectLDAPObject.__init__(self, *args, **kw)
        self.connected = False
        self.access_id = ''
        self.access_key = ''
        self._connection_time = None

    def get_lifetime(self):

        if self._connection_time is None:
            return 0
        return time.time() - self._connection_time

    def cm_bind(self, access_id='', access_key=''):

        ldap_prot = self._uri.split("://")[0]
        if ldap_prot == "ldaps":
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            
        self.set_option(ldap.OPT_REFERRALS, 0)
        res = ReconnectLDAPObject.bind_s(self, access_id, access_key)
        self.connected = True
        self.access_id = access_id
        self.access_key = access_key

        if self._connection_time is None:
            self._connection_time = time.time()

        return res

    def cm_unbind(self):
        try:
            return ReconnectLDAPObject.unbind_ext_s(self)
        finally:
            self.connected = False
            self.access_id = None
            self.access_key = None

class ConnectionManager(object):

    def __init__(self, uri, access_id, access_key, size=32, retry_max=3,
                 retry_delay=.1, use_tls=False, timeout=-1, use_pool=True,
                 max_lifetime=600):

        self._pool = []
        self.size = size
        self.retry_max = retry_max
        self.retry_delay = retry_delay
        self.uri = uri
        self.access_id = access_id
        self.access_key = access_key
        self._pool_lock = RLock()
        self.use_tls = use_tls
        self.timeout = timeout
        self.connector = LDAPConnector
        self.use_pool = use_pool
        self.max_lifetime = max_lifetime
        self.max_size = 128
    
    def __len__(self):
        return len(self._pool)

    def _match(self, access_id, access_key):

        if access_key is not None:
            access_key = utf8_encode(access_key)

        if access_id is not None:
            access_id = utf8_encode(access_id)

        with self._pool_lock:
            inactives = []

            for conn in reversed(self._pool):
                # already in usage
                if conn.active:
                    continue

                # let's check the lifetime
                if conn.get_lifetime() > self.max_lifetime:
                    # this connector has lived for too long,
                    # we want to unbind it and remove it from the pool
                    try:
                        self._unbind(conn)
                    except Exception:
                        logger.debug('Failure attempting to unbind after '
                                  'timeout; should be harmless', exc_info=True)

                    self._pool.remove(conn)
                    continue

                # we found a connector for this bind
                if conn.access_id == access_id and conn.access_key == access_key:
                    conn.active = True
                    return conn

                inactives.append(conn)

            # no connector was available, let's rebind the latest inactive one
            if len(inactives) > 0:
                for conn in inactives:
                    try:
                        self._bind(conn, access_id, access_key)
                        return conn
                    except ldap.INVALID_CREDENTIALS as error:
                        
                        self._pool.remove(conn)
                        exc = error
                        logger.error('Invalid credentials. Cancelling retry',
                                  exc_info=True)
                        raise exc

                    except Exception:
                        logger.debug('Removing connection from pool after '
                                  'failure to rebind', exc_info=True)
                        self._pool.remove(conn)

                return None

        # There are no connector that match
        return None

    def _bind(self, conn, access_id, access_key):
        # let's bind
        if self.use_tls:
            try:
                conn.start_tls_s()
            except Exception:
                raise BackendError('Could not activate TLS on established '
                                   'connection with %s' % self.uri,
                                   backend=conn)

        if access_id is not None:
            conn.cm_bind(access_id, access_key)

        conn.active = True
    
    def _unbind(self, conn):
        
        conn.cm_unbind()
        conn.active = False

    def _create_connector(self, access_id, access_key):

        connected = False
        if access_key is not None:
            access_key = utf8_encode(access_key)
        if access_id is not None:
            access_key = utf8_encode(access_key)

        # If multiple server URIs have been provided, loop through
        # each one in turn in case of connection failures (server down,
        # timeout, etc.).  URIs can be delimited by either commas or
        # whitespace.
        for server in re.split(r'[\s,]+', self.uri):
            tries = 0
            exc = None
            conn = None

            # trying retry_max times in a row with a fresh connector
            while tries < self.retry_max and not connected:
                try:
                    logger.debug('Attempting to create a new connector '
                              'to %s (attempt %d)', server, tries + 1)
                    
                    conn = self.connector(server, retry_max=self.retry_max,
                                              retry_delay=self.retry_delay)

                    self._bind(conn, access_id, access_key)

                    connected = True
                except ldap.INVALID_CREDENTIALS as error:
                    # Treat this as a hard failure instead of retrying to
                    # avoid locking out the LDAP account due to successive
                    # failed bind attempts.  We also don't want to try
                    # connecting to additional servers if multiple URIs were
                    # provide, as failed bind attempts may be replicated
                    # across multiple LDAP servers.
                    exc = error
                    logger.error('Invalid credentials. Cancelling retry',
                              exc_info=True)
                    raise exc
                except ldap.LDAPError as error:
                    exc = error
                    tries += 1
                    if tries < self.retry_max:
                        logger.info('Failure attempting to create and bind '
                                 'connector; will retry after %r seconds',
                                 self.retry_delay, exc_info=True)
                        time.sleep(self.retry_delay)
                    else:
                        logger.error('Failure attempting to create and bind '
                                  'connector', exc_info=True)

            # We successfully connected to one of the servers, so
            # we can just return the connection and stop processing
            # any additional URIs.
            if connected:
                return conn

        # We failed to connect to any of the servers,
        # so raise an appropriate exception.
        if not connected:
            if isinstance(exc, (ldap.NO_SUCH_OBJECT,
                                ldap.SERVER_DOWN,
                                ldap.TIMEOUT)):
                raise exc

        # that's something else
        raise BackendError(str(exc), backend=conn)
    
    def try_release_connection(self):

        if not self.use_pool:
            return None
        
        with self._pool_lock:
            for conn in reversed(self._pool):
                
                if conn.active:
                    continue
                logger.info("try release conn....[%s][%s]" % (conn.access_id, conn.access_key))
                # unconnected connector, let's drop it
                self._pool.remove(conn)
                # let's try to unbind it
                conn.cm_unbind()
        
        if len(self._pool) >= self.size:
            self.size = self.size + CONN_STEP_SIZE
            if self.size >= self.max_size:
                self.size = self.max_size
                return False
       
        return True
    
    def _get_connection(self, access_id=None, access_key=None):

        if access_id is None:
            access_id = self.access_id
        if access_key is None:
            access_key = self.access_key

        if self.use_pool:
            # let's try to recycle an existing one
            conn = self._match(access_id, access_key)
            if conn is not None:
                return conn
            
            # the pool is full
            if len(self._pool) >= self.size:
                ret = self.try_release_connection()
                if not ret:
                    logger.error("exceed max ldap connection")
                    raise MaxConnectionReachedError(self.uri)

        # we need to create a new connector
        conn = self._create_connector(access_id, access_key)

        # adding it to the pool
        if self.use_pool:
            with self._pool_lock:
                self._pool.append(conn)
        else:
            # with no pool, the connector is always active
            conn.active = True
        
        return conn

    def release_connection(self, connection, is_unbind=False):
        
        if self.use_pool:
            with self._pool_lock:
                if not connection.connected or is_unbind:
                    # unconnected connector, let's drop it
                    self._pool.remove(connection)
                else:
                    # can be reused - let's mark is as not active
                    connection.active = False

                    # done.
                    return
        else:
            connection.active = False

        # let's try to unbind it
        try:
            connection.cm_unbind()
        except ldap.LDAPError:
            # avoid error on invalid state
            logger.debug('Failure attempting to unbind on release; '
                      'should be harmless', exc_info=True)

    def connection(self, access_id=None, access_key=None):

        tries = 0
        conn = None
        while tries < self.retry_max:
            try:
                conn = self._get_connection(access_id, access_key)
            except MaxConnectionReachedError:
                tries += 1
                time.sleep(0.1)

                # removing the first inactive connector going backward
                with self._pool_lock:
                    reversed_list = reversed(list(enumerate(self._pool)))
                    for index, conn_ in reversed_list:
                        if not conn_.active:
                            self._pool.pop(index)
                            break
            else:
                break

        if conn is None:
            raise MaxConnectionReachedError(self.uri)

        return conn

