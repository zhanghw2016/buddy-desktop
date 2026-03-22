'''
Created on 2015-10-01

@author: yunify
'''

import decimal
import inspect
import re

class BaseChecker(object):

    TYPE_NAMES = []

    @classmethod
    def _check(cls, val, min_value, max_value):
        if min_value is not None and val < min_value:
            return False

        if max_value is not None and val > max_value:
            return False

        return True


class StringChecker(BaseChecker):

    TYPE_NAMES = ["str", "string"]

    @classmethod
    def check(cls, raw, min_value=None, max_value=None):
        valid = cls._check(len(str(raw)), min_value, max_value)
        return valid, raw


class BooleanChecker(BaseChecker):

    TYPE_NAMES = ["bool", "boolean"]

    @classmethod
    def check(cls, raw, min_value=None, max_value=None):
        valid = str(raw).lower() in ["true", "on", "1", "false", "0", "off"]
        return valid, raw


class IntegerChecker(BaseChecker):

    TYPE_NAMES = ["int", "integer"]

    @classmethod
    def check(cls, raw, min_value=None, max_value=None):
        if not str(raw).isdigit():
            return False, raw

        val = int(raw)
        valid = cls._check(val, min_value, max_value)
        return valid, raw

    
class DecimalChecker(BaseChecker):

    TYPE_NAMES = ["float", "double", "decimal"]

    @classmethod
    def check(cls, raw, min_value=None, max_value=None):
        try:
            val = decimal.Decimal(str(raw))
        except decimal.InvalidOperation:
            return False, raw

        min_value = min_value if min_value is None else decimal.Decimal(str(min_value))
        max_value = max_value if max_value is None else decimal.Decimal(str(max_value))
        valid = cls._check(val, min_value, max_value)
        return valid, raw


class MegabyteChecker(BaseChecker):

    TYPE_NAMES = ["k", "kb", "kib", "m", "mb", "mib", "g", "gb", "gib"]
    BYTE_RE = re.compile(r"^(\d+)(?i)(?:(k|m|g)(?:(?:i?)b)?)$")

    @classmethod
    def byte(cls, raw):
        match = cls.BYTE_RE.search(raw)
        if not match:
            raise ValueError("not a byte value: [%s]"%raw)

        val, unit = match.groups()
        val = int(val)
        return val * dict(k=1024, m=1024**2, g=1024**3)[unit.lower()] if unit else val

    @classmethod
    def check(cls, raw, min_value=None, max_value=None):
        _raw = str(raw)
        try:
            val = cls.byte(_raw)
        except ValueError:
            return False, raw

        min_value = min_value if min_value is None else cls.byte("%sMB"%min_value)
        max_value = max_value if max_value is None else cls.byte("%sMB"%max_value)
        valid = cls._check(val, min_value, max_value)
        if not valid:
            return False, raw

        raw_val, raw_unit = cls.BYTE_RE.search(_raw).groups()
        # It must be "kB", rather than "KB".
        unit = raw_unit.upper() if raw_unit.lower() != "k" else raw_unit.lower()
        target = "%s%sB" % (raw_val, unit)
        return valid, target


global Checkers
Checkers = []

def get_checker(var_type):
    global Checkers
    if not Checkers:
        is_checker = lambda obj: inspect.isclass(obj) and issubclass(obj, BaseChecker)
        Checkers = [obj for _, obj in globals().iteritems() if is_checker(obj)]

    Classes = [C for C in Checkers if var_type.lower() in C.TYPE_NAMES]
    if not Classes:
        raise KeyError("no such checker for [%s]"%var_type)
    return Classes[0]

def validate(var_type, var_val, min_value=None, max_value=None):
    Checker = get_checker(var_type)
    return Checker.check(var_val, min_value, max_value)

if __name__ == "__main__":
    assert (True, "1kB") == validate("mb", "1k")
    assert (True, "1MB") == validate("mb", "1mb")
    assert (True, "1GB") == validate("mb", "1gib")
    assert (True, "1024kB") == validate("mb", "1024k", min_value=1)
    assert (True, "1MB") == validate("mb", "1MB", min_value=1, max_value=1024)
    assert (False, 1) == validate("mb", 1)
    assert (False, "1m") == validate("mb", "1m", min_value=32)
    assert (False, "16M") == validate("mb", "16M", max_value=8)

    assert (True, 1) == validate("int", 1)
    assert (True, "1") == validate("integer", "1")
    assert (True, "1") == validate("int", "1", min_value=0)
    assert (True, "1") == validate("int", "1", min_value=0, max_value=1)
    assert (False, "1") == validate("int", "1", min_value=16)
    assert (False, 1) == validate("int", 1, max_value=0)
    assert (False, "a") == validate("int", "a")

    assert (True, 0) == validate("float", 0)
    assert (True, "0.09") == validate("float", "0.09", min_value=0)
    assert (True, 0.09) == validate("float", 0.09, min_value=0)
    assert (False, "0.09") == validate("float", "0.09", min_value="3.14")
    assert (False, 0.09) == validate("float", 0.09, max_value="0.01")
    assert (False, "a") == validate("float", "a")

    assert (True, True) == validate("bool", True)
    assert (True, "false") == validate("boolean", "false")
    assert (True, 1) == validate("bool", 1)
    assert (True, "0") == validate("bool", "0")
    assert (True, "on") == validate("boolean", "on")
    assert (True, "off") == validate("bool", "off")
    assert (False, 2) == validate("bool", 2)
    assert (False, "a") == validate("bool", "a")

    assert (True, "s") == validate("str", "s")
    assert (True, "s") == validate("string", "s")
    assert (False, "s") == validate("str", "s", min_value=5)
    assert (False, "st") == validate("str", "st", max_value=1)
