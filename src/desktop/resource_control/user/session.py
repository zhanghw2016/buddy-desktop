'''
Created on 2012-10-17

@author: yunify
'''
import context
import constants as const
from utils.id_tool import alloc_session_id
from mc.constants import MC_KEY_PREFIX_SESSOIN_KEY, MC_KEY_PREFIX_SESSOIN_KEY_LIST
from log.logger import logger
import api.user.user as APIUser
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from utils.auth import check_password
import resource_control.auth.radius as Radius

def check_session_radius_auth(sender, auth_user):
    
    if APIUser.is_global_admin_user(sender):
        return None

    ret = Radius.check_radius_user(auth_user)
    if not ret:
        return None
    
    return ret

def check_session_user(sender, user_name):
    ctx = context.instance()
    owner = sender["owner"]
    zones = ctx.zones
    default_zone = ''
    if zones:
        default_zone = zones.keys()[0]
    
    user = {
        "user_name": sender["user_name"],
        "user_id": sender["user_id"],
        "auth_service_id": sender.get("auth_service_id"),
        "zone": sender["zone"] if sender["zone"] else default_zone,
        "role": sender["role"]
        }
    
    sender_user_name = sender["user_name"]
    if "domain" in sender:
        sender_user_name = "%s@%s" % (sender_user_name, sender["domain"])           
    
    if user_name == sender_user_name:
        return user
    
    ret = APIUser.get_user(ctx, user_name)
    if isinstance(ret, Error):
        return ret

    user = ret
    if owner != user["user_id"]:
        logger.error("create session, user %s dont match owner %s" % (user["user_id"], owner))
        return Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                     ErrorMsg.ERR_MSG_INVALID_PARAMETER_VALUE, user_name)
    
    if user["status"] != const.USER_STATUS_ACTIVE:
        logger.error("user %s status %s cant create session" % (user_name, user["status"]))
        return Error(ErrorCodes.USER_IS_NOT_ACTIVE, 
                     ErrorMsg.ERR_MSG_USER_STATUS_NO_ACTIVE)
    
    return user

def check_session_user_login(sender, user, user_name, auth_service_id, password):
    
    ctx = context.instance()
    zone_id = user["zone"]
    user_id = sender["owner"]
    if APIUser.is_global_admin_user(sender):
        
        user_id = user["user_id"]       
        global_users = ctx.pgm.get_global_admin_user(user_id)
        if not global_users:
            logger.error("global user %s no found" % (user_name))
            return Error(ErrorCodes.USER_NAME_ERROR,
                    ErrorMsg.ERR_MSG_USER_NO_FOUND, user_name)
        global_user = global_users[user_id]
        
        ret = ctx.auth.check_user_change_password(global_user)
        if isinstance(ret, Error):
            return ret
        
        if not check_password(password, global_user["password"]):
            logger.error("check user session password %s fail" % (user_id))
            return Error(ErrorCodes.PASSWD_NOT_MATCHED,
                         ErrorMsg.ERR_CODE_MSG_USER_NOT_FOUND_OR_PASSWD_NOT_MATCHED)

        return user
        
    ret = ctx.auth.get_auth_users(auth_service_id, user_names=user_name)
    if isinstance(ret, Error):
        return ret

    if not ret:
        logger.error("check user session no found auth user %s, %s" % (auth_service_id, user_name))
        return Error(ErrorCodes.RESOURCE_NOT_FOUND, 
                     ErrorMsg.ERR_MSG_ZONE_NO_CONFIG_AUTH_SERVICE, zone_id)
    
    auth_user = ret[user_name]

    ret = ctx.auth.auth_login(auth_service_id, user_name, password)
    if isinstance(ret, Error):
        return ret
    
    if "auth_service_id" not in auth_user:
        auth_user["auth_service_id"] = auth_service_id

    
    auth_user["user_id"] = user_id
  
    ret = ctx.auth.check_user_change_password(auth_user)
    if isinstance(ret, Error):
        return ret

    return auth_user

