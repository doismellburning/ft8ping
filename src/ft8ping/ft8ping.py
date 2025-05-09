import structlog
from scapy.all import ICMP, raw

from .hashcodes import hashcodes
from .std_call_to_c28 import std_call_to_c28

log = structlog.get_logger()


def make_icmp_fields(source: str, destination: str):

    encoded_source = std_call_to_c28(source)  # 28 bits
    log.info("Encoded callsign as c28", callsign=source, c28=encoded_source)

    encoded_destination = hashcodes(destination)[0]  # First hash is the 10-bit one
    log.info("Hashed callsign as h10", callsign=destination, h10=encoded_destination)

    id_val = encoded_source >> 12  # First 16 bits

    # Remaining 12 bits of c28 + first 4 bits of h10
    seq_val = (encoded_source & 0xFFF) << 4 | encoded_destination >> 6

    # Remaining 6 bits of h10
    payload_val = (encoded_destination & 0x3F).to_bytes(1, "big")

    log.info(
        "Built ICMP fields",
        id_val=id_val,
        seq_val=seq_val,
        payload_val=payload_val,
    )

    return (id_val, seq_val, payload_val)


def make_ping(source: str, destination: str):
    id_val, seq_val, payload_val = make_icmp_fields(source, destination)

    req = ICMP(id=id_val, seq=seq_val)
    req /= payload_val

    log.info("Made packet", packet=req, raw=raw(req))

    return req


def main():
    p = make_ping("2E0KGG", "G4HSK")
    print(p)


if __name__ == "__main__":  # pragma: no cover
    main()
