import context
from log.logger import logger
import constants as const
import db.constants as dbconst
import resource_control.desktop.resource_permission as ResCheck
import resource_control.auth.password_prompt as PwdPrompt
import error.error_code as ErrorCodes    
import error.error_msg as ErrorMsg
from error.error import Error
import api.user.user as APIUser
from common import (
    get_reverse,
    get_sort_key,
    build_filter_conditions,
    return_success, 
    return_error,
    return_items
    )
from utils.json import json_load
import resource_control.user.user as ZoneUser 

def handle_create_password_prompt_question(req):
    ret = ResCheck.check_request_param(req, ["question_content"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    question_content = req.get("question_content")
    ret = PwdPrompt.check_password_prompt_question(question_content)
    if not ret:
        logger.error("password prompt question have exist.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_PASSWORD_PROMPT_QUESTRION_EXIST_ERROR))

    ret = PwdPrompt.create_password_prompt_question(question_content)
    if ret == None:
        logger.error("create password prompt question error.")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_CREATE_PASSWORD_PROMPT_QUESTRION_ERROR))

    rep = {
        "prompt_question_id": ret
        }
    return return_success(req, rep)

def handle_modify_password_prompt_question(req):
    ret = ResCheck.check_request_param(req, ["prompt_question"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    prompt_question_id = req.get("prompt_question")
    question_content = req.get("question_content")
    ret = PwdPrompt.check_password_prompt_question(question_content)
    if not ret:
        logger.error("password prompt question have exist.")
        return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                       ErrorMsg.ERR_MSG_PASSWORD_PROMPT_QUESTRION_EXIST_ERROR))

    ret = PwdPrompt.modify_password_prompt_question(prompt_question_id, question_content)
    if ret == None:
        logger.error("modify password prompt question error.")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_MODIFY_PASSWORD_PROMPT_QUESTRION_ERROR))

    # update answer of this question
    ret = PwdPrompt.update_password_prompt_answer_question(prompt_question_id, question_content)
    if ret == None:
        logger.error("update have answer of this question")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_MODIFY_PASSWORD_PROMPT_QUESTRION_ERROR))

    rep = {
        "prompt_question_id": ret
        }
    return return_success(req, rep)

def handle_delete_password_prompt_question(req):
    prompt_question_ids = req.get("prompt_questions", [])
    if len(prompt_question_ids) == 0:
        return return_success(req, {"prompt_questions": []})

    ret = PwdPrompt.delete_password_prompt_question(prompt_question_ids)
    if not ret:
        logger.error("delete password prompt question error.")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DELETE_PASSWORD_PROMPT_QUESTRION_ERROR))

    # update answer of this question
    for prompt_question_id in prompt_question_ids:
        ret = PwdPrompt.clear_password_prompt_answer_question(prompt_question_id)
        if ret == None:
            logger.error("update have answer of this question")
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                           ErrorMsg.ERR_MSG_MODIFY_PASSWORD_PROMPT_QUESTRION_ERROR))

    rep = {
        "prompt_questions": prompt_question_ids
        }
    return return_success(req, rep)

