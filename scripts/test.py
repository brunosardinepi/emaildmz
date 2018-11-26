#!/usr/bin/env python3

from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import FeedParser
import datetime
import re
import smtplib
import sys


def send_email(content):
    # setup for reading the body of the email
    content = content.readlines()
    parser = FeedParser()

    for line in content:
        # reading the body of the email
        parser.feed(line)

        # locating the sender
        keyword = "Return-Path: "
        if re.match('^{}'.format(keyword), line):
            from_email = line.split(keyword)[1].strip()
            from_email = from_email.replace("<", "")
            from_email = from_email.replace(">", "")

        # locating the recipient
        keyword = "X-Original-To: "
        if re.match('^{}'.format(keyword), line):
            to_email = line.split(keyword)[1].strip()

        # locating the subject
        keyword = "Subject: "
        if re.match('^{}'.format(keyword), line):
            subject = line.split(keyword)[1].strip()

    # creating the body of the email
    message = parser.close()
    message = message.get_payload()

    # creating the full email
    email = MIMEMultipart()
    email['Subject'] = "[{}] {}".format(from_email, subject)
#    email['From'] = from_email
    email['From'] = 'no-reply@emaildmz.com'
#    email['To'] = to_email
    email['To'] = 'iswearsheis18@gmail.com'
    message = MIMEText(message)
    email.attach(message)

    # sending the email
    s = smtplib.SMTP('localhost')
    s.sendmail(email['From'], email['To'], email.as_string())
    s.quit()


if __name__ == "__main__":
    send_email(sys.stdin)

