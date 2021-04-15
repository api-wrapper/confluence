#!/usr/bin/env python3
"""Wrappers for API of Atlassian Confluence"""
import os
from time import sleep
import json
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

    def rpc(self) -> str:
        """Construct URL of RPC API (deprecated)"""
        return self.base_url + '/rpc/json-rpc/confluenceservice-v2'

    def download(self, url, filename=None):
        """Download the file to current folder. Optionally set filename"""
        # kudos to https://stackoverflow.com/a/16696317 for this code
        if filename is None:
            filename = url.split('/')[-1]
        with self.session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return filename

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

    def export(self, key, scheme='XML', save_as=None):
        """Export the space using deprecated RPC API (unavailable in Cloud).
        Confluence export the space compressed in ZIP archive.
        Exported archive authomatically downloads to current directory.

        key -- mandatory variable, identifier of space.
        scheme -- XML (default) or HTML. Case-sensitive.
        save_as -- optionally set the name and extension of downloaded file.
        """
        url = self.rpc()
        data = json.dumps({
            'jsonrpc': 2.0,
            'method': 'exportSpace',
            'params': [
                key,
                'TYPE_' + scheme,
                'true'
            ],
            'id': 12345})

        resp = self.session.post(url, data=data)
        resp = parse(resp)

        url = resp['result']

        if save_as is None:
            self.download(url)
        else:
            self.download(url, filename=save_as)

    def delete(self, key):
        """Initiate deletion of space and waiting for process completion.
           key -- mandatory string variable. The key of the space to delete.
        """
        url = self.rest('space/' + key)
        resp = self.session.delete(url)
        resp = parse(resp)

        url = self.base_url + resp['links']['status']
        resp = self.session.get(url)
        resp = parse(resp)
        while resp['percentageComplete'] < 100:
            resp = self.session.get(url)
            resp = parse(resp)
            sleep(1)
