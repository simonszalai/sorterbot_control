from rest_framework import serializers
from .models import Arm, Session


class ArmSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Arm
        fields = ['arm_id', 'arm_address']


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    arm = serializers.SlugRelatedField(
        queryset=Arm.objects.all(),
        slug_field='id'
    )

    class Meta:
        model = Session
        fields = [
            'arm', 'session_id', 'status', 'before_img_url', 'after_img_url',
            'logs_base_url', 'log_filenames'
        ]
