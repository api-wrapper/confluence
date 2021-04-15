## Python for Confluence API

Repository provide the wrappers for some Atlassian Confluence API endpoints.
File [confluence_api.py](confluence_api.py) contain available methods and this Readme show how to use them.

Wrappers support the [API pagination](https://developer.atlassian.com/server/confluence/pagination-in-the-rest-api/).

Names of classes and methods attempt to follow the official API documentation from:
- https://docs.atlassian.com/ConfluenceServer/rest/7.11.1/ (Confluence Server and Data Center)
- https://developer.atlassian.com/cloud/confluence/rest/ (for Confluence Cloud)

Sometimes wrappers may have a different names for some methods if Atlassian naming overlap with built-in Python names.

API for Cloud and on-premise Confluence versions may have some differences. This code trying implement the common methods first and add custom methods later if it will be required.

### Requiremens

- Python 3.6+
- Python [Requests](https://requests.readthedocs.io/en/master/) library
- Some API endpoints require Confluence administrator permissions or not available in Free license. In such cases API return informative error message.

### Usage

Assuming you have a Linux installed:

```bash
$ git clone https://github.com/api-wrapper/confluence.git
$ cd confluence/

# Install Python dependencies:
$ pip3 install -r ./requirements.txt --user

# Set environment variables:
$ export CONF_ADDR="" # URL of your Confluence instance
$ export CONF_USER="" # email or username of Confluence user
$ export CONF_PASS="" # password or API token
```

### Documentation
Code documented with Python [Docstrings](https://www.python.org/dev/peps/pep-0257/#what-is-a-docstring).
You may review built-in help with command like this:
```bash
$ pydoc3 ./confluence_api.py
```

### Examples

> :warning: **Running the code may lead to information change or removal. Use with caution.**

Examples described with Python command-line interface. Assuming the OS is Linux, need open the shell and enter:

```bash
$ python3
```
This open the window similar to:

```python
Python 3.6.9 (default, Apr 12 2021, 14:00:00)
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```
Type the examples after `>>>`. Press Enter to execute.

##### Get audit records

This code return audit records with a word 'Space' registered during 2 months.
Note: Access require admin privileges. Audit not available in Confluence Free edition.

```python
>>> from confluence_api import Audit
>>> audit = Audit()
>>> audit.get_records(start='2021-01-01', end='2021-03-01', search='Space')
```

You may omit passing the filter parameters, but in large instances this query may execute quite long.
```python
>>> audit.get_records()
```

##### Get list of spaces

Query show all spaces available for account which execute the request. It may optionally expand  returned parameters. [More about expansions in API](https://developer.atlassian.com/server/confluence/expansions-in-the-rest-api/).

```python
>>> from confluence_api import Spaces
>>> spaces = Spaces()
>>> spaces.get(expand='homepage')
```

You may also filter results:
```python
>>> spaces.get(key='SPACEKEY1')
>>> spaces.get(key=['SPACEKEY1','SPACEKEY2'])

>>> spaces.get(s_type='global')
>>> spaces.get(s_type='personal')

>>> spaces.get(status='current')
>>> spaces.get(status='archived')
```

Filters also can be combined:
```python
>>> spaces.get(s_type='personal', status='archived')
```
Retrieving and filtering the spaces also shown in [example_spaces_delete.py](example_spaces_delete.py).

##### Export the space

This method depends on using RPC API which known as deprecated. RPC API calls not supported in Confluence Cloud.

This code will be changed if we will find corresponding functional in upcoming versions of REST API for Confluence Cloud and Data Center.

```python
>>> from confluence_api import Spaces
>>> spaces = Spaces()
>>> spaces.export('SPACEKEY', save_as='example.zip')
```
This exports the space in XML format (Confluence automatically zip files to archive) and download archive to current folder.

Variable `save_as` is optional - you may skip it and use defaults proposed by Confluence.

Default XML export could be later imported to Confluence. Optionally you may format by adding argument `scheme='HTML'`

##### Delete the space

```python
>>> from confluence_api import Spaces
>>> spaces = Spaces()
>>> spaces.delete('SPACEKEY')
```
Script [example_spaces_delete.py](example_spaces_delete.py) show how to filter the spaces by specific description and remove them in loop.
