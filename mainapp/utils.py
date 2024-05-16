from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
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
        from_email='rehanilahi680@gmail.com',
        to_emails=to_email,
        subject=subject,
        plain_text_content=html
        # html_content=html 
        )
    try:
        sg = SendGridAPIClient(apikey)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
