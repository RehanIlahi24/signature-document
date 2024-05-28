from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from django.conf import settings
from django.core.mail import send_mail
from dotenv import load_dotenv

def get_client_ip_address_test(request):
    req_headers = request.META

    cf_connecting_ip = req_headers.get('HTTP_CF_CONNECTING_IP')
    if cf_connecting_ip:
        return cf_connecting_ip
    x_forwarded_for_value = req_headers.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(',')[0].strip()
    else:
        ip_addr = req_headers.get('REMOTE_ADDR')
    
    return ip_addr

def pagination_custom(request,table):
    paginator = Paginator(table, 10)
    page = request.GET.get('page')
    try:
        table = paginator.page(page)
    except PageNotAnInteger:
        table = paginator.page(1)
    except EmptyPage:
        table = paginator.page(paginator.num_pages)
    return table

load_dotenv() 
apikey = os.getenv("SENDGRID_APIKEY")

def send_email_siging(email, subject_content, message_content):
    subject = subject_content
    message = message_content
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email,]
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print('An error occurred while sending the email:', e)