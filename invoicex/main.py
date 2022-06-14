#!/usr/bin/env python

import asyncio
from datetime import date, timedelta
import os
import time

import invoicex.reader.github as github
import report
import invoicex.reader.ttrack as ttrack


def cli_parser():
    import argparse

    from dotenv import load_dotenv

    dotenv_path = os.path.join(
        os.path.abspath(os.path.dirname(os.path.dirname(__file__))), ".env"
    )

    load_dotenv(dotenv_path=dotenv_path)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--gh-user",
        dest="gh_user",
        action="store",
        type=str,
        default=None,
        required=True,
        help="The GitHub username.",
    )
    parser.add_argument(
        "--year-month",
        dest="year_month",
        action="store",
        type=str,
        required=True,
        help="Format: YYYY-MM",
    )
    parser.add_argument(
        "--gh-org",
        dest="gh_repos",
        action="append",
        help="Format: org/repo",
    )
    parser.add_argument(
        "--token",
        dest="token",
        action="store",
        type=str,
        default=os.getenv("GITHUB_TOKEN"),
        help="The GitHub access token.",
    )
    parser.add_argument(
        "--timezone",
        dest="timezone",
        action="store",
        type=str,
        default=time.strftime("%z"),
        help="The invoice timezone",
    )
    # TODO: add option for custom output dir
    """
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        action="store",
        type=str,
        default="/tmp/invoicex/",
        help="The output directory for the reports (default: /tmp)",
    )
    """
    parser.add_argument(
        "--ttrack-task",
        dest="ttrack_task",
        action="append",
        type=list,
        required=False,
        default=[],
        help="Task name from TTrack",
    )

    return parser


async def main():
    args = cli_parser().parse_args()
    results = await github.get_data(args)
    await report.generate(results, args)


if __name__ == "__main__":
    asyncio.run(main())
