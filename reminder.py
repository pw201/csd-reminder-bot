"""
Handle the business of sending reminder emails.

This can be run on its own from the command line to test it, see below.
"""
import argparse
import collections
import datetime
import email.message
from email.utils import formataddr
import logging
import smtplib

import config
import email_database
from rota import Rota

# Debugging flag to allow testing without spamming people.
ALLOW_SENDING_EMAILS=False

def send_email(name, address, subject, body):
    """
    Email the given address with the subject and body.
    """

    msg = email.message.EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = formataddr((config.BOT_NAME, config.BOT_ADDRESS))
    msg["To"] = formataddr((name, address))

    logging.debug(f"Email message:\n{msg.as_string()}")
    if ALLOW_SENDING_EMAILS:
        try:
            server = smtplib.SMTP(host=config.SMTP_SERVER, port=config.SMTP_PORT)
            server.starttls()
            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            logging.info(f"Sent email to {name} <{address}>")
        except smtplib.SMTPException:
            logging.exception(f"Failed to send email to {address}")

    else:
        logging.info(f"Would send email to {name} <{address}> if I were allowed")

def send_reminder_to(name, email_address, lesson_date, roles):
    roles = " and also a ".join(roles)
    lesson_date = lesson_date.strftime("%A %d %B %Y")
    message = f"""Hi {name},

This is to remind you that you've signed up be a {roles} for Cambridge Swing Dance on {lesson_date}. We really appreciate your help.

You're receiving this because you're signed up to automatic reminders. If you don't want them any more, reply to this to let me know.

Beep boop,

{config.BOT_NAME}
"""
    send_email(name=name,
               address=email_address,
               body=message,
               subject=f"Reminder: you're helping out at Cambridge Swing Dance on {lesson_date}")


def send_warning_to_committee(warnings, lesson_date):
    warnings = "\n * ".join(warnings)
    lesson_date = lesson_date.strftime("%A %d %B %Y")
    message = f"""Hi committee,

I found the following roles without people signed up for them, for the lesson on {lesson_date}:

 * {warnings}

Beep boop,

{config.BOT_NAME}
"""
    send_email(name="CSD committee",
               address=config.COMMITTEE_WARNINGS_ADDDRESS,
               body=message,
               subject=f"Missing volunteers for {lesson_date}")


def send_emails_for_lesson(rota, lesson_date, min_teachers, min_volunteers, min_djs):
    """
    Send the reminder emails for the given rota and lesson date. If there are
    less than min_whatever of that role signed up on the sheet, also send a
    warning to committee.
    """
    # (role description, minimum number, method to get the names from the rota)
    roles = [("teacher", min_teachers, rota.teachers_on_date),
             ("door volunteer", min_volunteers, rota.volunteers_on_date),
             ("DJ", min_djs, rota.djs_on_date),
             ]

    committee_warnings = []
    # We'll accumulate people's roles in names_to_roles so that you only get
    # one email if you're both teaching and DJing, say.
    names_to_roles = collections.defaultdict(list)
    # For each role, work out who's doing it and whether that's enough people.
    for description, min_num, get_names_on_date in roles:
        try:
            names = get_names_on_date(lesson_date)
        except KeyError:
            # If we don't expect there to be any of a particular role, don't
            # crash when we don't find that heading in the sheet, as some
            # sheets have no DJs columns, for example. If we did expect to find
            # it, game over.
            if min_num > 0:
                raise
            else:
                continue # on to the next role

        for name in names:
            names_to_roles[name].append(description)

        if len(names) < min_num:
            committee_warnings.append(f"Expected {min_num} {description}s but only {len(names)} signed up.")

    for name, roles in names_to_roles.items():
        email_address = email_database.get_email_address(name)
        if email_address is None:
            logging.info(f"Can't find email address for {name}, who's a {roles} on {lesson_date}")
        else:
            send_reminder_to(name, email_address, lesson_date, roles)

    if committee_warnings:
        send_warning_to_committee(committee_warnings, lesson_date)


def from_cli():
    """
    When we run this module from the command line, take the details of a single
    sheet and send the emails about the next lesson on that sheet. This is for
    debugging or sending again if it all goes wrong.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="Google sheet key", required=True)
    parser.add_argument("--gid", help="Google sheet ID (for the individual sheet)", required=True)
    parser.add_argument("--teachers", help="Number of teachers, warn if there are less than the given number", type=int, default=0)
    parser.add_argument("--volunteers", help="Number of volunteers, warn if there are less than the given number", type=int, default=0)
    parser.add_argument("--djs", help="Number of DJs, warn if there are less than the given number", type=int, default=0)
    parser.add_argument("--test", help="Do not send emails, just log them", action="store_true")
    parser.add_argument("--debug", help="Turn on debug logging", action="store_true")
    parser.add_argument("--date", help="Date to look at, ISO format", type=datetime.date.fromisoformat, default=datetime.date.today())
    args = parser.parse_args()

    if args.test:
        global ALLOW_SENDING_EMAILS
        ALLOW_SENDING_EMAILS=False

    if args.test or args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    rota = Rota(key=args.key, gid=args.gid)
    send_emails_for_lesson(rota=rota, lesson_date=args.date, min_teachers=args.teachers, min_volunteers=args.volunteers, min_djs=args.djs)


if __name__ == "__main__":
    from_cli()

