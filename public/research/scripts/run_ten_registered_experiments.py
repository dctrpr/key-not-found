#!/usr/bin/env python3
import hashlib
import re
from collections import OrderedDict
from pathlib import Path

from highres_reflection_extract import orange_boxes, reflected_selection as highres_reflected_selection
from search_visual_private_keys import check_activity, key_addresses


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis_outputs' / 'ten_experiments'
OUT.mkdir(parents=True, exist_ok=True)

ARTICLE = ROOT / 'full_article_corrected.txt'
SECP256K1_N = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141', 16)

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

MEDIA_DIMS = [
    (828, 967),
    (828, 1270),
    (272, 271),
    (300, 168),
    (828, 366),
    (314, 174),
    (474, 309),
]

TCO_CODES = [
    'eiSeo82gxP',
    'lyoKtd3HfK',
    'KytK2wRQcM',
    'DQes0bXQZQ',
    'Xrnsix4Dwz',
    'XJn6zYNAUx',
]

BASE58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def normalize(text):
    return re.sub(r'\s+', ' ', text.strip())


def words(text):
    return re.findall(r"[A-Za-z0-9']+", text)


def article_lines():
    return ARTICLE.read_text().splitlines()


def page76_focus():
    lines = article_lines()
    # 1-based article lines 55-62 contain the strongest recovered-media overlap.
    return normalize(' '.join(lines[54:62]))


def page76_context():
    lines = article_lines()
    # Wider local page-76 context around Bukele/IMF/volcano/Strike.
    return normalize(' '.join(lines[35:75]))


def select_by_indices(text, indices, one_based=True):
    ws = words(text)
    if not ws:
        return ''
    out = []
    for idx in indices:
        pos = idx - 1 if one_based else idx
        if pos < 0:
            continue
        out.append(ws[pos % len(ws)])
    return ' '.join(out)


def letters_by_indices(text, indices, one_based=True):
    chars = re.sub(r'[^A-Za-z0-9]', '', text)
    if not chars:
        return ''
    out = []
    for idx in indices:
        pos = idx - 1 if one_based else idx
        if pos < 0:
            continue
        out.append(chars[pos % len(chars)])
    return ''.join(out)


def chunks_of_digits(value, width):
    return [int(value[i:i + width]) for i in range(0, len(value) - width + 1, width)]


def base58_numbers(value):
    return [BASE58.index(ch) + 1 for ch in value if ch in BASE58]


def text_features(label, text):
    ws = words(text)
    if not ws:
        return []
    return [
        (f'{label}:text', normalize(text)),
        (f'{label}:first_letters', ''.join(w[0] for w in ws)),
        (f'{label}:last_letters', ''.join(w[-1] for w in ws)),
        (f'{label}:word_lengths', ''.join(str(len(w)) for w in ws)),
        (f'{label}:alpha_positions_first', ''.join(f'{ord(w[0].lower()) - 96:02d}' for w in ws if w[0].isalpha())),
    ]


