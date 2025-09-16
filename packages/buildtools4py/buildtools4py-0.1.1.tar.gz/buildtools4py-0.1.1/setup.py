# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['buildtools4py']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'buildtools4py',
    'version': '0.1.1',
    'description': 'python wrapper for (some) Android build-tools',
    'long_description': '<!--\nSPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>\nSPDX-License-Identifier: Apache-2.0\n-->\n\n# buildtools4py\n\npython wrapper for (some) Android build-tools\n\n## install\n\nThis project is published to pypi, you can install it using:\n\n```\npip install buildtools4py\n```\n\nThis project wraps Android build-tools. e.g. Those can be installed with SDK\nmanager from Android SDK like this:\n\n```\napt install sdkmanager\nsdkmanager \'build-tools;36.0.0\'\n```\n\n\n## apksigner verify\n\n```\nfrom buildtools4py.apksigner import apksigner_verify\n\nr = apksigner_verify(\'example.apk\')\n\nassert r.verifies\nassert len(r.signers) == 1\nassert r.signers[0].certificate_sha256 == "abcdef...abcdef"\n```\n\nYou can also convert the data into a dict/json:\n\n```\nfrom buildtools4py.apksigner import apksigner_verify\nfrom dataclasses import asdict\n\ndata = apksigner_verify(\'example.apk\')\ndatadict = asdict(data)\ndatajson = json.dumps(datadict, indent=2)\n```\n',
    'author': 'Michael Pöhn',
    'author_email': 'michael@poehn.at',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
