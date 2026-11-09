#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import quote

import requests
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
)
from mnemonic import Mnemonic


ROOT = Path(__file__).resolve().parents[1]
TEXT_FILE = ROOT / 'full_article_corrected.txt'

VALID_LENGTHS = (12, 15, 18, 21, 24)


HIGHLIGHT_GROUPS = {
    'orange': [
        'they are the sum of',
        'all our neuroses',
        'layer 1',
        'fact',
        "it's layer 1 for every great thing",
        "that's ever been invented or discovered",
        'maximalist',
        'keep your dignity',
        'layer 1',
        'get some toxicity get some bitcoin open your heart to',
        'bitcoin',
        'by the rancid catnip of fiat money',
        'buying the dip',
        'shitcoiner at heart',
        'toxic bitcoin maximalists within six months',
        'harass old women and children',
        "the numbers don't lie",
        'america left 85',
        'billion worth of hate toys in afghanistan',
        '2 trillion fiat cuck bucks',
        'the game theorized bitcoin protocol',
        'infinitely more efficient',
        'to transact and store wealth in than fiat shitcoins',
        'or gold',
        "that's right bitcoin will take",
        'all the energy',
        'everyone will live their own experience in the rabbit hole',
        'we are getting our souls back and our minds',
    ],
    'inverted': [
        'money printers banking terrorists stock traders central bank arsonists',
        "don't fall for shitcoinery",
        'gotta be this way forty years of dumb post 1971 fiat money nonsense',
        "it's a stun gun to the genitals",
        '1 billion',
        'volcano bonds',
        'sorry bhutan you fell for that snake oil salesmen over at xrp get ready to experience shitcoin hell',
        'shitcoiners useless royals',
        'it does this by monetizing',
        'gargantuanly wasteful',
        'money printing',
        'wars to keep it going',
        'war and violence',
        'economy',
    ],
}


def clean_words(text):
    return re.sub(r'[^a-z\s]', ' ', text.lower()).split()


def line_words(line):
    return clean_words(line)


def bip_only(seq, wordset):
    return [word for word in seq if word in wordset]


