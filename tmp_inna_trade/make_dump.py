#!/usr/bin/python
import os
import sys
import tempfile
from datetime import date, datetime

from email.MIMEMultipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from email.utils import COMMASPACE, formatdate
from email import encoders
import smtplib

from make_dump_settings import *

def db_dump(db_name, dump_file):
    ret = os.system('pg_dump -U postgres %s | gzip > %s'%(db_name, dump_file))
    if ret:
        raise Exception('Database dump does not created!')

def send_file(dump_file):
    cur_date = date.today().strftime("%d.%m.%Y")
    msg = MIMEMultipart()
    msg['From'] = SEND_FROM
    msg['To'] = SEND_TO
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = 'Database dump - %s'%cur_date

    msg.attach( MIMEText('Collect datetime: %s'%datetime.now()) )

    part = MIMEBase('application', "octet-stream")
    part.set_payload( open(dump_file,"rb").read() )
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="db_dump-{0}.gz"'.format(cur_date))
    msg.attach(part)

    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.starttls()
    smtp.login(SMTP_LOGIN, SMTP_PASSWORD)
    smtp.sendmail(SEND_FROM, SEND_TO, msg.as_string())
    smtp.quit()

if __name__ == '__main__':
    dump_file = tempfile.NamedTemporaryFile()
    try:
        db_dump(DB_NAME, dump_file.name)
        send_file(dump_file.name)
    except Exception, err:
        print 'ERROR: %s'%err
        sys.exit(1)
    finally:
        dump_file.close()

