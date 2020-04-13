from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Arm(models.Model):
    arm_id = models.CharField(max_length=20)
    arm_address = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        super(Arm, self).save(*args, **kwargs)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('default', {'type': 'arm.added'})
        print("sent")


class Session(models.Model):
    arm = models.ForeignKey(Arm, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    before_img_url = models.CharField(max_length=300)
    after_img_url = models.CharField(max_length=300)
    logs_base_url = models.CharField(max_length=300)
    log_filenames = models.TextField()
