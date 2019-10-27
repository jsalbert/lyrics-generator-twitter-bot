import ssl
import json
import smtplib


class EmailSender:
    def __init__(self, authentication_json_path):
        with open(authentication_json_path, 'r') as f:
            authentication_params = json.load(f)

        self.password = authentication_params['PASSWORD']
        self.email = authentication_params['EMAIL']

        # Port for SSL
        self.port = 465

        # Create a secure SSL context
        self.context = ssl.create_default_context()

    def send_email(self, email_receiver, message):
        with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context=self.context) as server:
            server.login(self.email, self.password)
            server.sendmail(self.email, email_receiver, message)
