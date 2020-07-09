import argparse
import logging
from datetime import datetime

from triager.mailer import send_mail
from triager.tablemaker import make_table
from triager.triager import Triager


def run(args):
    # setup logger
    logging_level = logging.DEBUG if args.debug else logging.INFO
    if args.log_to_file:
        logging.basicConfig(filename=args.log_to_file, level=logging_level)
    elif args.log:
        logging.basicConfig(
            format="%(levelname)-10s%(message)s", level=logging_level
        )

    triager = Triager(cfg=args.config_file)
    issues = triager.triage()

    if issues:
        table = make_table(issues)
        logging.info("Printing triaged table to console")
        print(table)

        if args.send_email is True:
            send_mail(
                content=table,
                sender=triager.sender,
                receivers=triager.maintainers,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Triage issues and pull-requests from repositories of interest.",
        prog="Ansible Network Triager",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        dest="config_file",
        action="store",
        help="Path to config file (selects 'config.yaml' in cwd by default)",
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--log-to-file",
        nargs="?",
        const="/tmp/triager-{0}.log".format(
            datetime.now().strftime("%Y-%m-%d-%X")
        ),
        dest="log_to_file",
        help="save logging information to a file",
    )
    group.add_argument(
        "--log", action="store_true", help="display logging data on console",
    )

    parser.add_argument(
        "--debug", action="store_true", help="Bump logging level to debug"
    )

    parser.add_argument(
        "--send-email",
        action="store_true",
        help="send the triaged table as an email to the list of maintainers",
    )

    run(parser.parse_args())