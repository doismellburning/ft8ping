"""
In an ideal world we would compile the Fortran and compare.
In this world I'll do a few manual comparisons...
"""

from ft8ping import std_call_to_c28 as std_call_to_c28_module
from ft8ping.std_call_to_c28 import std_call_to_c28


def test_2e0kgg():
    """
    $ ./std_call_to_c28 2E0KGG
    Callsign: 2E0KGG  c28 as decimal integer:  30279371
    """
    c28 = std_call_to_c28("2E0KGG")

    assert c28 == 30279371


def test_main(capsys, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr("sys.argv", ["std_call_to_c28.py", "2E0KGG"])
        std_call_to_c28_module.main()

    out = capsys.readouterr().out

    assert "30279371" in out


def test_main_no_args(capsys, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr("sys.argv", ["std_call_to_c28.py"])
        std_call_to_c28_module.main()

    out = capsys.readouterr().out

    assert "Usage" in out
