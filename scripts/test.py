#!/home/gnowak/emaildmz/emaildmzenv/bin/python

from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import FeedParser
from email import message_from_file
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
    # NEED TO HANDLE NO USER ID EXISTING
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
    # NEED TO HANDLE NO FORWARDING EMAILS EXISTING
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
    # convert stdin.sys to email Message
    message = message_from_file(content)

    # get a dict of the message headers and their values
    message_items = dict(message.items())

    # get the user id based on the email 'to' header
    user_id = get_user_id(message_items['To'])

    # get the forwarding emails
    forwarding_emails = get_forwarding_emails(message_items['To'], user_id)

    # creating the full email
    # use 'alternative': https://en.wikipedia.org/wiki/MIME#Alternative
    email = MIMEMultipart('alternative')
    email['Subject'] = "{} {}".format(
        message_items['Return-Path'],
        message_items['Subject'],
        )
    email['From'] = 'no-reply@emaildmz.com'
    email['To'] = ", ".join(forwarding_emails)
    email.set_payload(message)

    # sending the email
    s = smtplib.SMTP('localhost')
    s.sendmail(email['From'], forwarding_emails, email.as_string())
    s.quit()

if __name__ == "__main__":
    send_email(sys.stdin)
