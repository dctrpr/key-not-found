#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests
from bip_utils import (
    Bip39SeedGenerator,
    Bip39MnemonicValidator,
    Bip44,
    Bip44Changes,
    Bip44Coins,
    Bip49,
    Bip49Coins,
    Bip84,
    Bip84Coins,
)


ROOT = Path(__file__).resolve().parents[1]
HITS_FILE = Path('/tmp/maxpuzzle_highlight_hits.json')


def derive_addresses(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate('')
    derivations = [
        ('m/44h/0h/0h/0/0', Bip44.FromSeed(seed, Bip44Coins.BITCOIN)),
        ('m/49h/0h/0h/0/0', Bip49.FromSeed(seed, Bip49Coins.BITCOIN)),
        ('m/84h/0h/0h/0/0', Bip84.FromSeed(seed, Bip84Coins.BITCOIN)),
    ]
    out = []
    for path, ctx in derivations:
        addr = (
            ctx.Purpose()
            .Coin()
            .Account(0)
            .Change(Bip44Changes.CHAIN_EXT)
            .AddressIndex(0)
            .PublicKey()
            .ToAddress()
        )
        out.append((path, addr))
    return out


def chunks(items, size):
    for idx in range(0, len(items), size):
        yield items[idx : idx + size]


def main():
    if not HITS_FILE.exists():
        print('Missing /tmp/maxpuzzle_highlight_hits.json. Run: node scripts/investigate_highlights.js --json > /tmp/maxpuzzle_highlight_hits.json', file=sys.stderr)
        return 2

    hits = json.loads(HITS_FILE.read_text())
    address_map = {}
    skipped = 0
    validator = Bip39MnemonicValidator()
    for hit in hits:
        if not validator.IsValid(hit['phrase']):
            skipped += 1
            continue
        for path, address in derive_addresses(hit['phrase']):
            address_map[address] = {**hit, 'path': path, 'address': address}

    addresses = sorted(address_map)
    print(f'Checking {len(hits) - skipped} strict mnemonics / {len(addresses)} unique addresses... skipped {skipped} local-checksum false positives.')

    found = []
    session = requests.Session()
    for batch in chunks(addresses, 35):
        active = '|'.join(batch)
        url = f'https://blockchain.info/multiaddr?active={quote(active, safe="|")}'
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        for item in data.get('addresses', []):
            total_received = int(item.get('total_received', 0))
            final_balance = int(item.get('final_balance', 0))
            if total_received > 0 or final_balance > 0:
                hit = address_map[item['address']]
                found.append(
                    {
                        **hit,
                        'total_received': total_received,
                        'final_balance': final_balance,
                    }
                )
        time.sleep(0.35)

    print(f'Addresses with activity: {len(found)}')
    for hit in found:
        print()
        print(f"{hit['address']} path={hit['path']} received={hit['total_received']} balance={hit['final_balance']}")
        print(f"{hit['source']} {hit['edit']}")
        print(hit['phrase'])

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
