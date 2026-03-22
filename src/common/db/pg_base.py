'''
Created on 2012-9-24

@author: yunify
'''
import logging
import random
import time
import traceback
from psycopg2.extras import RealDictCursor
from psycopg2 import ProgrammingError, IntegrityError, DataError
from log.logger import logger
from contextlib import contextmanager
from db.constants import DEFAULT_LIMIT, MAX_LIMIT, INDEXED_COLUMNS, SEARCH_COLUMNS, \
                         MAX_OFFSET
from db.data_types import (
    SearchType,
    SearchWordType,
    TimeStampType,
    RangeType,
    NotType,
    AndMaskType,
    OrMaskType,
    RegExpType,
)
from db.pg_pool import PGPool
from utils.thread_local import is_pg_proxied

class PGBase(object):
    ''' A thread-safe postgreSQL basic client wrapper for one database 
        Note:
            - support proxy mode if slave pool is specified
    '''
    
    # max retry time when get available connection from pool 
    # if get failed, it will wait for a random time before next get.
    # Notice: the maximum sleep time will be 0.1 * (2 ** MAX_RETRY_TIME)
    #         that is: 5 -> 3.2 secs, 6 -> 6.4 secs
    MAX_RETRY_TIME = 2
    
    def __init__(self):
        self.db = None
        self.pool_m = None  # master pool
        self.pool_s = None  # slave pool
    
    def open(self, db, auth_m, auth_s=None):
        pool_m = PGPool(db, auth_m)
        if 0 != pool_m.open():
            pool_m.close()
            logger.error("open master db [%s] [%s] failed" % (auth_m.host, auth_m.database))
            return -1
        
        pool_s = None
        if auth_s:
            pool_s = PGPool(db, auth_s)
            if 0 != pool_s.open():
                pool_m.close()
                pool_s.close()
                logger.error("open slave db [%s] [%s] failed" % (auth_s.host, auth_s.database))
                return -1

        # close original first
        self.close()
        
        # switch
        self.db = db
        self.pool_m = pool_m
        self.pool_s = pool_s
        return 0
    
    def close(self):
        ''' close all connections in the poll.
        @return True if succeeded and False if failed.
        '''
        try:
            self.db = None
            
            if self.pool_m:
                self.pool_m.closeall()
                self.pool_m = None
                
            if self.pool_s:
                self.pool_s.closeall()
                self.pool_s = None
        except Exception, e:
            logger.error("closing pool failed: %s" % (e))
            return False
        return True   
    
    @contextmanager
    def connection(self, auto_commit=False, pool=None):
        ''' get connection for running transaction script 
            sqls in script will be deemed as a transaction and can be rolled-back/committed as a whole
            Usage:
                with pgclient.connection() as conn:
                    result = pgclient.execute("SELECT XXXX", conn=conn)
                    ...
                    pgclient.execute("INSERT XXXX", conn=conn)
                    ...
                    pgclient.execute("DELETE XXXX", conn=conn)
                    
            @param auto_commit - set auto-commit mode for this connection
            @note: If script wants to rollback, shall set conn.commit = False
        '''
        
        pool = self.pool_m if not pool else pool
        
        # get corresponding pool
        # get connection
        conn = self._get_conn(pool)
        if conn is not None:
            if auto_commit:
                try:
                    conn.conn.autocommit = True
                except Exception, e:
                    logger.error("set autocommit error [%s]" % e)
                    self._put_conn(conn, reopen=True)
                    conn = None

        try:
            yield conn
        except:
            logger.critical("yield exits with exception: %s" % traceback.format_exc())

        if conn is not None:
            if auto_commit:
                if conn.invalid:
                    self._put_conn(conn, True)
                else:
                    # auto commit, no rollback
                    try:
                        conn.conn.autocommit = False
                    except Exception, e:
                        logger.error("set autocommit error [%s]" % e)
                        self._put_conn(conn, reopen=True)
                        return
                    self._put_conn(conn)
            else:
                if conn.invalid:
                    self._rollback(conn)
                    self._put_conn(conn, True)
                else:
                    # manual commit, according to user's choice to rollback or commit transaction
                    close = not self._commit(conn) if conn.commit else not self._rollback(conn)
                    self._put_conn(conn, close=close)
        return
    
    def execute_sql(self, sql, parameters=None, executemany=False, expect_affcnt=-1, no_cache=False):
        # normally it shall be auto commit
        # but if there is expected_affcnt, shall commit according to expected value
        auto_commit = True if expect_affcnt == -1 else False
        
        # decide which pool to use
        pool = self.pool_m
        if self.pool_s and is_pg_proxied(self.db):
            # for read only requests, read from read-only pool
            op = sql[:10].strip().lower()
            if not op.startswith("update") and not op.startswith("delete") and not op.startswith("insert"):
                pool = self.pool_s
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Picking pg slave for sql: [%s]" % sql)
        
        # if connection is closed, all connections in pool may be invalid
        # so retry until succeed or fail
        retries = pool.auth.maxconn + 1
        while retries > 0:
            with self.connection(auto_commit, pool) as conn:
                if conn != None:
                    affcnt = self._execute(conn, sql, parameters, executemany, no_cache=no_cache)
                    if affcnt != None:               
                        if expect_affcnt != -1 and affcnt != expect_affcnt:
                            if not auto_commit:
                                conn.commit = False
                            logger.error("execute [%s] partially failed" % (sql))
                            return None
                        return affcnt
                    
                    if not auto_commit:
                        conn.commit = False
                        
                    # if execute failed, but connection is ok, don't retry
                    if not conn.invalid:
                        break
                    
            retries -= 1
            sleep_time = random.random() * (0.1 * (2 ** (pool.auth.maxconn - retries)))
            sleep_time = sleep_time if sleep_time <= 1 else 1
            time.sleep(sleep_time)

        raise Exception("execute [%s] failed" % (sql))
    
    def execute(self, conn, sql, parameters=None, no_cache=False):
        '''  a convenient helper to execute a sql statement.
        @param sql - the sql statement to be executed.
                     e.g. "INSERT INTO test (num, data) VALUES (%s, %s)"
        @param parameters - a sequence of variables in the sql operation.
                     e.g. (100, "abc'def")
        @return - 1) if it is a query operation (such as "SELECT"), 
                    return values if succeeded or None if failed
                  2) if it is a command operation (such as "INSERT" or "UPDATE"),
                    return affected rows count if succeeded or None if failed
        '''
        return self._execute(conn, sql, parameters, no_cache=no_cache)
    
    def executemany(self, conn, sql, parameters=None, no_cache=False):
        '''  a convenient helper to execute multiple sql statements.
        @param sql - the sql statement to be executed.
                     e.g. "INSERT INTO test (num, data) VALUES (%s, %s)"
        @param parameters - a sequence of variables in the sql operation.
                     e.g. (100, "abc'def")
        @return - 1) if it is a query operation (such as "SELECT"), 
                    return values if succeeded or None if failed
                  2) if it is a command operation (such as "INSERT" or "UPDATE"),
                    return affected rows count if succeeded or None if failed
        '''
        return self._execute(conn, sql, parameters, executemany=True, no_cache=no_cache)

    def get_all(self, table, condition={}, sort_key=None, columns=None, distinct=False, limit=MAX_LIMIT, interval=0):
        rows = []

        if distinct:
            if not columns:
                logger.error("get_all() requires columns when using distinct")
                return None
            count = self.get_count(table, condition, distinct_columes=columns)
        else:
            count = self.get_count(table, condition)

        if count is None:
            logger.error("get all rows of [%s] failed" % table)
            return None
        if count == 0:
            return rows

        offset = 0
        while offset <= count:
            ret = self.base_get(table, condition, offset=offset, limit=limit, sort_key=sort_key, columns=columns, distinct=distinct)
            if ret is None:
                logger.error("get all rows of [%s] failed" % table)
                return None
            if len(ret) == 0:
                break
            rows.extend(ret)
            offset += len(ret)
            # Avoid the last sleep.
            if offset >= count:
                break
            # sleep interval seconds to ease database pressure
            if interval > 0:
                time.sleep(interval)

        return rows

    def get_sum(self, table, column, condition={}):
        '''
            Accept the filter conditions, and return sum of each column.
        @param table - table name of the resources
        @param column - the column whose sum you want to get. 
        @param condition - a dictionary of filter conditions 
                                   e.g. {'f1':'v1', 'f2','v2'}
        @return sum if succeeded and None if failed.
        '''
        result = self.base_get_sum(table, [column], condition)
        if result is None or len(result) == 0:
            logger.debug("get colum [%s] sum from [%s] failed" % (column, table)) 
            return None
        return result[0][column]
    
    def get_count(self, table, condition={}, is_and=True, distinct_columes=None, allow_estimates=False):
        '''
            Accept the filter conditions, and return resources count.
        @param table - table name of the resources
        @param condition - a dictionary of filter conditions 
                                   e.g. {'f1':'v1', 'f2','v2'}, 
        @param distinct_columes - the columns that need to be distinct
        @param allow_estimates - whether to allow estimates when doing a full count of rows in a table.
        @return count if succeeded and None if failed.
        '''
        # if doing a full count of rows in a table, use estimate count to speed up
        if allow_estimates and len(condition) == 0 and distinct_columes is None:
            return self.base_get_estimate_count(table)
        
        result = self.base_get_count(table, condition, is_and, distinct_columes)
        if result is None or len(result) == 0:
            logger.debug("get count from [%s] failed" % (table)) 
            return None
        return result[0]['count']
    
    def base_get_estimate_count(self, table):
        ''' get estimate row count of a table '''
        # build sql
        try:
            sql = "select reltuples from pg_class where relname = '%s';" % table
        except Exception, e:
            logger.exception("build sql failed: %s" % e)
            return None 
        
        # execute sql, set auto-commit for select sql
        count_set = self.execute_sql(sql)
        if count_set is None or len(count_set) == 0:
            logger.error("get estimate count from [%s] failed" % table)
            return None
        return int(count_set[0]['reltuples']) 
    
    def base_get_sum(self, table, columns, condition={}, is_and=True, group_by=None,
                     offset=0, limit=DEFAULT_LIMIT):
        '''
            Accept the filter conditions, and return sum of each column.
        @param table - table name of the resources
        @param columns - the columns you want to get their sum. 
        @param condition - a dictionary of filter conditions 
                                   e.g. {'f1':'v1', 'f2','v2'}, 
        @param group_by - the column name you want to group by  
        @return sum of each column if succeeded and None if failed.
        '''
        # restrictions on limit and offset
        limit = self._get_limit(limit)
        offset = self._get_offset(offset)
        
        # build sql and parameters
        try:
            sql = "select"
            for i in range(len(columns)):
                if i == 0:
                    sql += " sum(%s) as %s" % (columns[i], columns[i])
                else:
                    sql += ", sum(%s) as %s" % (columns[i], columns[i])
            if group_by is not None:
                sql += ", %s" % group_by
            sql += " from %s" % (table)
            
            # condition
            (sql_str, parameters) = self._build_sql_condition(table, condition, is_and)
            sql += sql_str
                
            # group by
            if group_by is not None:
                sql += " group by %s" % group_by
                
            # offset
            sql += " offset %d limit %d;" % (offset, limit)
        except Exception, e:
            logger.exception("build sql failed: %s" % e)
            return None 
        
        # execute sql, set auto-commit for select sql
        sum_set = self.execute_sql(sql, parameters)
        if sum_set is None:
            logger.error("get sum failed")
            return None
        return sum_set
    
    def base_get_count(self, table, condition={}, is_and=True, distinct_columes=None,
                       group_by=None, offset=0, limit=DEFAULT_LIMIT):
        '''
            Accept the filter conditions, and return resources count.
        @param table - table name of the resources
        @param condition - a dictionary of filter conditions 
                                   e.g. {'f1':'v1', 'f2','v2'}, 
        @param distinct_columes - the columns that need to be distinct
        @param group_by - the column name you want to group by  
        @return count if succeeded and None if failed.
        '''
        # restrictions on limit and offset
        limit = self._get_limit(limit)
        offset = self._get_offset(offset)
        
        # build sql and parameters
        try:
            group_by_str = "" if group_by is None else ", %s" % group_by
            if distinct_columes is None:
                sql = "select count(*)%s from %s" % (group_by_str, table)
            else:
                sql = "select count(distinct(%s))%s from %s" % (",".join(distinct_columes), group_by_str, table)
            
            # condition
            (sql_str, parameters) = self._build_sql_condition(table, condition, is_and)
            sql += sql_str
                    
            # group by
            if group_by is not None:
                sql += " group by %s" % group_by
                
            # offset
            sql += " offset %d limit %d;" % (offset, limit)
        except Exception, e:
            logger.exception("build sql failed: %s" % e)
            return None 
        
        # execute sql, set auto-commit for select sql
        count_set = self.execute_sql(sql, parameters)
        if count_set is None:
            logger.error("get count failed")
            return None
        return count_set
    
    def base_get(self, table, condition={}, columns=None, sort_key=None,
                 reverse=False, offset=0, limit=DEFAULT_LIMIT, is_and=True, no_cache=False, distinct=False):
        '''
            Accept the filter conditions, and return the eligible resources.
        @param table - table name of the resources
        @param condition - a dictionary of filter conditions 
                                   e.g. {'f1':'v1', 'f2','v2'}, 
        @param columns - the returning columns of results.
                                 e.g. ['col1','col2'], 
        @param sort_key - the sort key. e.g. "create_time"
        @param reverse - sort order, True for DESC, False for ASC
        @param offset - an integer to specify starting offset for returning result, used in paging
        @param limit - an integer to specify the limitation of return count
        @param distinct - select distinct or not. 
        @return resources set if succeeded and None if failed.
                e.g. {{'col1':'v1', 'col2','v2'}, 
                      {'col1':'v1', 'col2','v2'},}
        '''
        # restrictions on limit and offset
        limit = self._get_limit(limit)
        offset = self._get_offset(offset)
        
        # build sql and parameters
        try:
            if columns is None or len(columns) == 0:
                columns = "*"
            else:
                columns = ",".join(columns)
            if distinct and columns != "*":
                sql = "select distinct %s from %s" % (columns, table)
            else:
                sql = "select %s from %s" % (columns, table)
            
            # condition
            (sql_str, parameters) = self._build_sql_condition(table, condition, is_and)
            sql += sql_str
                
            # sort
            if sort_key is not None:
                sql += " order by %s %s" % (sort_key, "desc" if reverse else "asc")
                
            # offset
            sql += " offset %d limit %d;" % (offset, limit)
        except Exception, e:
            logger.exception("build sql failed: %s" % e)
            return None 
        
        # execute sql, set auto-commit for select sql
        return self.execute_sql(sql, parameters, no_cache=no_cache)

    def base_insert(self, table, columns):
        ''' insert a new record
        @param table - table name of the resources
        @param columns - a dictionary of columns to insert
                        e.g. {'col1':'v1', 'col2','v2'},
        @return affected row count or -1 if failed
        '''
        if columns is None or len(columns) == 0:
            logger.error("cannot insert empty columns")
            return -1
        
        # build sql and parameters
        try:
            sql = "insert into %s" % table
            (col_names, val_names, parameters) = ("", "", [])
            for k, v in columns.items():
                if len(parameters) == 0:
                    col_names += "(%s" % k
                    val_names += "(%s"
                else:
                    col_names += ", %s" % k
                    val_names += ", %s"
                parameters.append(v)
            sql += " %s) values %s)" % (col_names, val_names)
        except Exception, e:
            logger.exception("build sql failed: %s" % (e))
            return -1
        
        # execute sql
        affcnt = self.execute_sql(sql, parameters)
        if affcnt is None:
            logger.error("insert failed: [%s]" % columns)
            return -1   
        return affcnt 

    def base_update(self, table, condition, columns, is_and=True, expect_affcnt=-1, suppress_warning=False):
        ''' update a record
        @param table - table name of the resources.
        @param condition - on what condition, {key1:val1, key2:val2}
        @param columns - a dictionary of new columns to update
                        e.g. {'col1':'new_v1', 'col2','new_v2'},
        @param expect_affcnt - how many affected count is expected
        @param suppress_warning - do not log error message if set to True
        @return affected row count or -1 if failed
        '''
        if condition == None or len(condition) == 0:
            logger.warn("empty condition")
            return 0
        if columns is None or len(columns) == 0:
            logger.warn("empty columns")
            return 0
        
        # build sql and parameters
        try:
            # columns
            sql = "update %s set" % table
            parameters = []
            for key, val in columns.iteritems():
                if len(parameters) == 0:
                    sql += " %s = %%s" % (key)
                else:
                    sql += " , %s = %%s" % (key)
                parameters.append(val)
                
            # condition
            sql += " where"
            csign = "and" if is_and else "or"
            old_len = len(parameters)
            for key, val in condition.iteritems():
                pend_str = csign
                if len(parameters) == old_len:
                    pend_str = ""
                if isinstance(val, (list, tuple)):
                    if len(val) == 1:
                        sql += " %s %s = %%s" % (pend_str, key)
                        parameters.append(val[0])
                    else:
                        sql += " %s %s in %%s" % (pend_str, key)
                        parameters.append(tuple(val))
                elif isinstance(val, RangeType):
                    # val.val: [start, end]
                    if val.val[0] is None:
                        sql += " %s %s <= %%s" % (pend_str, key)
                        parameters.append(val.val[1]) 
                    elif val.val[1] is None:
                        sql += " %s %s >= %%s" % (pend_str, key)
                        parameters.append(val.val[0]) 
                    else:
                        sql += " %s %s between %%s and %%s" % (pend_str, key)
                        parameters.append(val.val[0])
                        parameters.append(val.val[1])
                else:
                    sql += " %s %s = %%s" % (pend_str, key)
                    parameters.append(val)
        except Exception, e:
            logger.exception("build sql failed: %s" % (e))
            return -1
        
        # execute sql
        affcnt = self.execute_sql(sql, parameters, expect_affcnt=expect_affcnt)
        if affcnt is None:
            if suppress_warning:
                logger.debug("update failed: [%s] [%s]" % (condition, str(affcnt)))
            else:
                logger.error("update failed: [%s] [%s]" % (condition, str(affcnt)))
            return -1   
        return affcnt

    def base_delete(self, table, condition, is_and=True, expect_affcnt=-1):
        ''' delete by filter condition
        
        @param table - which table to delete
        @param condition - on what condition, {key1:val1, key2:val2}
        @param is_and - True for "and" condition; False for "or" condition
        @param expect_affcnt - how many affected count is expected
        @return affected row count or -1 if failed
        '''  
        if condition == None or len(condition) == 0:
            logger.warn("empty condition")
            return 0
        
        # build sql and parameters
        try:
            sql = "delete from %s" % (table)

            # condition
            sql += " where"
            parameters = []
            csign = "and" if is_and else "or"
            for key, val in condition.iteritems():
                pend_str = csign
                if len(parameters) == 0:
                    pend_str = ""
                if isinstance(val, (list, tuple)):
                    if len(val) == 1:
                        sql += " %s %s = %%s" % (pend_str, key)
                        parameters.append(val[0])
                    else:
                        sql += " %s %s in %%s" % (pend_str, key)
                        parameters.append(tuple(val))
                elif isinstance(val, RangeType):
                    # val.val: [start, end]
                    if val.val[0] is None:
                        sql += " %s %s <= %%s" % (pend_str, key)
                        parameters.append(val.val[1]) 
                    elif val.val[1] is None:
                        sql += " %s %s >= %%s" % (pend_str, key)
                        parameters.append(val.val[0]) 
                    else:
                        sql += " %s %s between %%s and %%s" % (pend_str, key)
                        parameters.append(val.val[0])
                        parameters.append(val.val[1])
                else:
                    sql += " %s %s = %%s" % (pend_str, key)
                    parameters.append(val)
        except Exception, e:
            logger.exception("build sql failed: %s" % (e))
            return -1
        
        # execute sql
        affcnt = self.execute_sql(sql, parameters, expect_affcnt=expect_affcnt)
        if affcnt is None:
            logger.error("delete failed: [%s] [%s]" % (condition, str(affcnt)))
            return -1   
        return affcnt

    def base_join(self, join_keys, columns, conditions={}, sort_keys={},
                  offset=0, limit=DEFAULT_LIMIT, is_and=True, no_cache=False, distinct=False, extra_sql=None):
        '''
            Join multiple tables, and return the eligible resources.
        @param join_keys - the joining keys of each tables.
                                 e.g. [(('tableA', keyA), ('tableB': keyB), join_type),
                                       (('tableA', keyA), ('tableB': keyB), join_type)]
                           the joining type: JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN.
        @param columns - the returning columns of each tables.
                                 e.g. {'tableA': ['col1','col2'],
                                       'tableB': None,}
        @param conditions - a dictionary of filter conditions for each tables
                                   e.g. {'tableA': {'f1':'v1', 'f2','v2'},
                                         'tableB': {'f1':'v1', 'f2','v2'},}
        @param sort_keys - the sort keys, [sort_key, reverse=False] or sort_key.
                                 e.g. {'tableA': [keyA, True],
                                       'tableB': keyB}
        @param offset - an integer to specify starting offset for returning result, used in paging
        @param limit - an integer to specify the limitation of return count
        @return resources set if succeeded and None if failed.
                e.g. [{'col1':'v1', 'col2','v2'},
                      {'col1':'v1', 'col2','v2'},]
        '''
        # restrictions on limit and offset
        limit = self._get_limit(limit)
        offset = self._get_offset(offset)

        # build sql and parameters
        try:
            # display columns and join keys
            columns = self._build_join_display_columns(columns)
            tables = self._build_join_keys(join_keys)

            if distinct and columns != "*":
                sql = "select distinct %s from %s" % (columns, tables)
            else:
                sql = "select %s from %s" % (columns, tables)

            # filter condition
            (sql_str, parameters) = self._build_join_conditions(conditions, is_and)
            sql += sql_str

            if extra_sql:
                sql += extra_sql

            # sort
            if len(sort_keys) > 0:
                sql += " order by %s" % self._build_join_sort_keys(sort_keys)

            # offset
            sql += " offset %d limit %d;" % (offset, limit)
        except Exception, e:
            logger.exception("build sql failed: %s" % e)
            return None

        # execute sql, set auto-commit for select sql
        return self.execute_sql(sql, parameters, no_cache=no_cache)

    def get_join_count(self, join_keys, conditions={}, is_and=True, columns="*", distinct=False, extra_sql=None):
        '''
            Join multiple tables, and return resources count.
        @param join_keys - the joining keys of each tables.
                                 e.g. [(('tableA', keyA), ('tableB': keyB), join_type),
                                       (('tableA', keyA), ('tableB': keyB), join_type)]
                           the joining type: JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN.
        @param conditions - a dictionary of filter conditions for each tables
                                   e.g. {'tableA': {'f1':'v1', 'f2','v2'},
                                         'tableB': {'f1':'v1', 'f2','v2'},}
        @return count if succeeded and None if failed.
        '''

        # build sql and parameters
        try:
            # display columns and join keys

            tables = self._build_join_keys(join_keys)

            if distinct and columns != "*":
                columns = self._build_join_display_columns(columns)
                sql = "select count(distinct(%s)) from %s" % (columns, tables)
            else:
                sql = "select count(*) from %s" % tables

            # filter condition
            (sql_str, parameters) = self._build_join_conditions(conditions, is_and)
            sql += sql_str

            if extra_sql:
                sql += extra_sql

        except Exception, e:
            logger.exception("build sql failed: %s" % e)
            return None

        # execute sql, set auto-commit for select sql
        count_set = self.execute_sql(sql, parameters)
        if count_set is None or len(count_set) == 0:
            logger.debug("get count from join [%s] failed" % (join_keys))
            return None
        return count_set[0]['count']

    def _get_limit(self, limit):
        ''' restrictions on limit '''
        limit = MAX_LIMIT if limit > MAX_LIMIT else limit
        limit = DEFAULT_LIMIT if limit < 0 else limit
        return limit
    
    def _get_offset(self, offset):
        ''' restrictions on limit '''
        offset = 0 if offset < 0 else offset
        offset = MAX_OFFSET if offset > MAX_OFFSET else offset
        return offset
    
    def _build_join_display_columns(self, columns):
        ''' build join display columns '''
        display_columns = []
        for table, cols in columns.items():
            if cols is None:
                display_columns.append("%s.*" % table)
                continue
            for col_name in cols:
                display_columns.append("%s.%s" % (table, col_name))
        return ", ".join(display_columns)
    
    def _build_join_keys(self, join_keys):
        ''' build join keys '''
        sql_str = "%s " % join_keys[0][0][0]
        rtable = None
        for join_key in join_keys:
            (table_left, key_left) = join_key[0]
            (table_right, key_right) = join_key[1]
            join_type = 'join'
            if len(join_key) > 2:
                join_type = join_key[2]
            if rtable is None or rtable != table_right:
                sql_str += " %s %s on %s.%s = %s.%s" % (join_type, table_right, table_left, key_left, table_right, key_right)
            else:
                sql_str += " and %s.%s = %s.%s" % (table_left, key_left, table_right, key_right)
            rtable = table_right
        return sql_str
    
    def _build_join_conditions(self, conditions, is_and, no_where=False):
        ''' build join conditions '''
        # build condition
        sql = ""
        if len(conditions) > 0:
            for condition in conditions.values():
                if condition and not no_where:
                    sql += " where"
                    break;
        parameters = []
        csign = "and" if is_and else "or"
        for table, condition in conditions.iteritems():
            if condition is None:
                continue
            for key, val in condition.iteritems():
                pend_str = csign
                if len(parameters) == 0:
                    pend_str = ""
                if isinstance(val, (list, tuple)):
                    if len(val) == 1:
                        sql += " %s %s.%s = %%s" % (pend_str, table, key)
                        parameters.append(val[0])
                    else:
                        sql += " %s %s.%s in %%s" % (pend_str, table, key)
                        parameters.append(tuple(val))    
                elif isinstance(val, NotType):
                    if isinstance(val.val, (list, tuple)):
                        if len(val.val) == 1:
                            sql += " %s %s.%s != %%s" % (pend_str, table, key)
                            parameters.append(val.val[0])
                        else:
                            sql += " %s %s.%s not in %%s" % (pend_str, table, key)
                            parameters.append(tuple(val.val))  
                    else:      
                        sql += " %s %s.%s != %%s" % (pend_str, table, key)
                        parameters.append(val.val)    
                elif isinstance(val, SearchType):
                    sql += " %s %s.%s ilike %%s" % (pend_str, table, key)
                    parameters.append(val.val)
                elif isinstance(val, SearchWordType):
                    sql += " %s (" % pend_str
                    cnt = 0
                    for col in SEARCH_COLUMNS[table]:
                        if cnt == 0:
                            sql += "%s.%s ilike %%s " % (table, col)
                        else:
                            sql += "or %s.%s ilike %%s " % (table, col)
                        cnt += 1
                        parameters.append("%%%s%%" % val.val)
                    if cnt == 0:
                        sql += " %s.%s = %%s)" % (table, INDEXED_COLUMNS[table][0])
                    else:
                        sql += " or %s.%s = %%s)" % (table, INDEXED_COLUMNS[table][0]) 
                    parameters.append(val.val)
                elif isinstance(val, TimeStampType):
                    # val.val: [start_time, end_time]
                    if val.val[0] is None:
                        sql += " %s %s.%s <= %%s" % (pend_str, table, key)
                        parameters.append(val.val[1]) 
                    elif val.val[1] is None:
                        sql += " %s %s.%s >= %%s" % (pend_str, table, key)
                        parameters.append(val.val[0]) 
                    else:
                        sql += " %s %s.%s between %%s and %%s" % (pend_str, table, key)
                        parameters.append(val.val[0])
                        parameters.append(val.val[1])
                elif isinstance(val, RangeType):
                    # val.val: [start, end]
                    if val.val[0] is None:
                        sql += " %s %s.%s <= %%s" % (pend_str, table, key)
                        parameters.append(val.val[1]) 
                    elif val.val[1] is None:
                        sql += " %s %s.%s >= %%s" % (pend_str, table, key)
                        parameters.append(val.val[0]) 
                    else:
                        sql += " %s %s.%s between %%s and %%s" % (pend_str, table, key)
                        parameters.append(val.val[0])
                        parameters.append(val.val[1])  
                elif isinstance(val, RegExpType):
                    sql += " %s %s.%s %s %%s" % (pend_str, table, key, val.operator)
                    parameters.append(val.val)
                else:
                    sql += " %s %s.%s = %%s" % (pend_str, table, key)
                    parameters.append(val)
        return (sql, parameters)
    
    def _build_join_sort_keys(self, sort_keys):
        ''' build join keys '''
        sql_str = ""
        for table, sort_key in sort_keys.items():
            if sort_key is None:
                continue
            key = sort_key
            sort_order = "asc"
            if isinstance(sort_key, (list, tuple)):
                key = sort_key[0]
                sort_order = "desc" if sort_key[1] else "asc"
            if sql_str == "":
                sql_str += "%s.%s %s" % (table, key, sort_order)
            else:
                sql_str += ", %s.%s %s" % (table, key, sort_order)
        return sql_str
    
    def _build_sql_condition(self, table, condition, is_and):
        ''' build sql condition '''
        # build condition
        sql = ""
        if len(condition) > 0:
            sql += " where"
        parameters = []
        csign = "and" if is_and else "or"
        for key, val in condition.iteritems():
            pend_str = csign
            if len(parameters) == 0:
                pend_str = ""
            if isinstance(val, (list, tuple)):
                if len(val) == 1:
                    sql += " %s %s = %%s" % (pend_str, key)
                    parameters.append(val[0])
                else:
                    sql += " %s %s in %%s" % (pend_str, key)
                    parameters.append(tuple(val))
            elif isinstance(val, SearchType):
                sql += " %s %s ilike %%s" % (pend_str, key)
                parameters.append(val.val)
            elif isinstance(val, SearchWordType):
                sql += " %s (" % pend_str
                cnt = 0
                for col in SEARCH_COLUMNS[table]:
                    if cnt == 0:
                        sql += "%s ilike %%s " % (col)
                    else:
                        sql += "or %s ilike %%s " % (col)
                    cnt += 1
                    parameters.append("%%%s%%" % val.val)
                if cnt == 0:
                    sql += " %s = %%s)" % (INDEXED_COLUMNS[table][0])
                else:
                    sql += " or %s = %%s)" % (INDEXED_COLUMNS[table][0])
                parameters.append(val.val) 
            elif isinstance(val, TimeStampType):
                # val.val: [start_time, end_time]
                if val.val[0] is None:
                    sql += " %s %s <= %%s" % (pend_str, key)
                    parameters.append(val.val[1]) 
                elif val.val[1] is None:
                    sql += " %s %s >= %%s" % (pend_str, key)
                    parameters.append(val.val[0]) 
                else:
                    sql += " %s %s between %%s and %%s" % (pend_str, key)
                    parameters.append(val.val[0])
                    parameters.append(val.val[1])  
            elif isinstance(val, RangeType):
                # val.val: [start, end]
                if val.val[0] is None:
                    sql += " %s %s <= %%s" % (pend_str, key)
                    parameters.append(val.val[1]) 
                elif val.val[1] is None:
                    sql += " %s %s >= %%s" % (pend_str, key)
                    parameters.append(val.val[0]) 
                else:
                    sql += " %s %s between %%s and %%s" % (pend_str, key)
                    parameters.append(val.val[0])
                    parameters.append(val.val[1])  
            elif isinstance(val, NotType):
                if isinstance(val.val, (list, tuple)):
                    if len(val.val) == 1:
                        sql += " %s %s != %%s" % (pend_str, key)
                        parameters.append(val.val[0])
                    else:
                        sql += " %s %s not in %%s" % (pend_str, key)
                        parameters.append(tuple(val.val))
                elif isinstance(val.val, AndMaskType):
                    sql += " %s %s & %%s != %%s" % (pend_str, key)
                    parameters.append(val.val.lhs)
                    parameters.append(val.val.rhs)
                elif isinstance(val.val, OrMaskType):
                    sql += " %s %s | %%s != %%s" % (pend_str, key)
                    parameters.append(val.val.lhs)
                    parameters.append(val.val.rhs)
                else:
                    sql += " %s %s != %%s" % (pend_str, key)
                    parameters.append(val.val)
            elif isinstance(val, AndMaskType):
                sql += " %s %s & %%s = %%s" % (pend_str, key)
                parameters.append(val.lhs)
                parameters.append(val.rhs)
            elif isinstance(val, OrMaskType):
                sql += " %s %s | %%s = %%s" % (pend_str, key)
                parameters.append(val.lhs)
                parameters.append(val.rhs)
            elif isinstance(val, RegExpType):
                sql += " %s %s %s %%s" % (pend_str, key, val.operator)
                parameters.append(val.val)
            else:
                sql += " %s %s = %%s" % (pend_str, key)
                parameters.append(val)
        return (sql, parameters)
    
    def _get_conn(self, pool):
        ''' get connection from pool 
        @return a valid connection if succeeded and None if failed.
        '''
        class Conn():
            def __init__(self, conn):
                self.commit = True  # normally commit for manual transaction, set to False if want to rollback
                self.conn = conn
                self.invalid = False
                self.pool = pool  # the actual pool
                
        # if get failed, it will wait for a random time before next get.
        conn = None
        retry_time = 0
        while retry_time < self.MAX_RETRY_TIME:
            try:
                conn = pool.getconn()
                return Conn(conn) if conn != None else None
            except Exception, e:
                # may failed if connection pool exhausted
                logger.warn("get connection failed: %s" % (e))
                retry_time += 1
                sleep_time = random.random() * (0.1 * (2 ** retry_time))
                time.sleep(sleep_time)
                logger.warn("retry get_conn for [%d] time after sleep for [%.2f] secs" % (retry_time, sleep_time))
        
        # if get connection failed, try to reconnect for another pool 
        logger.critical("get connection failed after retry for [%d] times" % (retry_time))
        pool.reopen()
        return None
        
    def _put_conn(self, conn, close=False, reopen=False):
        ''' return connection back to pool 
            If close is True, discard the connection from the pool.
        @return True if succeeded and False if failed.
        '''
        try:
            if reopen:
                conn.pool.reopen()
            else:
                conn.pool.putconn(conn.conn, close=close)
        except Exception, e:
            # may failed if the pool is closed
            logger.error("put connection failed: %s" % (e))
            return False
        return True
    
    def _commit(self, conn):
        ''' Commit any pending transaction of the 
            connection to the database.
        @return True if succeeded and False if failed.
        '''
        try:
            conn.conn.commit()
        except Exception, e:
            # may failed if connection already closed
            logger.error("connection commit failed: %s" % (e))
            return False
        return True

    def _rollback(self, conn):
        ''' Roll back to the start of any pending 
            transaction of the connection.
        @return True if succeeded and False if failed. 
        '''
        try:
            conn.conn.rollback()
        except Exception, e:
            # may failed if connection already closed
            if -1 == ("%s" % e).find("connection already closed"):
                logger.error("connection rollback failed: %s" % (e))
            return False
        return True
    
    def _fetchall(self, cursor):
        ''' fetch all result from a cursor
        @return result if succeeded and None if failed
        '''
        try:
            result = cursor.fetchall()
        except Exception, e:
            logger.error("cursor fetchall failed: %s" % (e))
            return None
        return result        

    def _execute(self, conn, sql, parameters=None, executemany=False, no_cache=False):
        ''' execute sql within a connection '''               
        if conn == None:
            return None

        # select may have comment at the head
        query = True
        op = sql[:10].strip().lower()
        if op.startswith("update") or op.startswith("delete") or op.startswith("insert"):
            query = False
        
        sqlstr = sql
        if query and no_cache:
            sqlstr = "/* NO QUERY CACHE */ " + sql
    
        # execute sql, use a dictionary-like cursor
        cur = None
        try:
            cur = conn.conn.cursor(cursor_factory=RealDictCursor)
            if executemany:
                cur.executemany(sqlstr, parameters)
            else:
                cur.execute(sqlstr, parameters)
                
            if query:
                values = self._fetchall(cur)
                if logger.isEnabledFor(logging.DEBUG):
                    row_num = len(values)
                    format_str = ""
                    for i, v in enumerate(values):
                        if i >= 10:
                            break
                        if row_num > 1:
                            format_str += "\n\t row [%d]:" % i
                        for key in v.iterkeys():
                            format_str += "\n\t\t %s: [%s]" % (key, str(v[key]))
                    format_str += "\n"

                    logger.debug("execute sql [%s] with [%s] returns [%d] rows: %s",
                                 sql, "()" if parameters is None else parameters, row_num, format_str)
                return values
            
            affected_cnt = cur.rowcount
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("execute sql [%s] with [%s] affects [%d] rows",
                             sql, "()" if parameters is None else parameters, affected_cnt)
        except Exception, e:
            if isinstance(e, (ProgrammingError, IntegrityError, DataError)):
                logger.critical("execute sql [%s] failed: %s" % (sql, e))
                return None
            if -1 == ("%s" % e).find("client idle limit reached"):
                logger.debug("execute sql [%s] failed: %s" % (sql, e))
            conn.invalid = True
            return None
        finally:
            if cur != None:
                try:
                    cur.close()
                except:
                    pass

        return affected_cnt
