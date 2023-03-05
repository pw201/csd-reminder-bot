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

The script is intended to be invoked daily using `cron.py`, which will go through all
the sheets in `config.SHEETS` and email reminders for any sheets which have a
lesson coming up. `cron.py` will by default send emails for lessons today, but
can be given a `--days` argument to work a number of days in advance.

> python cron.py --days 1

will send emails for lessons tomorrow.

## Spreadsheet formats

The `key` and `gid` for a Google Sheet refer to the fields in the sheet's URL,
see https://stackoverflow.com/a/44184071 for details. The `gid` field
distinguishes different tabs on the same sheet.

The `rota.py` module expects to find a sheet with a row of column headings
(which need not be the first row in the sheet) which begin with a "Date" column
and then contain whatever other columns it's looking for. This is currently
hardcoded to CSD's columns for teachers, DJs and door volunteers, as is the
`reminder.py` code which composes and sends the emails.

The `email_database.py` module expects to find a Google Sheet produced by
Google Forms with columns named "Email address" and "Name". The column headings
must appear in the first row (as they will when Google Forms creates the
sheet).

## Debugging

Various modules can be run directly from the command line to debug them. For
example, `reminder.py` will accept a bunch of command line options to send
emails for a particular sheet on a particular day.

The `make_sample_config.py` script will create a new `sample_config.py` from
`config.py` by replacing quoted strings with null strings, removing the
passwords that are in it. `config.py` itself is in this project's `.gitignore` file.
