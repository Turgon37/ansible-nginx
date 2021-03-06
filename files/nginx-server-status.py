#!/usr/bin/env python

import argparse
import base64
import json
import urllib2
import re
import sys


# RETRIEVE INFORMATIONS
if __name__ == '__main__':
    # Create parser
    parser = argparse.ArgumentParser(description='Command line utility to query stats from nginx status virtual host')
    parser.add_argument('-P', '--port', action='store', type=int,
                        dest='port', default=80,
                        help='The port on which to call web endpoint')
    parser.add_argument('-u', '--url', action='store',
                        dest='url',
                        help='The url on which to call web endpoint')
    parser.add_argument('-l', '--login', action='store', dest='login',
                        help='optional username')
    parser.add_argument('-p', '--password', action='store', dest='password',
                        help='optional password')
    parser.add_argument('-t', '--timeout', action='store', dest='timeout',
                        default=1, help='timeout in seconds')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        default=False, help='Enable output of errors')

    args = parser.parse_args()
    if args.verbose:
        print(str(vars(args)))

    content = dict(error=None)

    # prepare request
    request = urllib2.Request(url='http://localhost:{port}{url}'.format(**vars(args)))
    if hasattr(args, 'username') and hasattr(args, 'password'):
        if args.verbose:
            sys.stdout.write('using basic auth')
        base64string = base64.encodestring('{}:{}'.format(args.username, args.password)).strip()
        request.add_header("Authorization", "Basic {}".format(base64string))

    # execute query
    try:
        answer = urllib2.urlopen(request, timeout=args.timeout)
    except urllib2.HTTPError as e:
        content['error'] = str(e)
        print(json.dumps(content))
        sys.exit(1)
    status = answer.read()
    answer.close()

    # parse status datas
    if args.verbose:
        sys.stdout.write(status)

    lines = status.splitlines()
    match = re.match('Active connections:\s+([0-9]+)', lines[0])
    if match:
        content['actives'] = int(match.group(1))

    match = re.match('\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)', lines[2])
    if match:
        content['accepts'] = int(match.group(1))
        content['handled'] = int(match.group(2))
        content['requests'] = int(match.group(3))

    match = re.match('Reading:\s+([0-9]+)\s+Writing:\s+([0-9]+)\s+Waiting:\s+([0-9]+)', lines[3])
    if match:
        content['reading'] = int(match.group(1))
        content['writing'] = int(match.group(2))
        content['waiting'] = int(match.group(3))

    # OUTPUT
    print(json.dumps(content))
    sys.exit(0)
