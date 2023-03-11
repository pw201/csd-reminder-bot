"""
Utilities used in more than one place.
"""
import collections
import io
import requests

# A type for configuring details of a set of lessons which are found on a
# single tab of a Google Sheet. Typically, all the lessons of a particular
# type on a particular night of the week.
LessonDetails = collections.namedtuple("LessonDetails", ["key", "gid", "min_teachers", "min_volunteers", "min_djs", "extra_text"])

def csv_from_gsheet(key, gid):
    """
    Return a StringIO instance with the CSV data in the given Google Sheet.
    """
    # From https://stackoverflow.com/a/44184071
    sheet_url = f"https://docs.google.com/spreadsheets/d/{key}/export?format=csv&id={key}&gid={gid}"
    req = requests.get(sheet_url)
    req.raise_for_status()
    return io.StringIO(req.text, newline="")
