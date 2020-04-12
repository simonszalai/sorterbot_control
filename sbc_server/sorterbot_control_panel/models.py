from django.db import models


class Arm(models.Model):
    arm_id = models.CharField(max_length=20)
    arm_address = models.CharField(max_length=200)


class Session(models.Model):
    arm = models.ForeignKey(Arm, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    before_img_url = models.CharField(max_length=300)
    after_img_url = models.CharField(max_length=300)
    logs_base_url = models.CharField(max_length=300)
    log_filenames = models.TextField()
