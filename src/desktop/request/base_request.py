'''
Created on 2012-7-9

@author: yunify
'''
import copy

from request.consolidator.api_acl import APIAccessControl
from constants import (
    USER_STATUS_ACTIVE,
    SUPPORTED_SUB_CHANNLES,
)
import context
import error.error_code as ErrorCodes
from error.error import Error
import error.error_msg as ErrorMsg
from log.logger import logger
from utils.json import json_load
from utils.misc import is_str
from api.user.user import get_user

class BaseRequest(object):

    def __init__(self):
        """ This is a base request object
        """
        self.sender = None
        # error message
        self.error = None
        pass

    def __str__(self):
        return ""
    
    def validate(self):
        ''' validate request '''
        return False
    
    def check_api_access(self):
        ''' api access control '''
        acl = APIAccessControl(self.sender)
        action = self.params.get('action', None)
        if not action:
            logger.error("request without action field")
            self.set_error(Error(ErrorCodes.INVALID_REQUEST_FORMAT, ErrorMsg.ERR_MSG_MISSING_PARAMETER, "action"))
            return False
        if not acl.check_access(action):
            logger.error("check api access failed for [%s]" % self.sender)
            self.set_error(acl.get_error())
            return False   
                 
        return True

    def check_sub_channel(self):
        # Avoid breaking the origin params.
        params = copy.deepcopy(self.params)
        sub_channel = params.get("sub_channel", "").strip()

        if sub_channel:
            params = self._build_list_params(params)

            if sub_channel not in SUPPORTED_SUB_CHANNLES:
                logger.error("sub channel unsupported, [%s]" % sub_channel)
                self.set_error(
                    Error(
                        ErrorCodes.INVALID_REQUEST_FORMAT,
                        ErrorMsg.ERR_MSG_UNSUPPORTED_PARAMETER_VALUE,
                        args=("sub_channel", sub_channel)
                    )
                )
                return False

            return False
        return True

    def build_internal_request(self):
        ''' build request in internal format '''
        return None
    
    def get_error(self):
        ''' return the information describing the error occurred
            in validating the request or building the internal request.
        '''
        return self.error
    
    def set_error(self, error):
        ''' set error '''
        self.error = error
        
    def _build_list_params(self, params):
        ''' build list params
            there are two types of list params we need to transform:
            1) list type:
                {'param.1':'val1', 'param.2':'val2', ...} 
                        => {'param':['val1', 'val2', ...]}
            2) dict in list type:
                {'param.1.k1':'v11', 'param.1.k2':'v12', 
                 'param.2.k1':'v21', 'param.2.k2':'v22', ...} 
                        => {'param':[{'k1':'v11', 'k2':'v12'}, {'k1':'v21', 'k2':'v22'}]}
        '''
        list_dict_params = {}    
        for param, value in sorted(params.items()):
            items = param.split('.')
            cnt = len(items)
            if cnt == 1:
                # Ignore the not-list param.
                continue
            elif cnt == 2:
                (list_param, _) = items

                # Ignore the previous-type-not-match param.
                if not isinstance(params.get(list_param, []), list):
                    continue

                if list_param not in params:
                    params[list_param] = []
                params[list_param].append(value)
            elif cnt == 3:
                (list_param, seq, dict_param) = items

                # Ignore the previous-type-not-match param.
                if not isinstance(params.get(list_param, {}), dict):
                    continue

                if list_param not in list_dict_params:
                    list_dict_params[list_param] = {}
                if seq not in list_dict_params[list_param]:
                    list_dict_params[list_param][seq] = {}
                list_dict_params[list_param][seq].update({dict_param:value})
        
        _list_dict_params_ = []
        # build "dict in list" type
        for k, v in list_dict_params.items():
            if k not in params or not isinstance(params[k], list):
                params[k] = []
            if k not in _list_dict_params_:
                _list_dict_params_.append(k)
            for val in v.values():
                params[k].append(val) 
                
        # build "list in dict" type for value
        for p in _list_dict_params_:
            l = params[p]
            for d in l:
                for k, v in d.items():
                    if not is_str(v):
                        continue
                    _v = json_load(v) if v and v[0] in ["["] and v[len(v)-1] in ["]"] else None
                    if _v is not None:
                        d[k] = _v
        return params
    
    def _check_access(self, user_id, zone_id=None):
        ''' check access authority of user
            @return: user info if succeeded and None if failed 
        '''
        ctx = context.instance()
        
        auth_service_id = self.params.get("auth_service")

        ret = get_user(ctx, user_id, zone_id, auth_service_id)
        if isinstance(ret, Error):
            self.set_error(ret)
            return None
        user = ret

        # check if user is disable
        if user["status"] != USER_STATUS_ACTIVE:
            logger.error("user [%s] is not active" % (user_id))
            err = Error(ErrorCodes.USER_IS_NOT_ACTIVE,
                        ErrorMsg.ERR_MSG_USER_STATUS_NO_ACTIVE, user["user_name"])
            self.set_error(err)
            return None

        return user

    def _is_readonly_action(self, action):
        if action.startswith('Describe') or action.startswith('Get'):
            return True
        return False
    
    def _get_params(self, params):
        ''' get not empty params '''
        new_params = {}
        for k, v in params.items():
            new_params[k] = v
        return new_params
    
    def _get_sender(self, user):
        sender = {'owner': user['user_id'],
                  'role': user['role'],
                  'user_name': user['user_name'],
                  'auth_service_id': user.get('auth_service_id', '')
                 }

        return sender
