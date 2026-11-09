#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import re
import time
from collections import OrderedDict
from urllib.parse import quote

import requests
from bip_utils import (
    CoinsConf,
    P2TRAddrEncoder,
    P2WPKHAddrEncoder,
    Secp256k1PrivateKey,
    WifDecoder,
)

from read_reflected_masks import reflected_selection
from read_manual_inverted_reflections import reflected_selection as inverted_reflected_selection
from highres_reflection_extract import reflected_selection as highres_reflected_selection


BECH32_HRP = CoinsConf.BitcoinMainNet.ParamByKey('p2wpkh_hrp')
BASE58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
SECP256K1_N = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141', 16)

ORANGE_PAIRS = [(79, 75), (75, 79), (78, 76), (76, 78), (78, 75), (79, 76)]
INVERTED_PAIRS = [(79, 75), (75, 79), (78, 76), (76, 78), (77, 77)]


def b58decode(value):
    n = 0
    for ch in value:
        idx = BASE58.find(ch)
        if idx < 0:
            raise ValueError(f'not base58: {ch}')
        n = n * 58 + idx
    leading = len(value) - len(value.lstrip('1'))
    raw = n.to_bytes((n.bit_length() + 7) // 8, 'big') if n else b''
    return b'\x00' * leading + raw


def b58encode(raw):
    n = int.from_bytes(raw, 'big')
    out = ''
    while n:
        n, rem = divmod(n, 58)
        out = BASE58[rem] + out
    leading = len(raw) - len(raw.lstrip(b'\x00'))
    return '1' * leading + (out or '')


def b58check(version, payload):
    body = bytes([version]) + payload
    checksum = hashlib.sha256(hashlib.sha256(body).digest()).digest()[:4]
    return b58encode(body + checksum)


def hash160(raw):
    ripe = hashlib.new('ripemd160')
    ripe.update(hashlib.sha256(raw).digest())
    return ripe.digest()


def clean_words(text):
    return re.sub(r'[^A-Za-z0-9]+', ' ', text).split()


def valid_secret(secret):
    if len(secret) != 32:
        return False
    n = int.from_bytes(secret, 'big')
    return 1 <= n < SECP256K1_N


def key_addresses(secret_bytes, label, include_taproot=True):
    if not valid_secret(secret_bytes):
        return []
    try:
        priv = Secp256k1PrivateKey.FromBytes(secret_bytes)
    except Exception:
        return []
    compressed = priv.PublicKey().RawCompressed().ToBytes()
    uncompressed = priv.PublicKey().RawUncompressed().ToBytes()
    pub_hash = hash160(compressed)
    redeem = b'\x00\x14' + pub_hash
    out = [
        (f'{label}:p2pkh:compressed', b58check(0, hash160(compressed))),
        (f'{label}:p2pkh:uncompressed', b58check(0, hash160(uncompressed))),
        (f'{label}:p2sh-p2wpkh', b58check(5, hash160(redeem))),
        (f'{label}:p2wpkh', P2WPKHAddrEncoder.EncodeKey(compressed, hrp=BECH32_HRP)),
    ]
    if include_taproot:
        out.append((f'{label}:p2tr', P2TRAddrEncoder.EncodeKey(compressed, hrp=BECH32_HRP)))
    return out


def collect_records(orange_source='lowres'):
    records = []
    sources = []
    if orange_source in ('lowres', 'both'):
        sources.append(('orange', ORANGE_PAIRS, reflected_selection))
    if orange_source in ('highres', 'both'):
        sources.append(('highres_orange', ORANGE_PAIRS, highres_reflected_selection))
    sources.append(('inverted', INVERTED_PAIRS, inverted_reflected_selection))

    for kind, pairs, fn in sources:
        for source, target in pairs:
            group = f'{kind}_{source}_onto_{target}'
            for idx, src_box, refl_box, text, chars in fn(source, target):
                if not (text or chars):
                    continue
                records.append(
                    {
                        'kind': kind,
                        'group': group,
                        'source_page': source,
                        'target_page': target,
                        'idx': idx,
                        'src_box': tuple(src_box),
                        'refl_box': tuple(refl_box),
                        'text': text.strip(),
                        'chars': chars.strip(),
                    }
                )
    return records


def text_variants(label, text):
    words = clean_words(text)
    letters = ''.join(re.findall(r'[A-Za-z]', text))
    alnum = ''.join(re.findall(r'[A-Za-z0-9]', text))
    lower_words = [w.lower() for w in words]
    variants = OrderedDict()
    variants[label] = text.strip()
    variants[f'{label}:lower'] = text.lower().strip()
    variants[f'{label}:nospace'] = alnum
    variants[f'{label}:nospace_lower'] = alnum.lower()
    variants[f'{label}:letters'] = letters
    variants[f'{label}:letters_lower'] = letters.lower()
    variants[f'{label}:first_letters'] = ''.join(w[0] for w in words if w)
    variants[f'{label}:last_letters'] = ''.join(w[-1] for w in words if w)
    variants[f'{label}:firstlast'] = ''.join((w[0] + w[-1]) for w in words if w)
    variants[f'{label}:lastfirst'] = ''.join((w[-1] + w[0]) for w in words if w)
    variants[f'{label}:word_lengths_csv'] = ','.join(str(len(w)) for w in words)
    variants[f'{label}:word_lengths_digits'] = ''.join(str(len(w) % 10) for w in words)
    variants[f'{label}:alpha_positions'] = ''.join(f'{ord(ch.lower()) - 96:02d}' for ch in letters if ch.isalpha())
    variants[f'{label}:bip39ish_words'] = ' '.join(w for w in lower_words if len(w) >= 3)
    for key, value in list(variants.items()):
        variants[f'{key}:reverse'] = value[::-1]
    return variants


def has_min_entropy(value):
    compact = ''.join(re.findall(r'[A-Za-z0-9]', value))
    if len(compact) < 16:
        return False
    if compact.isdigit() and len(compact) < 32:
        return False
    return True


def digest_candidates(label, value):
    raw = value.encode('utf-8')
    if not raw or not has_min_entropy(value):
        return
    hashes = [
        ('sha256', hashlib.sha256(raw).digest()),
        ('sha256d', hashlib.sha256(hashlib.sha256(raw).digest()).digest()),
        ('sha3_256', hashlib.sha3_256(raw).digest()),
        ('blake2s', hashlib.blake2s(raw, digest_size=32).digest()),
        ('sha512_first32', hashlib.sha512(raw).digest()[:32]),
        ('sha512_last32', hashlib.sha512(raw).digest()[-32:]),
    ]
    for name, secret in hashes:
        yield f'{label}:{name}', secret, value[:220]


def direct_text_candidates(label, value, include_base58_raw=False, include_ascii_windows=False, include_loose_hex=False):
    # Whole-text aggregates can be long enough to create many mostly-random
    # sliding windows. Hashes still cover them; direct scans stay bounded.
    if len(value) > 420:
        value = value[:210] + value[-210:]
    hex_sources = [m.group(0) for m in re.finditer(r'(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])', value)]
    if include_loose_hex:
        hex_sources.append(''.join(re.findall(r'[0-9a-fA-F]', value)))
    for hex_source in hex_sources:
        for start in range(0, max(0, len(hex_source) - 64 + 1)):
            chunk = hex_source[start:start + 64]
            if len(chunk) == 64:
                secret = bytes.fromhex(chunk)
                yield f'{label}:hex64:{start}', secret, chunk
                yield f'{label}:hex64_revbytes:{start}', secret[::-1], chunk

    compact_b58 = ''.join(ch for ch in value if ch in BASE58)
    for length in range(43, 53):
        for start in range(0, max(0, len(compact_b58) - length + 1)):
            chunk = compact_b58[start:start + length]
            if length in (51, 52) and chunk[0] in '5KL':
                try:
                    yield f'{label}:wif:{start}:{length}', WifDecoder.Decode(chunk), chunk
                except Exception:
                    pass
            if include_base58_raw:
                try:
                    raw = b58decode(chunk)
                except ValueError:
                    continue
                if len(raw) == 32:
                    yield f'{label}:base58raw:{start}:{length}', raw, chunk
                if len(raw) == 33 and raw[0] == 0:
                    yield f'{label}:base58raw0:{start}:{length}', raw[1:], chunk

    raw = value.encode('utf-8')
    if len(raw) == 32:
        yield f'{label}:ascii32_exact', raw, value
    elif include_ascii_windows:
        for start in range(0, max(0, len(raw) - 32 + 1)):
            chunk = raw[start:start + 32]
            if len(chunk) == 32:
                yield f'{label}:ascii32:{start}', chunk, chunk.decode('utf-8', 'replace')


def byte_windows(label, values, source, include_reverse=True):
    data = bytes(v % 256 for v in values)
    for start in range(0, max(0, len(data) - 32 + 1)):
        secret = data[start:start + 32]
        yield f'{label}:bytes32:{start}', secret, source
        if include_reverse:
            yield f'{label}:bytes32_rev:{start}', secret[::-1], source
    if data:
        yield f'{label}:bytes_sha256', hashlib.sha256(data).digest(), source


def word_stream_candidates(label, text, include_windows=False):
    words = clean_words(text)
    letters = [ord(ch.lower()) - 96 for ch in ''.join(re.findall(r'[A-Za-z]', text)) if ch.isalpha()]
    firsts = [ord(w[0].lower()) - 96 for w in words if w and w[0].isalpha()]
    lasts = [ord(w[-1].lower()) - 96 for w in words if w and w[-1].isalpha()]
    lengths = [len(w) for w in words]
    streams = {
        'letter_positions': letters,
        'first_positions': firsts,
        'last_positions': lasts,
        'firstlast_positions': list(itertools.chain.from_iterable(zip(firsts, lasts))) if len(firsts) == len(lasts) else [],
        'word_lengths': lengths,
        'word_lengths_plus_firsts': [a + b for a, b in zip(lengths, firsts)],
        'word_lengths_times_firsts': [a * b for a, b in zip(lengths, firsts)],
    }
    for name, values in streams.items():
        if len(values) >= 16:
            source = ','.join(map(str, values[:120]))
            yield f'{label}:{name}:sha256', hashlib.sha256(bytes(v % 256 for v in values)).digest(), source
            if include_windows:
                yield from byte_windows(f'{label}:{name}', values, source)


def geometry_candidates(records):
    groups = OrderedDict()
    for rec in records:
        groups.setdefault(rec['group'], []).append(rec)
    for group, items in groups.items():
        raw = []
        normalized = []
        deltas = []
        csv_parts = []
        for rec in items:
            values = [
                rec['source_page'],
                rec['target_page'],
                rec['idx'],
                *rec['src_box'],
                *rec['refl_box'],
                rec['src_box'][2] - rec['src_box'][0],
                rec['src_box'][3] - rec['src_box'][1],
                rec['refl_box'][2] - rec['refl_box'][0],
                rec['refl_box'][3] - rec['refl_box'][1],
                len(clean_words(rec['text'])),
                len(clean_words(rec['chars'])),
                len(rec['text']),
                len(rec['chars']),
            ]
            raw.extend(values)
            csv_parts.append(','.join(map(str, values)))
            for value in values:
                normalized.append(round(value / 2805 * 255))
                normalized.append(value // 256)
                normalized.append(value % 256)
            x1, y1, x2, y2 = rec['src_box']
            rx1, ry1, rx2, ry2 = rec['refl_box']
            deltas.extend([abs(rx1 - x1), abs(rx2 - x2), abs(ry1 - y1), abs(ry2 - y2), x2 - x1, y2 - y1])

        source = ' / '.join(csv_parts)
        yield from byte_windows(f'{group}:geometry_raw_lowbytes', raw, source)
        yield from byte_windows(f'{group}:geometry_normalized', normalized, source)
        yield from byte_windows(f'{group}:geometry_deltas', deltas, source)
        yield f'{group}:geometry_csv_sha256', hashlib.sha256('|'.join(csv_parts).encode()).digest(), source
        yield f'{group}:geometry_csv_sha256_reverse', hashlib.sha256('|'.join(reversed(csv_parts)).encode()).digest(), source


def generate_candidates(
    records,
    include_base58_raw=False,
    include_ascii_windows=False,
    include_word_windows=False,
    include_loose_hex=False,
    priority_only=False,
):
    candidates = OrderedDict()

    def add(label, secret, source):
        if valid_secret(secret):
            candidates.setdefault(secret.hex(), {'label': label, 'secret': secret, 'source': source})

    grouped_text = OrderedDict()
    for rec in records:
        grouped_text.setdefault(rec['group'], {'text': [], 'chars': []})
        if rec['text']:
            grouped_text[rec['group']]['text'].append(rec['text'])
        if rec['chars']:
            grouped_text[rec['group']]['chars'].append(rec['chars'])
        if not priority_only:
            for field in ('text', 'chars'):
                value = rec[field]
                if not value:
                    continue
                for tlabel, variant in text_variants(f"{rec['group']}:box{rec['idx']}:{field}", value).items():
                    for label, secret, source in digest_candidates(tlabel, variant):
                        add(label, secret, source)
                    for label, secret, source in direct_text_candidates(
                        tlabel,
                        variant,
                        include_base58_raw=include_base58_raw,
                        include_ascii_windows=include_ascii_windows,
                        include_loose_hex=include_loose_hex,
                    ):
                        add(label, secret, source)
                    for label, secret, source in word_stream_candidates(tlabel, variant, include_windows=include_word_windows):
                        add(label, secret, source)

    all_text_parts = []
    for group, fields in grouped_text.items():
        for field, parts in fields.items():
            joined = ' '.join(parts)
            all_text_parts.append((f'{group}:{field}:joined', joined))
            all_text_parts.append((f'{group}:{field}:joined_reverse_boxes', ' '.join(reversed(parts))))
    all_text_parts.append(('all_groups_text', ' '.join(text for _, text in all_text_parts)))
    all_text_parts.append(('all_groups_text_reverse', ' '.join(text for _, text in reversed(all_text_parts))))

    for label, text in all_text_parts:
        for tlabel, variant in text_variants(label, text).items():
            for clabel, secret, source in digest_candidates(tlabel, variant):
                add(clabel, secret, source)
            for clabel, secret, source in direct_text_candidates(
                tlabel,
                variant,
                include_base58_raw=include_base58_raw,
                include_ascii_windows=include_ascii_windows,
                include_loose_hex=include_loose_hex,
            ):
                add(clabel, secret, source)
            for clabel, secret, source in word_stream_candidates(tlabel, variant, include_windows=include_word_windows):
                add(clabel, secret, source)

    for label, secret, source in geometry_candidates(records):
        add(label, secret, source)

    return candidates


def build_address_map(candidates, include_taproot=True, kind_filter='all'):
    address_map = {}
    for info in candidates.values():
        for kind, address in key_addresses(info['secret'], info['label'], include_taproot=include_taproot):
            if kind_filter != 'all' and kind_filter not in kind:
                continue
            address_map[address] = {**info, 'kind': kind}
    return address_map


def check_activity(address_map, batch_size=25, sleep_s=1.25, start_batch=0):
    found = []
    addresses = sorted(address_map)
    session = requests.Session()
    total_batches = (len(addresses) + batch_size - 1) // batch_size
    for batch_no, index in enumerate(range(0, len(addresses), batch_size)):
        if batch_no < start_batch:
            continue
        batch = addresses[index:index + batch_size]
        active = quote('|'.join(batch), safe='|')
        for attempt in range(8):
            response = session.get(f'https://blockchain.info/multiaddr?active={active}', timeout=30)
            if response.status_code != 429:
                response.raise_for_status()
                break
            wait = sleep_s * (2 ** attempt)
            print(f'429 at batch {batch_no + 1}/{total_batches}; sleeping {wait:.1f}s', flush=True)
            time.sleep(wait)
        else:
            response.raise_for_status()
        for item in response.json().get('addresses', []):
            total_received = int(item.get('total_received', 0))
            final_balance = int(item.get('final_balance', 0))
            if total_received or final_balance:
                found.append({**address_map[item['address']], 'address': item['address'], 'total_received': total_received, 'final_balance': final_balance})
        if (batch_no + 1) % 50 == 0 or batch_no == total_batches - 1:
            print(f'checked batch {batch_no + 1}/{total_batches}', flush=True)
        time.sleep(sleep_s)
    return found


def main():
    parser = argparse.ArgumentParser(description='Search second-stage visual/reflection private key candidates.')
    parser.add_argument('--check-chain', action='store_true', help='check generated addresses through blockchain.info')
    parser.add_argument('--include-base58-raw', action='store_true', help='also scan raw base58 32-byte sliding windows over prose')
    parser.add_argument('--include-ascii-windows', action='store_true', help='also scan raw 32-byte ASCII windows over prose')
    parser.add_argument('--include-word-windows', action='store_true', help='also scan every 32-byte window of word/letter numeric streams')
    parser.add_argument('--include-loose-hex', action='store_true', help='also form 64-hex windows from all A-F characters in prose')
    parser.add_argument('--priority-only', action='store_true', help='check joined selections and geometry, but skip per-box expansions')
    parser.add_argument('--orange-source', choices=['lowres', 'highres', 'both'], default='lowres', help='which orange reflected-mask source to search')
    parser.add_argument('--no-taproot', action='store_true', help='skip p2tr address derivation/checking')
    parser.add_argument('--kind-filter', default='all', help='substring filter for address kind, e.g. p2pkh, p2wpkh, p2sh-p2wpkh, p2tr')
    parser.add_argument('--batch-size', type=int, default=25, help='addresses per blockchain.info multiaddr request')
    parser.add_argument('--sleep', type=float, default=1.25, help='seconds between blockchain.info requests')
    parser.add_argument('--start-batch', type=int, default=0, help='resume checking at this zero-based batch index')
    parser.add_argument('--limit', type=int, default=0, help='limit candidate secrets before address derivation, for quick tests')
    args = parser.parse_args()

    records = collect_records(orange_source=args.orange_source)
    candidates = generate_candidates(
        records,
        include_base58_raw=args.include_base58_raw,
        include_ascii_windows=args.include_ascii_windows,
        include_word_windows=args.include_word_windows,
        include_loose_hex=args.include_loose_hex,
        priority_only=args.priority_only,
    )
    if args.limit:
        candidates = OrderedDict(list(candidates.items())[: args.limit])
    address_map = build_address_map(candidates, include_taproot=not args.no_taproot, kind_filter=args.kind_filter)

    print(f'Reflected records: {len(records)}')
    print(f'Unique private-key candidates: {len(candidates)}')
    print(f'Unique addresses: {len(address_map)}')
    print('First 20 candidate labels:')
    for info in itertools.islice(candidates.values(), 20):
        print(f"  {info['secret'].hex()}  {info['label']}  source={info['source'][:90]}")

    if args.check_chain:
        print(f'Checking {len(address_map)} addresses...')
        found = check_activity(address_map, batch_size=args.batch_size, sleep_s=args.sleep, start_batch=args.start_batch)
        print(f'Addresses with activity: {len(found)}')
        for hit in found:
            print()
            print(f"{hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']}")
            print(f"{hit['label']} secret={hit['secret'].hex()}")
            print(hit['source'][:500])


if __name__ == '__main__':
    main()
