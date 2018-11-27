#!/home/gnowak/emaildmz/emaildmzenv/bin/python

from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import FeedParser
import datetime
import psycopg2
import re
import smtplib
import sys

import django, os, sys
sys.path.append("/home/gnowak/emaildmz")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emaildmz.settings")
django.setup()

from emaildmz import config


def get_user_id(user_email):
    # find the user id based on the alias that the email was sent to
    conn = psycopg2.connect(host=config.settings['db_host'],
                            database=config.settings['db_name'],
                            user=config.settings['db_user'],
                            password=config.settings['db_password'],
    )
    cur = conn.cursor()
    alias_name = user_email.split('@')[0]
    cur.execute("SELECT user_id FROM aliases_alias WHERE name = %s",
        (alias_name,))
    user_id = cur.fetchone()[0]

    cur.close()
    conn.close()

    return user_id

def get_forwarding_emails(user_email, user_id):
    conn = psycopg2.connect(host=config.settings['db_host'],
                            database=config.settings['db_name'],
                            user=config.settings['db_user'],
                            password=config.settings['db_password'],
    )
    cur = conn.cursor()
    cur.execute("SELECT email FROM aliases_forwardingemail WHERE user_id = %s",
        (user_id,))
    forwarding_emails = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT email FROM auth_user WHERE id = %s",
        (user_id,))
    user_email = cur.fetchone()[0]

    forwarding_emails.append(user_email)

    cur.close()
    conn.close()

    return forwarding_emails

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
        keyword = "To: "
        if re.match('^{}'.format(keyword), line):
            to_email = line.split(keyword)[1].strip()
            user_id = get_user_id(to_email)
            forwarding_emails = get_forwarding_emails(to_email, user_id)

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
    email['From'] = 'no-reply@emaildmz.com'
    email['To'] = ", ".join(forwarding_emails)

    message = MIMEText(message)
    email.attach(message)

    # sending the email
    s = smtplib.SMTP('localhost')
    s.sendmail(email['From'], forwarding_emails, email.as_string())
    s.quit()

def get_body(content):
    content = content.readlines()
    open("/home/gnowak/test.txt", "w").close()
    with open("/home/gnowak/test.txt", "a") as file:
        for line in content:
            file.write("line = {}".format(line))

if __name__ == "__main__":
#    user_id = get_user_id('gn9012@gmail.com')
#    forwarding_emails = get_forwarding_emails('gn9012@gmail.com', user_id)
    send_email(sys.stdin)
#    get_body(sys.stdin)

