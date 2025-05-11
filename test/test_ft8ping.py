from click.testing import CliRunner

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
    runner = CliRunner()
    result = runner.invoke(ft8ping.main, "--source 2E0KGG --destination G4HSK")

    assert "packet" in result.output
