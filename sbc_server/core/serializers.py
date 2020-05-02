from rest_framework import serializers
from .models import Arm, Session, UI, Log


class ArmSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Arm
        fields = ["arm_id", "last_online"]


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    arm = serializers.SlugRelatedField(
        queryset=Arm.objects.all(),
        slug_field="arm_id"
    )

    class Meta:
        model = Session
        fields = [
            "arm", "session_id", "status", "before_img_url", "after_img_url",
            "logs_base_url", "log_filenames"
        ]


class UISerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UI
        fields = ["id", "cloud_status", "arms_to_start"]


class LogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Log
        fields = [
            "arm", "session", "log_type", "asctime", "created", "name",
            "levelname", "msg", "pathname", "lineno"
        ]
