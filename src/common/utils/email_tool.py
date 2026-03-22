# -*- coding: utf-8 -*-
'''
Created on 2012-11-09

@author: yunify
'''
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.Header import Header
from email.Utils import formataddr
from lepl.apps.rfc3696 import Email
from log.logger import logger

def send_email(subject, sender, recipients, body, sender_name, smtp_server, smtp_port, login_user, login_password, ssl_on=False, timeout=15, attachments=None):
    ''' send email to recipients
        @param subject: the title of the mail.
        @param sender: the email address of sender.
        @param password: the sender's email password.
        @param recipients: a list of email recipients.
        @param body: the content of the email. 
        @param sender_name: the name displayed in customer's mail box instead of sender email address. 
        @param attachments: the attachments, [{'name': "name.txt", 'data': 'file data', 'charset': 'UTF-8'}]
    '''
    
    if not isinstance(recipients, (list, tuple)):
        recipients = [recipients]
    if attachments and not isinstance(attachments, (list, tuple)):
        attachments = [attachments]
    
    try:
        # Header class is smart enough to try US-ASCII, then the charset we
        # provide, then fall back to UTF-8.
        header_charset = 'UTF-8'
    
        # We must choose the body charset manually
        for body_charset in 'US-ASCII', 'UTF-8':
            try:
                body.encode(body_charset)
            except UnicodeError:
                pass
            else:
                break
    
        # We must always pass Unicode strings to Header, otherwise it will
        # use RFC 2047 encoding even on plain ASCII strings.
        sender_name = str(Header(unicode(sender_name), header_charset))
    
        # Make sure email addresses do not contain non-ASCII characters
        sender_addr = sender.encode('ascii')
        recipient_addrs = (",".join(recipients)).encode('ascii')
    
        msg = MIMEMultipart()
        # Create the message ('html' stands for Content-Type: text/html)
        body = MIMEText(body.encode(body_charset), 'html', body_charset)
        msg.attach(body)

        if attachments:
            for attachment in attachments:
                att = MIMEText(attachment['data'], 'base64', attachment['charset'])
                att["Content-Type"] = 'application/octet-stream'
                att_header = Header(unicode(attachment['name']), header_charset)
                att.add_header('Content-Disposition', 'attachment; filename="%s"' % att_header)
                if 'content_id' in attachment:
                    att.add_header('Content-ID', '<%s>' % attachment['content_id'])
                msg.attach(att)

        msg['From'] = formataddr((sender_name, sender_addr))
        msg['To'] = recipient_addrs
        msg['Subject'] = Header(unicode(subject), header_charset)
    
        # Send the message via gmail
        if ssl_on:
            session = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=timeout)
        else:
            session = smtplib.SMTP(smtp_server, smtp_port, timeout=timeout)
        session.ehlo()
        # session.starttls()
        session.login(login_user, login_password)
        session.sendmail(sender, recipients, msg.as_string())
        session.quit()
    except Exception, e:
        logger.error("send email [%s] [%s] -> [%s] failed [%s]" % (subject, sender, recipients, e))
        return False
    return True

def is_email_valid(email_addr):
    ''' check if the email address is valid '''
    try:
        validator = Email()
        ret = validator(email_addr)
    except Exception, e:
        logger.error('validate email address [%s] failed, [%s]' % (email_addr, e))
        return False
    return ret
