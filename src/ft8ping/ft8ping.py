import subprocess
import tempfile
from pathlib import Path

import click
import structlog
from scapy.compat import raw
from scapy.layers.inet import ICMP

from .hashcodes import hashcodes
from .std_call_to_c28 import std_call_to_c28

log = structlog.get_logger()


def make_icmp_fields(source: str, destination: str) -> tuple[int, int, bytes]:

    encoded_source = std_call_to_c28(source)  # 28 bits
    log.debug(
        "Encoded callsign as c28",
        callsign=source,
        c28=encoded_source,
        c28_hex=hex(encoded_source),
    )

    encoded_destination = hashcodes(destination)[0]  # First hash is the 10-bit one
    log.debug(
        "Hashed callsign as h10",
        callsign=destination,
        h10=encoded_destination,
        h10_hex=hex(encoded_destination),
    )

    id_val = encoded_source >> 12  # First 16 bits

    # Remaining 12 bits of c28 + first 4 bits of h10
    seq_val = (encoded_source & 0xFFF) << 4 | encoded_destination >> 6

    # Remaining 6 bits of h10
    # TODO LIES it's 8 bits
    payload_val = (encoded_destination & 0x3F).to_bytes(1, "big")

    log.debug(
        "Built ICMP fields",
        id_val=id_val,
        seq_val=seq_val,
        payload_val=payload_val,
    )

    return (id_val, seq_val, payload_val)


def make_ping(source: str, destination: str) -> ICMP:
    id_val, seq_val, payload_val = make_icmp_fields(source, destination)

    req = ICMP(id=id_val, seq=seq_val)
    req /= payload_val

    log.debug("Made packet", packet=req, raw=raw(req))

    return req


def parse_ping(packet: ICMP) -> tuple[int, int]:
    id_val = packet.id
    seq_val = packet.seq
    payload_val = bytes(packet.payload)

    return parse_fields(id_val, seq_val, payload_val)


def parse_fields(id_val: int, seq_val: int, payload_val: bytes) -> tuple[int, int]:
    source_c28 = (id_val << 12) | ((seq_val & 0xFFF0) >> 4)
    destination_h10 = ((seq_val & 0xF) << 6) | int.from_bytes(
        payload_val,
        "big",
    )  # FIXME

    return (source_c28, destination_h10)


def packet_to_telemetry_hex(packet: ICMP) -> str:
    packet_bytes = bytes(packet)
    log.debug("Packet bytes", packet_bytes=packet_bytes, length=len(packet_bytes))

    # TODO Check 9 bytes long (72 bits), then we downshift to fit in the 71 bits of a telemetry packet
    packet_as_int = int.from_bytes(packet_bytes, byteorder="big")
    shifted = packet_as_int >> 1

    hex_string = hex(shifted)[2:]  # Remove leading "0x"

    return hex_string


def make_audio(telemetry_hex: str) -> Path:
    tmpdir = tempfile.mkdtemp(prefix="ft8ping-")

    log.debug("Made tmpdir", tmpdir=tmpdir)

    # ft8sim "test" 1500 0 0.1 1.0 1 +30
    result = subprocess.run(
        [
            "ft8sim",
            telemetry_hex,
            "1500",
            "0",  # "DT": "Time offset from nominal" - examples use 0
            "0.1",  # "fdop": "Watterson frequency spread" - examples seem to use 0.1 so let's go with that
            "1.0",  # "del": "Watterson delay" - examples seem to use 1.0 so let's go with that
            "1",  # "nfiles": only one file
            "91",  # "snr": ft8sim special-cases values over 90
        ],
        capture_output=True,
        cwd=tmpdir,
        check=True,
        text=True,
    )

    if "i3.n3: 0.5" not in result.stdout:  # pragma: no cover
        log.fatal(
            "ft8sim possibly didn't create a telemetry packet?",
            stdout=result.stdout,
        )

    filename = "000000_000001.wav"  # ft8sim default

    if filename not in result.stdout:  # pragma: no cover
        log.fatal(
            "ft8sim didn't seem to create a file with the expected name",
            expected=filename,
            stdout=result.stdout,
        )

    return Path(tmpdir) / filename


def build_rigctl_command(radio_model: str, radio_device: str) -> list[str]:
    return [
        "rigctl",
        "--model",
        radio_model,
        "--rig-file",
        radio_device,
    ]


def transmit(
    audio_filepath: Path,
    radio_model: str,
    radio_device: str,
    audio_device: str,
) -> None:
    # TODO This makes a *LOT* of assumptions about rig support and state etc...
    # TODO Dry run that just dumps command used?
    # TODO Check for presence of commands?
    rigctl_command = build_rigctl_command(radio_model, radio_device)

    cmd = rigctl_command + ["set_ptt", "1"]
    subprocess.run(cmd, check=True)
    log.info("PTT Enabled", cmd=" ".join(cmd))

    cmd = [
        "aplay",
        "--device",
        audio_device,
        str(audio_filepath),
    ]
    log.info("Playing audio", cmd=" ".join(cmd))
    subprocess.run(
        cmd,
        check=True,
    )
    log.info("Played audio")

    cmd = rigctl_command + ["set_ptt", "0"]
    subprocess.run(cmd, check=True)
    log.info("PTT Disabled", cmd=cmd)


@click.group("ft8ping")
def main():
    pass


@main.command()
@click.option("--source", required=True, help="Source callsign, i.e. yours")
@click.option("--destination", required=True, help="Destination callsign")
@click.option(
    "--no-transmit",
    is_flag=True,
    default=False,
    help="Don't transmit, just generate audio file",
)
@click.option("--radio-model", default="1", help="Radio model (see `rigctl --list`)")
@click.option(
    "--radio-device",
    default="/dev/radio",
    help="Radio device (e.g. `/dev/radio`)",
)
@click.option(
    "--audio-device",
    default="plughw:0,0",
    help="Audio device for radio input (see `aplay -l`)",
)
def send(source, destination, no_transmit, radio_model, radio_device, audio_device):
    # TODO Make no-transmit skip other options? Or make them subcommands -
    # always need src/dest, but genaudio doesn't need more while tx needs devices
    packet = make_ping(source, destination)
    log.info("Made packet", packet=packet, hexdump=hex(int.from_bytes(raw(packet))))
    telemetry_hex = packet_to_telemetry_hex(packet)
    log.info("Telemetry hex", packet=telemetry_hex, length=len(telemetry_hex))
    audio_filepath = make_audio(telemetry_hex)
    log.info("Made FT8 audio", path=str(audio_filepath))

    if no_transmit:
        return

    # TODO Sleep
    log.info("Sleeping TODO")
    log.info("Transmitting")
    transmit(audio_filepath, radio_model, radio_device, audio_device)
    log.info("Transmitted!")


@main.command("hashcodes")
@click.argument("callsign")
def hashcodes_command(callsign):
    callsign = callsign.upper()
    h = hashcodes(callsign)
    print(f"Callsign: {callsign}")
    print(f"h10: {h[0]}")
    print(f"h12: {h[1]}")
    print(f"h22: {h[2]}")
    print(f"Biased for storage in c28: {h[3]}")


@main.command("std_call_to_c28")
@click.argument("callsign")
def std_call_to_c28_command(callsign):
    callsign = callsign.upper()
    c28 = std_call_to_c28(callsign)
    print(f"Callsign: {callsign}")
    print(f"c28: {c28}")


if __name__ == "__main__":  # pragma: no cover
    main()
