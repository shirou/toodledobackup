==============================================
Toodledo Task Backup Tool
==============================================

What's This
-------------

This tool makes backups about your toodledo tasks into the local DB.

Notice: This tool only make "task" backup. Folders, Contexts, Goals
and Locations are will not backuped.

Requirement
-------------

- Python 2.7 or later

  - If you install `argparse`, you can run under Python 2.6

How to run
------------------

1. obtain Application ID and Application Token from Toodledo.

  - see http://api.toodledo.com/2/account/doc_register.php

2. copy conf.ini.sample to conf.ini.
3. write config.ini.
4. run::

  % python toodlebackup.py -c /path/to/conf.ini

5. write cron if you want

config
-----------

- [USER]
  - email: write your email address which uses in Toodledo.
  - password: your password.

- [TASKS]

  - fields: write fields what you make backup in CSV format.

- [LOG]

  - logdb: full path of logging DB.
  - logfile: full path of logfile (optional).

- [APP]

  - APPID: Application ID from Toodledo.
  - APPTOKEN: Application Token from Toodledo.

Valid fields list
++++++++++++++++++++++++++++++++

- tag, folder, context, goal, location, parent, children, 
- order, duedate, duedatemod, startdate, 
- duetime, starttime, remind, repeat, 
- repeatfrom, status, length, star, 
- added, timer, timeron, note, meta

dump
----------

You can dump to the CSV file format from the log db.

::

  % python toodlebackup.py -c /path/to/conf.ini dump > tasks.csv

Notice: UNIX time stamp will converted to the ISO 8601 format.

cron
-------------

You can set cron to run this tool periodically.

::

  30 21 * * * * python /path/to/toodlebackup.py -c /path/to/conf.ini


Acknowledgement
--------------------

- poodledo -- Toodledo API python module

  - http://code.google.com/p/poodledo/

  - This tool uses some parts of poodledo.
