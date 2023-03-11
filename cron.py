"""
Run from cron or similar, send emails for the lessons which are today (or today + N days).
"""
import argparse
import datetime
import logging

import config
import reminder
import rota

def send_reminders_for_today(days_advance):
    """
    For all the nights in config.LESSON_DETAILS, see whether they have a lesson
    days_advance from today, and send the reminders for that lesson if they do.
    """

    lesson_date = datetime.date.today() + datetime.timedelta(days=days_advance)
    for details in config.LESSON_DETAILS:
        r = rota.Rota(key=details.key, gid=details.gid)
        if r.has_lesson_on_date(lesson_date):
            reminder.send_emails_for_lesson(rota=r,
                                            lesson_date=lesson_date,
                                            details=details)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Turn on debug logging", action="store_true")
    parser.add_argument("--days",
                        help="How many days to look ahead from the current date",
                        type=int, default=0)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    send_reminders_for_today(days_advance=args.days)
