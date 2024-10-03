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
import re
import smtplib

import config
import email_database
from rota import Rota
import utils

# Match things which separate names in a single cell
NAME_SPLITTER = re.compile(r"[/&,\+]|\s+and\s+")

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
    if config.ALLOW_SENDING_EMAILS:
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


def send_reminder_to(name, email_address, lesson_date, roles, extra_text):
    """Remind name at email_address that they're helping on lesson_date with roles."""
    roles = " and ".join(roles)
    lesson_date = lesson_date.strftime("%A %d %B %Y")
    message = f"""Hi {name},

This is to remind you that you've signed up to be a {roles} for {config.ORGANISATION} on {lesson_date}. We really appreciate your help.

{extra_text}

Beep boop,

{config.BOT_NAME}

PS: You're receiving this because you're signed up to automatic reminders. If you don't want them any more, reply to this to let me know.

"""
    send_email(name=name,
               address=email_address,
               body=message,
               subject=f"Reminder: you're a {roles} on {lesson_date}")


def send_warning_email(warnings, lesson_date):
    """
    Warn that there are insufficient signups for the lesson_date lesson.
    warnings is a dictionary keyed by roles with some warning text for each.
    """
    warnings_text = "\n\n - ".join(
        [f"{role}: {warning}" for role, warning in warnings.items()])
    lesson_date = lesson_date.strftime("%A %d %B %Y")
    message = f"""Hi {config.WARNINGS_NAME},

I found the following roles without people signed up for them on {lesson_date}:

 - {warnings_text}

Beep boop,

{config.BOT_NAME}
"""
    send_email(name=config.WARNINGS_NAME,
               address=config.WARNINGS_ADDDRESS,
               body=message,
               subject=f"Missing {', '.join(warnings.keys())} for {lesson_date}")


def send_emails_for_lesson(rota, lesson_date, details):
    """
    Send the reminder emails for the given rota and lesson date. details is a
    utils.LessonDetails giving the details of that night. If there are less
    than min_whatever of that role signed up on the sheet, also send a
    warning to committee.
    """
    # (role description, minimum number, method to get the names from the rota)
    roles = [("teacher", details.min_teachers, rota.teachers_on_date),
             ("door volunteer", details.min_volunteers, rota.volunteers_on_date),
             ("DJ", details.min_djs, rota.djs_on_date),
             ]

    # Keys are the role description, values are some text saying what's wrong.
    warnings = {}
    # We'll accumulate people's roles in name_to_roles so that you only get
    # one email if you're both teaching and DJing, say.
    name_to_roles = collections.defaultdict(list)
    # For each role, work out who's doing it and whether that's enough people.
    for role, min_num, get_names_on_date in roles:
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

        names = process_names(names)
        for name in names:
            name_to_roles[name].append(role)

        if len(names) < min_num:
            warnings[role] = f"minimum {min_num} but {len(names)} signed up."

    for name, roles in name_to_roles.items():
        if details.extra_text is not None:
            extra_text = details.extra_text(roles)
        else:
            extra_text = ""
        lookup_and_send_email(lesson_date, name, roles, extra_text)

    if warnings:
        send_warning_email(warnings, lesson_date)


def process_names(names):
    """
    Cope with a variety of funny things that happen on the sign up sheet. Turn
    cell contents into actual names, return a list of them.
    """
    ret = []
    for name in names:
        # "Blah Led by Buggins + Muggins" splits into Buggins, Muggins
        if "Led by " in name:
            name = name.split("Led by ")[1]
        ret.extend(NAME_SPLITTER.split(name))

    return [name.strip() for name in ret]

def lookup_and_send_email(lesson_date, name, roles, extra_text):
    """
    Given the lesson_date, name on the sheet and roles, work out who to send email to
    and send it.
    """
    if config.FORCE_EMAILS_TO:
        email_address = config.FORCE_EMAILS_TO
    else:
        email_address = email_database.db.get_email_address(name)

    if email_address is None:
        logging.info(f"Can't find email address for {name}, who's a {roles} on {lesson_date}")
    else:
        send_reminder_to(name, email_address, lesson_date, roles, extra_text)


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
    parser.add_argument("--text", help="Extra text to add to emails", type=str, default="")
    args = parser.parse_args()

    if args.test:
        config.ALLOW_SENDING_EMAILS=False

    if args.test or args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    rota = Rota(key=args.key, gid=args.gid)
    details = utils.LessonDetails(key=args.key, gid=args.gid,
                          min_teachers=args.teachers,
                          min_volunteers=args.volunteers,
                          min_djs=args.djs,
                          extra_text=lambda r: args.text)
    send_emails_for_lesson(rota=rota, lesson_date=args.date, details=details)


if __name__ == "__main__":
    from_cli()

