#!/usr/bin/env python3
"""Wrappers for API of Atlassian Confluence"""
import os
import requests

def parse(resp):
    """Decode HTTP response to JSON"""
    try:
        resp = resp.json()
    except ValueError as error:
        raise RuntimeError('Decoding JSON has failed') from error
    if 'statusCode' in resp or 'status-code' in resp:
        raise RuntimeError(resp)
    return resp

class Confluence:
    """Establish a session with Confluence instance"""
    def __init__(self):
        username = os.getenv('CONF_USER')
        password = os.getenv('CONF_PASS')

        headers = {
            'Content-Type':'application/json',
            'Accept':'application/json',
            'X-Atlassian-Token':'no-check'}

        self.base_url = os.getenv('CONF_ADDR')
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update(headers)

    def rest(self, path) -> str:
        """Construct URL of REST API"""
        return self.base_url + '/rest/api/' + path

class Audit(Confluence):
    """Methods to operate with Audit Log events"""
    def get_records(self, start=None, end=None, search=None):
        """Fetch list of AuditRecord instances dating back to a certain time.

        Keyword arguments are optional, defaults set to None:

        start -- string in format YYYY-MM-DD (server) or Unix Timestamp (cloud)
        end -- string in format YYYY-MM-DD (server) or Unix Timestamp (cloud)
        search -- string to filter the results

        If do not pass any argument, script try to return all available logs.
        """
        params = {
            'startDate': start,
            'endDate': end,
            'searchString': search,
            'start': 0,
            'limit': 1000
        }
        url = self.rest('audit')
        resp = self.session.get(url, params=params)
        resp = parse(resp)
        result = resp['results']
        while 'next' in resp['_links']:
            url = resp['_links']['base'] + resp['_links']['next']
            resp = self.session.get(url, params=params)
            resp = parse(resp)
            result.extend(resp['results'])
        return result

class Spaces(Confluence):
    """Methods to operate with a Confluence spaces"""

    def get(self, s_type=None, status=None, key=None, label=None, expand=None):
        # using s_type to avoid redefining of built-in Python word 'type'
        """Returns the list of spaces sorted alphabetically in ascending order.

        Keyword arguments are optional, defaults set to None:

        key -- filter by single space (key='SPC') or list (key=['SPC1','SPC2'])
        s_type -- type of space could be 'global' or 'personal'
        status -- space could be 'current' (active) or 'archived'
        label -- expect the string (label='Bla') or list (label=['IT','Sales'])
        expand -- comma separated list of space properties to expand in results

        If do not pass any argument, script return all spaces you may access.
        """
        if s_type is not None and s_type not in ['global', 'personal']:
            raise RuntimeError(F'Wrong space type "{s_type}"')
        if status is not None and status not in ['current', 'archived']:
            raise RuntimeError(F'Wrong space status "{status}"')
        params = {
            'spaceKey': key,
            'type': s_type,
            'status': status,
            'expand': expand,
            'label': label,
            'start': 0,
            'limit': 30
        }
        url = self.rest('space')
        resp = self.session.get(url, params=params)
        resp = parse(resp)
        result = resp['results']
        while 'next' in resp['_links']:
            url = resp['_links']['base'] + resp['_links']['next']
            resp = self.session.get(url, params=params)
            resp = parse(resp)
            result.extend(resp['results'])
        return result
