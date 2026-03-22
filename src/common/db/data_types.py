'''
Created on 2012-9-24

@author: yunify
'''

class SearchType(object):
    ''' data type for 'like' search in sql '''
    def __init__(self, val, pattern="both"):
        # remove wildcard
        val = unicode(val)
        ch_to_delete = u"%_![]^'"
        translate_table = dict([(ord(ch), u' ') for ch in ch_to_delete])
        val = val.translate(translate_table)
        val = "%".join(val.strip().split())
        if pattern == "left":
            val = "%%%s" % val
        elif pattern == "right":
            val = "%s%%" % val
        else:
            val = "%%%s%%" % val
        self.val = val
    
    def __str__(self):
        return self.val
    
class SearchWordType(object):
    ''' data type for search word for resource
        this type will search both seachType columns and id columns
    '''
    def __init__(self, val):
        # remove wildcard
        val = unicode(val)
        ch_to_delete = u"%_![]^"
        translate_table = dict([(ord(ch), u' ') for ch in ch_to_delete])
        val = val.translate(translate_table)
        val = "%".join(val.strip().split())
        self.val = val
    
    def __str__(self):
        return self.val
    
class TimeStampType(object):
    ''' data type for timestamp range filter.
    '''
    def __init__(self, val):
        '''
        @param val: val should be an two-item list like [start_time, end_time].
                    e.g. ['2012-12-30 00:29:40', '2013-01-30 00:29:45']
        '''
        if isinstance(val, list) and len(val) == 2:
            self.val = val
        else:
            self.val = [None, None]
    
    def __str__(self):
        return str(self.val)
    
class RangeType(object):
    ''' data type for range filter.
    '''
    def __init__(self, val):
        '''
        @param val: val should be an two-item list like [start, end].
                    e.g. [0, 100]
        '''
        if isinstance(val, list) and len(val) == 2:
            self.val = val
        else:
            self.val = [None, None]
    
    def __str__(self):
        return str(self.val)
    
class NotType(object):
    ''' data type for Not filter.
    '''
    def __init__(self, val):
        '''
        @param val: val can be string or list type or AndMaskType or OrMaskType.
        '''
        self.val = val
    
    def __str__(self):
        return str(self.val)


class AndMaskType(object):
    def __init__(self, lhs, rhs=0):
        """
        ex:
            column & lhs = rhs
        :param lhs: left hand side operand, only support int currently
        :param rhs: right hand side operand, only support int currently
        :return:
        """
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "column & " + str(self.lhs) + "=" + str(self.rhs)


class OrMaskType(object):
    def __init__(self, lhs, rhs):
        """
        ex:
            column | lhs = rhs
        :param lhs: left hand side operand, only support int currently
        :param rhs: right hand side operand, only support int currently
        :return:
        """
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "column | " + str(self.lhs) + "=" + str(self.rhs)


class RegExpType(object):
    ''' data type for RegExp filter.
    '''
    def __init__(self, val, sensitive=True, is_match=True):
        '''
        @param val: val should be an RegExp string like "^.*(name)|(name2).*$"
        @param sensitive: sensitive(True), insensitive(False)
        @param is_match: match or not march
        '''
        _operator_map = {
            (True, True): '~',
            (True, False): '!~',
            (False, True): '~*',
            (False, False): '!~*',
        }
        self.val = val
        self.operator = _operator_map[(sensitive, is_match)]

    def __str__(self):
        return str(self.val)