def handle_describe_password_prompt_question(req):
    ctx = context.instance()
    sender = req["sender"]

    filter_conditions = build_filter_conditions(req, dbconst.TB_PROMPT_QUESTION)
    if "prompt_questions" in req:
        filter_conditions.update({"prompt_question_id": req["prompt_questions"]})
    display_columns = dbconst.PUBLIC_COLUMNS[dbconst.TB_PROMPT_QUESTION]

    prompt_question_set = ctx.pg.get_by_filter(dbconst.TB_PROMPT_QUESTION, filter_conditions, display_columns,
                                     sort_key=get_sort_key(dbconst.TB_PROMPT_QUESTION, req.get("sort_key")),
                                     reverse=get_reverse(req.get("reverse")),
                                     offset=req.get("offset", 0),
                                     limit=req.get("limit", dbconst.DEFAULT_LIMIT))
    if prompt_question_set is None:
        logger.error("describe prompt question failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESCRIBE_PASSWORD_PROMPT_QUESTRION_ERROR))

    #format values for normal console
    if APIUser.is_normal_console(sender):
        prompt_answers = ctx.pgm.get_user_password_prompt_answers(sender["owner"])
        if prompt_answers:
            for prompt_question_id, prompt_question in prompt_question_set.items():
                if prompt_question_id in prompt_answers.keys():
                    prompt_question["status"] = const.PASSWORD_PORMPT_STATUS_FINISHED
                    prompt_question["prompt_answer_id"] = prompt_answers[prompt_question_id]["prompt_answer_id"]
                else:
                    prompt_question["status"] = const.PASSWORD_PORMPT_STATUS_UNFINISHED

    #format values for admin console

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_PROMPT_QUESTION, filter_conditions)
    if total_count is None:
        logger.error("get prompt question count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    rep = {'total_count':total_count}

    return return_items(req, prompt_question_set, "prompt_question", **rep)

def handle_create_password_prompt_answer(req):
    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["user_name", "prompt_question", "answer_content"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    user_name = req.get("user_name")
    user_id = ctx.pgm.get_user_id_by_user_name(user_name, zone_id=sender["zone"])
    if user_id != sender["owner"]:
        logger.error("user only can set question of yourself.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED))

    prompt_question_id = req.get("prompt_question")
    answer_content = req.get("answer_content")

    answers = ctx.pgm.get_user_password_prompt_answers(user_id)
    if answers:
        if prompt_question_id in answers.keys():
            logger.error("this question [%s] have answer with this user [%s]" % (prompt_question_id, user_id))
            return return_error(req, Error(ErrorCodes.INVALID_REQUEST_PARAM_VALUE,
                                           ErrorMsg.ERR_MSG_PASSWORD_PROMPT_QUESTRION_HAVE_USER_ANSWER_ERROR))

    question_content = ctx.pgm.get_prompt_question_content(prompt_question_id)
    ret = PwdPrompt.create_password_prompt_answer(user_id, prompt_question_id, question_content, answer_content)
    if ret == None:
        logger.error("create password prompt answer error.")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_CREATE_PASSWORD_PROMPT_ANSWER_ERROR))

    # check answer number
    prompt_answer_number = ctx.pgm.get_password_prompt_answer(user_id)
    system_custom_cfg = ctx.pgm.get_system_custom_configs(system_custom_ids=const.REDEFINE_SYSTEM_CUSTOM,
                                                          module_type=const.CUSTOM_MODULE_TYPE_PASSWORD_RESTORE)
    security_question_policy_min_number = system_custom_cfg.get("security_question_policy_min_number")
    if prompt_answer_number >= int(security_question_policy_min_number["item_value"]):
        attrs = {"password_protect": 1}
        ZoneUser.modify_desktop_user(user_id, attrs)

    rep = {
        "prompt_answer_id": ret
        }
    return return_success(req, rep)

def handle_modify_password_prompt_answer(req):
    ctx = context.instance()
    sender = req["sender"]
    ret = ResCheck.check_request_param(req, ["prompt_answer"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    prompt_answer_id = req.get("prompt_answer")
    prompt_answer = ctx.pgm.get_user_password_prompt_answer(prompt_answer_id)
    if not prompt_answer:
        logger.error("prompt answer [%s] not found." % prompt_answer_id)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_CODE_MSG_RESOURCE_NOT_FOUND))

    if prompt_answer["user_id"] != sender["owner"]:
        logger.error("user can not modify other user prompt answer.")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_CODE_MSG_PERMISSION_DENIED))

    answer_content = req.get("answer_content")
    ret = PwdPrompt.modify_password_prompt_answer(prompt_answer_id, answer_content)
    if not ret:
        logger.error("modify promtp answer error.")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_MODIFY_PASSWORD_PROMPT_ANSWER_ERROR))

    rep = {
        "prompt_answer_id": prompt_answer_id
        }
    return return_success(req, rep)


def handle_delete_password_prompt_answer(req):
    ctx = context.instance()
    sender = req["sender"]

    prompt_answer_ids = req.get("prompt_answers", [])
    if len(prompt_answer_ids) == 0:
        return return_success(req, {"prompt_answers": []})

    for prompt_answer_id in prompt_answer_ids:
        prompt_answer = ctx.pgm.get_user_password_prompt_answer(prompt_answer_id)
        if prompt_answer is None:
            prompt_answer_ids.remove(prompt_answer_ids)
            continue
        if prompt_answer.get("user_id") != sender["owner"]:
            logger.error("user can not delete other user prompt answer.")
            return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                           ErrorMsg.ERR_MSG_DELETE_PASSWORD_PROMPT_QUESTRION_ERROR))

    ret = PwdPrompt.delete_password_prompt_answer(prompt_answer_ids)
    if not ret:
        logger.error("delete password prompt question error.")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_DELETE_PASSWORD_PROMPT_QUESTRION_ERROR))

    # check answer number
    user_id = sender["owner"]
    prompt_answer_number = ctx.pgm.get_password_prompt_answer(user_id)
    system_custom_cfg = ctx.pgm.get_system_custom_configs(system_custom_ids=const.REDEFINE_SYSTEM_CUSTOM,
                                                          module_type=const.CUSTOM_MODULE_TYPE_PASSWORD_RESTORE)
    security_question_policy_min_number = system_custom_cfg.get("security_question_policy_min_number")
    if prompt_answer_number < int(security_question_policy_min_number["item_value"]):
        attrs = {
            "password_protect": 0,
            "security_question": 0
            }
        ZoneUser.modify_desktop_user(user_id, attrs)

    rep = {
        "prompt_answers": prompt_answer_ids
        }
    return return_success(req, rep)

