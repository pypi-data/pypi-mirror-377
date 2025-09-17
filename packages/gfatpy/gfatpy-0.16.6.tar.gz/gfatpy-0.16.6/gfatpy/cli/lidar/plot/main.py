import argparse

from gfatpy.lidar.plot.quicklook import date_quicklook


def main():
    parser = argparse.ArgumentParser(description="usage %prog [arguments]")
    parser.add_argument(
        "-i",
        "--initial_date",
        action="store",
        dest="dateini",
        required=True,
        help="Initial date [example: '20190131'].",
    )
    parser.add_argument(
        "-e",
        "--final_date",
        action="store",
        dest="dateend",
        default=None,
        help="Final date [example: '20190131'].",
    )
    parser.add_argument(
        "-d",
        "--datadir",
        action="store",
        dest="path1a",
        default="GFATserver",
        help="Path where date-hierarchy files are located [example: '~/data/1a'].",
    )
    parser.add_argument(
        "-f",
        "--figuredir",
        action="store",
        dest="figpath",
        default="GFATserver",
        help="Path where figures will be saved [example: '~/radar/quicklooks'].",
    )
    args = parser.parse_args()

    date_quicklook(
        args.dateini, dateend=args.dateend, path1a=args.path1a, figpath=args.figpath
    )


if __name__ == "__main__":
    main()
