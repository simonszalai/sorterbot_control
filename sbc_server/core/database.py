from django.forms.models import model_to_dict
from .models import Arm, Session, Log


class DB:
    def get_arms(self):
        arms = Arm.objects.all().order_by("arm_id")
        return [model_to_dict(arm) for arm in arms]

    def get_sessions_of_arm(self, arm_id):
        sessions_of_arm = Session.objects.filter(arm=arm_id).order_by("-session_started")
        return [model_to_dict(session) for session in sessions_of_arm]

    def get_logs(self, arm_id, session_id, log_type):
        logs = Log.objects.filter(arm=arm_id, session=session_id, log_type=log_type).order_by("created")
        return [model_to_dict(log) for log in logs]

    def get_session_by_id(self, id):
        session = Session.objects.get(id=id)
        return session
