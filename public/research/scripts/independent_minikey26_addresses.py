#!/usr/bin/env python3
"""Independent, offline mainnet address derivation for one minikey.

Python standard library only. No wallet, network, signing, or transaction code.
`derive_five` returns the same ordered type/address records as the public Node
reference. Derived secret material exists transiently in memory, never in any
return value, receipt, exception, log, or file. Python/OpenSSL cannot guarantee
complete memory zeroization; a mutable digest buffer is cleared best-effort.

Controls are restricted to the published 30-character minikey example and
synthetic scalar one. The CLI never prints minikeys, scalars, or addresses.

CLI target mode (not exercised during implementation):
  --lead PRIVATE_JSON --out NEW_PRIVATE_OUTPUT
The lead JSON must contain a string field named `minikey`, or string `value`
with `format` equal to `minikey`. Both paths must be
outside directories named `public`; the input file must have private mode, and
the output is exclusively created with mode 0600. The output contains only the
five public addresses and nonsensitive scope metadata.

References: BIP173, BIP350, BIP340/341, BIP86 address construction (no HD path).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import Optional


# Public secp256k1 domain parameters, not private-key material.
FIELD_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
ORDER_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GENERATOR = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)
Point = Optional[tuple[int, int]]  # None represents the point at infinity.
BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BECH32 = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
BECH32M_CONSTANT = 0x2BC830A3
ADDRESS_TYPES = (
    "P2PKH uncompressed",
    "P2PKH compressed",
    "P2SH-P2WPKH",
    "P2WPKH",
    "P2TR key-path with BIP341 TapTweak",
)
PUBLISHED_CONTROL = "S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy"


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _hash160(data: bytes) -> bytes:
    return hashlib.new("ripemd160", _sha256(data)).digest()


def _has_minikey_shape(value: object) -> bool:
    if not isinstance(value, str) or len(value) not in (22, 26, 30):
        return False
    if not value.startswith("S") or any(c not in BASE58 for c in value):
        return False
    return True


def is_minikey(value: object) -> bool:
    """Require 22/30 ASCII Base58 characters, initial S, and the one-byte check."""
    if not _has_minikey_shape(value):
        return False
    return _sha256((value + "?").encode("ascii"))[0] == 0


def _on_curve(point: Point) -> bool:
    if point is None:
        return True
    x, y = point
    return 0 <= x < FIELD_P and 0 <= y < FIELD_P and (y * y - x * x * x - 7) % FIELD_P == 0


def _add(left: Point, right: Point) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        if (y1 + y2) % FIELD_P == 0:
            return None
        slope = (3 * x1 * x1) * pow(2 * y1, -1, FIELD_P) % FIELD_P
    else:
        slope = (y2 - y1) * pow((x2 - x1) % FIELD_P, -1, FIELD_P) % FIELD_P
    x3 = (slope * slope - x1 - x2) % FIELD_P
    return x3, (slope * (x1 - x3) - y1) % FIELD_P


def _multiply_bytes(point: Point, factor: bytes | bytearray) -> Point:
    """Left-to-right double/add; no conversion of a secret digest to an int."""
    result = None
    for octet in factor:
        for shift in range(7, -1, -1):
            result = _add(result, result)
            if (octet >> shift) & 1:
                result = _add(result, point)
    return result


def _lift_even_x(x: int) -> tuple[int, int]:
    if not 0 <= x < FIELD_P:
        raise ValueError("INVALID_PUBLIC_POINT")
    square = (pow(x, 3, FIELD_P) + 7) % FIELD_P
    y = pow(square, (FIELD_P + 1) // 4, FIELD_P)
    if y * y % FIELD_P != square:
        raise ValueError("INVALID_PUBLIC_POINT")
    return x, y if y % 2 == 0 else FIELD_P - y


def _base58check(version: int, payload: bytes) -> str:
    if version not in (0, 5) or len(payload) != 20:
        raise ValueError("INVALID_BASE58_PAYLOAD")
    data = bytes([version]) + payload
    data += _sha256(_sha256(data))[:4]
    leading_zeros = len(data) - len(data.lstrip(b"\0"))
    value = int.from_bytes(data, "big")  # Public address data only.
    chars = []
    while value:
        value, remainder = divmod(value, 58)
        chars.append(BASE58[remainder])
    return "1" * leading_zeros + "".join(reversed(chars))


def _polymod(values: list[int]) -> int:
    generators = (0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3)
    checksum = 1
    for value in values:
        top = checksum >> 25
        checksum = ((checksum & 0x1FFFFFF) << 5) ^ value
        for bit, generator in enumerate(generators):
            if (top >> bit) & 1:
                checksum ^= generator
    return checksum


def _hrp_expand(hrp: str) -> list[int]:
    return [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]


def _convert_bits(data: bytes) -> list[int]:
    """Convert 8-bit bytes to 5-bit groups with BIP173's zero padding."""
    accumulator = 0
    bit_count = 0
    result = []
    for value in data:
        accumulator = ((accumulator << 8) | value) & 0xFFF
        bit_count += 8
        while bit_count >= 5:
            bit_count -= 5
            result.append((accumulator >> bit_count) & 31)
    if bit_count:
        result.append((accumulator << (5 - bit_count)) & 31)
    return result


