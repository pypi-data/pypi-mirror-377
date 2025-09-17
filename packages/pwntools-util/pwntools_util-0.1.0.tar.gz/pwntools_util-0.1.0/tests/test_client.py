# ----- test -----

# imports

from pwntools_util import PwnUtil, _COLORS

# test

def test_client():
    print(f"[{_COLORS['Blue']}pwntools_util{_COLORS['Reset']}]: Testing pwntools util...")

    # Connect
    ppp = PwnUtil()
    ppp.connectLocal("./tests/test_server.py")

    # Get data
    print(ppp.getline().strip().decode())
    print(ppp.getNumberFromLine())
    print(ppp.getNumberFromLine())
    a, b = ppp.getAllNumbersFromLine()
    print(a, b)
    print(ppp.getNumberListFromLine())
    print(ppp.getNumberListFromLine())

    # Send data
    ppp.getuntil("-> ")
    ppp.sendline(f"{_COLORS['Green']}I <3 pwnUtil{_COLORS['Reset']}")
    print(ppp.getline().strip().decode())

    # Disconnect
    ppp.disconnect()
