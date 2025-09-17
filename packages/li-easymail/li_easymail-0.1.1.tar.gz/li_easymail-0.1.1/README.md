# Easymail

Easymail is a lightweight Python wrapper for the Gmail API that simplifies sending emails.  
It handles authentication, token storage, and message creation so you can focus on writing your messages instead of boilerplate code.

- Simple and intuitive API
- Automatic Gmail OAuth2 authentication
- Local token storage for seamless reuse
- Minimal setup – authenticate once and send emails in seconds

## Installation

```bash
pip install li-easymail
```

## Usage

```python
from easymail import easymail

easymail.credentials("client_secret.json")
easymail.sendmail.subject("Hello!")
easymail.sendmail.recipient("example@gmail.com")
easymail.sendmail("This is a test email sent using Easymail 🚀")
```