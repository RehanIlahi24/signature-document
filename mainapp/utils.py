from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from django.conf import settings
from django.core.mail import send_mail
from dotenv import load_dotenv

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

def send_email(to_email,subject,html):
    print("email called before")
    message = Mail(
        from_email='dysignca@gmail.com',
        to_emails=to_email,
        subject=subject,
        plain_text_content=html
        # html_content=html 
        )
    try:
        print('enter try')
        sg = SendGridAPIClient(apikey)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        print('exit try')
    except Exception as e:
        print('error : ', e.message)

def send_email_siging(email, subject_content, message_content):
    print('start')
    subject = subject_content
    message = message_content
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email,]
    try:
        print('enter into send email')
        send_mail(subject, message, from_email, recipient_list)
        print('Email sent successfully')
    except Exception as e:
        print('An error occurred while sending the email:', e)
    print('end')