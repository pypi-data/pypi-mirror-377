# Welcome to pwntools util!

This Python package is a wrapper class for Gallopsled's [pwntools](https://www.pwntools.com). It's created to facilitate different aspects of writing a pwntools program.

```py
from pwntools_util import PwnUtil

ppp = PwnUtil()
ppp.connectRemote('example.com', 352)

n = ppp.getNumberFromLine()
ppp.sendline('the payload')
ppp.interactive()

ppp.disconnect()
```

## Installation

pwntools_util is on the Python Package Index (PyPI). Install it using [pip](https://pip.pypa.io/en/stable/):

```sh
python3 -m pip install --upgrade pwntools-util
```
