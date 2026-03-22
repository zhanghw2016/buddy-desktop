'''
Created on 2014-5-28

@author: yunify
'''

import random
from psycopg2.pool import ThreadedConnectionPool
from log.logger import logger

class PGAuth():

    def __init__(self, host, user, password=None, minconn=1, maxconn=15, port=None):
        self.host = host
        self.port = "5432" if port == None else port
        self.user = user
        self.password = password if password is not None else None
        self.minconn = minconn
        self.maxconn = maxconn

class PGPool():
    ''' a PG pool object for one database '''
    
    def __init__(self, db, auth):
        self.pool = None   
        self.db = db
        self.auth = auth
        random.shuffle(self.auth.host)
        self.hindex = -1
    
    def open(self):
        ''' open connection pool for a db '''
        try:
            self.hindex = (self.hindex + 1) % len(self.auth.host)
            self.host = self.auth.host[self.hindex]
                
            # creating pool for connection to db server 
            self.pool = ThreadedConnectionPool(minconn=self.auth.minconn,
                                               maxconn=self.auth.maxconn,
                                               database=self.db,
                                               user=self.auth.user,
                                               password=self.auth.password,
                                               host=self.host,
                                               port=self.auth.port)
            
            logger.info("open db [%s] [%s] ok: [%s] [%s]" % (self.auth.host, self.db, self.auth.minconn, self.auth.maxconn)) 
        except Exception, e:
            logger.error("open db [%s] [%s] failed: %s" % (self.auth.host, self.db, e))
            return -1
        
        return 0
    
    def close(self):
        try:
            self.pool.closeall()
        except Exception, e:
            logger.error("closing pool failed: %s" % (e))
            return False
        return True 
    
    def reopen(self):
        self.close()
        self.open() 
    
    def getconn(self):
        return self.pool.getconn()
    
    def putconn(self, conn, close=False):
        return self.pool.putconn(conn, close=close)
