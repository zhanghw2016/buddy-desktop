'''
Created on 2012-9-24

@author: yunify
'''

import traceback
from contextlib import contextmanager
from db.constants import INDEXED_COLUMNS, COMPOSITE_PRIMARY_KEY_TABLES, DEFAULT_LIMIT
from log.logger import logger
from db.pg_base import PGBase
from utils.thread_local import enable_pg_proxy, disable_pg_proxy
from collections import OrderedDict

@contextmanager
def pg_no_proxy(db):
    ''' disable pg proxy, use r/w only '''
    disable_pg_proxy(db)
    try:
        yield
    except:
        logger.critical("yield exits with exception: %s" % traceback.format_exc())
    enable_pg_proxy(db)

class PGClient(PGBase):
    ''' A thread-safe postgreSQL client wrapper for one database '''

    def __init__(self):
        super(PGClient, self).__init__()

        self.delete_pre_trigger = None
        self.delete_triggers = set()
        self.update_pre_trigger = None
        self.update_triggers = set()
        self.insert_triggers = set()

    def set_delete_pre_trigger(self, pre_trigger):
        ''' set pre-trigger for delete operation '''
        self.delete_pre_trigger = pre_trigger

    def add_delete_trigger(self, trigger):
        ''' add the trigger as call back when records are deleted '''
        self.delete_triggers.add(trigger)

    def set_update_pre_trigger(self, pre_trigger):
        ''' set pre-trigger for update operation '''
        self.update_pre_trigger = pre_trigger

    def add_update_trigger(self, trigger):
        ''' add the trigger as call back when records are updated '''
        self.update_triggers.add(trigger)

    def add_insert_trigger(self, trigger):
        ''' add the trigger as call back when records are inserted '''
        self.insert_triggers.add(trigger)

    def get(self, table, key, columns=None):
        '''
            Return the columns of key in table.
        @param table - table name of the resources
        @param key - the row key you want to get
        @return a dictionary of columns of key if succeeded and None if failed.
                e.g. {'col1':'v1', 'col2','v2'},
        '''

        condition = {INDEXED_COLUMNS[table][0] : key}
        result = self.base_get(table, condition, columns)
        if result is None or len(result) == 0:
            logger.debug("get [%s] from [%s] failed" % (key, table))
            return None
        return result[0]

    def multiget(self, table, keys):
        '''
            Return the columns of keys in table.
        @param table - table name of the resources
        @param keys - the row keys you want to get
        @return a dictionary of columns of keys if succeeded and None if failed.
                e.g. {'k1':{'col1':'v1', 'col2','v2'},
                      'k2':{'col1':'v1', 'col2','v2'},}
        Note: The implementation here is a little bit awkward because
              "executemany" is not supported well when using select with RealDictCursor.
        '''
        resources_set = {}
        primary_key = INDEXED_COLUMNS[table][0]
        for key in keys:
            resource = self.get(table, key)
            if resource is not None:
                resources_set[resource[primary_key]] = resource
        return resources_set

    def get_by_filter(self, table, condition, columns=None,
                      sort_key=None, reverse=False, offset=0, limit=DEFAULT_LIMIT,
                      ordered=False, is_list=False):
        '''
            Accept the filter conditions, and return the eligible resources.
        @param table - table name of the resources
        @param condition - a dictionary of filter conditions
                                   e.g. {'f1':'v1', 'f2','v2'},
        @param columns - the returning columns of results.
                                 e.g. ['col1','col2'],
        @param sort_key - the sort key. e.g. "create_time"
        @param reverse - sort order, True for ASC, False for DESC
        @param offset - an integer to specify starting offset for returning result, used in paging
        @param limit - an integer to specify the limitation of return count
        @param ordered - return OrderedDict or not
        @return resources set if succeeded and None if failed.
                e.g. {'k1':{'col1':'v1', 'col2','v2'},
                      'k2':{'col1':'v1', 'col2','v2'},}
        '''
        
        if columns is not None and not columns:
            return {}
        
        result = self.base_get(table, condition, columns, sort_key, reverse, offset, limit)
        if result is not None:
            resources_set = OrderedDict() if ordered else {}
            if is_list:
                return result

            primary_key = INDEXED_COLUMNS[table][0]
            for res in result:
                resources_set[res[primary_key]] = res
            return resources_set

        return None

    def insert(self, table, columns):
        ''' insert a new record
        @param table - table name of the resources
        @param columns - a dictionary of columns to insert
                        e.g. {'col1':'v1', 'col2','v2'},
        @return True if succeeded and False if failed.
        '''
        affcnt = self.base_insert(table, columns)
        if affcnt == -1:
            logger.error("insert failed: [%s]" % columns)
            return False

        # insert triggers when succeed
        for trigger in self.insert_triggers:
            trigger(table, columns)
        return True

    def batch_insert(self, table, rows, allow_partially_successful=False):
        ''' insert multiple rows at a time
        @param table - table name of the resources
        @param rows - a dictionary of rows to insert.
                        e.g. {'r1':{'k1':'v1', 'k2','v2'},
                              'r2':{'k1':'v1', 'k2','v2'}}
                        Note:
                            the column names of every row to
                            insert should be the same.
        @param allow_partially_successful - if True, than partially successful is allowed.
        @return True if succeeded and False if failed.
        '''
        if rows is None or len(rows) == 0:
            logger.error("cannot insert empty rows")
            return False

        # build sql and parameters
        try:
            sql = "insert into %s" % table
            (col_names, val_names, parameters) = ("", "", [])
            for val in rows.values():
                rparam = []
                for k in sorted(val.keys()):
                    if len(parameters) == 0:
                        if len(col_names) == 0:
                            col_names += "(%s" % k
                            val_names += "(%s"
                        else:
                            col_names += ", %s" % k
                            val_names += ", %s"
                    rparam.append(val[k])
                parameters.append(tuple(rparam))
            sql += " %s) values %s)" % (col_names, val_names)
        except Exception, e:
            logger.exception("build sql failed: %s" % (e))
            return False

        # execute sql
        expect_affcnt = len(rows) if not allow_partially_successful else -1
        ret = self.execute_sql(sql, parameters, executemany=True, expect_affcnt=expect_affcnt)
        if ret is None:
            logger.error("batch insert failed: [%s]" % rows)
            return False

        # insert triggers when succeed
        for val in rows.values():
            for trigger in self.insert_triggers:
                trigger(table, val)
        return True

    def update(self, table, key, columns, suppress_warning=False,expect_affcnt=1):
        ''' update a record
        @param table - table name of the resources.
        @param key - the primary key you want to update.
        @param columns - a dictionary of new columns to update
                        e.g. {'col1':'new_v1', 'col2','new_v2'},
        @param suppress_warning - do not log error message if set to True
        @return True if succeeded and False if failed.
        '''
        # run pre-trigger for getting owner etc.
        if self.update_pre_trigger:
            self.update_pre_trigger(table, key, columns)

        condition = {INDEXED_COLUMNS[table][0] : key}

        if isinstance(key, list):
            expect_affcnt = len(key)

        affcnt = self.base_update(table, condition, columns, expect_affcnt=expect_affcnt, suppress_warning=suppress_warning)
        if affcnt == -1:
            if suppress_warning:
                logger.debug("update failed: [%s]" % columns)
            else:
                logger.error("update failed: [%s]" % columns)
            return False

        # update triggers when succeed
        for trigger in self.update_triggers:
            trigger(table, key, columns)
        return True

    def batch_update(self, table, rows, allow_partially_successful=False):
        ''' update multiple rows
        @param table - table name of the resources.
        @param rows - the rows you want to update.
                      e.g. {'r1':{'k1':'v1', 'k2','v2'},
                            'r2':{'k1':'v1', 'k2','v2'}}
                      Note:
                            the column names of every row to
                            update should be the same.
        @param allow_partially_successful - if True, than partially successful is allowed.
        @return True if succeeded and False if failed.
        '''
        if rows is None or len(rows) == 0:
            logger.error("cannot update empty rows")
            return False

        # build sql and parameters
        try:
            primary_key = INDEXED_COLUMNS[table][0]
            sql = "update %s set" % table
            parameters = []
            for key, val in rows.items():
                rparams = []
                for k in sorted(val.keys()):
                    if k == primary_key:
                        # primary key can not be updated
                        continue
                    if len(parameters) == 0:
                        if len(rparams) == 0:
                            sql += " %s = %%s" % k
                        else:
                            sql += ", %s = %%s" % k
                    rparams.append(val[k])
                rparams.append(key)
                parameters.append(tuple(rparams))
            # the first indexed column of the table is primary key
            sql += " where %s = %%s" % primary_key
        except Exception, e:
            logger.exception("build sql failed: %s" % (e))
            return False

        # execute sql
        expect_affcnt = len(rows) if not allow_partially_successful else -1
        ret = self.execute_sql(sql, parameters, executemany=True, expect_affcnt=expect_affcnt)
        if ret is None:
            logger.error("batch update failed: [%s]" % rows)
            return False

        # update triggers when succeed
        for key, val in rows.items():
            for trigger in self.update_triggers:
                trigger(table, key, val)
        return True

    def delete(self, table, key, allow_partially_successful=True):
        ''' delete row in table by specifying primary key or composite keys.
        @param table - table name of the resources.
        @param key - the primary key or composite keys you want to delete.
                     You can specify a primary key, which is a string, or you
                     can specify a list of composite keys, which is a list.
        @param allow_partially_successful - if True, than partially successful is allowed.
        @return True if succeeded and False if failed.
        '''

        # run pre-trigger for getting owner etc.
        if self.delete_pre_trigger:
            self.delete_pre_trigger(table, key)

        if not isinstance(key, list) and table in COMPOSITE_PRIMARY_KEY_TABLES:
            logger.error("when delete rows in table with composite keys, please specify composite keys as a list")
            return False

        if isinstance(key, list) and table not in COMPOSITE_PRIMARY_KEY_TABLES:
            logger.error("please specify one key at a time.")
            return False

        # build sql and parameters
        try:
            if not isinstance(key, list):
                condition = {INDEXED_COLUMNS[table][0] : key}
            else:
                condition = {}
                for i in range(len(key)):
                    condition[COMPOSITE_PRIMARY_KEY_TABLES[table][i]] = key[i]
        except Exception, e:
            logger.exception("build sql failed: %s" % (e))
            return False

        expect_affcnt = 1 if not allow_partially_successful else -1
        affcnt = self.base_delete(table, condition, expect_affcnt=expect_affcnt)
        if affcnt == -1:
            logger.error("delete failed: [%s]" % condition)
            return False

        # update triggers when succeed
        for trigger in self.delete_triggers:
            trigger(table, key)
        return True
