# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from asgiref.sync import async_to_sync
# import channels.layers
# from .models import UI


# @receiver(post_save, sender=UI, dispatch_uid="status_changed")
# def on_status_change(sender, instance, **kwargs):
#     # Only send signal if cloud_status changed
#     if instance.cloud_status:
#         channel_layer = channels.layers.get_channel_layer()
#         async_to_sync(channel_layer.group_send)("default", {
#             "type": "status.changed",
#             "status": instance.cloud_status
#         })