def experiments():
    focus = page76_focus()
    context = page76_context()

    out = OrderedDict()

    out['E01_page76_focus_text_features'] = text_features('page76_focus', focus)

    out['E02_page76_context_text_features'] = text_features('page76_context', context)

    idx_20btc = [20, 2, 20, 2008, 2011, 2017, 51, 95, 42, 20000, 100000, 12000]
    out['E03_numbers_from_article_as_indices'] = [
        ('numbers_words_focus', select_by_indices(focus, idx_20btc)),
        ('numbers_letters_focus', letters_by_indices(focus, idx_20btc)),
        ('numbers_words_context', select_by_indices(context, idx_20btc)),
        ('numbers_letters_context', letters_by_indices(context, idx_20btc)),
    ]

    dims = [n for pair in MEDIA_DIMS for n in pair]
    out['E04_thread_media_dimensions_as_indices'] = [
        ('media_dims_words_focus', select_by_indices(focus, dims)),
        ('media_dims_letters_focus', letters_by_indices(focus, dims)),
        ('media_dims_words_context', select_by_indices(context, dims)),
        ('media_dims_letters_context', letters_by_indices(context, dims)),
    ]

    tweet_chunks = []
    for tid in TWEET_IDS:
        tweet_chunks.extend(chunks_of_digits(tid, 2))
        tweet_chunks.extend(chunks_of_digits(tid, 3))
    out['E05_tweet_id_digit_chunks_as_indices'] = [
        ('tweet_chunks_words_focus', select_by_indices(focus, tweet_chunks[:80])),
        ('tweet_chunks_letters_focus', letters_by_indices(focus, tweet_chunks[:160])),
        ('tweet_ids_joined', ''.join(TWEET_IDS)),
        ('tweet_ids_spaced', ' '.join(TWEET_IDS)),
    ]

    media_nums = []
    for mid in MEDIA_IDS:
        media_nums.extend(base58_numbers(mid))
    out['E06_media_id_base58_positions'] = [
        ('media_base58_words_focus', select_by_indices(focus, media_nums)),
        ('media_base58_letters_focus', letters_by_indices(focus, media_nums)),
        ('media_ids_joined', ''.join(MEDIA_IDS)),
        ('media_ids_spaced', ' '.join(MEDIA_IDS)),
    ]

    tco_nums = []
    for code in TCO_CODES:
        tco_nums.extend(base58_numbers(code))
    out['E07_tco_shortcode_positions'] = [
        ('tco_base58_words_focus', select_by_indices(focus, tco_nums)),
        ('tco_base58_letters_focus', letters_by_indices(focus, tco_nums)),
        ('tco_codes_joined', ''.join(TCO_CODES)),
        ('tco_codes_spaced', ' '.join(TCO_CODES)),
    ]

    reflected_79_76 = normalize(' '.join(text for _, _, _, text, _ in highres_reflected_selection(79, 76) if text))
    out['E08_reflected_79_to_76_features'] = text_features('reflected_79_to_76', reflected_79_76)

    p79_boxes, _ = orange_boxes(79)
    p79_nums = []
    for box in p79_boxes:
        x1, y1, x2, y2 = box
        p79_nums.extend([x1, y1, x2, y2, (x1 + x2) // 2, (y1 + y2) // 2, x2 - x1, y2 - y1])
    out['E09_page79_orange_geometry_indices'] = [
        ('p79_geometry_words_focus', select_by_indices(focus, p79_nums)),
        ('p79_geometry_letters_focus', letters_by_indices(focus, p79_nums)),
        ('p79_geometry_words_context', select_by_indices(context, p79_nums)),
        ('p79_geometry_letters_context', letters_by_indices(context, p79_nums)),
    ]

    order_labels = [
        'max bukele',
        'max bukele stacy',
        'max bukele magazine',
        'max stacy car',
        'stacy lava el salvador',
        'bitcoin volcano',
    ]
    order_text = ' '.join(order_labels)
    out['E10_thread_image_order_labels'] = [
        ('order_labels_text', order_text),
        ('order_labels_first_letters', ''.join(w[0] for w in words(order_text))),
        ('order_labels_last_letters', ''.join(w[-1] for w in words(order_text))),
        ('order_labels_lengths', ''.join(str(len(w)) for w in words(order_text))),
    ]

    return out


def variants(label, text):
    text = normalize(text)
    if not text:
        return []
    values = {
        label: text,
        f'{label}:lower': text.lower(),
        f'{label}:nospace': re.sub(r'[^A-Za-z0-9]', '', text),
        f'{label}:reverse': text[::-1],
    }
    return [(k, v) for k, v in values.items() if v]


def candidate_secrets(exps):
    seen = set()
    for exp_id, items in exps.items():
        for label, text in items:
            for vlabel, value in variants(f'{exp_id}:{label}', text):
                for hash_name, digest in [
                    ('sha256', hashlib.sha256(value.encode()).digest()),
                    ('sha256d', hashlib.sha256(hashlib.sha256(value.encode()).digest()).digest()),
                    ('sha3_256', hashlib.sha3_256(value.encode()).digest()),
                    ('blake2s', hashlib.blake2s(value.encode()).digest()),
                ]:
                    key = (vlabel, hash_name, digest)
                    if key in seen:
                        continue
                    seen.add(key)
                    yield {
                        'experiment': exp_id,
                        'label': f'{vlabel}:{hash_name}',
                        'secret': digest,
                        'source': value,
                    }


def write_report(exps, found=None):
    found = found or []
    lines = ['# Ten Registered Experiments', '']
    lines.append('Scope: ten narrow derivation experiments tied to page 76, recovered thread media, mirror geometry, and known numeric clues.')
    lines.append('')
    for exp_id, items in exps.items():
        lines.append(f'## {exp_id}')
        lines.append(f'- generated strings: {len(items)}')
        for label, text in items[:12]:
            clipped = text if len(text) <= 240 else text[:237] + '...'
            lines.append(f'- `{label}`: {clipped}')
        lines.append('')
    lines.append('## Chain Check')
    lines.append(f'- activity found: {len(found)}')
    for hit in found:
        lines.append(f"- {hit['address']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']}")
    (OUT / 'ten_registered_experiments.md').write_text('\n'.join(lines) + '\n')


def main():
    exps = experiments()
    candidates = list(candidate_secrets(exps))
    address_map = {}
    for info in candidates:
        for kind, address in key_addresses(info['secret'], info['label'], include_taproot=True):
            address_map[address] = {**info, 'kind': kind}

    print(f'experiments: {len(exps)}')
    print(f'candidate strings: {sum(len(v) for v in exps.values())}')
    print(f'candidate secrets: {len(candidates)}')
    print(f'addresses to check: {len(address_map)}')
    found = check_activity(address_map, batch_size=25, sleep_s=0.5)
    print(f'activity found: {len(found)}')
    for hit in found:
        print(f"{hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']} {hit['label']}")
    write_report(exps, found)


if __name__ == '__main__':
    main()
