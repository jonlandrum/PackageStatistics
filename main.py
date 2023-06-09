from argparse import ArgumentParser
from package_statistics import PackageStatistics


def parse_args():
    parser = ArgumentParser(description='Reads the contents index file for the specified architecture and prints the'
                                        'statistics of the top ten packages')
    parser.add_argument(
        '-a', '--arch',
        dest='arch',
        required=True,
        help='architecture of the target system',
        type=str)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    PackageStatistics(args.arch)
