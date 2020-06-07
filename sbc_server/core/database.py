"""
A class to organize direct database manipulations, used by WebSocket message handlers.
"""

from django.forms.models import model_to_dict
from .models import Arm, Session, Log


class DB:
    """
    A class to organize direct database manipulations.
    """
    def get_arms(self):
        """
        Retrieve a list of registered arms ordered by arm_id.

        Returns
        -------
        arms : list of dicts
            List of arms represented as dicts.

        """

        arms = Arm.objects.all().order_by("arm_id")
        return [model_to_dict(arm) for arm in arms]

    def get_sessions_of_arm(self, arm_id):
        """
        Retrieve a list of sessions of given arm.

        Parameters
        ----------
        arm_id : str
            Retrieve sessions only of the arm with given arm_id.

        Returns
        -------
        sessions_of_arm : list of dicts
            List of sessions represented as dicts.

        """

        sessions_of_arm = Session.objects.filter(arm=arm_id).order_by("-session_started")
        return [model_to_dict(session) for session in sessions_of_arm]

    def get_logs(self, arm_id, session_id, log_type):
        """
        Retrieve, filter and order logs.

        Parameters
        ----------
        arm_id : str
            Retrieve logs only of the arm with given arm_id.
        session_id : str
            Retrieve logs only of the session with given session_id.
        log_type : str
            Retrieve logs only of the given type.

        Returns
        -------
        logs : list of dicts
            List of log entries represented as dicts.

        """

        logs = Log.objects.filter(arm=arm_id, session=session_id, log_type=log_type).order_by("created")
        return [model_to_dict(log) for log in logs]

    def get_session_by_id(self, id):
        """
        Retrieve a session by ID.

        Parameters
        ----------
        id : str
            ID of session to retrieve.

        Returns
        -------
        session : dict
            Session with given ID as dict.
        """

        session = Session.objects.get(id=id)
        return session
