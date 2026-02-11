import os.path
import base64
from datetime import datetime, timedelta
from io import BytesIO

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class Email:

    def __init__(self, email):
        self.email = email

    @property
    def headers(self):
        return self.email['payload']['headers']

    @property
    def subject(self):
        subjects = [datum['value'] for datum in self.headers if datum['name'] == 'Subject']
        if len(subjects) != 1:
            raise ValueError("Invalid number of subjects found: " + str(subjects))
        return subjects[0]

    @property
    def sender(self):
        senders = [datum['value'] for datum in self.headers if datum['name'] == 'From']
        if len(senders) != 1:
            raise ValueError("Invalid number of senders found: " + str(senders))
        return senders[0]

    @property
    def recipients(self):
        recipients = [datum['value'] for datum in self.headers if datum['name'] == 'To']
        if len(recipients) != 1:
            raise ValueError("Invalid number of recipient lists found: " + str(recipients))
        return recipients[0]

    @property
    def date(self):
        dates = [datum['value'] for datum in self.headers if datum['name'] == 'Date']
        if len(dates) != 1:
            raise ValueError("Invalid number of dates found: " + str(dates))
        date_str = dates[0]
        return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')

    @property
    def labels(self):
        return self.email['labelIds']

    @property
    def read(self):
        return 'UNREAD' not in self.labels

    @property
    def parts(self):
        return self.email['payload'].get('parts', [self.email['payload']])

    @property
    def body(self):
        return self.extend_body_from_parts('', self.parts)

    @staticmethod
    def extend_body_from_parts(body, parts):
        for part in parts:
            data = part['body'].get('data', b'')
            body += base64.urlsafe_b64decode(data).decode('utf-8')
            if 'parts' in part:
                body = Email.extend_body_from_parts(body, part['parts'])
        return body

    @property
    def attachment_ids(self):
        return dict(self.extract_attachment_ids_from_parts(self.parts))

    @staticmethod
    def extract_attachment_ids_from_parts(parts):
        attachments = []
        for part in parts:
            if part['filename']:
                data = part['body'].get('attachmentId', b'')
                if data:
                    attachments.append((part['filename'], data))
            if 'parts' in part:
                attachments.extend(Email.extract_attachment_ids_from_parts(part['parts']))
        return attachments

class GmailClient:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.modify']

    def __init__(self, credentials_filename, server_port=59587, token_filename='token_gmail.json'):
        self.credentials_filename = credentials_filename
        self.server_port = server_port
        self.token_filename = token_filename
        self.credentials = self.authenticate()
        self.service = build('gmail', 'v1', credentials=self.credentials)

    def authenticate(self):
        credentials = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.token_filename):
            credentials = Credentials.from_authorized_user_file(self.token_filename, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                    self.credentials_filename, self.SCOPES)
                credentials = flow.run_local_server(port=self.server_port)
            # Save the credentials for the next run
            with open(self.token_filename, 'w') as token:
                token.write(credentials.to_json())
        return credentials

    def read_emails(self, status='unread', since=None, **kwargs):
        if since is not None:
            timestamp_since = (datetime.now() - since).strftime('%Y/%m/%d')
        else:
            timestamp_since = '1/1/1'
        dispatch = {'unread': 'is:unread ', 'read': 'is:read ', 'all': ''}
        query = f"{dispatch[status]}after:{timestamp_since}"
        kwargs.setdefault('q', query)
        results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], **kwargs).execute()
        messages = results.get('messages', [])
        for message in messages[:4]:
            yield Email(self.service.users().messages().get(userId='me', id=message['id']).execute())

    def mark_as_read(self, message, **kwargs):
        return self.service.users().messages().modify(userId='me', id=message.email['id'], body={'removeLabelIds': ['UNREAD']}, **kwargs).execute()

if __name__ == '__main__':
    creds_filename = 'gmail_web_client_secret.json'
    mailbox = GmailClient(creds_filename)
    for message in mailbox.read_emails(since=timedelta(days=2)):
    # for message in mailbox.read_emails(status='all'):
        print(f'Subject: {message.subject}')
        print(f'From: {message.sender}')
        print(f'Date: {message.date}')
        print(f'Read: {message.read}')
        # print(f'Body: {message.body}')
        # print(f'Attachments: {message.attachment_ids}')
        # print('---')
        # if 'microsoft' in message.sender:
        #     mailbox.mark_as_read(message)
