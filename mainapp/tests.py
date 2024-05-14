from django.test import TestCase
from .models import *
import uuid
from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.
class UsertestMethod(TestCase):
    def setUp(self):
        self.uid = uuid.uuid1()
        self.email = 'martin@gmail.com'
        self.username = 'Martin Guptil' # this field is set to unique so give unique username whenever you try to add a new user.
        self.first_name = 'Martin'
        self.last_name = 'Guptil'
        self.password = '123'
        self.passport_image = '/media/user_images/pymaven_logo_2.png' #change image name to which one you have in your media. 
        self.hashed_password = make_password(self.password)

        self.user = User.objects.create(
            email=self.email,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            password=self.hashed_password,
            uid=self.uid,
            passport_image=self.passport_image
        )

    def test_create_user(self):
        self.assertEqual(self.user.uid, self.uid)
        self.assertEqual(self.user.email, self.email)
        self.assertEqual(self.user.username, self.username)
        self.assertEqual(self.user.first_name, self.first_name)
        self.assertEqual(self.user.last_name, self.last_name)
        self.assertEqual(self.user.passport_image, self.passport_image)
        self.assertTrue(self.user.check_password(self.password))
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_active)
        self.assertIsNotNone(self.user.last_login)

    def test_update_user(self):
        new_email = 'martinguptil@example.com'
        new_username = 'Martin Guptil updated'
        new_first_name = 'Martin Updated'
        new_last_name = 'Guptil Updated'
        new_passport_image = '/media/user_images/updated_image.png' #change image name to which one you have in your media. 
        new_password = '1234'

        self.user.email = new_email
        self.user.username = new_username
        self.user.first_name = new_first_name
        self.user.last_name = new_last_name
        self.user.passport_image = new_passport_image
        self.user.set_password(new_password)
        self.user.save()

        updated_user = User.objects.get(id=self.user.id)

        self.assertEqual(updated_user.email, new_email)
        self.assertEqual(updated_user.username, new_username)
        self.assertEqual(updated_user.first_name, new_first_name)
        self.assertEqual(updated_user.last_name, new_last_name)
        self.assertEqual(updated_user.passport_image, new_passport_image)
        self.assertTrue(updated_user.check_password(new_password))
        self.assertIsNotNone(updated_user.last_login)
        self.assertFalse(updated_user.check_password(self.password))

class DocumentFileTestMethod(TestCase):
    def test_create_document_file(self):
        file = '/media/document_files/JOB__10255_GrOFi00' #change file name to which one you have in your media.

        doc_file_ob = DocumentFile.objects.create(file=file)

        self.assertEqual(doc_file_ob.file, file)

class DocumentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='123')

    def test_create_document(self):
        document_file = DocumentFile.objects.create(file='test_file.pdf') #change file name to which one you have in your media.
        signature_image = 'signature_images/test_signature.png'
        
        document = Document.objects.create(
            user=self.user,
            document_file=document_file,
            signature_image=signature_image  # Set the signature_image to the dummy image
        )
        document.refresh_from_db()

        self.assertEqual(document.user, self.user)
        self.assertEqual(document.document_file, document_file)
        self.assertFalse(document.is_signed)
        self.assertEqual(document.signature_image, signature_image)  
        self.assertIsNone(document.ip_address)
        self.assertIsNone(document.os)
        self.assertIsNone(document.os_version)
        self.assertIsNone(document.browser)
        self.assertIsNone(document.browser_version)
        self.assertIsNone(document.device)
        self.assertIsNotNone(document.created_at)
        self.assertIsNotNone(document.updated_at)

    def test_update_document_after_signature(self):
        document_file = DocumentFile.objects.create(file='test_file.pdf') #change file name to which one you have in your media.
        signed_document_file = DocumentFile.objects.create(file='signed_test_file.pdf') #change file name to which one you have in your media.
        document = Document.objects.create(user=self.user, document_file=document_file)

        document.signature_image = 'signature_images/test_signature.png' #change image name to which one you have in your media.
        document.ip_address = '192.168.1.1'
        document.os = 'Windows'
        document.os_version = '10'
        document.browser = 'Chrome'
        document.browser_version = '90.0'
        document.device = 'PC'
        document.is_signed = True
        document.signed_document = signed_document_file
        document.save()

        updated_document = Document.objects.get(pk=document.pk)

        self.assertEqual(updated_document.signature_image, 'signature_images/test_signature.png') #change image name to which one you have in your media.
        self.assertEqual(updated_document.ip_address, '192.168.1.1')
        self.assertEqual(updated_document.os, 'Windows')
        self.assertEqual(updated_document.os_version, '10')
        self.assertEqual(updated_document.browser, 'Chrome')
        self.assertEqual(updated_document.browser_version, '90.0')
        self.assertEqual(updated_document.device, 'PC')
        self.assertTrue(updated_document.is_signed)
        self.assertEqual(updated_document.signed_document, signed_document_file)
        self.assertIsNotNone(updated_document.created_at)
        self.assertIsNotNone(updated_document.updated_at)