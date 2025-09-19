<!--
SPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>
SPDX-License-Identifier: Apache-2.0
-->

# buildtools4py

python wrapper for (some) Android build-tools

## usage

### install

This project is published to pypi, you can install it using:

```
pip install buildtools4py
```

This project wraps Android build-tools. e.g. Those can be installed with SDK
manager from Android SDK like this:

```
apt install sdkmanager
sdkmanager 'build-tools;36.0.0'
```


### apksigner verify

```
from buildtools4py.apksigner import apksigner_verify

r = apksigner_verify('example.apk')

assert r.verifies
assert len(r.signers) == 1
assert r.signers[0].certificate_sha256 == "abcdef...abcdef"
```

You can also convert the data into a dict/json:

```
from buildtools4py.apksigner import apksigner_verify
from dataclasses import asdict

data = apksigner_verify('example.apk')
datadict = asdict(data)
datajson = json.dumps(datadict, indent=2)
```

## development hints

### commit check: run all check, linters, tests, etc.

Make sure this runs without any errors/warnings before commiting. This runs all sortos of checks, linters, tests, etc. to make sure the code is in acceptable shape.

```
tools/check
```
