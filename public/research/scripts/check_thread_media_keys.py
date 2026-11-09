#!/usr/bin/env python3
import hashlib
import re

from search_visual_private_keys import check_activity, key_addresses


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

PAGE_76_FOCUS = [
    'Have you seen the president of El Salvador',
    'trolling the International Monetary Fund IMF on Twitter',
    'buying the dip',
    'President Nayib Bukele',
    'tap his nations volcanoes to mine',
    'Volcano Bonds',
    'pay off the IMF',
    'Nayib Bukele volcano bonds buying the dip IMF',
    'El Salvador IMF buying the dip volcano bonds',
]


def normalize(value):
    return re.sub(r'\s+', ' ', value).strip()


def base_strings():
    yield 'tweet_ids_joined', ''.join(TWEET_IDS)
    yield 'tweet_ids_spaced', ' '.join(TWEET_IDS)
    yield 'tweet_ids_dashed', '-'.join(TWEET_IDS)
    yield 'media_ids_joined', ''.join(MEDIA_IDS)
    yield 'media_ids_spaced', ' '.join(MEDIA_IDS)
    yield 'tco_codes_joined', ''.join(TCO_CODES)
    yield 'tco_codes_spaced', ' '.join(TCO_CODES)
    yield 'thread_order_labels', 'Bukele Stacy Bukele car lava volcano'
    yield 'thread_order_labels_full', 'Max Bukele Stacy Max Bukele Max Stacy lava Bitcoin volcano'
    for idx, phrase in enumerate(PAGE_76_FOCUS, 1):
        yield f'page76_focus_{idx}', phrase
    yield 'page76_focus_joined', ' '.join(PAGE_76_FOCUS)


def variants(label, text):
    text = normalize(text)
    values = {
        label: text,
        f'{label}:lower': text.lower(),
        f'{label}:nospace': re.sub(r'[^A-Za-z0-9]', '', text),
        f'{label}:reverse': text[::-1],
    }
    for k, v in values.items():
        if v:
            yield k, v


def candidate_secrets():
    seen = set()
    for label, text in base_strings():
        for vlabel, value in variants(label, text):
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
                yield {'label': f'{vlabel}:{hash_name}', 'secret': digest, 'source': value}


def main():
    address_map = {}
    count = 0
    for info in candidate_secrets():
        count += 1
        for kind, address in key_addresses(info['secret'], info['label'], include_taproot=True):
            address_map[address] = {**info, 'kind': kind}
    print(f'thread/media candidate secrets: {count}')
    print(f'addresses to check: {len(address_map)}')
    found = check_activity(address_map, batch_size=25, sleep_s=0.5)
    print(f'activity found: {len(found)}')
    for hit in found:
        print(f"{hit['address']} {hit['kind']} received={hit['total_received']} balance={hit['final_balance']} label={hit['label']} source={hit['source']}")


if __name__ == '__main__':
    main()
