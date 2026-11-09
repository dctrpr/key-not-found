#!/usr/bin/env python3
import hashlib
import itertools
import re
import time
from urllib.parse import quote

import requests
from bip_utils import (
    CoinsConf,
    P2PKHAddrEncoder,
    P2WPKHAddrEncoder,
    Secp256k1PrivateKey,
    WifDecoder,
)

from read_reflected_masks import reflected_selection
from read_manual_inverted_reflections import reflected_selection as inverted_reflected_selection


P2PKH_VER = CoinsConf.BitcoinMainNet.ParamByKey('p2pkh_net_ver')
BECH32_HRP = CoinsConf.BitcoinMainNet.ParamByKey('p2wpkh_hrp')
BASE58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


PAIR_DIRECTIONS = [
    (79, 75),
    (75, 79),
    (78, 76),
    (76, 78),
]


def clean_words(text):
    return re.sub(r'[^A-Za-z0-9]+', ' ', text).split()


def key_addresses(secret_bytes, label):
    try:
        priv = Secp256k1PrivateKey.FromBytes(secret_bytes)
    except Exception:
        return []
    compressed = priv.PublicKey().RawCompressed().ToBytes()
    uncompressed = priv.PublicKey().RawUncompressed().ToBytes()
    return [
        (f'{label}:p2pkh:compressed', P2PKHAddrEncoder.EncodeKey(compressed, net_ver=P2PKH_VER)),
        (f'{label}:p2pkh:uncompressed', P2PKHAddrEncoder.EncodeKey(uncompressed, net_ver=P2PKH_VER)),
        (f'{label}:p2wpkh', P2WPKHAddrEncoder.EncodeKey(compressed, hrp=BECH32_HRP)),
    ]


def reflected_texts():
    records = []
    char_records = []
    for src, dst in PAIR_DIRECTIONS:
        parts = []
        char_parts = []
        for item in reflected_selection(src, dst):
            text = item[3]
            chars = item[4] if len(item) > 4 else text
            if text:
                parts.append(text)
            if chars:
                char_parts.append(chars)
        joined = ' '.join(parts)
        char_joined = ' '.join(char_parts)
        records.append((f'{src}_onto_{dst}', joined))
        char_records.append((f'{src}_onto_{dst}_chars', char_joined))

    inverted_records = []
    inverted_char_records = []
    for src, dst in [(79, 75), (75, 79), (78, 76), (76, 78), (77, 77)]:
        parts = []
        char_parts = []
        for item in inverted_reflected_selection(src, dst):
            text = item[3]
            chars = item[4] if len(item) > 4 else text
            if text:
                parts.append(text)
            if chars:
                char_parts.append(chars)
        if parts:
            inverted_records.append((f'inverted_{src}_onto_{dst}', ' '.join(parts)))
        if char_parts:
            inverted_char_records.append((f'inverted_{src}_onto_{dst}_chars', ' '.join(char_parts)))

    records.extend(char_records)
    records.extend(inverted_records)
    records.extend(inverted_char_records)
    word_only = [item for item in records if not item[0].endswith('_chars')]
    char_only = [item for item in records if item[0].endswith('_chars')]
    records.append(('all_in_order', ' '.join(text for _, text in word_only)))
    records.append(('all_reverse_order', ' '.join(text for _, text in reversed(word_only))))
    records.append(('all_chars_in_order', ' '.join(text for _, text in char_only)))
    records.append(('all_chars_reverse_order', ' '.join(text for _, text in reversed(char_only))))
    return records


def transforms(label, text):
    words = clean_words(text)
    letters = ''.join(re.findall(r'[A-Za-z]', text))
    alnum = ''.join(re.findall(r'[A-Za-z0-9]', text))
    variants = {
        label: text.strip(),
        f'{label}:lower': text.lower(),
        f'{label}:nospace': alnum,
        f'{label}:letters': letters,
        f'{label}:letters_lower': letters.lower(),
        f'{label}:first_letters': ''.join(w[0] for w in words if w),
        f'{label}:last_letters': ''.join(w[-1] for w in words if w),
        f'{label}:first_letters_upper': ''.join(w[0].upper() for w in words if w),
        f'{label}:last_letters_upper': ''.join(w[-1].upper() for w in words if w),
    }
    for key, value in list(variants.items()):
        variants[f'{key}:reverse'] = value[::-1]
    return variants


def direct_wif_candidates(label, value):
    compact = ''.join(ch for ch in value if ch in BASE58)
    for length in (51, 52):
        for start in range(0, len(compact) - length + 1):
            candidate = compact[start:start + length]
            if candidate[0] not in '5KL':
                continue
            try:
                secret = WifDecoder.Decode(candidate)
            except Exception:
                continue
            yield f'{label}:wif:{start}:{length}', candidate, secret


def check_activity(address_map):
    found = []
    addresses = sorted(address_map)
    session = requests.Session()
    for index in range(0, len(addresses), 35):
        batch = addresses[index:index + 35]
        active = quote('|'.join(batch), safe='|')
        response = session.get(f'https://blockchain.info/multiaddr?active={active}', timeout=30)
        response.raise_for_status()
        for item in response.json().get('addresses', []):
            total_received = int(item.get('total_received', 0))
            final_balance = int(item.get('final_balance', 0))
            if total_received or final_balance:
                found.append({**address_map[item['address']], 'total_received': total_received, 'final_balance': final_balance})
        time.sleep(0.35)
    return found


def main():
    address_map = {}
    summaries = []
    for label, text in reflected_texts():
        summaries.append((label, text))
        for tlabel, value in transforms(label, text).items():
            if not value:
                continue
            digest = hashlib.sha256(value.encode()).digest()
            for kind, address in key_addresses(digest, f'{tlabel}:sha256'):
                address_map[address] = {'label': tlabel, 'kind': kind, 'source': value[:200], 'secret': digest.hex()}
            for wlabel, wif, secret in direct_wif_candidates(tlabel, value):
                for kind, address in key_addresses(secret, wlabel):
                    address_map[address] = {'label': wlabel, 'kind': kind, 'source': wif, 'secret': secret.hex()}

    print('Reflected selected texts:')
    for label, text in summaries:
        print(f'\n[{label}] {text}')

    print(f'\nChecking {len(address_map)} reflected-text-derived addresses...')
    found = check_activity(address_map)
    print(f'Addresses with activity: {len(found)}')
    for hit in found:
        print()
        print(f"{hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']}")
        print(f"{hit['label']} secret={hit['secret']}")
        print(hit['source'])


if __name__ == '__main__':
    main()
