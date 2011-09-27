from commonlib.messaging.email import Mailer
from conf_test import config
import os

def test_basic_send():

    mailer = Mailer(config['mail'])
    to = config['mail']['mail.smtp.username']
    subject = "TurboMail test"
    rich = """
    <html>
        <body>
            <strong>Hi There</strong>
        </body>
    </html>"""
    attachment = os.getcwd()+'/requirements.txt'
    mailer.start()
    mailer.send(to, to, subject, rich=rich, attachment=attachment)
