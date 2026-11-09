#!/usr/bin/env python3
import hashlib
import json
import math
import re
import time
from collections import OrderedDict
from pathlib import Path
from urllib.parse import quote

import requests
from bip_utils import Bip39MnemonicValidator, WifDecoder

from highres_reflection_extract import reflected_selection as highres_orange_reflection
from read_manual_inverted_reflections import reflected_selection as inverted_reflection
from search_visual_private_keys import BASE58, key_addresses, valid_secret
from run_second_wave_crypto_experiments import WORDLIST, derive_mnemonic_addresses


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'analysis_outputs' / 'schott_literal_experiments'
OUT_DIR.mkdir(parents=True, exist_ok=True)
MAP_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'article_3d_map_data.json'
MODEL_JSON = ROOT / 'analysis_outputs' / '3d_article_map' / 'canonical_char_model.json'
REPORT_MD = OUT_DIR / 'schott_literal_experiments.md'
REPORT_JSON = OUT_DIR / 'schott_literal_experiments.json'

LEAF_PAIRS = [(75, 76), (76, 75), (77, 78), (78, 77), (79, 80), (80, 79)]
BIP39 = set(WORDLIST)


def clean_words(text):
    return re.sub(r'[^A-Za-z0-9]+', ' ', text).split()


def normalize_word(word):
    return re.sub(r'[^a-z]+', '', word.lower())


def chunks(value, n):
    return ' '.join(value[i:i + n] for i in range(0, len(value), n))


def check_activity(address_map, batch_size=40, sleep_s=0.75):
    found = []
    addresses = sorted(address_map)
    if not addresses:
        return found
    session = requests.Session()
    total_batches = (len(addresses) + batch_size - 1) // batch_size
    for batch_no, start in enumerate(range(0, len(addresses), batch_size), 1):
        batch = addresses[start:start + batch_size]
        active = quote('|'.join(batch), safe='|')
        for attempt in range(10):
            response = session.get(f'https://blockchain.info/multiaddr?active={active}', timeout=30)
            if response.status_code != 429:
                response.raise_for_status()
                break
            wait = min(45, sleep_s * (2 ** attempt))
            print(f'429 at batch {batch_no}/{total_batches}; sleeping {wait:.1f}s', flush=True)
            time.sleep(wait)
        else:
            response.raise_for_status()
        for item in response.json().get('addresses', []):
            received = int(item.get('total_received', 0))
            balance = int(item.get('final_balance', 0))
            if received or balance:
                found.append({**address_map[item['address']], 'address': item['address'], 'total_received': received, 'final_balance': balance})
        if batch_no % 50 == 0:
            print(f'checked {batch_no}/{total_batches} batches', flush=True)
        time.sleep(sleep_s)
    return found


