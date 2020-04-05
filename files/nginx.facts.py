#!/usr/bin/env python3

import json
import re
import subprocess
import sys

content = dict()

version_re = re.compile('nginx/(?P<version>(?P<major>[0-9]+)\.(?P<branch>[0-9]+)\.[0-9]+)')
stdout = None
try:
    result = subprocess.Popen(['/usr/bin/env', 'nginx', '-v'],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True)
    (stdout, stderr) = result.communicate()
except subprocess.CalledProcessError as e:
    content['error'] = str(e)

if stdout is not None:
    match = version_re.search(stderr + stdout)
    if match:
        content['version_full'] = match.group('version')
        content['version_major'] = match.group('major')
        content['version_branch'] = match.group('branch')

    if 'version_branch' in content:
        try:
            version_branch = int(content['version_branch'])
            if version_branch % 2 == 0:
                content['branch'] = 'stable'
            else:
                content['branch'] = 'mainline'
        except ValueError:
            pass


if len(content) == 0:
    content = None

print(json.dumps(content))
sys.exit(0)
