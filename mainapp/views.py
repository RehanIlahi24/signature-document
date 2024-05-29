from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from datetime import date
from django.core.files.base import ContentFile
from django_ratelimit.decorators import ratelimit
from .ip_validating import *
from .models import *
from .utils import *
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from tempfile import NamedTemporaryFile
from io import BytesIO
import hashlib
import subprocess
import base64
import PyPDF2
import uuid
import os
# Create your views here.

def get_client_ip_address(request):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
    x_forwarded_for = request.META.get('HTTP_REMOTE_ADDR')
    print('remote : ', x_forwarded_for)
    print('touple values : ', x_forwarded_for_value)
    if x_forwarded_for_value:
        print('if statement')
        ip_addr = x_forwarded_for_value.split(',')[0]
    else:
        print('else statement')
        ip_addr = req_headers.get('REMOTE_ADDR')
    return ip_addr

@ratelimit(key='ip', rate='10/m', method=['GET', 'POST'])
def user_login(request):
    ip_address = get_client_ip_address(request)
    result = check_ip_blacklist(ip_address)
    
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

@ratelimit(key='ip', rate='10/m', method=['GET', 'POST'])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        data = request.POST
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        passport_image = request.FILES.get('passport_image')
        password1 = data.get('password1')
        password2 = data.get('password2')
        check_obj = User.objects.filter(username=username)
        if not check_obj.exists():
            if password1 == password2:
                hashed_password = make_password(password1)
                User.objects.create(passport_image=passport_image, password=hashed_password, username=username, first_name=first_name, last_name=last_name, email=email)
                messages.success(request,"Successfully SignUp!")
                return redirect('index')
            else:
                messages.error(request,"Password does not match!")
                return redirect('signup')
        else:
            messages.warning(request,"User with this username already exists!")
            return redirect('signup')
    return render(request, 'signup.html')

@ratelimit(key='ip', rate='10/m', method=['GET', 'POST'])
@login_required()
def change_password(request):
    try:
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
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')

@ratelimit(key='ip', rate='10/m', method=['GET', 'POST'])
@login_required()
def user_logout(request):
    try:
        logout(request)
        messages.success(request, 'Logout Successfully!')
        return redirect('index')
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')

@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def index(request):
    try:
        print('user ip address :', get_client_ip_address(request))
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
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')

@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def user_view(request):
    try:
        if request.user.is_superuser:
            users = User.objects.all().exclude(is_superuser=True).order_by('-id')
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
                    email = data.get('email')
                    first_name = data.get('first_name')
                    last_name = data.get('last_name')
                    image = request.FILES.get('image')
                    password = data.get('password')
                    password2 = data.get('password2')
                    existing_user = User.objects.filter(username=username).first()
                    if existing_user:
                        messages.error(request, "User with this username already exists!")
                        return redirect('user_view')
                    if password == password2:
                        uid = uuid.uuid1()
                        hashed_password = make_password(password)
                        User.objects.create(username=username, first_name=first_name, last_name=last_name, password=hashed_password, passport_image=image, email=email, uid=uid)
                        messages.success(request,"Successfully Created User!")
                        return redirect('user_view')
                    else:
                        messages.warning(request,"Password does not match, Please try again!")
                        return redirect('user_view')
            return render(request, 'user.html', {'users' : users, 'active1' : 'active'})
        else:
            messages.error(request,"You are not superuser!")
            return redirect('index')
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')

