import smtplib

class Utils:
    @classmethod
    def init(cls, config):
        cls.from_email = config.get('EMAIL_FROM','')
        cls.smtp_server = config.get('SMTP_SERVER', '') # SMTP_SERVER syntax "smtp_host:smtp_port:[ssl]:[username]:[password]"

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
        message = 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' % (cls.from_email, ", ".join(to_list), subject, message)

        smtp_server = cls.connect_to_smtp()

        if not from_email:
            from_email = cls.from_email

        smtp_server.sendmail(from_email, to_list, message)
        smtp_server.quit()



'''
#test connection

Utils.init({'SMTP_SERVER': 'smtp.priocom.com:25:nossl:kandrusenko:kandrusenko', 'EMAIL_FROM':'konstantin_andrusenko@priocom.com'})
Utils.sendMail(['gentoo@i.ua'], 'Test message', 'MEssage text...')
'''
