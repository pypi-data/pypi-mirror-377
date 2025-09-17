"""Parse database connection strings"""

from __future__ import print_function

import argparse
import json

import six
from six.moves import urllib


def _escape_string(s):
    new_s = ''
    s_iter = iter(s)
    for c in s_iter:
        if c == '\\':
            new_s += urllib.parse.quote(next(s_iter), safe='')
        elif c == '%':
            new_s += urllib.parse.quote(c, safe='')
        else:
            new_s += c
    return new_s


def _unescape_dict(d):
    new_d = {}
    for k, v in d.items():
        if isinstance(v, six.string_types) and '%' in v:
            new_d[k] = urllib.parse.unquote(v)
        else:
            new_d[k] = v
    return new_d


def to_dict(s, assume_my_cnf=True):
    """Convert connection string s into a dict suitable for use with connect().

    Only mysql is supported. If you leave off the leading 'mysql://', it will
    be assumed.

    If assume_my_cnf is True, assume read_default_file=~/.my.cnf if
    read_default_file isn't specified in the string.

    Characters that have meaning in URLs (@, #, /, etc.) need to be backslash
    escaped.

    To simplify parsing, there are a few limitations:
      - no quotes (single or double) are allowed in the string
      - read_default_file is the only option supported at this time

    >>> to_dict('mysql://localhost/') == {'host': 'localhost', 'read_default_file': '~/.my.cnf'}
    True
    >>> to_dict('mysql://localhost/?read_default_file=test.cnf') == {'host': 'localhost', 'read_default_file': 'test.cnf'}
    True
    >>> to_dict('mysql://localhost/Blah', False) == {'host': 'localhost', 'db': 'Blah'}
    True
    >>> to_dict('mysql://localhost/Blah?read_default_file=~/.my.cnf') == {'host': 'localhost', 'db': 'Blah', 'read_default_file': '~/.my.cnf'}
    True
    >>> to_dict('mysql://localhost:1234/Blah', False) == {'host': 'localhost', 'db': 'Blah', 'port': 1234}
    True
    >>> to_dict('mysql://person@localhost:1234/Blah', False) == {'host': 'localhost', 'db': 'Blah', 'port': 1234, 'user': 'person'}
    True
    >>> to_dict('mysql://person:xyz234@localhost:1234/Blah', False) == {'host': 'localhost', 'db': 'Blah', 'port': 1234, 'user': 'person', 'passwd': 'xyz234'}
    True
    >>> to_dict('localhost', False) == {'host': 'localhost'}
    True
    >>> to_dict('localhost:1234', False) == {'host': 'localhost', 'port': 1234}
    True
    >>> to_dict('person:XY\\:\\@\\/Tax2\\#@localhost', False) == {'host': 'localhost', 'user': 'person', 'passwd': 'XY:@/Tax2#'}
    True
    """
    d = {}

    if '"' in s or "'" in s:
        raise ValueError("Quote character found in connection string")

    if '://' not in s:
        s = 'mysql://' + s
    s = _escape_string(s)
    parsed = urllib.parse.urlparse(s)
    if parsed.scheme != 'mysql':
        raise ValueError("scheme must be 'mysql'")

    # query
    q = urllib.parse.parse_qs(parsed.query)
    if 'read_default_file' in q:
        d['read_default_file'] = q['read_default_file'][0]
    elif assume_my_cnf:
        d['read_default_file'] = '~/.my.cnf'

    # path
    if len(parsed.path) > 1:
        d['db'] = parsed.path[1:]

    # netloc
    if '@' in parsed.netloc:
        auth, host = parsed.netloc.split('@')
        if ':' in auth:
            d['user'], d['passwd'] = auth.split(':')
        else:
            d['user'] = auth
    else:
        host = parsed.netloc
    if ':' in host:
        d['host'], port = host.split(':')
        d['port'] = int(port)
    else:
        d['host'] = host

    d = _unescape_dict(d)
    return d


