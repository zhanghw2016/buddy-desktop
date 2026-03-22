from log.logger import logger
import context
import constants as const
import db.constants as dbconst
from utils.id_tool import (
    UUID_TYPE_PROMPT_QUESTION,
    UUID_TYPE_PROMPT_ANSWER, 
    get_uuid,
)
from utils.misc import get_current_time
import resource_control.user.user as DesktopUser 

def check_password_prompt_question(question_content):
    if not question_content:
        logger.error("question_content is NULL")
        return None

    ctx = context.instance()
    conds = {
        "question_content": question_content
        }
    if not ctx.pg.base_get(dbconst.TB_PROMPT_QUESTION, conds):
        return True
    return False

def create_password_prompt_question(question_content):
    if not question_content:
        logger.error("question_content is NULL")
        return None

    ctx = context.instance()
    curtime = get_current_time(to_seconds=False)
    prompt_question_id = get_uuid(UUID_TYPE_PROMPT_QUESTION,
                                  ctx.checker, 
                                  long_format=True)

    prompt_question = {}
    prompt_question['prompt_question_id'] = prompt_question_id
    prompt_question['create_time'] = curtime
    prompt_question['question_content'] = question_content

    if not ctx.pg.insert(dbconst.TB_PROMPT_QUESTION, prompt_question):
        logger.error("create prompt question [%s] failed." % (prompt_question))
        return None
    return prompt_question_id

def modify_password_prompt_question(prompt_question_id, question_content):
    if not prompt_question_id:
        logger.error("prompt_question_id is NULL")
        return None

    ctx = context.instance()
    conds = {"prompt_question_id": prompt_question_id}
    prompt_question = {}
    if question_content:
        prompt_question['question_content'] = question_content
    if len(prompt_question) == 0:
        return prompt_question_id

    if ctx.pg.base_update(dbconst.TB_PROMPT_QUESTION, conds, prompt_question) < 0:
        logger.error("modify prompt question [%s] failed." % (prompt_question_id))
        return None
    return prompt_question_id

def delete_password_prompt_question(prompt_question_ids):
    if not prompt_question_ids:
        return True

    ctx = context.instance()
    conds = {"prompt_question_id": prompt_question_ids}

    if not ctx.pg.base_delete(dbconst.TB_PROMPT_QUESTION, conds):
        logger.error("delete prompt question [%s] failed." % (prompt_question_ids))
        return False
    return prompt_question_ids

def create_password_prompt_answer(user_id, prompt_question_id, question_content, answer_content):
    if not user_id or not answer_content or not answer_content or not question_content:
        logger.error("user_id, prompt_question or prompt_question or question_content is NULL")
        return None

    ctx = context.instance()
    curtime = get_current_time(to_seconds=False)
    prompt_answer_id = get_uuid(UUID_TYPE_PROMPT_ANSWER,
                                  ctx.checker, 
                                  long_format=True)

    prompt_answer = {}
    prompt_answer['prompt_answer_id'] = prompt_answer_id
    prompt_answer['prompt_question_id'] = prompt_question_id
    prompt_answer['create_time'] = curtime
    prompt_answer['user_id'] = user_id
    prompt_answer['answer_content'] = answer_content
    prompt_answer['question_content'] = question_content

    if not ctx.pg.insert(dbconst.TB_PROMPT_ANSWER, prompt_answer):
        logger.error("create prompt answer [%s] failed." % (prompt_answer))
        return None
    return prompt_answer_id

def modify_password_prompt_answer(prompt_answer_id, answer_content):
    if not prompt_answer_id:
        logger.error("prompt_question_id is NULL")
        return None

    ctx = context.instance()
    conds = {"prompt_answer_id": prompt_answer_id}
    prmpt_answer = {}
    prmpt_answer['answer_content'] = answer_content

    if ctx.pg.base_update(dbconst.TB_PROMPT_ANSWER, conds, prmpt_answer) < 0:
        logger.error("modify prompt answer [%s] failed." % (prompt_answer_id))
        return None
    return prompt_answer_id

def update_password_prompt_answer_question(prompt_question_id, question_content):
    if not prompt_question_id:
        logger.error("prompt_question_id is NULL")
        return None
    if not question_content:
        logger.error("question_content is NULL")
        return None

    ctx = context.instance()
    conds = {"prompt_question_id": prompt_question_id}
    prmpt_answer = {"question_content": question_content}

    if ctx.pg.base_update(dbconst.TB_PROMPT_ANSWER, conds, prmpt_answer) < 0:
        logger.error("modify prompt answer prompt_question_id:[%s], question_content:[%s]failed." % (prompt_question_id, question_content))
        return None
    return prompt_question_id

