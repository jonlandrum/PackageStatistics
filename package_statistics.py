import requests
import gzip
import sqlite3
import sys

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

    def create_contents_database(self):
        """Creates the SQLite3 database in memory"""
        cur = self.conn.cursor()
        command = 'CREATE TABLE contents (' \
                  'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                  'file TEXT, ' \
                  'location TEXT);'
        cur.execute(command)

    def download_contents_index(self):
        """Downloads the relevant contents index file to the current directory.

        Inspiration taken from https://stackoverflow.com/a/62113263/2386514
        for the status bar.
        """
        repository = 'http://ftp.uk.debian.org/debian/dists/stable/main/'
        #             http://ftp.archive.ubuntu.com/ubuntu/dists/trusty/
        url = '{}{}'.format(repository, self.file)
        response = requests.get(url, stream=True, allow_redirects=True)
        if response.status_code == 404:
            sys.exit(
                'The file "{}" does not exist on the remote server'.format(
                    self.file))
        if response.status_code != 200:
            sys.exit(
                'There was an error retrieving the file from the remote server')
        total_size = int(response.headers.get('Content-Length', 0))
        with open(self.file, 'wb') as file, tqdm(
                desc=self.file,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)

    def populate_contents_database(self):
        """Parses the downloaded file and populates the database with the
        file/location pairs
        """
        cur = self.conn.cursor()
        with gzip.open(self.file, 'rb') as f:
            has_pre_text = False
            first_line = f.readline().strip('\n')
            if '/' not in first_line:
                has_pre_text = True
            for line in f:
                words = line.split()
                if has_pre_text:
                    if words[0] == 'FILE' and words[-1] == 'LOCATION':
                        pass
