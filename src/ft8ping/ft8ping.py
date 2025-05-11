import structlog
from scapy.all import ICMP, raw  # ty: ignore[unresolved-import]

from .hashcodes import hashcodes
from .std_call_to_c28 import std_call_to_c28

log = structlog.get_logger()


def make_icmp_fields(source: str, destination: str) -> tuple[int, int, bytes]:

    encoded_source = std_call_to_c28(source)  # 28 bits
    log.info(
        "Encoded callsign as c28",
        callsign=source,
        c28=encoded_source,
        c28_hex=hex(encoded_source),
    )

    encoded_destination = hashcodes(destination)[0]  # First hash is the 10-bit one
    log.info(
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

    log.info(
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

    log.info("Made packet", packet=req, raw=raw(req))

    return req


def parse_ping(packet: ICMP) -> tuple[int, int]:
    id_val = packet.id
    seq_val = packet.seq
    payload_val = bytes(packet.payload)

    return parse_fields(id_val, seq_val, payload_val)


def parse_fields(id_val: int, seq_val: int, payload_val: bytes) -> tuple[int, int]:
    source_c28 = (id_val << 12) | ((seq_val & 0xFFF0) >> 4)
    destination_h10 = ((seq_val & 0xF) << 6) | int.from_bytes(
        payload_val, "big"
    )  # FIXME

    return (source_c28, destination_h10)


def main():
    p = make_ping("2E0KGG", "G4HSK")
    print(p)


if __name__ == "__main__":  # pragma: no cover
    main()
