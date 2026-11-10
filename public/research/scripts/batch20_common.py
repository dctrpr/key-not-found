#!/usr/bin/env python3
"""Offline literal-record validators shared by the preregistered batch.

Importing this module does not read target data or write files. Candidate
records stay in memory; public results omit secret values and hit locators.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORT = Path(__file__).resolve().parent / "batch20_support"
ENGLISH_SHA256 = "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
DEFAULT_FORMATS = ("wif", "minikey", "hex64", "bip39")
ALL_FORMATS = DEFAULT_FORMATS + ("extended_private", "bip38", "address", "sec_public")
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
B58_CLASS = "1-9A-HJ-NP-Za-km-z"
HEX_CLASS = "0-9A-Fa-f"
BECH = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
FIELD = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
PRIVATE_VERSIONS = {0x0488ADE4: "xprv", 0x049D7878: "yprv", 0x04B2430C: "zprv",
                    0x0295B005: "Yprv", 0x02AA7A99: "Zprv"}
FP_DOMAIN = b"KEY404/batch20/record-fingerprint/v1\x00"
FINGERPRINT_RULE = {"algorithm": "SHA-256", "domainText": "KEY404/batch20/record-fingerprint/v1",
                    "separatorHex": "00", "rule": "SHA256(domain || 0x00 || ASCII(format) || 0x00 || canonical record bytes)"}


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def fingerprint(kind: str, canonical: bytes) -> str:
    return hashlib.sha256(FP_DOMAIN + kind.encode("ascii") + b"\x00" + canonical).hexdigest()


def b58encode(data: bytes) -> str:
    value, text = int.from_bytes(data, "big"), ""
    while value:
        value, remainder = divmod(value, 58)
        text = B58[remainder] + text
    return "1" * (len(data) - len(data.lstrip(b"\x00"))) + text


def b58decode(text: str) -> bytes | None:
    if not text or any(c not in B58 for c in text):
        return None
    number = 0
    for char in text:
        number = number * 58 + B58.index(char)
    raw = number.to_bytes((number.bit_length() + 7) // 8, "big")
    raw = b"\x00" * (len(text) - len(text.lstrip("1"))) + raw
    return raw if b58encode(raw) == text else None


def b58check(text: str) -> bytes | None:
    raw = b58decode(text)
    if raw is None or len(raw) < 5 or not hmac.compare_digest(sha256(sha256(raw[:-4]))[:4], raw[-4:]):
        return None
    return raw[:-4]


def scalar_valid(raw: bytes) -> bool:
    return len(raw) == 32 and 0 < int.from_bytes(raw, "big") < ORDER


def wordlist() -> tuple[list[str], dict[str, int]]:
    raw = (SUPPORT / "english.txt").read_bytes()
    if hashlib.sha256(raw).hexdigest() != ENGLISH_SHA256:
        raise ValueError("Official BIP39 wordlist hash mismatch")
    words = raw.decode("ascii").splitlines()
    if len(words) != 2048 or len(set(words)) != 2048:
        raise ValueError("Official BIP39 wordlist must contain 2048 unique words")
    return words, {word: index for index, word in enumerate(words)}


def bip39_valid(words: list[str], indexes: dict[str, int]) -> bool:
    if len(words) not in (12, 15, 18, 21, 24) or any(w not in indexes for w in words):
        return False
    bits = "".join(f"{indexes[word]:011b}" for word in words)
    checksum_bits = len(words) // 3
    entropy_bits = bits[:-checksum_bits]
    entropy = int(entropy_bits, 2).to_bytes(len(entropy_bits) // 8, "big")
    expected = f"{int.from_bytes(sha256(entropy), 'big'):0256b}"[:checksum_bits]
    return bits[-checksum_bits:] == expected


def bech_polymod(values: list[int]) -> int:
    check = 1
    generators = (0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3)
    for value in values:
        high = check >> 25
        check = ((check & 0x1FFFFFF) << 5) ^ value
        for bit, generator in enumerate(generators):
            if (high >> bit) & 1:
                check ^= generator
    return check


def convertbits(values: list[int], from_bits: int, to_bits: int, pad: bool) -> bytes | None:
    accumulator = bits = 0
    result = []
    for value in values:
        if value < 0 or value >> from_bits:
            return None
        accumulator = ((accumulator << from_bits) | value) & ((1 << (from_bits + to_bits - 1)) - 1)
        bits += from_bits
        while bits >= to_bits:
            bits -= to_bits
            result.append((accumulator >> bits) & ((1 << to_bits) - 1))
    if pad:
        if bits:
            result.append((accumulator << (to_bits - bits)) & ((1 << to_bits) - 1))
    elif bits >= from_bits or ((accumulator << (to_bits - bits)) & ((1 << to_bits) - 1)):
        return None
    return bytes(result)


def witness_address(text: str) -> dict | None:
    if not 14 <= len(text) <= 90 or (text != text.lower() and text != text.upper()):
        return None
    lower = text.lower()
    separator = lower.rfind("1")
    if separator < 1 or lower[:separator] != "bc" or len(lower) - separator < 7:
        return None
    try:
        data = [BECH.index(c) for c in lower[separator + 1:]]
    except ValueError:
        return None
    hrp = lower[:separator]
    expanded = [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]
    polymod = bech_polymod(expanded + data)
    values = data[:-6]
    if not values:
        return None
    version = values[0]
    program = convertbits(values[1:], 5, 8, False)
    # Fixed batch scope: established v0 P2WPKH/P2WSH and v1 32-byte Taproot.
    if program is None or version not in (0, 1):
        return None
    if version == 0 and (polymod != 1 or len(program) not in (20, 32)):
        return None
    if version == 1 and (polymod != 0x2BC830A3 or len(program) != 32):
        return None
    return {"address": lower, "type": "P2WPKH" if version == 0 and len(program) == 20
            else "P2WSH" if version == 0 else "P2TR", "witnessVersion": version}


def sec_point(text: str) -> dict | None:
    try:
        raw = bytes.fromhex(text)
    except ValueError:
        return None
    if len(raw) == 33 and raw[0] in (2, 3):
        x = int.from_bytes(raw[1:], "big")
        if x >= FIELD:
            return None
        squared = (x * x * x + 7) % FIELD
        y = pow(squared, (FIELD + 1) // 4, FIELD)
        if y * y % FIELD != squared:
            return None
        if y & 1 != raw[0] & 1:
            y = FIELD - y
        if y >= FIELD or y & 1 != raw[0] & 1:
            return None
        encoding = "compressedSEC"
    elif len(raw) == 65 and raw[0] == 4:
        x, y = int.from_bytes(raw[1:33], "big"), int.from_bytes(raw[33:], "big")
        if x >= FIELD or y >= FIELD or y * y % FIELD != (x * x * x + 7) % FIELD:
            return None
        encoding = "uncompressedSEC"
    else:
        return None
    canonical = bytes([2 + (y & 1)]) + x.to_bytes(32, "big")
    return {"canonical": canonical, "encoding": encoding, "publicKey": raw.hex()}


def validate_record(kind: str, value: str, indexes: dict[str, int] | None = None) -> tuple[bytes, dict] | None:
    if kind == "minikey":
        if len(value) in (22, 30) and re.fullmatch(r"S[" + B58_CLASS + r"]+", value) and sha256((value + "?").encode("ascii"))[0] == 0:
            return value.encode("ascii"), {"length": len(value), "checkBits": 8, "private": True}
    elif kind == "wif":
        payload = b58check(value)
        if payload and len(payload) in (33, 34) and payload[0] == 0x80 and (len(payload) == 33 or payload[-1] == 1) and scalar_valid(payload[1:33]):
            return payload, {"compressed": len(payload) == 34, "checkBits": 32, "private": True}
    elif kind == "hex64":
        if re.fullmatch(r"[" + HEX_CLASS + r"]{64}", value):
            raw = bytes.fromhex(value)
            if scalar_valid(raw):
                return raw, {"checkBits": 0, "private": True}
    elif kind == "bip39":
        words = value.split(" ")
        if indexes is not None and bip39_valid(words, indexes):
            return value.encode("ascii"), {"wordCount": len(words), "checkBits": len(words) // 3, "private": True}
    elif kind == "extended_private":
        payload = b58check(value)
        if payload and len(payload) == 78 and int.from_bytes(payload[:4], "big") in PRIVATE_VERSIONS and payload[45] == 0 and scalar_valid(payload[46:]):
            if payload[4] == 0 and (payload[5:9] != b"\x00" * 4 or payload[9:13] != b"\x00" * 4):
                return None
            return payload, {"version": PRIVATE_VERSIONS[int.from_bytes(payload[:4], "big")], "depth": payload[4], "checkBits": 32, "private": True}
    elif kind == "bip38":
        payload = b58check(value)
        if payload and len(payload) == 39 and payload[:2] in (b"\x01\x42", b"\x01\x43"):
            flags = (0xC0, 0xE0) if payload[1] == 0x42 else (0, 4, 0x20, 0x24)
            if payload[2] in flags:
                return payload, {"recordType": "non-EC-multiplied" if payload[1] == 0x42 else "EC-multiplied", "checkBits": 32, "encrypted": True, "private": True}
    elif kind == "address":
        payload = b58check(value)
        if payload and len(payload) == 21 and payload[0] in (0, 5):
            return value.encode("ascii"), {"address": value, "type": "P2PKH" if payload[0] == 0 else "P2SH", "checkBits": 32, "private": False}
        witness = witness_address(value)
        if witness:
            return witness["address"].encode("ascii"), {**witness, "private": False}
    elif kind == "sec_public":
        point = sec_point(value)
        if point:
            return point["canonical"], {"encoding": point["encoding"], "publicKey": point["publicKey"], "checkBits": 0, "onCurve": True, "private": False}
    return None


def shape_values(kind: str, text: str, indexes: dict[str, int] | None = None):
    if kind in ("wif", "minikey", "extended_private", "bip38"):
        rules = {"wif": [("[5KL]", n) for n in (51, 52)],
                 "minikey": [("S", n) for n in (22, 30)],
                 "extended_private": [("(?:xprv|yprv|zprv|Yprv|Zprv)", 111)],
                 "bip38": [("6P", 58)]}[kind]
        for prefix, length in rules:
            prefix_size = 4 if kind == "extended_private" else 2 if kind == "bip38" else 1
            pattern = r"(?=(" + prefix + "[" + B58_CLASS + "]{" + str(length - prefix_size) + r"}))"
            for match in re.finditer(pattern, text):
                yield match.group(1)
    elif kind == "hex64":
        yield from (m.group(0) for m in re.finditer(r"(?<![" + HEX_CLASS + "])[" + HEX_CLASS + r"]{64}(?![" + HEX_CLASS + "])", text))
    elif kind == "sec_public":
        for prefix, remainder in (("(?:02|03)", 64), ("04", 128)):
            pattern = r"(?<![" + HEX_CLASS + "])" + prefix + "[" + HEX_CLASS + "]{" + str(remainder) + r"}(?![" + HEX_CLASS + "])"
            yield from (m.group(0) for m in re.finditer(pattern, text))
    elif kind == "bip39":
        # An invalid decoded group is missing data, never disposable punctuation.
        # Case is normalized for BIP39; ordinary punctuation bounds lexical words.
        for region in text.split("␞"):
            words = [m.group(0).lower() for m in re.finditer(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*", region)]
            for length in (12, 15, 18, 21, 24):
                for offset in range(max(0, len(words) - length + 1)):
                    chunk = words[offset:offset + length]
                    if indexes is not None and all(w in indexes for w in chunk):
                        yield " ".join(chunk)
    elif kind == "address":
        for length in range(26, 36):
            yield from (m.group(1) for m in re.finditer(r"(?=([13][" + B58_CLASS + "]{" + str(length - 1) + r"}))", text))
        for match in re.finditer(r"(?i)(?=(bc1[" + BECH + r"]{11,87}))", text):
            run = match.group(1)
            for length in range(14, len(run) + 1):
                yield run[:length]


def scan_streams(streams: list[dict], formats=DEFAULT_FORMATS) -> dict:
    """Return safe counts/record fingerprints; no files, requests or secret locators.

    Every unique exact stream and whitespace-only-compacted form is considered.
    shapeCounts count occurrences; uniqueShapeCounts count actual validations.
    Any valid record is a lead requiring review, never an automatic solution.
    """
    formats = tuple(formats)
    if not formats or len(set(formats)) != len(formats) or any(f not in ALL_FORMATS for f in formats):
        raise ValueError("Unknown or duplicated record formats")
    if any(not isinstance(s, dict) or not isinstance(s.get("id"), str) or not isinstance(s.get("text"), str) for s in streams):
        raise ValueError("Streams require string id and text fields")
    unique_text = {s["text"] for s in streams}
    forms = sorted(unique_text | {re.sub(r"\s", "", text) for text in unique_text})
    indexes = wordlist()[1] if "bip39" in formats else None
    shape_counts = {f: 0 for f in formats}
    tested = {f: set() for f in formats}
    valid = {f: {} for f in formats}
    for text in forms:
        for kind in formats:
            for value in shape_values(kind, text, indexes):
                shape_counts[kind] += 1
                if value in tested[kind]:
                    continue
                tested[kind].add(value)
                checked = validate_record(kind, value, indexes)
                if checked is not None:
                    canonical, metadata = checked
                    fp = fingerprint(kind, canonical)
                    valid[kind].setdefault(fp, {"format": kind, "fingerprint": fp, **metadata})
    hits = [hit for kind in formats for _, hit in sorted(valid[kind].items())]
    return {"streamCount": len(streams), "uniqueStreamCount": len(unique_text),
            "uniqueFormCount": len(forms), "formats": list(formats), "shapeCounts": shape_counts,
            "uniqueShapeCounts": {f: len(tested[f]) for f in formats},
            "executionCount": sum(len(tested[f]) for f in formats),
            "validCounts": {f: len(valid[f]) for f in formats}, "hits": hits,
            "privateReviewRequired": bool(hits), "fingerprintRule": FINGERPRINT_RULE,
            "networkQueries": 0, "rawAsciiScalarInterpretations": 0}


def self_test() -> dict:
    controls = json.loads((SUPPORT / "controls.json").read_text())
    _, indexes = wordlist()
    assert validate_record("bip39", controls["bip39_valid"], indexes)
    mnemonic_words = controls["bip39_valid"].split()
    broken_mnemonic = " ".join(mnemonic_words[:6]) + " ␞ " + " ".join(mnemonic_words[6:])
    assert not list(shape_values("bip39", broken_mnemonic, indexes))
    assert not validate_record("bip39", " ".join(["abandon"] * 12), indexes)
    for kind, key in (("extended_private", "bip32_extended_private"), ("bip38", "bip38_encrypted_private"), ("address", "legacy_address"), ("address", "segwit_v0"), ("address", "segwit_v1"), ("sec_public", "sec_compressed_generator"), ("sec_public", "sec_uncompressed_generator")):
        assert validate_record(kind, controls[key]), "Published format control failed: " + key

    def checked_encoding(payload):
        return b58encode(bytes(payload) + sha256(sha256(bytes(payload)))[:4])

    root = bytearray(b58check(controls["bip32_extended_private"]))
    root[4:13] = bytes(9)
    for version, tag in PRIVATE_VERSIONS.items():
        changed = bytearray(root)
        changed[:4] = version.to_bytes(4, "big")
        encoded_version = checked_encoding(changed)
        assert encoded_version.startswith(tag) and len(encoded_version) == 111
        assert validate_record("extended_private", encoded_version)
    for offset, value in ((5, 1), (12, 1), (45, 1)):
        changed = bytearray(root)
        changed[offset] = value
        assert not validate_record("extended_private", checked_encoding(changed))
    for invalid_scalar in (0, ORDER):
        changed = bytearray(root)
        changed[46:] = invalid_scalar.to_bytes(32, "big")
        assert not validate_record("extended_private", checked_encoding(changed))

    encrypted = bytearray(b58check(controls["bip38_encrypted_private"]))
    for prefix, allowed in ((0x42, (0xC0, 0xE0)), (0x43, (0, 4, 0x20, 0x24))):
        for flags in allowed:
            changed = bytearray(encrypted)
            changed[1:3] = bytes([prefix, flags])
            assert validate_record("bip38", checked_encoding(changed))
        changed = bytearray(encrypted)
        changed[1:3] = bytes([prefix, (0xC0 if prefix == 0x42 else 0) | 0x10])
        assert not validate_record("bip38", checked_encoding(changed))
    bad_encrypted = controls["bip38_encrypted_private"]
    bad_encrypted = bad_encrypted[:-1] + ("1" if bad_encrypted[-1] != "1" else "2")
    assert not validate_record("bip38", bad_encrypted)

    def witness_control(data, constant):
        expanded = [3, 3, 0, 2, 3]  # HRP expansion for the literal 'bc'.
        remainder = bech_polymod(expanded + data + [0] * 6) ^ constant
        checksum = [(remainder >> (5 * (5 - i))) & 31 for i in range(6)]
        return "bc1" + "".join(BECH[v] for v in data + checksum)

    v0_data = [BECH.index(c) for c in controls["segwit_v0"].lower().split("1", 1)[1]][:-6]
    v1_data = [BECH.index(c) for c in controls["segwit_v1"].lower().split("1", 1)[1]][:-6]
    assert witness_address(witness_control(v0_data, 1))
    assert witness_address(witness_control(v1_data, 0x2BC830A3))
    assert not witness_address(witness_control(v0_data, 0x2BC830A3))
    assert not witness_address(witness_control(v1_data, 1))
    assert not witness_address(witness_control(v0_data + [0], 1))
    bad_padding = v1_data[:-1] + [v1_data[-1] ^ 1]
    assert not witness_address(witness_control(bad_padding, 0x2BC830A3))
    sample = "S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy"
    assert validate_record("minikey", sample)
    short = None
    for counter in range(65536):
        number, suffix = counter, ""
        while number:
            number, remainder = divmod(number, 58)
            suffix = B58[remainder] + suffix
        candidate = "S" + "2" * 15 + (suffix or "1").rjust(6, "2")
        if validate_record("minikey", candidate):
            short = candidate
            break
    assert short is not None and len(short) == 22
    payload = b"\x80" + bytes.fromhex("00" * 31 + "01") + b"\x01"
    encoded = b58encode(payload + sha256(sha256(payload))[:4])
    assert validate_record("wif", encoded)
    assert not validate_record("wif", encoded[:-1] + ("1" if encoded[-1] != "1" else "2"))
    assert not validate_record("hex64", "0" * 64)
    assert not validate_record("sec_public", "02" + "ff" * 32)
    assert not validate_record("sec_public", "04" + "00" * 64)
    assert not validate_record("address", controls["segwit_v0"][0].upper() + controls["segwit_v0"][1:].lower())
    for control in (sample, short):
        result = scan_streams([{"id": "control", "text": "prefix::" + control + "::suffix"}], ["minikey"])
        assert result["validCounts"]["minikey"] >= 1
        assert control not in json.dumps(result)
        assert sha256(control.encode()).hex() not in json.dumps(result)
        assert not any("locator" in k.lower() for hit in result["hits"] for k in hit)
    return {"passed": True, "controls": ["official2048wordlist", "BIP39valid-invalid", "BIP39-invalid-group-barrier", "BIP32-all5SLIP132-private-versions", "invalid-root-parent-child-marker-scalar", "BIP38-all6-structural-flag-combinations", "BIP38-reserved-flags-checksum", "Base58Check", "Bech32-v0", "Bech32m-v1", "cross-checksum-version-and-invalid-padding", "SEC-oncurve", "WIF", "minikey22and30-embedded", "invalid-checksum-scalar-case-point", "safe-domain-separated-output"],
            "targetInputRead": False, "targetChecks": 0, "networkQueries": 0}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2))
    else:
        parser.print_help()
