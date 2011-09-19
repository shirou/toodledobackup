#!/usr/bin/env python
# -*- coding: utf-8 -*-

from poodledomini import ApiClient
import ConfigParser
import datetime
import sys
import os
import json

import sqlite3
import argparse

DEFAULT_FIELDS = ["id", "modified", "title", "completed"]
VALID_FIELDS = ["tag", "folder", "context", "goal",
                "location", "parent", "children",
                "order", "duedate", "duedatemod", "startdate",
                "duetime", "starttime", "remind", "repeat",
                "repeatfrom", "status", "length", "star",
                "added", "timer", "timeron", "note", "meta"]
TIME_FIELDS = ["duedate", "startdate", "duetime", "starttime",
               "remind", "modified", "completed", "added"]
SCHEMA="""
create table tasks (
  id integer, -- id
  modified integer, -- modified datetime
  json text -- JSON string
);
"""

def dump(config):
    """
    Dump from task backup db
    """
    
    logdb = config.get('LOG', 'logdb')
    fields = config.get('TASKS','fields').split(",")
    check_fields(fields)
    fields = DEFAULT_FIELDS + fields

    if not os.path.exists(logdb):
        print("logdb is not exits at " + logdb)
        exit(1)
    conn = sqlite3.connect(logdb)
    c = conn.cursor()

    c.execute("SELECT id, modified, json FROM tasks ORDER BY modified")
    tasks = c.fetchall()
    print ",".join(fields) # print header
    for task in tasks:
        j = json.loads(task[2])

        # convert UNIX timestamp to ISO 8801 format 
        for f in TIME_FIELDS:
            if f in j.keys():
                time = int(j[f])
                if time != 0:
                    j[f] = str(datetime.datetime.fromtimestamp(time))
                    
        data = []
        for f in fields:
            tmp = j[f]
            if isinstance(tmp, basestring):
                data.append('"' + tmp + '"')
            else:
                data.append('"' + str(tmp) + '"')
                
        print ",".join(data)

def append(config, tasks):
    """
    insert task to DB
    """
    
    logdb = config.get('LOG', 'logdb')
    # this time, not checked    
    fields = config.get('TASKS','fields').split(",")
    fields = DEFAULT_FIELDS + fields

    logfd = None
    if config.has_option('LOG', 'logfile'):
        logfile = config.get('LOG', 'logfile')
        logfd = open(logfile, "a")
    
    firstTime = False
    if not os.path.exists(logdb):
        firstTime = True
    conn = sqlite3.connect(logdb)

    # create table if db is not exists
    if firstTime:
        conn.execute(SCHEMA)
        conn.commit()

    insert_query = ""
    for task in tasks:
        if "total" in task:
            continue
        _id = task['id']
        _modified = task['modified']
        
        q = """SELECT * FROM tasks
        WHERE id = {0} AND
        modified = {1}""".format(_id, _modified)
        
        cur = conn.cursor()
        cur.execute(q)
        ret = cur.fetchone()
        if not ret:
            s = json.dumps(task)
            insert_query += """INSERT INTO tasks VALUES
            ({0}, {1},'{2}');\n""".format(_id, _modified, s)

            datestr = str(datetime.datetime.fromtimestamp(_modified))
            if logfd:
                logfd.write("Add: id={0} modified={1}".format(_id, datestr));

    if insert_query:
        with conn:
            conn.executescript(insert_query)

    conn.close()
    if logfd:
        logfd.close()
    
def auth(config, cli):
    """
    Authentication to the toodledo 
    """
    
    email = config.get('USER','email')
    password = config.get('USER','password')

    key = cli.authenticate(email, password)

    return key

def check_fields(fields):
    """
    check user input fields are valid or not.
    """
    
    diff = set(fields).difference(VALID_FIELDS + DEFAULT_FIELDS)
    
    if len(diff) > 0:
        print(", ".join(diff) + " is(are) not valid fields name.")

def getTasks(config, cli, key):
    """
    get task list from toodledo.
    """
    
    fields = config.get('TASKS','fields').split(",")
    check_fields(fields)

    # remove DEFAULT_FIELDS
    fields = list(set(fields).difference(DEFAULT_FIELDS))
    
    tasks = cli.getTasks(key=key,fields=",".join(fields))

    return tasks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Toodledo task backup tool')
    parser.add_argument('-c', '--config',
                        required=True,
                        help='config file path')
    parser.add_argument('command',
                        nargs='?',
                        help='command (default: backup)',
                        default='log')

    args = parser.parse_args()

    conf = args.config
    
    config = ConfigParser.RawConfigParser()
    config.read(conf)

    if args.command == 'backup':
        appid = config.get('APP','APPID')
        apptoken = config.get('APP','APPTOKEN')
        cli = ApiClient(application_id=appid,
                        app_token=apptoken)

        key = auth(config, cli)
        tasks = getTasks(config, cli, key)

        append(config, tasks)
    else:
        dump(config)
