#!/usr/bin/env python3
"""Exact literal shape reachability for a finite word-choice language.

The library consumes supplied layers, graphs, and a dictionary. The CLI runs
only synthetic controls. Reachability returns booleans and resource counts.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import re
from collections import deque

from global_mirror_dag import graph as build_graph


MODES = ("words-spaced", "words-joined", "initials", "finals")
END = -1
BASE58 = frozenset("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
HEX = frozenset("0123456789abcdefABCDEF")
WIF_LENGTHS = (51, 52)
MINIKEY_LENGTHS = (22, 26, 30)
BIP39_LENGTHS = (12, 15, 18, 21, 24)
DEFAULT_MAXIMUM_UNITS = 2_000_000
TRIE_ROOT = 0
INVALID_TOKEN = -1


class WorkLimitExceeded(RuntimeError):
    """The registered descriptor work limit prevented completion."""


class Budget:
    """Count deterministic structural work and state/transition attempts."""

    def __init__(self, maximum_units=DEFAULT_MAXIMUM_UNITS):
        if type(maximum_units) is not int or maximum_units < 0:
            raise ValueError("Work limit must be a nonnegative integer")
        self.maximum_units = maximum_units
        self.units = 0
        self.by_kind = {}

    def charge(self, kind, count=1):
        if not count:
            return
        self.units += count
        self.by_kind[kind] = self.by_kind.get(kind, 0) + count
        if self.units > self.maximum_units:
            raise WorkLimitExceeded("Descriptor work-unit cap exceeded")

    def report(self):
        return {"maximumWorkUnits": self.maximum_units, "workUnits": self.units,
                "byKind": dict(self.by_kind)}


def reading_graph(layers, mode, reverse=False):
    """Adapt ordered `[token]` and `[None, token]` G02 positions to a DAG."""
    if mode not in MODES or type(reverse) is not bool:
        raise ValueError("Unknown mode or order")
    rows = []
    for layer in layers:
        if not isinstance(layer, (list, tuple)) or (
            len(layer) != 1 and (len(layer) != 2 or layer[0] is not None)
        ):
            raise ValueError("Invalid must/optional layer")
        token = layer[-1]
        if (not isinstance(token, str) or not token
                or any(char.isspace() for char in token)
                or not any(char.isalnum() for char in token)):
            raise ValueError("Layer requires a nonempty lexical token without whitespace")
        if mode == "finals":
            token = next(char for char in reversed(token) if char.isalnum())
        rows.append([None, token] if len(layer) == 2 else [token])
    graph_mode = "words-joined" if mode == "finals" else mode
    return build_graph(rows, graph_mode, reverse)


def _live_dag(graph, budget):
    """Validate the graph and retain only nodes on complete language paths."""
    chars = graph["chars"]
    successors = graph["next"]
    if not isinstance(chars, dict) or not isinstance(successors, dict):
        raise ValueError("Invalid graph dictionaries")
    budget.charge("graphNodes", len(chars) + 1)
    if (set(chars) != set(successors) or any(type(node) is not int or node < 0 for node in chars)
            or any(not isinstance(char, str) or len(char) != 1 for char in chars.values())):
        raise ValueError("Invalid character nodes")
    nodes = set(chars) | {END}
    raw_first = graph["first"]
    if not isinstance(raw_first, (set, frozenset, list, tuple)):
        raise ValueError("Invalid graph starts")
    budget.charge("graphStarts", len(raw_first))
    if any(type(node) is not int or node not in nodes for node in raw_first):
        raise ValueError("Invalid graph start node")
    first = set(raw_first)
    adjacency = {END: ()}
    predecessors = {node: [] for node in nodes}
    for node in sorted(chars):
        children = successors[node]
        if not isinstance(children, (set, frozenset, list, tuple)):
            raise ValueError("Invalid successor collection")
        budget.charge("graphEdges", len(children))
        if any(type(child) is not int or child not in nodes for child in children):
            raise ValueError("Unknown graph successor")
        adjacency[node] = tuple(sorted(set(children)))
        for child in adjacency[node]:
            predecessors[child].append(node)

    def reachable(seeds, edges):
        visited, pending = set(), list(seeds)
        while pending:
            node = pending.pop()
            if node not in visited:
                visited.add(node)
                pending.extend(edges[node])
        return visited

    from_start = reachable(first, adjacency)
    if END not in from_start:
        raise ValueError("Graph has no complete language path")
    live = from_start & reachable((END,), predecessors)
    live_next = {node: tuple(child for child in adjacency[node] if child in live) for node in live}
    indegree = {node: sum(parent in live for parent in predecessors[node]) for node in live}
    queue = deque(node for node in sorted(live) if not indegree[node])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for child in live_next[node]:
            indegree[child] -= 1
            if not indegree[child]:
                queue.append(child)
    if len(order) != len(live):
        raise ValueError("Complete language paths require an acyclic graph")
    return chars, live_next, tuple(sorted(first & live)), order


def _base58_presence(chars, successors, order, budget):
    """An embedded match needs a marker and a sufficiently long Base58 run."""
    longest_from = {END: 0}
    wif_max, minikey_max = 0, 0
    for node in reversed(order):
        if node == END:
            continue
        budget.charge("base58Nodes")
        char = chars[node]
        if char not in BASE58:
            longest_from[node] = 0
            continue
        children = successors[node]
        budget.charge("base58Edges", len(children))
        run = min(max(WIF_LENGTHS), 1 + max((longest_from[child] for child in children), default=0))
        longest_from[node] = run
        if char in "5KL":
            wif_max = max(wif_max, run)
        if char == "S":
            minikey_max = max(minikey_max, run)
    return wif_max, minikey_max


def _hex64_presence(chars, successors, first, order, budget):
    """Propagate feasible trailing hex lengths as a capped 66-bit set."""
    exact = 1 << 64
    overflow = 1 << 65
    mask = (overflow << 1) - 1
    incoming = dict.fromkeys(first, 1)
    found = False
    for node in order:
        budget.charge("hexNodes")
        lengths = incoming.pop(node, 0)
        if node == END:
            found |= bool(lengths & exact)
            continue
        if chars[node] in HEX:
            advanced = ((lengths << 1) & mask) | (lengths & overflow)
        else:
            found |= bool(lengths & exact)
            advanced = 1 if lengths else 0
        children = successors[node]
        budget.charge("hexEdges", len(children))
        for child in children:
            incoming[child] = incoming.get(child, 0) | advanced
    return found


def _dictionary_trie(dictionary, budget):
    edges, accepting = [{}], set()
    for word in dictionary:
        if not isinstance(word, str) or not word or not word.isascii() or not word.isalpha() or not word.islower():
            raise ValueError("Expected lowercase ASCII words from the English dictionary")
        budget.charge("dictionaryCodepoints", len(word))
        node = TRIE_ROOT
        for char in word:
            child = edges[node].get(char)
            if child is None:
                child = len(edges)
                edges[node][char] = child
                edges.append({})
            node = child
        accepting.add(node)
    return edges, accepting


def _bip39_streak(chars, successors, first, order, dictionary, budget):
    """Keep the longest feasible streak per lexical state at each graph node."""
    trie, accepting = _dictionary_trie(dictionary, budget)
    maximum = max(BIP39_LENGTHS)
    incoming = {node: {(TRIE_ROOT, False): 0} for node in first}
    best = 0

    def finish(cursor, streak):
        if cursor == TRIE_ROOT:
            return streak
        return min(maximum, streak + 1) if cursor in accepting else 0

    for node in order:
        states = incoming.pop(node, {})
        budget.charge("bip39States", len(states))
        if node == END:
            for (cursor, _), streak in states.items():
                best = max(best, finish(cursor, streak))
            continue
        char = chars[node]
        alnum = char.isascii() and char.isalnum()
        apostrophe = char in ("'", "’")
        advanced = {}
        for (cursor, pending_quote), streak in states.items():
            if alnum:
                if pending_quote or cursor == INVALID_TOKEN:
                    cursor = INVALID_TOKEN
                else:
                    cursor = trie[cursor].get(char.lower(), INVALID_TOKEN)
                if cursor == INVALID_TOKEN:
                    streak = 0
                state = (cursor, False)
            elif apostrophe and cursor != TRIE_ROOT and not pending_quote:
                # This quote joins the token only if the next char is alnum.
                state = (cursor, True)
            else:
                streak = finish(cursor, streak)
                best = max(best, streak)
                if char == "␞":
                    streak = 0
                state = (TRIE_ROOT, False)
            advanced[state] = max(advanced.get(state, 0), streak)
        children = successors[node]
        budget.charge("bip39Transitions", len(children) * len(advanced))
        for child in children:
            target = incoming.setdefault(child, {})
            for state, streak in advanced.items():
                target[state] = max(target.get(state, 0), streak)
    return best


def shape_presence(graph, dictionary, budget=None):
    """Decide literal shape presence on all complete paths of one descriptor.

    ``presence`` is null when a deterministic work limit interrupts a check.
    Malformed graph or dictionary input raises ValueError or a schema error.
    The dictionary argument can be an iterable of words or a word-index map.
    """
    if budget is None:
        budget = Budget()
    try:
        chars, successors, first, order = _live_dag(graph, budget)
        wif, minikey = _base58_presence(chars, successors, order, budget)
        hex64 = _hex64_presence(chars, successors, first, order, budget)
        bip39 = _bip39_streak(chars, successors, first, order, dictionary, budget)
    except WorkLimitExceeded:
        return {"complete": False, "presence": None, "reason": "work-unit-cap",
                "resourceCounts": budget.report()}
    return {
        "complete": True,
        "presence": {
            "wif": {str(length): wif >= length for length in WIF_LENGTHS},
            "minikey": {str(length): minikey >= length for length in MINIKEY_LENGTHS},
            "hex64": hex64,
            "bip39": {str(length): bip39 >= length for length in BIP39_LENGTHS},
        },
        "reason": None,
        "resourceCounts": budget.report(),
    }


def _flat_projection(words, mode):
    if mode == "words-spaced":
        return " ".join(words)
    if mode == "words-joined":
        return "".join(words)
    if mode == "initials":
        return "".join(next(c for c in word if c.isalnum()) for word in words)
    return "".join(next(c for c in reversed(word) if c.isalnum()) for word in words)


def _flat_presence(texts, dictionary, common):
    indexes = dict.fromkeys(dictionary, 0)
    wif, minikey, bip39 = set(), set(), set()
    hex64 = False
    for text in texts:
        wif.update(len(value) for value in common.shape_values("wif", text))
        minikey.update(len(value) for value in common.shape_values("minikey", text))
        if re.search(r"S[1-9A-HJ-NP-Za-km-z]{25}", text):
            minikey.add(26)
        hex64 |= any(True for _ in common.shape_values("hex64", text))
        bip39.update(len(value.split()) for value in common.shape_values("bip39", text, indexes))
    return {"wif": {str(n): n in wif for n in WIF_LENGTHS},
            "minikey": {str(n): n in minikey for n in MINIKEY_LENGTHS},
            "hex64": hex64,
            "bip39": {str(n): n in bip39 for n in BIP39_LENGTHS}}


def self_test():
    """Compare the product search to exact flat shapes on synthetic paths."""
    import batch20_common as common

    if not __debug__:
        raise RuntimeError("Synthetic controls require assertions enabled")
    dictionary = ("abandon", "ability", "about", "act", "able")
    fixtures = [
        [], [[None, "é"]], [["noise"], [None, "S"], ["2" * 21], [None, "2" * 8]],
        [["L"], ["a" * 50], [None, "a"]],
        [[None, "Z"], ["f" * 32], [None, "a"], ["f" * 32], [None, "Z"]],
        [[None, "Z"], ["0" * 64], ["F"]],
        [["éS!"], *[["x2!"]] * 25, *[[None, "x2!"]] * 4],
        [["About"]] * 11 + [[None, "aBILITY"], ["abandon"]],
        [["about"]] * 11 + [["about'"], ["able"]],
        [["about"]] * 11 + [["about’about"], ["able"]],
        [["about"]] * 11 + [["about''about"], ["able"]],
        [["about"]] * 11 + [["about␞able"], ["able"]],
        [["about"]] * 11 + [["bad␞about"], ["able"]],
        [["about"]] * 24,
        [["about"]] * 23 + [[None, "1"]],
        [["about"]] * 23 + [["about’"]],
        [["aban"], [None, "bad"], ["don"], *[["about"]] * 11],
    ]
    # Preserve optional and must layer semantics while exhaustively covering
    # the concrete paths of each randomly assembled small fixture.
    rng = random.Random(20261110)
    pool = ["S", "K", "L", "2" * 22, "3" * 26, "a" * 32, "a" * 64,
            "abandon", "ABOUT", "ability", "about'", "’act", "q␞about", "é2'", "9"]
    for _ in range(48):
        fixtures.append([([None, word] if rng.choice((False, True)) else [word])
                         for word in rng.choices(pool, k=rng.randint(1, 7))])
    comparisons = 0
    for layers in fixtures:
        for mode, reverse in itertools.product(MODES, (False, True)):
            texts = []
            for path in itertools.product(*layers):
                words = [token for token in path if token is not None]
                if reverse:
                    words.reverse()
                texts.append(_flat_projection(words, mode))
            result = shape_presence(reading_graph(layers, mode, reverse), dictionary)
            assert result["complete"] and result["presence"] == _flat_presence(texts, dictionary, common)
            comparisons += 1

    # Punctuation-only segments are legal in the generic graph. They check a
    # pending quote split across graph nodes and a hard barrier after a word.
    for tail in [["'"], ["'", "a"], ["’", "'", "about"], ["␞", "able"]]:
        words = ["about "] * 11 + ["act"] + tail
        graph = build_graph([[word] for word in words])
        result = shape_presence(graph, dictionary)
        assert result["presence"] == _flat_presence(["".join(words)], dictionary, common)
        comparisons += 1

    dead = build_graph([["S" + "2" * 29]])
    dead["first"].add(END)
    for children in dead["next"].values():
        children.discard(END)
    assert shape_presence(dead, dictionary)["presence"] == _flat_presence([""], dictionary, common)
    comparisons += 1

    capped = shape_presence(reading_graph([["S"]], "initials"), dictionary, Budget(0))
    assert not capped["complete"] and capped["presence"] is None and capped["reason"] == "work-unit-cap"
    return {"passed": True, "flatComparisons": comparisons,
            "projectionModes": list(MODES), "cappedResultIsInconclusive": True,
            "targetInputsRead": False, "targetRecognitionRun": False, "keyChecks": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", required=True)
    parser.parse_args(argv)
    print(json.dumps(self_test(), sort_keys=True))


if __name__ == "__main__":
    main()
