#!/usr/bin/env python3
import hashlib
import re
from collections import OrderedDict
from pathlib import Path

from search_visual_private_keys import check_activity, key_addresses


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / 'overdose_series'
OUT.mkdir(parents=True, exist_ok=True)


SOURCE_STRINGS = OrderedDict(
    [
        ('el_salvador_feature', 'Featuring OVERDOSE with Max Keiser'),
        ('puzzle_title_common', 'Bitcoin is Toxic AF'),
        ('puzzle_title_upper', 'BITCOIN IS TOXIC AF'),
        ('orange_party_overdose', 'Overdose: Who is The Banana Republic Now, Biatch?'),
        ('orange_party_quote', 'You cannot centralize power and adopt Bitcoin at the same time.'),
        ('withdrawal_overdose', 'Overdose: Buy Love, Sell Fear'),
        ('withdrawal_title', 'Buy Love, Sell Fear'),
        ('inscription_overdose', 'Overdose: Bitcoin Is A Mirror That Reflects All'),
        ('inscription_title', 'Bitcoin Is A Mirror That Reflects All'),
        ('inscription_teaser', 'Take a good, long look at Bitcoin: What does it tell you about yourself?'),
        ('inscription_title_max', 'Bitcoin Is A Mirror That Reflects All Max Keiser'),
        ('series_titles_joined', 'Bitcoin is Toxic AF | Who is The Banana Republic Now, Biatch? | Buy Love, Sell Fear | Bitcoin Is A Mirror That Reflects All'),
        ('series_titles_reverse_order', 'Bitcoin Is A Mirror That Reflects All | Buy Love, Sell Fear | Who is The Banana Republic Now, Biatch? | Bitcoin is Toxic AF'),
        ('mirror_clue_plus_title', 'Mirror writing neurological reflections on an unusual phenomenon Bitcoin Is A Mirror That Reflects All'),
        ('announcement_plus_title', "I hid a private Bitcoin key encoded in this piece I wrote for Bitcoin Magazine Mr President Nobody's figured it out yet but it's for 20 BTC Bitcoin Is A Mirror That Reflects All"),
        ('inscription_block', '786501'),
        ('inscription_tx', '54e48e5f5c656b26c3bca14a8c95aa583d07ebe84dde3b7dd4a78f4e4186e713'),
        ('inscription_hash', '6c53cd987119ef797d5adccd76241247988a0a5ef783572a9972e7371c5fb0cc'),
    ]
)


def variants(label, text):
    compact = re.sub(r'[^A-Za-z0-9]', '', text)
    variants = OrderedDict(
        [
            (label, text),
            (f'{label}:lower', text.lower()),
            (f'{label}:nospace', compact),
            (f'{label}:nospace_lower', compact.lower()),
            (f'{label}:reverse', text[::-1]),
            (f'{label}:reverse_nospace', compact[::-1]),
        ]
    )
    return variants


def candidate_secrets():
    out = OrderedDict()
    for source_label, text in SOURCE_STRINGS.items():
        for label, value in variants(source_label, text).items():
            if not value:
                continue
            raw = value.encode('utf-8')
            for hash_name, secret in [
                ('sha256', hashlib.sha256(raw).digest()),
                ('sha256d', hashlib.sha256(hashlib.sha256(raw).digest()).digest()),
                ('sha3_256', hashlib.sha3_256(raw).digest()),
                ('blake2s', hashlib.blake2s(raw, digest_size=32).digest()),
            ]:
                out.setdefault(secret.hex(), {'label': f'{label}:{hash_name}', 'secret': secret, 'source': value})
            hex_text = re.sub(r'[^0-9a-fA-F]', '', value)
            if len(hex_text) == 64:
                secret = bytes.fromhex(hex_text)
                out.setdefault(secret.hex(), {'label': f'{label}:hex64', 'secret': secret, 'source': value})
                out.setdefault(secret[::-1].hex(), {'label': f'{label}:hex64_reverse_bytes', 'secret': secret[::-1], 'source': value})
    return list(out.values())


def main():
    candidates = candidate_secrets()
    address_map = {}
    for candidate in candidates:
        for kind, address in key_addresses(candidate['secret'], candidate['label'], include_taproot=True):
            address_map[address] = {**candidate, 'kind': kind}
    print(f'source strings: {len(SOURCE_STRINGS)}')
    print(f'candidate private keys: {len(candidates)}')
    print(f'derived addresses to check: {len(address_map)}')
    found = check_activity(address_map, batch_size=40, sleep_s=0.25)
    print(f'active addresses found: {len(found)}')
    lines = ['# OVERDOSE Series Key Check', '']
    lines.append('Scope: small branch for recurring Max Keiser OVERDOSE titles, including the later official title `Bitcoin Is A Mirror That Reflects All`.')
    lines.append('')
    lines.append('## Summary')
    lines.append(f'- source strings: {len(SOURCE_STRINGS)}')
    lines.append(f'- candidate private keys: {len(candidates)}')
    lines.append(f'- derived addresses checked: {len(address_map)}')
    lines.append(f'- active addresses found: {len(found)}')
    lines.append('')
    lines.append('## Source Strings')
    for label, text in SOURCE_STRINGS.items():
        lines.append(f'- {label}: {text}')
    lines.append('')
    lines.append('## Hits')
    if not found:
        lines.append('- none')
    for hit in found:
        lines.append(f"- {hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']} source={hit['source']}")
    (OUT / 'overdose_series_key_check.md').write_text('\n'.join(lines) + '\n')
    print(f"report: {OUT / 'overdose_series_key_check.md'}")


if __name__ == '__main__':
    main()
