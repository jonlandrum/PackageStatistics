import urllib.request
import gzip
import sqlite3

from tqdm import tqdm


class TqdmUpdateTo(tqdm):
    """Displays a download progress bar
    via: https://github.com/tqdm/tqdm/blob/master/examples/tqdm_wget.py"""
    def update_to(self, b=1, bsize=1, tsize=None):
        """Provides an update_to method
        Attributes:
            b:      int, optional
                number of blocks transferred so far [default: 1].
            bsize:  int, optional
                size of each block (in tqdm units) [default: 1].
            tsize:  int, optional
                total size of progress bar (in tqdm units). [default: None]; if None, remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        return self.update(b * bsize - self.n)


class PackageStatistics(object):
    """Reads the contents index file for the specified architecture and prints the statistics of the top ten packages
    Attributes:
        arch:   str
            architecture of the target system.
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
        """Creates the SQLite3 database in the current directory"""
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS contents (id INTEGER PRIMARY KEY AUTOINCREMENT, file, location);')

    def download_contents_index(self):
        """Downloads the relevant contents index file to the current directory"""
        repository = 'http://ftp.uk.debian.org/debian/dists/stable/main/'
        url = '{}{}'.format(repository, self.file)
        with TqdmUpdateTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=url.split('/')[-1]) as prog:
            file, headers = urllib.request.urlretrieve(url, filename=self.file, reporthook=prog.update_to, data=None)
            prog.total = prog.n
