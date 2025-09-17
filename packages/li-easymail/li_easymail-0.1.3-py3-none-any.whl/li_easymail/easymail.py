from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
import os

class _Easymail:
    def __init__(self):
        self.creds = None
        self.service = None
        self._subject = ""
        self._recipient = ""

    def credentials(self, client_secret_file, token_file="token.json"):
        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(token_file, ['https://www.googleapis.com/auth/gmail.send'])
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, ['https://www.googleapis.com/auth/gmail.send'])
                self.creds = flow.run_local_server(port=0)
            with open(token_file, 'w') as f:
                f.write(self.creds.to_json())
        self.service = build('gmail', 'v1', credentials=self.creds)

    class SendMail:
        def __init__(self, parent):
            self.parent = parent

        def subject(self, text):
            self.parent._subject = text

        def recipient(self, email):
            self.parent._recipient = email

        def __call__(self, body):
            if not self.parent._subject or not self.parent._recipient:
                raise ValueError("Subject and recipient must be set before sending.")
            message = MIMEText(body)
            message['to'] = self.parent._recipient
            message['subject'] = self.parent._subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw_message}
            self.parent.service.users().messages().send(userId='me', body=send_message).execute()
            print(f"Email sent to {self.parent._recipient}!")

easymail = _Easymail()
easymail.sendmail = _Easymail.SendMail(easymail)
