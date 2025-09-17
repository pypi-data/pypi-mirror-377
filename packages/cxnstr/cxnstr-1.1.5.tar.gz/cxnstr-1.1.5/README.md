# cxnstr

Parse database connection strings in python. Currently only supports
MySQL.

    >>> import cxnstr
    >>> params = cxnstr.to_dict("myhost:3306/MyDB?read_default_file=~/.my.cnf")
    >>> params
    {'host': 'myhost', 'port': 3306, 'db': 'MyDB', 'read_default_file': '~/.my.cnf'}
    >>> import pymysql
    >>> conn = pymysql.connect(**params)

See doctests for full connection string specification.

The library also includes a command line program for parsing connection
strings and outputting in various formats:

    $ cxnstr -t json "myhost:3306/MyDB?read_default_file=~/.my.cnf"
    {"read_default_file": "~/.my.cnf", "db": "MyDB", "host": "myhost", "port": 3306}
