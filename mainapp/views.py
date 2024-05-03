from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .utils import *
from django.http import JsonResponse
import uuid
from reportlab.lib import colors
from io import BytesIO
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
import base64
from datetime import time
from reportlab.lib.units import inch
from docx2pdf import convert
import aspose.words as aw
# Create your views here.

def get_client_ip_address(request):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(',')[-1].strip()
    else:
        ip_addr = req_headers.get('REMOTE_ADDR')
    return ip_addr

def user_login(request):
    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == 'POST':
        data = request.POST
        username = data['username']
        password = data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request,"Successfully Login!")
            return redirect("index")
        else:
            messages.warning(request,"Incorrect username or password!")
    return render(request,'login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        data = request.POST
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        passport_image = request.FILES.get('passport_image')
        password1 = data.get('password1')
        password2 = data.get('password2')
        check_obj = User.objects.filter(username=username)
        if not check_obj.exists():
            if password1 == password2:
                hashed_password = make_password(password1)
                User.objects.create(passport_image=passport_image, password=hashed_password, username=username, first_name=first_name, last_name=last_name)
                messages.success(request,"Successfully SignUp!")
                return redirect('index')
            else:
                messages.error(request,"Password does not match!")
                return redirect('signup')
        else:
            messages.warning(request,"User with this username already exists!")
            return redirect('signup')
    return render(request, 'signup.html')

@login_required()
def change_password(request):
    if request.method == "POST":
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')
        user = User.objects.get(id=request.user.id)
        if p1 == p2:
            user.set_password(p1) 
            user.save()   
            messages.success(request,"Successfully Change Password!")
            return redirect('index')
        else:
            messages.warning(request,"Password does not match!")
            return redirect('change_password')
    return render(request, 'change_password.html')

@login_required()
def user_logout(request):
    try:
        logout(request)
        messages.success(request, 'Logout Successfully!')
        return redirect('index')
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')

@login_required()
def index(request):
    # try:
    if request.user.is_superuser:
        total_users = User.objects.exclude(is_superuser=True).count()
        verified_users = User.objects.filter(is_active=True, is_superuser=False).count()
        unverified_users = User.objects.filter(is_active=False, is_superuser=False).count()
        total_asign_doc = Document.objects.all().count()
        signed_doc = Document.objects.filter(is_signed=True).count()
        today_signed_doc = Document.objects.filter(is_signed=True, created_at__date=date.today()).count()
        return render(request, 'index.html', {'active' : 'active', 'total_users' : total_users, 'verified_users' : verified_users, 'unverified_users' : unverified_users, 'total_asign_doc' : total_asign_doc, 'signed_doc' : signed_doc, 'today_signed_doc' : today_signed_doc})
    else:
        today_asign_doc = Document.objects.filter(user=request.user, created_at__date=date.today()).count()
        today_signed_doc = Document.objects.filter(user=request.user, is_signed=True, created_at__date=date.today()).count()
        total_signed_doc = Document.objects.filter(user=request.user, is_signed=True).count()
        return render(request, 'index.html', {'active' : 'active', 'today_asign_doc' : today_asign_doc, 'today_signed_doc' : today_signed_doc, 'total_signed_doc' : total_signed_doc})
    # except:
    #     messages.warning(request, 'Request is not responed please check your internet connection and try again!')
    #     return redirect('index')

@login_required()
def user_view(request):
    # try:
        if request.user.is_superuser:
            users = User.objects.all().exclude(is_superuser=True)
            users = pagination_custom(request,users)
            if request.method == "POST":
                data = request.POST
                type = data.get('type')
                if type == 'delete':
                    id = data.get('user_id')
                    user = User.objects.get(id=id)
                    user.delete()
                    messages.success(request, 'Successfully Delete User!')
                    return redirect('user_view')
                if type == 'new-user':
                    username = data.get('username')
                    first_name = data.get('first_name')
                    last_name = data.get('last_name')
                    password = data.get('password')
                    password2 = data.get('password2')
                    existing_user = User.objects.filter(username=username).first()
                    if existing_user:
                        messages.error(request, "User with this username already exists!")
                        return redirect('user_view')
                    if password == password2:
                        uid = uuid.uuid1()
                        hashed_password = make_password(password)
                        User.objects.create(username=username, first_name=first_name, last_name=last_name, password=hashed_password, uid=uid)
                        messages.success(request,"Successfully Created User!")
                        return redirect('user_view')
                    else:
                        messages.warning(request,"Password does not match, Please try again!")
                        return redirect('user_view')
            return render(request, 'user.html', {'users' : users, 'active1' : 'active'})
        else:
            messages.error(request,"You are not superuser!")
            return redirect('index')
    # except:
    #         messages.warning(request, 'Request is not responed please check your internet connection and try again!')
    #         return redirect('index')

@login_required()
def user_detail(request, id):
    # try:
        if  request.user.is_superuser:
            users = User.objects.all()
            usr = User.objects.get(id=id)
            if request.method == "POST":
                data = request.POST
                username = data.get('username')
                first_name = data.get('first_name')
                last_name = data.get('last_name')
                image = request.FILES.get('image')
                is_active = data.get('is_active') == 'on'
                existing_user = User.objects.filter(username=username).exclude(id=usr.id).first()
                if existing_user:
                    messages.error(request, "User with this username already exists!")
                    return redirect('user_view')
                usr.username = username
                usr.first_name = first_name
                usr.last_name = last_name
                if image:
                    usr.passport_image = image
                usr.is_active = is_active
                usr.save()
                messages.success(request,f'Successfully Updated {usr.username}!')
                return redirect('user_view')
            return render(request, 'user_detail.html', {'users' : users, 'usr' : usr})
        else:
            messages.error(request,"You are not superuser!")
            return redirect('index')
    # except:
    #         messages.warning(request, 'Request is not responed please check your internet connection and try again!')
    #         return redirect('user_view')

def document_files(request):
    if request.user.is_superuser:
        docs = DocumentFile.objects.all()
        if request.method == "POST":
            data = request.POST
            type = data.get('type')
            if type == 'delete':
                id = data.get('doc_id')
                doc_ob = get_object_or_404(DocumentFile, id=id)
                doc_ob.delete()
                messages.success(request, 'Successfully Delete File!')
                return redirect('document_files')
            if type == 'new-document':
                document = request.FILES.get('document')
                if DocumentFile.objects.filter(file=document).exists():
                    messages.error(request, "File already exists!")
                else:
                    document_file = DocumentFile(file=document)  
                    document_file.save()
                    messages.success(request, "Successfully Add File!")
                return redirect('document_files')
        return render(request, 'document_files.html', {'active2' : 'active', 'docs' : docs})
    else:
        messages.error(request,"You are not superuser!")
        return redirect('index')
    
def asign_document(request):
    if request.user.is_superuser:
        docs = DocumentFile.objects.all()
        doc_ob = Document.objects.all()
        users = User.objects.all().exclude(is_superuser=True)
        if request.method == "POST":
            data = request.POST
            type = data.get('type')
            if type == 'delete':
                id = data.get('doc_id')
                doc_ob = Document.objects.get(id=id)
                doc_ob.delete()
                messages.success(request, 'Successfully Un asign File!')
                return redirect('asign_document')
            if type == 'new-asign':
                user_id = data.get('user')
                document_id = data.get('document')
                
                user_ob = User.objects.get(id=user_id)
                doc_ob = DocumentFile.objects.get(id=document_id)
                
                existing_document = Document.objects.filter(user=user_ob, document_file=doc_ob).first()
                if existing_document:
                    messages.error(request, "File already asign to this user!")
                    return redirect('asign_document')
                Document.objects.create(user=user_ob, document_file=doc_ob)
                messages.success(request,"Successfully Asign File!")
                return redirect('asign_document')
        return render(request, 'asign_document.html', {'active3' : 'active', 'doc_ob' : doc_ob, 'docs' : docs, 'users' : users})
    else:
        messages.error(request,"You are not superuser!")
        return redirect('index')

@login_required()
def asign_document_detail(request, id):
    # try:
        if request.user.is_superuser:
            docs = DocumentFile.objects.all()
            users = User.objects.all().exclude(is_superuser=True)
            asign_doc_ob = Document.objects.get(id=id)
            if request.method == "POST":
                data = request.POST
                user_id = data.get('user')
                document_id = data.get('document')
                
                user_ob = User.objects.get(id=user_id)
                doc_ob = DocumentFile.objects.get(id=document_id)
                
                existing_document = Document.objects.filter(user=user_ob, document_file=doc_ob).exclude(id=asign_doc_ob.id).first()
                if existing_document:
                    messages.error(request, "This File already asign to this user!")
                    return redirect('asign_document')
                asign_doc_ob.user = user_ob
                asign_doc_ob.document_file = doc_ob
                asign_doc_ob.save()
                messages.success(request,f'Successfully Updated!')
                return redirect('asign_document')
            return render(request, 'asign_document_detail.html', {'users' : users, 'docs' : docs, 'asign_doc_ob' : asign_doc_ob})
        else:
            messages.error(request,"You are not superuser!")
            return redirect('index')

def sign_document(request):
    if not request.user.is_superuser:
        doc_ob = Document.objects.filter(user=request.user, is_signed=False).order_by('-created_at')
        return render(request, 'sign_document.html', {'active4' : 'active', 'doc_ob' : doc_ob})

def sign_document_detail(request, id=None):
    document_ob = Document.objects.get(id=id)
    if request.method == 'POST':
        user_agent = request.user_agent
        ip_address = get_client_ip_address(request)
        browser = user_agent.browser.family
        browser_version = user_agent.browser.version_string
        os = user_agent.os.family
        os_version = user_agent.os.version_string
        is_pc = user_agent.is_pc
        is_mobile = user_agent.is_mobile
        is_tablet = user_agent.is_tablet
        
        signature_data = request.POST.get('signature_data') 
        if signature_data:
            format, imgstr = signature_data.split(';base64,')
            ext = format.split('/')[-1]  
            signature_image_data = ContentFile(base64.b64decode(imgstr), name='signature.' + ext)
            document_ob.signature_image.save('signature.' + ext, signature_image_data, save=True)
        document_ob.is_signed = True
        document_ob.ip_address = ip_address
        document_ob.browser = browser
        document_ob.browser_version = browser_version
        document_ob.os = os
        document_ob.os_version = os_version
        if is_pc:
            document_ob.device = 'Pc'
        elif is_mobile:
            document_ob.device = 'Mobile'
        elif is_tablet:
            document_ob.device = 'Tablet'

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []

        signature_image_path = document_ob.signature_image.path

        signature_image_width = 100
        signature_image_height = 50
        signature_image = Image(signature_image_path, width=signature_image_width, height=signature_image_height)
        file_name = document_ob.document_file.file.name.split('/')[-1]

        data = [
            ['Signature', signature_image],
            ['User', request.user.username],
            ['File Name', file_name],
            ['Is Signed', 'True'],
            ['IP Address', ip_address],
            ['Operating System', os],
            ['OS Version', os_version],
            ['Browser', browser],
            ['Browser Version', browser_version],
            ['Device', 'Pc' if is_pc else ('Mobile' if is_mobile else 'Tablet')],
            ['Assigning Date', document_ob.created_at.strftime("%B %d, %Y")],
            ['Assigning Time', document_ob.created_at.strftime("%I:%M %p")],
            ['Signed Date', document_ob.updated_at.strftime("%B %d, %Y")],
            ['Signed Time', document_ob.updated_at.strftime("%I:%M %p")],
        ]

        table = Table(data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))

        elements.append(table)
        doc.build(elements)
        pdf_file = ContentFile(pdf_buffer.getvalue())
        dc = DocumentFile()
        dc.file.save(f'signed_{file_name}', pdf_file, save=True)
        pdf_buffer.close()


        # Assuming document_ob is the Document object
    # document_file = document_ob.document_file.file
    # if document_file:
    #     # Open the existing PDF file
    #     with open(document_file.path, 'rb') as file:
    #         existing_pdf = PdfReader(file)

    #         # Create a BytesIO buffer to store the modified PDF content
    #         pdf_buffer = BytesIO()

    #         # Create a canvas for the new page with ReportLab
    #         doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    #         elements = []

    #         signature_image_path = document_ob.signature_image.path

    #         # # Set the width and height of the image as per your requirement
    #         signature_image_width = 100
    #         signature_image_height = 50
    #         signature_image = Image(signature_image_path, width=signature_image_width, height=signature_image_height)
    #         file_name = document_ob.document_file.file.name.split('/')[-1]
    #         # # Define data for the table

    #         data = [
    #             ['Signature', signature_image],
    #             ['User', request.user.username],
    #             ['File Name', file_name],
    #             ['Is Signed', 'True'],
                # ['IP Address', ip_address],
                # ['Operating System', os],
                # ['OS Version', os_version],
                # ['Browser', browser],
                # ['Browser Version', browser_version],
                # ['Device', 'Pc' if is_pc else ('Mobile' if is_mobile else 'Tablet')],
                # ['Assigning Date', document_ob.created_at.strftime("%B %d, %Y")],
                # ['Assigning Time', document_ob.created_at.strftime("%I:%M %p")],
                # ['Signed Date', document_ob.updated_at.strftime("%B %d, %Y")],
                # ['Signed Time', document_ob.updated_at.strftime("%I:%M %p")],
            # ]


            # Create a table and set style
            # table = Table(data, colWidths=[200, 200])
            # table.setStyle(TableStyle([
            #     ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
            #     ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            #     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            #     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            #     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            #     ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            # ]))


            # # Add table to the elements list
            # elements.append(table)

            # # Build the PDF document
            # doc.build(elements)

            # # Merge the existing PDF with the new PDF content
            # merger = PdfMerger()
            # merger.append(existing_pdf)

            # # Close the existing PDF
            # existing_pdf.close()

            # # Append the modified PDF content to the merger
            # pdf_buffer.seek(0)
            # merger.append(pdf_buffer)

            # # Save the merged PDF content to a BytesIO buffer
            # merged_pdf_buffer = BytesIO()
            # merger.write(merged_pdf_buffer)

            # # Save the modified PDF file to the database
            # dc = DocumentFile()
            # dc.file.save(f'signed_{document_file.name.split("/")[-1]}', merged_pdf_buffer, save=True)

            # # Close the PDF buffers
            # pdf_buffer.close()
            # merged_pdf_buffer.close()








        document_ob.save()
        messages.success(request, 'Successfully Signed!')
        return redirect('sign_document')
    return render(request, 'sign_document_detail.html', {'active4' : 'active', 'doc_ob' : document_ob})

def signed_document(request):
    if request.user.is_superuser:
        document_ob = Document.objects.filter(is_signed=True).order_by('-created_at')
    if not request.user.is_superuser:
        document_ob = Document.objects.filter(is_signed=True, user=request.user).order_by('-created_at')
    return render(request, 'signed_documents.html', {'active5' : 'active', 'doc_ob' : document_ob})

def signed_document_detail(request, id):
    if not request.user.is_superuser:
        document_ob = Document.objects.filter(is_signed=True, id=id, user=request.user)
    document_ob = Document.objects.get(id=id)
    return render(request, 'signed_document_detail.html', {'doc' : document_ob})

# print(User.objects.values())
# User.objects.filter(is_superuser=False).delete()