# from abc import ABC, abstractmethod
from api.client import ApiClientHandler

class Actor():
    @property
    def handleName(self):
        return self._handleName


class HumanActor(Actor):
    @property
    def userName(self):
        return self._userName

    @property
    def emailAddress(self):
        return self._emailAddress

    def __init__(self, handle_name:str, user_name:str, email_address:str, *args, **kwargs):
        self._handleName = handle_name
        self._userName = user_name
        self._emailAddress = email_address


class LlmActor(Actor):
    @property
    def modelName(self):
        return self._modelName

    def __init__(self, handle_name:str, model_name:str, *args, **kwargs):
        self._handleName = handle_name
        self._modelName = model_name


class RoleMixIn():
    """
    都度都度の条件分岐なしでロール間の振る舞い相互作用を定義するにはこれがいい
    """
    @property
    def role(self):
        return self._role


class InterviewerMixIn(RoleMixIn):
    def __init__(self, *args, **kwargs):
        self._role = "Interviewwer"


class IntervieweeMixIn(RoleMixIn):
    def __init__(self, *args, **kwargs):
        self._role = "Interviewee"


class EvaluatorMixIn(RoleMixIn):
    def __init__(self, *args, **kwargs):
        self._role = "Evaluator"


class DirectorMixIn(RoleMixIn):
    def __init__(self, *args, **kwargs):
        self._role = "Director"


# 具体クラス

class LlmInterviewer(LlmActor, InterviewerMixIn):
    def __init__(self, handle_name:str, model_name:str, *args, **kwargs):
        LlmActor.__init__(self, handle_name, model_name)
        InterviewerMixIn.__init__(self)


class HumanInterviewee(HumanActor, IntervieweeMixIn):
    def __init__(self, handle_name:str, user_name:str, email_address:str, *args, **kwargs):
        HumanActor.__init__(self, handle_name, user_name, email_address)
        IntervieweeMixIn.__init__(self)


class LlmEvaluator(LlmActor, EvaluatorMixIn):
    def __init__(self, handle_name:str, model_name:str, *args, **kwargs):
        LlmActor.__init__(self, handle_name, model_name)
        EvaluatorMixIn.__init__(self)


class HumanDirector(HumanActor, DirectorMixIn):
    def __init__(self, handle_name:str, user_name:str, email_address:str, *args, **kwargs):
        HumanActor.__init__(self, handle_name, user_name, email_address)
        DirectorMixIn.__init__(self)

