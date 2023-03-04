"""
Retrieve email address given a name on the sign-up sheet.
"""
import collections
import csv
import logging

import config
import utils

class EmailDatabase:
    """
    Holds mapping of names to email addresses.
    """

    def __init__(self, key, gid):
        """
        Read our lookup table from the given Google Sheet.
        """
        self.name_to_email = collections.defaultdict(list)
        csv_reader = csv.DictReader(utils.csv_from_gsheet(key, gid))

        for row in csv_reader:
            email = row["Email address"]
            first_name = row["First name"].lower().strip()
            self.name_to_email[first_name].append(email)
            surname = row.get('Surname', "").lower().strip()
            if surname:
                # Also store the email address under the full name
                self.name_to_email[f"{first_name} {surname}"].append(email)
                # And the first name, first letter of surname
                self.name_to_email[f"{first_name} {surname[0]}"].append(email)

    def get_email_address(self, name):
        """
        Try to find the email address the given name. Returns None if no email
        address is found, or if the name is ambiguous so that more than one
        email address is found. Otherwise, returns the email address.
        """
        name = name.lower().strip()
        names = name.split()
        addresses = []
        # Try building the name up from the space separated parts of it, as
        # we may get a match that way. This is meant to allow for funny
        # spacing in the signup sheet, or people with more than 2 part names.
        running = []
        for n in names:
            running.append(n)
            try_name = " ".join(running)
            if try_name in self.name_to_email:
                # Prefer the more specific, i.e. longer, name, even if we already
                # found some addresses on the previous loop.
                addresses = self.name_to_email[try_name]

        if len(addresses) > 1:
            logging.warning(f"'{name}' is ambiguous, found {addresses}")

        if len(addresses) == 1:
            return addresses[0]
        else:
            return None


# We only want one of these each time we run, so make a singleton
db = EmailDatabase(config.EMAIL_KEY, config.EMAIL_GID)

if __name__ == '__main__':
    # Lookup the name given us on the command line, print the result.
    import sys
    print(db.get_email_address(" ".join(sys.argv[1:])))
