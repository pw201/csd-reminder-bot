import csv
import datetime
import io
import logging
import requests


class Rota(object):
    """
    Represent the teaching/volunteering rota on a Google sheet.
    """
    def __init__(self, key, gid):
        # List of column headings found in the sheet
        self.headings = []
        # Keys are the dates, values are dictionaries whose keys are the column
        # heading and value is the value in the cell.
        # e.g. self.by_date[date] = {'Teacher (lead)': 'Jo Bloggs', ... }
        self.by_date = {}
        # From https://stackoverflow.com/a/44184071
        sheet_url = f"https://docs.google.com/spreadsheets/d/{key}/export?format=csv&id={key}&gid={gid}"
        self._fetch_sheet(sheet_url)

    def _fetch_sheet(self, sheet_url):
        r = requests.get(sheet_url)
        r.raise_for_status()
        csv_io = io.StringIO(r.text, newline="")
        csv_reader = csv.reader(csv_io)
        for row in csv_reader:
            # Find the headings by assuming the first one is always "Date"
            if row[0] == "Date":
                self.headings = row
                continue

            if self.headings:
                try:
                    day, month, year = [int(n) for n in row[0].split("/")]
                except ValueError:
                    # Ignore anything which doesn't look like a date.
                    continue
                date = datetime.date(year=year, month=month, day=day)
                self.by_date[date] = dict(zip(self.headings, row))
        logging.debug(f"Found {len(self.by_date)} dates in {sheet_url}")

    def next_date(self):
        """
        Return a datetime.date which is the next date on the sheet after or equal to
        the current date.
        """
        today = datetime.date.today()
        future_dates = [date for date in sorted(self.by_date.keys()) if today <= date]
        if future_dates:
            return future_dates[0]
        else:
            return None

    def has_lesson_on_date(self, date):
        """
        Return True if the given date is one where we have a lesson.
        """
        return date in self.by_date

    def whos_on_date(self, date, heading_substring):
        """
        Return a list of all the people on the supplied datetime.date who had
        the given heading, doing a case-insensitive substring match on it so
        you can say "dj" and match "first DJ" and "band/second DJ".

        If a cell for that heading is empty, it is not returned (so if nobody's
        signed up, you get an empty list).

        If no heading matches heading_substring, raises a KeyError, as the
        format of the sheet has probably changed under you.
        """
        d = self.by_date[date]
        substring = heading_substring.lower()
        matching_headings = [heading
                             for heading in self.headings
                             if substring in heading.lower()]
        if not matching_headings:
            raise KeyError(f"Found no headings matching '{heading_substring}'")

        return [d[heading].strip()
                for heading in matching_headings
                if d[heading].strip() != ""]

    def teachers_on_date(self, date):
        "Convenience method for finding the teachers on a given date."
        return self.whos_on_date(date, "teacher ") # trailing space avoids finding "Teacher's notes"

    def volunteers_on_date(self, date):
        "Convenience method for finding the volunteers on a given date."
        return self.whos_on_date(date, "volunteer ")

    def djs_on_date(self, date):
        "Convenience method for finding the DJs on a given date."
        return self.whos_on_date(date, " dj")