def clear_password_prompt_answer_question(prompt_question_id):
    if not prompt_question_id:
        logger.error("prompt_question_id is NULL")
        return None

    ctx = context.instance()
    conds = {"prompt_question_id": prompt_question_id}
    prmpt_answer = {}
    prmpt_answer['prompt_question_id'] = ''

    if ctx.pg.base_update(dbconst.TB_PROMPT_ANSWER, conds, prmpt_answer) < 0:
        logger.error("modify prompt answer [%s] failed." % (prompt_question_id))
        return None
    return prompt_question_id

def delete_password_prompt_answer(prompt_answer_ids):
    if not prompt_answer_ids:
        return True

    ctx = context.instance()
    conds = {"prompt_answer_id": prompt_answer_ids}

    if not ctx.pg.base_delete(dbconst.TB_PROMPT_ANSWER, conds):
        logger.error("delete prompt answer [%s] failed." % (prompt_answer_ids))
        return False
    return prompt_answer_ids

def chech_password_prompt_answer(prompt_answers):
    if not prompt_answers or len(prompt_answers) < const.MIN_CHECK_PORMPT_ANSWER_SIZE:
        logger.error("prompt_answers is invalid")
        return False

    check_success_times = 0
    ctx = context.instance()
    
    for prompt_answer in prompt_answers:
        prompt_answer_id = prompt_answer["prompt_answer_id"]
        real_answer = ctx.pgm.get_user_password_prompt_answer(prompt_answer_id)
        if not real_answer:
            continue

        if real_answer["answer_content"] == prompt_answer["answer_content"]:
            check_success_times = check_success_times + 1

    system_custom_cfg = ctx.pgm.get_system_custom_configs(system_custom_ids=const.REDEFINE_SYSTEM_CUSTOM,
                                                                      module_type=const.CUSTOM_MODULE_TYPE_PASSWORD_RESTORE)
    if system_custom_cfg:
        if system_custom_cfg.get("support_user_password_restore"):
            security_question_policy_check_number = system_custom_cfg.get("security_question_policy_check_number")
            if security_question_policy_check_number:
                security_question_policy_check_number_value = int(security_question_policy_check_number["item_value"])
                if check_success_times >= security_question_policy_check_number_value:
                    return True

    return False

def update_have_password_answer_users():
    ctx = context.instance()
    system_custom_cfg = ctx.pgm.get_system_custom_configs(system_custom_ids=const.REDEFINE_SYSTEM_CUSTOM,
                                                          module_type=const.CUSTOM_MODULE_TYPE_PASSWORD_RESTORE)

    security_question_policy_min_number = system_custom_cfg.get("security_question_policy_min_number")
    if security_question_policy_min_number:
        security_question_policy_min_number = int(security_question_policy_min_number["item_value"])

    filter_conditions = {}
    offset = 0
    limit = 1000
    total_count = ctx.pg.get_count(dbconst.TB_DESKTOP_USER, filter_conditions)
    while total_count-limit>0:
        desktop_user_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_USER, 
                                                filter_conditions, 
                                                offset=offset, 
                                                limit=limit)
        if desktop_user_set is None:
            logger.error("describe desktop user failed , condition: [%s]" % filter_conditions)
            return None
        for _,desktop_user in desktop_user_set.items():
            user_id = desktop_user.get("user_id")
            if not user_id:
                continue
            password_protect = desktop_user.get("password_protect", 0)
            prompt_answer_number = ctx.pgm.get_password_prompt_answer(user_id)
            if security_question_policy_min_number>0:
                if prompt_answer_number>=security_question_policy_min_number:
                    if password_protect == 0:
                        attrs = {"password_protect": 1}
                        DesktopUser.modify_desktop_user(user_id, attrs)
                else:
                    if password_protect == 1:
                        attrs = {"password_protect": 0}
                        DesktopUser.modify_desktop_user(user_id, attrs)

        offset = offset + limit
        total_count = total_count - limit
    else:
        limit = total_count
        desktop_user_set = ctx.pg.get_by_filter(dbconst.TB_DESKTOP_USER, 
                                                filter_conditions, 
                                                offset=offset, 
                                                limit=limit)
        if desktop_user_set is None:
            logger.error("describe desktop user failed , condition: [%s]" % filter_conditions)
            return None
        for _,desktop_user in desktop_user_set.items():
            user_id = desktop_user.get("user_id")
            if not user_id:
                continue
            password_protect = desktop_user.get("password_protect", 0)
            prompt_answer_number = ctx.pgm.get_password_prompt_answer(user_id)
            if security_question_policy_min_number>0:
                if prompt_answer_number>=security_question_policy_min_number:
                    if password_protect == 0:
                        attrs = {"password_protect": 1}
                        DesktopUser.modify_desktop_user(user_id, attrs)
                else:
                    if password_protect == 1:
                        attrs = {"password_protect": 0}
                        DesktopUser.modify_desktop_user(user_id, attrs)