@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def user_detail(request, id):
    try:
        if  request.user.is_superuser:
            users = User.objects.all()
            usr = User.objects.get(id=id)
            if request.method == "POST":
                data = request.POST
                username = data.get('username')
                email = data.get('email')
                first_name = data.get('first_name')
                last_name = data.get('last_name')
                image = request.FILES.get('image')
                password1 = data.get('password1')
                password2 = data.get('password2')
                is_active = data.get('is_active') == 'on'
                existing_user = User.objects.filter(username=username).exclude(id=usr.id).first()
                if existing_user:
                    messages.error(request, "User with this username already exists!")
                    return redirect('user_view')
                if password1 and password2:
                    if password1 == password2:
                        usr.username = username
                        usr.email = email
                        usr.first_name = first_name
                        usr.last_name = last_name
                        if image:
                            usr.passport_image = image
                        usr.is_active = is_active
                        usr.set_password(password1)
                        usr.save()
                        messages.success(request,f'Successfully Updated {usr.username}!')
                        return redirect('user_view')
                    else:
                        messages.warning(request,"Password does not match, Please try again!")
                        return redirect('user_view')
                elif password1=="" and password2=="":
                    usr.username = username
                    usr.email = email
                    usr.first_name = first_name
                    usr.last_name = last_name
                    if image:
                        usr.passport_image = image
                    usr.is_active = is_active
                    usr.save()
                    messages.success(request,f'Successfully Updated {usr.username}!')
                    return redirect('user_view')
                else:
                    messages.warning(request,"Password does not match, Please try again!")
                    return redirect('user_view')
            return render(request, 'user_detail.html', {'users' : users, 'usr' : usr})
        else:
            messages.error(request,"You are not superuser!")
            return redirect('index')
    except:
            messages.warning(request, 'Request is not responed please check your internet connection and try again!')
            return redirect('user_view')

def doc2pdf_linux(doc):
    pdf_path = f"{os.path.splitext(doc)[0]}.pdf"
    cmd = f"/usr/bin/libreoffice --convert-to pdf --outdir {os.path.dirname(doc)} {doc}"
    try:
        subprocess.run(cmd, shell=True, check=True)
        return pdf_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting document: {e}")
        return None

@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def document_files(request):
    try:
        if request.user.is_superuser:
            signed_document_ids = Document.objects.values('signed_document__id').filter(signed_document__isnull=False)
            docs = DocumentFile.objects.exclude(id__in=signed_document_ids).order_by('-id')
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
                    if document.name.endswith('.docx'):
                        with NamedTemporaryFile(delete=False, suffix='.docx') as temp_docx_file:
                            for chunk in document.chunks():
                                temp_docx_file.write(chunk)
                            temp_docx_path = temp_docx_file.name
                        # try:
                        pdf_path = doc2pdf_linux(temp_docx_path)
                        pdf_filename = os.path.basename(pdf_path)
                        new_name = f'{document.name[:-5]}.pdf'
                        os.rename(pdf_path, os.path.join(os.path.dirname(pdf_path), new_name))
                        if not DocumentFile.objects.filter(file=new_name).exists():
                            with open(os.path.join(os.path.dirname(pdf_path), new_name), 'rb') as pdf_file:
                                document_file = DocumentFile()
                                document_file.file.save(new_name, ContentFile(pdf_file.read()), save=True)
                                document_file.save()
                                messages.success(request, "Successfully added file!")
                    else:
                        document_file = DocumentFile(file=document)  
                        document_file.save()
                        messages.success(request, "Successfully Add File!")
                    return redirect('document_files')
            return render(request, 'document_files.html', {'active2' : 'active', 'docs' : docs})
        else:
            messages.error(request,"You are not superuser!")
            return redirect('index')
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')    

@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def asign_document(request):
    try:
        if request.user.is_superuser:
            signed_document_ids = Document.objects.values('signed_document__id').filter(signed_document__isnull=False)
            docs = DocumentFile.objects.exclude(id__in=signed_document_ids)
            doc_ob = Document.objects.all().order_by('-created_at')
            users = User.objects.all().exclude(is_superuser=True)
            if request.method == "POST":
                data = request.POST
                type = data.get('type')
                if type == 'delete':
                    id = data.get('doc_id')
                    doc_ob = Document.objects.get(id=id)
                    if doc_ob.signed_document:
                        sign_doc_id = doc_ob.signed_document.id
                        DocumentFile.objects.filter(id=sign_doc_id).first().delete()
                    doc_ob.delete()
                    messages.success(request, 'Successfully Unasign File!')
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
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')

@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def asign_document_detail(request, id):
    try:
        if request.user.is_superuser:
            signed_document_ids = Document.objects.values('signed_document__id').filter(signed_document__isnull=False)
            docs = DocumentFile.objects.exclude(id__in=signed_document_ids)
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
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')

