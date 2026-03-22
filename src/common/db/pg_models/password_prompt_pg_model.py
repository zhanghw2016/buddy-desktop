import db.constants as dbconst

class PasswordPromptPGModel():
    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_password_prompt_questions(self, prompt_question_id=None):
        conditions = {}
        if prompt_question_id:
            conditions["prompt_question_id"] = prompt_question_id
        prompt_questions = self.pg.base_get(dbconst.TB_PROMPT_QUESTION, conditions)
        if not prompt_questions:
            return None
        return prompt_questions

    def get_user_password_prompt_answers(self, user_id):
        if not user_id:
            return None

        conditions = {"user_id": user_id}
        result = {}
        prompt_answers = self.pg.base_get(dbconst.TB_PROMPT_ANSWER, conditions)
        if prompt_answers is not None and len(prompt_answers) != 0:
            for prompt_answer in prompt_answers:
                result[prompt_answer["prompt_question_id"]] = prompt_answer

        return result

    def get_user_password_prompt_answer(self, prompt_answer_id):
        if not prompt_answer_id:
            return None

        conditions = {"prompt_answer_id": prompt_answer_id}
        prompt_answers = self.pg.base_get(dbconst.TB_PROMPT_ANSWER, conditions)
        if prompt_answers is not None and len(prompt_answers) != 0:
            return prompt_answers[0]

        return None

    def get_prompt_answer_users(self, prompt_question_id):
        if not prompt_question_id:
            return None

        conditions = {"prompt_question_id": prompt_question_id}
        prompt_answers = self.pg.base_get(dbconst.TB_PROMPT_ANSWER, conditions)
        if prompt_answers is None and len(prompt_answers) == 0:
            return None

        users = []
        for prompt_answer in prompt_answers:
            user_id = prompt_answer["user_id"]
            user = self.pg.base_get(dbconst.TB_DESKTOP_USER, condition={"user_id":user_id}, columns={"user_id", "user_name", "real_name"})
            if user:
                users.append(user)

        return users

    def check_user_password_prompt_answer(self, prompt_question_id):
        if not prompt_question_id:
            return False

        conditions = {"prompt_question_id": prompt_question_id}
        prompt_answers = self.pg.base_get(dbconst.TB_PROMPT_ANSWER, conditions)
        if prompt_answers is not None and len(prompt_answers) != 0:
            return True

        return False

    def get_prompt_question_content(self, prompt_question_id):
        if not prompt_question_id:
            return None

        conditions = {"prompt_question_id": prompt_question_id}
        prompt_questions = self.pg.base_get(dbconst.TB_PROMPT_QUESTION, conditions)
        if not prompt_questions:
            return None

        return prompt_questions[0]["question_content"]

    def check_ignore_security_question(self, user_id):
        user_set = self.pg.base_get(dbconst.TB_DESKTOP_USER, condition={"user_id":user_id}, columns={"security_question"})
        if not user_set:
            return False
        security_question = user_set[0]["security_question"]
        if security_question == 2:
            return True
        return False
