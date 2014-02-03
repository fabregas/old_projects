import smtplib
from settings import EMAIL_FROM, SMTP_SERVER
from email.mime.text import MIMEText

class MailClient:
    from_email = EMAIL_FROM
    smtp_server = SMTP_SERVER # SMTP_SERVER syntax "smtp_host:smtp_port:[ssl]:[username]:[password]"

    @classmethod
    def connect_to_smtp(cls):
        parts = cls.smtp_server.split(':')

        if len(parts) != 5:
            raise Exception ('SMTP_SERVER variable is not valid!')

        smtp_host, smtp_port, ssl, username, password = parts

        if ssl.lower() == 'ssl':
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)

        if username.strip():
                server.login(username, password)

        return server


    @classmethod
    def sendMail(cls, to_list, subject, message, from_email=None):
        #message = 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' % (cls.from_email, ", ".join(to_list), subject.decode('utf8'), message.decode('utf8'))

        smtp_server = cls.connect_to_smtp()

        if not from_email:
            from_email = cls.from_email

        msg = MIMEText(message.encode('utf8'), 'plain', 'utf-8')
        msg["Subject"] = subject
        msg["From"] = cls.from_email
        msg["To"] = ", ".join(to_list)

        smtp_server.sendmail(from_email, to_list, msg.as_string())
        smtp_server.quit()


