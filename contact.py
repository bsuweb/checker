import smtplib
from email.mime.text import MIMEText


class Email:
    def __init__(self, emails, message, subject):
        self.emails = emails
        self.message = message
        self.subject = subject
        self.sender = 'bsuchecker@...'

    def send(self):
        msg = MIMEText(self.message)
        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = ','.join(self.emails)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(USER, PASSWORD)
        s.sendmail(self.sender, self.emails, msg.as_string())
        s.close()
