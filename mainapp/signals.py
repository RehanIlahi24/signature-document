from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import send_email_siging
import hashlib
from django.conf import settings
from django.core.mail import EmailMessage
from .models import *

@receiver(post_save, sender=Document)
def send_email_of_complete_signing(sender, instance, **kwargs):
    print('signal called')
    if instance.is_signed == True:
        email = instance.user.email
        sign = instance.signature_image.url.split('/')[-1]
        signed_document_url = instance.signed_document.file.url 
        signed_document_path = instance.signed_document.file.path 
        signed_document_name = instance.signed_document.file.name.split('/')[-1] 

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
        sha512.update(signed_document_name.encode('utf-8'))
        for key, value in metadata.items():
            sha512.update(f"{key}:{value}".encode('utf-8'))
        hash_value = sha512.hexdigest()
        
        email_body = (
            f"Dear {instance.user.username},\n\n"
            
            f"You have successfully signed the document.\n"
            f"This is an automatic message in which we attach a copy of the signed document along with the audit of modifications and signature as well as the key metadata of the transaction and the unique identifier.\n\n"
            
            f"Signed Document: {signed_document_name}\n\n"

            f"IP address: {instance.ip_address}\n"
            f"Operating system and version: {instance.os} {instance.os_version}\n"
            f"Browser and version: {instance.browser} {instance.browser_version}\n"
            f"Device type: {instance.device}\n\n"
            
            f"Unique identifier: {hash_value}\n\n"

            f"Best regards,\n"
            f"DyRevolution"
        )

        email_message = EmailMessage(
            subject='Document Signed Successfully',
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )

        email_message.attach_file(signed_document_path)

        email_message.send()

