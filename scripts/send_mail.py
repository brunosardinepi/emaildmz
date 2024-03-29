#!/home/relay/emaildmz/emaildmzenv/bin/python

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
sys.path.append("/home/relay/emaildmz")
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

def get_alias_recipients(alias_id):
    # find the alias's recipients
    conn = psycopg2.connect(host=config.settings['db_host'],
                            database=config.settings['db_name'],
                            user=config.settings['db_user'],
                            password=config.settings['db_password'],
    )
    cur = conn.cursor()

    # get the recipients based on the alias_id
    cur.execute("SELECT email FROM recipients_recipient WHERE alias_id = %s", (alias_id,))
    rows = cur.fetchall()

    # convert the query results to a list
    recipients = [row[0] for row in rows]

    # close the db connection
    cur.close()
    conn.close()

    return recipients

def get_alias_id(email):
    # find the alias id based on the alias that the email was sent to
    conn = psycopg2.connect(host=config.settings['db_host'],
                            database=config.settings['db_name'],
                            user=config.settings['db_user'],
                            password=config.settings['db_password'],
    )
    cur = conn.cursor()

    # alias in the db is the first half of the email address, before the '@'
    alias_name = email.split('@')[0]

    # get the alias_id based on the alias
    cur.execute("SELECT id FROM aliases_alias WHERE name = %s", (alias_name,))
    row = cur.fetchone()

    # if we found something, assign to alias_id
    if row is not None:
        alias_id = row[0]

    # otherwise, set to None
    else:
        alias_id = None

    # close the db connection
    cur.close()
    conn.close()

    return alias_id

def domain_is_blocked(alias_id, user_id, sender_email):
    open("/home/relay/test.txt", "w").close()

    # strip the domain from the sender's email
    domain = sender_email.split('@')[1]

    # connect to the database
    conn = psycopg2.connect(host=config.settings['db_host'],
                            database=config.settings['db_name'],
                            user=config.settings['db_user'],
                            password=config.settings['db_password'],
    )
    cur = conn.cursor()

    # find filters that block this domain
    query = """ SELECT name
                FROM filters_filter
                WHERE alias_id = {}
                AND is_blocked = 't'
                AND name ILIKE '%' || '{}' || '%' """.format(alias_id, domain)

    cur.execute(query)
    rows_blocked = cur.fetchall()

    # convert the results to a list
    rows_blocked = [row[0] for row in rows_blocked]

    # find all filters for this domain
    query = """ SELECT name
                FROM filters_filter
                WHERE alias_id = {}
                AND name ILIKE '%' || '{}' || '%' """.format(alias_id, domain)

    cur.execute(query)
    rows_all = cur.fetchall()

    # convert the results to a list
    rows_all = [row[0] for row in rows_all]

    # check for '*' entry in the blocked filters
    catchall = "*@{}".format(domain)
    if catchall in rows_blocked:

        # this domain is blocked
        is_blocked = True

    # check for exact match in the blocked filters
    elif sender_email in rows_blocked:

        # this sender is blocked
        is_blocked = True

    # if nothing matched, then this domain is either
    # in the allowed filter, or there is no filter yet
    else:

        # make sure there isn't an entry already
        if sender_email not in rows_all and catchall not in rows_all:

            # add a filter, set to allow
            query = """ INSERT INTO filters_filter (name, is_blocked, alias_id, user_id)
                        VALUES ('{}', {}, {}, {}) """.format(
                            sender_email, False, alias_id, user_id)
            cur.execute(query)

            # save the changes
            conn.commit()

        # set local variable to "allowed"
        is_blocked = False

    # if it's blocked, return True
    if is_blocked == True:
        return True

    # if it's allowed, return False
    elif is_blocked == False:
        return False

    # idk how we'd get here but just in case
    else:
        return

def send_email(content):
    # convert stdin.sys to email Message
    message = message_from_file(content)

    # get a dict of the message headers and their values
    message_items = dict(message.items())

    # get the alias id based on the email 'to' header
    alias_id = get_alias_id(message_items['Delivered-To'])

    # if there's no alias, bail
    if alias_id is None:
        return

    # get the user id based on the email 'to' header
    user_id = get_user_id(message_items['Delivered-To'])

    # get the sender's email address
    sender_email = message_items['Return-Path'].split("<")[1]
    sender_email = sender_email.split(">")[0]

    # check if this domain is blocked for this alias
    is_blocked = domain_is_blocked(alias_id, user_id, sender_email)

    # if this domain is blocked, bail
    if is_blocked == True:
        return

    # if it's allowed, go on
    elif is_blocked == False:

        # get the alias recipients
        recipients = get_alias_recipients(alias_id)

        # check if there is anyone to forward to
        if len(recipients) < 1:
            return

        # creating the full email
        # use 'alternative': https://en.wikipedia.org/wiki/MIME#Alternative
        email = MIMEMultipart('alternative')
        email['Subject'] = "[{}] {}".format(
            sender_email,
            message_items['Subject'],
            )
        email['From'] = 'no-reply@emaildmz.com'
        email['To'] = ", ".join(recipients)
        email.set_payload(message)

        # sending the email
        s = smtplib.SMTP('localhost')
        s.sendmail(email['From'], recipients, email.as_string())
        s.quit()

        # write to log
        with open("/home/relay/emaildmz/scripts/send_mail.log", 'a') as file:
            file.write("[{}] FROM: {}; ALIAS: {}; RECIPIENTS: {}; SUBJECT: {}\n".format(
                datetime.datetime.now(),
                sender_email,
                message_items['Delivered-To'],
                recipients,
                message_items['Subject'],
                )
            )

if __name__ == "__main__":
    send_email(sys.stdin)
