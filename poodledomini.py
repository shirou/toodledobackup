#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# http://api.toodledo.com/2/index.php
#

import os
import urllib
import urllib2

import json
import time
from datetime import datetime, timedelta

try:
    from hashlib import md5
except ImportError:
    from md5 import md5



def check_api_key(f):
    ''' A decorator that makes the decorated function check for a API key'''
    def fn(*args, **kwargs):
        self = args[0]
        # check if key is set to a value
        if 'key' in kwargs and kwargs['key'] is not None:
            return f(*args, **kwargs)
        else:
            # try to get the key from the ApiClient
            if self.key is not None:
                kwargs['key'] = self.key
                return f(*args, **kwargs)
            else:
                raise PoodledoError('need API key to call function %s' % f.__name__)
    return fn

class ApiClient(object):
    ''' Toodledo API client'''
    _SERVICE_URL = 'http://api.toodledo.com/2/'
    _SERVICE_URL_SSL = 'http://api.toodledo.com/2/'

    def __init__(self, key=None, application_id=None, app_token=None):
        ''' Initializes a new ApiClient w/o auth credentials'''
        self._urlopener = urllib2.build_opener()

        if application_id and app_token:
            self.application_id = application_id
            self.app_token = app_token
        else:
            raise KeyError("App ID and App token are required.")

    def _create_url(self,**kwargs):
        ''' Creates a request url by appending key-value pairs to the SERVICE_URL'''

        if "scheme" in kwargs and "https" in kwargs["scheme"]:
            url = ApiClient._SERVICE_URL_SSL
            del(kwargs["scheme"])
        else:
            url = ApiClient._SERVICE_URL

        url += kwargs["path"]
        del(kwargs["path"])
        kwargs["appid"] = self.application_id
        if "passwd" in kwargs:
            kwargs["pass"] = kwargs["passwd"]
            del(kwargs["passwd"])
        
        # add args to url (key1=value1;key2=value2)
        # trailing underscores are stripped from keys to allow keys like pass_
        url += ';'.join(key.rstrip('_') + '=' + urllib2.quote(str(kwargs[key])) for key in sorted(kwargs))
        return url

    def _call(self, **kwargs):            
        url = self._create_url(**kwargs)
        stream = self._urlopener.open(url)
        return json.loads(stream.read())

    def authenticate(self, email, passwd):
        ''' 
            Uses credentials to get userid, token and auth key.

            Returns the auth key, which can be cached and used later in the constructor in 
            order to skip authenticate()
        '''
        
        self.userid = self.getUserid(email, passwd)

        self.signature = md5(self.userid + self.app_token).hexdigest()

        self.session_token = self.getToken(self.signature, self.userid)
        self.key = self._generateKey(self.app_token, self.session_token, passwd)
        return self.key

    @property
    def isAuthenticated(self):
        return bool(self.key is not None)

    def _generateKey(self, app_token, session_token, passwd):
        ''' Generates a key as specified in the API docs'''
        return md5(md5(passwd).hexdigest() + app_token + session_token ).hexdigest()

    def getToken(self, sig, userid):
        ret = self._call(path='account/token.php?',
                         vers=21,
                         userid=userid,
                         sig=sig,
                         scheme="https")

        if 'errorCode' in ret:
            raise Exception(ret['errorDesc'])
        
        token = ret['token']
        if token == '1':
            raise Exception('could not get token.')
        return token
    
    def getUserid(self, email, passwd):
        sig = md5(email+self.app_token).hexdigest()

        userid = self._call(path='account/lookup.php?',
                            email=email,
                            passwd=passwd,
                            sig=sig,
                            scheme="https")['userid']
        if userid == '1':
            raise KeyError('invalid username/password')
        return userid 

    @check_api_key
    def getTasks(self, key=None, **kwargs):
        return self._call(path='tasks/get.php?', key=key, **kwargs)