def group_word(groups, wordset, mode):
    out = []
    for group in groups:
        filtered = bip_only(clean_words(group), wordset)
        if not filtered:
            continue
        if mode == 'first':
            out.append(filtered[0])
        elif mode == 'last':
            out.append(filtered[-1])
        else:
            out.append(filtered[len(filtered) // 2])
    return out


def interleave(a, b):
    out = []
    for index in range(max(len(a), len(b))):
        if index < len(a):
            out.append(a[index])
        if index < len(b):
            out.append(b[index])
    return out


def sequence_sources(text, wordset):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    all_words = clean_words(text)

    sources = []
    sources.append(('raw:words', all_words))
    sources.append(('raw:bip39-only', bip_only(all_words, wordset)))
    sources.append(('raw:reverse-bip39-only', list(reversed(bip_only(all_words, wordset)))))

    for offset in (0, 1):
        selected = lines[offset::2]
        label = 'odd-lines' if offset == 0 else 'even-lines'
        selected_words = clean_words(' '.join(selected))
        sources.append((f'{label}:bip39-only', bip_only(selected_words, wordset)))
        sources.append((f'{label}:first-words', bip_only([line_words(line)[0] for line in selected if line_words(line)], wordset)))
        sources.append((f'{label}:last-words', bip_only([line_words(line)[-1] for line in selected if line_words(line)], wordset)))

    for mode in ('first', 'last'):
        seq = [line_words(line)[0 if mode == 'first' else -1] for line in lines if line_words(line)]
        sources.append((f'lines:{mode}-words', bip_only(seq, wordset)))
        sources.append((f'lines:{mode}-words-reverse', list(reversed(bip_only(seq, wordset)))))

    for n in range(2, 41):
        for offset in range(n):
            selected = all_words[offset::n]
            filtered = bip_only(selected, wordset)
            if len(filtered) >= 12:
                sources.append((f'nth:{n}:offset:{offset}:bip39-only', filtered))

    for name, groups in HIGHLIGHT_GROUPS.items():
        flattened = bip_only(clean_words(' '.join(groups)), wordset)
        sources.append((f'highlight:{name}:all', flattened))
        sources.append((f'highlight:{name}:all-reverse', list(reversed(flattened))))
        for mode in ('first', 'last', 'middle'):
            sources.append((f'highlight:{name}:{mode}', group_word(groups, wordset, mode)))
            sources.append((f'highlight:{name}:{mode}-reverse', list(reversed(group_word(groups, wordset, mode)))))

    for mode in ('first', 'last', 'middle'):
        orange = group_word(HIGHLIGHT_GROUPS['orange'], wordset, mode)
        inverted = group_word(HIGHLIGHT_GROUPS['inverted'], wordset, mode)
        sources.append((f'highlight:combined:{mode}:orange-inverted', orange + inverted))
        sources.append((f'highlight:combined:{mode}:inverted-orange', inverted + orange))
        sources.append((f'highlight:combined:{mode}:interleaved', interleave(orange, inverted)))

    return sources


def candidate_windows(seq):
    for length in VALID_LENGTHS:
        for start in range(0, len(seq) - length + 1):
            yield seq[start : start + length], f'window:{start}:{length}'
    for start in range(0, len(seq) - 13 + 1):
        window = seq[start : start + 13]
        for drop in range(13):
            yield window[:drop] + window[drop + 1 :], f'window:{start}:13-drop:{drop}:{window[drop]}'


def strict_candidates():
    text = TEXT_FILE.read_text()
    wordset = set(Mnemonic('english').wordlist)
    validator = Bip39MnemonicValidator()
    seen = set()
    hits = []

    for source, seq in sequence_sources(text, wordset):
        for words, edit in candidate_windows(seq):
            phrase = ' '.join(words)
            if phrase in seen:
                continue
            seen.add(phrase)
            if validator.IsValid(phrase):
                hits.append({'source': source, 'edit': edit, 'phrase': phrase})

    return hits


def derive_addresses(mnemonic):
    seed = Bip39SeedGenerator(mnemonic).Generate('')
    contexts = [
        ('m/44h/0h/0h/0/0', Bip44.FromSeed(seed, Bip44Coins.BITCOIN)),
        ('m/49h/0h/0h/0/0', Bip49.FromSeed(seed, Bip49Coins.BITCOIN)),
        ('m/84h/0h/0h/0/0', Bip84.FromSeed(seed, Bip84Coins.BITCOIN)),
    ]
    for path, ctx in contexts:
        address = (
            ctx.Purpose()
            .Coin()
            .Account(0)
            .Change(Bip44Changes.CHAIN_EXT)
            .AddressIndex(0)
            .PublicKey()
            .ToAddress()
        )
        yield path, address


def check_activity(hits):
    address_map = {}
    for hit in hits:
        for path, address in derive_addresses(hit['phrase']):
            address_map[address] = {**hit, 'path': path, 'address': address}

    found = []
    session = requests.Session()
    addresses = sorted(address_map)
    for index in range(0, len(addresses), 35):
        batch = addresses[index : index + 35]
        active = quote('|'.join(batch), safe='|')
        response = session.get(f'https://blockchain.info/multiaddr?active={active}', timeout=30)
        response.raise_for_status()
        for item in response.json().get('addresses', []):
            total_received = int(item.get('total_received', 0))
            final_balance = int(item.get('final_balance', 0))
            if total_received > 0 or final_balance > 0:
                found.append({**address_map[item['address']], 'total_received': total_received, 'final_balance': final_balance})
        time.sleep(0.35)
    return found, len(addresses)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-chain', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    hits = strict_candidates()
    if args.json:
        print(json.dumps(hits, indent=2))
        return

    print(f'Strict BIP39 candidates: {len(hits)}')
    by_source = {}
    for hit in hits:
        by_source[hit['source']] = by_source.get(hit['source'], 0) + 1
    for source, count in sorted(by_source.items(), key=lambda item: (-item[1], item[0]))[:30]:
        print(f'{count:4} {source}')

    print('\nFirst 30 candidates:')
    for hit in hits[:30]:
        print(f"[{hit['source']}] {hit['edit']} :: {hit['phrase']}")

    if args.check_chain:
        found, address_count = check_activity(hits)
        print(f'\nChecked {address_count} addresses. Addresses with activity: {len(found)}')
        for hit in found:
            print()
            print(f"{hit['address']} path={hit['path']} received={hit['total_received']} balance={hit['final_balance']}")
            print(f"{hit['source']} {hit['edit']}")
            print(hit['phrase'])


if __name__ == '__main__':
    main()
