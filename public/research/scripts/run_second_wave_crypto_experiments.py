#!/usr/bin/env python3
import hashlib
import itertools
import re
import argparse
from collections import OrderedDict
from pathlib import Path

from bip_utils import (
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Changes,
    Bip44Coins,
    Bip49,
    Bip49Coins,
    Bip84,
    Bip84Coins,
    WifDecoder,
)
from mnemonic import Mnemonic

from highres_reflection_extract import orange_boxes, reflected_selection as highres_reflected_selection
from read_manual_inverted_reflections import reflected_selection as inverted_reflected_selection
from search_structured_candidates import HIGHLIGHT_GROUPS
from search_visual_private_keys import BASE58, b58decode, check_activity, key_addresses, valid_secret


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / 'second_wave'
OUT.mkdir(parents=True, exist_ok=True)

ARTICLE = ROOT / 'full_article_corrected.txt'
SECP256K1_N = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141', 16)
WORDLIST = Mnemonic('english').wordlist
WORDSET = set(WORDLIST)

TWEET_IDS = [
    '1632068898169450497',
    '1632069025391075328',
    '1632134737639907328',
    '1632159731325497346',
    '1632223164435496960',
    '1632272898164416512',
]

MEDIA_IDS = [
    'FqZGAb7aYAEdnKL',
    'FqZGH-oaAAcL8y5',
    'FqZGH-takAInkt4',
    'FqaB47TagAEbd2r',
    'FqaYnkpaMAEuMC5',
    'FqbSUHHWcAM05op',
    'Fqb_i__WYAE33V5',
]

TCO_CODES = [
    'eiSeo82gxP',
    'lyoKtd3HfK',
    'KytK2wRQcM',
    'DQes0bXQZQ',
    'Xrnsix4Dwz',
    'XJn6zYNAUx',
]


def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())


def words(text):
    return re.findall(r"[A-Za-z0-9']+", text)


def compact_alnum(text):
    return ''.join(re.findall(r'[A-Za-z0-9]', text))


def article_text():
    return ARTICLE.read_text()


def article_lines():
    return ARTICLE.read_text().splitlines()


def page76_focus():
    return clean_text(' '.join(article_lines()[54:62]))


def page76_context():
    return clean_text(' '.join(article_lines()[35:75]))


def reflected_text(source, target):
    return clean_text(' '.join(text for _, _, _, text, _ in highres_reflected_selection(source, target) if text))


def inverted_text(source, target):
    return clean_text(' '.join(text for _, _, _, text, _ in inverted_reflected_selection(source, target) if text))


def high_signal_strings():
    values = OrderedDict()
    values['article'] = article_text()
    values['page76_focus'] = page76_focus()
    values['page76_context'] = page76_context()
    values['orange_highlights'] = ' '.join(HIGHLIGHT_GROUPS['orange'])
    values['inverted_highlights'] = ' '.join(HIGHLIGHT_GROUPS['inverted'])
    values['reflected_79_75'] = reflected_text(79, 75)
    values['reflected_78_76'] = reflected_text(78, 76)
    values['reflected_76_78'] = reflected_text(76, 78)
    values['reflected_79_76'] = reflected_text(79, 76)
    values['inverted_76_78'] = inverted_text(76, 78)
    values['tweet_ids'] = ' '.join(TWEET_IDS)
    values['media_ids'] = ' '.join(MEDIA_IDS)
    values['tco_codes'] = ' '.join(TCO_CODES)
    return values


def text_variants(label, text):
    ws = words(text)
    variants = OrderedDict()
    variants[label] = clean_text(text)
    variants[f'{label}:lower'] = clean_text(text.lower())
    variants[f'{label}:alnum'] = compact_alnum(text)
    variants[f'{label}:alnum_lower'] = compact_alnum(text).lower()
    variants[f'{label}:letters'] = ''.join(re.findall(r'[A-Za-z]', text))
    variants[f'{label}:first_letters'] = ''.join(w[0] for w in ws if w)
    variants[f'{label}:last_letters'] = ''.join(w[-1] for w in ws if w)
    variants[f'{label}:firstlast'] = ''.join(w[0] + w[-1] for w in ws if w)
    for key, value in list(variants.items()):
        variants[f'{key}:reverse'] = value[::-1]
    return variants