@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def sign_document(request):
    try:
        if not request.user.is_superuser:
            doc_ob = Document.objects.filter(user=request.user, is_signed=False).order_by('-created_at')
            return render(request, 'sign_document.html', {'active4' : 'active', 'doc_ob' : doc_ob})
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')

@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def sign_document_detail(request, id=None):
    try:
        document_ob = Document.objects.get(id=id, user=request.user)
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
            if document_ob.signature_image:
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

                existing_pdf_path = document_ob.document_file.file.path
                signature_image_path = document_ob.signature_image.path
                signature_image_width = 100
                signature_image_height = 50
                signature_image = Image(signature_image_path, width=signature_image_width, height=signature_image_height)
                file_name = document_ob.document_file.file.name.split('/')[-1]

                sign = document_ob.signature_image.url.split('/')[-1]
                metadata = {
                    'ip_address': ip_address,
                    'os': os,
                    'os_version': os_version,
                    'browser': browser,
                    'browser_version': browser_version,
                    'device': document_ob.device
                }
                sha512 = hashlib.sha512()
                sha512.update(sign.encode('utf-8'))
                sha512.update(file_name.encode('utf-8'))
                for key, value in metadata.items():
                    sha512.update(f"{key}:{value}".encode('utf-8'))
                hash_value = sha512.hexdigest()

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
                with open(existing_pdf_path, "rb") as existing_file:
                    existing_pdf = PyPDF2.PdfReader(existing_file)
                    output_pdf = PyPDF2.PdfWriter()
                    for page_num in range(len(existing_pdf.pages)):
                        page = existing_pdf.pages[page_num]
                        output_pdf.add_page(page)
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
                    doc.build([table])
                    buffer.seek(0)
                    new_pdf = PyPDF2.PdfReader(buffer)
                    for page_num in range(len(new_pdf.pages)):
                        page = new_pdf.pages[page_num]
                        output_pdf.add_page(page)
                    output_buffer = BytesIO()
                    output_pdf.write(output_buffer)
                    output_buffer.seek(0)
                    output_document_file = DocumentFile.objects.create()
                    output_document_file.file.save(f'signed_{request.user.username}_{file_name}', ContentFile(output_buffer.read()), save=True)
                    document_ob.signed_document = output_document_file
                    document_ob.hash_value = hash_value
                    document_ob.save()
                    messages.success(request, 'Successfully Signed!')
                    return redirect('signed_document')
        return render(request, 'sign_document_detail.html', {'active4' : 'active', 'doc_ob' : document_ob})
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')
    
@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def signed_document(request):
    try:
        if request.user.is_superuser:
            document_ob = Document.objects.filter(is_signed=True).order_by('-updated_at')
        if not request.user.is_superuser:
            document_ob = Document.objects.filter(is_signed=True, user=request.user).order_by('-updated_at')
        return render(request, 'signed_documents.html', {'active5' : 'active', 'doc_ob' : document_ob})
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')

@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def signed_document_detail(request, id):
    try:
        if request.user.is_superuser:
            document_ob = Document.objects.get(id=id, is_signed=True)
        else:
            document_ob = Document.objects.get(id=id, is_signed=True, user=request.user)
        return render(request, 'signed_document_detail.html', {'doc' : document_ob})
    except:
        messages.warning(request, 'Request is not responed please check your internet connection and try again!')
        return redirect('index')

@ratelimit(key='ip', rate='15/m', method=['GET', 'POST'])
@login_required()
def download_pdf(request, document_id):
    document = Document.objects.get(pk=document_id, user=request.user)
    document_path = document.signed_document.file.path
    file_name = document.signed_document.file.name.split('/')[-1]
    with open(document_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

# print(Document.objects.prefetch_related('document_file').values('id', 'document_file__id' ,'document_file__file'))
# User.objects.filter(is_superuser=False).delete()

# doc = Document.objects.get(id=2)
# pdf_path = convert(doc.document_file.file.path, "output1.pdf")
# print('path : ', pdf_path)
# import win32com.client

# input_file = doc.document_file.file.path
# output_file = "output11.pdf"
# doc_to_pdf(input_file, output_file)