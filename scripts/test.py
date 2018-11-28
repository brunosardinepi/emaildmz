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
    # find the user id based on the alias that the email was sent to
    conn = psycopg2.connect(host=config.settings['db_host'],
                            database=config.settings['db_name'],
                            user=config.settings['db_user'],
                            password=config.settings['db_password'],
    )
    cur = conn.cursor()

    # alias in the db is the first half of the email address, before the '@'
    alias_name = user_email.split('@')[0]

    # get the user_id based on the alias
    cur.execute("SELECT user_id FROM aliases_alias WHERE name = %s",
        (alias_name,))
    row = cur.fetchone()

    # if we found something, assign to user_id
    if row is not None:
        user_id = row[0]
    # otherwise, set to None
    else:
        user_id = None

    # close the db connection
    cur.close()
    conn.close()

    return user_id

def get_forwarding_emails(user_email, user_id):
    # find the user's forwarding emails
    conn = psycopg2.connect(host=config.settings['db_host'],
                            database=config.settings['db_name'],
                            user=config.settings['db_user'],
                            password=config.settings['db_password'],
    )
    cur = conn.cursor()

    # get the forwarding emails based on the user_id
    cur.execute("SELECT email FROM aliases_forwardingemail WHERE user_id = %s",
        (user_id,))
    rows = cur.fetchall()

    # convert the query results to a list
    forwarding_emails = [row[0] for row in rows]

    # get the user's real email address
    cur.execute("SELECT email FROM auth_user WHERE id = %s",
        (user_id,))
    row = cur.fetchone()
    user_email = row[0]

    # add the user's real email address to the list of recipients
    forwarding_emails.append(user_email)

    # close the db connection
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

    # if we got None for user_id, there's no user with this email, so we abort
    if user_id is None:
        return

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
