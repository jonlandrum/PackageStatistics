import gzip
import requests
import sqlite3
import sys

from time import time
from tqdm import tqdm


class PackageStatistics(object):
    """Reads the contents index file for the specified architecture and prints
    the statistics of the top ten packages

    Attributes:
        arch:   str
            architecture to query
    """
    def __init__(self, arch=''):
        """Initialize this instance with supplied values"""
        self.arch = arch
        self.conn = sqlite3.connect(':memory:')
        self.file = 'Contents-{}.gz'.format(self.arch)
        self.print_packages()

    def print_packages(self):
        """Prints the top ten packages of the repository."""
        self.create_contents_database()
        self.download_contents_index()
        self.populate_contents_database()
        cur = self.conn.cursor()
        cur.execute("""
            SELECT location, COUNT(*) as number
            FROM contents
            GROUP BY location
            ORDER BY number DESC
            LIMIT 10;
        """)
        results = cur.fetchall()
        line = 1
        print('Rank\t{:<40}\tCount'.format('Package'))
        print('-------------------------------------------------------------')
        for result in results:
            print('{:>3}.\t{:<40}\t{}'.format(line, result[0], result[1]))
            line = line + 1

    def create_contents_database(self):
        """Creates the SQLite3 database in memory"""
        cur = self.conn.cursor()
        command = """
        CREATE TABLE contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT,
            location TEXT
        );
                  """
        cur.execute(command)

    def download_contents_index(self):
        """Downloads the relevant contents index file to the current directory.

        Inspiration taken from https://stackoverflow.com/a/62113263/2386514
        for the progress bar.
        """
        repository = 'http://ftp.uk.debian.org/debian/dists/stable/main/'
        # repository = 'http://ftp.archive.ubuntu.com/ubuntu/dists/trusty/'
        url = '{}{}'.format(repository, self.file)
        response = requests.get(url, stream=True, allow_redirects=True)
        if response.status_code == 404:
            sys.exit(
                'The file "{}" does not exist on the remote server'.format(
                    self.file))
        if response.status_code != 200 and \
                response.status_code != 301 and \
                response.status_code != 302:
            sys.exit(
                'There was an error retrieving the file from the remote server')
        total_size = int(response.headers.get('Content-Length', 0))
        with open(self.file, 'wb') as file, tqdm(desc=self.file,
                                                 total=total_size,
                                                 unit='iB', unit_scale=True,
                                                 unit_divisor=1024) as prog:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                prog.update(size)

    def populate_contents_database(self):
        """Parses the downloaded file and populates the database with the
        file/location pairs
        """
        cur = self.conn.cursor()
        with gzip.open(self.file, 'rt', encoding='ISO-8859-1') as f:
            first_line = f.readline().strip('\n')
            f.seek(0, 0)
            if '/' not in first_line:  # See README.md for explanation
                words = first_line.rsplit(' ', 1)
                while words[0] != 'FILE' and words[-1] != 'LOCATION':
                    line = f.readline().strip('\n').strip()
                    words = line.rsplit(' ', 1)
                f.readline().strip('\n').strip()
            print('Processing', end='', flush=True)
            start = time()
            for line in f:
                words = line.strip().rsplit(' ', 1)
                file, locations = words[0].strip(), words[-1].split(',')
                for location in locations:
                    cur.execute("""
                        INSERT INTO contents (file, location) VALUES (?, ?)
                    """, (file, location))
                    now = time() - start
                    if now > 0 and now % 1 == 0: print('.', end='', flush=True)
            print()
