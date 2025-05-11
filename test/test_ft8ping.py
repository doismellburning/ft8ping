from ft8ping import ft8ping
from ft8ping.hashcodes import hashcodes
from ft8ping.std_call_to_c28 import std_call_to_c28


def test_invert():
    source = "G8GKA"
    c28 = std_call_to_c28(source)

    destination = "M6KGG"
    h10 = hashcodes(destination)[0]

    packet = ft8ping.make_ping(source, destination)

    decoded_c28, decoded_h10 = ft8ping.parse_ping(packet)

    assert c28 == decoded_c28
    assert h10 == decoded_h10


def test_main_no_args(capsys, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr("sys.argv", ["ft8ping.py"])
        ft8ping.main()

    out = capsys.readouterr().out

    assert "packet" in out
