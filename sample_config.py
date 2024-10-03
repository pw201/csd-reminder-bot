# Copy me to config.py and fill in the blanks.
"""
Configuration information for the bot.
"""

# config.py should not be checked in to github, as it contains passwords and
# spreadsheet URLs. config.py is in the project .gitignore file for that
# reason. If you change it, run make_sample_config.py to regenerate the sample
# without passwords in, which you can then check in.

from utils import LessonDetails

# Debugging flag to allow testing without spamming people. Set this to True to actually send anything.
ALLOW_SENDING_EMAILS=True
# Force addresess for all names to exist and send emails to this single address, if set
FORCE_EMAILS_TO=None

# Who am I?
BOT_ADDRESS = ""
BOT_NAME = ""
ORGANISATION = ""

# Where warnings about there being not enough volunteers go
WARNINGS_NAME = ""
WARNINGS_ADDDRESS=""

# SMTP server information
SMTP_SERVER=""
SMTP_PORT=587
SMTP_USERNAME=""
SMTP_PASSWORD=""

# You can define functions which are called with the list of roles as an argument.
# These should return any extra text to be included in the email to that role.
# Setting the extra_text member of LessonDetails to that function uses it for
# that night's lessons. Setting extra_text=None means it's ignored.

# When we run from cron.py, daily, look at these sheets and send emails.
LESSON_DETAILS = [
    # Tuesdays
    LessonDetails(key="", gid="",
              min_teachers=2, min_volunteers=1, min_djs=2,
              extra_text=tuesday_text),
    # Wednesdays 
    LessonDetails(key="", gid="",
              min_teachers=2, min_volunteers=1, min_djs=0,
              extra_text=wednesday_text),
    # Shall We Dance
    LessonDetails(key="", gid="",
              min_teachers=1, min_volunteers=0, min_djs=0,
              extra_text=None),
]

# The sheet which is the backend of the reminder email signup form.
# This should have "Email address" and "Name" as column headings
EMAIL_KEY=""
EMAIL_GID=""
