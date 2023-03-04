"""
Run from cron or similar, send emails for the lessons which are today.
"""
import argparse
import datetime
import logging

import config
import reminder
import rota

def send_reminders_for_today(days_advance):
    """
    For all the sheets in config.SHEETS, see whether they have a lesson
    days_advance from today, and send the reminders for that lesson if they do.
    """

    lesson_date = datetime.date.today() + datetime.timedelta(days=days_advance)
    for sheet in config.SHEETS:
        r = rota.Rota(key=sheet.key, gid=sheet.gid)
        if r.has_lesson_on_date(lesson_date):
            reminder.send_emails_for_lesson(rota=r,
                                            lesson_date=lesson_date,
                                            min_teachers=sheet.min_teachers,
                                            min_volunteers=sheet.min_volunteers,
                                            min_djs=sheet.min_djs)


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
