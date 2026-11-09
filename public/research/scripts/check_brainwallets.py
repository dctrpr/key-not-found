#!/usr/bin/env python3
import hashlib
import re
import time
from urllib.parse import quote

import requests
from bip_utils import (
    CoinsConf,
    P2PKHAddrEncoder,
    P2WPKHAddrEncoder,
    Secp256k1PrivateKey,
)

from search_structured_candidates import HIGHLIGHT_GROUPS, TEXT_FILE


P2PKH_VER = CoinsConf.BitcoinMainNet.ParamByKey('p2pkh_net_ver')
BECH32_HRP = CoinsConf.BitcoinMainNet.ParamByKey('p2wpkh_hrp')


def normalize(text):
    return re.sub(r'\s+', ' ', text.strip())


def mirror_text(text):
    return text[::-1]


def address_from_secret(secret_bytes):
    priv = Secp256k1PrivateKey.FromBytes(secret_bytes)
    compressed = priv.PublicKey().RawCompressed().ToBytes()
    uncompressed = priv.PublicKey().RawUncompressed().ToBytes()
    return [
        ('sha256:p2pkh:compressed', P2PKHAddrEncoder.EncodeKey(compressed, net_ver=P2PKH_VER)),
        ('sha256:p2pkh:uncompressed', P2PKHAddrEncoder.EncodeKey(uncompressed, net_ver=P2PKH_VER)),
        ('sha256:p2wpkh', P2WPKHAddrEncoder.EncodeKey(compressed, hrp=BECH32_HRP)),
    ]


def candidates():
    article = normalize(TEXT_FILE.read_text())
    orange = normalize(' '.join(HIGHLIGHT_GROUPS['orange']))
    inverted = normalize(' '.join(HIGHLIGHT_GROUPS['inverted']))
    first_letters = ''.join(group.strip()[0] for group in HIGHLIGHT_GROUPS['orange'] + HIGHLIGHT_GROUPS['inverted'] if group.strip())
    last_letters = ''.join(group.strip()[-1] for group in HIGHLIGHT_GROUPS['orange'] + HIGHLIGHT_GROUPS['inverted'] if group.strip())

    base = {
        'title': 'BITCOIN IS TOXIC AF',
        'tweet-quote': "I hid a private Bitcoin key encoded in this piece I wrote for Bitcoin Magazine Mr President Nobody's figured it out yet but it's for 20 BTC",
        'mirror-clue': 'Mirror writing neurological reflections on an unusual phenomenon',
        'article': article,
        'orange-highlights': orange,
        'inverted-highlights': inverted,
        'orange-then-inverted': normalize(f'{orange} {inverted}'),
        'inverted-then-orange': normalize(f'{inverted} {orange}'),
        'highlight-first-letters': first_letters,
        'highlight-last-letters': last_letters,
    }

    for label, text in base.items():
        variants = {
            label: text,
            f'{label}:lower': text.lower(),
            f'{label}:nospace': re.sub(r'[^A-Za-z0-9]', '', text),
            f'{label}:mirror': mirror_text(text),
            f'{label}:mirror-lower': mirror_text(text.lower()),
            f'{label}:mirror-nospace': mirror_text(re.sub(r'[^A-Za-z0-9]', '', text)),
        }
        for variant_label, variant_text in variants.items():
            if variant_text:
                yield variant_label, variant_text


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
    for label, text in candidates():
        digest = hashlib.sha256(text.encode()).digest()
        for kind, address in address_from_secret(digest):
            address_map[address] = {
                'label': label,
                'kind': kind,
                'address': address,
                'sha256_hex': digest.hex(),
            }

    print(f'Checking {len(address_map)} brainwallet-derived addresses...')
    found = check_activity(address_map)
    print(f'Addresses with activity: {len(found)}')
    for hit in found:
        print()
        print(f"{hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']}")
        print(f"{hit['label']} sha256={hit['sha256_hex']}")


if __name__ == '__main__':
    main()