def add_hash_candidates(out, experiment, label, value):
    if len(compact_alnum(value)) < 16:
        return
    raw = value.encode()
    for name, secret in [
        ('sha256', hashlib.sha256(raw).digest()),
        ('sha256d', hashlib.sha256(hashlib.sha256(raw).digest()).digest()),
        ('sha3_256', hashlib.sha3_256(raw).digest()),
        ('blake2s', hashlib.blake2s(raw).digest()),
    ]:
        add_secret(out, experiment, f'{label}:{name}', secret, value[:240])


def add_secret(out, experiment, label, secret, source):
    if valid_secret(secret):
        out.setdefault(secret.hex(), {'experiment': experiment, 'label': label, 'secret': secret, 'source': source})


def scan_wif_and_base58(out, experiment, label, value):
    compact = ''.join(ch for ch in value if ch in BASE58)
    for length in range(22, 53):
        for start in range(0, len(compact) - length + 1):
            chunk = compact[start:start + length]
            if length in (51, 52) and chunk[0] in '5KL':
                try:
                    add_secret(out, experiment, f'{label}:wif:{start}:{length}', WifDecoder.Decode(chunk), chunk)
                except Exception:
                    pass
            if 43 <= length <= 52:
                try:
                    raw = b58decode(chunk)
                except Exception:
                    continue
                if len(raw) == 32:
                    add_secret(out, experiment, f'{label}:base58raw:{start}:{length}', raw, chunk)
                if len(raw) == 33 and raw[0] == 0:
                    add_secret(out, experiment, f'{label}:base58raw0:{start}:{length}', raw[1:], chunk)


def scan_minikey(out, experiment, label, value):
    compact = ''.join(ch for ch in value if ch in BASE58)
    for length in (22, 26, 30):
        for start in range(0, len(compact) - length + 1):
            chunk = compact[start:start + length]
            if not chunk.startswith('S'):
                continue
            if hashlib.sha256((chunk + '?').encode()).digest()[0] == 0:
                add_secret(out, experiment, f'{label}:minikey:{start}:{length}', hashlib.sha256(chunk.encode()).digest(), chunk)


def scan_hex64(out, experiment, label, value):
    for source_label, hex_source in [
        ('strict', ' '.join(re.findall(r'(?<![0-9a-fA-F])([0-9a-fA-F]{64})(?![0-9a-fA-F])', value))),
        ('loose', ''.join(re.findall(r'[0-9a-fA-F]', value))),
    ]:
        for start in range(0, max(0, len(hex_source) - 64 + 1)):
            chunk = hex_source[start:start + 64]
            if len(chunk) == 64 and re.fullmatch(r'[0-9a-fA-F]{64}', chunk):
                secret = bytes.fromhex(chunk)
                add_secret(out, experiment, f'{label}:hex64:{source_label}:{start}', secret, chunk)
                add_secret(out, experiment, f'{label}:hex64_rev:{source_label}:{start}', secret[::-1], chunk)


def byte_windows(out, experiment, label, values, source):
    if not values:
        return
    streams = OrderedDict()
    streams['raw_mod256'] = [v % 256 for v in values]
    streams['lowbyte'] = [v & 255 for v in values]
    streams['highbyte'] = [(v >> 8) & 255 for v in values]
    max_v = max(abs(v) for v in values) or 1
    streams['scaled255'] = [round(abs(v) / max_v * 255) for v in values]
    for stream_name, stream in streams.items():
        data = bytes(stream)
        add_secret(out, experiment, f'{label}:{stream_name}:sha256', hashlib.sha256(data).digest(), source)
        for start in range(0, max(0, len(data) - 32 + 1)):
            chunk = data[start:start + 32]
            add_secret(out, experiment, f'{label}:{stream_name}:bytes32:{start}', chunk, source)
            add_secret(out, experiment, f'{label}:{stream_name}:bytes32_rev:{start}', chunk[::-1], source)


