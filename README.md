# csd-reminder-bot

This is a little Python application to read various Google Sheets containing a
rota of volunteers who've signed up to help out on various days at a swing
dance club, and email those volunteers with reminders at the appropriate time.
It can also email warnings to a fixed address if there aren't enough volunteers
signed up on a particular day.

It was written for [Cambridge Swing
Dance](https://www.cambridgeswingdance.com/) (CSD). It's public so people in
CSD can see what it does, and in the vague hope that someone else might also
find can be adapted to help them.

## Installing it

The script uses Python 3. You'll need the
[requests](https://requests.readthedocs.io/en/latest/) module available where
you're running.

The script is configured by the settings in `config.py`, so you'll need to copy
`sample_config.py` to `config.py` and fill those in. 

## Running it

The script is intended to be invoked daily using `cron.py`, which will go
through all the utils.LessonDetails objects in `config.LESSON_DETAILS` and
email reminders for any lessons coming up.

LessonDetails is a type for configuring details of a set of lessons which are
found on a single tab of a Google Sheet. Typically, all the lessons of a
particular type on a particular night of the week.

`cron.py` will by default send
emails for lessons today, but can be given a `--days` argument to work a number
of days in advance.

> python cron.py --days 1

will send emails for lessons tomorrow.

### Typical setup

On a Linux machine:

```bash
# Clone this repository
git clone https://github.com/pw201/csd-reminder-bot.git
cd csd-reminder-bot

# Create a config from the sample.
cp sample_config.py config.py
vim config.py # other editors are available

# Make a virtual environment for installing the dependencies.
python -m venv ./venv
. venv/bin/activate
pip install requests

python cron.py --debug # to try it with debugging output on
```

Running it daily from `cron`, here's a `crontab`:

```
SHELL=/bin/bash
MAILTO=you@yourdomain # fill this bit in with where logs should be emailed

# m h  dom mon dow   command
# Reminders at 8 am every day for the lessons that day.
0   8   *   *   *    (cd /home/pw201/csd-reminder-bot; source venv/bin/activate; python cron.py)
```

## Spreadsheet formats

The `key` and `gid` for a Google Sheet refer to the fields in the sheet's URL,
see https://stackoverflow.com/a/44184071 for details. The `gid` field
distinguishes different tabs on the same sheet.

The `rota.py` module expects to find a sheet with a row of column headings
(which need not be the first row in the sheet) which begin with a "Date" column.

Some `Rota` methods are hardcoded to CSD's roles for teachers, DJs, and door
volunteers, as is the `reminder.py` code which composes and sends the emails.
The roles and email messages could all be abstracted away and configured in
`config.py` if I could be bothered, but if you want to use this for non-CSD
reasons, you'll be hacking about with the code anyway.

The `email_database.py` module expects to find a Google Sheet with columns
named "Email address" and "Name". The column headings must appear in the first
row (as they will when Google Forms creates the sheet, if your form fields have
those names).

## Debugging

Various modules can be run directly from the command line to debug them. For
example, `reminder.py` will accept a bunch of command line options to send
emails for a particular sheet on a particular day.

There are a couple of debug options in `config.py` which can force the script to
never send emails or to always send them to a single address.

The `make_sample_config.py` script will create a new `sample_config.py` from
`config.py` by replacing quoted strings with null strings, removing the
passwords that are in it. `config.py` itself is in this project's `.gitignore` file.
