import subprocess
import tempfile

from click.testing import CliRunner
from scapy.layers.inet import ICMP

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


def test_main_default(fake_process):
    runner = CliRunner()
    fake_process.register(["aplay", fake_process.any()])
    fake_process.allow_unregistered(True)

    result = runner.invoke(
        ft8ping.main,
        "send --source 2E0KGG --destination G4HSK",
    )

    assert result.exit_code == 0, result.output
    assert "packet" in result.output


def test_main_no_transmit(fake_process):
    runner = CliRunner()
    fake_process.register(["aplay", fake_process.any()])
    fake_process.allow_unregistered(True)

    result = runner.invoke(
        ft8ping.main,
        "send --source 2E0KGG --destination G4HSK --no-transmit",
    )

    assert result.exit_code == 0, result.output
    assert "packet" in result.output


def test_hashcodes():
    runner = CliRunner()

    result = runner.invoke(
        ft8ping.main,
        "hashcodes 2E0KGG",
    )

    assert result.exit_code == 0, result.output
    assert "2E0KGG" in result.output


def test_std_call_to_c28():
    runner = CliRunner()

    result = runner.invoke(
        ft8ping.main,
        "std_call_to_c28 2E0KGG",
    )

    assert result.exit_code == 0, result.output
    assert "2E0KGG" in result.output
    assert "30279371" in result.output


def test_packet_to_telemetry_hex():
    payload_int = 6  # Arbitrary value from a test run
    packet = ICMP(id=0x1CE0, seq=0x6CB8) / payload_int.to_bytes(1)

    assert len(bytes(packet)) == 9

    x = ft8ping.packet_to_telemetry_hex(packet)

    # "Telemetry data, up to 18 hexadecimal digits or 71 bits maximum.
    # With 18 digits, the first digit must fall in the range 0 – 7."
    assert len(x) < 18 or len(x) == 18 and x[0] in "01234567"


# Generate an audio file, then decode it with the `jt9` tool bundled with WSJT-X
def test_audio_decode():
    telemetry_hex = "40034310E70365E83"
    audio_file = ft8ping.make_audio(telemetry_hex)

    result = subprocess.run(
        [
            "jt9",
            "--ft8",
            audio_file,
        ],
        capture_output=True,
        check=True,
        cwd=tempfile.mkdtemp(),  # jt9 leaves files around when decoding, so let's litter /tmp rather than anywhere else
        text=True,
    )

    assert telemetry_hex in result.stdout
