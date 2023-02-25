import csv
import datetime
import io
import requests


SHEET_URL="https://docs.google.com/spreadsheets/d/***REMOVED***/gviz/tq?tqx=out:csv&sheet=1407312817&headers=0"
SHEET_URL="https://docs.google.com/spreadsheets/d/***REMOVED***/export?format=csv&id=***REMOVED***&gid=1407312817"

class Rota(object):
    """
    Represent the teaching/volunteering rota on a Google sheet.
    """
    def __init__(self, sheet_url):
        # List of column headings found in the sheet
        self.headings = []
        # Keys are the dates, values are dictionaries whose keys are the column
        # heading and value is the value in the cell.
        # e.g. self.by_date[date] = {'Teacher (lead)': 'Jo Bloggs', ... }
        self.by_date = {}
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

    def next_date(self):
        """
        Return a datetime.date which is the next date on the sheet after (or equal to)
        the current date.
        """
        today = datetime.date.today()
        future_dates = [date for date in sorted(self.by_date.keys()) if today <= date]
        if future_dates:
            return future_dates[0]
        else:
            return None

    def whos_on_date(self, date, heading_substring):
        """
        Return a list of all the people on the supplied datetime.date who had
        the given heading, doing a case-insensitive substring match on it so
        you can say "DJ" and match "first DJ" and "band/second DJ".

        If a cell for that heading is empty, it is not returned. If nothing
        matches, returns an empty list.
        """
        d = self.by_date[date]
        heading_substring = heading_substring.lower()
        return [d[heading].strip()
                for heading in self.headings
                if heading_substring in heading.lower() and d[heading].strip() != ""]

    def teachers_on_date(self, date):
        "Convenience method for finding the teachers on a given date."
        return self.whos_on_date(date, "teacher ") # trailing space avoids finding "Teacher's notes"

    def volunteers_on_date(self, date):
        "Convenience method for finding the volunteers on a given date."
        return self.whos_on_date(date, "volunteer ")

    def djs_on_date(self, date):
        "Convenience method for finding the DJs on a given date."
        return self.whos_on_date(date, " dj")


if __name__ == "__main__":
    s = Rota(SHEET_URL)
    import pdb; pdb.set_trace()

