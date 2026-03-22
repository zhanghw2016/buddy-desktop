'''
Created on 2012-6-26

@author: yunify
'''
import context
import error.error_code as ErrorCodes
import error.error_msg as ErrorMsg
from error.error import Error
from log.logger import logger
from utils.misc import is_str
from common import is_global_admin_user, is_console_admin_user, is_citrix_platform
from constants import (
    ACTION_VDI_WHITE_LIST, 
    ACTION_VDI_ADMIN_WHITE_LIST, 
    ACTION_VDI_DENY_CITRIX,
    CHECK_PLATFROM,
    PLATFROM_CITRIX,
    PLATFROM_QINGDESKTOP
)
from request.consolidator.policy_group.acl import POLICCY_GROUP_API_ACL
from request.consolidator.security_policy.acl import SECURITY_POLICY_API_ACL
from request.consolidator.zone.acl import ZONE_API_ACL
from request.consolidator.auth.acl import AUTH_API_ACL
from request.consolidator.user.acl import DESKTOP_USER_API_ACL
from request.consolidator.citrix.acl import CITRIX_API_ACL
from request.consolidator.system.acl import SYSTEM_API_ACL
from request.consolidator.snapshot.acl import SNAPSHOT_API_ACL
from request.consolidator.terminal.acl import TERMINAL_API_ACL
from request.consolidator.module_custom.acl import MODULE_CUSTOM_API_ACL
from request.consolidator.system_custom.acl import SYSTEM_CUSTOM_API_ACL
from request.consolidator.desktop_service_management.acl import DESKTOP_SERVICE_MANAGEMENT_API_ACL
from request.consolidator.apply_approve.acl import APPLY_APPROVE_API_ACL
from request.consolidator.workflow.acl import WORKFLOW_API_ACL
from request.consolidator.component_version.acl import COMPONENT_VSERION_API_ACL
from request.consolidator.file_share.acl import FILE_SHARE_API_ACL
from request.consolidator.citrix_policy.acl import CITRIX_POLICY_API_ACL
from api.limit.api_limit import check_api_limit 
class APIAccessControl(object):
    ''' each user role will have a corresponding api access list '''
    
    API_ACL = {}
    def __init__(self, sender):
        '''
        @param sender - the info of the sender of the request
        '''
        self.sender = sender
        self.role = sender['role']
        self.channel = sender['channel']
        # error message
        self.error = Error(ErrorCodes.PERMISSION_DENIED)
        self.API_ACL.update(POLICCY_GROUP_API_ACL)
        self.API_ACL.update(SECURITY_POLICY_API_ACL)
        self.API_ACL.update(ZONE_API_ACL)
        self.API_ACL.update(AUTH_API_ACL)
        self.API_ACL.update(DESKTOP_USER_API_ACL)
        self.API_ACL.update(CITRIX_API_ACL)
        self.API_ACL.update(SYSTEM_API_ACL)
        self.API_ACL.update(SNAPSHOT_API_ACL)
        self.API_ACL.update(TERMINAL_API_ACL)
        self.API_ACL.update(MODULE_CUSTOM_API_ACL)
        self.API_ACL.update(SYSTEM_CUSTOM_API_ACL)
        self.API_ACL.update(DESKTOP_SERVICE_MANAGEMENT_API_ACL)
        self.API_ACL.update(APPLY_APPROVE_API_ACL)
        self.API_ACL.update(WORKFLOW_API_ACL)
        self.API_ACL.update(COMPONENT_VSERION_API_ACL)
        self.API_ACL.update(FILE_SHARE_API_ACL)
        self.API_ACL.update(CITRIX_POLICY_API_ACL)
        
    def get_error(self):
        ''' return the information describing the error occurred
            in Request Builder.
        '''
        return self.error

    def set_error(self, code, msg=None, args=None):
        ''' set error '''
        self.error = Error(code, msg, args)
    
    def check_platform(self, zone_id, action):

        ctx = context.instance()
        platforms = self.API_ACL[action][CHECK_PLATFROM]

        platform = PLATFROM_QINGDESKTOP
        if is_citrix_platform(ctx, zone_id):
            platform = PLATFROM_CITRIX

        if platform not in platforms:
            return False
        
        return True
    
    def check_access(self, action):
        ''' check api access '''

        ctx = context.instance()
        
        if action is None:
            logger.error("action can not be None")
            self.set_error(ErrorCodes.INVALID_REQUEST_FORMAT,
                           ErrorMsg.ERR_MSG_MISSING_PARAMETER, "action")
            return False

        if not is_str(action):
            logger.error("illegal action [%s] of sender [%s]" % (
                action, self.sender))
            self.set_error(ErrorMsg.ERR_MSG_PARAMETER_SHOULD_BE_STR, "action")
            return False
        
        ret = check_api_limit(ctx, action)
        if not ret:
            logger.error("api action %s access exceed max limit" % action)
            self.set_error(ErrorCodes.PERMISSION_DENIED,
                               ErrorMsg.ERR_MSG_API_ACCESS_EXCEED_MAX_LIMIT, action)
            return False
       
        if action in self.API_ACL:
            if self.channel not in self.API_ACL[action]:
                logger.error("can not handle action [%s] through channel [%s] for sender [%s]" % (
                    action, self.channel, self.sender))
                self.set_error(ErrorCodes.PERMISSION_DENIED,
                               ErrorMsg.ERR_MSG_CAN_NOT_HANDLE_REQUEST)
                return False
    
            if self.role not in self.API_ACL[action][self.channel]:
                logger.error("can not handle action [%s] for role [%s], sender [%s]" % (
                    action, self.role, self.sender))
                self.set_error(ErrorCodes.PERMISSION_DENIED,
                               ErrorMsg.ERR_MSG_CAN_NOT_HANDLE_REQUEST)
                return False
            
            if not self.check_platform(self.sender["zone"], action):
                logger.error("can not handle action [%s] dismatch platform, sender [%s]" % (
                    action, self.sender))
                self.set_error(ErrorCodes.PERMISSION_DENIED,
                               ErrorMsg.ERR_MSG_CAN_NOT_HANDLE_REQUEST)
            
        else:
            if is_citrix_platform(ctx, self.sender["zone"]):
                if action in ACTION_VDI_DENY_CITRIX:
                    return False
                
            if is_global_admin_user(self.sender):
                return True
    
            if is_console_admin_user(self.sender) and action in ACTION_VDI_ADMIN_WHITE_LIST:
                return True
    
            if action in ACTION_VDI_WHITE_LIST:
                return True

        return True
