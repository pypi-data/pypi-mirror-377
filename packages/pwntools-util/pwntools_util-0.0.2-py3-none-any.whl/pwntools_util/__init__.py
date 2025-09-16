# pwntools wrapper with bytes casting and common utils

# ----- pwn -----

# imports

import pwn
import re

# constants

_COLORS = {
    'Green': '\033[92m',
    'Blue': '\033[94m',
    'Yellow': '\033[93m',
    'Reset': '\033[0m',
}

# type utilities

def dataToBytes(data: str | bytes | tuple[str] | tuple[bytes]):
    if type(data) is tuple:
        result = tuple(dataToBytes(d) for d in data)
    elif type(data) is str:
        result = data.encode()
    else:
        result = data
    return result

# string utilities

def getNumberFromString(string: str):
    return int(re.search(r"\d+", string)[0])

def toNumberList(a_list: list[str]):
    res = [getNumberFromString(x) for x in a_list]
    return res

def getSimpleList(string: str, separator: str = None):
    return re.search(r"\[(.+)\]", string)[1].split(separator)

# class

class PwnUtil:
    def __init__(self):
        self._conn = None
        self._header = f"[{_COLORS['Yellow']}PwnUtil{_COLORS['Reset']}]"

    # Connect / disconnect

    def connectRemote(self, host: str, port: int):
        print(f"{self._header}: Connecting to {_COLORS['Green']}remote{_COLORS['Reset']}!")
        self._conn = pwn.remote(host, port)

    def connectLocal(self, path_to_file: str, path_to_interpreter: str = "./.venv/bin/python"):
        print(f"{self._header}: Connecting to {_COLORS['Blue']}local{_COLORS['Reset']}!")
        self._conn = pwn.process([path_to_interpreter, path_to_file])

    def disconnect(self):
        if self._conn:
            self._conn.close()
            print(f"{self._header}: Disconnected!")

    # Get & send

    def getline(self, timeout = 5):
        return self._conn.recvline(timeout=timeout)

    def getuntil(self, data: str | bytes | tuple[str] | tuple[bytes], timeout = 5):
        return self._conn.recvuntil(dataToBytes(data), timeout=timeout)

    def getall(self, timeout = 5):
        return self._conn.recvall(timeout=timeout)

    def sendline(self, data: str | bytes):
        self._conn.sendline(dataToBytes(data))

    def interactive(self):
        self._conn.interactive()

    # Utility

    def getNumberFromLine(self):
        return getNumberFromString(self.getline().decode())

    def getNumberListFromLine(self):
        return toNumberList(getSimpleList(self.getline().decode()))
