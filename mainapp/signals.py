from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .utils import send_email_siging
import hashlib
from django.db.models.signals import post_save
# from dashboard.views import business
from .models import *

def calculate_sha512_hash(sign, signed_document, metadata):
    sha512 = hashlib.sha512()
    sha512.update(sign.encode('utf-8'))
    sha512.update(signed_document.encode('utf-8'))
    for key, value in metadata.items():
        sha512.update(f"{key}:{value}".encode('utf-8'))
    return sha512.hexdigest()

@receiver(post_save, sender=Document)
def send_email_of_complete_signing(sender, instance, **kwargs):
    print("signal called before")
    if instance.is_signed:
        print("signal called after")
        email = instance.user.email
        sign = instance.signature_image.url  
        signed_document = instance.signed_document.file.url  
        metadata = {
            'ip_address': instance.ip_address,
            'os': instance.os,
            'os_version': instance.os_version,
            'browser': instance.browser,
            'browser_version': instance.browser_version,
            'device': instance.device
        }
        hash_value = calculate_sha512_hash(sign, signed_document, metadata)
        
        # Email body
        email_body = (
            f"Dear Customer,\n\n"
            f"Your have successfully signed document.\n\n"
            f"Sign: {sign}\n"
            f"Signed Document: {signed_document}\n"
            f"Metadata: {metadata}\n\n"
            f"Hash (SHA-512): {hash_value}\n\n"
            f"Best regards,\n"
            f"DySign"
        )
        
        send_email_siging(email, 'Document Signed Successfully', email_body)

        # Save the hash in the instance metadata (optional, depending on your needs)
        instance.metadata_hash = hash_value
        instance.save()



@receiver(post_save, sender=Document) 
def send_email_of_complete_siging(sender, instance, **kwargs):
    print("signal called before")
    if instance.is_signed == True:
        print("signal called after")
        email = instance.user.email 
        send_email_siging(email, f'{instance.ip_address} successfully signed!', f'{instance.ip_address} successfully signed!')

# @receiver(pre_delete, sender=Document)
# def delete_related_signed_document(sender, instance, **kwargs):
#     print("signal called before delete")
#     if instance.signed_document:
#         print("signal called after delete")
#         if os.path.isfile(instance.signed_document.file.path):
#             os.remove(instance.signed_document.file.path)
#             print("signal called after delete complete")