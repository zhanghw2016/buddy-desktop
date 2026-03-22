# =========================================================================
# Copyright 2012-present Yunify, Inc.
# -------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========================================================================

"""
Check parameters in request
"""

from utils.misc import parse_ts,is_str

class RequestChecker(object):

    def err_occur(self, error_msg):
        raise error_msg

    def is_integer(self, value):
        try:
            int(value)
        except:
            return False
        return True

    def check_integer_params(self, directive, params):
        """ Specified params should be `int` type if in directive
        @param directive: the directive to check
        @param params: the params that should be `int` type.
        """
        for param in params:
            if param not in directive:
                continue
            val = directive[param]
            if self.is_integer(val):
                directive[param] = int(val)
            else:
                self.err_occur(
                    "parameter [%s] should be integer in directive [%s]" % (param, directive))

    def check_list_params(self, directive, params):
        """ Specified params should be `list` type if in directive
        @param directive: the directive to check
        @param params: the params that should be `list` type.
        """
        for param in params:
            if param not in directive:
                continue
            if not isinstance(directive[param], list):
                self.err_occur(
                    "parameter [%s] should be list in directive [%s]" % (param, directive))

    def check_required_params(self, directive, params):
        """ Specified params should be in directive
        @param directive: the directive to check
        @param params: the params that should be in directive.
        """
        for param in params:
            if param not in directive:
                self.err_occur(
                    "[%s] should be specified in directive [%s]" % (param, directive))

    def check_datetime_params(self, directive, params):
        """ Specified params should be `date` type if in directive
        @param directive: the directive to check
        @param params: the params that should be `date` type.
        """
        for param in params:
            if param not in directive:
                continue
            if not parse_ts(directive[param]):
                self.err_occur(
                    "[%s] should be 'YYYY-MM-DDThh:mm:ssZ' in directive [%s]" % (param, directive))

    def check_str_params(self, directive, params):
        '''
            @param directive: the directive to check
            @param params: the params that should be string type.
        '''
        for param in params:
            if param not in directive:
                continue
            if not is_str(directive[param]):
                self.err_occur("parameter [%s] should be string in directive [%s]" % (param, directive))

    def check_params(self, directive, required_params=None,
                     integer_params=None, list_params=None, 
                     datetime_params=None, str_params=None):
        """ Check parameters in directive
        @param directive: the directive to check, should be `dict` type.
        @param required_params: a list of parameter that should be in directive.
        @param integer_params: a list of parameter that should be `integer` type
                               if it exists in directive.
        @param list_params: a list of parameter that should be `list` type
                            if it exists in directive.
        @param datetime_params: a list of parameter that should be `date` type
                                if it exists in directive.
        """
        if not isinstance(directive, dict):
            self.err_occur('[%s] should be dict type' % directive)
            return False

        if required_params:
            self.check_required_params(directive, required_params)
        if integer_params:
            self.check_integer_params(directive, integer_params)
        if list_params:
            self.check_list_params(directive, list_params)
        if datetime_params:
            self.check_datetime_params(directive, datetime_params)
        if str_params:
            self.check_str_params(directive, str_params)
        return True


