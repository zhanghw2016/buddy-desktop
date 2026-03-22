'''
Created on 2017-3-23
@author: yunify
'''
from log.logger import logger
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
from common import (
    return_success, return_error
)
import context
from resource_control.user.session import (
       create_session,
       delete_session,
       check_session
)
import constants as const
import resource_control.desktop.resource_permission as ResCheck
import resource_control.user.session as Session
import resource_control.user.user as ZoneUser
import api.auth.auth_const as AuthConst
import resource_control.auth.auth_user as AuthUser

def handle_create_desktop_user_session(req):

    ctx = context.instance()
    # check must parameters
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ['user_name', 'password'])
    if isinstance(ret, Error):
        return return_error(req, ret)

    password = req['password']
    user_name = req['user_name']
    session_type = req.get('session_type', 'web')
    client_ip = req.get('client_ip', '127.0.0.1')

    ret = Session.check_session_user(sender, user_name)
    if isinstance(ret, Error):
        user_id = ctx.pgm.get_user_id_by_user_name(user_name)
        if user_id:
            ZoneUser.create_user_login_record(user_id, sender["zone"], client_ip, status=const.LOGIN_STATUS_FAIL, errmsg="User Not Existed")
        return return_error(req, ret)

    user = ret
    user_id = user["user_id"]
    user_name = user["user_name"]

    lock_time_dict = {}
    auth_service_id = user.get('auth_service_id')
    if not auth_service_id:
        desktop_users = ctx.pgm.get_desktop_users(user_id)
        if desktop_users:
            desktop_user = desktop_users[user_id]
            auth_service_id = desktop_user["auth_service_id"]

    ret = AuthUser.check_auth_user_password(sender, user, auth_service_id, lock_time_dict)
    if isinstance(ret, Error):
        ZoneUser.create_user_login_record(user_id, sender["zone"], client_ip, status=const.LOGIN_STATUS_FAIL, errmsg=ret.get_message(lang=const.EN))
        lock_time = lock_time_dict.get("lock_time")
        if ret.get_code() == AuthConst.ERROR_CODE_HEX_MAP[AuthConst.ERROR_ACCOUNT_LOCKED_OUT] and lock_time:
            return return_error(req, ret, lock_time=lock_time, auth_service_id=auth_service_id)

        return return_error(req, ret, auth_service_id=auth_service_id)

    # check user login
    ret = Session.check_session_user_login(sender, user, user_name, auth_service_id, password)
    if isinstance(ret, Error):
        ZoneUser.create_user_login_record(user_id, sender["zone"], client_ip, status=const.LOGIN_STATUS_FAIL, errmsg=ret.get_message(lang=const.EN))
        if ret.get_code() == AuthConst.ERROR_CODE_HEX_MAP[AuthConst.ERROR_PASSWORD_MUST_CHANGE]:

            return return_error(req, ret, zone=sender["zone"], auth_service_id=auth_service_id, user_id=sender["owner"])

        return return_error(req, ret, auth_service_id=auth_service_id)
    
    auth_user = ret
    
    rep = {}

    # check radius auth
    ret = Session.check_session_radius_auth(sender, auth_user)
    if ret:
        rep = {"check_radius": True, "user_id": user_id}
        return return_success(req, rep)

    # create session
    ret = create_session(user_id, session_type)
    if not ret:
        ZoneUser.create_user_login_record(user_id, sender["zone"], client_ip, status=const.LOGIN_STATUS_FAIL, errmsg="Create Session Error")
        return return_error(req, Error(ErrorCodes.SESSION_EXPIRED), auth_service_id=auth_service_id)

    # record user login
    ZoneUser.create_user_login_record(user_id, sender["zone"], client_ip)

    rep["sk"] = ret
    rep["zone"] = user["zone"]

    if user_id==const.GLOBAL_ADMIN_USER_ID or ctx.pgm.check_ignore_security_question(user_id):
        rep["security_question"] = 0
        return return_success(req, rep)

    rep["security_question"] = 0
    # system_custom_cfg = ctx.pgm.get_system_custom_configs(system_custom_ids=const.REDEFINE_SYSTEM_CUSTOM,
    #                                                                   module_type=const.CUSTOM_MODULE_TYPE_PASSWORD_RESTORE)
    # if system_custom_cfg:
    #     if system_custom_cfg.get("support_user_password_restore"):
    #         support_user_password_restore = system_custom_cfg.get("support_user_password_restore")
    #         security_question_policy_min_number = system_custom_cfg.get("security_question_policy_min_number")
    #         security_question_policy = system_custom_cfg.get("security_question_policy")
    #         if support_user_password_restore and int(support_user_password_restore["item_value"])==1:
    #             if security_question_policy and security_question_policy["item_value"] == "force":
    #                 if security_question_policy_min_number and int(security_question_policy_min_number["item_value"])>0:
    #                     prompt_answer_number = ctx.pgm.get_password_prompt_answer(user_id)
    #                     if prompt_answer_number < int(security_question_policy_min_number["item_value"]):
    #                         rep["security_question"] = 1
    #                         password_prompt_questions = ctx.pgm.get_password_prompt_questions()
    #                         if password_prompt_questions is None:
    #                             rep["security_question"] = 0
    #                         else:
    #                             if len(password_prompt_questions) < int(security_question_policy_min_number["item_value"]):
    #                                 rep["security_question"] = 0

    return return_success(req, rep)

def handle_delete_desktop_user_session(req):
    # check must parameters
    for param in ['sk']:
        if param not in req or not req[param]:
            logger.error("[%s] not found in this request" % param)
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                                           ErrorMsg.ERR_MSG_MISSING_PARAMETER, param))

    sk = None
    rep = {}
    if req.get('sk', ''):
        sk = req['sk']

    ret = delete_session(sk)
    if not ret:
        return return_error(req, Error(ErrorCodes.SESSION_EXPIRED))

    rep['result'] = 'ok'
    return return_success(req, rep)

def handle_check_desktop_user_session(req):

    # check must parameters
    for param in ['sk']:
        if param not in req or not req[param]:
            logger.error("[%s] not found in this request" % param)
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_FORMAT, 
                                           ErrorMsg.ERR_MSG_MISSING_PARAMETER, param))
    sender = req["sender"]
    sk = None
    rep = {}
    if req.get('sk', ''):
        sk = req['sk']

    ret = check_session(sk)
    if not ret:
        return return_error(req, Error(ErrorCodes.SESSION_EXPIRED))

    rep['user_id'] = ret
    rep["zone"] = sender["zone"]
    
    return return_success(req, rep)

