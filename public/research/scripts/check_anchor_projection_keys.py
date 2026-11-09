#!/usr/bin/env python3
import hashlib
import re
from pathlib import Path

from search_visual_private_keys import check_activity, key_addresses


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'analysis_outputs' / 'source_audit' / 'visual_anchor_projections.md'


def variants(label, text):
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return
    base = {
        label: text,
        f'{label}:lower': text.lower(),
        f'{label}:nospace': re.sub(r'[^A-Za-z0-9]', '', text),
        f'{label}:reverse': text[::-1],
    }
    for key, value in base.items():
        if value:
            yield key, value


def projection_strings():
    text = REPORT.read_text()
    for line in text.splitlines():
        if line.startswith('- same-line text:'):
            yield 'same_line', line.split(':', 1)[1].strip()
        if line.startswith('- nearest words:'):
            words = [part.split('(', 1)[0].strip() for part in line.split(':', 1)[1].split('/')]
            yield 'nearest_words', ' '.join(word for word in words if word)


def candidate_secrets():
    seen = set()
    for idx, (kind, text) in enumerate(projection_strings(), 1):
        for label, value in variants(f'{kind}_{idx}', text):
            for hash_name, digest in [
                ('sha256', hashlib.sha256(value.encode()).digest()),
                ('sha256d', hashlib.sha256(hashlib.sha256(value.encode()).digest()).digest()),
                ('sha3_256', hashlib.sha3_256(value.encode()).digest()),
                ('blake2s', hashlib.blake2s(value.encode()).digest()),
            ]:
                key = (label, hash_name, digest)
                if key in seen:
                    continue
                seen.add(key)
                yield {
                    'label': f'{label}:{hash_name}',
                    'secret': digest,
                    'source': value,
                }


def main():
    address_map = {}
    count = 0
    for info in candidate_secrets():
        count += 1
        for kind, address in key_addresses(info['secret'], info['label'], include_taproot=True):
            address_map[address] = {**info, 'kind': kind}
    print(f'anchor projection candidate secrets: {count}')
    print(f'addresses to check: {len(address_map)}')
    found = check_activity(address_map, batch_size=25, sleep_s=0.5)
    print(f'activity found: {len(found)}')
    for hit in found:
        print(f"{hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']} source={hit['source']}")


if __name__ == '__main__':
    main()
