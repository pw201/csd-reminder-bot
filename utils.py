"""
Utilities used in more than one place.
"""
import collections
import io
import requests

# A type for configuring which sheets we look at, see config.py.
RotaSheet = collections.namedtuple("RotaSheet", ["key", "gid", "min_teachers", "min_volunteers", "min_djs"])

def csv_from_gsheet(key, gid):
    """
    Return a StringIO instance with the CSV data in the given Google Sheet.
    """
    # From https://stackoverflow.com/a/44184071
    sheet_url = f"https://docs.google.com/spreadsheets/d/{key}/export?format=csv&id={key}&gid={gid}"
    req = requests.get(sheet_url)
    req.raise_for_status()
    return io.StringIO(req.text, newline="")
