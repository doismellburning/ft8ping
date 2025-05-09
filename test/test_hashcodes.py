"""
In an ideal world we would compile the Fortran and compare.
In this world I'll do a few manual comparisons...
"""

from ft8ping import hashcodes as hashcodes_module
from ft8ping.hashcodes import hashcodes


def test_2e0kgg():
    """
    $ ./hashcodes 2E0KGG
    Callsign         h10       h12       h22
    -----------------------------------------
    2E0KGG           309      1239   1269521
    Biased for storage in c28:       3333113
    """
    h = hashcodes("2E0KGG")

    assert h[0] == 309
    assert h[1] == 1239
    assert h[2] == 1269521
    assert h[3] == 3333113


def test_main(capsys, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr("sys.argv", ["hashcodes.py", "2E0KGG"])
        hashcodes_module.main()

    out = capsys.readouterr().out

    assert "309" in out
    assert "1239" in out
    assert "1269521" in out
    assert "3333113" in out


def test_main_no_args(capsys, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr("sys.argv", ["hashcodes.py"])
        hashcodes_module.main()

    out = capsys.readouterr().out

    assert "Usage" in out
