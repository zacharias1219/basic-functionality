import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_verification_email(name, email, chatbot_id):
    body = f"""
    Hello {name},

    Thank you for using our services. Here is the bot you have created. You can use this as a free trial for 3 days.

    Bot ID: {chatbot_id}

    Code Snippet:
    <iframe src="http://autoserve.com/chatbots/{chatbot_id}" title="AI-Powered Chatbot" width="600" height="400" style="border:1px solid #ccc;"> </iframe>

    Add this code to your web page to start serving your customers.

    Regards,
    Autoserve
    """
    
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_USER')
    msg['To'] = email
    msg['Subject'] = 'Your AI-Powered Chatbot'
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
        server.send_message(msg)