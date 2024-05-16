from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .utils import send_email
# from dashboard.views import business
from .models import *

@receiver(post_save, sender=Document) 
def send_Email_task_complete(sender, instance, **kwargs):
    print("signal called before")
    if instance.is_signed == True:
        print("signal called after")
        email = instance.user.email 
        send_email(email, f'{instance.ip_address} successfully signed!', f'{instance.ip_address} successfully signed!')

# @receiver(pre_delete, sender=Document)
# def delete_related_signed_document(sender, instance, **kwargs):
#     print("signal called before delete")
#     if instance.signed_document:
#         print("signal called after delete")
#         if os.path.isfile(instance.signed_document.file.path):
#             os.remove(instance.signed_document.file.path)
#             print("signal called after delete complete")