def text_variants(label, text):
    words = clean_words(text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    alnum = ''.join(re.findall(r'[A-Za-z0-9]', text))
    letters = ''.join(re.findall(r'[A-Za-z]', text))
    variants = OrderedDict()
    variants[f'{label}:raw'] = text.strip()
    variants[f'{label}:char_reverse'] = text[::-1].strip()
    variants[f'{label}:word_reverse'] = ' '.join(reversed(words))
    variants[f'{label}:line_reverse'] = ' '.join(reversed(lines))
    variants[f'{label}:letters'] = letters
    variants[f'{label}:letters_reverse'] = letters[::-1]
    variants[f'{label}:alnum'] = alnum
    variants[f'{label}:alnum_reverse'] = alnum[::-1]
    variants[f'{label}:first_letters'] = ''.join(word[0] for word in words if word)
    variants[f'{label}:last_letters'] = ''.join(word[-1] for word in words if word)
    variants[f'{label}:first_letters_reverse'] = ''.join(word[0] for word in reversed(words) if word)
    variants[f'{label}:last_letters_reverse'] = ''.join(word[-1] for word in reversed(words) if word)
    # Literal mirror-writing: reverse word order and reverse each word's letters.
    variants[f'{label}:word_order_and_each_word_reversed'] = ' '.join(word[::-1] for word in reversed(words))
    return OrderedDict((k, v) for k, v in variants.items() if v)


def add_secret(candidates, label, secret, source):
    if valid_secret(secret):
        candidates.setdefault(secret.hex(), {'label': label, 'secret': secret, 'source': source[:260]})


def candidate_secrets_from_streams(streams):
    candidates = OrderedDict()
    for label, text in streams.items():
        for variant_label, value in text_variants(label, text).items():
            raw = value.encode()
            if len(re.sub(r'[^A-Za-z0-9]', '', value)) >= 16:
                for name, digest in [
                    ('sha256', hashlib.sha256(raw).digest()),
                    ('sha256d', hashlib.sha256(hashlib.sha256(raw).digest()).digest()),
                    ('sha3_256', hashlib.sha3_256(raw).digest()),
                    ('blake2s', hashlib.blake2s(raw, digest_size=32).digest()),
                ]:
                    add_secret(candidates, f'{variant_label}:{name}', digest, value)

            compact_b58 = ''.join(ch for ch in value if ch in BASE58)
            for scan_label, scan_value in [('b58', compact_b58), ('b58_reverse', compact_b58[::-1])]:
                for length in range(43, 53):
                    for start in range(0, max(0, len(scan_value) - length + 1)):
                        chunk = scan_value[start:start + length]
                        if length in (51, 52) and chunk and chunk[0] in '5KL':
                            try:
                                add_secret(candidates, f'{variant_label}:{scan_label}:wif:{start}:{length}', WifDecoder.Decode(chunk), chunk)
                            except Exception:
                                pass
    return list(candidates.values())


def address_map_for_secrets(secrets):
    address_map = {}
    for item in secrets:
        for kind, address in key_addresses(item['secret'], item['label'], include_taproot=True):
            address_map[address] = {**item, 'kind': kind}
    return address_map


def hold_to_light_streams():
    streams = OrderedDict()
    details = []
    for source, target in LEAF_PAIRS:
        for kind, fn in [('orange_highres', highres_orange_reflection), ('grey_manual', inverted_reflection)]:
            parts = []
            char_parts = []
            try:
                rows = fn(source, target)
            except Exception as exc:
                details.append({'kind': kind, 'source': source, 'target': target, 'error': str(exc)})
                continue
            for idx, src_box, refl_box, text, chars in rows:
                if text:
                    parts.append(text)
                if chars:
                    char_parts.append(chars)
                details.append({
                    'kind': kind,
                    'source': source,
                    'target': target,
                    'idx': idx,
                    'text': text,
                    'chars': chars,
                    'reflectedBox': list(refl_box),
                })
            if parts:
                streams[f'hold_to_light:{kind}:{source}_onto_{target}:words'] = ' / '.join(parts)
            if char_parts:
                streams[f'hold_to_light:{kind}:{source}_onto_{target}:chars'] = ' / '.join(char_parts)
    return streams, details


def bimanual_streams():
    map_data = json.loads(MAP_JSON.read_text())
    model = json.loads(MODEL_JSON.read_text())
    streams = OrderedDict()

    target_groups = {75: [], 76: [], 78: [], 79: []}
    for reflection in map_data.get('reflections', []):
        target = reflection.get('target')
        if target in target_groups and reflection.get('text'):
            target_groups[target].extend(clean_words(reflection['text']))

    def interleave(a, b):
        out = []
        for i in range(max(len(a), len(b))):
            if i < len(a):
                out.append(a[i])
            if i < len(b):
                out.append(b[i])
        return ' '.join(out)

    left = target_groups[76] + target_groups[75]
    right = target_groups[78] + target_groups[79]
    streams['bimanual:reflected_targets:left76_75_right78_79'] = interleave(left, right)
    streams['bimanual:reflected_targets:center_out_right_reversed'] = interleave(left, list(reversed(right)))
    streams['bimanual:reflected_targets:left_reversed_right'] = interleave(list(reversed(left)), right)

    pages = model['pages']
    for a, b in [('p2', 'p4'), ('p1', 'p5')]:
        sa = pages[a]['streams']['partialBoldLetters']
        sb = pages[b]['streams']['partialBoldLetters']
        streams[f'bimanual:partial_bold:{a}_{b}:normal'] = ''.join(x + y for x, y in zip(sa, sb)) + (sa[len(sb):] if len(sa) > len(sb) else sb[len(sa):])
        sbr = sb[::-1]
        streams[f'bimanual:partial_bold:{a}_{b}:right_reversed'] = ''.join(x + y for x, y in zip(sa, sbr)) + (sa[len(sbr):] if len(sa) > len(sbr) else sbr[len(sa):])
    return streams


def visual_diff_streams():
    map_data = json.loads(MAP_JSON.read_text())
    streams = OrderedDict()
    rows = []
    for selection in map_data.get('raySelections', [])[:40]:
        words = clean_words(selection.get('text', ''))
        if len(words) < 2:
            continue
        letters = [word[0].lower() for word in words if word and word[0].isalpha()]
        deltas = []
        chars = []
        for a, b in zip(letters, letters[1:]):
            da = ord(a) - 96
            db = ord(b) - 96
            diff = (db - da) % 26
            if diff == 0:
                diff = 26
            deltas.append(diff)
            chars.append(chr(diff + 96))
        stream = ''.join(chars)
        label = f"visual_diff:ray{selection.get('rank')}:{selection.get('a')}->{selection.get('b')}:{selection.get('mode')}:{selection.get('threshold')}:{selection.get('order')}"
        streams[label] = stream
        rows.append({'label': label, 'text': selection.get('text', ''), 'firstLetters': ''.join(letters), 'deltaLetters': stream, 'deltas': deltas})
    joined = ''.join(row['deltaLetters'] for row in rows)
    if joined:
        streams['visual_diff:all_top_ray_delta_letters'] = joined
    return streams, rows


def strict_bip39_ray():
    validator = Bip39MnemonicValidator()
    map_data = json.loads(MAP_JSON.read_text())
    rows = []
    mnemonic_candidates = OrderedDict()
    for selection in map_data.get('raySelections', []):
        words = clean_words(selection.get('text', ''))
        bip_words = [normalize_word(word) for word in words]
        bip_words = [word for word in bip_words if word in BIP39]
        row = {
            'rank': selection.get('rank'),
            'selector': f"{selection.get('a')}->{selection.get('b')}:{selection.get('mode')}:{selection.get('threshold')}:{selection.get('order')}",
            'text': selection.get('text', ''),
            'bip39Words': bip_words,
            'count': len(bip_words),
        }
        for order_name, ordered in [('forward', bip_words), ('reverse', list(reversed(bip_words)))]:
            for length in (12, 15, 18, 21, 24):
                if len(ordered) == length:
                    phrase = ' '.join(ordered)
                    if validator.IsValid(phrase):
                        mnemonic_candidates.setdefault(phrase, {'label': f"ray{selection.get('rank')}:{order_name}:{length}", 'phrase': phrase})
                for start in range(0, max(0, len(ordered) - length + 1)):
                    phrase = ' '.join(ordered[start:start + length])
                    if validator.IsValid(phrase):
                        mnemonic_candidates.setdefault(phrase, {'label': f"ray{selection.get('rank')}:{order_name}:window{start}:{length}", 'phrase': phrase})
        rows.append(row)
    return rows, list(mnemonic_candidates.values())


def check_mnemonics(mnemonics):
    address_map = {}
    for mnemonic in mnemonics:
        for path, address in derive_mnemonic_addresses(mnemonic['phrase']):
            address_map[address] = {**mnemonic, 'path': path}
    found = check_activity(address_map, batch_size=40, sleep_s=0.25) if address_map else []
    return address_map, found


def main():
    streams = OrderedDict()
    hold_streams, hold_details = hold_to_light_streams()
    streams.update(hold_streams)
    streams.update(bimanual_streams())
    diff_streams, diff_rows = visual_diff_streams()
    streams.update(diff_streams)

    secrets = candidate_secrets_from_streams(streams)
    address_map = address_map_for_secrets(secrets)
    found = check_activity(address_map, batch_size=40, sleep_s=0.75)

    bip_rows, mnemonics = strict_bip39_ray()
    mnemonic_addresses, mnemonic_found = check_mnemonics(mnemonics)

    result = {
        'streamCount': len(streams),
        'secretCandidateCount': len(secrets),
        'addressCount': len(address_map),
        'activityFound': found,
        'holdToLightDetails': hold_details,
        'streams': streams,
        'visualDiffRows': diff_rows,
        'strictBip39RayRows': bip_rows,
        'strictBip39MnemonicCount': len(mnemonics),
        'strictBip39AddressCount': len(mnemonic_addresses),
        'strictBip39ActivityFound': mnemonic_found,
    }
    REPORT_JSON.write_text(json.dumps(result, indent=2, default=str))

    lines = ['# Schott Literal Experiments', '']
    lines.append('Scope: test five literal interpretations of the Schott mirror-writing clue: hold-to-light leaf pairs, character/word reversal, bimanual interleaving, visual letter-diff streams, and strict BIP39 ray interception.')
    lines.append('')
    lines.append('## Chain Summary')
    lines.append(f"- experiment streams checked: {len(streams)}")
    lines.append(f"- private-key candidates from stream hashes/reversals/backward Base58 windows: {len(secrets)}")
    lines.append(f"- private-key addresses checked: {len(address_map)}")
    lines.append(f"- private-key activity found: {len(found)}")
    lines.append(f"- strict BIP39 ray mnemonic candidates: {len(mnemonics)}")
    lines.append(f"- strict BIP39 ray addresses checked: {len(mnemonic_addresses)}")
    lines.append(f"- strict BIP39 activity found: {len(mnemonic_found)}")
    lines.append('')
    lines.append('## Hold-To-Light Leaf Pairs')
    for label, text in hold_streams.items():
        lines.append(f"- {label}: `{text[:300]}`")
    lines.append('')
    lines.append('## Bimanual Interleaves')
    for label, text in bimanual_streams().items():
        compact = re.sub(r'\\s+', ' ', text)
        lines.append(f"- {label}: len={len(compact)} `{compact[:260]}`")
    lines.append('')
    lines.append('## Visual Diff / Letter Delta')
    for row in diff_rows[:20]:
        lines.append(f"- {row['label']}: firstLetters=`{row['firstLetters']}` deltas=`{row['deltaLetters']}` source=`{row['text']}`")
    lines.append(f"- all top-ray delta letters len={len(diff_streams.get('visual_diff:all_top_ray_delta_letters', ''))}: `{chunks(diff_streams.get('visual_diff:all_top_ray_delta_letters', ''), 5)[:500]}`")
    lines.append('')
    lines.append('## Strict BIP39 Ray Interception')
    for row in bip_rows[:40]:
        if row['bip39Words']:
            lines.append(f"- rank {row['rank']} {row['selector']}: count={row['count']} words=`{' '.join(row['bip39Words'])}`")
    if not any(row['bip39Words'] for row in bip_rows):
        lines.append('- no ray selection contained BIP39-valid words')
    lines.append('')
    lines.append('## Hits')
    if not found and not mnemonic_found:
        lines.append('- none')
    for hit in found:
        lines.append(f"- private-key hit {hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']}")
    for hit in mnemonic_found:
        lines.append(f"- mnemonic hit {hit['address']} {hit['path']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']}")
    lines.append('')
    lines.append('## Assessment')
    lines.append('- Literal front/back leaf mirroring produced additional contextual text, but no direct private-key activity under reversed strings, reversed words, or backward Base58/WIF windows.')
    lines.append('- Bimanual interleaving of reflected text pulls and corrected partial-bold page pairs did not produce readable instruction text or active key material.')
    lines.append('- Letter-delta streams from anchor-ray selections produced compact sequences but no key activity; they should not be promoted without a better registration rule.')
    lines.append('- Strict BIP39 ray filtering found BIP39-valid words inside ray-selected prose, but no complete checksum-valid 12/24-word mnemonic sequence.')
    REPORT_MD.write_text('\n'.join(lines) + '\n')
    print(f'wrote {REPORT_JSON}')
    print(f'wrote {REPORT_MD}')


if __name__ == '__main__':
    main()