def dict_to_perl(d):
    """Convert a dict into a string representing a Perl hash.

    The hash is meant to be eval'd by Perl code and then used to connect via
    DBI->connect(). Something like this:

        my %params = eval(<output of this function>);
        my $dbh = DBI->connect($params{"cxnstr"}, $params{"user"}, $params{"passwd"});

    The keys of the returned hash will be "cxnstr", "user", and "passwd".

    NEVER USE THIS FUNCTION WITH UNTRUSTED INPUT!

    >>> dict_to_perl({'host': 'localhost'})
    '("cxnstr", "DBI:mysql::localhost:;", "user", undef, "passwd", undef)'
    >>> dict_to_perl({'host': 'localhost', 'port': 123})
    '("cxnstr", "DBI:mysql::localhost:123;", "user", undef, "passwd", undef)'
    >>> dict_to_perl({'host': 'localhost', 'port': 123, 'db': 'Blah'})
    '("cxnstr", "DBI:mysql:Blah:localhost:123;", "user", undef, "passwd", undef)'
    >>> dict_to_perl({'host': 'localhost', 'port': 123, 'db': 'Blah', 'read_default_file': '~/.my.cnf'})
    '("cxnstr", "DBI:mysql:Blah:localhost:123;mysql_read_default_file=~/.my.cnf", "user", undef, "passwd", undef)'
    >>> dict_to_perl({'host': 'localhost', 'port': 123, 'db': 'Blah', 'user': 'person'})
    '("cxnstr", "DBI:mysql:Blah:localhost:123;", "user", "person", "passwd", undef)'
    >>> dict_to_perl({'host': 'localhost', 'port': 123, 'db': 'Blah', 'user': 'person', 'passwd': 'goldfish'})
    '("cxnstr", "DBI:mysql:Blah:localhost:123;", "user", "person", "passwd", "goldfish")'
    """
    d = d.copy()
    perl_cxnstr = 'DBI:mysql:{db}:{host}:{port};'
    perl_cxnstr = perl_cxnstr.format(
        db=d.get('db', ''),
        host=d.get('host', ''),
        port=d.get('port', '')
    )
    if 'read_default_file' in d:
        perl_cxnstr += 'mysql_read_default_file=' + d['read_default_file']
    rv = '("cxnstr", "{perl_cxnstr}", "user", {user}, "passwd", {passwd})'
    rv = rv.format(
        perl_cxnstr=perl_cxnstr,
        user='"' + d['user'] + '"' if 'user' in d else 'undef',
        passwd='"' + d['passwd'] + '"' if 'passwd' in d else 'undef'
    )
    return rv


def dict_to_mysql_cli_args(d):
    """Convert a dict into a list of args to the MySQL Client CLI.

    The global my.cnf file is explicitly ignored if 'read_default_file' is not
    in d.

    If 'passwd' is in d, the password will be passed on the command line, which
    means that other users will be able to see it.

    NEVER USE THIS FUNCTION WITH UNTRUSTED INPUT!

    >>> dict_to_mysql_cli_args({'host': 'localhost'})
    ['--defaults-file=', '-h', 'localhost']
    >>> dict_to_mysql_cli_args({'host': 'localhost', 'port': 123})
    ['--defaults-file=', '-h', 'localhost', '-P', '123']
    >>> dict_to_mysql_cli_args({'host': 'localhost', 'port': 123, 'db': 'Blah'})
    ['--defaults-file=', '-h', 'localhost', '-P', '123', 'Blah']
    >>> dict_to_mysql_cli_args({'host': 'localhost', 'port': 123, 'db': 'Blah', 'read_default_file': '~/.my.cnf'})
    ['--defaults-file=~/.my.cnf', '-h', 'localhost', '-P', '123', 'Blah']
    >>> dict_to_mysql_cli_args({'host': 'localhost', 'port': 123, 'db': 'Blah', 'user': 'person'})
    ['--defaults-file=', '-h', 'localhost', '-P', '123', '-u', 'person', 'Blah']
    >>> dict_to_mysql_cli_args({'host': 'localhost', 'port': 123, 'db': 'Blah', 'user': 'person', 'passwd': 'goldfish'})
    ['--defaults-file=', '-h', 'localhost', '-P', '123', '-u', 'person', '--password=goldfish', 'Blah']
    """
    args = []
    args.append('--defaults-file={}'.format(d.get('read_default_file', '')))
    if 'host' in d:
        args.extend(['-h', d['host']])
    if 'port' in d:
        args.extend(['-P', str(d['port'])])
    if 'user' in d:
        args.extend(['-u', d['user']])
    if 'passwd' in d:
        args.append('--password={}'.format(d['passwd']))
    if 'db' in d:
        args.append(d['db'])
    return args


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('-t', '--to', choices=['json', 'mysql-cli', 'perl'], default='json')
    ap.add_argument('connection_string')
    args = ap.parse_args()

    d = to_dict(args.connection_string)
    if args.to == 'mysql-cli':
        print(' '.join(['mysql'] + dict_to_mysql_cli_args(d)))
    elif args.to == 'perl':
        print(dict_to_perl(d))
    elif args.to == 'json':
        print(json.dumps(d))


if __name__ == '__main__':
    main()
