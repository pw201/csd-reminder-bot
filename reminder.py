import argparse
import collections
import email.message
from email.utils import formataddr
import logging
import smtplib

import config
import email_database
from rota import Rota

def send_email(name, address, subject, body, test_only):
    """
    Email the given address with the subject and body, unless test_only in
    which case we just log it.
    """

    msg = email.message.EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = formataddr((config.BOT_NAME, config.BOT_ADDRESS))
    msg["To"] = formataddr((name, address))

    if test_only:
        logging.debug(f"Dry run message:\n{msg.as_string()}")
        return

    try:
        server = smtplib.SMTP(host=config.SMTP_SERVER, port=config.SMTP_PORT)
        server.starttls()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logging.info(f"Send email to {address}")
    except smtplib.SMTPException:
        logging.exception(f"Failed to send email to {address}")


def send_reminder_to(name, email_address, next_lesson_date, roles, test_only):
    roles = " and also a ".join(roles)
    next_lesson_date = next_lesson_date.strftime("%A %d %B %Y")
    message = f"""Hi {name}, it's {config.BOT_NAME}.

Thanks for volunteering to be a {roles} on {next_lesson_date}. We really appreciate your help.

You're receiving this because you're signed up to reminders. If you don't want them any more, reply to this to let me know.

Beep boop,

{config.BOT_NAME}
"""
    send_email(name=name,
               address=email_address,
               body=message,
               subject=f"Volunteering for Cambridge Swing Dance on {next_lesson_date}",
               test_only=test_only)


def send_warning_to_committee(warnings, next_lesson_date, test_only):
    warnings = "\n * ".join(warnings)
    next_lesson_date = next_lesson_date.strftime("%A %d %B %Y")
    message = f"""Hi committee, it's {config.BOT_NAME}.

I found the volunteer roles missing for the lesson on {next_lesson_date}:

 * {warnings}

Beep boop,

{config.BOT_NAME}
"""
    send_email(name="CSD committee",
               address=config.COMMITTEE_WARNINGS_ADDDRESS,
               body=message,
               subject=f"Missing volunters for {next_lesson_date}",
               test_only=test_only)


def send_emails(rota, num_teachers, num_volunteers, num_djs, test_only):
    next_lesson_date = rota.next_date()

    roles = [("teacher", num_teachers, rota.teachers_on_date),
             ("door volunteer", num_volunteers, rota.volunteers_on_date),
             ("DJ", num_djs, rota.djs_on_date),
             ]

    committee_warnings = []
    names_to_roles = collections.defaultdict(list)
    for description, num, get_names_on_date in roles:
        names = get_names_on_date(next_lesson_date)
        for name in names:
            names_to_roles[name].append(description)

        if num and len(names) < num:
            committee_warnings.append(f"Expected {num} {description}s but only {len(names)} are signed up.")

    for name, roles in names_to_roles.items():
        email_address = email_database.get_email_address(name)
        if email_address is None:
            logging.info(f"Can't find email address for {name}, who's a {description} on {next_lesson_date}")
        else:
            send_reminder_to(name, email_address, next_lesson_date, roles, test_only)

    if committee_warnings:
        send_warning_to_committee(committee_warnings, next_lesson_date, test_only)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="Google sheet key", required=True)
    parser.add_argument("--gid", help="Google sheet ID (for the individual sheet)", required=True)
    parser.add_argument("--teachers", help="Number of teachers, warn if there are less than the given number", type=int)
    parser.add_argument("--volunteers", help="Number of volunteers, warn if there are less than the given number", type=int)
    parser.add_argument("--djs", help="Number of DJs, warn if there are less than the given number", type=int)
    parser.add_argument("--test", help="Do not send emails, just log them", action="store_true")
    parser.add_argument("--debug", help="Turn on debug logging", action="store_true")
    args = parser.parse_args()

    if args.test or args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    sheet_url = f"https://docs.google.com/spreadsheets/d/{args.key}/export?format=csv&id={args.key}&gid={args.gid}"
    rota = Rota(sheet_url)
    send_emails(rota, num_teachers=args.teachers, num_volunteers=args.volunteers, num_djs=args.djs, test_only=args.test)


if __name__ == "__main__":
    main()

