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
            name = row['Name'].lower().strip()
            self.name_to_email[name].append(email)

    def get_email_address(self, name):
        """
        Try to find the email address the given name. Returns None if no email
        address is found, or if the name is ambiguous so that more than one
        email address is found. Otherwise, returns the email address.
        """
        name = name.lower().strip()
        addresses = set()
        # We don't do a dictionary lookup but rather see whether the name
        # starts with the name from the rota, so that the rota can say "Joe B"
        # or "Joe Bloggs" or "Joe Blo" and all will match someone who gave
        # their name as "Joe Bloggs".
        for db_name, db_addresses in self.name_to_email.items():
            if db_name.startswith(name):
                addresses.update(db_addresses)

        if len(addresses) > 1:
            logging.warning(f"'{name}' is ambiguous, found addresses: {addresses}")

        if len(addresses) == 1:
            return addresses.pop()
        else:
            return None


# We only want one of these each time we run, so make a singleton
db = EmailDatabase(config.EMAIL_KEY, config.EMAIL_GID)

if __name__ == '__main__':
    # Lookup the name given us on the command line, print the result.
    import sys
    print(db.get_email_address(" ".join(sys.argv[1:])))
