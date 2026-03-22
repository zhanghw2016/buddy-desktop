'''
Created on 2012-6-26

@author: yunify
'''
import error.error_code as ErrorCodes
from error.error import Error
from constants import (
    REQ_EXPIRED_INTERVAL,
    DEFAULT_MAX_COUNT_PER_TIME,
)
from db.constants import (
    DEFAULT_LIMIT,
    MAX_OFFSET,
)
from utils.time_stamp import get_ts, get_expired_ts


class BaseRequestBuilder(object):
    ''' API request builder '''

    def __init__(self, sender):
        '''
        @param sender - the id of the sender of the request
        '''
        self.sender = sender
        # error message
        self.error = Error(ErrorCodes.INVALID_REQUEST_FORMAT)

    def _add_auth(self, params):
        ''' add privilege related parameters '''
        params["sender"] = self.sender

    def _add_expires(self, params):
        ''' add expires time '''
        params["expires"] = get_expired_ts(get_ts(), REQ_EXPIRED_INTERVAL)

    def _build_params(self, action, body):
        ''' build parameters '''
        params = {}
        for k in body:
            params[k] = body[k]
        params['action'] = action

        # add auth and expires
        self._add_auth(params)
        self._add_expires(params)
        return params

    def filter_out_none(self, dictionary, keys=None):
        """ Filter out items whose value is None.
            If `keys` specified, only return non-None items with matched key.
        """
        ret = {}
        if keys is None:
            keys = []
        for key, value in dictionary.items():
            if value is None or (keys and key not in keys):
                continue
            ret[key] = value
        return ret

    def _get_count(self, c):
        c = int(c)
        return c if c < DEFAULT_MAX_COUNT_PER_TIME else DEFAULT_MAX_COUNT_PER_TIME

    def _get_limit(self, l):
        l = int(l)
        return l if l < DEFAULT_LIMIT else DEFAULT_LIMIT

    def _get_offset(self, o):
        o = int(o)
        return o if o < MAX_OFFSET else MAX_OFFSET

    def _get_reverse(self, r):
        r = int(r)
        return False if r == 0 else True