def handle_describe_password_prompt_have_answer(req):
    ctx = context.instance()
    ret = ResCheck.check_request_param(req, ["user_name"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    sender = req["sender"]
    user_name = req["user_name"]
    if '@' in user_name:
        user_name = user_name.split('@')[0]
    
    user_id = None
    user_role = sender["role"]
    if user_role == const.USER_ROLE_NORMAL:
        user_id = sender["owner"]

    if not user_id:
        user_id = ctx.pgm.get_user_id_by_user_name(user_name, zone_id=sender["zone"])
        if not user_id:
            rep = {'total_count': 0}
            return return_items(req, None, "prompt_answer", **rep)

    filter_conditions = {}
    filter_conditions.update({"user_id": user_id})
    display_columns = ["prompt_answer_id", "question_content", "user_id"]

    prompt_answer_set = ctx.pg.get_by_filter(dbconst.TB_PROMPT_ANSWER, filter_conditions, display_columns,
                                     sort_key=get_sort_key(dbconst.TB_PROMPT_QUESTION, req.get("sort_key")),
                                     reverse=get_reverse(req.get("reverse")),
                                     offset=req.get("offset", 0),
                                     limit=req.get("limit", dbconst.DEFAULT_LIMIT))
    if prompt_answer_set is None:
        logger.error("describe prompt answer failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESCRIBE_PASSWORD_PROMPT_QUESTRION_ERROR))

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_PROMPT_ANSWER, filter_conditions)
    if total_count is None:
        logger.error("get prompt answer count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    rep = {'total_count':total_count}
    return return_items(req, prompt_answer_set, "prompt_answer", **rep)

def handle_check_password_prompt_answer(req):
    sender = req["sender"]

    ret = ResCheck.check_request_param(req, ["json_answers"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    if APIUser.is_admin_console(sender):
        logger.error("prompt answer can be checked by normal console.")
        return return_error(req, Error(ErrorCodes.PERMISSION_DENIED))

    json_answers = req.get("json_answers", "")
    prompt_answers = json_load(json_answers)

    ret = PwdPrompt.chech_password_prompt_answer(prompt_answers)
    if not ret:
        logger.error("check password prompt answer is error.")
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_CHECK_PASSWORD_PROMPT_ANSWER_ERROR))

    # modify reset password flag
    user_id = sender["owner"]
    ret = ZoneUser.modify_desktop_user_reset_password_flag(user_id, const.FLAG_ENABLE_USER_RESET_PASSWORD)
    if not ret:
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_RESET_PASSWORD_FLAG_ERROR))

    return return_success(req, {})

def handle_describe_have_password_answer_users(req):
    ctx = context.instance()

    filter_conditions = build_filter_conditions(req, dbconst.TB_DESKTOP_USER)
    filter_conditions["password_protect"] = 1
    filter_conditions["status"] = "active"
    if "user_name" in req:
        filter_conditions.update({"user_name": req["user_name"]})

    display_columns = dbconst.PUBLIC_COLUMNS[dbconst.TB_DESKTOP_USER]
    desktop_user_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_USER, filter_conditions, display_columns,
                                         sort_key=get_sort_key(dbconst.TB_DESKTOP_USER, req.get("sort_key")),
                                         reverse=get_reverse(req.get("reverse")),
                                         offset=req.get("offset", 0),
                                         limit=req.get("limit", dbconst.DEFAULT_LIMIT))
    if desktop_user_set is None:
        logger.error("describe have password user failed [%s]" % req)
        rep = {'total_count': 0}
        rep["user_set"] = []
        return return_success(req, rep)

    # get total count
    total_count = ctx.pg.get_count(dbconst.TB_DESKTOP_USER, filter_conditions)
    if total_count is None:
        logger.error("describe have password user failed count failed [%s]" % req)
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR, 
                                       ErrorMsg.ERR_MSG_DESC_RESOURCE_FAILED))
    rep = {'total_count': total_count}
    return return_items(req, desktop_user_set, "user", **rep)

def handle_ignore_password_prompt_question(req):
    ret = ResCheck.check_request_param(req, ["user", "security_question"])
    if isinstance(ret, Error):
        return return_error(req, ret)

    user_id = req.get("user")
    security_question = req.get("security_question")

    ret = ZoneUser.modify_desktop_user_security_question_flag(user_id, security_question)
    if not ret:
        return return_error(req, Error(ErrorCodes.INTERNAL_ERROR,
                                       ErrorMsg.ERR_MSG_SET_SECURITY_QUESTION_FLAG_ERROR))
    rep = {"user_id": user_id}
    return return_success(req, rep)
