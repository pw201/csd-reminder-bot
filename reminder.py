import argparse
import logging

from rota import Rota



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", help="Google sheet key", required=True)
    parser.add_argument("-g", "--gid", help="Google sheet ID (for the individual sheet)", required=True)
    parser.add_argument("-t", "--teachers", help="Number of teachers, warn if there are less than the given number", type=int)
    parser.add_argument("-v", "--volunteers", help="Number of volunteers, warn if there are less than the given number", type=int)
    parser.add_argument("-d", "--djs", help="Number of DJs, warn if there are less than the given number", type=int)

    args = parser.parse_args()
    sheet_url = f"https://docs.google.com/spreadsheets/d/{args.key}/export?format=csv&id={args.key}&gid={args.gid}"
    rota = Rota(sheet_url)
    next_lesson = rota.next_date()

    if args.teachers:
        send_emails(role="Teacher", ) # TODO

if __name__ == "__main__":
    main()

