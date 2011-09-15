#!/usr/bin/env python
# -*- coding: utf-8 -*-

from poodledomini import ApiClient
import ConfigParser
import datetime
import sys
import os
import json

import sqlite3

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
    logdb = config.get('LOG', 'logdb')
    # this time, not checked
    fields = config.get('TASKS','fields').split(",")
    fields = DEFAULT_FIELDS + fields

    if not os.path.exists(logdb):
        print("logdb is not exits at " + logdb)
        exit(1)
    conn = sqlite3.connect(logdb)
    c = conn.cursor()

    c.execute("SELECT id, modified, json FROM tasks")
    tasks = c.fetchall()
    for task in tasks:
        j = json.loads(task[2])

        for f in TIME_FIELDS:
            if f in j.keys():
                time = int(j[f])
                if time != 0:
                    j[f] = str(datetime.datetime.fromtimestamp(time))
        print j

def append(config, tasks):
    logdb = config.get('LOG', 'logdb')
    # this time, not checked
    fields = config.get('TASKS','fields').split(",")
    fields = DEFAULT_FIELDS + fields

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
            print _id, _modified
            s = json.dumps(task)
            insert_query += """INSERT INTO tasks VALUES
            ({0}, {1},'{2}');\n""".format(_id, _modified, s)

    if insert_query:
        with conn:
            conn.executescript(insert_query)

    conn.close()
    
def auth(config, cli):
    email = config.get('USER','email')
    password = config.get('USER','password')

    key = cli.authenticate(email, password)
    #key ="b97068324fba89a6caa7f3f23b9263bf"
    
    return key

def check_fields(fields):
    diff = set(fields).difference(VALID_FIELDS + DEFAULT_FIELDS)
    
    if len(diff) > 0:
        print(", ".join(diff) + " is(are) not valid fields name.")

def getTasks(config, cli, key):
    fields = config.get('TASKS','fields').split(",")
    check_fields(fields)

    # remove DEFAULT_FIELDS
    fields = list(set(fields).difference(DEFAULT_FIELDS))
    
    tasks = cli.getTasks(key=key,fields=",".join(fields))

    return tasks


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "specify config file path."
        print "ex: " + sys.argv[0] + " <config file path>"
        exit(1)
        
    conf = sys.argv[1]
    
    config = ConfigParser.RawConfigParser()
    config.read(conf)

    appid = config.get('APP','APPID')
    apptoken = config.get('APP','APPTOKEN')
    cli = ApiClient(application_id=appid,
                    app_token=apptoken)

    key = auth(config, cli)
    tasks = getTasks(config, cli, key)
    append(config, tasks)
#    dump(config)
