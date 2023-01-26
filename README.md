Package Statistics
==================

A CLI program for outputting package statistics for a given Debian repository. The data is gathered from Debian context files within the repository for a given system architecture.

File Definition
---------------
The specification of the content index file is provided at [wiki.debian.org](https://wiki.debian.org/DebianRepository/Format?action=show&redirect=RepositoryFormat#A.22Contents.22_indices):

> The files `dists/$DIST/$COMP/Contents-$SARCH.gz` (and `dists/$DIST/$COMP/Contents-udeb-$SARCH.gz` for udebs) are so called Contents indices. The variable `$SARCH` means either a binary architecture or the pseudo-architecture "`source`" that represents source packages. They are optional indices describing which files can be found in which packages. Prior to Debian wheezy, the files were located below "`dists/$DIST/Contents-$SARCH.gz`".
>
> Contents indices begin with zero or more lines of free form text followed by a table mapping filenames to one or more packages. The table SHALL have two columns, separated by one or more spaces. The first row of the table SHOULD have the columns "FILE" and "LOCATION", the following rows shall have the following columns:
>
> 1. A filename relative to the root directory, without leading .
> 2. A list of qualified package names, separated by comma. A qualified package name has the form `[[$AREA/]$SECTION/]$NAME`, where `$AREA` is the archive area, `$SECTION` the package section, and `$NAME` the name of the package. Inclusion of the area in the name should be considered deprecated.
>
> Clients should ignore lines not conforming to this scheme. Clients should correctly handle file names containing white space characters (possibly taking advantage of the fact that package names cannot include white space characters).

Assumptions
-----------
The format definition of the contents index file gives two vague specifications:

1. If the file has free-form text at its beginning, there is no apparent requirement that the file also have table headers (by using the weaker directive "SHOULD" instead of "SHALL").
2. If the file has free-form text at its beginning and does *not* have headers before the table, there is no defined way to determine if the current line is part of the table. The reason for this is because the free-form text can contain any value, including even an example line that would be found within the table in order to explain the format. As such, any method for parsing a line of text to determine if it is part of the table or not that does not also take into account the context of its surrounding lines would conclude that the current line is part of the table, and this conclusion would be erroneous.

Additionally, there is also no specified method to determine if an arbitrary file has free-form text before its table or not without first parsing the file to search for the table headers. Since there is no size limit imposed on this free-form text, in the worst case scenario the file would have to be parsed to its last line before determining if the file contains table headers. As the uncompressed content index files can be many hundreds of megabytes in size, this approach is not practical.

A potential solution is to test the first line of the file to see if it contains the `/` character. This character can be chosen since it is used within the content index description to indicate a directory change. However, this approach won't work because of the previously noted example that the free-form text area can contain anything, including even an example line from the table. Furthermore, there is no requirement that either the package name or the path contain a `/`.

Another potential solution is to test the first line to see if there are multiple successive space characters at any point in the line, as this could indicate the line is an entry from the table. However, this approach also will not work as there is no requirement that the file and location be separated by multiple spaces; only a single space is mandatory. Additionally, many people still use the archaic two-space separator between sentences, and this would erroneously trigger the algorithm to conclude the current line is an entry from the table. Notwithstanding these issues, this approach still fails because of the previously noted example that the free-form text area can contain anything.

A somewhat workable solution is to split the line into its right and left sides based on the specification that a package name cannot contain a whitespace character, and then test the left side to see if it contains a `/` character, with the caveat that file names most likely will not be in the root directory, and that the first line of the free-form text area will not contain a `/` character.

For these reasons, I have programmed this script on the following assumptions:
1. **IF** the file has free-form text, then it also **MUST** have table headers
2. **IF** the first line of the file contains a `/` character, then this line **MUST** be determined to be the first entry in the table.
3. **IF** the first line of the file can be determined to fit the pattern of an entry from the table, then the file **MUST** be parsed as if it has **NO** free-form text and **NO** table headers before the table data.

If the file does not conform to these assumptions, it will be treated as an improperly formatted content index file and a notification of such will be printed to the console.

If the file requested is not found on the remote server, a notification of such will be printed to the console.