def _segwit(version: int, program: bytes) -> str:
    if not 0 <= version <= 16 or not 2 <= len(program) <= 40:
        raise ValueError("INVALID_WITNESS_PROGRAM")
    if version == 0 and len(program) not in (20, 32):
        raise ValueError("INVALID_WITNESS_PROGRAM")
    hrp = "bc"
    data = [version] + _convert_bits(program)
    constant = 1 if version == 0 else BECH32M_CONSTANT
    checksum = _polymod(_hrp_expand(hrp) + data + [0] * 6) ^ constant
    check_digits = [(checksum >> (5 * (5 - i))) & 31 for i in range(6)]
    return hrp + "1" + "".join(BECH32[v] for v in data + check_digits)


def _taproot_output(point: tuple[int, int]) -> tuple[int, int]:
    # An x-only key is lifted to the EVEN y root, including when the original
    # SEC public key has odd y. No script-tree root is appended to the hash.
    internal = _lift_even_x(point[0])
    tag_hash = _sha256(b"TapTweak")
    tweak_bytes = _sha256(tag_hash + tag_hash + internal[0].to_bytes(32, "big"))
    if tweak_bytes >= ORDER_N.to_bytes(32, "big"):
        raise ValueError("INVALID_TAPTWEAK")  # Reject; do not silently reduce.
    output = _add(internal, _multiply_bytes(GENERATOR, tweak_bytes))
    if output is None:
        raise ValueError("INVALID_TAPROOT_OUTPUT")
    return output


def _five_from_point(point: tuple[int, int]) -> list[dict[str, str]]:
    if not _on_curve(point):
        raise ValueError("INVALID_PUBLIC_POINT")
    x, y = point
    compressed = bytes([2 + y % 2]) + x.to_bytes(32, "big")
    uncompressed = b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")
    pubkey_hash = _hash160(compressed)
    redeem_script = b"\x00\x14" + pubkey_hash
    taproot = _taproot_output(point)
    addresses = (
        _base58check(0, _hash160(uncompressed)),
        _base58check(0, pubkey_hash),
        _base58check(5, _hash160(redeem_script)),
        _segwit(0, pubkey_hash),
        _segwit(1, taproot[0].to_bytes(32, "big")),
    )
    return [{"type": kind, "address": address} for kind, address in zip(ADDRESS_TYPES, addresses)]


def _point_from_secret(secret: bytearray) -> tuple[int, int]:
    if len(secret) != 32 or not any(secret) or secret >= ORDER_N.to_bytes(32, "big"):
        raise ValueError("INVALID_PRIVATE_SCALAR")
    point = _multiply_bytes(GENERATOR, secret)
    if point is None or not _on_curve(point):
        raise ValueError("INVALID_PUBLIC_POINT")
    return point


def derive_five(minikey: str) -> list[dict[str, str]]:
    """Validate one minikey and return exactly five standard mainnet addresses.

    Invalid format/checksum/scalar raises a generic ValueError. No secret is
    attached to errors. SHA256(minikey) is NEVER persisted, printed, returned,
    or used as a fingerprint. There is no blockchain lookup.
    """
    if not is_minikey(minikey):
        raise ValueError("INVALID_MINIKEY")
    secret = bytearray(_sha256(minikey.encode("ascii")))
    try:
        return _five_from_point(_point_from_secret(secret))
    finally:
        for index in range(len(secret)):
            secret[index] = 0