def create_session(user_id, session_type="web"):
    ''' create session for user
        @param session_type: 'web' or 'mobile', each type has different expiration time

        @return session key or None.
    '''
    ctx = context.instance()
    expired_time = ctx.session_expired_time
    value = '%s:%s' % (user_id, expired_time)
    count = 0
    while count < 2:
        sk = alloc_session_id()
        if ctx.mcm.set(MC_KEY_PREFIX_SESSOIN_KEY, sk, value, expired_time):
            add_session_to_list(user_id, sk)
            logger.debug("alloc session key [%s] for [%s]" % (sk, user_id))
            return sk
        count += 1
    return None

def refresh_session(sk):
    ''' refresh the existence of session key '''
    # get session key
    ctx = context.instance()
    value = ctx.mcm.get(MC_KEY_PREFIX_SESSOIN_KEY, sk)
    if value is None:
        return False

    user_id = value.split(':')[0]
    expired_time = ctx.session_expired_time
    if ctx.mcm.set(MC_KEY_PREFIX_SESSOIN_KEY, sk, value, expired_time):
        add_session_to_list(user_id, sk)
        return True
    logger.error("refresh session key [%s] for [%s] error." % (sk, user_id))
    return False

def check_session(sk):
    ''' check the existence of session key
        @return user_id of the session key or None.
    '''
    # get session key
    ctx = context.instance()
    
    
    value = ctx.mcm.get(MC_KEY_PREFIX_SESSOIN_KEY, sk)
    if value is None:
        return None
    user_id = value.split(':')[0]
    return user_id

def renew_session(sk, user_id, session_type="web"):
    ''' renew session key
        @return True if renew ok and False if failed
    '''
    ctx = context.instance()
    if session_type == 'mobile':
        expired_time = ctx.app_session_expired_time
    else:
        expired_time = ctx.session_expired_time
    # use prev expired time if exists
    value = ctx.mcm.get(MC_KEY_PREFIX_SESSOIN_KEY, sk)
    if value:
        parts = value.split(':')
        if len(parts) == 2:
            expired_time = int(parts[1])

    value = '%s:%s' % (user_id, expired_time)
    if ctx.mcm.set(MC_KEY_PREFIX_SESSOIN_KEY, sk, value, expired_time):
        add_session_to_list(user_id, sk)
        logger.debug("renew session key [%s] for [%s]" % (sk, user_id))
        return True
    return False

def delete_session(sk):
    ''' delete session key
        @return True on success and False on failed.
    '''
    ctx = context.instance()

    ctx.mcm.get(MC_KEY_PREFIX_SESSOIN_KEY, sk)

    if not ctx.mcm.delete(MC_KEY_PREFIX_SESSOIN_KEY, sk):
        logger.error("delete session key [%s] failed" % (sk))
        return False

    return True

def add_session_to_list(user_id, sk):
    ctx = context.instance()
    sk_list = ctx.mcm.get(MC_KEY_PREFIX_SESSOIN_KEY_LIST, user_id) or ''

    sk_list = sk_list.split(',')
    if sk and sk not in sk_list:
        sk_list.append(sk)

    if len(sk_list) > 10:
        sk_list = [k for k in sk_list if ctx.mcm.get(MC_KEY_PREFIX_SESSOIN_KEY, k)]

    logger.debug("current session key list is [%s]", sk_list)
    sk_list = ','.join(sk_list)
    expired_time = ctx.session_expired_time
    ctx.mcm.set(MC_KEY_PREFIX_SESSOIN_KEY_LIST, user_id, sk_list, expired_time)

def clear_user_sessions(user_id):
    ''' clear all current session keys
    '''
    ctx = context.instance()
    sk_list = ctx.mcm.get(MC_KEY_PREFIX_SESSOIN_KEY_LIST, user_id)
    if not sk_list:
        return

    for sk in sk_list.split(','):
        ctx.mcm.delete(MC_KEY_PREFIX_SESSOIN_KEY, sk)
