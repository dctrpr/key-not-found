#!/usr/bin/env python3
import hashlib
import re
from collections import OrderedDict
from pathlib import Path

from bip_utils import Bip39MnemonicValidator

from run_anchor_ray_selector import build_selections
from run_second_wave_crypto_experiments import WORDLIST, derive_mnemonic_addresses
from search_visual_private_keys import check_activity, key_addresses, valid_secret


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / 'anchor_ray_selector'
OUT.mkdir(parents=True, exist_ok=True)


def add_secret(out, label, secret, source):
    if valid_secret(secret):
        out.setdefault(secret.hex(), {'label': label, 'secret': secret, 'source': source[:260]})


def byte_stream_secrets(label, values, source):
    values = [int(v) for v in values]
    if not values:
        return
    csv = ','.join(map(str, values))
    raw = bytes(v % 256 for v in values)
    yield f'{label}:csv_sha256', hashlib.sha256(csv.encode()).digest(), source
    yield f'{label}:csv_sha256d', hashlib.sha256(hashlib.sha256(csv.encode()).digest()).digest(), source
    yield f'{label}:bytes_sha256', hashlib.sha256(raw).digest(), source
    yield f'{label}:bytes_reverse_sha256', hashlib.sha256(raw[::-1]).digest(), source
    for start in range(0, max(0, len(raw) - 32 + 1)):
        chunk = raw[start:start + 32]
        yield f'{label}:bytes32:{start}', chunk, source
        yield f'{label}:bytes32_reverse:{start}', chunk[::-1], source


def bip39_from_values(label, values, source):
    validator = Bip39MnemonicValidator()
    vals = [abs(int(v)) % 2048 for v in values]
    seen = set()
    for length in (12, 15, 18, 21, 24):
        for start in range(0, len(vals) - length + 1):
            phrase = ' '.join(WORDLIST[i] for i in vals[start:start + length])
            if phrase in seen:
                continue
            if validator.IsValid(phrase):
                seen.add(phrase)
                yield {'label': f'{label}:bip39:{start}:{length}', 'phrase': phrase, 'source': source[:260]}


def selection_streams(selection, idx):
    words = selection['words']
    text = selection['text']
    clean_words = [re.sub(r'[^A-Za-z0-9]', '', item['text']) for item in words]
    indexes = [item['index'] for item in words]
    deltas = [b - a for a, b in zip(indexes, indexes[1:])]
    lengths = [len(w) for w in clean_words if w]
    firsts = [ord(w[0].lower()) - 96 for w in clean_words if w and w[0].isalpha()]
    lasts = [ord(w[-1].lower()) - 96 for w in clean_words if w and w[-1].isalpha()]
    xs = [round(item['center'][0]) for item in words]
    ys = [round(item['center'][1]) for item in words]
    ts = [round(item['t'] * 1000) for item in words]
    dists = [round(item['dist'] * 10) for item in words]
    firstlast = []
    for a, b in zip(firsts, lasts):
        firstlast.extend([a, b])
    mixed = []
    for parts in zip(indexes, lengths or [0] * len(indexes), firsts or [0] * len(indexes)):
        mixed.extend(parts)
    label_base = f"ray_index_{idx:03d}:{selection['a']}->{selection['b']}:{selection['mode']}:{selection['threshold']}:{selection['order']}"
    streams = OrderedDict(
        [
            ('word_indexes', indexes),
            ('word_index_deltas', deltas),
            ('word_lengths', lengths),
            ('first_letters', firsts),
            ('last_letters', lasts),
            ('first_last_letters', firstlast),
            ('x_centers', xs),
            ('y_centers', ys),
            ('line_t_values', ts),
            ('line_distances', dists),
            ('mixed_index_length_first', mixed),
        ]
    )
    for name, values in streams.items():
        if len(values) >= 8:
            yield f'{label_base}:{name}', values, text