# Frozen address-only public controls. Populated from a separate Node control
# run and independently checked against well-known scalar-one P2PKH vectors.
EXPECTED_PUBLIC_CONTROL: tuple[str, ...] = ('1CciesT23BNionJeXrbxmjc7ywfiyM4oLW', '1PZuicD1ACRfBuKEgp2XaJhVvnwpeETDyn', '3FJeDuA15H3LZuYR4E4MikQDKjTxy6DjFS', 'bc1q77xpty0n7d8arl3nnhphzp5m0dyjhumsv7usuc', 'bc1ptrn8c2fuy92nczpejtjlwpj7h73hgftkjshhmuqdch0hr943mg8sykpkcx')
EXPECTED_SCALAR_ONE: tuple[str, ...] = ('1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm', '1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH', '3JvL6Ymt8MVWiCNHC7oWU6nLeHNJKLZGLN', 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4', 'bc1pmfr3p9j00pfxjh0zmgp99y8zftmd3s5pmedqhyptwy6lm87hf5sspknck9')


def self_test() -> dict[str, object]:
    """Offline controls only; the returned receipt contains no addresses/keys."""
    if len(EXPECTED_PUBLIC_CONTROL) != 5 or len(EXPECTED_SCALAR_ONE) != 5:
        raise ValueError("CONTROL_VECTORS_NOT_FROZEN")
    checks = 0

    def require(condition: bool) -> None:
        nonlocal checks
        if not condition:
            raise ValueError("SELF_TEST_FAILED")
        checks += 1

    require(is_minikey(PUBLISHED_CONTROL))
    # Test the 22-character shape gate without synthesizing a new valid key.
    # Checksum-invalid 22-character strings are expected to be rejected.
    bad_22 = "S" + "2" * 21
    if is_minikey(bad_22):
        bad_22 = "S" + "3" + "2" * 20
    require(_has_minikey_shape(bad_22))
    require(not is_minikey(bad_22))
    for invalid in ("T" + PUBLISHED_CONTROL[1:], "S0" + PUBLISHED_CONTROL[2:],
                    PUBLISHED_CONTROL + "1", PUBLISHED_CONTROL[:-1],
                    PUBLISHED_CONTROL.lower(), "", None):
        require(not is_minikey(invalid))
    bad_checksum = next(PUBLISHED_CONTROL[:-1] + c for c in BASE58
                        if not is_minikey(PUBLISHED_CONTROL[:-1] + c))
    require(not is_minikey(bad_checksum))
    try:
        derive_five(bad_checksum)
    except ValueError as error:
        require(str(error) == "INVALID_MINIKEY")
    else:
        require(False)

    require(_on_curve(GENERATOR))
    require(_add(None, GENERATOR) == GENERATOR)
    require(_add(GENERATOR, None) == GENERATOR)
    opposite = (GENERATOR[0], FIELD_P - GENERATOR[1])
    require(_add(GENERATOR, opposite) is None)
    require(_multiply_bytes(GENERATOR, bytes(32)) is None)
    require(_multiply_bytes(GENERATOR, ORDER_N.to_bytes(32, "big")) is None)
    require(_lift_even_x(opposite[0]) == GENERATOR)
    require(_taproot_output(opposite) == _taproot_output(GENERATOR))

    for invalid_secret in (bytearray(32), bytearray(ORDER_N.to_bytes(32, "big")), bytearray(31)):
        try:
            _point_from_secret(invalid_secret)
        except ValueError as error:
            require(str(error) == "INVALID_PRIVATE_SCALAR")
        else:
            require(False)

    one = bytearray(32)
    one[-1] = 1
    try:
        point = _point_from_secret(one)
        require(point == GENERATOR)
        scalar_one_result = _five_from_point(point)
    finally:
        for index in range(len(one)):
            one[index] = 0
    public_result = derive_five(PUBLISHED_CONTROL)
    require(tuple(x["address"] for x in public_result) == EXPECTED_PUBLIC_CONTROL)
    require(tuple(x["address"] for x in scalar_one_result) == EXPECTED_SCALAR_ONE)
    require(scalar_one_result[0]["address"] == "1EHNa6Q4Jz2uvNExL497mE43ikXhwF6kZm")
    require(scalar_one_result[1]["address"] == "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH")
    # Check the emitted witness checksums directly, including v0/v1 domain
    # separation. This validates encoding, not a complete generic decoder.
    for result in (public_result, scalar_one_result):
        for index, expected_constant in ((3, 1), (4, BECH32M_CONSTANT)):
            address = result[index]["address"]
            hrp, body = address.rsplit("1", 1)
            require(_polymod(_hrp_expand(hrp) + [BECH32.index(c) for c in body]) == expected_constant)
    return {
        "status": "PASS",
        "checksPassed": checks,
        "controlSets": 2,
        "addressFormatsPerControl": 5,
        "addressVectorsMatched": 10,
        "targetInputRead": False,
        "addressQueries": 0,
    }


class _CliError(Exception):
    pass


class _PrivateParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # argparse's default message can echo user-provided argument values.
        raise _CliError("INVALID_ARGUMENTS")


def _private_path(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if any(part.lower() == "public" for part in path.parts):
        raise _CliError("PRIVATE_PATH_REQUIRED")
    return path


def _extract_minikey(record: object) -> str:
    if not isinstance(record, dict):
        raise _CliError("INVALID_INPUT")
    if isinstance(record.get("minikey"), str):
        if "value" in record and record["value"] != record["minikey"]:
            raise _CliError("CONFLICTING_INPUT")
        return record["minikey"]
    if record.get("format") == "minikey" and isinstance(record.get("value"), str):
        return record["value"]
    raise _CliError("INVALID_INPUT")


def _write_private_result(lead_argument: str, output_argument: str) -> dict[str, object]:
    lead = _private_path(lead_argument)
    output = _private_path(output_argument)
    if output.exists() or output.is_symlink():
        raise _CliError("OUTPUT_ALREADY_EXISTS")
    if not lead.is_file() or lead.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise _CliError("PRIVATE_INPUT_REQUIRED")
    if lead.stat().st_size > 65536:
        raise _CliError("INVALID_INPUT")
    # This is the only CLI branch that opens a lead, and it requires BOTH
    # explicit flags. Implementation/control tests never call this branch.
    with lead.open("r", encoding="utf-8") as source:
        record = json.load(source)
    addresses = derive_five(_extract_minikey(record))
    result = {
        "schemaVersion": 1,
        "network": "bitcoin-mainnet",
        "derivation": "independent-python-stdlib-v1",
        "minikeyFormatValid": True,
        "addressCount": len(addresses),
        "addresses": addresses,
        "addressQueries": 0,
    }
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as destination:
        json.dump(result, destination, indent=2, ensure_ascii=True)
        destination.write("\n")
    return {"status": "PASS", "addressCount": 5, "addressQueries": 0, "privateOutputWritten": True}


def main(argv: Optional[list[str]] = None) -> int:
    parser = _PrivateParser(description="Offline independent address checker; console output is redacted.",
                            allow_abbrev=False)
    parser.add_argument("--self-test", action="store_true", help="run public/synthetic controls only")
    parser.add_argument("--lead", metavar="PRIVATE_JSON", help="private JSON containing a minikey field")
    parser.add_argument("--out", metavar="NEW_PRIVATE_OUTPUT", help="new private address result file")
    try:
        args = parser.parse_args(argv)
        if args.self_test:
            if args.lead or args.out:
                raise _CliError("INCOMPATIBLE_ARGUMENTS")
            receipt = self_test()
        else:
            if not args.lead or not args.out:
                raise _CliError("BOTH_PRIVATE_PATHS_REQUIRED")
            receipt = _write_private_result(args.lead, args.out)
        print(json.dumps(receipt, sort_keys=True))
        return 0
    except _CliError as error:
        print(json.dumps({"status": "FAIL", "errorCode": str(error)}, sort_keys=True))
        return 2
    except Exception:
        # Never expose exception text, argument values, paths, keys, or hashes.
        print(json.dumps({"status": "FAIL", "errorCode": "VALIDATION_OR_IO_FAILURE"}, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