def geometry_values():
    values = []
    for page in [75, 76, 77, 78, 79, 80]:
        boxes, size = orange_boxes(page)
        values.extend([page, *size, len(boxes)])
        for idx, (x1, y1, x2, y2) in enumerate(boxes, 1):
            values.extend([idx, x1, y1, x2, y2, x2 - x1, y2 - y1, (x1 + x2) // 2, (y1 + y2) // 2])
    return values


def reflected_geometry_values():
    values = []
    for source, target in [(79, 75), (78, 76), (76, 78), (79, 76)]:
        for idx, src, refl, text, chars in highres_reflected_selection(source, target):
            values.extend([source, target, idx, *src, *refl, len(words(text)), len(text), len(chars)])
    return values


def bip39_from_indices(out, experiment, label, indices):
    vals = [abs(v) % 2048 for v in indices]
    validator = Bip39MnemonicValidator()
    for length in (12, 15, 18, 21, 24):
        for start in range(0, len(vals) - length + 1):
            phrase = ' '.join(WORDLIST[i] for i in vals[start:start + length])
            if validator.IsValid(phrase):
                out.append({'experiment': experiment, 'label': f'{label}:bip39:{start}:{length}', 'phrase': phrase})


def derive_mnemonic_addresses(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate('')
    contexts = [
        ('m/44h/0h/0h/0/0', Bip44.FromSeed(seed, Bip44Coins.BITCOIN)),
        ('m/49h/0h/0h/0/0', Bip49.FromSeed(seed, Bip49Coins.BITCOIN)),
        ('m/84h/0h/0h/0/0', Bip84.FromSeed(seed, Bip84Coins.BITCOIN)),
    ]
    for path, ctx in contexts:
        address = ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0).PublicKey().ToAddress()
        yield path, address


def run_experiments():
    secrets = OrderedDict()
    mnemonics = []
    strings = high_signal_strings()

    for label, text in strings.items():
        for vlabel, value in text_variants(label, text).items():
            if len(value) > 20000:
                value = value[:10000] + value[-10000:]
            scan_wif_and_base58(secrets, 'E11_wif_base58_direct_scan', vlabel, value)
            scan_minikey(secrets, 'E12_minikey_scan', vlabel, value)
            scan_hex64(secrets, 'E13_hex64_direct_scan', vlabel, value)

    byte_windows(secrets, 'E14_orange_geometry_byte_streams', 'orange_geometry', geometry_values(), 'all highres orange boxes')
    byte_windows(secrets, 'E15_reflected_geometry_byte_streams', 'reflected_geometry', reflected_geometry_values(), 'highres reflected boxes/text lengths')

    bip39_from_indices(mnemonics, 'E16_geometry_bip39_indices', 'orange_geometry', geometry_values())
    bip39_from_indices(mnemonics, 'E17_reflected_geometry_bip39_indices', 'reflected_geometry', reflected_geometry_values())

    id_values = []
    for value in TWEET_IDS + MEDIA_IDS + TCO_CODES:
        id_values.extend(BASE58.index(ch) + 1 for ch in value if ch in BASE58)
        id_values.extend(int(ch) for ch in value if ch.isdigit())
    byte_windows(secrets, 'E18_id_shortcode_byte_streams', 'ids_and_shortcodes', id_values, 'tweet/media/tco id streams')
    bip39_from_indices(mnemonics, 'E19_id_shortcode_bip39_indices', 'ids_and_shortcodes', id_values)

    salts = [
        '20 BTC',
        'Max Keiser',
        'Bitcoin Magazine',
        'Mirror writing',
        'El Salvador',
        'Nayib Bukele',
        'Volcano Bonds',
        'buying the dip',
    ]
    priority = [
        strings['page76_focus'],
        strings['reflected_79_76'],
        strings['reflected_79_75'],
        strings['orange_highlights'],
        strings['inverted_highlights'],
    ]
    for salt, text in itertools.product(salts, priority):
        for sep in ['', ' ', ':', '|']:
            value = f'{salt}{sep}{text}'
            add_hash_candidates(secrets, 'E20_salted_priority_hashes', f'{salt}{sep}priority', value)

    return secrets, mnemonics


def check_mnemonics(mnemonics):
    address_map = {}
    for hit in mnemonics:
        for path, address in derive_mnemonic_addresses(hit['phrase']):
            address_map[address] = {**hit, 'path': path, 'address': address}
    if not address_map:
        return [], 0
    found = check_activity(address_map, batch_size=25, sleep_s=0.5)
    return found, len(address_map)


def write_report(secrets, found, mnemonics, mnemonic_found, mnemonic_address_count):
    by_exp = OrderedDict()
    for info in secrets.values():
        by_exp.setdefault(info['experiment'], 0)
        by_exp[info['experiment']] += 1
    mn_by_exp = OrderedDict()
    for info in mnemonics:
        mn_by_exp.setdefault(info['experiment'], 0)
        mn_by_exp[info['experiment']] += 1

    lines = ['# Second-Wave Crypto Experiments', '']
    lines.append('Scope: checksum-valid/direct encoding and structured byte/index tests, not broad phrase hashing.')
    lines.append('')
    lines.append('## Secret Candidate Counts')
    for exp, count in by_exp.items():
        lines.append(f'- {exp}: {count}')
    lines.append('')
    lines.append('## BIP39 Candidate Counts')
    for exp, count in mn_by_exp.items():
        lines.append(f'- {exp}: {count}')
    if not mn_by_exp:
        lines.append('- none')
    lines.append('')
    lines.append('## Chain Results')
    lines.append(f'- private-key candidates generated: {len(secrets)}')
    lines.append(f'- private-key activity found: {len(found)}')
    lines.append(f'- BIP39 candidates: {len(mnemonics)}')
    lines.append(f'- BIP39 addresses checked: {mnemonic_address_count}')
    lines.append(f'- BIP39 activity found: {len(mnemonic_found)}')
    for hit in found:
        lines.append(f"- private-key hit: {hit['address']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']}")
    for hit in mnemonic_found:
        lines.append(f"- mnemonic hit: {hit['address']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']}")
    lines.append('')
    lines.append('## Sample Secret Candidates')
    for info in list(secrets.values())[:80]:
        src = str(info['source'])
        if len(src) > 120:
            src = src[:117] + '...'
        lines.append(f"- {info['experiment']} `{info['label']}` source={src}")
    if mnemonics:
        lines.append('')
        lines.append('## BIP39 Candidates')
        for info in mnemonics[:80]:
            lines.append(f"- {info['experiment']} `{info['label']}` {info['phrase']}")
    (OUT / 'second_wave_crypto_experiments.md').write_text('\n'.join(lines) + '\n')


def priority_secret(info):
    label = info['label']
    experiment = info['experiment']
    if ':wif:' in label or ':minikey:' in label:
        return True
    if ':hex64:strict:' in label:
        return True
    if experiment == 'E20_salted_priority_hashes':
        return True
    if label.endswith(':sha256') and experiment in {
        'E14_orange_geometry_byte_streams',
        'E15_reflected_geometry_byte_streams',
        'E18_id_shortcode_byte_streams',
    }:
        return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-chain', action='store_true')
    parser.add_argument('--all-candidates', action='store_true', help='chain-check every generated candidate; normally too broad')
    parser.add_argument('--max-addresses', type=int, default=5000)
    args = parser.parse_args()

    secrets, mnemonics = run_experiments()
    chain_secrets = secrets
    if args.check_chain and not args.all_candidates:
        chain_secrets = OrderedDict((key, info) for key, info in secrets.items() if priority_secret(info))

    address_map = {}
    for info in chain_secrets.values():
        for kind, address in key_addresses(info['secret'], info['label'], include_taproot=True):
            address_map[address] = {**info, 'kind': kind}
    print(f'secret candidates: {len(secrets)}')
    print(f'priority secret candidates: {len(chain_secrets)}')
    print(f'private-key addresses selected: {len(address_map)}')
    if args.check_chain and len(address_map) > args.max_addresses:
        raise SystemExit(f'refusing to check {len(address_map)} addresses; raise --max-addresses or narrow candidates')
    found = check_activity(address_map, batch_size=25, sleep_s=0.5) if args.check_chain and address_map else []
    print(f'private-key activity found: {len(found)}')
    print(f'BIP39 candidates: {len(mnemonics)}')
    mnemonic_found, mnemonic_address_count = check_mnemonics(mnemonics) if args.check_chain else ([], 0)
    print(f'BIP39 addresses checked: {mnemonic_address_count}')
    print(f'BIP39 activity found: {len(mnemonic_found)}')
    write_report(secrets, found, mnemonics, mnemonic_found, mnemonic_address_count)


if __name__ == '__main__':
    main()
