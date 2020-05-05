from django.db import models
from channels.layers import get_channel_layer
from django.forms.models import model_to_dict
from asgiref.sync import async_to_sync


class Arm(models.Model):
    arm_id = models.CharField(max_length=20, primary_key=True)
    last_online = models.DateTimeField()

    def save(self, *args, **kwargs):
        super(Arm, self).save(*args, **kwargs)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("default", {"type": "push.arms"})


class Session(models.Model):
    arm = models.ForeignKey(Arm, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=40)
    status = models.CharField(max_length=20, blank=True)
    before_img_url = models.CharField(max_length=300, blank=True)
    after_img_url = models.CharField(max_length=300, blank=True)
    logs_base_url = models.CharField(max_length=300, blank=True)
    log_filenames = models.TextField(blank=True)
    enabled_log_types = models.TextField(default="[]")

    def save(self, *args, **kwargs):
        super(Session, self).save(*args, **kwargs)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("default", {"type": "push.sessions.of.arm", "arm_id": self.arm.arm_id})


class UI(models.Model):
    arms_to_start = models.TextField()
    open_logs = models.CharField(max_length=40, default="")

    def save(self, *args, **kwargs):
        # Always save to line 1
        self.id = 1

        # Get current UI object and convert it to dict
        ui_objects = UI.objects.all()
        if len(ui_objects) > 0:
            current_UI = model_to_dict(UI.objects.all()[0])
        else:
            super().save(*args, **kwargs)
            return

        # If there are values not provided, set them to the current ones
        for key in current_UI.keys():
            if getattr(self, key) == "":
                setattr(self, key, current_UI[key])

        # Save new UI object to DB
        super().save(*args, **kwargs)


class Log(models.Model):
    arm = models.ForeignKey(Arm, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    log_type = models.CharField(max_length=40)
    asctime = models.CharField(max_length=40)
    created = models.CharField(max_length=40)
    name = models.CharField(max_length=20)
    levelname = models.CharField(max_length=10)
    msg = models.TextField()
    pathname = models.CharField(max_length=200)
    lineno = models.CharField(max_length=10)
    bm_id = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        super(Log, self).save(*args, **kwargs)
        open_logs = UI.objects.get(id=1).open_logs.split(".")

        try:
            if str(open_logs[0]) == str(self.arm.arm_id) and str(open_logs[1]) == str(self.session.id) and str(open_logs[2]) == str(self.log_type):
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "default",
                    {
                        "type": "push.logs",
                        "arm_id": self.arm.arm_id,
                        "sess_id": self.session.id,
                        "log_type": self.log_type
                    }
                )
        except IndexError:
            pass
