from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import send_email_siging
import hashlib
from .models import *

@receiver(post_save, sender=Document)
def send_email_of_complete_signing(sender, instance, **kwargs):
    if instance.is_signed == True:
        email = instance.user.email
        sign = instance.signature_image.url.split('/')[-1]
        signed_document = instance.signed_document.file.url.split('/')[-1]  
        metadata = {
            'ip_address': instance.ip_address,
            'os': instance.os,
            'os_version': instance.os_version,
            'browser': instance.browser,
            'browser_version': instance.browser_version,
            'device': instance.device
        }
        sha512 = hashlib.sha512()
        sha512.update(sign.encode('utf-8'))
        sha512.update(signed_document.encode('utf-8'))
        for key, value in metadata.items():
            sha512.update(f"{key}:{value}".encode('utf-8'))
        hash_value = sha512.hexdigest()
        
        email_body = (
            f"Dear Customer,\n\n"
            f"Your have successfully signed document.\n\n"
            f"Signed Document: {signed_document}\n"
            f"{metadata}\n\n"
            f"{hash_value}\n\n"
            f"Best regards,\n"
            f"DySign"
        )        
        send_email_siging(email, 'Document Signed Successfully', email_body)