def run():
    selections, _, _ = build_selections()
    selected = selections[:80]
    secrets = OrderedDict()
    mnemonics = OrderedDict()
    for idx, selection in enumerate(selected, 1):
        for label, values, source in selection_streams(selection, idx):
            for secret_label, secret, secret_source in byte_stream_secrets(label, values, source):
                add_secret(secrets, secret_label, secret, secret_source)
            for mnemonic in bip39_from_values(label, values, source):
                mnemonics.setdefault(mnemonic['phrase'], mnemonic)
    return selected, list(secrets.values()), list(mnemonics.values())


def check_secrets(secrets):
    address_map = {}
    for secret in secrets:
        for kind, address in key_addresses(secret['secret'], secret['label'], include_taproot=True):
            address_map[address] = {**secret, 'kind': kind}
    found = check_activity(address_map, batch_size=40, sleep_s=0.25) if address_map else []
    return found, address_map


def check_mnemonics(mnemonics):
    address_map = {}
    for mnemonic in mnemonics:
        for path, address in derive_mnemonic_addresses(mnemonic['phrase']):
            address_map[address] = {**mnemonic, 'path': path}
    found = check_activity(address_map, batch_size=40, sleep_s=0.25) if address_map else []
    return found, address_map


def write_report(selections, secrets, secret_addresses, secret_found, mnemonics, mnemonic_addresses, mnemonic_found):
    lines = ['# Anchor Ray Index Experiment', '']
    lines.append('Hypothesis: if the anchor rays select the right words, their page-order indexes, deltas, letter positions, and line metrics may encode the key more directly than prose hashes.')
    lines.append('')
    lines.append('## Summary')
    lines.append(f'- ray selections used: {len(selections)}')
    lines.append(f'- private-key candidates: {len(secrets)}')
    lines.append(f'- private-key addresses checked: {len(secret_addresses)}')
    lines.append(f'- private-key activity found: {len(secret_found)}')
    lines.append(f'- checksum-valid BIP39 candidates: {len(mnemonics)}')
    lines.append(f'- BIP39 addresses checked: {len(mnemonic_addresses)}')
    lines.append(f'- BIP39 activity found: {len(mnemonic_found)}')
    lines.append('')
    lines.append('## Top Source Selections Used')
    for idx, selection in enumerate(selections[:20], 1):
        lines.append(f"{idx:02d}. {selection['a']} -> {selection['b']} {selection['mode']} threshold={selection['threshold']} order={selection['order']}")
        lines.append(f"    {selection['text']}")
    lines.append('')
    lines.append('## Hits')
    if not secret_found and not mnemonic_found:
        lines.append('- none')
    for hit in secret_found:
        lines.append(f"- private key hit {hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']}")
    for hit in mnemonic_found:
        lines.append(f"- mnemonic hit {hit['address']} {hit['path']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']}")
    if mnemonics:
        lines.append('')
        lines.append('## First Checksum-Valid Mnemonics')
        for item in mnemonics[:30]:
            lines.append(f"- {item['label']}: {item['phrase']}")
    (OUT / 'anchor_ray_index_experiment.md').write_text('\n'.join(lines) + '\n')


def main():
    selections, secrets, mnemonics = run()
    print(f'ray selections used: {len(selections)}')
    print(f'private-key candidates: {len(secrets)}')
    print(f'checksum-valid BIP39 candidates: {len(mnemonics)}')
    secret_found, secret_addresses = check_secrets(secrets)
    print(f'private-key addresses checked: {len(secret_addresses)}')
    print(f'private-key activity found: {len(secret_found)}')
    mnemonic_found, mnemonic_addresses = check_mnemonics(mnemonics)
    print(f'BIP39 addresses checked: {len(mnemonic_addresses)}')
    print(f'BIP39 activity found: {len(mnemonic_found)}')
    write_report(selections, secrets, secret_addresses, secret_found, mnemonics, mnemonic_addresses, mnemonic_found)
    print(f"report: {OUT / 'anchor_ray_index_experiment.md'}")


if __name__ == '__main__':
    main()
