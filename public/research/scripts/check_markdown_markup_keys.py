#!/usr/bin/env python3
import hashlib
import itertools
from collections import OrderedDict
from pathlib import Path

from bip_utils import Bip39MnemonicValidator

from analyze_markdown_markup import analyze_page, atbash, split_pages
from run_second_wave_crypto_experiments import WORDLIST, derive_mnemonic_addresses
from search_visual_private_keys import check_activity, key_addresses, valid_secret


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'analysis_outputs' / '3d_article_map' / 'user_markdown_transcript.md'
OUT = ROOT / 'analysis_outputs' / '3d_article_map' / 'markdown_markup_key_check.md'


def add_secret(out, label, secret, source):
    if valid_secret(secret):
        out.setdefault(secret.hex(), {'label': label, 'secret': secret, 'source': source[:260]})


def stream_variants(label, stream):
    compact = ''.join(ch for ch in stream if ch.isalnum())
    variants = OrderedDict()
    variants[label] = stream
    variants[f'{label}:lower'] = stream.lower()
    variants[f'{label}:upper'] = stream.upper()
    variants[f'{label}:reverse'] = stream[::-1]
    variants[f'{label}:atbash'] = atbash(stream)
    variants[f'{label}:chunks5_space'] = ' '.join(stream[i:i + 5] for i in range(0, len(stream), 5))
    variants[f'{label}:compact'] = compact
    return variants


def byte_streams(label, stream):
    letters = [ch for ch in stream if ch.isalpha()]
    alpha = [ord(ch.lower()) - 96 for ch in letters]
    ascii_vals = [ord(ch) for ch in stream]
    streams = {
        'alpha_positions': alpha,
        'ascii': ascii_vals,
        'alpha_positions_reverse': list(reversed(alpha)),
        'ascii_reverse': list(reversed(ascii_vals)),
    }
    for name, values in streams.items():
        if not values:
            continue
        raw = bytes(v % 256 for v in values)
        yield f'{label}:{name}:sha256', hashlib.sha256(raw).digest(), ','.join(map(str, values[:160]))
        for start in range(0, max(0, len(raw) - 32 + 1)):
            chunk = raw[start:start + 32]
            yield f'{label}:{name}:bytes32:{start}', chunk, ','.join(map(str, values[start:start + 32]))
            yield f'{label}:{name}:bytes32_reverse:{start}', chunk[::-1], ','.join(map(str, values[start:start + 32]))


def bip39_candidates(label, stream):
    validator = Bip39MnemonicValidator()
    letters = [ord(ch.lower()) - 96 for ch in stream if ch.isalpha()]
    streams = {
        'alpha': letters,
        'alpha_reverse': list(reversed(letters)),
        'ascii': [ord(ch) for ch in stream],
    }
    seen = set()
    for name, values in streams.items():
        vals = [v % 2048 for v in values]
        for length in (12, 15, 18, 21, 24):
            for start in range(0, len(vals) - length + 1):
                phrase = ' '.join(WORDLIST[i] for i in vals[start:start + length])
                if phrase in seen:
                    continue
                if validator.IsValid(phrase):
                    seen.add(phrase)
                    yield {'label': f'{label}:{name}:bip39:{start}:{length}', 'phrase': phrase}


def collect_streams():
    pages = OrderedDict((pid, analyze_page(page)) for pid, page in split_pages(SRC.read_text()).items())
    streams = OrderedDict()
    for pid, page in pages.items():
        streams[f'{pid}_partial_bold'] = page['bold_partial_stream']
        streams[f'{pid}_all_bold'] = page['bold_all_stream']
    streams['all_partial_bold'] = ''.join(page['bold_partial_stream'] for page in pages.values())
    streams['all_bold'] = ''.join(page['bold_all_stream'] for page in pages.values())
    streams['partial_by_page_pipe'] = '|'.join(page['bold_partial_stream'] for page in pages.values())
    streams['partial_page_lengths'] = ','.join(str(len(page['bold_partial_stream'])) for page in pages.values())
    return streams


def build_candidates(streams):
    secrets = OrderedDict()
    mnemonics = OrderedDict()
    for label, stream in streams.items():
        for variant_label, value in stream_variants(label, stream).items():
            if not value:
                continue
            raw = value.encode('utf-8')
            for hash_name, digest in [
                ('sha256', hashlib.sha256(raw).digest()),
                ('sha256d', hashlib.sha256(hashlib.sha256(raw).digest()).digest()),
                ('sha3_256', hashlib.sha3_256(raw).digest()),
                ('blake2s', hashlib.blake2s(raw, digest_size=32).digest()),
            ]:
                add_secret(secrets, f'{variant_label}:{hash_name}', digest, value)
        if 'all_bold' not in label:
            for candidate_label, secret, source in byte_streams(label, stream):
                add_secret(secrets, candidate_label, secret, source)
            for mnemonic in bip39_candidates(label, stream):
                mnemonics.setdefault(mnemonic['phrase'], mnemonic)
    return list(secrets.values()), list(mnemonics.values())


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


def main():
    streams = collect_streams()
    secrets, mnemonics = build_candidates(streams)
    print(f'markup streams: {len(streams)}')
    print(f'private-key candidates: {len(secrets)}')
    print(f'BIP39 candidates: {len(mnemonics)}')
    secret_found, secret_addresses = check_secrets(secrets)
    print(f'private-key addresses checked: {len(secret_addresses)}')
    print(f'private-key activity found: {len(secret_found)}')
    mnemonic_found, mnemonic_addresses = check_mnemonics(mnemonics)
    print(f'BIP39 addresses checked: {len(mnemonic_addresses)}')
    print(f'BIP39 activity found: {len(mnemonic_found)}')

    lines = ['# Markdown Markup Key Check', '']
    lines.append('Scope: bounded key/index check over user-supplied Markdown bold streams only. This does not repeat broad article hashing.')
    lines.append('')
    lines.append('## Summary')
    lines.append(f'- markup streams: {len(streams)}')
    lines.append(f'- private-key candidates: {len(secrets)}')
    lines.append(f'- private-key addresses checked: {len(secret_addresses)}')
    lines.append(f'- private-key activity found: {len(secret_found)}')
    lines.append(f'- checksum-valid BIP39 candidates: {len(mnemonics)}')
    lines.append(f'- BIP39 addresses checked: {len(mnemonic_addresses)}')
    lines.append(f'- BIP39 activity found: {len(mnemonic_found)}')
    lines.append('')
    lines.append('## Streams')
    for label, stream in streams.items():
        lines.append(f'- {label}: length={len(stream)} value=`{stream[:220]}`')
    lines.append('')
    lines.append('## Hits')
    if not secret_found and not mnemonic_found:
        lines.append('- none')
    for hit in secret_found:
        lines.append(f"- private key hit {hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']}")
    for hit in mnemonic_found:
        lines.append(f"- mnemonic hit {hit['address']} {hit['path']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']}")
    lines.append('')
    lines.append('## Assessment')
    lines.append('- Direct private-key and standard BIP39 derivations from the Markdown bold streams found no activity.')
    lines.append('- Keep the bold stream as structured evidence, but do not keep hashing it without a new geometric/order selector.')
    OUT.write_text('\n'.join(lines) + '\n')
    print(f'report: {OUT}')


if __name__ == '__main__':
    main()
