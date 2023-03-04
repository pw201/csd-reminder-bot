"""Copy me to config.py and fill in the blanks."""

from utils import RotaSheet

# Who am I?
BOT_ADDRESS = ""
BOT_NAME = ""
ORGANISATION = ""

# Where warnings about there being not enough volunteers go
WARNINGS_NAME = ""
WARNINGS_ADDDRESS=""

# Debugging flag to allow testing without spamming people. Set this to True to actually send anything.
ALLOW_SENDING_EMAILS=False

# SMTP server information
SMTP_SERVER=""
SMTP_PORT=587
SMTP_USERNAME=""
SMTP_PASSWORD=""

# When we run from cron.py, daily, look at these sheets and send emails.
SHEETS = [
    # Tuesdays 2023
    RotaSheet(key="", gid="", min_teachers=2, min_volunteers=1, min_djs=2),
    # Wednesdays 2023
    RotaSheet(key="", gid="", min_teachers=2, min_volunteers=1, min_djs=0),
    # Shall We Dance 2023
    RotaSheet(key="", gid="", min_teachers=1, min_volunteers=0, min_djs=0),
]

# The sheet which is the backend of the reminder email signup form.
# This should have Email address, First name, Surname as column headings.
EMAIL_KEY=""
EMAIL_GID=""
